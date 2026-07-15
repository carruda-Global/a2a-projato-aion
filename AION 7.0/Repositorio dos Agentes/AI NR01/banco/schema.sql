-- NR1 AI — Módulo 1: Banco de Dados
-- PostgreSQL (Supabase) — schema isolado "nr1ai", não mistura com tabelas do AION
-- Campo `norma` presente onde faz sentido para reuso futuro (PMOC/PGRS/LTCAT),
-- sem generalizar a arquitetura agora — só evita retrabalho de schema depois.

CREATE SCHEMA IF NOT EXISTS nr1ai;
SET search_path TO nr1ai;

-- ── Usuários ──────────────────────────────────────────────────────────────
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    licenca_tipo TEXT NOT NULL DEFAULT 'gratuita' CHECK (licenca_tipo IN ('gratuita', 'premium')),
    licenca_valida_ate TIMESTAMPTZ,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Empresas ──────────────────────────────────────────────────────────────
CREATE TABLE empresas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    razao_social TEXT NOT NULL,
    nome_fantasia TEXT,
    cnpj TEXT NOT NULL,
    cnae TEXT,
    endereco TEXT,
    cidade TEXT,
    estado TEXT,
    cep TEXT,
    telefone TEXT,
    email TEXT,
    quantidade_funcionarios INTEGER,
    responsavel TEXT,
    ano_construcao INTEGER, -- usado pela regra de amianto (RQ-0047): edificações pré-2017
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_empresas_usuario ON empresas(usuario_id);
CREATE INDEX idx_empresas_cnpj ON empresas(cnpj);

-- ── Setores ───────────────────────────────────────────────────────────────
CREATE TABLE setores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_setores_empresa ON setores(empresa_id);

-- ── Funções ───────────────────────────────────────────────────────────────
CREATE TABLE funcoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setor_id UUID NOT NULL REFERENCES setores(id) ON DELETE CASCADE,
    cargo TEXT NOT NULL,
    quantidade INTEGER DEFAULT 1,
    descricao TEXT,
    jornada TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_funcoes_setor ON funcoes(setor_id);

-- ── Atividades ────────────────────────────────────────────────────────────
CREATE TABLE atividades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funcao_id UUID NOT NULL REFERENCES funcoes(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,               -- ex: "Soldagem MIG", "Corte de concreto"
    descricao TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_atividades_funcao ON atividades(funcao_id);

-- ── Máquinas ──────────────────────────────────────────────────────────────
CREATE TABLE maquinas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    fabricante TEXT,
    modelo TEXT,
    ano INTEGER,
    numero_serie TEXT,
    local TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_maquinas_empresa ON maquinas(empresa_id);

-- ── Produtos Químicos ─────────────────────────────────────────────────────
CREATE TABLE produtos_quimicos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nome TEXT NOT NULL,
    cas TEXT,                          -- número CAS, quando aplicável (ex: tolueno 108-88-3)
    fabricante TEXT,
    fispq_url TEXT,
    local_armazenamento TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_produtos_empresa ON produtos_quimicos(empresa_id);

-- ── Banco Mestre: Perigos (catálogo global, não por empresa) ────────────────
CREATE TABLE perigos (
    id TEXT PRIMARY KEY,                -- ex: 'RQ-0043', 'RF-0001' (ID do banco mestre)
    norma TEXT NOT NULL DEFAULT 'NR-1', -- campo de reuso futuro (PMOC/PGRS/LTCAT)
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL CHECK (categoria IN ('Físico', 'Químico', 'Biológico', 'Ergonômico', 'Acidente')),
    descricao TEXT,
    consequencias TEXT,
    base_legal TEXT,                    -- ex: "NR-15, Anexo 11, Quadro 1"
    versao TEXT NOT NULL DEFAULT '1.0',
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_perigos_categoria ON perigos(categoria);
CREATE INDEX idx_perigos_norma ON perigos(norma);

-- ── Controles (catálogo global, hierarquia de controle) ─────────────────────
CREATE TABLE controles (
    id TEXT PRIMARY KEY,                -- ex: 'CT-0001'
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('Eliminação', 'Substituição', 'Engenharia', 'Administrativo', 'EPI')),
    descricao TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── EPIs (catálogo global) ───────────────────────────────────────────────────
CREATE TABLE epis (
    id TEXT PRIMARY KEY,                -- ex: 'EPI-0001'
    nome TEXT NOT NULL,
    ca TEXT,                            -- Certificado de Aprovação
    fabricante TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── EPCs (catálogo global) ───────────────────────────────────────────────────
CREATE TABLE epcs (
    id TEXT PRIMARY KEY,                -- ex: 'EPC-0001'
    nome TEXT NOT NULL,
    descricao TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Treinamentos (catálogo global) ───────────────────────────────────────────
CREATE TABLE treinamentos (
    id TEXT PRIMARY KEY,                -- ex: 'TR-0001'
    nome TEXT NOT NULL,                 -- ex: "NR-12 (segurança em máquinas)"
    carga_horaria INTEGER,
    periodicidade TEXT,                 -- ex: "anual", "único"
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Riscos (avaliação de um perigo para uma empresa específica) ────────────
CREATE TABLE riscos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    atividade_id UUID REFERENCES atividades(id) ON DELETE SET NULL,
    perigo_id TEXT NOT NULL REFERENCES perigos(id),
    probabilidade INTEGER CHECK (probabilidade BETWEEN 1 AND 5),
    severidade INTEGER CHECK (severidade BETWEEN 1 AND 5),
    nivel_risco INTEGER GENERATED ALWAYS AS (probabilidade * severidade) STORED,
    status TEXT NOT NULL DEFAULT 'identificado' CHECK (status IN ('identificado', 'em_tratamento', 'controlado')),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_riscos_empresa ON riscos(empresa_id);
CREATE INDEX idx_riscos_perigo ON riscos(perigo_id);

-- ── Perguntas (Questionário Inteligente) ─────────────────────────────────────
CREATE TABLE perguntas (
    id TEXT PRIMARY KEY,                -- ex: 'Q-0001'
    texto TEXT NOT NULL,                -- ex: "Existe soldagem?"
    tipo_resposta TEXT NOT NULL DEFAULT 'sim_nao' CHECK (tipo_resposta IN ('sim_nao', 'texto', 'numero', 'selecao')),
    pergunta_pai_id TEXT REFERENCES perguntas(id), -- condicional: só aparece se pai foi respondida
    condicao_exibicao TEXT,             -- ex: "resposta_pai = 'sim'"
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Respostas (por empresa) ───────────────────────────────────────────────
CREATE TABLE respostas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    pergunta_id TEXT NOT NULL REFERENCES perguntas(id),
    valor TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (empresa_id, pergunta_id)
);
CREATE INDEX idx_respostas_empresa ON respostas(empresa_id);

-- ── Documentos gerados ────────────────────────────────────────────────────
CREATE TABLE documentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL CHECK (tipo IN ('PGR', 'Inventario', 'PlanoAcao', 'OrdemServico', 'APR', 'Cronograma')),
    formato TEXT NOT NULL CHECK (formato IN ('docx', 'pdf')),
    versao INTEGER NOT NULL DEFAULT 1,
    marca_dagua BOOLEAN NOT NULL DEFAULT true, -- false somente com licença premium
    arquivo_url TEXT,
    gerado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_documentos_empresa ON documentos(empresa_id);

-- ══════════════════════════════════════════════════════════════════════════
-- Tabelas de relacionamento (Módulo 7 — "aqui começa a inteligência")
-- ══════════════════════════════════════════════════════════════════════════

-- Quais perigos uma atividade do banco mestre normalmente gera (regra genérica,
-- não específica de uma empresa — usada pelo motor de decisão)
CREATE TABLE atividade_perigo (
    atividade_nome TEXT NOT NULL,       -- nome padronizado, ex: "Soldagem MIG"
    perigo_id TEXT NOT NULL REFERENCES perigos(id),
    PRIMARY KEY (atividade_nome, perigo_id)
);

-- Quais controles tratam um perigo (hierarquia de controle do banco mestre)
CREATE TABLE perigo_controle (
    perigo_id TEXT NOT NULL REFERENCES perigos(id),
    controle_id TEXT NOT NULL REFERENCES controles(id),
    PRIMARY KEY (perigo_id, controle_id)
);

-- Quais EPIs são indicados para um perigo
CREATE TABLE perigo_epi (
    perigo_id TEXT NOT NULL REFERENCES perigos(id),
    epi_id TEXT NOT NULL REFERENCES epis(id),
    PRIMARY KEY (perigo_id, epi_id)
);

-- Quais EPCs são indicados para um perigo
CREATE TABLE perigo_epc (
    perigo_id TEXT NOT NULL REFERENCES perigos(id),
    epc_id TEXT NOT NULL REFERENCES epcs(id),
    PRIMARY KEY (perigo_id, epc_id)
);

-- Quais treinamentos são exigidos para um perigo
CREATE TABLE perigo_treinamento (
    perigo_id TEXT NOT NULL REFERENCES perigos(id),
    treinamento_id TEXT NOT NULL REFERENCES treinamentos(id),
    PRIMARY KEY (perigo_id, treinamento_id)
);

-- Quais documentos um perigo exige gerar (ex: amianto exige bloqueio + laudo)
CREATE TABLE perigo_documento (
    perigo_id TEXT NOT NULL REFERENCES perigos(id),
    tipo_documento TEXT NOT NULL,
    PRIMARY KEY (perigo_id, tipo_documento)
);
