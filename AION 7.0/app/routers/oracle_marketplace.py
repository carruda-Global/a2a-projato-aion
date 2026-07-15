import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.config import Settings
from src.monetization.oracle_client import OracleMarketplaceClient
from src.monetization.plans import PLANS, get_plan

logger = logging.getLogger(__name__)

router = APIRouter()

_active_subscriptions: dict[str, dict] = {}


class OracleActivationResponse(BaseModel):
    status: str
    subscription_id: str | None = None
    customer_tenancy_id: str | None = None
    plan: str | None = None
    redirect_url: str | None = None
    message: str | None = None


class OracleSubscriptionResponse(BaseModel):
    subscription_id: str
    customer_tenancy_id: str
    plan_id: str
    status: str
    created_at: str
    redirect_url: str | None = None


@router.get("/activate")
async def activate(
    token: str = Query(default="", alias="token"),
    product_id: str = Query(default="", alias="product_id"),
    plan: str = Query(default="compliance_essencial"),
):
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Token Oracle Marketplace nao fornecido. Token JWT necessario.",
        )

    settings = Settings()
    oracle = OracleMarketplaceClient(settings)

    resolved = oracle.resolve_subscription(token)
    if not resolved:
        raise HTTPException(
            status_code=400,
            detail="Falha ao validar token Oracle Marketplace. Token invalido ou expirado.",
        )

    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    subscription_id = resolved["subscription_id"]
    customer_tenancy_id = resolved["customer_tenancy_id"]
    now = datetime.utcnow().isoformat()

    _active_subscriptions[customer_tenancy_id] = {
        "subscription_id": subscription_id,
        "customer_tenancy_id": customer_tenancy_id,
        "plan_id": plan,
        "plan_name": plan_info["name"],
        "status": "pending_activation",
        "created_at": now,
    }

    activated = oracle.activate_subscription(subscription_id)
    if activated:
        _active_subscriptions[customer_tenancy_id]["status"] = "active"

    status = "active" if activated else "pending_activation"
    logger.info(
        "Oracle activation: tenancy=%s plan=%s sub=%s status=%s",
        customer_tenancy_id, plan, subscription_id, status,
    )

    redirect_url = (
        f"https://engenheiro-producao-ai.onrender.com/dashboard?"
        f"subscription_id={subscription_id}&source=oracle"
    )

    return OracleActivationResponse(
        status=status,
        subscription_id=subscription_id,
        customer_tenancy_id=customer_tenancy_id,
        plan=plan,
        redirect_url=redirect_url,
        message="Assinatura ativada com sucesso!" if activated else "Assinatura pendente de ativacao.",
    )


@router.get("/subscriptions")
async def list_subscriptions():
    settings = Settings()
    oracle = OracleMarketplaceClient(settings)
    subs = oracle.list_subscriptions()
    return {
        "subscriptions": subs,
        "total": len(subs),
        "product_id": settings.oracle_product_id,
    }


@router.get("/subscription/{customer_tenancy_id}")
async def get_subscription(customer_tenancy_id: str):
    local_sub = _active_subscriptions.get(customer_tenancy_id)
    if local_sub:
        return {
            "active": local_sub["status"] == "active",
            "subscription_id": local_sub["subscription_id"],
            "customer_tenancy_id": customer_tenancy_id,
            "plan": local_sub["plan_id"],
            "status": local_sub["status"],
            "created_at": local_sub["created_at"],
        }

    settings = Settings()
    oracle = OracleMarketplaceClient(settings)
    for sub in oracle.list_subscriptions():
        if sub["tenant_id"] == customer_tenancy_id:
            return {
                "active": sub["state"] == "ACTIVE",
                "subscription_id": sub["subscription_id"],
                "customer_tenancy_id": customer_tenancy_id,
                "status": sub["state"],
            }

    return {
        "active": False,
        "customer_tenancy_id": customer_tenancy_id,
        "message": "Assinatura nao encontrada",
    }


@router.post("/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("eventType", "")
    subscription_id = payload.get("subscriptionId", "")

    if event_type == "SUBSCRIPTION_ACTIVATED":
        logger.info("Oracle subscription activated: %s", subscription_id)
    elif event_type == "SUBSCRIPTION_SUSPENDED":
        logger.info("Oracle subscription suspended: %s", subscription_id)
        for tenancy, sub in _active_subscriptions.items():
            if sub.get("subscription_id") == subscription_id:
                sub["status"] = "suspended"
    elif event_type == "SUBSCRIPTION_CANCELLED":
        logger.info("Oracle subscription cancelled: %s", subscription_id)
        for tenancy, sub in _active_subscriptions.items():
            if sub.get("subscription_id") == subscription_id:
                sub["status"] = "cancelled"
    else:
        logger.info("Oracle webhook evento: %s", event_type)

    return {"received": True, "event_type": event_type, "subscription_id": subscription_id}


@router.get("/plans")
async def list_plans():
    oracle_plans = []
    for plan in PLANS:
        price_usd = plan["price"] / 600
        oracle_plans.append({
            "id": plan["id"],
            "name": plan["name"],
            "price_brl": f"R$ {plan['price'] / 100:,.2f}",
            "price_usd": f"${price_usd:,.2f}",
            "agents": plan["agents"],
            "features": plan["features"],
        })
    return {
        "plans": oracle_plans,
        "product_id": "EngenheiroProducaoAI_SaaS",
    }
