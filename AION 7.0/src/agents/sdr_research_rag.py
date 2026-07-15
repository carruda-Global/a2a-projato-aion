"""General-purpose research knowledge base for the SDR/sales system --
generalizes the per-customer RAG pattern in voice_rag.py into a shared,
topic-tagged store so real market/competitor research (e.g. the TrustMRR
findings) gets persisted and is actually retrievable later, instead of
living only in a chat transcript."""
import os
import logging

import httpx

logger = logging.getLogger(__name__)

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_EMBEDDING_MODEL = "gemini-embedding-001"
_EMBEDDING_DIMS = 1536
_TABLE = "sdr_research_knowledge"


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
        logger.warning("[SDRResearch] GEMINI_API_KEY not set -- embedding skipped")
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
        logger.warning("[SDRResearch] Embedding failed: %s", e)
        return None


async def ingest_research(topic: str, text: str, source: str = "") -> int:
    """Chunks, embeds, and stores a research finding under `topic` (e.g.
    'trustmrr-market-research', 'competitor-chatdash'). Returns how many
    chunks were actually stored."""
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
                    json={"topic": topic, "content": chunk, "source": source, "embedding": embedding},
                    headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
                )
                if resp.status_code < 300:
                    stored += 1
            except Exception as e:
                logger.warning("[SDRResearch] Failed to store chunk: %s", e)
    return stored


async def retrieve_research(query: str, k: int = 5) -> list[dict]:
    """Real similarity search via match_sdr_research. Returns [] (not an
    error) if nothing is stored yet or embedding fails."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return []
    embedding = await _embed(query)
    if embedding is None:
        return []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{_SUPABASE_URL}/rest/v1/rpc/match_sdr_research",
                json={"query_embedding": embedding, "match_count": k},
                headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            )
            resp.raise_for_status()
            return [{"topic": row["topic"], "content": row["content"], "source": row.get("source", "")} for row in resp.json()]
    except Exception as e:
        logger.warning("[SDRResearch] Retrieval failed: %s", e)
        return []
