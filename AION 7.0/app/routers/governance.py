from fastapi import APIRouter, Request
from src.agents.universal_governance import UniversalGovernanceLayer

router = APIRouter(prefix="/api/governance", tags=["governance"])


@router.post("/intercept")
async def intercept_agent_action(request: Request):
    data = await request.json()
    platform = request.headers.get("X-Platform", "ecosystem")
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    gov = UniversalGovernanceLayer()
    result = await gov.execute({
        "action": "intercept",
        "agent_id": data.get("agent_id"),
        "platform": platform,
        "action_type": data.get("action_type"),
        "payload": data.get("payload", {}),
        "tenant_id": tenant_id
    })
    return result


@router.get("/dashboard/{tenant_id}")
async def governance_dashboard(tenant_id: str):
    gov = UniversalGovernanceLayer()
    return await gov.execute({"action": "dashboard", "tenant_id": tenant_id})
