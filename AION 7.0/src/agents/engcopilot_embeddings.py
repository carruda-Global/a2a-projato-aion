"""Real embedding-based retrieval for the engcopilot schema -- powers the
8 AEC core agents (src/agents/aec_rag.py). Uses the SAME asyncpg pool the
engineering_copilot module already relies on for all its CRUD, deliberately
NOT Supabase PostgREST: a direct check confirmed PostgREST returns
"Invalid schema: engcopilot" (only public/graphql_public are exposed), so
every prior retrieve_project_context() call silently returned no context.
Same Gemini embedding model/dimension as voice_rag.py and sdr_research_rag.py
for consistency (gemini-embedding-001, 1536-dim)."""
import logging
import os

import httpx

logger = logging.getLogger(__name__)

_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_EMBEDDING_MODEL = "gemini-embedding-001"
_EMBEDDING_DIMS = 1536  # matches VECTOR(1536) in documento_chunks / projeto_embeddings


def _chunk_text(text: str, target_chars: int = 500) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    return [text[i:i + target_chars] for i in range(0, len(text), target_chars)]


def _to_vector_literal(embedding: list[float]) -> str:
    """asyncpg has no built-in pgvector codec -- send the pg vector text
    input format ('[0.1,0.2,...]') and cast explicitly in SQL, rather than
    relying on Python's list repr (which inserts spaces after commas)."""
    return "[" + ",".join(repr(float(v)) for v in embedding) + "]"


async def _embed(text: str) -> list[float] | None:
    if not _GEMINI_API_KEY or not text.strip():
        return None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{_EMBEDDING_MODEL}:embedContent",
                params={"key": _GEMINI_API_KEY},
                json={
                    "model": f"models/{_EMBEDDING_MODEL}",
                    "content": {"parts": [{"text": text[:8000]}]},
                    "outputDimensionality": _EMBEDDING_DIMS,
                },
            )
            r.raise_for_status()
            return r.json()["embedding"]["values"]
    except Exception as e:
        logger.warning("[EngCopilotRAG] Embedding failed: %s", e)
        return None


async def embed_documento(documento_id, projeto_id, texto_extraido: str) -> int:
    """Chunks and embeds a document's extracted text, called right after
    upload (Modulo 1). Returns how many chunks were actually stored --
    embedding failures are skipped, not fatal to the upload."""
    from app.core.engineering.db import get_pool

    chunks = _chunk_text(texto_extraido)
    if not chunks:
        return 0
    pool = get_pool()
    stored = 0
    for chunk in chunks:
        embedding = await _embed(chunk)
        if embedding is None:
            continue
        await pool.execute(
            "INSERT INTO documento_chunks (documento_id, projeto_id, chunk_text, embedding) VALUES ($1, $2, $3, $4::vector)",
            documento_id, projeto_id, chunk, _to_vector_literal(embedding),
        )
        stored += 1
    return stored


async def embed_projeto(projeto_id, cliente: str, local: str | None, escopo: str | None) -> bool:
    """Embeds a short project summary, called right after project creation."""
    from app.core.engineering.db import get_pool

    resumo = f"Client: {cliente or '?'} | Location: {local or '?'} | Scope: {escopo or '?'}"
    embedding = await _embed(resumo)
    if embedding is None:
        return False
    pool = get_pool()
    await pool.execute(
        """
        INSERT INTO projeto_embeddings (projeto_id, resumo_texto, embedding)
        VALUES ($1, $2, $3::vector)
        ON CONFLICT (projeto_id) DO UPDATE SET resumo_texto = $2, embedding = $3::vector, atualizado_em = now()
        """,
        projeto_id, resumo, _to_vector_literal(embedding),
    )
    return True


async def retrieve_similar_context(query: str, limit: int = 5) -> str:
    """Real semantic retrieval: embeds the query, finds the closest document
    chunks and project summaries by cosine distance across the whole
    engcopilot schema (this feeds the 8 general AEC agents, not one specific
    project, so cross-project retrieval is intentional here). Falls back to
    empty context -- never fabricates -- if embeddings aren't configured or
    nothing is stored yet."""
    from app.core.engineering.db import get_pool

    embedding = await _embed(query)
    if embedding is None:
        return ""

    vector_literal = _to_vector_literal(embedding)
    try:
        pool = get_pool()
        chunk_rows = await pool.fetch(
            """
            SELECT dc.chunk_text, d.nome_arquivo, p.cliente
            FROM documento_chunks dc
            JOIN documentos d ON d.id = dc.documento_id
            JOIN projetos p ON p.id = dc.projeto_id
            ORDER BY dc.embedding <=> $1::vector
            LIMIT $2
            """,
            vector_literal, limit,
        )
        projeto_rows = await pool.fetch(
            """
            SELECT resumo_texto FROM projeto_embeddings
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            vector_literal, min(limit, 3),
        )
    except Exception as e:
        logger.info("[EngCopilotRAG] Retrieval query failed (%s) -- responding without project context", e)
        return ""

    parts = []
    if projeto_rows:
        parts.append("Most relevant past projects:\n" + "\n".join(f"- {r['resumo_texto']}" for r in projeto_rows))
    if chunk_rows:
        parts.append("Most relevant document excerpts:\n" + "\n".join(
            f"- [{r['nome_arquivo']} / {r['cliente']}] {r['chunk_text'][:300]}" for r in chunk_rows
        ))
    return "\n\n".join(parts)
