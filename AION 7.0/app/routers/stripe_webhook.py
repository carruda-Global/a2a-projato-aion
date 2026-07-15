import asyncio
import os
import uuid

import httpx
from fastapi import APIRouter, Request, HTTPException
import stripe
from src.monetization.subscription_activator import activate_subscription, deactivate_subscription
from src.monetization.plans import get_plan
from src.email.smtp_mailer import send_via_hostinger
from src.agents.affiliate_program import record_referral, record_commission_if_referred
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["webhook"])

# Set directly at import time — do not rely on some other module happening to
# instantiate StripeClient() first (nothing in the app did, which meant every
# webhook call crashed with AttributeError: module 'stripe' has no attribute
# 'webhook_secret').
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_CONNECT_WEBHOOK_SECRET = os.getenv("STRIPE_CONNECT_WEBHOOK_SECRET", "")
GA4_MEASUREMENT_ID = os.getenv("GA4_MEASUREMENT_ID", "")
GA4_API_SECRET = os.getenv("GA4_API_SECRET", "")

DEFAULT_PLAN_ID = "compliance_essencial"
VOICE_RECEPTIONIST_PLAN_ID = "voice_receptionist_starter"
VOICE_RECEPTIONIST_ONBOARDING_URL = "https://global-engenharia.com/ecosystem/callreception/get-started"


async def _send_ga4_purchase_event(session, plan_id: str, customer_email: str) -> None:
    """Server-side conversion event via GA4 Measurement Protocol -- real
    revenue attribution, since this fires on confirmed payment, not just a
    client-side page view. No stitched client_id from the browser session
    is available here, so GA4 will show it as a new session, but the
    revenue/plan data is still real and valuable."""
    if not (GA4_MEASUREMENT_ID and GA4_API_SECRET):
        return
    try:
        amount = (getattr(session, "amount_total", 0) or 0) / 100
        currency = (getattr(session, "currency", "") or "usd").upper()
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                "https://www.google-analytics.com/mp/collect",
                params={"measurement_id": GA4_MEASUREMENT_ID, "api_secret": GA4_API_SECRET},
                json={
                    "client_id": str(uuid.uuid4()),
                    "events": [{
                        "name": "purchase",
                        "params": {
                            "currency": currency,
                            "value": amount,
                            "transaction_id": session.id,
                            "items": [{"item_id": plan_id, "item_name": plan_id}],
                        },
                    }],
                },
            )
    except Exception as e:
        logger.warning("GA4 purchase event failed for %s: %s", customer_email, e)


async def _send_welcome_email(customer_email: str, plan_id: str) -> None:
    # Previously sent via Resend, whose sending domain isn't verified —
    # every welcome email across every plan was silently failing. Hostinger
    # SMTP is the confirmed-working channel (see directory listing emails
    # sent this session), so all welcome emails go through it now.
    if not (os.getenv("HOSTINGER_EMAIL_USER") and os.getenv("HOSTINGER_EMAIL_PASSWORD")):
        logger.warning("HOSTINGER_EMAIL_USER/PASSWORD not set — welcome email not sent to %s", customer_email)
        return
    plan = get_plan(plan_id) or {}
    plan_name = plan.get("name", plan_id)

    if plan_id == VOICE_RECEPTIONIST_PLAN_ID:
        subject = "Your AI Voice Receptionist is ready to set up"
        body = (
            f"<p>Welcome to AION Voice Receptionist!</p>"
            f"<p>Your <strong>{plan_name}</strong> subscription is now active.</p>"
            f"<p><a href='{VOICE_RECEPTIONIST_ONBOARDING_URL}'>Click here to set up your AI receptionist</a> — "
            f"enter your business name and we'll pull your hours and address automatically, "
            f"then your dedicated phone number goes live in under a minute.</p>"
            f"<p>Questions? Just reply — a real person reads this inbox.</p>"
            f"<p>— Global Match Engenharia</p>"
        )
    else:
        subject = "Welcome to AION Compliance"
        body = (
            f"<p>Welcome to AION Compliance!</p>"
            f"<p>Your <strong>{plan_name}</strong> subscription is now active.</p>"
            f"<p>To get started, reply to this email with your company name and the "
            f"assessment you'd like to run first (SOC2, ISO27001, EU AI Act, Contract Risk, "
            f"or Vendor Risk) and we'll onboard you directly.</p>"
            f"<p>Questions? Just reply — a real person reads this inbox.</p>"
            f"<p>— Global Match Engenharia</p>"
        )
    try:
        await asyncio.to_thread(send_via_hostinger, customer_email, subject, body)
    except Exception as e:
        logger.warning("Welcome email error for %s: %s", customer_email, e)


def _resolve_plan_id(session) -> str:
    """Payment Links created for this platform carry metadata.internal_plan_id
    (see the Global Compliance Copilot link created via the Stripe API). Older
    links created directly in the Dashboard don't have it — fall back to the
    entry-level plan rather than silently granting nothing."""
    payment_link_id = getattr(session, "payment_link", None)
    if payment_link_id:
        try:
            link = stripe.PaymentLink.retrieve(payment_link_id)
            plan_id = (link.get("metadata") or {}).get("internal_plan_id")
            if plan_id:
                return plan_id
        except Exception as e:
            logger.warning("Could not resolve plan from payment_link %s: %s", payment_link_id, e)
    return DEFAULT_PLAN_ID


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.type
    data = event.data.object

    logger.info(f"Stripe webhook received: {event_type}")

    if event_type == "checkout.session.completed":
        session = data
        customer_email = (
            (getattr(session, "customer_details", None) or {}).get("email")
            if getattr(session, "customer_details", None)
            else getattr(session, "customer_email", None)
        )
        if not customer_email:
            logger.warning("Checkout completed without a customer email: %s", session.id)
            return {"status": "success", "event": event_type}

        plan_id = _resolve_plan_id(session)
        activate_subscription(
            source="stripe",
            external_id=customer_email,
            customer_id=session.customer or customer_email,
            plan_id=plan_id,
            customer_email=customer_email,
        )
        await _send_welcome_email(customer_email, plan_id)
        await _send_ga4_purchase_event(session, plan_id, customer_email)

        referral_code = getattr(session, "client_reference_id", None)
        if referral_code:
            await record_referral(customer_email, referral_code, plan_id)
            logger.info(f"Referral recorded: {customer_email} <- {referral_code}")

        logger.info(f"Checkout completed: {session.id} | customer={customer_email} | plan={plan_id}")
        return {"status": "success", "event": event_type}

    elif event_type == "customer.subscription.created":
        logger.info(f"Subscription created: {data.id} | status={data.status}")

    elif event_type == "customer.subscription.updated":
        logger.info(f"Subscription updated: {data.id} | status={data.status}")

    elif event_type == "customer.subscription.deleted":
        customer_id = getattr(data, "customer", None)
        if customer_id:
            try:
                customer = stripe.Customer.retrieve(customer_id)
                email = customer.get("email")
                if email:
                    deactivate_subscription("stripe", email)
            except Exception as e:
                logger.warning("Could not deactivate subscription for customer %s: %s", customer_id, e)
        logger.info(f"Subscription deleted: {data.id}")

    elif event_type == "invoice.paid":
        logger.info(f"Invoice paid: {data.id} | amount={data.amount_paid}")
        customer_id = getattr(data, "customer", None)
        if customer_id:
            try:
                customer = stripe.Customer.retrieve(customer_id)
                email = customer.get("email")
                if email:
                    await record_commission_if_referred(email, data.amount_paid, data.currency)
            except Exception as e:
                logger.warning("Could not check affiliate referral for customer %s: %s", customer_id, e)

    elif event_type == "invoice.payment_failed":
        logger.warning(f"Invoice payment failed: {data.id}")

    return {"status": "success", "event": event_type}


@router.post("/stripe/connect")
async def stripe_connect_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_CONNECT_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

    logger.info(f"Stripe Connect webhook: {event.type}")
    return {"status": "success", "event": event.type}
