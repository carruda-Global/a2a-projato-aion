"""Endpoints do Procurement Copilot MVP — Vendor Intelligence (score real,
deterministico), Purchase Intelligence (requisicoes), RFQ Intelligence
(cotacoes + comparacao) e Spend Intelligence (curva ABC).

Contract Intelligence do MVP original nao foi duplicado aqui — o
Contract Risk Copilot (`/api/contract-risk`) ja existe e faz exatamente
isso, real, desde antes desta sessao."""
from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.procurement import crud

router = APIRouter(prefix="/api/procurement-copilot", tags=["procurement-copilot"])


class FornecedorIn(BaseModel):
    nome: str
    cnpj: str | None = None
    categoria: str | None = None
    tem_iso9001: bool = False
    tem_iso14001: bool = False
    tem_certificado_seguranca: bool = False
    anos_mercado: int = 0
    entregas_no_prazo_pct: int = 0
    incidentes_qualidade: int = 0


@router.post("/fornecedores")
async def criar_fornecedor(dados: FornecedorIn):
    return await crud.criar_fornecedor(dados.model_dump())


@router.get("/fornecedores")
async def listar_fornecedores():
    return await crud.listar_fornecedores()


class RequisicaoIn(BaseModel):
    descricao: str
    quantidade: float | None = None
    unidade: str | None = None


@router.post("/requisicoes")
async def criar_requisicao(dados: RequisicaoIn):
    return await crud.criar_requisicao(dados.descricao, dados.quantidade, dados.unidade)


class RFQIn(BaseModel):
    requisicao_id: UUID
    escopo: str
    criterios_tecnicos: str = ""


@router.post("/rfqs")
async def criar_rfq(dados: RFQIn):
    return await crud.criar_rfq(dados.requisicao_id, dados.escopo, dados.criterios_tecnicos)


class CotacaoIn(BaseModel):
    rfq_id: UUID
    fornecedor_id: UUID
    preco: float
    prazo_dias: int = 0


@router.post("/cotacoes")
async def registrar_cotacao(dados: CotacaoIn):
    return await crud.registrar_cotacao(dados.rfq_id, dados.fornecedor_id, dados.preco, dados.prazo_dias)


@router.get("/rfqs/{rfq_id}/comparativo")
async def comparar_cotacoes(rfq_id: UUID):
    return await crud.comparar_cotacoes(rfq_id)


class CompraIn(BaseModel):
    fornecedor_id: UUID
    categoria: str
    valor: float


@router.post("/compras")
async def registrar_compra(dados: CompraIn):
    return await crud.registrar_compra(dados.fornecedor_id, dados.categoria, dados.valor)


@router.get("/dashboard")
async def dashboard():
    fornecedores = await crud.listar_fornecedores()
    spend = await crud.spend_analytics()
    return {
        "total_fornecedores": len(fornecedores),
        "fornecedores_alto_risco": len([f for f in fornecedores if f["classificacao"] in ("Alto Risco", "Critico")]),
        "spend": spend,
    }
