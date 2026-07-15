import logging
from src.database.supabase_client import SupabaseClient
from src.monetization.plans import get_plan_by_id

logger = logging.getLogger(__name__)


class TenantsAPI:
    def __init__(self, db: SupabaseClient):
        self.db = db

    def get_tenant(self, tenant_id: str) -> dict | None:
        r = self.db.client.table("tenants").select("*").eq("id", tenant_id).execute()
        return r.data[0] if r.data else None

    def get_tenant_by_email(self, email: str) -> dict | None:
        r = self.db.client.table("tenants").select("*").eq("email", email).execute()
        return r.data[0] if r.data else None

    def get_tenant_agents(self, tenant_id: str) -> list:
        r = self.db.client.table("tenants").select("agents").eq("id", tenant_id).execute()
        return r.data[0].get("agents", []) if r.data else []

    def update_tenant_plan(self, tenant_id: str, plan_id: str) -> dict:
        plan = get_plan_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plano invalido: {plan_id}")
        self.db.client.table("tenants").update({"plan_id": plan_id, "plan_name": plan["name"]}).eq("id", tenant_id).execute()
        logger.info(f"Tenant {tenant_id} atualizado para plano {plan['name']}")
        return self.get_tenant(tenant_id)

    def deactivate_tenant(self, tenant_id: str):
        self.db.client.table("tenants").update({"status": "inactive"}).eq("id", tenant_id).execute()
        logger.info(f"Tenant {tenant_id} desativado")
