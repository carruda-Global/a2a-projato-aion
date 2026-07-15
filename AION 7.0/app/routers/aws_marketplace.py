import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.config import Settings
from src.monetization.aws_client import AWSMarketplaceClient
from src.monetization.plans import PLANS, get_plan

logger = logging.getLogger(__name__)

router = APIRouter()


class SubscriptionResponse(BaseModel):
    subscription_id: str
    customer_id: str
    plan_id: str
    status: str
    created_at: str
    redirect_url: str | None = None


class EntitlementResponse(BaseModel):
    active: bool
    customer_id: str
    dimension: str | None = None
    expiration: str | None = None


_active_subscriptions: dict[str, dict] = {}


@router.get("/subscribe")
async def subscribe(
    x_amzn_marketplace_token: str = Query(default="", alias="x-amzn-marketplace-token"),
    plan: str = Query(default="compliance_essencial"),
):
    if not x_amzn_marketplace_token:
        raise HTTPException(
            status_code=400,
            detail="Token AWS Marketplace nao fornecido. Faca subscribe via AWS Marketplace.",
        )

    settings = Settings()
    aws = AWSMarketplaceClient(settings)

    customer = aws.resolve_customer(x_amzn_marketplace_token)
    if not customer:
        raise HTTPException(
            status_code=400,
            detail="Falha ao validar token AWS Marketplace. Token invalido ou expirado.",
        )

    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    subscription_id = f"aws_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    _active_subscriptions[customer["customer_id"]] = {
        "subscription_id": subscription_id,
        "customer_id": customer["customer_id"],
        "customer_aws_account_id": customer.get("customer_aws_account_id", ""),
        "plan_id": plan,
        "plan_name": plan_info["name"],
        "status": "active",
        "created_at": now,
    }

    logger.info(
        "Novo subscribe AWS: customer=%s plan=%s sub=%s",
        customer["customer_id"],
        plan,
        subscription_id,
    )

    redirect_url = settings.aws_subscribe_redirect_url or (
        f"https://engenheiro-producao-ai.onrender.com/dashboard?"
        f"subscription_id={subscription_id}"
    )

    return SubscriptionResponse(
        subscription_id=subscription_id,
        customer_id=customer["customer_id"],
        plan_id=plan,
        status="active",
        created_at=now,
        redirect_url=redirect_url,
    )


@router.post("/sns")
async def sns_notification(request: Request):
    settings = Settings()
    aws = AWSMarketplaceClient(settings)

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    result = aws.process_sns_notification(payload)

    action = result["action"]
    customer_id = result["customer_id"]

    if action == "subscribe":
        if customer_id and customer_id not in _active_subscriptions:
            _active_subscriptions[customer_id] = {
                "subscription_id": f"aws_{uuid.uuid4().hex[:12]}",
                "customer_id": customer_id,
                "plan_id": "compliance_essencial",
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
            }
    elif action in ("unsubscribe", "expire"):
        if customer_id and customer_id in _active_subscriptions:
            _active_subscriptions[customer_id]["status"] = "cancelled"

    logger.info("SNS processado: action=%s customer=%s", action, customer_id)
    return {"received": True, "action": action}


@router.get("/entitlement/{customer_id}")
async def check_entitlement(customer_id: str):
    settings = Settings()
    aws = AWSMarketplaceClient(settings)

    local_sub = _active_subscriptions.get(customer_id)
    if local_sub and local_sub["status"] == "active":
        return EntitlementResponse(
            active=True,
            customer_id=customer_id,
            dimension=local_sub.get("plan_id", "compliance_essencial"),
        )

    aws_entitlement = aws.get_entitlement(customer_id)
    if aws_entitlement and aws_entitlement["status"] == "Active":
        return EntitlementResponse(
            active=True,
            customer_id=customer_id,
            dimension=aws_entitlement["dimension"],
        )

    return EntitlementResponse(active=False, customer_id=customer_id)


@router.get("/verify")
async def verify_subscription(
    customer_id: str = Query(...),
    plan: str = Query(default="compliance_essencial"),
):
    settings = Settings()
    aws = AWSMarketplaceClient(settings)

    local_sub = _active_subscriptions.get(customer_id)
    if local_sub and local_sub["status"] == "active":
        return {"valid": True, "customer_id": customer_id, "plan": local_sub["plan_id"]}

    is_active = aws.is_subscription_active(customer_id)
    return {"valid": is_active, "customer_id": customer_id, "plan": plan if is_active else None}


@router.get("/plans")
async def list_aws_plans():
    aws_plans = []
    for plan in PLANS:
        aws_plans.append({
            "id": plan["id"],
            "name": plan["name"],
            "price": f"R$ {plan['price'] / 100:,.2f}",
            "price_usd": f"${plan['price'] / 600:,.2f}",
            "agents": plan["agents"],
            "features": plan["features"],
        })
    return {"plans": aws_plans, "product_code": "prod_engenheiro_producao_ai"}
