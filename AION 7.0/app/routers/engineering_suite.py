"""Router HTTP para os 10 agentes de engenharia AEC do Engineering Suite —
unificado com o mesmo projeto/banco do Engineering Copilot (schema engcopilot)
e com o mesmo gate de assinatura dos outros Global Copilots. Cada chamada exige
um projeto existente, e o resultado fica registrado no historico de documentos
do projeto (visivel via GET /api/engineering-copilot/projetos/{id})."""
import asyncio
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from src.agents._copilot_common import tem_licenca_premium
from app.core.engineering import crud
from src.agents.spec_analyst import SpecAnalystAgent
from src.agents.requirements_analyst import RequirementsAnalystAgent
from src.agents.bim_coordinator import BIMCoordinatorAgent
from src.agents.field_execution import FieldExecutionAgent
from src.agents.logistics import LogisticsAgent
from src.agents.inventory import InventoryAgent
from src.agents.rfi_creation import RFICreationAgent
from src.agents.work_synopsis import WorkSynopsisAgent
from src.agents.engineering_assistant import EngineeringAssistantAgent
from src.agents.photo_intelligence import PhotoIntelligenceAgent

router = APIRouter(prefix="/api/engineering-suite", tags=["engineering-suite"])

CHECKOUT_URL = "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l"


def _llm() -> DeepSeekClient:
    return DeepSeekClient(Settings())


class TextIn(BaseModel):
    projeto_id: UUID
    text: str
    lang: str = "pt"
    customer_email: str = ""


class TextPairIn(BaseModel):
    projeto_id: UUID
    text_a: str
    text_b: str
    lang: str = "pt"
    customer_email: str = ""


class QuestionIn(BaseModel):
    projeto_id: UUID
    question: str
    context: str = ""
    lang: str = "pt"
    customer_email: str = ""


class ItemsIn(BaseModel):
    projeto_id: UUID
    items: list[dict]
    lang: str = "pt"
    customer_email: str = ""


async def _preparar(projeto_id: UUID, customer_email: str) -> bool:
    """Valida que o projeto existe no mesmo banco do Engineering Copilot e
    resolve se a licenca do cliente e premium."""
    projeto = await crud.obter_projeto(projeto_id)
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto nao encontrado")
    email = customer_email or projeto.get("customer_email") or ""
    return tem_licenca_premium(email)


async def _persistir(projeto_id: UUID, modulo: str, entrada: str, resultado: dict) -> None:
    """Registra a chamada como um documento do projeto — unifica o historico do
    Suite com o do Engineering Copilot (visivel no mesmo GET /projetos/{id})."""
    await crud.adicionar_documento(projeto_id, f"suite_{modulo}.json", entrada, resultado)


def _responder(modulo: str, resultado: dict, premium: bool) -> dict:
    if premium:
        return {"module": modulo, "result": resultado, "license": "premium"}
    return {
        "module": modulo,
        "preview": resultado,
        "license": "demo",
        "message": "Resultado gerado em modo demonstracao — assine para liberar o relatorio completo e o historico do projeto.",
        "checkout_url": CHECKOUT_URL,
    }


# ---- Spec Analyst ----
@router.post("/spec-analyst/analyze")
async def spec_analyze(dados: TextIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = SpecAnalystAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.analyze_document, dados.text, dados.lang)
    await _persistir(dados.projeto_id, "spec_analyst_analyze", dados.text, resultado)
    return _responder("spec_analyst_analyze", resultado, premium)


@router.post("/spec-analyst/check-compliance")
async def spec_check_compliance(dados: TextPairIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = SpecAnalystAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.check_compliance, dados.text_a, dados.text_b, dados.lang)
    resultado = {"agent": "spec_analyst", "result": texto}
    await _persistir(dados.projeto_id, "spec_analyst_check_compliance", f"{dados.text_a}\n---\n{dados.text_b}", resultado)
    return _responder("spec_analyst_check_compliance", resultado, premium)


# ---- Requirements Analyst ----
@router.post("/requirements-analyst/analyze")
async def req_analyze(dados: TextIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = RequirementsAnalystAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.analyze_requirements, dados.text, dados.lang)
    await _persistir(dados.projeto_id, "requirements_analyst_analyze", dados.text, resultado)
    return _responder("requirements_analyst_analyze", resultado, premium)


@router.post("/requirements-analyst/check-consistency")
async def req_check_consistency(dados: TextPairIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = RequirementsAnalystAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.check_consistency, dados.text_a, dados.text_b, dados.lang)
    resultado = {"agent": "requirements_analyst", "result": texto}
    await _persistir(dados.projeto_id, "requirements_analyst_check_consistency", f"{dados.text_a}\n---\n{dados.text_b}", resultado)
    return _responder("requirements_analyst_check_consistency", resultado, premium)


# ---- BIM Coordinator ----
@router.post("/bim-coordinator/generate-element")
async def bim_generate(dados: TextIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = BIMCoordinatorAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.generate_bim_element, dados.text, dados.lang)
    await _persistir(dados.projeto_id, "bim_coordinator_generate_element", dados.text, resultado)
    return _responder("bim_coordinator_generate_element", resultado, premium)


@router.post("/bim-coordinator/clash-detection")
async def bim_clash(dados: TextIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = BIMCoordinatorAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.clash_detection, dados.text, dados.lang)
    resultado = {"agent": "bim_coordinator", "result": texto}
    await _persistir(dados.projeto_id, "bim_coordinator_clash_detection", dados.text, resultado)
    return _responder("bim_coordinator_clash_detection", resultado, premium)


# ---- Field Execution ----
@router.post("/field-execution/instructions")
async def field_instructions(dados: TextIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = FieldExecutionAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.generate_field_instructions, dados.text, dados.lang)
    await _persistir(dados.projeto_id, "field_execution_instructions", dados.text, resultado)
    return _responder("field_execution_instructions", resultado, premium)


@router.post("/field-execution/deviations")
async def field_deviations(dados: TextPairIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = FieldExecutionAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.identify_deviations, dados.text_a, dados.text_b, dados.lang)
    resultado = {"agent": "field_execution", "result": texto}
    await _persistir(dados.projeto_id, "field_execution_deviations", f"{dados.text_a}\n---\n{dados.text_b}", resultado)
    return _responder("field_execution_deviations", resultado, premium)


# ---- Logistics ----
@router.post("/logistics/track-shipment")
async def logistics_track(dados: ItemsIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = LogisticsAgent(Settings(), _llm())
    shipment_data = dados.items[0] if dados.items else {}
    resultado = await asyncio.to_thread(agent.track_shipment, shipment_data, dados.lang)
    await _persistir(dados.projeto_id, "logistics_track_shipment", str(shipment_data), resultado)
    return _responder("logistics_track_shipment", resultado, premium)


@router.post("/logistics/check-issues")
async def logistics_issues(dados: ItemsIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = LogisticsAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.check_delivery_issues, dados.items, dados.lang)
    resultado = {"agent": "logistics", "result": texto}
    await _persistir(dados.projeto_id, "logistics_check_issues", str(dados.items), resultado)
    return _responder("logistics_check_issues", resultado, premium)


# ---- Inventory ----
@router.post("/inventory/check-stock")
async def inventory_check(dados: ItemsIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = InventoryAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.check_stock, dados.items, dados.lang)
    await _persistir(dados.projeto_id, "inventory_check_stock", str(dados.items), resultado)
    return _responder("inventory_check_stock", resultado, premium)


@router.post("/inventory/suggest-substitute")
async def inventory_substitute(dados: TextPairIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = InventoryAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.suggest_substitute, dados.text_a, dados.text_b, dados.lang)
    resultado = {"agent": "inventory", "result": texto}
    await _persistir(dados.projeto_id, "inventory_suggest_substitute", f"{dados.text_a}\n---\n{dados.text_b}", resultado)
    return _responder("inventory_suggest_substitute", resultado, premium)


# ---- RFI Creation ----
@router.post("/rfi/create")
async def rfi_create(dados: QuestionIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = RFICreationAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.create_rfi, dados.question, dados.context, dados.lang)
    await _persistir(dados.projeto_id, "rfi_create", dados.question, resultado)
    return _responder("rfi_create", resultado, premium)


@router.post("/rfi/search-specification")
async def rfi_search(dados: QuestionIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = RFICreationAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.search_specification, dados.question, dados.context, dados.lang)
    resultado = {"agent": "rfi_creation", "result": texto}
    await _persistir(dados.projeto_id, "rfi_search_specification", dados.question, resultado)
    return _responder("rfi_search_specification", resultado, premium)


# ---- Work Synopsis ----
@router.post("/work-synopsis/generate")
async def synopsis_generate(dados: TextIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = WorkSynopsisAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.generate_synopsis, dados.text, dados.lang)
    await _persistir(dados.projeto_id, "work_synopsis_generate", dados.text, resultado)
    return _responder("work_synopsis_generate", resultado, premium)


@router.post("/work-synopsis/status")
async def synopsis_status(dados: TextIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = WorkSynopsisAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.summarize_project_status, dados.text, dados.lang)
    resultado = {"agent": "work_synopsis", "result": texto}
    await _persistir(dados.projeto_id, "work_synopsis_status", dados.text, resultado)
    return _responder("work_synopsis_status", resultado, premium)


# ---- Engineering Assistant ----
@router.post("/engineering-assistant/ask")
async def assistant_ask(dados: QuestionIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = EngineeringAssistantAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.answer_question, dados.question, dados.context, dados.lang)
    await _persistir(dados.projeto_id, "engineering_assistant_ask", dados.question, resultado)
    return _responder("engineering_assistant_ask", resultado, premium)


@router.post("/engineering-assistant/summarize")
async def assistant_summarize(dados: TextIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = EngineeringAssistantAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.summarize_document, dados.text, dados.lang)
    resultado = {"agent": "engineering_assistant", "result": texto}
    await _persistir(dados.projeto_id, "engineering_assistant_summarize", dados.text, resultado)
    return _responder("engineering_assistant_summarize", resultado, premium)


# ---- Photo Intelligence ----
@router.post("/photo-intelligence/analyze")
async def photo_analyze(dados: TextIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = PhotoIntelligenceAgent(Settings(), _llm())
    resultado = await asyncio.to_thread(agent.analyze_photo, dados.text, dados.lang)
    await _persistir(dados.projeto_id, "photo_intelligence_analyze", dados.text, resultado)
    return _responder("photo_intelligence_analyze", resultado, premium)


@router.post("/photo-intelligence/compare-schedule")
async def photo_compare(dados: TextPairIn):
    premium = await _preparar(dados.projeto_id, dados.customer_email)
    agent = PhotoIntelligenceAgent(Settings(), _llm())
    texto = await asyncio.to_thread(agent.compare_with_schedule, dados.text_a, dados.text_b, dados.lang)
    resultado = {"agent": "photo_intelligence", "result": texto}
    await _persistir(dados.projeto_id, "photo_intelligence_compare_schedule", f"{dados.text_a}\n---\n{dados.text_b}", resultado)
    return _responder("photo_intelligence_compare_schedule", resultado, premium)
