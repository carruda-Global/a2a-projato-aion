from fastapi import APIRouter
from src.database.supabase_client import SupabaseClient
from src.config import Settings
from src.fulfillment.provisioning.activate_tenant import TenantsAPI

router = APIRouter(prefix="/api/status", tags=["status"])


def _get_tenants():
    return TenantsAPI(SupabaseClient(Settings()))


@router.get("/{tenant_id}")
async def get_tenant_status(tenant_id: str):
    t = _get_tenants()
    tenant = t.get_tenant(tenant_id)
    if not tenant:
        return {"error": "Tenant nao encontrado"}
    return {
        "tenant_id": tenant["id"],
        "name": tenant["name"],
        "plan": tenant["plan_name"],
        "status": tenant["status"],
        "agents": tenant.get("agents", []),
        "created_at": tenant.get("created_at"),
    }


@router.get("/{tenant_id}/agents")
async def get_tenant_agents(tenant_id: str):
    t = _get_tenants()
    agents = t.get_tenant_agents(tenant_id)
    return {"tenant_id": tenant_id, "agents": agents, "total": len(agents)}


@router.get("/email/{email}")
async def get_tenant_by_email(email: str):
    t = _get_tenants()
    tenant = t.get_tenant_by_email(email)
    if not tenant:
        return {"error": "Tenant nao encontrado para este email"}
    return {
        "tenant_id": tenant["id"],
        "name": tenant["name"],
        "plan": tenant["plan_name"],
        "status": tenant["status"],
    }
