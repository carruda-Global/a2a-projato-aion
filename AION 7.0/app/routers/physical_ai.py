from fastapi import APIRouter, Request, BackgroundTasks
from src.agents.physical_ai_connector import PhysicalAIConnector

router = APIRouter(prefix="/api/physical-ai", tags=["physical_ai"])


@router.post("/event")
async def receive_physical_event(request: Request, bg: BackgroundTasks):
    data = await request.json()
    source = request.headers.get("X-Source", "unknown")
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    connector = PhysicalAIConnector()
    bg.add_task(connector.process_event, data.get("event_type"), data, source, tenant_id)
    return {"status": "received", "event_type": data.get("event_type")}


@router.get("/events/{tenant_id}")
async def get_physical_events(tenant_id: str, limit: int = 50):
    return {"events": [], "total": 0}


@router.get("/carbon/realtime/{tenant_id}")
async def get_realtime_carbon(tenant_id: str):
    return {"total_tco2": 0}
