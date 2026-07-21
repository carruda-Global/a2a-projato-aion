"""AI Voice Agent / Virtual Receptionist — answers business phone calls 24/7.

Unlike the document-based Global Copilots, this product has a real per-minute
cost the instant a call connects, so the paywall can't "generate the full
result and gate the download": an unlicensed visitor is routed to the shared
demo number (capped duration) instead of getting their own provisioned line.
Call telephony/STT/TTS runs on Vapi; this router owns the business logic
(licensing, call logging, lead/cost tracking), not the audio pipeline.
"""
import logging
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException

from src.config import Settings
from src.agents._copilot_common import tem_licenca_premium
from src.monetization.subscription_activator import get_subscription
from src.agents.voice_rag import ingest_knowledge, retrieve_context
from src.agents.voice_call_intelligence import classify_call
from src.agents.voice_compliance_receipts import record_call_receipt
from src.agents.voice_vertical_templates import seed_vertical_knowledge

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice-agent", tags=["voice_agent"])

CHECKOUT_URL = "https://buy.stripe.com/28E4gBa6Ibov2PicOsg7e0x"
VAPI_API_BASE = "https://api.vapi.ai"
DEMO_CALL_MAX_SECONDS = 180
# Vapi requires a desired area code for free US numbers; 406 confirmed
# available at integration time (same area as the shared demo number).
VAPI_DEFAULT_AREA_CODE = "406"
PLACES_API_BASE = "https://places.googleapis.com/v1"
PLACES_FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.internationalPhoneNumber,places.regularOpeningHours"
BASE_URL = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")
DEFAULT_LOCATION_LABEL = "primary"
# UK/Canada/Australia guidance all call for a defined, bounded retention
# period for call recordings/transcripts -- 90 days is a common, defensible
# default for a receptionist product (long enough for a business to follow
# up on any lead, short enough to not be indefinite retention of PII).
CALL_DATA_RETENTION_DAYS = 90
# How many phone lines/locations each plan includes. Unknown/legacy plan_id
# falls back to 1 rather than silently allowing unlimited lines.
PLAN_LINE_LIMITS = {
    "voice_receptionist_starter": 1,
    "voice_receptionist_growth": 2,
    "voice_receptionist_agency": 50,  # wholesale tier: many client lines under one agency account
}


@router.get("/lines/{customer_email}")
async def get_line_status(customer_email: str) -> dict:
    """How many lines this customer already has vs. how many their plan
    includes — the onboarding page uses this to decide whether to offer
    'add another location' after the first number is live."""
    customer_email = customer_email.strip().lower()
    sub = get_subscription("stripe", customer_email)
    plan_id = (sub or {}).get("plan_id", "")
    limit = PLAN_LINE_LIMITS.get(plan_id, 1)
    used = len(_get_lines_for_customer(customer_email))
    return {"plan_id": plan_id, "used": used, "limit": limit, "can_add_line": used < limit}


@router.post("/provision")
async def provision_number(data: dict):
    """Give a licensed customer a real, dedicated phone number. Unlicensed
    visitors get routed to the shared demo number instead — provisioning a
    real number per free visitor would mean paying a standing monthly
    rental fee for every anonymous trial, which doesn't scale to $0."""
    customer_email = (data.get("customer_email") or "").strip().lower()
    location_label = (data.get("location_label") or DEFAULT_LOCATION_LABEL).strip() or DEFAULT_LOCATION_LABEL
    vertical = (data.get("vertical") or "").strip().lower()
    reseller_agency = (data.get("reseller_agency") or "").strip()

    if not tem_licenca_premium(customer_email):
        settings = Settings()
        return {
            "licensed": False,
            "demo_phone_number_id": settings.vapi_demo_phone_number_id,
            "message": (
                f"Try it live on our shared demo line (max {DEMO_CALL_MAX_SECONDS // 60} min per call) "
                "before subscribing."
            ),
            "checkout_url": CHECKOUT_URL,
        }

    sub = get_subscription("stripe", customer_email)
    plan_id = (sub or {}).get("plan_id", "")
    line_limit = PLAN_LINE_LIMITS.get(plan_id, 1)
    existing_lines = _get_lines_for_customer(customer_email)
    if any(l.get("location_label") == location_label for l in existing_lines):
        raise HTTPException(status_code=409, detail=f"A line named '{location_label}' already exists for this account")
    if len(existing_lines) >= line_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Your plan includes {line_limit} phone line(s) and you're already using all of them. Upgrade to add more.",
        )

    settings = Settings()
    if not settings.vapi_api_key:
        raise HTTPException(status_code=503, detail="Voice provider not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{VAPI_API_BASE}/phone-number",
            headers={"Authorization": f"Bearer {settings.vapi_api_key}"},
            json={
                "provider": "vapi",
                "name": f"aion-{customer_email}-{location_label}",
                "numberDesiredAreaCode": VAPI_DEFAULT_AREA_CODE,
                # Only customer numbers get this — the shared demo number keeps
                # its dashboard-configured default assistant untouched, so a bug
                # here can't break the public demo line.
                "server": {"url": f"{BASE_URL}/api/voice-agent/webhook/vapi"},
            },
        )
        if resp.status_code >= 400:
            logger.error("Vapi provisioning failed for %s: %s", customer_email, resp.text)
            raise HTTPException(status_code=502, detail="Could not provision a phone number right now")
        phone = resp.json()

    _upsert_voice_agent_line(customer_email, location_label, {
        "customer_email": customer_email,
        "location_label": location_label,
        "phone_number_id": phone.get("id"),
        "phone_number": phone.get("number"),
        "provisioned_at": datetime.now(timezone.utc).isoformat(),
        "reseller_agency": reseller_agency or None,
        "vertical": vertical or None,
    })

    seeded_chunks = 0
    if vertical:
        seeded_chunks = await seed_vertical_knowledge(customer_email, location_label, vertical)

    return {
        "licensed": True, "phone_number": phone.get("number"), "phone_number_id": phone.get("id"),
        "location_label": location_label, "vertical_knowledge_seeded": seeded_chunks,
    }


@router.post("/import-business")
async def import_business(data: dict):
    """Auto-fills business hours/phone/address from the customer's public
    Google Business Profile listing (Goodcall does the same) so setup needs
    less manual typing. Uses the Places API (New) with just an API key —
    business hours are public data, so this doesn't need the OAuth-gated
    Business Information API, which would require the customer to grant
    consent to *their own* Google Business account."""
    customer_email = (data.get("customer_email") or "").strip().lower()
    business_name = (data.get("business_name") or "").strip()
    location_hint = (data.get("location") or "").strip()
    location_label = (data.get("location_label") or DEFAULT_LOCATION_LABEL).strip() or DEFAULT_LOCATION_LABEL
    if not (customer_email and business_name):
        raise HTTPException(status_code=400, detail="customer_email and business_name are required")

    settings = Settings()
    if not settings.google_places_api_key:
        raise HTTPException(status_code=503, detail="Business lookup not configured")

    text_query = f"{business_name} {location_hint}".strip()
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{PLACES_API_BASE}/places:searchText",
            headers={
                "X-Goog-Api-Key": settings.google_places_api_key,
                "X-Goog-FieldMask": PLACES_FIELD_MASK,
                "Content-Type": "application/json",
            },
            json={"textQuery": text_query},
        )
        if resp.status_code >= 400:
            logger.error("Places lookup failed for %s: %s", text_query, resp.text)
            raise HTTPException(status_code=502, detail="Could not look up this business right now")
        places = resp.json().get("places", [])

    if not places:
        return {"found": False, "message": "No matching Google Business Profile found — enter details manually."}

    place = places[0]
    hours = place.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
    business_data = {
        "customer_email": customer_email,
        "location_label": location_label,
        "google_place_id": place.get("id", ""),
        "business_name": place.get("displayName", {}).get("text", business_name),
        "business_address": place.get("formattedAddress", ""),
        "business_phone": place.get("internationalPhoneNumber", ""),
        "business_hours": hours,
    }
    _upsert_voice_agent_line(customer_email, location_label, business_data)
    return {"found": True, **business_data}


@router.post("/billing/run-overage")
async def run_overage_billing_endpoint(month: str | None = None):
    """Manual/cron trigger for real overage-minute billing (see
    voice_overage_billing_agent.py). `month` is optional 'YYYY-MM', defaults
    to the previous completed calendar month. Safe to call repeatedly --
    idempotent per (customer_email, billing_month)."""
    from src.agents.voice_overage_billing_agent import run_overage_billing

    return await run_overage_billing(target_month=month)


@router.post("/webhook/vapi")
async def vapi_webhook(data: dict):
    """Receives Vapi server-side call events. `assistant-request` fires the
    instant a call connects, before any audio plays — must respond within
    7.5s with the assistant config for THIS call. This is what actually
    delivers a personalized receptionist per customer, built from whatever
    business info /import-business (or manual entry) captured; without this,
    every provisioned number would share one generic default assistant.
    `end-of-call-report` logs to voice_calls, the source of truth for
    minutes used (trial cap, overage) and real cost spent per customer."""
    message = data.get("message", data)
    call = message.get("call", {})
    msg_type = message.get("type", "")

    if msg_type == "assistant-request":
        response = await _build_assistant_response(call.get("phoneNumberId", ""))
        await record_call_receipt(
            call_id=call.get("id", ""), tool="recording_disclosure_given",
            arguments={"phone_number_id": call.get("phoneNumberId", "")},
            outcome="disclosed_in_first_message", risk_classification="low",
        )
        return response

    if msg_type != "end-of-call-report":
        return {"received": True}

    call_id = call.get("id", "")
    started_at = call.get("startedAt")
    ended_at = call.get("endedAt")
    duration_seconds = int(message.get("durationSeconds", 0) or 0)
    phone_number_id = call.get("phoneNumberId", "")
    is_trial = phone_number_id == Settings().vapi_demo_phone_number_id
    # assistantOverrides.metadata.customer_email is never actually set by
    # anything in this flow (assistant-request builds the prompt inline, no
    # metadata attached) -- the real, working way to attribute a call is the
    # same phoneNumberId lookup _build_assistant_response already uses.
    owner = _get_business_by_phone_number_id(phone_number_id) if phone_number_id else None
    customer_email = (owner or {}).get("customer_email", "")

    row = {
        "id": call_id,
        "customer_email": customer_email,
        "phone_number": call.get("phoneNumber", {}).get("number", ""),
        "caller_number": call.get("customer", {}).get("number", ""),
        "direction": "inbound",
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": duration_seconds,
        "outcome": message.get("endedReason", ""),
        "transcript": message.get("transcript", ""),
        "recording_url": message.get("recordingUrl", ""),
        "is_trial_call": is_trial,
        "cost_usd": float(message.get("cost", 0) or 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _log_supabase_upsert("voice_calls", row)
    logger.info("Voice call logged: id=%s duration=%ss trial=%s", call_id, duration_seconds, is_trial)

    if customer_email and not is_trial:
        from app.routers.zapier_integration import fire_customer_webhooks
        await fire_customer_webhooks(customer_email, "call_completed", {
            "call_id": call_id, "caller_number": row["caller_number"],
            "duration_seconds": duration_seconds, "outcome": row["outcome"],
            "started_at": started_at, "ended_at": ended_at,
        })

    transcript = row["transcript"]
    if call_id and transcript.strip():
        try:
            # compliance receipt for this classification is recorded inside
            # the graph itself (compliance_node), not bolted on here.
            intelligence = await classify_call(transcript, call_id=call_id)
            _log_supabase_upsert("voice_call_intelligence", {
                "call_id": call_id,
                "intent": intelligence.get("intent", ""),
                "lead_name": intelligence.get("lead_name", ""),
                "lead_phone": intelligence.get("lead_phone", ""),
                "summary": intelligence.get("summary", ""),
                "urgency": intelligence.get("urgency", ""),
            })
            logger.info("Call intelligence classified: id=%s intent=%s urgency=%s", call_id, intelligence.get("intent"), intelligence.get("urgency"))
            if customer_email and not is_trial and (intelligence.get("lead_name") or intelligence.get("lead_phone")):
                from app.routers.zapier_integration import fire_customer_webhooks
                await fire_customer_webhooks(customer_email, "lead_captured", {
                    "call_id": call_id,
                    "lead_name": intelligence.get("lead_name", ""),
                    "lead_phone": intelligence.get("lead_phone", ""),
                    "intent": intelligence.get("intent", ""),
                    "summary": intelligence.get("summary", ""),
                    "urgency": intelligence.get("urgency", ""),
                })
        except Exception as e:
            logger.warning("Call intelligence classification failed for %s: %s", call_id, e)

    return {"received": True}


@router.post("/knowledge")
async def add_knowledge(data: dict):
    """Customer adds FAQ/policy text -- becomes real RAG context for their
    assistant's calls. Requires an active license, same as provisioning a
    real line, since this is per-customer data, not the shared demo."""
    customer_email = (data.get("customer_email") or "").strip().lower()
    location_label = (data.get("location_label") or DEFAULT_LOCATION_LABEL).strip() or DEFAULT_LOCATION_LABEL
    content = (data.get("content") or "").strip()
    if not (customer_email and content):
        raise HTTPException(status_code=400, detail="customer_email and content are required")
    if not tem_licenca_premium(customer_email):
        raise HTTPException(status_code=403, detail="Active subscription required to add knowledge base content")

    stored = await ingest_knowledge(customer_email, location_label, content)
    return {"chunks_stored": stored}


@router.get("/calls/{customer_email}")
async def list_calls(customer_email: str):
    if not tem_licenca_premium(customer_email):
        raise HTTPException(status_code=403, detail="Active subscription required")
    from src.database.supabase_client import SupabaseClient

    db = SupabaseClient(Settings())
    resp = (
        db.client.table("voice_calls")
        .select("*")
        .eq("customer_email", customer_email.strip().lower())
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    calls = resp.data or []
    total_seconds = sum(c.get("duration_seconds", 0) for c in calls)
    return {"calls": calls, "total_minutes_this_page": round(total_seconds / 60, 1)}


@router.get("/dashboard/{customer_email}")
async def customer_dashboard(customer_email: str):
    """Real value delivered this calendar month -- calls answered, leads
    captured, unique callers vs. the plan's caller cap. Backs
    get-started.html's post-signup view and (item 4) the standalone
    dashboard.html, both self-serve like the rest of this product (no
    login system exists anywhere else in it either -- gated by the same
    tem_licenca_premium check used for knowledge base and call history)."""
    customer_email = customer_email.strip().lower()
    if not tem_licenca_premium(customer_email):
        raise HTTPException(status_code=403, detail="Active subscription required")

    from src.database.supabase_client import SupabaseClient
    from src.agents.voice_overage_billing_agent import _caller_cap

    db = SupabaseClient(Settings())
    sub = get_subscription(customer_email) or {}
    plan_id = sub.get("plan_id", "voice_receptionist_starter")

    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    resp = (
        db.client.table("voice_calls")
        .select("caller_number,duration_seconds,is_trial_call")
        .eq("customer_email", customer_email)
        .eq("is_trial_call", False)
        .gte("started_at", month_start)
        .execute()
    )
    calls = resp.data or []
    total_minutes = round(sum((c.get("duration_seconds") or 0) for c in calls) / 60.0, 1)
    unique_callers = len({c["caller_number"] for c in calls if c.get("caller_number")})

    leads_resp = (
        db.client.table("voice_call_intelligence")
        .select("call_id,lead_name,lead_phone")
        .execute()
    )
    call_ids = [c["id"] for c in (
        db.client.table("voice_calls")
        .select("id")
        .eq("customer_email", customer_email)
        .eq("is_trial_call", False)
        .gte("started_at", month_start)
        .execute()
    ).data or []]
    leads = [r for r in (leads_resp.data or []) if r.get("call_id") in call_ids and (r.get("lead_name") or r.get("lead_phone"))]

    caller_cap = _caller_cap(plan_id, customer_email, db)

    return {
        "customer_email": customer_email,
        "plan_id": plan_id,
        "month": datetime.now(timezone.utc).strftime("%Y-%m"),
        "calls_answered": len(calls),
        "leads_captured": len(leads),
        "minutes_used": total_minutes,
        "unique_callers": unique_callers,
        "unique_caller_cap": caller_cap,
    }


async def _build_assistant_response(phone_number_id: str) -> dict:
    business = _get_business_by_phone_number_id(phone_number_id) if phone_number_id else None
    business_name = (business or {}).get("business_name") or "your business"
    hours = (business or {}).get("business_hours") or []
    hours_text = "; ".join(hours) if hours else "standard business hours"
    address = (business or {}).get("business_address") or ""

    knowledge_text = ""
    customer_email = (business or {}).get("customer_email", "")
    location_label = (business or {}).get("location_label", DEFAULT_LOCATION_LABEL)
    if customer_email:
        # No caller question exists yet at call start -- a generic anchor
        # query still surfaces the most topically relevant stored FAQ/policy
        # chunks via real similarity search, grounding the prompt in the
        # business's actual info instead of guessing.
        chunks = await retrieve_context(customer_email, location_label, "frequently asked questions about this business", k=3)
        if chunks:
            knowledge_text = "Known info about this business:\n" + "\n".join(f"- {c}" for c in chunks) + "\n"

    system_prompt = (
        f"You are the AI phone receptionist for {business_name}. "
        f"Business hours: {hours_text}. "
        + (f"Address: {address}. " if address else "")
        + knowledge_text
        + "Greet callers warmly, answer questions about hours and location, and if you "
        "can't fully help, take their name, phone number, and reason for calling so the "
        "business can follow up. Keep responses brief and natural, like a real "
        "receptionist, not a robot reading a script. "
        "Do not omit the recording/AI-analysis disclosure in your first message -- it is "
        "a legal requirement in every market this product serves (US two-party-consent "
        "states, UK, Canada, Australia), not optional phrasing."
    )
    return {
        "assistant": {
            # Legal requirement across every market this product serves (US
            # two-party-consent states carry criminal penalties for recording
            # without notice; UK/Canada/Australia all require disclosure at
            # call start too) -- this line is not just a nicety.
            "firstMessage": f"Thanks for calling {business_name}. This call may be recorded and analyzed by AI to help us follow up with you. How can I help today?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [{"role": "system", "content": system_prompt}],
            },
        }
    }


def _get_business_by_phone_number_id(phone_number_id: str) -> dict | None:
    try:
        from src.database.supabase_client import SupabaseClient

        db = SupabaseClient(Settings())
        resp = (
            db.client.table("voice_agent_numbers")
            .select("*")
            .eq("phone_number_id", phone_number_id)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None
    except Exception as e:
        logger.warning("Falha ao buscar voice_agent_numbers por phone_number_id: %s", e)
        return None


def _get_lines_for_customer(customer_email: str) -> list[dict]:
    try:
        from src.database.supabase_client import SupabaseClient

        db = SupabaseClient(Settings())
        resp = (
            db.client.table("voice_agent_numbers")
            .select("*")
            .eq("customer_email", customer_email)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        logger.warning("Falha ao buscar linhas de voice_agent_numbers: %s", e)
        return []


def _upsert_voice_agent_line(customer_email: str, location_label: str, row: dict) -> None:
    # voice_agent_numbers is keyed on (customer_email, location_label) since
    # the Growth plan allows more than one line per customer -- conflict
    # target must be given explicitly, the table no longer has a single-column PK.
    try:
        from src.database.supabase_client import SupabaseClient

        db = SupabaseClient(Settings())
        db.client.table("voice_agent_numbers").upsert(
            row, on_conflict="customer_email,location_label"
        ).execute()
    except Exception as e:
        logger.warning("Falha ao gravar voice_agent_numbers: %s", e)


def _log_supabase_upsert(table: str, row: dict) -> None:
    try:
        from src.database.supabase_client import SupabaseClient

        db = SupabaseClient(Settings())
        db.client.table(table).upsert(row).execute()
    except Exception as e:
        logger.warning("Falha ao gravar %s: %s", table, e)


@router.post("/caller-data-request")
async def caller_data_request(data: dict):
    """Real caller-facing data right (UK GDPR/PIPEDA/Australia Privacy Act
    all give the recorded party access/erasure rights, not just the
    business). A caller who wants to know or erase what was captured about
    them looks it up by the phone number they called from."""
    caller_number = (data.get("caller_number") or "").strip()
    action = (data.get("action") or "access").strip().lower()
    if not caller_number:
        raise HTTPException(status_code=400, detail="caller_number is required")
    if action not in ("access", "erase"):
        raise HTTPException(status_code=400, detail="action must be 'access' or 'erase'")

    from src.database.supabase_client import SupabaseClient

    db = SupabaseClient(Settings())
    calls = (
        db.client.table("voice_calls")
        .select("id,started_at,duration_seconds,transcript,recording_url")
        .eq("caller_number", caller_number)
        .execute()
    ).data or []

    if action == "access":
        return {"caller_number": caller_number, "calls": calls}

    call_ids = [c["id"] for c in calls]
    if call_ids:
        db.client.table("voice_calls").update({
            "transcript": "", "recording_url": "", "caller_number": "[erased by request]",
        }).in_("id", call_ids).execute()
        db.client.table("voice_call_intelligence").update({
            "lead_name": "", "lead_phone": "", "summary": "[erased by request]",
        }).in_("call_id", call_ids).execute()
    return {"caller_number": caller_number, "calls_erased": len(call_ids)}


async def purge_expired_call_data() -> dict:
    """Scheduled retention job -- deletes the identifying/content fields of
    calls older than CALL_DATA_RETENTION_DAYS (transcript, recording,
    caller number, lead name/phone), keeping only non-identifying aggregate
    fields (duration, cost, intent, urgency) the business owner legitimately
    needs for ongoing analytics. Real requirement, not decorative: UK ICO
    and Australia's Privacy Act guidance both call for a bounded retention
    period rather than indefinite storage of call content."""
    from datetime import timedelta
    from src.database.supabase_client import SupabaseClient

    cutoff = (datetime.now(timezone.utc) - timedelta(days=CALL_DATA_RETENTION_DAYS)).isoformat()
    db = SupabaseClient(Settings())
    expired = (
        db.client.table("voice_calls")
        .select("id")
        .lt("created_at", cutoff)
        .neq("caller_number", "[erased by request]")
        .execute()
    ).data or []
    call_ids = [c["id"] for c in expired]
    if not call_ids:
        return {"purged": 0}

    db.client.table("voice_calls").update({
        "transcript": "", "recording_url": "", "caller_number": "[retention expired]",
    }).in_("id", call_ids).execute()
    db.client.table("voice_call_intelligence").update({
        "lead_name": "", "lead_phone": "", "summary": "[retention expired]",
    }).in_("call_id", call_ids).execute()
    logger.info("[Retention] Purged content for %d calls older than %d days", len(call_ids), CALL_DATA_RETENTION_DAYS)
    return {"purged": len(call_ids)}
