import hashlib
import hmac
import json
import logging
import os
import uuid

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.monetization.plans import PLANS
from src.monetization.subscription_activator import (
    activate_subscription,
    deactivate_subscription,
    get_subscription as get_active_sub,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appsumo", tags=["appsumo"])

APPSUMO_SECRET = os.getenv("APPSUMO_WEBHOOK_SECRET", "")
PLAN_MAP = {
    "aion_compliance_tier1": "compliance_essencial",
    "aion_compliance_tier2": "regulatory_pro",
    "aion_compliance_tier3": "full_suite",
}


class AppSumoWebhookPayload(BaseModel):
    action: str = ""
    plan_id: str = ""
    uuid: str = ""
    activation_email: str = ""
    invoice_item_uuid: str = ""
    quantity: int = 1


class AppSumoLicenseRequest(BaseModel):
    license_key: str
    domain: str = ""


class AppSumoLicenseResponse(BaseModel):
    status: str
    license_key: str
    plan_id: str
    activation_email: str
    activated_at: str | None = None
    expires_at: str | None = None


def _verify_signature(timestamp: str, payload: bytes, signature: str) -> bool:
    """Per AppSumo Licensing API v2 docs (docs.licensing.appsumo.com/webhook/
    webhook__security.html): the signed message is the timestamp combined with
    the raw request body, HMAC-SHA256'd with the shared API key. Headers are
    X-Appsumo-Timestamp and X-Appsumo-Signature."""
    if not APPSUMO_SECRET:
        logger.error("APPSUMO_WEBHOOK_SECRET nao configurado — rejeitando webhook (fail closed)")
        return False
    if not timestamp or not signature:
        return False
    message = timestamp.encode() + payload
    expected = hmac.new(APPSUMO_SECRET.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.body()
    timestamp = request.headers.get("x-appsumo-timestamp", "")
    signature = request.headers.get("x-appsumo-signature", "")

    if not _verify_signature(timestamp, body, signature):
        raise HTTPException(status_code=401, detail="Assinatura invalida")

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    action = payload.get("action", "")
    plan_id = payload.get("plan_id", "")
    activation_uuid = payload.get("uuid", "")
    activation_email = payload.get("activation_email", "")
    invoice_uuid = payload.get("invoice_item_uuid", str(uuid.uuid4()))

    logger.info("AppSumo webhook: %s plan=%s user=%s uuid=%s", action, plan_id, activation_email, activation_uuid)

    internal_plan = PLAN_MAP.get(plan_id, "compliance_essencial")

    if action == "activate":
        license_key = str(uuid.uuid4())
        _license_store[license_key] = {
            "plan_id": internal_plan,
            "activation_email": activation_email,
            "activation_uuid": activation_uuid,
            "invoice_uuid": invoice_uuid,
            "status": "active",
            "activated_at": None,
        }

        activate_subscription(
            source="appsumo",
            external_id=activation_uuid,
            customer_id=activation_uuid,
            plan_id=internal_plan,
            customer_email=activation_email,
            customer_name=f"AppSumo {activation_email}",
        )

        logger.info("AppSumo license activated: %s plan=%s", license_key[:8], internal_plan)

        return {
            "status": "activated",
            "license_key": license_key,
            "plan_id": internal_plan,
            "activation_email": activation_email,
        }

    elif action == "refund":
        deactivate_subscription("appsumo", activation_uuid)
        for key, lic in list(_license_store.items()):
            if lic.get("activation_uuid") == activation_uuid:
                _license_store[key]["status"] = "refunded"
                logger.info("AppSumo license refunded: %s", key[:8])

        return {"status": "refunded"}

    elif action == "cancel":
        deactivate_subscription("appsumo", activation_uuid)
        for key, lic in list(_license_store.items()):
            if lic.get("activation_uuid") == activation_uuid:
                _license_store[key]["status"] = "cancelled"

        return {"status": "cancelled"}

    return {"received": True, "action": action}


@router.post("/license/activate")
async def activate_license(payload: AppSumoLicenseRequest):
    license_key = payload.license_key
    lic = _license_store.get(license_key)
    if not lic:
        raise HTTPException(status_code=404, detail="License key nao encontrada")

    if lic["status"] != "active":
        raise HTTPException(status_code=403, detail=f"License status: {lic['status']}")

    lic["activated_at"] = str(__import__("datetime").datetime.now())
    sub = activate_subscription(
        source="appsumo",
        external_id=lic["activation_uuid"],
        customer_id=lic["activation_uuid"],
        plan_id=lic["plan_id"],
        customer_email=lic["activation_email"],
        customer_name=f"AppSumo {lic['activation_email']}",
    )

    return AppSumoLicenseResponse(
        status="active",
        license_key=license_key,
        plan_id=lic["plan_id"],
        activation_email=lic["activation_email"],
        activated_at=sub.get("activated_at"),
        expires_at=None,
    )


@router.post("/license/validate")
async def validate_license(payload: AppSumoLicenseRequest):
    lic = _license_store.get(payload.license_key)
    if not lic:
        return {"valid": False, "reason": "License key invalida"}
    if lic["status"] != "active":
        return {"valid": False, "reason": f"License {lic['status']}"}
    sub = get_active_sub("appsumo", lic["activation_uuid"])
    return {
        "valid": sub is not None,
        "plan_id": lic["plan_id"],
        "activation_email": lic["activation_email"],
    }


@router.get("/plans")
async def list_plans():
    return {
        "appsumo_tiers": [
            {"id": "aion_compliance_tier1", "name": "AION Compliance Tier 1", "internal_plan": "compliance_essencial", "price": "$49"},
            {"id": "aion_compliance_tier2", "name": "AION Compliance Tier 2", "internal_plan": "regulatory_pro", "price": "$149"},
            {"id": "aion_compliance_tier3", "name": "AION Compliance Tier 3", "internal_plan": "full_suite", "price": "$299"},
        ],
        "internal_plans": PLANS,
    }


_license_store: dict[str, dict] = {}
