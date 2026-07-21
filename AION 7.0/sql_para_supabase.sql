DO $$
BEGIN
  -- S� executa se a tabela ainda n�o existe
  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'subscriptions') THEN
    CREATE TABLE subscriptions (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        external_id TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        customer_email TEXT DEFAULT '',
        customer_name TEXT DEFAULT '',
        plan_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        activated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        cancelled_at TIMESTAMPTZ,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        metadata JSONB DEFAULT '{}',
        UNIQUE(source, external_id)
    );
    CREATE INDEX idx_subscriptions_customer_id ON subscriptions(customer_id);
    CREATE INDEX idx_subscriptions_status ON subscriptions(status);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'processed_webhook_events') THEN
    CREATE TABLE processed_webhook_events (
        event_id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        event_type TEXT NOT NULL,
        payload JSONB DEFAULT '{}'
    );
    CREATE INDEX idx_webhook_events_source ON processed_webhook_events(source);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'agent_executions') THEN
    CREATE TABLE agent_executions (
        id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
        tenant_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        task_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued',
        input_summary TEXT,
        result_summary TEXT,
        llm_tokens_used INTEGER DEFAULT 0,
        cost_brl NUMERIC(10,4) DEFAULT 0,
        queued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        error_message TEXT
    );
    CREATE INDEX idx_agent_executions_tenant ON agent_executions(tenant_id);
    CREATE INDEX idx_agent_executions_status ON agent_executions(status);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'agent_registry') THEN
    CREATE TABLE agent_registry (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        cluster TEXT NOT NULL,
        description TEXT,
        llm_model TEXT NOT NULL DEFAULT 'deepseek-chat',
        status TEXT NOT NULL DEFAULT 'active',
        plan_ids TEXT[] DEFAULT '{}',
        config JSONB DEFAULT '{}',
        version TEXT DEFAULT '1.0.0',
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'audit_log') THEN
    CREATE TABLE audit_log (
        id BIGSERIAL PRIMARY KEY,
        tenant_id TEXT,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        resource_type TEXT NOT NULL,
        resource_id TEXT,
        details JSONB DEFAULT '{}',
        ip_address TEXT,
        hash TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX idx_audit_log_tenant ON audit_log(tenant_id);
    CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS microsoft_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id TEXT UNIQUE,
    token TEXT,
    plan TEXT,
    status TEXT DEFAULT 'pending',
    company TEXT,
    email TEXT,
    source TEXT DEFAULT 'microsoft_marketplace',
    activated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS voice_calls (
    id TEXT PRIMARY KEY,
    customer_email TEXT NOT NULL DEFAULT '',
    phone_number TEXT NOT NULL DEFAULT '',
    caller_number TEXT,
    direction TEXT DEFAULT 'inbound',
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER DEFAULT 0,
    outcome TEXT,
    transcript TEXT,
    recording_url TEXT,
    lead_name TEXT,
    lead_phone TEXT,
    lead_intent TEXT,
    is_trial_call BOOLEAN DEFAULT false,
    cost_usd NUMERIC(10,4) DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_voice_calls_customer ON voice_calls(customer_email);
CREATE INDEX IF NOT EXISTS idx_voice_calls_started ON voice_calls(started_at);

-- Overage billing was advertised on vendas.html ("$0.15/min after 300 min")
-- but never actually metered or charged -- every customer using more than
-- their plan cap was pure margin loss with no invoice ever created. This
-- table makes voice_overage_billing_agent.py idempotent: one row per
-- (customer_email, billing_month) so a cron that runs daily never
-- double-charges the same month twice.
-- Real Zapier/webhook subscriptions for Voice Receptionist events, scoped
-- per customer. The prior implementation kept subscriptions in an in-memory
-- Python dict (_webhook_subscriptions in zapier_integration.py) -- wiped on
-- every Render restart/redeploy, and not scoped to any customer, so it
-- could never actually deliver a specific customer's call events to their
-- own Zap. This table is what makes the "Zapier integration" real instead
-- of a dead endpoint nobody's data ever reached.
CREATE TABLE IF NOT EXISTS zapier_webhook_subscriptions (
    id TEXT PRIMARY KEY,
    customer_email TEXT NOT NULL,
    event TEXT NOT NULL,  -- 'call_completed' | 'lead_captured'
    target_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_zapier_subs_customer_event ON zapier_webhook_subscriptions(customer_email, event);

-- Billed per unique caller over the plan's monthly cap ($0.50/extra caller,
-- matching Goodcall's real, market-proven model) -- not per minute. Matches
-- what vendas.html actually sells ("unlimited minutes, up to N unique
-- callers/mo").
CREATE TABLE IF NOT EXISTS voice_overage_billing_log (
    id TEXT PRIMARY KEY,
    customer_email TEXT NOT NULL,
    billing_month TEXT NOT NULL,  -- 'YYYY-MM'
    plan_id TEXT NOT NULL,
    unique_callers_used INTEGER NOT NULL,
    unique_caller_cap INTEGER NOT NULL,
    overage_callers INTEGER NOT NULL,
    overage_rate_usd NUMERIC(6,4) NOT NULL,
    amount_usd_cents INTEGER NOT NULL,
    stripe_invoice_item_id TEXT,
    billed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(customer_email, billing_month)
);

CREATE TABLE IF NOT EXISTS voice_agent_numbers (
    customer_email TEXT PRIMARY KEY,
    phone_number_id TEXT,
    phone_number TEXT,
    provisioned_at TIMESTAMPTZ DEFAULT NOW(),
    google_place_id TEXT,
    business_name TEXT,
    business_address TEXT,
    business_phone TEXT,
    business_hours JSONB
);

DO $$
BEGIN
    ALTER TABLE voice_agent_numbers ALTER COLUMN phone_number_id DROP NOT NULL;
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

ALTER TABLE voice_agent_numbers ADD COLUMN IF NOT EXISTS google_place_id TEXT;
ALTER TABLE voice_agent_numbers ADD COLUMN IF NOT EXISTS business_name TEXT;
ALTER TABLE voice_agent_numbers ADD COLUMN IF NOT EXISTS business_address TEXT;
ALTER TABLE voice_agent_numbers ADD COLUMN IF NOT EXISTS business_phone TEXT;
ALTER TABLE voice_agent_numbers ADD COLUMN IF NOT EXISTS business_hours JSONB;

-- Growth plan (2026-07) allows up to 2 phone lines/locations per customer,
-- so customer_email can no longer be the primary key -- switch to a real
-- id, keyed uniquely on (customer_email, location_label) instead. Existing
-- rows get location_label='primary' via the column default, so today's
-- single-line customers are unaffected.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
ALTER TABLE voice_agent_numbers ADD COLUMN IF NOT EXISTS id UUID DEFAULT gen_random_uuid();
ALTER TABLE voice_agent_numbers ADD COLUMN IF NOT EXISTS location_label TEXT NOT NULL DEFAULT 'primary';

DO $$
BEGIN
    ALTER TABLE voice_agent_numbers DROP CONSTRAINT voice_agent_numbers_pkey;
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE voice_agent_numbers ADD PRIMARY KEY (id);
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE voice_agent_numbers ADD CONSTRAINT voice_agent_numbers_email_location_key UNIQUE (customer_email, location_label);
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

CREATE INDEX IF NOT EXISTS idx_ms_sub_id ON microsoft_subscriptions(subscription_id);
CREATE INDEX IF NOT EXISTS idx_ms_status ON microsoft_subscriptions(status);

-- LinkedIn post history (moved off local JSON file -- wiped on every Render
-- redeploy since that's an ephemeral filesystem, breaking the engagement
-- feedback loop's anti-repeat/weighting logic).
CREATE TABLE IF NOT EXISTS linkedin_post_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id TEXT NOT NULL,
    topico_id TEXT NOT NULL,
    tipo TEXT NOT NULL,
    url TEXT,
    published_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_li_history_topico ON linkedin_post_history(topico_id);
CREATE INDEX IF NOT EXISTS idx_li_history_published ON linkedin_post_history(published_at);

-- SDR outreach log (moved off local JSON file -- same ephemeral-filesystem
-- problem as linkedin_post_history had; this is what lets us query which
-- identified site visitors were actually contacted, and whether the email
-- send succeeded).
CREATE TABLE IF NOT EXISTS sdr_outreach_log (
    id BIGSERIAL PRIMARY KEY,
    company TEXT,
    email TEXT,
    source TEXT,
    sector TEXT,
    whatsapp_link TEXT,
    email_sent BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sdr_log_source ON sdr_outreach_log(source);
CREATE INDEX IF NOT EXISTS idx_sdr_log_created ON sdr_outreach_log(created_at);

-- Voice Receptionist RAG knowledge base -- real per-customer FAQ/policy
-- content, embedded and searched via pgvector so the assistant's system
-- prompt can be grounded in the business's actual info instead of just
-- hours/address.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS voice_agent_knowledge (
    id BIGSERIAL PRIMARY KEY,
    customer_email TEXT NOT NULL,
    location_label TEXT NOT NULL DEFAULT 'primary',
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_voice_knowledge_customer ON voice_agent_knowledge(customer_email, location_label);
CREATE INDEX IF NOT EXISTS idx_voice_knowledge_embedding
    ON voice_agent_knowledge USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE OR REPLACE FUNCTION match_voice_knowledge(
    p_customer_email TEXT,
    p_location_label TEXT,
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 3
)
RETURNS TABLE (id BIGINT, content TEXT, similarity FLOAT)
LANGUAGE SQL STABLE
AS $$
    SELECT id, content, 1 - (embedding <=> query_embedding) AS similarity
    FROM voice_agent_knowledge
    WHERE customer_email = p_customer_email AND location_label = p_location_label
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Structured post-call intent classification -- real output of the
-- LangGraph pipeline that processes the call transcript after it ends.
CREATE TABLE IF NOT EXISTS voice_call_intelligence (
    call_id TEXT PRIMARY KEY REFERENCES voice_calls(id) ON DELETE CASCADE,
    intent TEXT,
    lead_name TEXT,
    lead_phone TEXT,
    summary TEXT,
    urgency TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Compliance receipts (immutable hash chain) for the voice call pipeline.
-- src/security/audit/compliance_receipts.py's ComplianceReceipt only keeps
-- its chain in memory -- useless for an audit trail on a stateless web
-- service that restarts/redeploys constantly. This table is the real,
-- persistent version: each row's prev_receipt_hash points at the last row
-- actually in the database, not an in-memory list.
CREATE TABLE IF NOT EXISTS voice_call_compliance_receipts (
    id BIGSERIAL PRIMARY KEY,
    call_id TEXT,
    action TEXT NOT NULL,
    decision TEXT NOT NULL,
    risk_classification TEXT NOT NULL DEFAULT 'low',
    prev_receipt_hash TEXT NOT NULL,
    receipt_hash TEXT NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_voice_receipts_call ON voice_call_compliance_receipts(call_id);

-- LinkedIn anti-repeat combo tracking (moved off local JSON file -- same
-- ephemeral-filesystem problem. This one was the highest-impact instance:
-- every Render redeploy reset the "already posted" cycle back to all 312
-- combos available, so old low-engagement compliance topics kept getting
-- reselected right after every deploy instead of staying deprioritized.
CREATE TABLE IF NOT EXISTS linkedin_used_combos (
    combo_id TEXT PRIMARY KEY,
    used_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Shared, persistent compliance audit trail for ANY agent in the
-- architecture (not just Voice Receptionist) -- src/security/agent_compliance.py
CREATE TABLE IF NOT EXISTS agent_compliance_receipts (
    id BIGSERIAL PRIMARY KEY,
    agent_id TEXT NOT NULL,
    action TEXT NOT NULL,
    decision TEXT NOT NULL,
    risk_classification TEXT NOT NULL DEFAULT 'low',
    prev_receipt_hash TEXT NOT NULL,
    receipt_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_agent_compliance_agent ON agent_compliance_receipts (agent_id, created_at DESC);

-- Real system health reports (pulse every 30min + daily deep check) --
-- src/agents/system_health_agent.py
CREATE TABLE IF NOT EXISTS system_health_reports (
    id BIGSERIAL PRIMARY KEY,
    run_at TIMESTAMPTZ NOT NULL,
    deep BOOLEAN NOT NULL DEFAULT false,
    total_checks INTEGER NOT NULL,
    failures INTEGER NOT NULL DEFAULT 0,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_health_reports_run_at ON system_health_reports (run_at DESC);

-- SDR/sales research knowledge base -- src/agents/sdr_research_rag.py
CREATE TABLE IF NOT EXISTS sdr_research_knowledge (
    id BIGSERIAL PRIMARY KEY,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sdr_research_topic ON sdr_research_knowledge(topic);
CREATE INDEX IF NOT EXISTS idx_sdr_research_embedding
    ON sdr_research_knowledge USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE OR REPLACE FUNCTION match_sdr_research(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 5
)
RETURNS TABLE (id BIGINT, topic TEXT, content TEXT, source TEXT, similarity FLOAT)
LANGUAGE SQL STABLE
AS $$
    SELECT id, topic, content, source, 1 - (embedding <=> query_embedding) AS similarity
    FROM sdr_research_knowledge
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Agency white-label attribution + vertical for pre-seeded RAG templates
ALTER TABLE voice_agent_numbers ADD COLUMN IF NOT EXISTS reseller_agency TEXT;
ALTER TABLE voice_agent_numbers ADD COLUMN IF NOT EXISTS vertical TEXT;

-- Real affiliate/referral program -- src/agents/affiliate_program.py
CREATE TABLE IF NOT EXISTS affiliates (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    referral_code TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS affiliate_customers (
    id BIGSERIAL PRIMARY KEY,
    customer_email TEXT NOT NULL UNIQUE,
    referral_code TEXT NOT NULL,
    plan_id TEXT,
    signed_up_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS affiliate_commissions (
    id BIGSERIAL PRIMARY KEY,
    referral_code TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_affiliate_commissions_code ON affiliate_commissions(referral_code);

-- SDR growth-channel dedup state -- src/agents/directory_submission_agent.py.
-- Replaces the in-memory batch counter that used to reset to directory #1
-- on every backend redeploy; also used to stop the Dev.to PR job from
-- republishing identical content every 14 days.
CREATE TABLE IF NOT EXISTS sdr_growth_log (
    channel TEXT NOT NULL,
    item_key TEXT NOT NULL,
    last_sent_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (channel, item_key)
);

-- 2026-07-20: "notes" column for the SEO migration production report
-- (channel=seo_migration_report) -- stores the per-run generated/skipped
-- counts per market as JSON text, so /api/seo/agent/status can surface
-- real progress without re-invoking anything.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'sdr_growth_log' AND column_name = 'notes'
    ) THEN
        ALTER TABLE sdr_growth_log ADD COLUMN notes TEXT;
    END IF;
END $$;

-- Real AgentOps execution log -- src/security/agent_execution_log.py.
-- Duration + success/failure per agent call, the operational data that was
-- previously nonexistent (no signal short of a user noticing a slow or
-- silently-failing agent). Token/cost-per-call is a separate, larger change
-- not done yet (DeepSeekClient.chat() doesn't expose usage data today).
CREATE TABLE IF NOT EXISTS agent_execution_log (
    id BIGSERIAL PRIMARY KEY,
    agent_id TEXT NOT NULL,
    duration_ms INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_agent_execution_agent_time ON agent_execution_log (agent_id, created_at DESC);

-- Minimal real "model registry": ties every execution row to the exact
-- deployed commit (Render's RENDER_GIT_COMMIT env var) so a failure/incident
-- can be traced to precisely which code version was live. NOT a separate
-- prompt/version registry table -- prompts are already versioned by git,
-- and there's a single shared DeepSeekClient today, so a per-agent
-- model/prompt table would just duplicate what git already tracks.
ALTER TABLE agent_execution_log ADD COLUMN IF NOT EXISTS commit_hash TEXT;
