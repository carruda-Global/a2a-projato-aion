-- Engineering Copilot — schema isolado, mesmo padrao do nr1ai.
CREATE SCHEMA IF NOT EXISTS engcopilot;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS engcopilot.projetos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_email TEXT,
    cliente TEXT NOT NULL,
    local TEXT,
    escopo TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS engcopilot.documentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projeto_id UUID NOT NULL REFERENCES engcopilot.projetos(id) ON DELETE CASCADE,
    nome_arquivo TEXT NOT NULL,
    texto_extraido TEXT,
    dados_extraidos JSONB,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS engcopilot.equipamentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projeto_id UUID NOT NULL REFERENCES engcopilot.projetos(id) ON DELETE CASCADE,
    tag TEXT,
    tipo TEXT,
    fabricante TEXT,
    modelo TEXT,
    capacidade TEXT,
    localizacao TEXT,
    origem TEXT NOT NULL DEFAULT 'documento', -- 'documento' | 'foto'
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS engcopilot.normas_aplicaveis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projeto_id UUID NOT NULL REFERENCES engcopilot.projetos(id) ON DELETE CASCADE,
    norma TEXT NOT NULL,
    descricao TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS engcopilot.fotos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    projeto_id UUID NOT NULL REFERENCES engcopilot.projetos(id) ON DELETE CASCADE,
    nome_arquivo TEXT NOT NULL,
    analise JSONB,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Real RAG for the 8 AEC core agents (src/agents/aec_rag.py) -- was
-- previously a dead recency-based stub, PostgREST also never exposed this
-- schema (Supabase "Invalid schema: engcopilot", confirmed via direct API
-- call), so context always came back empty. Retrieval now goes through the
-- same asyncpg pool this module already uses for everything else, no
-- PostgREST/schema-exposure dependency.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS engcopilot.documento_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id UUID NOT NULL REFERENCES engcopilot.documentos(id) ON DELETE CASCADE,
    projeto_id UUID NOT NULL REFERENCES engcopilot.projetos(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_documento_chunks_embedding
    ON engcopilot.documento_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE IF NOT EXISTS engcopilot.projeto_embeddings (
    projeto_id UUID PRIMARY KEY REFERENCES engcopilot.projetos(id) ON DELETE CASCADE,
    resumo_texto TEXT NOT NULL,
    embedding VECTOR(1536),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
