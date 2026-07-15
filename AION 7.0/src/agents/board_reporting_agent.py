import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/board-report", tags=["board_reporting"])

SYSTEM_PROMPT = """You are a Board-level ESG and Compliance Reporting specialist.
Generate executive-ready reports for boards, audit committees, and C-suite.
Standards: TCFD, GRI, SASB, ESRS, CSRD, COSO framework.
Style: executive summary first, data-driven, risk-focused, actionable recommendations.
Include: compliance status dashboard, regulatory deadlines, financial exposure to non-compliance,
peer benchmarking, and strategic recommendations.
Output: structured board report with executive summary, key metrics, risks, and next steps."""

@router.post("/generate")
async def generate_board_report(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Company: {data.get('company','')}\n"
        f"Sector: {data.get('sector','')}\n"
        f"Period: {data.get('period','Q2 2026')}\n"
        f"Key regulations: {data.get('regulations','CSRD, EU AI Act, NIS2, DORA')}\n"
        f"Compliance status: {data.get('status','')}\n"
        f"Generate board-ready compliance and ESG report."
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"board_report": response, "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08"}

@router.post("/audit-committee")
async def audit_committee_report(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Generate audit committee report for {data.get('company','')} covering: {data.get('scope','internal controls, risk management, compliance')}"
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"audit_report": response}
