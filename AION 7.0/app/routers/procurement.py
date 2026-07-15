"""Router HTTP para o Procurement Agent — ate hoje so existia internamente
(orquestrador + protocolo A2A), sem jeito do cliente usar de verdade.

Escopo real hoje: processar lista de materiais para compra, e comparar
cotacoes de fornecedores (ambos via LLM). NAO inclui ainda Vendor
Intelligence com score de risco, RFQ automation, Contract Intelligence ou
Spend Analytics do MVP completo do Procurement Copilot — isso e
desenvolvimento futuro, nao existe ainda."""
import asyncio
from fastapi import APIRouter
from pydantic import BaseModel

from src.agents.procurement import ProcurementAgent
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/procurement", tags=["procurement"])


class MaterialItem(BaseModel):
    name: str
    quantity: float = 0
    unit: str = "un"


class ProcessOrderIn(BaseModel):
    materials: list[MaterialItem]
    lang: str = "pt"


class QuoteItem(BaseModel):
    supplier: str
    price: float = 0
    lead_time: str = ""


class CompareQuotesIn(BaseModel):
    quotes: list[QuoteItem]
    lang: str = "pt"


def _get_agent() -> ProcurementAgent:
    settings = Settings()
    llm = DeepSeekClient(settings)
    return ProcurementAgent(settings, llm)


@router.post("/process-order")
async def process_order(dados: ProcessOrderIn):
    agent = _get_agent()
    material_list = [m.model_dump() for m in dados.materials]
    return await asyncio.to_thread(agent.process_order, material_list, dados.lang)


@router.post("/compare-quotes")
async def compare_quotes(dados: CompareQuotesIn):
    agent = _get_agent()
    quotes = [q.model_dump() for q in dados.quotes]
    recomendacao = await asyncio.to_thread(agent.compare_quotes, quotes, dados.lang)
    return {"agent": "procurement", "recomendacao": recomendacao}
