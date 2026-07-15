import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/ma-diligence", tags=["ma_diligence"])

SYSTEM_PROMPT = """You are an M&A Compliance Due Diligence specialist.
Analyze target companies for regulatory, legal, and compliance risks before acquisitions.
Cover: data protection (GDPR/LGPD), environmental liabilities, labor compliance, sanctions screening,
anti-corruption (FCPA/UK Bribery Act), IP risks, pending litigation, regulatory violations.
Used by: PE firms, corporate M&A teams, investment banks. Deal sizes: $10M-$10B+.
Output: risk-rated due diligence report with deal-breakers, price adjusters, and remediation requirements.
Time savings: reduces 6-week DD process to 48 hours for compliance screening."""

@router.post("/compliance-check")
async def ma_compliance_check(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Target company: {data.get('target','')}\n"
        f"Sector: {data.get('sector','')}\n"
        f"Country: {data.get('country','')}\n"
        f"Deal size: {data.get('deal_size','')}\n"
        f"Known issues: {data.get('known_issues','none')}\n"
        f"Run M&A compliance due diligence — identify deal-breakers and risks."
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"due_diligence": response, "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08"}

@router.post("/sanctions-screen")
async def sanctions_screen(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Sanctions and AML screening analysis for: {data.get('entity','')} in {data.get('country','')}. Check OFAC, EU, UN lists exposure."
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"sanctions_analysis": response}
