from fastapi import APIRouter, Request
from src.database.supabase_client import SupabaseClient
import logging

router = APIRouter(prefix="/api/leads", tags=["leads"])
logger = logging.getLogger(__name__)


@router.post("/microsoft")
async def receive_microsoft_lead(request: Request):
    try:
        data = await request.json()
        db = SupabaseClient()
        db.table("leads").insert({
            "source": "microsoft_marketplace",
            "company": data.get("CompanyName", ""),
            "email": data.get("EmailAddress", ""),
            "name": f"{data.get('FirstName','')} {data.get('LastName','')}".strip(),
            "offer": data.get("OfferTitle", ""),
            "country": data.get("Country", ""),
            "phone": data.get("Phone", ""),
            "raw": str(data),
        }).execute()
        logger.info(f"Lead Microsoft recebido: {data.get('EmailAddress')}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Erro ao salvar lead: {e}")
        return {"status": "ok"}
