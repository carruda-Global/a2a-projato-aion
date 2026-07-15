"""
AgentVerse message handler -- responds to the uAgents protocol (Fetch.ai).
Receives messages from other agents on the network and replies with real
info about AION Voice Receptionist.

AgentVerse delivers messages as a signed uAgents `Envelope` (not plain
JSON). The reply also needs to be an Envelope signed with this agent's
identity (derived from AGENT_SEED_PHRASE), or the sender won't recognize
the response.

This replaces an older version of this file (deleted 2026-07-02) that
served the retired 19-Copilot compliance product -- that version returned
the same hardcoded risk_score/findings template regardless of what was
asked, which wasn't real analysis. This version is intentionally simpler:
one real product, one honest reply describing it.
"""
import os
import json
import base64
import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/agentverse", tags=["agentverse"])
logger = logging.getLogger(__name__)

try:
    from uagents_core.envelope import Envelope
    from uagents_core.identity import Identity
    from uagents_core.models import Model
    from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
    _UAGENTS_AVAILABLE = True
except ImportError as e:
    _UAGENTS_AVAILABLE = False
    logger.error("[AgentVerse] uagents-core not available, identity/messaging disabled: %s", e)

BASE_URL = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")
AGENT_SEED = os.getenv("AGENT_SEED_PHRASE", "")
PRODUCT_URL = "https://global-engenharia.com/ecosystem/callreception"
CHECKOUT_URL = "https://buy.stripe.com/28E4gBa6Ibov2PicOsg7e0x"
DEMO_PHONE = "+1 (406) 602-9130"

_identity = None
_chat_schema_digest = None
if _UAGENTS_AVAILABLE and AGENT_SEED:
    try:
        _identity = Identity.from_seed(AGENT_SEED, 0)
        _chat_schema_digest = Model.build_schema_digest(ChatMessage)
        logger.info("[AgentVerse] Identity loaded: %s", _identity.address)
    except Exception as e:
        logger.error("[AgentVerse] Failed to load identity: %s", e)

PLANS = [
    {"id": "starter", "name": "Starter", "price_usd": 89, "minutes": 300, "lines": 1},
    {"id": "growth", "name": "Growth", "price_usd": 179, "minutes": 750, "lines": 2},
]

PRODUCT_REPLY_MARKDOWN = f"""## AION Voice Receptionist

An AI phone agent that answers business calls 24/7, texts back missed calls instantly, and captures every caller as a lead (name, number, reason for calling).

**Plans:**
- Starter: $89/mo, 300 minutes included, 1 phone line
- Growth: $179/mo, 750 minutes included, 2 phone lines/locations

No per-call fee, no customer cap. Self-service setup -- enter your business name, we pull your hours from Google, live in under 20 minutes.

**Try it live:** call the demo line at {DEMO_PHONE} (no signup needed, capped at 3 min/call)
**Get started:** {CHECKOUT_URL}
**Learn more:** {PRODUCT_URL}

---
*AION Voice Receptionist · Global Match Engenharia*
""".strip()


def _extract_text(body: dict) -> str:
    """Extract readable text from a uAgents envelope in any shape."""
    raw_payload = body.get("payload") or body.get("content") or body.get("message") or body.get("text") or ""

    if isinstance(raw_payload, str):
        try:
            decoded = base64.b64decode(raw_payload + "==").decode("utf-8")
            raw_payload = json.loads(decoded)
        except Exception:
            try:
                raw_payload = json.loads(raw_payload)
            except Exception:
                return raw_payload

    if isinstance(raw_payload, dict):
        msg = raw_payload.get("msg", raw_payload)
        content = msg.get("content", [])
        if isinstance(content, list):
            texts = [c.get("text", "") for c in content if isinstance(c, dict)]
            return " ".join(filter(None, texts))
        return str(msg.get("text", "") or msg.get("message", "") or msg)

    return str(body)


async def _build_reply_text(text: str) -> str:
    return PRODUCT_REPLY_MARKDOWN


@router.post("/messages")
async def receive_message(request: Request):
    """Main uAgents message endpoint. AgentVerse delivers messages here as
    a signed Envelope; the reply must also be a signed Envelope, or
    AgentVerse reports "Response was not received from agent" even on a
    200 OK."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    if not isinstance(body, dict):
        body = {}

    # Real AgentVerse traffic: signed uAgents Envelope.
    if _UAGENTS_AVAILABLE and "schema_digest" in body and "payload" in body and isinstance(body.get("payload"), str):
        return await _handle_envelope(body)

    # Fallback: plain JSON (manual tests, curl, warmup).
    return await _handle_plain(body)


async def _handle_envelope(body: dict) -> JSONResponse:
    incoming_sender = body.get("sender", "")
    incoming_session = body.get("session")
    logger.info("[AgentVerse] Envelope received from: %s | session: %s", incoming_sender, incoming_session)

    text = ""
    try:
        env = Envelope.model_validate(body)
        raw = env.decode_payload()
        chat_msg = ChatMessage.model_validate_json(raw)
        text = chat_msg.text()
    except Exception as e:
        logger.warning("[AgentVerse] Failed to decode envelope payload: %s", e)

    reply_text = await _build_reply_text(text)

    if _identity is None:
        logger.error("[AgentVerse] Identity not configured (AGENT_SEED_PHRASE missing) -- cannot sign reply")
        return JSONResponse({"error": "agent identity not configured"}, status_code=503)

    reply_msg = ChatMessage(content=[TextContent(text=reply_text)])
    reply_env = Envelope(
        version=1,
        sender=_identity.address,
        target=incoming_sender,
        session=incoming_session,
        schema_digest=_chat_schema_digest,
    )
    reply_env.encode_payload(reply_msg.model_dump_json())
    reply_env.sign(_identity)

    return JSONResponse(json.loads(reply_env.model_dump_json()))


async def _handle_plain(body: dict) -> JSONResponse:
    sender = body.get("sender", "unknown")
    session = body.get("session", "")
    logger.info("[AgentVerse] Plain message received from: %s | session: %s", sender, session)

    text = _extract_text(body).lower()

    if not body or "ping" in text or body.get("type") == "ping":
        return JSONResponse({
            "type": "pong",
            "agent": "AION Voice Receptionist",
            "description": "AI phone agent that answers business calls 24/7 for small businesses in the US/UK/CA/AU.",
            "plans": PLANS,
            "demo_phone": DEMO_PHONE,
            "checkout_url": CHECKOUT_URL,
            "product_url": PRODUCT_URL,
        })

    chat_response = await _build_reply_text(_extract_text(body))

    return JSONResponse({
        "type": "agent_message",
        "sender": body.get("target", _identity.address if _identity else ""),
        "target": sender,
        "session": session,
        "content": [{"type": "text", "text": chat_response}],
        "status": "success",
    })


@router.get("/messages")
async def agent_info():
    """Agent info -- AgentVerse uses this for health checks."""
    return {
        "agent": "AION Voice Receptionist",
        "address": _identity.address if _identity else "unconfigured",
        "status": "active" if _identity else "identity_not_configured",
        "product_url": PRODUCT_URL,
        "endpoint": f"{BASE_URL}/api/agentverse/messages",
    }


@router.get("/warmup")
async def warmup():
    """Keep-alive endpoint -- ping every 10 min to avoid Render cold starts."""
    return {"status": "warm", "agent": "AION Voice Receptionist"}
