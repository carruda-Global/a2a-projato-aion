"""Real RAG for the Voice Receptionist: lets a customer add FAQ/policy text
that the assistant's system prompt gets grounded in, instead of only the
hardcoded hours/address fields.

Chunking is simple (paragraph-based, ~500 char target) since customer-supplied
FAQ text is short -- no need for a token-aware splitter at this scale."""
import os
import logging

import httpx

logger = logging.getLogger(__name__)

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_EMBEDDING_MODEL = "gemini-embedding-001"
_EMBEDDING_DIMS = 1536  # matches VECTOR(1536) in voice_agent_knowledge / match_voice_knowledge
_TABLE = "voice_agent_knowledge"


def _chunk_text(text: str, target_chars: int = 500) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for p in paragraphs:
        if current and len(current) + len(p) > target_chars:
            chunks.append(current)
            current = p
        else:
            current = f"{current}\n{p}" if current else p
    if current:
        chunks.append(current)
    return chunks


async def _embed(text: str) -> list[float] | None:
    if not _GEMINI_API_KEY:
        logger.warning("[VoiceRAG] GEMINI_API_KEY not set -- embedding skipped")
        return None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{_EMBEDDING_MODEL}:embedContent",
                params={"key": _GEMINI_API_KEY},
                json={"content": {"parts": [{"text": text}]}, "outputDimensionality": _EMBEDDING_DIMS},
            )
            r.raise_for_status()
            return r.json()["embedding"]["values"]
    except Exception as e:
        logger.warning("[VoiceRAG] Embedding failed: %s", e)
        return None


async def ingest_knowledge(customer_email: str, location_label: str, text: str) -> int:
    """Chunks and embeds `text`, storing each chunk as a row. Returns how
    many chunks were actually stored (embedding failures are skipped, not
    fatal, since a partial knowledge base is still useful)."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return 0
    chunks = _chunk_text(text)
    stored = 0
    async with httpx.AsyncClient(timeout=15) as client:
        for chunk in chunks:
            embedding = await _embed(chunk)
            if embedding is None:
                continue
            try:
                resp = await client.post(
                    f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
                    json={
                        "customer_email": customer_email,
                        "location_label": location_label,
                        "content": chunk,
                        "embedding": embedding,
                    },
                    headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
                )
                if resp.status_code < 300:
                    stored += 1
            except Exception as e:
                logger.warning("[VoiceRAG] Failed to store chunk: %s", e)
    return stored


async def retrieve_context(customer_email: str, location_label: str, query: str, k: int = 3) -> list[str]:
    """Real similarity search via the match_voice_knowledge Postgres function.
    Returns an empty list (not an error) if no knowledge exists yet or the
    embedding call fails -- the assistant prompt just falls back to hours/
    address only, same as before this feature existed."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return []
    embedding = await _embed(query)
    if embedding is None:
        return []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{_SUPABASE_URL}/rest/v1/rpc/match_voice_knowledge",
                json={
                    "p_customer_email": customer_email,
                    "p_location_label": location_label,
                    "query_embedding": embedding,
                    "match_count": k,
                },
                headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            )
            resp.raise_for_status()
            return [row["content"] for row in resp.json()]
    except Exception as e:
        logger.warning("[VoiceRAG] Retrieval failed: %s", e)
        return []
