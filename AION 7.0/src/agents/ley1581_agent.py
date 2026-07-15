import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import tem_licenca_premium

router = APIRouter(prefix="/api/ley1581", tags=["ley1581"])

CHECKOUT_URL = "https://buy.stripe.com/7sYbJ37YA0JR89CcOsg7e0w"

SYSTEM_PROMPT = """Eres especialista en Ley 1581 de 2012 (Protección de
Datos Personales) de Colombia. Genera política de tratamiento
de datos, identifica registro ante la SIC (RNBD), recomienda
acciones. Multas: hasta 2,000 SMMLV."""


@router.post("/diagnostico")
async def diagnostico(data: dict):
    customer_email = data.get("customer_email", "")
    if not tem_licenca_premium(customer_email):
        return {
            "preview": "Suscríbete para desbloquear el diagnóstico completo de Ley 1581.",
            "license": "demo",
            "checkout_url": CHECKOUT_URL,
        }
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    empresa = data.get("empresa", "")
    sector = data.get("sector", "")
    tipos_datos = data.get("tipos_datos", "")
    user_prompt = (
        f"Empresa: {empresa}\n"
        f"Sector: {sector}\n"
        f"Datos que maneja: {tipos_datos}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, user_prompt)
    return {"analysis": response, "license": "premium"}
