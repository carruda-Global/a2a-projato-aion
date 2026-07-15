import logging

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from src.monetization.plans import PLANS, get_plan
from src.config import get_settings, Settings
from src.monetization.stripe_client import StripeClient
from src.monetization.abacatepay_client import AbacatepayClient
from src.monetization.subscription_activator import (
    activate_subscription,
    deactivate_subscription,
    list_active_subscriptions,
    query_active_subscriptions_supabase,
    resolve_plan_agents,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/plans")
async def list_plans():
    return {"plans": PLANS}


@router.get("/active")
async def get_active_subscriptions():
    """Lista todas as assinaturas ativas com planos e agentes."""
    from supabase import create_client
    from src.config import get_settings
    from src.monetization.plans import get_plan

    settings = get_settings()

    memoria = list_active_subscriptions()

    supabase_active = query_active_subscriptions_supabase()

    ambas = {s["id"]: s for s in supabase_active}
    for s in memoria:
        if s["subscription_id"] not in ambas:
            plan = get_plan(s["plan_id"])
            agent_refs = plan.get("agents", []) if plan else []
            ambas[s["subscription_id"]] = {
                "id": s["subscription_id"],
                "source": s["source"],
                "customer_email": s["customer_email"],
                "customer_name": s["customer_name"],
                "customer_id": s["customer_id"],
                "plan_id": s["plan_id"],
                "plan_name": plan.get("name", "") if plan else "",
                "plan_price_brl": plan.get("price_brl", 0) if plan else 0,
                "status": s["status"],
                "activated_at": s["activated_at"],
                "agents": resolve_plan_agents(agent_refs) if agent_refs else [],
                "agent_count": len(resolve_plan_agents(agent_refs)) if agent_refs else 0,
            }

    subscriptions = sorted(ambas.values(), key=lambda x: x.get("activated_at", ""), reverse=True)
    total_agentes = sum(s["agent_count"] for s in subscriptions)

    return {
        "total_subscriptions": len(subscriptions),
        "total_agents_sold": total_agentes,
        "subscriptions": subscriptions,
    }


@router.get("/plans/{plan_id}")
async def get_plan_by_id(plan_id: str):
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")
    return {"plan": plan}


class CreateCheckoutRequest(BaseModel):
    plan_id: str
    success_url: str
    cancel_url: str
    customer_email: str | None = None


@router.post("/checkout")
async def create_checkout(req: CreateCheckoutRequest, settings: Settings = Depends(get_settings)):
    try:
        plan_config = settings.plans_config.get(req.plan_id)
        if not plan_config:
            raise HTTPException(status_code=400, detail=f"Plano {req.plan_id} nao encontrado")
        stripe_client = StripeClient(settings)
        url = stripe_client.create_checkout_session(
            req.plan_id, req.success_url, req.cancel_url, req.customer_email
        )
        if not url:
            raise HTTPException(status_code=400, detail="Falha ao criar sessao de checkout")
        return {"checkout_url": url, "method": "stripe"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


class CreatePixCheckoutRequest(BaseModel):
    plan_id: str
    customer_email: str | None = None
    customer_name: str | None = None
    success_url: str | None = None


@router.post("/checkout/pix")
async def create_pix_checkout(req: CreatePixCheckoutRequest, settings: Settings = Depends(get_settings)):
    try:
        plan_config = settings.plans_config.get(req.plan_id)
        if not plan_config:
            raise HTTPException(status_code=400, detail=f"Plano {req.plan_id} nao encontrado")

        async with AbacatepayClient(settings) as client:
            result = await client.create_pix_checkout(
                plan_id=req.plan_id,
                customer_email=req.customer_email,
                customer_name=req.customer_name,
                success_url=req.success_url,
            )
        if not result:
            raise HTTPException(status_code=400, detail="Falha ao criar checkout PIX")
        return result | {"method": "pix"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/checkout/pix/{checkout_id}")
async def get_pix_checkout_status(checkout_id: str, settings: Settings = Depends(get_settings)):
    try:
        async with AbacatepayClient(settings) as client:
            status = await client.get_checkout_status(checkout_id)
        if not status:
            raise HTTPException(status_code=404, detail="Checkout nao encontrado")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/webhook")
async def stripe_webhook(request: Request, settings: Settings = Depends(get_settings)):
    import stripe

    stripe.api_key = settings.stripe_secret_key

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    env = settings.app_env
    webhook_secret = getattr(settings, f"stripe_webhook_secret_{env}", None)
    if not webhook_secret:
        webhook_secret = settings.stripe_webhook_secret

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.type
    data = event.data.object

    if event_type == "checkout.session.completed":
        customer_email = data.get("customer_details", {}).get("email", "")
        subscription_id = data.get("subscription", "")
        customer_id = data.get("customer", "") or data.get("client_reference_id", "")
        plan_metadata = data.get("metadata", {})
        plan_id = plan_metadata.get("plan_id", "")
        activate_subscription(
            source="stripe",
            external_id=subscription_id,
            customer_id=customer_id or subscription_id,
            plan_id=plan_id,
            customer_email=customer_email,
        )
        logger.info("Stripe checkout completed: email=%s sub=%s plan=%s", customer_email, subscription_id, plan_id)

    elif event_type == "customer.subscription.updated":
        logger.info("Stripe subscription updated: sub=%s status=%s", data.id, data.status)

    elif event_type == "customer.subscription.deleted":
        deactivate_subscription("stripe", data.id)
        logger.info("Stripe subscription deleted: sub=%s", data.id)

    return {"received": True, "type": event_type, "env": env}


@router.post("/webhook/abacatepay")
async def abacatepay_webhook(request: Request, settings: Settings = Depends(get_settings)):
    async with AbacatepayClient(settings) as client:
        payload = await request.body()
        signature = request.headers.get("x-abacatepay-signature", "")
        event = client.verify_webhook(payload, signature)

    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    data = event["data"]

    if event_type == "checkout.paid":
        checkout_id = data.get("id", "")
        plan_id = data.get("metadata", {}).get("plan_id", "")
        customer_email = data.get("customer_email", "")
        activate_subscription(
            source="abacatepay",
            external_id=checkout_id,
            customer_id=checkout_id,
            plan_id=plan_id,
            customer_email=customer_email,
        )
        logger.info("PIX checkout paid: checkout=%s plan=%s email=%s", checkout_id, plan_id, customer_email)

    return {"received": True, "type": event_type}
