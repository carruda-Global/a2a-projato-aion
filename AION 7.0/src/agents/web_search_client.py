"""Real-time web search via OpenRouter's `:online` model suffix -- fills
the "no search API configured" gap flagged this session without a new
paid subscription, since OPENROUTER_API_KEY is already real and working
(confirmed live: correctly reproduced a same-day TrustMRR figure with the
right date and source URL)."""
import logging
import os

from openai import OpenAI

logger = logging.getLogger(__name__)

_OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
_ONLINE_MODEL = os.getenv("OPENROUTER_ONLINE_MODEL", "openai/gpt-4o-mini:online")


def _client() -> OpenAI | None:
    if not _OPENROUTER_KEY:
        return None
    return OpenAI(
        api_key=_OPENROUTER_KEY,
        base_url="https://openrouter.ai/api/v1",
        timeout=45,
        default_headers={"HTTP-Referer": "https://global-engenharia.com", "X-Title": "EcoSystem AEC"},
    )


async def search_web(query: str, max_tokens: int = 500) -> str | None:
    """Real, current web-search-grounded answer, or None if OpenRouter
    isn't configured or the call fails. Runs the sync OpenAI client in a
    thread so it doesn't block the event loop."""
    client = _client()
    if client is None:
        logger.warning("[WebSearch] OPENROUTER_API_KEY not set")
        return None
    try:
        import asyncio
        resp = await asyncio.to_thread(
            client.chat.completions.create,
            model=_ONLINE_MODEL,
            messages=[{"role": "user", "content": query}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.warning("[WebSearch] Search failed: %s", e)
        return None
