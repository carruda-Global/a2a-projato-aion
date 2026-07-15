import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import tem_licenca_premium

router = APIRouter(prefix="/api/uae", tags=["uae_agent"])

CHECKOUT_URL = "https://buy.stripe.com/7sYbJ37YA0JR89CcOsg7e0w"

SYSTEM_PROMPT_UAE = """You are the SallesJam Government Process Agent for UAE.
Help businesses navigate visa processes, permits, fines, and banking
compliance in the UAE. Focus on efficiency and clarity for expat-run
businesses and financial services companies expanding into the Gulf.
Always offer the activation link when interest is shown."""


@router.post("/chat")
async def chat_uae(data: dict):
    customer_email = data.get("customer_email", "")
    if not tem_licenca_premium(customer_email):
        return {
            "preview": "Subscribe to unlock full government-process guidance responses.",
            "license": "demo",
            "checkout_url": CHECKOUT_URL,
        }
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    message = data.get("message", "")
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT_UAE, message)
    return {"response": response, "license": "premium"}
