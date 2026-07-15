"""Real research/review skills for the SDR: consult the shared research
RAG, or route a proposal through the multi-perspective council, before
acting. Calls the main backend over HTTP (admin-secret protected) since
this worker runs as a separate, dependency-lean process -- see
app/routers/sdr_research.py."""
import logging
import os

import httpx

logger = logging.getLogger(__name__)

_BACKEND_URL = os.getenv("AION_BACKEND_URL", "https://engenheiro-producao-ai.onrender.com")
_ADMIN_SECRET = os.getenv("MARKETPLACE_ADMIN_SECRET", "")


async def query_research(query: str, k: int = 5) -> list[dict]:
    """Retrieves real, previously-stored research findings relevant to
    `query`. Returns [] (not an exception) if unavailable -- callers should
    treat an empty result as 'nothing known yet', not a hard failure."""
    if not _ADMIN_SECRET:
        logger.warning("[SDR] MARKETPLACE_ADMIN_SECRET not set, cannot query research")
        return []
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"{_BACKEND_URL}/api/sdr-research/query",
                json={"query": query, "k": k},
                headers={"X-Admin-Secret": _ADMIN_SECRET},
            )
            r.raise_for_status()
            return r.json().get("results", [])
    except Exception as e:
        logger.warning("[SDR] Research query failed: %s", e)
        return []


async def search_web_live(query: str) -> str | None:
    """Real-time web search via OpenRouter's :online models -- fills the
    gap where the SDR previously had no way to research anything not
    already in the RAG."""
    if not _ADMIN_SECRET:
        logger.warning("[SDR] MARKETPLACE_ADMIN_SECRET not set, cannot search web")
        return None
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(
                f"{_BACKEND_URL}/api/sdr-research/search",
                json={"query": query},
                headers={"X-Admin-Secret": _ADMIN_SECRET},
            )
            r.raise_for_status()
            return r.json().get("result")
    except Exception as e:
        logger.warning("[SDR] Live web search failed: %s", e)
        return None


async def ask_council(proposal: str) -> dict | None:
    """Routes a proposal (a niche to pursue, a lead worth following up,
    a strategy shift) through 3 real, independent LLM perspectives.
    Returns None if unavailable."""
    if not _ADMIN_SECRET:
        logger.warning("[SDR] MARKETPLACE_ADMIN_SECRET not set, cannot reach council")
        return None
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(
                f"{_BACKEND_URL}/api/sdr-research/council",
                json={"proposal": proposal},
                headers={"X-Admin-Secret": _ADMIN_SECRET},
            )
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logger.warning("[SDR] Council review failed: %s", e)
        return None


async def ingest_research(topic: str, text: str, source: str = "") -> int:
    """Persists a research finding so it's retrievable via query_research
    later instead of living only in a one-off conversation."""
    if not _ADMIN_SECRET:
        return 0
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"{_BACKEND_URL}/api/sdr-research/ingest",
                json={"topic": topic, "text": text, "source": source},
                headers={"X-Admin-Secret": _ADMIN_SECRET},
            )
            r.raise_for_status()
            return r.json().get("stored_chunks", 0)
    except Exception as e:
        logger.warning("[SDR] Research ingest failed: %s", e)
        return 0
