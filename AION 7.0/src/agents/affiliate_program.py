"""Real affiliate/referral tracking, built on Stripe's native
client_reference_id mechanism -- no third-party affiliate SaaS (Rewardful/
PartnerStack) needed. Every real competitor checked this session (Smith.ai,
Goodcall, Synthflow, Retell AI) runs a partner/affiliate program; this is
ours.

How tracking works:
1. An affiliate signs up, gets a real referral_code.
2. Their tracking link is an EXISTING Stripe Payment Link with
   ?client_reference_id={referral_code} appended -- Stripe passes this
   straight through to the checkout.session.completed webhook, no new
   Stripe objects needed per affiliate.
3. On checkout completion, we record which customer came from which
   affiliate (affiliate_customers).
4. On every invoice.paid for that customer within 12 months of signup, we
   record a 20% commission (affiliate_commissions) -- matches the real
   commission structure most of our competitors use for recurring SaaS.
"""
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
COMMISSION_RATE = 0.20
COMMISSION_MONTHS = 12


def _headers() -> dict:
    return {"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"}


async def signup_affiliate(name: str, email: str) -> dict | None:
    """Creates a real affiliate record with a unique referral code. Returns
    None (not a fake success) if Supabase isn't reachable."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return None
    referral_code = secrets.token_urlsafe(6).replace("-", "").replace("_", "")[:8].upper()
    row = {
        "name": name, "email": email.strip().lower(), "referral_code": referral_code,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{_SUPABASE_URL}/rest/v1/affiliates", json=row,
                headers={**_headers(), "Prefer": "return=representation"},
            )
            resp.raise_for_status()
            return resp.json()[0] if resp.json() else row
    except Exception as e:
        logger.warning("[Affiliate] Signup failed: %s", e)
        return None


async def record_referral(customer_email: str, referral_code: str, plan_id: str) -> None:
    """Called from the checkout.session.completed webhook when a real
    client_reference_id is present. Links this customer to the affiliate
    for the 12-month commission window."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return
    row = {
        "customer_email": customer_email.strip().lower(), "referral_code": referral_code,
        "plan_id": plan_id, "signed_up_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            await client.post(
                f"{_SUPABASE_URL}/rest/v1/affiliate_customers", json=row,
                headers={**_headers(), "Prefer": "resolution=merge-duplicates"},
            )
    except Exception as e:
        logger.warning("[Affiliate] Failed to record referral: %s", e)


async def record_commission_if_referred(customer_email: str, amount_paid_cents: int, currency: str) -> None:
    """Called from invoice.paid. Looks up whether this customer was
    referred and is still within the 12-month commission window; if so,
    records a real 20% commission. No-op (not an error) if the customer
    wasn't referred or the window has passed."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{_SUPABASE_URL}/rest/v1/affiliate_customers",
                params={"customer_email": f"eq.{customer_email.strip().lower()}", "select": "referral_code,signed_up_at"},
                headers=_headers(),
            )
            resp.raise_for_status()
            rows = resp.json()
            if not rows:
                return
            referral_code = rows[0]["referral_code"]
            signed_up_at = datetime.fromisoformat(rows[0]["signed_up_at"].replace("Z", "+00:00"))
            if datetime.now(timezone.utc) - signed_up_at > timedelta(days=COMMISSION_MONTHS * 31):
                return

            commission = round(amount_paid_cents * COMMISSION_RATE)
            await client.post(
                f"{_SUPABASE_URL}/rest/v1/affiliate_commissions",
                json={
                    "referral_code": referral_code, "customer_email": customer_email.strip().lower(),
                    "amount_cents": commission, "currency": currency,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                headers=_headers(),
            )
    except Exception as e:
        logger.warning("[Affiliate] Failed to record commission: %s", e)
