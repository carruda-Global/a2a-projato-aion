"""Conexão Postgres — pool asyncpg, schema isolado 'nr1ai'."""
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
        server_settings={"search_path": "nr1ai"},
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
