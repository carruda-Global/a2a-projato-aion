"""Router HTTP para os 8 agentes do Compliance Copilot BR — ate hoje so
existiam internamente, sem jeito do cliente usar de verdade. Mesmo problema
do Procurement/Engineering Suite antes desta sessao. Todos reais (LLM),
ja vendidos (Compliance Essencial, Regulatory Pro, Tributario CBS/IBS)."""
import asyncio
from fastapi import APIRouter
from pydantic import BaseModel

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from src.agents.lgpd_operacional import LgpdOperacionalAgent
from src.agents.tributario_cbs_ibs import TributarioCBSIBSAgent
from src.agents.esg_ifrs import ESGIFRSAgent
from src.agents.inventario_carbono import InventarioCarbonoAgent
from src.agents.escopo3_fornecedores import Escopo3FornecedoresAgent
from src.agents.canal_denuncias import CanalDenunciasAgent
from src.agents.igualdade_salarial import IgualdadeSalarialAgent
from src.agents.compliance_anticorrupcao import ComplianceAnticorrupcaoAgent

router = APIRouter(prefix="/api/compliance-br", tags=["compliance-br"])


def _llm() -> DeepSeekClient:
    return DeepSeekClient(Settings())


class TextIn(BaseModel):
    text: str
    lang: str = "pt"


class TextPairIn(BaseModel):
    text_a: str
    text_b: str
    lang: str = "pt"


# ---- LGPD Operacional ----
@router.post("/lgpd/mapear-fluxos")
async def lgpd_mapear(dados: TextIn):
    agent = LgpdOperacionalAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.mapear_fluxos_dados, dados.text, dados.lang)


@router.post("/lgpd/gerar-ropa")
async def lgpd_ropa(dados: TextIn):
    agent = LgpdOperacionalAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.gerar_ropa, dados.text, dados.lang)


@router.post("/lgpd/avaliar-conformidade")
async def lgpd_conformidade(dados: TextIn):
    agent = LgpdOperacionalAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.avaliar_conformidade, dados.text, dados.lang)


# ---- Tributario CBS/IBS ----
@router.post("/tributario/classificar-produto")
async def trib_classificar(dados: TextIn):
    agent = TributarioCBSIBSAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.classificar_produto, dados.text, dados.lang)


@router.post("/tributario/verificar-conformidade")
async def trib_conformidade(dados: TextIn):
    agent = TributarioCBSIBSAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.verificar_conformidade, dados.text, dados.lang)


@router.post("/tributario/simular-impacto")
async def trib_impacto(dados: TextIn):
    agent = TributarioCBSIBSAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.simular_impacto, dados.text, dados.lang)


# ---- ESG / IFRS ----
@router.post("/esg/diagnosticar-maturidade")
async def esg_diagnostico(dados: TextIn):
    agent = ESGIFRSAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.diagnosticar_maturidade, dados.text, dados.lang)


@router.post("/esg/relatorio-sustentabilidade")
async def esg_relatorio(dados: TextIn):
    agent = ESGIFRSAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.gerar_relatorio_sustentabilidade, dados.text, dados.lang)


@router.post("/esg/questionario")
async def esg_questionario(dados: TextPairIn):
    agent = ESGIFRSAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.responder_questionario, dados.text_a, dados.text_b, dados.lang)


# ---- Inventario de Carbono ----
@router.post("/carbono/calcular-emissoes")
async def carbono_calcular(dados: TextIn):
    agent = InventarioCarbonoAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.calcular_emissoes, dados.text, dados.lang)


@router.post("/carbono/gerar-inventario")
async def carbono_inventario(dados: TextIn):
    agent = InventarioCarbonoAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.gerar_inventario, dados.text, dados.lang)


@router.post("/carbono/hotspots")
async def carbono_hotspots(dados: TextIn):
    agent = InventarioCarbonoAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.identificar_hotspots, dados.text, dados.lang)


# ---- Escopo 3 / Fornecedores ----
@router.post("/escopo3/avaliar-fornecedores")
async def escopo3_avaliar(dados: TextIn):
    agent = Escopo3FornecedoresAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.avaliar_fornecedores, dados.text, dados.lang)


# ---- Canal de Denuncias ----
@router.post("/whistleblower-br/classificar")
async def wb_classificar(dados: TextIn):
    agent = CanalDenunciasAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.classificar_denuncia, dados.text, dados.lang)


@router.post("/whistleblower-br/relatorio-semestral")
async def wb_relatorio(dados: TextIn):
    agent = CanalDenunciasAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.gerar_relatorio_semestral, dados.text, dados.lang)


@router.post("/whistleblower-br/configurar-canal")
async def wb_configurar(dados: TextIn):
    agent = CanalDenunciasAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.configurar_canal, dados.text, dados.lang)


# ---- Igualdade Salarial ----
@router.post("/igualdade-salarial/analisar-equidade")
async def eq_analisar(dados: TextIn):
    agent = IgualdadeSalarialAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.analisar_equidade, dados.text, dados.lang)


@router.post("/igualdade-salarial/relatorio-mte")
async def eq_relatorio(dados: TextIn):
    agent = IgualdadeSalarialAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.gerar_relatorio_mte, dados.text, dados.lang)


@router.post("/igualdade-salarial/monitorar-diversidade")
async def eq_diversidade(dados: TextIn):
    agent = IgualdadeSalarialAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.monitorar_diversidade, dados.text, dados.lang)


# ---- Compliance / Anticorrupcao ----
@router.post("/anticorrupcao/diagnosticar-maturidade")
async def anti_diagnostico(dados: TextIn):
    agent = ComplianceAnticorrupcaoAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.diagnosticar_maturidade, dados.text, dados.lang)


@router.post("/anticorrupcao/gerar-codigo-etica")
async def anti_codigo(dados: TextIn):
    agent = ComplianceAnticorrupcaoAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.gerar_codigo_etica, dados.text, dados.lang)


@router.post("/anticorrupcao/due-diligence")
async def anti_dd(dados: TextIn):
    agent = ComplianceAnticorrupcaoAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.due_diligence_terceiros, dados.text, dados.lang)


@router.post("/anticorrupcao/relatorio-cgu")
async def anti_cgu(dados: TextIn):
    agent = ComplianceAnticorrupcaoAgent(Settings(), _llm())
    return await asyncio.to_thread(agent.gerar_relatorio_cgu, dados.text, dados.lang)
