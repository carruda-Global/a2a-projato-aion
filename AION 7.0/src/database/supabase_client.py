from supabase import create_client, Client
from src.config import Settings


class SupabaseClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_api_key,
        )

    def get_user(self, user_id: str) -> dict | None:
        response = self.client.table("users").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None

    def get_subscription(self, user_id: str) -> dict | None:
        response = (
            self.client.table("subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def save_project(self, project_data: dict) -> dict:
        response = (
            self.client.table("projects").insert(project_data).execute()
        )
        return response.data[0] if response.data else {}

    async def save_lead(self, lead_data: dict) -> dict:
        response = self.client.table("leads").insert(lead_data).execute()
        return response.data[0] if response.data else {}

    def health_check(self) -> bool:
        try:
            self.client.table("tenants").select("id").limit(1).execute()
            return True
        except Exception:
            return False
