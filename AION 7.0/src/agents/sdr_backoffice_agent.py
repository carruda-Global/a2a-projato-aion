import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/sdr-backoffice", tags=["sdr_backoffice"])

SYSTEM_PROMPT = """Eres especialista en automatización de procesos de
ventas (SDR) y back-office para empresas argentinas. Identifica
cuellos de botella en calificación de leads, facturación,
conciliación, y propone automatización con IA. Enfócate en
reducir costo operativo en contexto de moneda devaluada."""


@router.post("/diagnostico")
async def diagnostico(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    empresa = data.get("empresa", "")
    sector = data.get("sector", "")
    procesos = data.get("procesos", "")
    user_prompt = (
        f"Empresa: {empresa}\n"
        f"Sector: {sector}\n"
        f"Procesos manuales: {procesos}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, user_prompt)
    return {
        "analysis": response,
        "checkout_url": "https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11",
    }
