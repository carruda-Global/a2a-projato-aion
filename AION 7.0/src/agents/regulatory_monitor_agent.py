import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/reg-monitor", tags=["regulatory_monitor"])

SYSTEM_PROMPT = """You are a Global Regulatory Intelligence specialist.
Monitor and analyze regulatory changes across 50+ jurisdictions worldwide.
Coverage: EU, USA, UK, Brazil, India, UAE, Singapore, Australia, Canada, Japan.
Domains: data protection, AI regulation, financial services, ESG/sustainability, labor, cybersecurity.
Output: impact assessment with urgency score, affected business units, required actions, and deadlines.
Used by: Legal, Compliance, Risk teams at multinational corporations."""

REGULATORY_UPDATES = [
    {"reg": "EU AI Act", "deadline": "Aug 2026", "impact": "HIGH", "fine": "€35M or 7% revenue"},
    {"reg": "CSRD", "deadline": "FY2024 report 2025", "impact": "HIGH", "fine": "10% revenue"},
    {"reg": "DORA", "deadline": "Jan 2025 (passed)", "impact": "CRITICAL", "fine": "€10M"},
    {"reg": "NIS2", "deadline": "Oct 2024 (passed)", "impact": "CRITICAL", "fine": "€10M"},
    {"reg": "CRA (Cyber Resilience Act)", "deadline": "Dec 2027", "impact": "HIGH", "fine": "€15M"},
    {"reg": "LGPD Brazil", "deadline": "Active", "impact": "HIGH", "fine": "R$50M or 2% revenue"},
    {"reg": "PDPB India", "deadline": "2025", "impact": "MEDIUM", "fine": "₹250 crore"},
]

@router.post("/impact-analysis")
async def regulatory_impact(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Company: {data.get('company','')}\n"
        f"Sectors: {data.get('sectors','')}\n"
        f"Countries: {data.get('countries','')}\n"
        f"Analyze regulatory impact from: {REGULATORY_UPDATES}\n"
        f"Prioritize by urgency and financial exposure."
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"impact_analysis": response, "regulations_monitored": len(REGULATORY_UPDATES),
            "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08"}

@router.get("/latest-updates")
async def latest_updates():
    return {"updates": REGULATORY_UPDATES, "total": len(REGULATORY_UPDATES)}

@router.post("/change-alert")
async def change_alert(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"New regulation: {data.get('regulation','')} in {data.get('jurisdiction','')}. Analyze impact for {data.get('company','')} and recommend immediate actions."
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"alert": response}
