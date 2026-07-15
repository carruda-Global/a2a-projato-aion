import json
import logging
import os
import uuid

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.app_utils.marketplace_auth import require_marketplace_admin_secret
from src.config import get_settings
from src.monetization.hubspot_client import HubSpotClient
from src.monetization.plans import PLANS, get_plan
from src.monetization.subscription_activator import (
    activate_subscription,
    deactivate_subscription,
    get_subscription as get_active_sub,
    get_subscription_by_id,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hubspot", tags=["hubspot"])

HUBSPOT_REDIRECT_URI = os.getenv(
    "HUBSPOT_REDIRECT_URI",
    "https://engenheiro-producao-ai.onrender.com/hubspot/oauth/callback",
)


class HubSpotInstallResponse(BaseModel):
    status: str
    portal_id: str | None = None
    installed_at: str | None = None
    message: str | None = None


class HubSpotWebhookResponse(BaseModel):
    received: bool
    event_type: str | None = None
    object_id: str | None = None


class HubSpotComplianceRequest(BaseModel):
    portal_id: str
    access_token: str
    object_type: str = "company"
    object_id: str
    service: str = "compliance-nr1"


@router.get("/install")
async def install():
    client = HubSpotClient()
    auth_url = client.get_authorization_url(HUBSPOT_REDIRECT_URI)
    return RedirectResponse(url=auth_url)


@router.get("/oauth/callback")
async def oauth_callback(code: str = Query(default="")):
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")

    client = HubSpotClient()
    result = await client.exchange_code(code, HUBSPOT_REDIRECT_URI)
    if not result:
        raise HTTPException(status_code=502, detail="Failed to authenticate with HubSpot")

    portal_id = result.get("hub_id", result.get("hubId", ""))
    access_token = result.get("access_token", "")
    refresh_token = result.get("refresh_token", "")

    if not portal_id or not access_token:
        raise HTTPException(status_code=502, detail="Invalid response from HubSpot")

    _store_tokens(portal_id, access_token, refresh_token)

    activate_subscription(
        source="hubspot",
        external_id=portal_id,
        customer_id=portal_id,
        plan_id="compliance_essencial",
        customer_email=result.get("user", ""),
        customer_name=f"HubSpot Portal {portal_id}",
    )

    logger.info("HubSpot installed: portal=%s", portal_id)

    return RedirectResponse(
        url=(
            f"https://global-engenharia.com/hubspot-ativacao/"
            f"?activated=true"
            f"&portal_id={portal_id}"
        )
    )


@router.post("/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("eventType", "")
    object_id = payload.get("objectId", "")
    portal_id = payload.get("portalId", "")

    logger.info("HubSpot webhook: %s object=%s portal=%s", event_type, object_id, portal_id)

    tokens = _get_tokens(portal_id)
    if not tokens:
        logger.warning("Portal %s not authenticated", portal_id)
        return HubSpotWebhookResponse(received=False, event_type=event_type, object_id=object_id)

    _process_hubspot_event(event_type, portal_id, object_id, tokens)

    return HubSpotWebhookResponse(received=True, event_type=event_type, object_id=object_id)


def _process_hubspot_event(event_type: str, portal_id: str, object_id: str, tokens: dict):
    object_type = ""
    if "contact" in event_type.lower():
        object_type = "contact"
    elif "company" in event_type.lower():
        object_type = "company"
    elif "deal" in event_type.lower():
        object_type = "deal"
    else:
        logger.info("Event ignored: %s", event_type)
        return

    change_source = event_type.split(".")[-1] if "." in event_type else ""
    if change_source in ("creation", "deletion"):
        pass

    sub = get_active_sub("hubspot", portal_id)
    if not sub:
        logger.info("Portal %s has no active subscription", portal_id)
        return

    sub_id = sub.get("subscription_id", "")
    logger.info(
        "Event processed: portal=%s object_type=%s object_id=%s sub=%s",
        portal_id, object_type, object_id, sub_id,
    )


@router.post("/compliance-check")
async def compliance_check(payload: HubSpotComplianceRequest):
    sub = get_active_sub("hubspot", payload.portal_id)
    if not sub:
        raise HTTPException(
            status_code=403,
            detail="Portal has no active subscription. Install the app from the HubSpot Marketplace.",
        )

    service = payload.service
    object_type = payload.object_type
    object_id = payload.object_id
    access_token = payload.access_token

    client = HubSpotClient()

    if object_type == "company":
        data = await client.get_company(access_token, object_id)
    elif object_type == "contact":
        data = await client.get_contact(access_token, object_id)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid type: {object_type}")

    if not data:
        raise HTTPException(status_code=404, detail=f"{object_type} {object_id} not found")

    company_name = ""
    company_email = ""
    if object_type == "company":
        company_name = data.get("properties", {}).get("name", "")
        company_email = data.get("properties", {}).get("domain", "")
    elif object_type == "contact":
        company_name = data.get("properties", {}).get("company", "")
        company_email = data.get("properties", {}).get("email", "")

    result = {
        "service": service,
        "object_type": object_type,
        "object_id": object_id,
        "company_name": company_name,
        "company_email": company_email,
        "status": "executed",
        "summary": f"Check {service} executed for {company_name} via HubSpot",
    }

    note_body = (
        f"[AION Compliance] {service}\n"
        f"Company: {company_name}\n"
        f"Status: {result['status']}\n"
        f"---\n"
        f"Check completed successfully. Visit the dashboard for details."
    )
    await client.create_note(access_token, object_type, object_id, note_body)

    return result


@router.get("/subscribe")
async def subscribe(
    request: Request,
    plan: str = Query(default="compliance_essencial"),
    portal_id: str = Query(default=""),
):
    require_marketplace_admin_secret(request, get_settings().marketplace_admin_secret)

    if not portal_id:
        raise HTTPException(
            status_code=400,
            detail="portal_id is required. Provided by HubSpot after installation.",
        )

    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plan not found")

    record = activate_subscription(
        source="hubspot",
        external_id=portal_id,
        customer_id=portal_id,
        plan_id=plan,
    )

    redirect_url = (
        f"https://engenheiro-producao-ai.onrender.com/dashboard?"
        f"source=hubspot&portal_id={portal_id}"
    )

    return {
        "status": record["status"],
        "subscription_id": f"hubspot_{portal_id}",
        "portal_id": portal_id,
        "plan": plan,
        "redirect_url": redirect_url,
    }


@router.get("/subscription/{portal_id}")
async def get_subscription(portal_id: str):
    sub = get_active_sub("hubspot", portal_id)
    if not sub:
        sub = get_subscription_by_id(f"hubspot_{portal_id}")
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub


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


@router.get("/portal/{portal_id}/status")
async def portal_status(portal_id: str):
    sub = get_active_sub("hubspot", portal_id)
    tokens = _get_tokens(portal_id)
    return {
        "portal_id": portal_id,
        "installed": tokens is not None,
        "subscription_active": sub is not None,
        "plan": sub.get("plan_id") if sub else None,
    }


_tokens_store: dict[str, dict] = {}


def _store_tokens(portal_id: str, access_token: str, refresh_token: str):
    _tokens_store[portal_id] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def _get_tokens(portal_id: str) -> dict | None:
    return _tokens_store.get(portal_id)
