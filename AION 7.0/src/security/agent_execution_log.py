"""Lightweight AgentOps execution log -- separate from agent_compliance.py's
hash-chained receipts (that's an audit trail of WHAT an agent did; this is
operational data on HOW it performed: duration, success/failure). Real gap
found this session: no execution timing/success-rate data existed anywhere,
so a slow or silently-failing agent had no signal short of a user noticing.

Token/cost-per-call is NOT captured here yet -- DeepSeekClient.chat() only
returns text today, discarding whatever usage data the API response
includes. Threading that through is a real, separate, larger change (touches
every call site) -- not done as part of this pass.

Also tags every row with the deployed commit hash (Render's RENDER_GIT_COMMIT,
set automatically per deploy) -- the minimal real version of a "model
registry": traceability of which exact code version was live for any given
success/failure, without inventing a separate versioning system on top of
what git already provides.
"""
import logging
import os
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
_COMMIT_HASH = os.getenv("RENDER_GIT_COMMIT", "unknown")[:12]


async def record_agent_execution(agent_id: str, duration_ms: int, success: bool, error_message: str = "") -> None:
    """Fire-and-forget: logging failures must never break the agent call
    itself, so this only warns, never raises."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(
                f"{_SUPABASE_URL}/rest/v1/agent_execution_log",
                json={
                    "agent_id": agent_id,
                    "duration_ms": duration_ms,
                    "success": success,
                    "error_message": error_message[:500] if error_message else None,
                    "commit_hash": _COMMIT_HASH,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            )
    except Exception as e:
        logger.warning("[AgentExecutionLog] Failed to record %s: %s", agent_id, e)
