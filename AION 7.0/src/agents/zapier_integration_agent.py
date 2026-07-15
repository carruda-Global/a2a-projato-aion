import asyncio
import httpx
import logging
from fastapi import APIRouter, Request
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/zapier", tags=["zapier"])
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a compliance automation specialist helping companies connect their tools.
When triggered by Zapier/Make.com webhooks, analyze the incoming data and run the appropriate compliance check.
Return structured, actionable output that can be used in downstream automations."""

SUPPORTED_TRIGGERS = {
    "new_employee": "Run NR-1, LGPD onboarding compliance check",
    "new_contract": "Run contract risk analysis for compliance clauses",
    "new_vendor": "Run vendor risk assessment",
    "data_breach": "Run LGPD/GDPR incident response protocol",
    "regulatory_change": "Analyze impact on company operations",
    "new_supplier": "Run CSRD supply chain compliance check",
}

@router.post("/trigger")
async def zapier_trigger(request: Request):
    """Universal webhook endpoint for Zapier/Make.com integrations."""
    data = await request.json()
    trigger_type = data.get("trigger", "general")
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    action = SUPPORTED_TRIGGERS.get(trigger_type, "Run general compliance check")
    prompt = (
        f"Triggered by: {trigger_type}\n"
        f"Action: {action}\n"
        f"Data: {str(data)[:1000]}\n"
        f"Provide immediate compliance guidance and next steps."
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "status": "processed",
        "trigger": trigger_type,
        "compliance_output": response,
        "powered_by": "EcoSystem AEC — global-engenharia.com/ecosystem",
    }

@router.post("/webhook/new-employee")
async def new_employee_compliance(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"New employee onboarding compliance for {data.get('company','')}. Employee: {data.get('role','')}. Check NR-1, LGPD, eSocial requirements."
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"compliance_checklist": response}

@router.post("/webhook/data-breach")
async def data_breach_response(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"DATA BREACH RESPONSE for {data.get('company','')}. Breach: {data.get('description','')}. Records: {data.get('records_affected','')}. Generate LGPD/GDPR incident response plan with ANPD/DPA notification timeline."
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"incident_response": response, "anpd_deadline": "72 hours", "gdpr_deadline": "72 hours"}

@router.get("/triggers")
async def list_triggers():
    return {"supported_triggers": SUPPORTED_TRIGGERS, "webhook_url": "https://engenheiro-producao-ai.onrender.com/api/zapier/trigger"}

@router.post("/press-release")
async def generate_press_release(data: dict):
    """Generate press release for distribution to TechCrunch, VentureBeat, etc."""
    deepseek = DeepSeekClient(Settings())
    pr_prompt = (
        "Write a compelling press release for B2B tech journalists:\n"
        "Headline angle: Brazilian AI startup launches 79 compliance agents covering EU AI Act, CSRD, DORA, NIS2, SOC2, ISO27001\n"
        f"Company: Global Match Engenharia — EcoSystem AEC + Regulatory\n"
        f"Key stats: 79 AI agents, 12 regulations, 8 countries, plans from $149/month\n"
        f"Unique angle: {data.get('angle','First platform to cover all major 2025-2026 regulatory deadlines in one product')}\n"
        "Format: headline, dateline, 4 paragraphs, boilerplate, contact info\n"
        "Target: TechCrunch, VentureBeat, RegTech Analyst, Compliance Week"
    )
    response = await asyncio.to_thread(deepseek.chat, "You are a tech PR specialist writing for B2B SaaS companies.", pr_prompt)
    return {"press_release": response, "distribution": ["OpenPR.com", "PRWeb", "EIN Presswire (free tier)"]}
