import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import tem_licenca_premium

router = APIRouter(prefix="/api/india", tags=["india_agent"])

CHECKOUT_URL = "https://buy.stripe.com/7sYbJ37YA0JR89CcOsg7e0w"

SYSTEM_PROMPT_IN = """You are the SallesJam Multilingual Support Agent for India.
Respond in the language the user writes in - English, Hindi, or any regional language.
You help e-commerce and fintech companies automate customer support across
multiple Indian languages, reducing support team costs by 60-80%.
Always offer the activation link when interest is shown."""


@router.post("/chat")
async def chat_india(data: dict):
    customer_email = data.get("customer_email", "")
    if not tem_licenca_premium(customer_email):
        return {
            "preview": "Subscribe to unlock full multilingual support responses.",
            "license": "demo",
            "checkout_url": CHECKOUT_URL,
        }
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    message = data.get("message", "")
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT_IN, message)
    return {"response": response, "license": "premium"}
