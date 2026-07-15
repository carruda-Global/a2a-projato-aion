"""Real project context for the 8 AEC core agents -- semantic retrieval via
engcopilot_embeddings.py, not the recency-only stub this used to be. The
previous version queried Supabase PostgREST with Accept-Profile: engcopilot,
which always failed silently (PostgREST only exposes public/graphql_public
by default -- confirmed via a direct API call returning "Invalid schema:
engcopilot"), so every one of the 8 core agents had been receiving empty
context since they were built. Now goes through the same asyncpg pool the
engineering_copilot module already uses for everything else."""
import logging

from src.agents.engcopilot_embeddings import retrieve_similar_context

logger = logging.getLogger(__name__)


async def retrieve_project_context(query: str, limit: int = 5) -> str:
    try:
        return await retrieve_similar_context(query, limit=limit)
    except Exception as e:
        logger.info("[AEC-RAG] engcopilot indisponivel (%s) -- respondendo sem contexto de projeto", e)
        return ""
