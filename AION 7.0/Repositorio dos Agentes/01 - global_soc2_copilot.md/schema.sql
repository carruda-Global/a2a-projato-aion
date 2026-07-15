-- Global Copilots — schema compartilhado (SOC2, ISO27001, Contract Risk,
-- Vendor Risk, EU AI Act). Schema isolado "copilots", mesmo padrão do nr1ai.

CREATE SCHEMA IF NOT EXISTS copilots;
SET search_path TO copilots;

CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    licenca_tipo TEXT NOT NULL DEFAULT 'gratuita' CHECK (licenca_tipo IN ('gratuita', 'premium')),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE empresas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    razao_social TEXT NOT NULL,
    cnpj TEXT,
    setor TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Um "framework" = SOC2, ISO27001, EU AI Act, Contract Risk, Vendor Risk
CREATE TABLE frameworks (
    id TEXT PRIMARY KEY,          -- 'soc2', 'iso27001', 'eu-ai-act', 'contract-risk', 'vendor-risk'
    nome TEXT NOT NULL,
    versao TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Catálogo real de controles/critérios por framework (não é o LLM inventando)
CREATE TABLE controles (
    id TEXT PRIMARY KEY,          -- ex: 'CC1.1', 'CC6.3', 'A1.2'
    framework_id TEXT NOT NULL REFERENCES frameworks(id),
    categoria TEXT NOT NULL,      -- ex: 'Control Environment', 'Logical Access'
    nome TEXT NOT NULL,
    descricao TEXT,
    obrigatorio BOOLEAN NOT NULL DEFAULT true, -- CC1-CC9 são obrigatórios; A/PI/C/P são por escopo
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_controles_framework ON controles(framework_id);

-- Pergunta de questionário ligada a um controle específico do catálogo
CREATE TABLE perguntas (
    id TEXT PRIMARY KEY,
    controle_id TEXT NOT NULL REFERENCES controles(id),
    texto TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE respostas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    pergunta_id TEXT NOT NULL REFERENCES perguntas(id),
    status TEXT NOT NULL CHECK (status IN ('implementado', 'parcial', 'ausente', 'nao_aplicavel')),
    evidencia_texto TEXT,          -- descrição livre da evidência (política, ferramenta usada etc.)
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (empresa_id, pergunta_id)
);
CREATE INDEX idx_respostas_empresa ON respostas(empresa_id);

CREATE TABLE documentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    framework_id TEXT NOT NULL REFERENCES frameworks(id),
    formato TEXT NOT NULL CHECK (formato IN ('pdf')),
    marca_dagua BOOLEAN NOT NULL DEFAULT true,
    gerado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
