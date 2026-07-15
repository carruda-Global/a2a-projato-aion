import asyncio
from fastapi import APIRouter, Request
from src.api.deepseek_client import DeepSeekClient
from src.rag.hybrid_rag import HybridRAG
from src.database.supabase_client import SupabaseClient
from src.config import Settings
import logging

router = APIRouter(prefix="/api/sales-agent", tags=["sales_agent"])
logger = logging.getLogger(__name__)

SYSTEM_PROMPT_BR = """Você é o Sales Agent da SallesJam.
Qualifica o visitante, responde dúvidas sobre compliance regulatório
(NR-1, LGPD, CBS/IBS, ESG) com precisão, conduz para o plano certo.
Sempre termine oferecendo o link de ativação quando demonstrar interesse."""

SYSTEM_PROMPT_US = """You are the SallesJam Sales Agent for the US market.
Qualify visitors, answer questions about EU AI Act Article 50
compliance with precision, guide to the right plan.
Always end by offering the activation link when interest is shown."""

SYSTEM_PROMPT_MX = """Eres el Sales Agent de SallesJam para México.
Califica al visitante, responde dudas sobre cumplimiento LFPDPPP
con precisión, guía al plan correcto."""

SYSTEM_PROMPT_CO = """Eres el Sales Agent de SallesJam para Colombia.
Califica al visitante, responde dudas sobre cumplimiento Ley 1581
con precisión, guía al plan correcto."""

SYSTEM_PROMPT_AR = """Eres el Sales Agent de SallesJam para Argentina.
Califica al visitante para servicios de automatización SDR
y back-office, guía al plan correcto."""

STRIPE_LINKS_BR = {
    "compliance_essencial": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03",
    "regulatory_pro": "https://buy.stripe.com/14dRwr3Ik0JRfC44hWg7e04",
    "esg_carbono": "https://buy.stripe.com/6oUeVf3IkeAH4Xq7u8g7e06",
}

STRIPE_LINKS_US = {
    "eu_ai_act": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
}

STRIPE_LINKS_MX = {
    "lfpdppp": "https://buy.stripe.com/4gw6oV9Jk8QRfC47u8g7e09",
}

STRIPE_LINKS_CO = {
    "ley1581": "https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10",
}

STRIPE_LINKS_AR = {
    "sdr_backoffice": "https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11",
}


def get_system_prompt(market: str) -> str:
    prompts = {
        "BR": SYSTEM_PROMPT_BR,
        "US": SYSTEM_PROMPT_US,
        "MX": SYSTEM_PROMPT_MX,
        "CO": SYSTEM_PROMPT_CO,
        "AR": SYSTEM_PROMPT_AR,
    }
    return prompts.get(market, SYSTEM_PROMPT_BR)


def get_stripe_link(market: str, plan: str) -> str:
    links = {
        "BR": STRIPE_LINKS_BR,
        "US": STRIPE_LINKS_US,
        "MX": STRIPE_LINKS_MX,
        "CO": STRIPE_LINKS_CO,
        "AR": STRIPE_LINKS_AR,
    }
    market_links = links.get(market, STRIPE_LINKS_BR)
    return market_links.get(plan, STRIPE_LINKS_BR["compliance_essencial"])


def _detect_plan_interest(message: str, response: str, market: str) -> str:
    text = (message + " " + response).lower()
    if market == "BR":
        if "esg" in text or "carbono" in text:
            return "esg_carbono"
        if "igualdade" in text or "denúncia" in text or "denuncia" in text:
            return "regulatory_pro"
        if "nr-1" in text or "nr1" in text or "lgpd" in text or "ativar" in text:
            return "compliance_essencial"
    elif market == "US":
        if "ai act" in text or "article 50" in text or "ready" in text:
            return "eu_ai_act"
    elif market == "MX":
        if "lfpdppp" in text or "datos" in text or "activar" in text:
            return "lfpdppp"
    elif market == "CO":
        if "1581" in text or "datos" in text or "activar" in text:
            return "ley1581"
    elif market == "AR":
        if "sdr" in text or "automatiza" in text or "activar" in text:
            return "sdr_backoffice"
    return ""


@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    page = data.get("page", "/")
    market = data.get("market", "BR")

    settings = Settings()
    context = await HybridRAG().retrieve(message)
    context_text = str(context.get("results", []))[:2000]
    deepseek = DeepSeekClient(settings)

    system_prompt = get_system_prompt(market)
    response = await asyncio.to_thread(
        deepseek.chat,
        system_prompt,
        f"Página: {page}\nContexto: {context_text}\nPergunta: {message}",
    )

    plan = _detect_plan_interest(message, response, market)
    if plan:
        link = get_stripe_link(market, plan)
        response += f"\n\n🔗 {link}"

    try:
        db = SupabaseClient(settings)
        db.client.table("chat_logs").insert({
            "message": message, "response": response, "page": page, "market": market,
        }).execute()
    except Exception as e:
        logger.warning(f"Falha ao salvar chat_log: {e}")

    return {"response": response}
