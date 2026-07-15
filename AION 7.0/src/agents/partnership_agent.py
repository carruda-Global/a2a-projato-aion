import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/partnership", tags=["partnership"])

SYSTEM_PROMPT = """You are a B2B partnership and channel sales specialist.
Help identify, qualify and recruit reseller partners for compliance AI software.
Target partners: accounting firms, law firms, management consultancies, HR consulting firms.
Commission structure: 30% recurring monthly commission on all referred subscriptions.
Our product: EcoSystem AEC + Regulatory — 71 AI agents, plans from R$590/month to R$19,997/month.
Write personalized partnership proposals and qualification frameworks."""

PARTNER_TYPES = {
    "accounting": "Tax and accounting firms advising SMEs on compliance",
    "legal": "Law firms specializing in labor, environmental, data protection law",
    "hr_consulting": "HR consultancies helping companies with NR-1, LGPD, eSocial",
    "it_consulting": "IT consultancies implementing ERP/CRM needing compliance layer",
    "management": "Management consultancies doing digital transformation projects",
}


@router.post("/qualify-partner")
async def qualify_partner(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Qualify this potential reseller partner:\n"
        f"Company: {data.get('company', '')}\n"
        f"Type: {data.get('partner_type', '')}\n"
        f"Clients: {data.get('client_base', '')}\n"
        f"Revenue: {data.get('revenue', '')}\n"
        f"Generate: qualification score (0-100), fit analysis, partnership proposal email"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "qualification": response,
        "commission": "30% recurring MRR",
        "partner_portal": "https://global-engenharia.com/ecosystem",
    }


@router.post("/generate-proposal")
async def generate_proposal(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    partner_type = data.get("partner_type", "accounting")
    prompt = (
        f"Write a partnership proposal for a {partner_type} firm:\n"
        f"Company: {data.get('company', '')}\n"
        f"Include: value proposition, commission structure (30% MRR), onboarding process, co-marketing"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"proposal": response}


@router.get("/partner-types")
async def list_partner_types():
    return {"partner_types": PARTNER_TYPES, "commission": "30% recurring"}
