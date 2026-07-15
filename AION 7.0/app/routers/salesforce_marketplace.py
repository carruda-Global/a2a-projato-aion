import json
import logging

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.app_utils.marketplace_auth import (
    require_marketplace_admin_secret,
    verify_hmac_signature,
)
from src.config import get_settings
from src.monetization.plans import PLANS, get_plan
from src.monetization.subscription_activator import (
    activate_subscription,
    deactivate_subscription,
    get_subscription as get_active_sub,
    get_subscription_by_id,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class SalesforceActivationResponse(BaseModel):
    status: str
    subscription_id: str | None = None
    plan: str | None = None
    redirect_url: str | None = None


@router.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-salesforce-signature", "")
    if not verify_hmac_signature(body, signature, get_settings().salesforce_webhook_secret):
        raise HTTPException(status_code=401, detail="Assinatura invalida")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("event_type", "")
    subscriber_id = payload.get("subscriber_id", "")

    logger.info("Salesforce webhook: %s subscriber=%s", event_type, subscriber_id)

    if event_type in ("SubscriptionCreate", "SubscriptionActivate"):
        activate_subscription(
            source="salesforce",
            external_id=subscriber_id,
            customer_id=payload.get("customer_id", subscriber_id),
            plan_id=payload.get("plan_id", "compliance_essencial"),
            customer_email=payload.get("customer_email", ""),
            customer_name=payload.get("customer_name", ""),
        )
    elif event_type in ("SubscriptionCancel", "SubscriptionExpire"):
        deactivate_subscription("salesforce", subscriber_id)

    return {"received": True, "event_type": event_type}


@router.get("/subscribe")
async def subscribe(
    request: Request,
    plan: str = Query(default="compliance_essencial"),
    subscriber_id: str = Query(default=""),
):
    require_marketplace_admin_secret(request, get_settings().marketplace_admin_secret)

    if not subscriber_id:
        raise HTTPException(
            status_code=400,
            detail="subscriber_id é obrigatório. Fornecido pelo Salesforce após assinatura.",
        )

    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    record = activate_subscription(
        source="salesforce",
        external_id=subscriber_id,
        customer_id=subscriber_id,
        plan_id=plan,
    )

    redirect_url = (
        f"https://engenheiro-producao-ai.onrender.com/dashboard?"
        f"source=salesforce&subscriber_id={subscriber_id}"
    )

    return SalesforceActivationResponse(
        status=record["status"],
        subscription_id=subscriber_id,
        plan=plan,
        redirect_url=redirect_url,
    )


@router.get("/subscription/{subscriber_id}")
async def get_subscription(subscriber_id: str):
    sub = get_active_sub("salesforce", subscriber_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura nao encontrada")
    return sub


@router.get("/plans")
async def list_plans():
    return {
        "plans": [
            {
                "id": p["id"],
                "name": p["name"],
                "price_usd": f"${p['price'] / 600:,.2f}",
                "agents": p["agents"],
                "features": p["features"],
            }
            for p in PLANS
        ]
    }
