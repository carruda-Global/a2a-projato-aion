from fastapi import APIRouter, Request
from src.agents.antigravity_bridge import AntigravityBridge
import uuid

router = APIRouter(prefix="/api/bridge", tags=["bridge"])


@router.post("/workflow")
async def create_workflow(request: Request):
    data = await request.json()
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    workflow_id = str(uuid.uuid4())
    bridge = AntigravityBridge()
    result = await bridge.execute({
        "action": "route",
        "workflow_id": workflow_id,
        "steps": data.get("steps", []),
        "tenant_id": tenant_id
    })
    return {"workflow_id": workflow_id, "status": "processing", **result}


@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    return {"workflow_id": workflow_id, "status": "completed"}
