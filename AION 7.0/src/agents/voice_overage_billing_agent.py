"""Real overage billing for the Voice Receptionist product -- billed per
unique caller over the plan's monthly cap, not per minute.

Matches vendas.html's sales copy ("unlimited minutes, up to N unique
callers/mo") exactly, and mirrors Goodcall's real, market-proven pricing
model ($0.50 per extra unique caller past the plan cap) instead of a
per-minute rate customers never see broken out. Before this file existed,
overage was only text on vendas.html's FAQ -- usage_billing.py (the metered
pattern reused by every other product) had zero references to
voice_receptionist, voice_calls, or overage, so any customer over cap was
pure margin loss with no invoice ever created for the difference.
Idempotent via voice_overage_billing_log so a daily cron never
double-charges the same month.
"""
import logging
from calendar import monthrange
from datetime import datetime, timedelta, timezone

import stripe

from src.config import Settings
from src.database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

# Unique-caller caps sold on vendas.html/index.html -- keep these three
# numbers in sync if pricing copy ever changes.
PLAN_CALLER_CAPS = {
    "voice_receptionist_starter": 120,
    "voice_receptionist_growth": 300,
}
AGENCY_CALLERS_PER_LINE = 80

# Same $0.50/extra-caller rate Goodcall uses -- a real, market-validated
# number, not invented. Flat across plans (their pricing does this too).
OVERAGE_RATE_USD_PER_CALLER = 0.50

VOICE_PLAN_IDS = ("voice_receptionist_starter", "voice_receptionist_growth", "voice_receptionist_agency")


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


def _caller_cap(plan_id: str, customer_email: str, db: SupabaseClient) -> int:
    if plan_id != "voice_receptionist_agency":
        return PLAN_CALLER_CAPS.get(plan_id, 0)
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
    return AGENCY_CALLERS_PER_LINE * max(num_lines, 1)


def _unique_callers_used(customer_email: str, month_start: str, month_end: str, db: SupabaseClient) -> int:
    resp = (
        db.client.table("voice_calls")
        .select("caller_number")
        .eq("customer_email", customer_email)
        .eq("is_trial_call", False)
        .gte("started_at", month_start)
        .lt("started_at", month_end)
        .execute()
    )
    rows = resp.data or []
    return len({r["caller_number"] for r in rows if r.get("caller_number")})


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

        callers_used = _unique_callers_used(customer_email, month_start, month_end, db)
        caller_cap = _caller_cap(plan_id, customer_email, db)
        overage_callers = max(0, callers_used - caller_cap)

        if overage_callers <= 0:
            skipped.append({"customer_email": customer_email, "reason": "no_overage", "callers_used": callers_used})
            continue

        amount_cents = round(overage_callers * OVERAGE_RATE_USD_PER_CALLER * 100)
        if amount_cents <= 0:
            continue

        # customer_id falls back to the raw email when Stripe didn't return
        # session.customer at checkout time (see stripe_webhook.py) -- an
        # email is not a valid Stripe customer ID, so invoicing would fail.
        # Log it as a real gap rather than silently eating the charge.
        if not customer_id or "@" in customer_id:
            errors.append({"customer_email": customer_email, "reason": "no_stripe_customer_id", "overage_callers": overage_callers})
            continue

        invoice_item_id = None
        try:
            item = stripe.InvoiceItem.create(
                customer=customer_id,
                amount=amount_cents,
                currency="usd",
                description=(
                    f"Voice Receptionist overage: {overage_callers} caller(s) over "
                    f"{caller_cap} included ({plan_id}, {month_str}) at $0.50/caller"
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
            "unique_callers_used": callers_used,
            "unique_caller_cap": caller_cap,
            "overage_callers": overage_callers,
            "overage_rate_usd": OVERAGE_RATE_USD_PER_CALLER,
            "amount_usd_cents": amount_cents,
            "stripe_invoice_item_id": invoice_item_id,
        }).execute()

        billed.append({
            "customer_email": customer_email,
            "overage_callers": overage_callers,
            "amount_usd": round(amount_cents / 100, 2),
        })
        logger.info("Overage billed: %s | %d extra callers | $%.2f", customer_email, overage_callers, amount_cents / 100)

    return {"month": month_str, "billed": billed, "skipped": skipped, "errors": errors}
