"""Engineering Copilot — Modulo 1 (Document Intelligence), Modulo 2 (Photo
Intelligence) e Modulo 3 (Engineering Assistant). Unica camada que fala com o
LLM; Modulo 4 (documentos) e Modulo 5 (compliance) sao deterministicos e nunca
chamam IA."""
import base64
import io
import os

from openai import OpenAI

from src.agents._copilot_common import parsear_json_llm
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")

DOCUMENT_SYSTEM_PROMPT = (
    "Voce e um motor de extracao de dados tecnicos de documentos de engenharia "
    "(memoriais, relatorios, plantas, planilhas). Leia o texto abaixo e extraia "
    "APENAS o que estiver explicitamente presente — nunca invente equipamentos, "
    "tags ou normas. Retorne JSON estrito no formato:\n"
    '{"equipamentos": [{"tag": "", "tipo": "", "fabricante": "", "modelo": "", '
    '"capacidade": "", "localizacao": ""}], '
    '"normas": [{"norma": "", "descricao": ""}], '
    '"datas": [""], "localizacao_geral": ""}'
)

PHOTO_SYSTEM_PROMPT = (
    "Voce e um especialista em vistoria fotografica de equipamentos e instalacoes "
    "de engenharia (climatizacao, industrial, predial). Analise a foto e retorne "
    "JSON estrito no formato:\n"
    '{"equipamentos_detectados": [{"tag": "", "tipo": "", "fabricante": "", "modelo": ""}], '
    '"tag_ocr": "", "problemas": [""], "estado_isolamento": "", "recomendacoes": [""]}\n'
    'Em "problemas", liste apenas o que for visivel: vazamento, corrosao, oxidacao, '
    "isolamento danificado, falta de EPI, risco de seguranca. Se nao houver problema "
    "visivel, retorne lista vazia."
)


def _vision_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))


async def extrair_dados_documento(texto: str) -> dict:
    """Modulo 1 — equipamentos, tags, modelos, fabricantes, normas, datas, localizacao."""
    import asyncio

    settings = Settings()
    llm = DeepSeekClient(settings)
    raw = await asyncio.to_thread(llm.chat, DOCUMENT_SYSTEM_PROMPT, f"Documento:\n{texto[:12000]}")
    dados = parsear_json_llm(raw)
    dados.setdefault("equipamentos", [])
    dados.setdefault("normas", [])
    dados.setdefault("datas", [])
    return dados


async def analisar_foto(conteudo: bytes, filename: str) -> dict:
    """Modulo 2 — deteccao de equipamentos, OCR de TAG, vazamentos, corrosao, isolamento."""
    import asyncio

    b64 = base64.b64encode(conteudo).decode("utf-8")
    ext = (filename.rsplit(".", 1)[-1] if "." in filename else "jpeg").lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

    def _chamar():
        client = _vision_client()
        response = client.chat.completions.create(
            model=_VISION_MODEL,
            messages=[
                {"role": "system", "content": PHOTO_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analise esta foto de obra/equipamento."},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    ],
                },
            ],
            max_tokens=1000,
        )
        return response.choices[0].message.content or ""

    raw = await asyncio.to_thread(_chamar)
    dados = parsear_json_llm(raw)
    dados.setdefault("equipamentos_detectados", [])
    dados.setdefault("problemas", [])
    return dados


ASSISTANT_SYSTEM_PROMPT = (
    "Voce e o Engineering Assistant — responde perguntas sobre o projeto de "
    "engenharia com base SOMENTE no contexto fornecido (documentos, equipamentos, "
    "normas e fotos ja processados). Se a informacao nao estiver no contexto, diga "
    "isso explicitamente em vez de inventar. Seja direto e cite normas/evidencias "
    "quando aplicavel."
)


def _montar_contexto(equipamentos: list[dict], normas: list[dict], documentos: list[dict], fotos: list[dict]) -> str:
    partes = [
        f"Equipamentos cadastrados ({len(equipamentos)}): " + "; ".join(
            f"{e.get('tag') or '(sem tag)'} — {e.get('tipo', '')} {e.get('fabricante', '')} {e.get('modelo', '')}"
            for e in equipamentos
        ),
        f"Normas identificadas ({len(normas)}): " + "; ".join(n.get("norma", "") for n in normas),
        f"Documentos recebidos ({len(documentos)}): " + "; ".join(d.get("nome_arquivo", "") for d in documentos),
        f"Fotos analisadas ({len(fotos)}): " + "; ".join(f.get("nome_arquivo", "") for f in fotos),
    ]
    return "\n".join(partes)


async def responder_pergunta(pergunta: str, equipamentos: list[dict], normas: list[dict],
                              documentos: list[dict], fotos: list[dict]) -> str:
    """Modulo 3 — Q&A: docs faltando? PMOC atende legislacao? memorial consistente?
    nao conformidades? normas aplicaveis? qual documento emitir?"""
    import asyncio

    settings = Settings()
    llm = DeepSeekClient(settings)
    contexto = _montar_contexto(equipamentos, normas, documentos, fotos)
    prompt = f"Contexto do projeto:\n{contexto}\n\nPergunta: {pergunta}"
    return await asyncio.to_thread(llm.chat, ASSISTANT_SYSTEM_PROMPT, prompt)
