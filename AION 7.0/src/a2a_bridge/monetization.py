import logging

import stripe

from src.config import Settings

logger = logging.getLogger(__name__)


async def check_subscription(
    settings: Settings,
    api_key: str | None,
    agent_id: str,
) -> bool:
    if settings.app_env == "development":
        return True

    if not api_key:
        logger.warning("A2A request sem API key - acesso negado")
        return False

    plan_ids = _resolve_plan_for_agent(agent_id)
    if not plan_ids:
        return False

    try:
        stripe.api_key = settings.stripe_secret_key
        from src.database.supabase_client import SupabaseClient

        db = SupabaseClient(settings)
        user = db.get_user(api_key)
        if not user:
            logger.warning("API key invalida: %s", api_key[:8])
            return False

        sub = db.get_subscription(user["id"])
        if not sub:
            logger.warning("Usuario %s sem assinatura ativa", user["id"])
            return False

        user_plan_id = sub.get("plan_id", "")
        return user_plan_id in plan_ids
    except Exception as e:
        logger.error("Erro ao verificar assinatura: %s", e)
        return False


def _resolve_plan_for_agent(agent_id: str) -> list[str]:
    from src.monetization.plans import PLANS

    plans = []
    for plan in PLANS:
        if agent_id in plan["agents"]:
            plans.append(plan["id"])
    return plans
