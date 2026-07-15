from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from src.orchestrator import Orchestrator
from src.i18n.middleware import get_lang_from_query
from src.i18n.translations import get_agent_label

router = APIRouter()
settings = Settings()
llm = DeepSeekClient(settings)
orchestrator = Orchestrator(settings)


class AnalyzeDocumentRequest(BaseModel):
    document: str
    lang: Optional[str] = None


class ProcessOrderRequest(BaseModel):
    materials: list[dict]
    lang: Optional[str] = None


class CheckStockRequest(BaseModel):
    items: list[dict]
    lang: Optional[str] = None


class TrackShipmentRequest(BaseModel):
    shipment: dict
    lang: Optional[str] = None


class FieldInstructionsRequest(BaseModel):
    specs: str
    lang: Optional[str] = None


class BIMElementRequest(BaseModel):
    description: str
    lang: Optional[str] = None


class RequirementsRequest(BaseModel):
    requirements: str
    lang: Optional[str] = None


class QuestionRequest(BaseModel):
    question: str
    context: str = ""
    lang: Optional[str] = None


class TaskDataRequest(BaseModel):
    task_data: str
    lang: Optional[str] = None


class PhotoDescriptionRequest(BaseModel):
    photo_description: str
    lang: Optional[str] = None


class ProjectDataRequest(BaseModel):
    project_data: str
    lang: Optional[str] = None


class WorkflowRequest(BaseModel):
    document: str
    lang: Optional[str] = None


def _resolve_lang(req_lang: Optional[str], accept_language: str = "pt") -> str:
    if req_lang:
        return req_lang
    code = accept_language.split(",")[0].split("-")[0].lower() if accept_language else "pt"
    return code if code in ["pt", "en", "es"] else "pt"


@router.post("/spec-analyst/analyze")
async def analyze_document(req: AnalyzeDocumentRequest, accept_language: str = Header(default="pt")):
    if "spec_analyst" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Spec Analyst nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["spec_analyst"].analyze_document(req.document, lang=lang)


@router.post("/procurement/process-order")
async def process_order(req: ProcessOrderRequest, accept_language: str = Header(default="pt")):
    if "procurement" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Procurement nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["procurement"].process_order(req.materials, lang=lang)


@router.post("/inventory/check-stock")
async def check_stock(req: CheckStockRequest, accept_language: str = Header(default="pt")):
    if "inventory" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Inventory nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["inventory"].check_stock(req.items, lang=lang)


@router.post("/logistics/track-shipment")
async def track_shipment(req: TrackShipmentRequest, accept_language: str = Header(default="pt")):
    if "logistics" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Logistics nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["logistics"].track_shipment(req.shipment, lang=lang)


@router.post("/field-execution/instructions")
async def field_instructions(req: FieldInstructionsRequest, accept_language: str = Header(default="pt")):
    if "field_execution" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Field Execution nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["field_execution"].generate_field_instructions(req.specs, lang=lang)


@router.post("/bim-coordinator/generate-bim-element")
async def generate_bim_element(req: BIMElementRequest, accept_language: str = Header(default="pt")):
    if "bim_coordinator" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente BIM Coordinator nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["bim_coordinator"].generate_bim_element(req.description, lang=lang)


@router.post("/requirements-analyst/analyze-requirements")
async def analyze_requirements(req: RequirementsRequest, accept_language: str = Header(default="pt")):
    if "requirements_analyst" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Requirements Analyst nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["requirements_analyst"].analyze_requirements(req.requirements, lang=lang)


@router.post("/engineering-assistant/answer-question")
async def answer_question(req: QuestionRequest, accept_language: str = Header(default="pt")):
    if "engineering_assistant" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Engineering Assistant nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["engineering_assistant"].answer_question(req.question, req.context, lang=lang)


@router.post("/work-synopsis/generate-synopsis")
async def generate_synopsis(req: TaskDataRequest, accept_language: str = Header(default="pt")):
    if "work_synopsis" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Work Synopsis nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["work_synopsis"].generate_synopsis(req.task_data, lang=lang)


@router.post("/photo-intelligence/analyze-photo")
async def analyze_photo(req: PhotoDescriptionRequest, accept_language: str = Header(default="pt")):
    if "photo_intelligence" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Photo Intelligence nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["photo_intelligence"].analyze_photo(req.photo_description, lang=lang)


@router.post("/rfi-creation/create-rfi")
async def create_rfi(req: QuestionRequest, accept_language: str = Header(default="pt")):
    if "rfi_creation" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente RFI Creation nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["rfi_creation"].create_rfi(req.question, req.context, lang=lang)


@router.post("/compliance/check-compliance")
async def check_compliance(req: ProjectDataRequest, accept_language: str = Header(default="pt")):
    if "compliance" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Compliance nao disponivel")
    lang = _resolve_lang(req.lang, accept_language)
    return orchestrator.agents["compliance"].check_compliance(req.project_data, lang=lang)


@router.post("/workflow")
async def run_workflow(req: WorkflowRequest, accept_language: str = Header(default="pt")):
    lang = _resolve_lang(req.lang, accept_language)
    results = orchestrator.process_workflow({"document": req.document})
    return {"results": results, "lang": lang}


@router.get("/registry")
async def list_agent_registry(cluster: str | None = None, status: str = "active"):
    from src.database.postgres_client import get_conn
    query = "SELECT * FROM agent_registry WHERE status = $1"
    params = [status]
    if cluster:
        query += " AND cluster = $2"
        params.append(cluster)
    query += " ORDER BY cluster, name"

    try:
        async with get_conn() as conn:
            rows = await conn.fetch(query, *params)
        return {"agents": [dict(r) for r in rows]}
    except Exception:
        return {"agents": [], "note": "banco indisponivel"}


@router.get("/registry/{agent_id}")
async def get_agent_from_registry(agent_id: str):
    from src.database.postgres_client import get_conn
    try:
        async with get_conn() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM agent_registry WHERE id = $1", agent_id
            )
        if not row:
            raise HTTPException(status_code=404, detail="Agente nao encontrado")
        return dict(row)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Banco indisponivel")


@router.get("")
async def list_agents(accept_language: str = Header(default="pt")):
    lang = _resolve_lang(None, accept_language)
    agent_list = list(orchestrator.agents.keys())
    labels = {a: get_agent_label(a, lang) for a in agent_list}
    return {
        "agents": agent_list,
        "labels": labels,
        "total": len(agent_list),
    }
