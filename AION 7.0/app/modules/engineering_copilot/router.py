"""Endpoints do Engineering Copilot — mesma estrutura do modulo NR1 (router
fino, logica em app/core/engineering/*). MVP v1.0: upload de documentos/fotos,
extracao (Modulo 1/2), assistente (Modulo 3), geracao de documentos (Modulo 4)
e compliance (Modulo 5)."""
import io
import logging
from uuid import UUID

from docx import Document as DocxReader
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.engineering import ai_engine, crud
from app.core.engineering.compliance_engine import avaliar_compliance
from app.core.engineering.document_generator import TITULOS, gerar_documento
from src.agents._copilot_common import extrair_texto, tem_licenca_premium
from src.agents.engcopilot_embeddings import embed_documento, embed_projeto

router = APIRouter(prefix="/api/engineering-copilot", tags=["engineering_copilot"])
logger = logging.getLogger(__name__)

# Mesmo link universal de "desbloquear premium" usado pelos outros Global
# Copilots (SOC2, ISO27001, Contract Risk, Vendor Risk, EU AI Act) — qualquer
# assinatura Stripe ativa (ex: plano AEC Full, price_id price_1TlxVSQn4rfjkSvEXodTHfNA)
# libera os documentos sem marca d'agua via tem_licenca_premium().
CHECKOUT_URL = "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l"


def _extrair_texto_documento(conteudo: bytes, filename: str) -> str:
    """Estende extrair_texto (PDF/texto) com suporte a DOCX — XLSX/CSV entram
    como texto bruto por ora; parsing tabular fica para uma proxima iteracao."""
    if filename.lower().endswith(".docx"):
        doc = DocxReader(io.BytesIO(conteudo))
        return "\n".join(p.text for p in doc.paragraphs)
    return extrair_texto(conteudo, filename)


class ProjetoIn(BaseModel):
    cliente: str
    local: str | None = None
    escopo: str | None = None
    customer_email: str = ""


class PerguntaIn(BaseModel):
    pergunta: str


async def _carregar_projeto(projeto_id: UUID) -> dict:
    projeto = await crud.obter_projeto(projeto_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto nao encontrado")
    return projeto


@router.post("/projetos")
async def criar_projeto(dados: ProjetoIn):
    projeto = await crud.criar_projeto(dados.model_dump())
    try:
        await embed_projeto(projeto["id"], projeto.get("cliente", ""), projeto.get("local"), projeto.get("escopo"))
    except Exception:
        logger.exception("embed_projeto failed for %s -- project created, embedding skipped", projeto["id"])
    return projeto


@router.get("/projetos/{projeto_id}")
async def obter_projeto(projeto_id: UUID):
    projeto = await _carregar_projeto(projeto_id)
    return {
        "projeto": projeto,
        "documentos": await crud.listar_documentos(projeto_id),
        "equipamentos": await crud.listar_equipamentos(projeto_id),
        "normas": await crud.listar_normas(projeto_id),
        "fotos": await crud.listar_fotos(projeto_id),
    }


@router.post("/projetos/{projeto_id}/documentos")
async def enviar_documento(projeto_id: UUID, file: UploadFile = File(...)):
    """Modulo 1 — Document Intelligence."""
    await _carregar_projeto(projeto_id)
    conteudo = await file.read()
    texto = _extrair_texto_documento(conteudo, file.filename or "")
    dados = await ai_engine.extrair_dados_documento(texto)

    documento = await crud.adicionar_documento(projeto_id, file.filename or "documento", texto, dados)
    if dados.get("equipamentos"):
        await crud.adicionar_equipamentos(projeto_id, dados["equipamentos"], origem="documento")
    if dados.get("normas"):
        await crud.adicionar_normas(projeto_id, dados["normas"])
    try:
        await embed_documento(documento["id"], projeto_id, texto)
    except Exception:
        logger.exception("embed_documento failed for %s -- document saved, embedding skipped", documento["id"])

    return {"documento": documento, "extraido": dados}


@router.post("/projetos/{projeto_id}/fotos")
async def enviar_foto(projeto_id: UUID, file: UploadFile = File(...)):
    """Modulo 2 — Photo Intelligence."""
    await _carregar_projeto(projeto_id)
    conteudo = await file.read()
    analise = await ai_engine.analisar_foto(conteudo, file.filename or "foto.jpg")

    foto = await crud.adicionar_foto(projeto_id, file.filename or "foto.jpg", analise)
    if analise.get("equipamentos_detectados"):
        await crud.adicionar_equipamentos(projeto_id, analise["equipamentos_detectados"], origem="foto")

    return {"foto": foto, "analise": analise}


@router.post("/projetos/{projeto_id}/perguntar")
async def perguntar(projeto_id: UUID, dados: PerguntaIn):
    """Modulo 3 — Engineering Assistant."""
    await _carregar_projeto(projeto_id)
    equipamentos = await crud.listar_equipamentos(projeto_id)
    normas = await crud.listar_normas(projeto_id)
    documentos = await crud.listar_documentos(projeto_id)
    fotos = await crud.listar_fotos(projeto_id)
    resposta = await ai_engine.responder_pergunta(dados.pergunta, equipamentos, normas, documentos, fotos)
    return {"pergunta": dados.pergunta, "resposta": resposta}


@router.get("/projetos/{projeto_id}/compliance")
async def compliance(projeto_id: UUID):
    """Modulo 5 — Compliance (NR, ABNT, CREA, ANVISA, fabricante)."""
    await _carregar_projeto(projeto_id)
    equipamentos = await crud.listar_equipamentos(projeto_id)
    normas = await crud.listar_normas(projeto_id)
    return avaliar_compliance(equipamentos, normas)


@router.get("/projetos/{projeto_id}/gerar/{tipo}")
async def gerar(projeto_id: UUID, tipo: str, customer_email: str = ""):
    """Modulo 4 — Document Generator. tipo em: memorial, relatorio_tecnico,
    inventario, checklist, plano_manutencao, relatorio_fotografico, data_book,
    relatorio_executivo, as_built."""
    if tipo not in TITULOS:
        raise HTTPException(status_code=400, detail=f"Tipo invalido. Opcoes: {sorted(TITULOS)}")

    projeto = await _carregar_projeto(projeto_id)
    equipamentos = await crud.listar_equipamentos(projeto_id)
    normas = await crud.listar_normas(projeto_id)
    documentos = await crud.listar_documentos(projeto_id)
    fotos = await crud.listar_fotos(projeto_id)
    compliance_resultado = avaliar_compliance(equipamentos, normas)

    email = customer_email or projeto.get("customer_email") or ""
    licenca_premium = tem_licenca_premium(email)

    buf = gerar_documento(tipo, projeto, equipamentos, normas, documentos, fotos,
                           compliance_resultado, licenca_premium=licenca_premium)
    nome_arquivo = f"{TITULOS[tipo].replace(' ', '_')}.docx"
    headers = {
        "Content-Disposition": f'attachment; filename="{nome_arquivo}"',
        "X-License-Status": "premium" if licenca_premium else "demo",
    }
    if not licenca_premium:
        headers["X-Checkout-Url"] = CHECKOUT_URL
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.get("/pricing")
async def pricing():
    """Info de venda para o wizard — qualquer assinatura Stripe ativa libera os
    9 documentos sem marca d'agua (mesmo gate dos outros Global Copilots)."""
    return {
        "checkout_url": CHECKOUT_URL,
        "message": "Assinatura ativa libera todos os documentos sem marca d'agua.",
        "planos_compativeis": ["aec_full", "compliance_essencial", "regulatory_pro", "full_suite"],
    }
