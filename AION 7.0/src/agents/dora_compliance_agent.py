import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/dora", tags=["dora"])

SYSTEM_PROMPT = """You are a DORA (Digital Operational Resilience Act) compliance specialist.
EU Regulation 2022/2554 — applies to all financial entities in the EU.
In force since January 17, 2025. Scope: banks, insurers, investment firms, crypto-asset providers.
5 pillars: ICT risk management, incident reporting, resilience testing, third-party risk, info sharing.
Penalties: Up to 1% of average daily global turnover for 6 months, or up to €5M for individuals.
Provide specific DORA compliance roadmap with concrete technical and organizational measures."""


@router.post("/compliance-check")
async def dora_check(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Financial entity: {data.get('company', '')}\n"
        f"Type: {data.get('entity_type', 'bank/insurer/investment firm')}\n"
        f"Country: {data.get('country', '')}\n"
        f"Current ICT risk framework: {data.get('ict_framework', 'none')}\n"
        f"Third-party ICT providers: {data.get('ict_providers', 'unknown')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "analysis": response,
        "in_force": "January 17, 2025",
        "pillars": ["ICT Risk", "Incident Reporting", "TLPT Testing", "Third-Party Risk", "Info Sharing"],
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }


@router.post("/incident-report")
async def dora_incident(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Draft a DORA-compliant ICT incident report:\n"
        f"Incident: {data.get('incident', '')}\n"
        f"Impact: {data.get('impact', '')}\n"
        f"Systems affected: {data.get('systems', '')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"incident_report": response, "reporting_deadline": "4h initial, 72h detailed, 30d final"}
