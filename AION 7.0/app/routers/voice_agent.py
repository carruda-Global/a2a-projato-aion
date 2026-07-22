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
from fastapi import APIRouter, HTTPException, Request

from app.app_utils.marketplace_auth import require_marketplace_admin_secret
from src.config import Settings
from src.agents._copilot_common import tem_licenca_premium
from src.monetization.subscription_activator import get_subscription
from src.agents.voice_rag import ingest_knowledge, retrieve_context
from src.agents.voice_call_intelligence import classify_call
from src.agents.voice_compliance_receipts import record_call_receipt
from src.agents.voice_vertical_templates import seed_vertical_knowledge
from src.agents.voice_i18n import TRANSCRIBER_LANGUAGE, resolve_language
from src.agents import voice_i18n

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
DEMO_EMAIL_PREFIX = "demo-"
DEMO_BUSINESS_NAME = {
    "pt": "Recepcionista de IA da AION (Demonstração)",
    "es": "Recepcionista de IA de AION (Demostración)",
}
PLAN_LINE_LIMITS = {
    "voice_receptionist_starter": 1,
    "voice_receptionist_growth": 2,
    "voice_receptionist_agency": 50,  # wholesale tier: many client lines under one agency account
}
# Fallback when a signup gives a language but no explicit country_code --
# best-effort guess, not a real geo lookup (es is ambiguous across all of
# LatAm; CL is just whichever single market got seeded into the pool first).
LANGUAGE_DEFAULT_COUNTRY = {"pt": "BR", "es": "CL", "en": "US"}


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
    language = resolve_language(data.get("language"))
    country_code = (data.get("country_code") or "").strip().upper() or LANGUAGE_DEFAULT_COUNTRY.get(language, "US")

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

    # Telnyx-carried numbers are bought and imported ahead of time (see
    # /admin/carrier-numbers/import), not created on demand -- so the first
    # move is to claim one from the pool for this country. Only countries
    # Vapi's native provider can't issue directly (BR, LatAm, UK, CA, AU)
    # need this; falling back to on-demand creation below is what already
    # served every US customer before this pool existed.
    claimed = _claim_carrier_number(country_code, customer_email, location_label)
    if claimed:
        phone = {"id": claimed["vapi_phone_number_id"], "number": claimed["e164_number"]}
    else:
        logger.warning(
            "No Telnyx carrier number available for country=%s (customer=%s) -- "
            "falling back to on-demand Vapi-native provisioning",
            country_code, customer_email,
        )
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
        "language": language,
    })

    seeded_chunks = 0
    if vertical:
        seeded_chunks = await seed_vertical_knowledge(customer_email, location_label, vertical)

    return {
        "licensed": True, "phone_number": phone.get("number"), "phone_number_id": phone.get("id"),
        "location_label": location_label, "vertical_knowledge_seeded": seeded_chunks,
        "language": language,
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


@router.get("/billing/cost-per-minute")
async def measured_cost_per_minute(days: int = 30):
    """Real, measured infra cost per talk-minute from Vapi's own cost_usd
    per call -- the number that anchors pricing decisions (e.g. whether
    Growth can drop to \$119 vs Goodcall's \$99) in measured data instead
    of estimates. Windows on created_at, not started_at: early webhook
    versions logged started_at as null and those rows carry real cost."""
    from datetime import timedelta
    from src.database.supabase_client import SupabaseClient

    db = SupabaseClient(Settings())
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    resp = (
        db.client.table("voice_calls")
        .select("duration_seconds,cost_usd,is_trial_call")
        .gte("created_at", cutoff)
        .gt("duration_seconds", 0)
        .execute()
    )
    rows = [r for r in (resp.data or []) if (r.get("cost_usd") or 0) > 0]
    total_minutes = sum(r["duration_seconds"] for r in rows) / 60.0
    total_cost = sum(float(r["cost_usd"]) for r in rows)
    return {
        "window_days": days,
        "calls_measured": len(rows),
        "total_minutes": round(total_minutes, 1),
        "total_cost_usd": round(total_cost, 4),
        "avg_cost_per_minute_usd": round(total_cost / total_minutes, 4) if total_minutes else None,
        "note": "Vapi-reported real cost per call; small samples of short calls skew low (context grows on long calls).",
    }


@router.get("/billing/customer-count")
async def voice_receptionist_customer_count():
    """Real count of active paying Voice Receptionist subscriptions --
    the one number that actually matters more than any traffic/SEO metric.
    Used to detect the first real sale during the Google Ads budget test."""
    from src.database.supabase_client import SupabaseClient

    db = SupabaseClient(Settings())
    resp = (
        db.client.table("subscriptions")
        .select("plan_id,activated_at", count="exact")
        .eq("status", "active")
        .in_("plan_id", ["voice_receptionist_starter", "voice_receptionist_growth", "voice_receptionist_agency"])
        .execute()
    )
    return {"active_customers": resp.count or 0, "rows": resp.data or []}


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
    # assistantOverrides.metadata.customer_email is never actually set by
    # anything in this flow (assistant-request builds the prompt inline, no
    # metadata attached) -- the real, working way to attribute a call is the
    # same phoneNumberId lookup _build_assistant_response already uses.
    owner = _get_business_by_phone_number_id(phone_number_id) if phone_number_id else None
    customer_email = (owner or {}).get("customer_email", "")
    # The pt/es demo lines (see debug/create-demo-number) aren't the single
    # env-configured English demo number, so they need their own check --
    # both are real Vapi numbers but neither is a paying customer's line.
    is_trial = (
        phone_number_id == Settings().vapi_demo_phone_number_id
        or customer_email.startswith(DEMO_EMAIL_PREFIX)
    )

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

    language = resolve_language((business or {}).get("language"))
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

    system_prompt = voice_i18n.system_prompt(language, business_name, hours_text, address, knowledge_text)
    # LLM provider is env-switchable: gpt-4o costs ~5x more per token than
    # deepseek-chat, and that difference alone is what blocks pricing the
    # Growth plan near Goodcall's $99 (margin math from 2026-07-21: at
    # ~$0.12/min all-in, $99 is negative-margin in the heavy-usage case; at
    # ~$0.07/min, $109-119 is safely profitable). Defaults to gpt-4o so a
    # deploy without the DeepSeek key configured in Vapi's dashboard
    # (Provider Keys -- a manual step outside this repo) degrades to the
    # current working setup instead of breaking live calls.
    llm_provider = os.getenv("VOICE_LLM_PROVIDER", "openai")
    llm_model = os.getenv("VOICE_LLM_MODEL", "deepseek-chat" if llm_provider == "deep-seek" else "gpt-4o")
    assistant: dict = {
        # Legal requirement across every market this product serves (US
        # two-party-consent states carry criminal penalties for recording
        # without notice; UK/Canada/Australia all require disclosure at
        # call start too) -- this line is not just a nicety.
        "firstMessage": voice_i18n.first_message(language, business_name),
        "model": {
            "provider": llm_provider,
            "model": llm_model,
            "messages": [{"role": "system", "content": system_prompt}],
        },
    }
    if language != "en":
        # Only overridden for pt/es -- omitting it for "en" leaves the phone
        # number's Vapi-dashboard-configured default transcriber/voice
        # untouched, so no existing US/UK/CA/AU customer is affected.
        # Forces Deepgram explicitly (provider is required alongside
        # "language" -- Vapi does not accept a bare {"language": ...}
        # partial).
        assistant["transcriber"] = {
            "provider": "deepgram",
            "model": "nova-2",
            "language": TRANSCRIBER_LANGUAGE[language],
        }
        # Azure's "multilingual-auto" voice picks a native-accented voice
        # based on the text's actual language instead of forcing one fixed
        # accent -- avoids hardcoding a single pt-BR/es-419 voiceId that
        # might not exist across every market this expansion targets
        # (Brazil, Mexico, Argentina, Bolivia, Chile, Paraguay). Untested
        # against a real call so far -- no pt/es phone number exists yet to
        # verify against (see debug/create-demo-number, currently blocked by
        # Vapi's org-level 403 on new number provisioning).
        assistant["voice"] = {"provider": "azure", "voiceId": "multilingual-auto"}
    return {"assistant": assistant}


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


def _claim_carrier_number(country_code: str, customer_email: str, location_label: str) -> dict | None:
    """Grabs one unassigned Telnyx-imported number for this country from the
    pool and marks it assigned. Not race-proof under concurrent signups for
    the same country/instant (no atomic claim -- Supabase update has no
    SELECT..FOR UPDATE SKIP LOCKED here), but at this product's signup
    volume a double-claim is a manual-fix edge case, not a load-bearing risk."""
    try:
        from src.database.supabase_client import SupabaseClient

        db = SupabaseClient(Settings())
        resp = (
            db.client.table("voice_carrier_numbers")
            .select("*")
            .eq("country_code", country_code)
            .is_("assigned_customer_email", "null")
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            return None
        row = rows[0]
        db.client.table("voice_carrier_numbers").update({
            "assigned_customer_email": customer_email,
            "assigned_location_label": location_label,
            "assigned_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", row["id"]).execute()
        return row
    except Exception as e:
        logger.warning("Falha ao buscar/reservar voice_carrier_numbers para %s: %s", country_code, e)
        return None


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


ZAPIER_TEST_ACCOUNT_EMAIL = "integration-testing@zapier.com"


@router.post("/debug/create-demo-number")
async def create_demo_number(data: dict):
    """Provisions a real Vapi number for a pt/es demo line -- the English
    demo number is a static env var set up manually at integration time, but
    pt/es didn't exist yet, so this does the same thing for those two via
    API instead of the dashboard. Idempotent: calling it twice for the same
    language returns the already-provisioned number instead of creating a
    second one (same safety pattern as grant_zapier_test_account)."""
    language = (data.get("language") or "").strip().lower()
    if language not in ("pt", "es"):
        raise HTTPException(status_code=400, detail="language must be 'pt' or 'es' (English demo already exists)")

    demo_email = f"{DEMO_EMAIL_PREFIX}{language}@aion.internal"
    existing = _get_lines_for_customer(demo_email)
    if existing:
        return {"status": "already_exists", "customer_email": demo_email, "phone_number": existing[0].get("phone_number")}

    settings = Settings()
    if not settings.vapi_api_key:
        raise HTTPException(status_code=503, detail="Voice provider not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{VAPI_API_BASE}/phone-number",
            headers={"Authorization": f"Bearer {settings.vapi_api_key}"},
            json={
                "provider": "vapi",
                "name": f"aion-demo-{language}",
                "numberDesiredAreaCode": VAPI_DEFAULT_AREA_CODE,
                "server": {"url": f"{BASE_URL}/api/voice-agent/webhook/vapi"},
            },
        )
        if resp.status_code >= 400:
            logger.error("Vapi demo number creation failed for %s: %s", language, resp.text)
            raise HTTPException(status_code=502, detail="Could not create the demo number right now")
        phone = resp.json()

    _upsert_voice_agent_line(demo_email, DEFAULT_LOCATION_LABEL, {
        "customer_email": demo_email,
        "location_label": DEFAULT_LOCATION_LABEL,
        "phone_number_id": phone.get("id"),
        "phone_number": phone.get("number"),
        "provisioned_at": datetime.now(timezone.utc).isoformat(),
        "business_name": DEMO_BUSINESS_NAME[language],
        "language": language,
    })
    return {"status": "created", "customer_email": demo_email, "phone_number": phone.get("number"), "phone_number_id": phone.get("id")}


@router.post("/admin/carrier-numbers/import")
async def import_carrier_number(data: dict, request: Request):
    """Imports one already-purchased Telnyx number into Vapi and adds it to
    the assignment pool -- the scriptable equivalent of the manual Vapi
    Dashboard > Phone Numbers > Create > Telnyx flow, run once per number
    bought (see runbook: Telnyx account/number purchase/Outbound Voice
    Profile are manual steps in the Telnyx dashboard, not doable from here).
    Requires MARKETPLACE_ADMIN_SECRET -- this both spends nothing itself
    (the Telnyx number is already paid for) and mutates live call routing,
    so it can't be open.
    """
    require_marketplace_admin_secret(request, Settings().marketplace_admin_secret)

    e164_number = (data.get("e164_number") or "").strip()
    country_code = (data.get("country_code") or "").strip().upper()
    language = resolve_language(data.get("language"))
    telnyx_credential_id = (data.get("telnyx_credential_id") or "").strip()
    name = (data.get("name") or f"aion-{country_code.lower()}-{e164_number}").strip()
    fallback_phone_number_id = (data.get("fallback_phone_number_id") or Settings().vapi_fallback_number_id).strip()
    if not (e164_number and country_code and telnyx_credential_id):
        raise HTTPException(status_code=400, detail="e164_number, country_code and telnyx_credential_id are required")

    settings = Settings()
    if not settings.vapi_api_key:
        raise HTTPException(status_code=503, detail="Voice provider not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{VAPI_API_BASE}/phone-number",
            headers={"Authorization": f"Bearer {settings.vapi_api_key}"},
            json={
                "provider": "telnyx",
                "number": e164_number,
                "credentialId": telnyx_credential_id,
                "name": name,
                "server": {"url": f"{BASE_URL}/api/voice-agent/webhook/vapi"},
            },
        )
        if resp.status_code >= 400:
            logger.error("Vapi Telnyx import failed for %s: %s", e164_number, resp.text)
            raise HTTPException(status_code=502, detail="Could not import this number into Vapi")
        phone = resp.json()
        vapi_phone_number_id = phone.get("id")

        if fallback_phone_number_id:
            fb_resp = await client.patch(
                f"{VAPI_API_BASE}/phone-number/{vapi_phone_number_id}",
                headers={"Authorization": f"Bearer {settings.vapi_api_key}"},
                json={"fallbackDestination": {
                    "type": "number",
                    "number": fallback_phone_number_id,
                    "numberE164CheckEnabled": True,
                }},
            )
            if fb_resp.status_code >= 400:
                # Number is already live in Vapi at this point -- log and
                # continue rather than discard a successfully imported
                # number over a fallback config error the operator can retry.
                logger.error("Fallback config failed for %s: %s", vapi_phone_number_id, fb_resp.text)

    row = {
        "country_code": country_code,
        "language": language,
        "e164_number": e164_number,
        "vapi_phone_number_id": vapi_phone_number_id,
        "provider": "telnyx",
        "fallback_vapi_phone_number_id": fallback_phone_number_id or None,
    }
    try:
        from src.database.supabase_client import SupabaseClient

        db = SupabaseClient(Settings())
        db.client.table("voice_carrier_numbers").upsert(row, on_conflict="e164_number").execute()
    except Exception as e:
        logger.error("Number %s imported into Vapi but pool insert failed: %s", e164_number, e)
        raise HTTPException(status_code=500, detail="Imported into Vapi but failed to record in the pool -- check logs")

    return {"status": "imported", **row}


@router.get("/admin/carrier-numbers")
async def list_carrier_numbers(request: Request, country_code: str | None = None):
    """Pool inventory -- which countries still have unassigned Telnyx
    numbers, so an operator knows when to buy/import more before running
    out mid-signup (see /provision's fallback-to-on-demand-Vapi warning)."""
    require_marketplace_admin_secret(request, Settings().marketplace_admin_secret)

    from src.database.supabase_client import SupabaseClient

    db = SupabaseClient(Settings())
    query = db.client.table("voice_carrier_numbers").select("*")
    if country_code:
        query = query.eq("country_code", country_code.strip().upper())
    rows = query.execute().data or []
    unassigned_by_country: dict[str, int] = {}
    for r in rows:
        if not r.get("assigned_customer_email"):
            cc = r["country_code"]
            unassigned_by_country[cc] = unassigned_by_country.get(cc, 0) + 1
    return {"numbers": rows, "unassigned_by_country": unassigned_by_country}


@router.post("/debug/grant-zapier-test-account")
async def grant_zapier_test_account():
    """One-off, hardcoded grant for Zapier's app-review test account --
    intentionally takes no input (email/plan are fixed constants) so this
    can't be repurposed into the unauthenticated arbitrary-email grant
    vulnerability fixed earlier in this product's history. Safe to call
    repeatedly (idempotent upsert via activate_subscription)."""
    from src.monetization.subscription_activator import activate_subscription

    record = activate_subscription(
        source="zapier_review",
        external_id="zapier-app-review-244200",
        customer_id=ZAPIER_TEST_ACCOUNT_EMAIL,
        plan_id="voice_receptionist_starter",
        customer_email=ZAPIER_TEST_ACCOUNT_EMAIL,
        customer_name="Zapier App Review",
    )
    return {"status": "granted", "customer_email": ZAPIER_TEST_ACCOUNT_EMAIL, "record": record}


@router.post("/debug/seed-zapier-test-call")
async def seed_zapier_test_call():
    """One-off, hardcoded sample call for Zapier's app-review test account
    -- lets the New Call Completed / New Lead Captured triggers' performList
    fallback return real data during Zap testing. Same no-input pattern as
    grant_zapier_test_account: nothing here is attacker-controlled.
    is_trial_call=True keeps it out of real billing/usage counts."""
    import uuid

    from src.database.supabase_client import SupabaseClient

    now = datetime.now(timezone.utc).isoformat()
    call_id = f"zapier_review_sample_{uuid.uuid4().hex[:8]}"
    row = {
        "id": call_id,
        "customer_email": ZAPIER_TEST_ACCOUNT_EMAIL,
        "phone_number": "+14065550100",
        "caller_number": "+14065550199",
        "direction": "inbound",
        "started_at": now,
        "ended_at": now,
        "duration_seconds": 87,
        "outcome": "lead_captured",
        "transcript": "[Sample call for Zapier app review] Hi, I'd like to book an appointment for next week -- Sure, let me take your name and number so the team can follow up.",
        "lead_name": "Sample Lead",
        "lead_phone": "+14065550199",
        "lead_intent": "appointment_request",
        "is_trial_call": True,
        "cost_usd": 0,
    }
    db = SupabaseClient(Settings())
    db.client.table("voice_calls").upsert(row).execute()
    return {"status": "seeded", "call_id": call_id, "customer_email": ZAPIER_TEST_ACCOUNT_EMAIL}


@router.post("/debug/fire-zapier-test-webhooks")
async def fire_zapier_test_webhooks():
    """Actually delivers a REST Hook event to whatever Zap(s) are subscribed
    for the Zapier review test account -- seed_zapier_test_call's row has
    is_trial_call=True *on purpose* (keeps it out of real billing), but the
    real webhook_vapi handler only calls fire_customer_webhooks for non-trial
    calls, so that seeded row alone never reaches a subscriber's Zap. Without
    this, a reviewer's Zap can stay "on" indefinitely and still never receive
    a real task, so Zapier's publishing checks (e.g. T001 "needs a successful
    task") never resolve. Payload shapes match exactly what the production
    end-of-call-report handler sends today -- this is a faithful replay, not
    an idealized sample. Same no-input, no-attacker-controlled-data pattern
    as the sibling debug/* endpoints."""
    import uuid
    from app.routers.zapier_integration import fire_customer_webhooks

    now = datetime.now(timezone.utc).isoformat()
    call_id = f"zapier_review_sample_{uuid.uuid4().hex[:8]}"
    await fire_customer_webhooks(ZAPIER_TEST_ACCOUNT_EMAIL, "call_completed", {
        "call_id": call_id,
        "caller_number": "+14065550199",
        "duration_seconds": 87,
        "outcome": "lead_captured",
        "started_at": now,
        "ended_at": now,
    })
    await fire_customer_webhooks(ZAPIER_TEST_ACCOUNT_EMAIL, "lead_captured", {
        "call_id": call_id,
        "lead_name": "Sample Lead",
        "lead_phone": "+14065550199",
        "intent": "appointment_request",
        "summary": "Caller wants to book an appointment for next week.",
        "urgency": "normal",
    })
    return {"status": "fired", "customer_email": ZAPIER_TEST_ACCOUNT_EMAIL, "call_id": call_id}
