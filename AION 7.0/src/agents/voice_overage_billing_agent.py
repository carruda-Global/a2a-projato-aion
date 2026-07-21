"""Real overage-minute billing for the Voice Receptionist product.

Before this file existed, "$0.15/min after 300 min" was only text on
vendas.html's FAQ -- usage_billing.py (the metered-billing pattern reused by
every other product) had zero references to voice_receptionist, voice_calls,
or overage. Every customer who used more than their plan's included minutes
cost real Vapi/LLM infra money with no invoice ever created for the
difference. This agent closes that gap using voice_calls (the source of
truth for real minutes used, logged by the Vapi end-of-call-report webhook
in voice_agent.py) against each plan's minute cap, and creates a real Stripe
invoice item for the overage -- idempotent via voice_overage_billing_log so
a daily cron never double-charges the same month.
"""
import logging
from calendar import monthrange
from datetime import datetime, timedelta, timezone

import stripe

from src.config import Settings
from src.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

# Minutes included per plan. Agency was sold on vendas.html with NO stated
# per-line minute cap -- 200 min/line is the first real number for it,
# documented here and in vendas.html together so the two never drift apart.
PLAN_MINUTES_INCLUDED = {
    "voice_receptionist_starter": 300,
    "voice_receptionist_growth": 750,
}
AGENCY_MINUTES_PER_LINE = 200

# Same overage rates already advertised on vendas.html -- this agent is what
# makes those numbers real instead of aspirational.
PLAN_OVERAGE_RATE_USD = {
    "voice_receptionist_starter": 0.15,
    "voice_receptionist_growth": 0.12,
    "voice_receptionist_agency": 0.15,
}

VOICE_PLAN_IDS = tuple(PLAN_OVERAGE_RATE_USD.keys())


def _previous_month_str(today: datetime | None = None) -> str:
    today = today or datetime.now(timezone.utc)
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - timedelta(days=1)
    return last_month_end.strftime("%Y-%m")


def _month_bounds(month_str: str) -> tuple[str, str]:
    year, month = (int(x) for x in month_str.split("-"))
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    days = monthrange(year, month)[1]
    end = datetime(year, month, days, 23, 59, 59, tzinfo=timezone.utc) + timedelta(seconds=1)
    return start.isoformat(), end.isoformat()


def _minutes_included(plan_id: str, customer_email: str, db: SupabaseClient) -> float:
    if plan_id != "voice_receptionist_agency":
        return PLAN_MINUTES_INCLUDED.get(plan_id, 0)
    try:
        resp = (
            db.client.table("voice_agent_numbers")
            .select("id", count="exact")
            .eq("customer_email", customer_email)
            .execute()
        )
        num_lines = resp.count or 1
    except Exception as e:
        logger.warning("Could not count agency lines for %s, assuming 5 (plan minimum): %s", customer_email, e)
        num_lines = 5
    return AGENCY_MINUTES_PER_LINE * max(num_lines, 1)


def _minutes_used(customer_email: str, month_start: str, month_end: str, db: SupabaseClient) -> float:
    resp = (
        db.client.table("voice_calls")
        .select("duration_seconds")
        .eq("customer_email", customer_email)
        .eq("is_trial_call", False)
        .gte("started_at", month_start)
        .lt("started_at", month_end)
        .execute()
    )
    rows = resp.data or []
    return sum((r.get("duration_seconds") or 0) for r in rows) / 60.0


async def run_overage_billing(target_month: str | None = None) -> dict:
    """Bills overage for one completed calendar month (defaults to the
    previous month -- never bills the current, still-in-progress month).
    Safe to call repeatedly: voice_overage_billing_log's UNIQUE
    (customer_email, billing_month) makes every customer/month combo a
    one-time charge."""
    month_str = target_month or _previous_month_str()
    month_start, month_end = _month_bounds(month_str)

    import os

    settings = Settings()
    db = SupabaseClient(settings)
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

    subs_resp = (
        db.client.table("subscriptions")
        .select("customer_email,customer_id,plan_id,status")
        .eq("status", "active")
        .in_("plan_id", list(VOICE_PLAN_IDS))
        .execute()
    )
    subscriptions = subs_resp.data or []

    billed, skipped, errors = [], [], []

    for sub in subscriptions:
        customer_email = sub.get("customer_email")
        customer_id = sub.get("customer_id")
        plan_id = sub.get("plan_id")
        if not customer_email or not plan_id:
            continue

        already = (
            db.client.table("voice_overage_billing_log")
            .select("id")
            .eq("customer_email", customer_email)
            .eq("billing_month", month_str)
            .execute()
        )
        if already.data:
            skipped.append({"customer_email": customer_email, "reason": "already_billed"})
            continue

        minutes_used = _minutes_used(customer_email, month_start, month_end, db)
        minutes_included = _minutes_included(plan_id, customer_email, db)
        overage_minutes = max(0.0, minutes_used - minutes_included)

        if overage_minutes <= 0:
            skipped.append({"customer_email": customer_email, "reason": "no_overage", "minutes_used": round(minutes_used, 1)})
            continue

        rate = PLAN_OVERAGE_RATE_USD.get(plan_id, 0.15)
        amount_cents = round(overage_minutes * rate * 100)
        if amount_cents <= 0:
            continue

        # customer_id falls back to the raw email when Stripe didn't return
        # session.customer at checkout time (see stripe_webhook.py) -- an
        # email is not a valid Stripe customer ID, so invoicing would fail.
        # Log it as a real gap rather than silently eating the charge.
        if not customer_id or "@" in customer_id:
            errors.append({"customer_email": customer_email, "reason": "no_stripe_customer_id", "overage_minutes": round(overage_minutes, 1)})
            continue

        invoice_item_id = None
        try:
            item = stripe.InvoiceItem.create(
                customer=customer_id,
                amount=amount_cents,
                currency="usd",
                description=(
                    f"Voice Receptionist overage: {overage_minutes:.0f} min over "
                    f"{minutes_included:.0f} min included ({plan_id}, {month_str})"
                ),
            )
            invoice_item_id = item.get("id")
        except Exception as e:
            logger.error("Stripe InvoiceItem creation failed for %s: %s", customer_email, e)
            errors.append({"customer_email": customer_email, "reason": f"stripe_error: {e}"})
            continue

        db.client.table("voice_overage_billing_log").insert({
            "id": f"{customer_email}:{month_str}",
            "customer_email": customer_email,
            "billing_month": month_str,
            "plan_id": plan_id,
            "minutes_used": round(minutes_used, 2),
            "minutes_included": round(minutes_included, 2),
            "overage_minutes": round(overage_minutes, 2),
            "overage_rate_usd": rate,
            "amount_usd_cents": amount_cents,
            "stripe_invoice_item_id": invoice_item_id,
        }).execute()

        billed.append({
            "customer_email": customer_email,
            "overage_minutes": round(overage_minutes, 1),
            "amount_usd": round(amount_cents / 100, 2),
        })
        logger.info("Overage billed: %s | %.1f min | $%.2f", customer_email, overage_minutes, amount_cents / 100)

    return {"month": month_str, "billed": billed, "skipped": skipped, "errors": errors}
