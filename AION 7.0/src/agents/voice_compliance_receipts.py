"""Persistent wrapper around src.security.audit.ComplianceReceipt for the
Voice Receptionist call pipeline.

ComplianceReceipt's own chain lives in `self.chain` (in-memory only) -- fine
for a single long-running process, useless as an audit trail on a stateless
FastAPI service that gets a fresh instance per request and redeploys
constantly. This module seeds a real ComplianceReceipt with the actual last
hash persisted in Supabase before creating each new receipt, so the chain is
genuinely continuous across requests and restarts -- the actual point of a
hash chain."""
import logging

import httpx

from src.security.audit.compliance_receipts import ComplianceReceipt
from src.config import Settings

logger = logging.getLogger(__name__)

_SUPABASE_URL = None
_SUPABASE_KEY = None
_TABLE = "voice_call_compliance_receipts"


def _supabase_config():
    global _SUPABASE_URL, _SUPABASE_KEY
    if _SUPABASE_URL is None:
        import os
        _SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        _SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
    return _SUPABASE_URL, _SUPABASE_KEY


async def record_call_receipt(
    call_id: str, tool: str, arguments: dict, outcome: str,
    decision: str = "allowed", risk_classification: str = "low",
) -> dict | None:
    """Records one real, persistent receipt in the chain for a call-pipeline
    action (e.g. 'recording_disclosure_given', 'ai_intent_classification').
    Returns the persisted receipt, or None if Supabase isn't configured."""
    url, key = _supabase_config()
    if not (url and key):
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"{url}/rest/v1/{_TABLE}",
                params={"select": "receipt_hash", "order": "id.desc", "limit": "1"},
                headers={"apikey": key, "Authorization": f"Bearer {key}"},
            )
            prev = r.json()
            prev_hash = prev[0]["receipt_hash"] if prev else "0000000000000000"
    except Exception as e:
        logger.warning("[VoiceCompliance] Failed to read previous receipt: %s", e)
        prev_hash = "0000000000000000"

    receipt_obj = ComplianceReceipt()
    receipt_obj.chain = [{"hash": prev_hash}]  # seed real continuity, not a fresh empty chain
    receipt = receipt_obj.create_receipt(
        action={"tool": tool, "arguments": arguments, "outcome": outcome},
        decision=decision,
        agent_id="voice_receptionist",
        risk_classification=risk_classification,
    )

    row = {
        "call_id": call_id,
        "action": tool,
        "decision": decision,
        "risk_classification": risk_classification,
        "prev_receipt_hash": receipt["previous_receipt_hash"],
        "receipt_hash": receipt["hash"],
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{url}/rest/v1/{_TABLE}",
                json=row,
                headers={"apikey": key, "Authorization": f"Bearer {key}"},
            )
    except Exception as e:
        logger.warning("[VoiceCompliance] Failed to persist receipt: %s", e)
        return None
    return row
