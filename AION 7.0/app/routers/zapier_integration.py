"""Zapier REST Hooks for Voice Receptionist events (call_completed,
lead_captured). This is what a customer's "Webhooks by Zapier" trigger
step points at -- not a published native Zapier app yet (that requires
submitting to Zapier's own developer platform and review process, a
separate step outside this codebase), but it's the real, working
subscribe/fire mechanism a Zap needs, scoped per customer.

Replaces the prior version, which kept subscriptions in an in-memory dict
(wiped on every Render restart) with no customer scoping and no connection
to any real voice_calls event -- functionally dead despite being "live".
"""
import logging
import uuid

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import Settings
from src.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/zapier", tags=["zapier"])

SUPPORTED_EVENTS = ("call_completed", "lead_captured")


class ZapierSubscribeRequest(BaseModel):
    customer_email: str
    event: str
    target_url: str


@router.post("/webhook/subscribe")
async def subscribe_webhook(payload: ZapierSubscribeRequest):
    if payload.event not in SUPPORTED_EVENTS:
        raise HTTPException(status_code=400, detail=f"event must be one of {SUPPORTED_EVENTS}")
    if not (payload.customer_email and payload.target_url):
        raise HTTPException(status_code=400, detail="customer_email and target_url are required")

    db = SupabaseClient(Settings())
    subscription_id = str(uuid.uuid4())
    db.client.table("zapier_webhook_subscriptions").insert({
        "id": subscription_id,
        "customer_email": payload.customer_email.strip().lower(),
        "event": payload.event,
        "target_url": payload.target_url,
    }).execute()
    logger.info("Zapier webhook subscribed: customer=%s event=%s sub=%s", payload.customer_email, payload.event, subscription_id)
    return {"subscription_id": subscription_id, "status": "active"}


@router.delete("/webhook/subscribe/{subscription_id}")
async def unsubscribe_webhook(subscription_id: str):
    db = SupabaseClient(Settings())
    resp = db.client.table("zapier_webhook_subscriptions").delete().eq("id", subscription_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Subscription nao encontrada")
    return {"status": "removed", "subscription_id": subscription_id}


@router.get("/webhook/subscriptions/{customer_email}")
async def list_subscriptions(customer_email: str):
    db = SupabaseClient(Settings())
    resp = (
        db.client.table("zapier_webhook_subscriptions")
        .select("id,event,target_url,created_at")
        .eq("customer_email", customer_email.strip().lower())
        .execute()
    )
    return {"subscriptions": resp.data or []}


@router.get("/health")
async def health_check():
    return {"name": "AION Zapier Integration", "version": "2.0.0", "status": "operational", "events": SUPPORTED_EVENTS}


async def fire_customer_webhooks(customer_email: str, event: str, payload: dict) -> None:
    """Called from voice_agent.py's end-of-call-report handler. Best-effort:
    a customer's Zap being slow/down must never break call logging."""
    if event not in SUPPORTED_EVENTS or not customer_email:
        return
    try:
        db = SupabaseClient(Settings())
        resp = (
            db.client.table("zapier_webhook_subscriptions")
            .select("target_url")
            .eq("customer_email", customer_email.strip().lower())
            .eq("event", event)
            .execute()
        )
        targets = [r["target_url"] for r in (resp.data or [])]
        if not targets:
            return
        async with httpx.AsyncClient(timeout=8) as client:
            for url in targets:
                try:
                    await client.post(url, json=payload)
                except Exception as e:
                    logger.warning("Zapier webhook delivery failed: customer=%s event=%s url=%s err=%s", customer_email, event, url, e)
    except Exception as e:
        logger.warning("Zapier webhook lookup failed for %s/%s: %s", customer_email, event, e)
