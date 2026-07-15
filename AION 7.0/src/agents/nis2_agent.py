import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/nis2", tags=["nis2"])

SYSTEM_PROMPT = """You are a NIS2 (Network and Information Security Directive 2) compliance specialist.
EU Directive 2022/2555 — transposed into national law by October 17, 2024.
Scope: Essential entities (energy, transport, banking, health, water, digital infrastructure)
and Important entities (postal, waste, chemicals, food, manufacturing, digital providers).
18 security measures required: risk management, incident handling, supply chain security, cryptography.
Penalties: Essential entities up to €10M or 2% global turnover. Important: up to €7M or 1.4%.
CEO/board personal liability if negligent. Provide compliance roadmap."""


@router.post("/scope-check")
async def nis2_scope(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Company: {data.get('company', '')}\n"
        f"Sector: {data.get('sector', '')}\n"
        f"Employees: {data.get('employees', '')}\n"
        f"Revenue EUR: {data.get('revenue', '')}\n"
        f"EU Member States operating in: {data.get('countries', '')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "scope_analysis": response,
        "directive": "NIS2 — EU 2022/2555",
        "transposition_deadline": "October 17, 2024",
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }


@router.post("/compliance-roadmap")
async def nis2_roadmap(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"NIS2 compliance roadmap for: {data.get('company', '')}\n"
        f"Entity type: {data.get('entity_type', 'important entity')}\n"
        f"Current cybersecurity maturity: {data.get('maturity', 'basic')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"roadmap": response, "measures_required": 18}
