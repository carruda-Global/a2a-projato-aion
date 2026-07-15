from fastapi import APIRouter, Request
from src.database.supabase_client import SupabaseClient
from src.config import Settings
import httpx

router = APIRouter(prefix="/api/visitor-id", tags=["visitor_id"])


class VisitorIDAgent:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def identify_visitor(self, ip: str, page_visited: str) -> dict:
        company_data = await self._reverse_ip_lookup(ip)
        if not company_data or not company_data.get("org"):
            return {"identified": False}

        market = self._detect_market(company_data.get("country", "BR"))
        lead = {
            "company_name": company_data.get("org"),
            "country": company_data.get("country"),
            "market": market,
            "page_visited": page_visited,
            "ip": ip,
        }
        await self._save_lead(lead)
        return {"identified": True, "lead": lead}

    def _detect_market(self, country: str) -> str:
        mapping = {"BR": "BR", "US": "US", "MX": "MX", "CO": "CO", "AR": "AR"}
        return mapping.get(country, "US")

    async def _reverse_ip_lookup(self, ip: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://ipapi.co/{ip}/json/")
        data = resp.json()
        return {"org": data.get("org"), "country": data.get("country_code")}

    async def _save_lead(self, lead: dict):
        db = SupabaseClient(self.settings)
        db.client.table("identified_leads").insert(lead).execute()


@router.post("/track")
async def track_visitor(request: Request):
    data = await request.json()
    client_ip = request.client.host
    page = data.get("page", "/")
    agent = VisitorIDAgent(Settings())
    return await agent.identify_visitor(client_ip, page)
