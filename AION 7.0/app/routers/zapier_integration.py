import json
import logging
import os
import uuid

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.monetization.plans import PLANS
from src.monetization.subscription_activator import (
    activate_subscription,
    get_subscription as get_active_sub,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/zapier", tags=["zapier"])


class ZapierWebhookPayload(BaseModel):
    event: str = ""
    target_url: str = ""
    payload: dict = {}


class ZapierCheckRequest(BaseModel):
    api_key: str = ""
    service: str = "compliance-nr1"
    company: str = ""
    sector: str = ""
    data_types: str = ""
    ai_systems: str = ""
    frameworks: str = "nr1,lgpd,eu-ai-act"


@router.post("/webhook/subscribe")
async def subscribe_webhook(payload: ZapierWebhookPayload):
    if not payload.target_url:
        raise HTTPException(status_code=400, detail="target_url é obrigatorio")
    subscription_id = str(uuid.uuid4())
    _webhook_subscriptions[subscription_id] = {
        "event": payload.event,
        "target_url": payload.target_url,
        "payload_template": payload.payload,
    }
    logger.info(
        "Zapier webhook subscribed: event=%s target=%s sub=%s",
        payload.event, payload.target_url, subscription_id,
    )
    return {"subscription_id": subscription_id, "status": "active"}


@router.delete("/webhook/subscribe/{subscription_id}")
async def unsubscribe_webhook(subscription_id: str):
    removed = _webhook_subscriptions.pop(subscription_id, None)
    if not removed:
        raise HTTPException(status_code=404, detail="Subscription nao encontrada")
    return {"status": "removed", "subscription_id": subscription_id}


@router.get("/health")
async def health_check():
    return {
        "name": "AION Zapier Integration",
        "version": "1.0.0",
        "status": "operational",
        "active_webhooks": len(_webhook_subscriptions),
    }


@router.get("/plans")
async def list_plans():
    return {
        "plans": [
            {
                "id": p["id"],
                "name": p["name"],
                "price_usd": f"${p['price_usd']:,.2f}",
                "agents": p["agents"],
            }
            for p in PLANS
        ]
    }


_webhook_subscriptions: dict[str, dict] = {}
