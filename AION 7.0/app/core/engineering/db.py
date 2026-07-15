"""Conexao Postgres do Engineering Copilot — pool asyncpg, schema isolado 'engcopilot'."""
import os
import asyncpg

_pool: asyncpg.Pool | None = None


async def init_pool() -> None:
    global _pool
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("DATABASE_URL nao configurada")
    _pool = await asyncpg.create_pool(
        database_url,
        min_size=1,
        max_size=5,
        # public is appended (not replacing engcopilot) so the pgvector
        # `vector` type -- already installed in public by voice_rag.py/
        # sdr_research_rag.py -- resolves for engcopilot_embeddings.py's
        # ::vector casts. engcopilot still resolves first for every
        # unqualified table name (projetos, documentos, etc.), so this
        # doesn't change any existing query's behavior.
        server_settings={"search_path": "engcopilot,public"},
    )


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Pool nao inicializado — chame init_pool() no startup")
    return _pool
