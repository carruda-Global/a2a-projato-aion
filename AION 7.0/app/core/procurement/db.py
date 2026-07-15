"""Conexao Postgres do Procurement Copilot — pool asyncpg, schema isolado
'procurement'. Mesmo padrao usado pelo NR1 AI (app/core/database/db.py)."""
import os
import asyncpg

_pool: asyncpg.Pool | None = None

_SCHEMA_SQL = """
CREATE SCHEMA IF NOT EXISTS procurement;

CREATE TABLE IF NOT EXISTS procurement.fornecedores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome TEXT NOT NULL,
    cnpj TEXT,
    categoria TEXT,
    tem_iso9001 BOOLEAN DEFAULT FALSE,
    tem_iso14001 BOOLEAN DEFAULT FALSE,
    tem_certificado_seguranca BOOLEAN DEFAULT FALSE,
    anos_mercado INTEGER DEFAULT 0,
    entregas_no_prazo_pct INTEGER DEFAULT 0,
    incidentes_qualidade INTEGER DEFAULT 0,
    score_risco INTEGER,
    classificacao TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS procurement.requisicoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    descricao TEXT NOT NULL,
    quantidade NUMERIC,
    unidade TEXT,
    status TEXT NOT NULL DEFAULT 'aberta',
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS procurement.rfqs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requisicao_id UUID REFERENCES procurement.requisicoes(id) ON DELETE CASCADE,
    escopo TEXT,
    criterios_tecnicos TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS procurement.cotacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id UUID REFERENCES procurement.rfqs(id) ON DELETE CASCADE,
    fornecedor_id UUID REFERENCES procurement.fornecedores(id),
    preco NUMERIC NOT NULL,
    prazo_dias INTEGER,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS procurement.compras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fornecedor_id UUID REFERENCES procurement.fornecedores(id),
    categoria TEXT,
    valor NUMERIC NOT NULL,
    data_compra DATE NOT NULL DEFAULT CURRENT_DATE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


async def init_pool() -> None:
    global _pool
    database_url = os.getenv("PROCUREMENT_DATABASE_URL", "") or os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("PROCUREMENT_DATABASE_URL / DATABASE_URL nao configurada")
    _pool = await asyncpg.create_pool(
        database_url,
        min_size=1,
        max_size=5,
        server_settings={"search_path": "procurement"},
    )
    async with _pool.acquire() as conn:
        await conn.execute(_SCHEMA_SQL)


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Pool nao inicializado — chame init_pool() no startup")
    return _pool
