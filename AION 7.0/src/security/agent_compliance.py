"""Shared, persistent audit-trail layer for any agent in the architecture.

Generalizes the pattern proven in src.agents.voice_compliance_receipts:
ComplianceReceipt's own chain lives in `self.chain` (in-memory only) --
useless as an audit trail on a stateless service that gets a fresh instance
per request and redeploys constantly. This module seeds a real
ComplianceReceipt with the actual last hash persisted in Supabase before
creating each new receipt, so the chain is genuinely continuous.

Any agent (Voice, the 8 AEC core agents, future ones) can call
record_agent_receipt() to get a real, hash-chained, persisted compliance
record instead of each product inventing its own audit logic.
"""
import logging
import os

import httpx

from src.security.audit.compliance_receipts import ComplianceReceipt

logger = logging.getLogger(__name__)

_TABLE = "agent_compliance_receipts"
_SUPABASE_URL = None
_SUPABASE_KEY = None


def _supabase_config():
    global _SUPABASE_URL, _SUPABASE_KEY
    if _SUPABASE_URL is None:
        _SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        _SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
    return _SUPABASE_URL, _SUPABASE_KEY


async def record_agent_receipt(
    agent_id: str, action: str, arguments: dict, outcome: str,
    decision: str = "allowed", risk_classification: str = "low",
) -> dict | None:
    """Records one real, persistent, hash-chained receipt for an agent
    execution. Returns the persisted receipt, or None if Supabase isn't
    configured or the write fails -- callers must not let this block the
    agent's actual response."""
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
        logger.warning("[AgentCompliance] Failed to read previous receipt: %s", e)
        prev_hash = "0000000000000000"

    receipt_obj = ComplianceReceipt()
    receipt_obj.chain = [{"hash": prev_hash}]
    receipt = receipt_obj.create_receipt(
        action={"tool": action, "arguments": arguments, "outcome": outcome},
        decision=decision,
        agent_id=agent_id,
        risk_classification=risk_classification,
    )

    row = {
        "agent_id": agent_id,
        "action": action,
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
        logger.warning("[AgentCompliance] Failed to persist receipt: %s", e)
        return None
    return row
