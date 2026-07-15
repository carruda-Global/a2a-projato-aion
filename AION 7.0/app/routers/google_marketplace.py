import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.app_utils.marketplace_auth import require_marketplace_admin_secret
from src.config import Settings, get_settings
from src.monetization.google_client import GoogleCloudMarketplaceClient
from src.monetization.plans import PLANS, get_plan

logger = logging.getLogger(__name__)

router = APIRouter()


class GoogleActivationResponse(BaseModel):
    status: str
    subscription_id: str | None = None
    customer_id: str | None = None
    plan: str | None = None
    redirect_url: str | None = None


class GoogleEntitlementResponse(BaseModel):
    active: bool
    customer_id: str
    plan: str | None = None
    state: str | None = None


class GoogleWebhookResponse(BaseModel):
    received: bool
    event_type: str | None = None
    entitlement_id: str | None = None


_active_subscriptions: dict[str, dict] = {}


@router.get("/subscribe")
async def subscribe(
    request: Request,
    plan: str = Query(default="compliance_essencial"),
    customer_id: str = Query(default=""),
):
    require_marketplace_admin_secret(request, get_settings().marketplace_admin_secret)

    if not customer_id:
        raise HTTPException(
            status_code=400,
            detail="customer_id é obrigatório. Fornecido pelo Google Cloud Marketplace após assinatura.",
        )

    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    subscription_id = f"gcp_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    _active_subscriptions[customer_id] = {
        "subscription_id": subscription_id,
        "customer_id": customer_id,
        "plan_id": plan,
        "plan_name": plan_info["name"],
        "status": "active",
        "created_at": now,
    }

    redirect_url = (
        f"https://engenheiro-producao-ai.onrender.com/dashboard?"
        f"subscription_id={subscription_id}&source=google"
    )
    logger.info("Google subscribe: customer=%s plan=%s", customer_id, plan)

    return GoogleActivationResponse(
        status="active",
        subscription_id=subscription_id,
        customer_id=customer_id,
        plan=plan,
        redirect_url=redirect_url,
    )


@router.post("/webhook")
async def handle_webhook(request: Request):
    require_marketplace_admin_secret(request, get_settings().marketplace_admin_secret)

    settings = Settings()
    client = GoogleCloudMarketplaceClient(settings)

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("eventType", "")
    entitlement_id = payload.get("entitlementId", "")

    if event_type == "ENTITLEMENT_CANCELLED":
        customer_id = payload.get("customerId", entitlement_id)
        if customer_id in _active_subscriptions:
            _active_subscriptions[customer_id]["status"] = "cancelled"
        logger.info("Google entitlement cancelled: %s", entitlement_id)

    elif event_type == "ENTITLEMENT_SUSPENDED":
        customer_id = payload.get("customerId", entitlement_id)
        if customer_id in _active_subscriptions:
            _active_subscriptions[customer_id]["status"] = "suspended"
        logger.info("Google entitlement suspended: %s", entitlement_id)

    elif event_type == "ENTITLEMENT_RENEWED":
        customer_id = payload.get("customerId", entitlement_id)
        if customer_id in _active_subscriptions:
            _active_subscriptions[customer_id]["status"] = "active"
        logger.info("Google entitlement renewed: %s", entitlement_id)

    elif event_type == "ENTITLEMENT_CREATED":
        customer_id = payload.get("customerId", entitlement_id)
        subscription_id = f"gcp_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()
        _active_subscriptions[customer_id] = {
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "plan_id": payload.get("planId", "compliance_essencial"),
            "status": "active",
            "created_at": now,
        }
        logger.info("Google entitlement created: %s", entitlement_id)

    else:
        logger.info("Google webhook evento desconhecido: %s", event_type)

    return GoogleWebhookResponse(
        received=True,
        event_type=event_type,
        entitlement_id=entitlement_id,
    )


@router.post("/fulfill")
async def fulfill_subscription(request: Request):
    require_marketplace_admin_secret(request, get_settings().marketplace_admin_secret)

    settings = Settings()
    client = GoogleCloudMarketplaceClient(settings)

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    entitlement_id = payload.get("entitlementId") or payload.get("entitlement_id", "")
    plan_id = payload.get("planId") or payload.get("plan_id", "compliance_essencial")
    customer_email = payload.get("customerEmail") or payload.get("customer_email", "")

    if not entitlement_id:
        raise HTTPException(status_code=400, detail="entitlementId é obrigatório")

    plan_info = get_plan(plan_id)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    subscription_id = f"gcp_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    _active_subscriptions[entitlement_id] = {
        "subscription_id": subscription_id,
        "entitlement_id": entitlement_id,
        "customer_email": customer_email,
        "plan_id": plan_id,
        "plan_name": plan_info["name"],
        "status": "active",
        "created_at": now,
    }

    logger.info(
        "Google fulfillment: entitlement=%s plan=%s email=%s",
        entitlement_id, plan_id, customer_email,
    )

    return {
        "status": "fulfilled",
        "subscription_id": subscription_id,
        "entitlement_id": entitlement_id,
        "plan": plan_id,
        "message": "Assinatura ativada com sucesso!",
    }


@router.get("/entitlement/{customer_id}")
async def check_entitlement(customer_id: str):
    sub = _active_subscriptions.get(customer_id)
    if sub and sub["status"] == "active":
        return GoogleEntitlementResponse(
            active=True,
            customer_id=customer_id,
            plan=sub["plan_id"],
            state="ACTIVE",
        )

    settings = Settings()
    client = GoogleCloudMarketplaceClient(settings)
    gcp_entitlement = client.resolve_entitlement(customer_id)
    if gcp_entitlement:
        return GoogleEntitlementResponse(
            active=gcp_entitlement.get("state") == "ACTIVE",
            customer_id=customer_id,
            plan=gcp_entitlement.get("plan"),
            state=gcp_entitlement.get("state"),
        )

    return GoogleEntitlementResponse(active=False, customer_id=customer_id)


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
