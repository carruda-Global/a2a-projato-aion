"""Router HTTP para Regulatory Analyst e Compliance PM (Microsoft Pack /
Enterprise Ops Copilot) — reais, ja vendidos. Mesmo gate de assinatura dos
outros Global Copilots (Contract Risk, Vendor Risk etc): sem licenca premium
devolve preview + link de checkout; com licenca devolve o resultado completo."""
import asyncio
from fastapi import APIRouter
from pydantic import BaseModel

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from src.agents._copilot_common import tem_licenca_premium
from src.agents.regulatory_analyst import RegulatoryAnalystAgent
from src.agents.compliance_pm import CompliancePMAgent

router = APIRouter(prefix="/api/enterprise-ops", tags=["enterprise-ops"])

CHECKOUT_URL = "https://buy.stripe.com/cNi8wRdiU8cj75y9Cgg7e0p"


def _llm() -> DeepSeekClient:
    return DeepSeekClient(Settings())


class TextIn(BaseModel):
    text: str
    lang: str = "pt"
    customer_email: str = ""


def _responder(modulo: str, resultado: dict, premium: bool) -> dict:
    if premium:
        return {"module": modulo, "result": resultado, "license": "premium"}
    return {
        "module": modulo,
        "preview": resultado,
        "license": "demo",
        "message": "Resultado gerado em modo demonstracao — assine para liberar o relatorio completo.",
        "checkout_url": CHECKOUT_URL,
    }


@router.post("/regulatory-analyst/analisar")
async def reg_analisar(dados: TextIn):
    premium = tem_licenca_premium(dados.customer_email)
    agent = RegulatoryAnalystAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.analisar_documento, dados.text, dados.lang)
    return _responder("regulatory_analyst_analisar", resultado, premium)


@router.post("/regulatory-analyst/relatorio-riscos")
async def reg_relatorio(dados: TextIn):
    premium = tem_licenca_premium(dados.customer_email)
    agent = RegulatoryAnalystAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.gerar_relatorio_riscos, dados.text, dados.lang)
    return _responder("regulatory_analyst_relatorio_riscos", resultado, premium)


@router.post("/compliance-pm/gerenciar-projeto")
async def pm_gerenciar(dados: TextIn):
    premium = tem_licenca_premium(dados.customer_email)
    agent = CompliancePMAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.gerenciar_projeto, dados.text, dados.lang)
    return _responder("compliance_pm_gerenciar_projeto", resultado, premium)


@router.post("/compliance-pm/monitorar-prazos")
async def pm_prazos(dados: TextIn):
    premium = tem_licenca_premium(dados.customer_email)
    agent = CompliancePMAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.monitorar_prazos, dados.text, dados.lang)
    return _responder("compliance_pm_monitorar_prazos", resultado, premium)
