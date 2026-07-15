CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    cluster TEXT NOT NULL,
    task_id TEXT,
    success BOOLEAN NOT NULL DEFAULT false,
    response_time_ms INTEGER NOT NULL DEFAULT 0,
    cost DECIMAL(10,4) NOT NULL DEFAULT 0,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    metric TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    tags JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evolution_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    generation INTEGER NOT NULL,
    agent_id TEXT NOT NULL,
    fitness DOUBLE PRECISION NOT NULL DEFAULT 0,
    novelty DOUBLE PRECISION NOT NULL DEFAULT 0,
    params JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    agent_id TEXT,
    user_id TEXT,
    data JSONB DEFAULT '{}',
    hash TEXT,
    previous_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_executions_tenant ON agent_executions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_executions_agent ON agent_executions(agent_id);
CREATE INDEX IF NOT EXISTS idx_executions_cluster ON agent_executions(cluster);
CREATE INDEX IF NOT EXISTS idx_metrics_tenant ON agent_metrics(tenant_id);
CREATE INDEX IF NOT EXISTS idx_evolution_tenant ON evolution_history(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_chain ON audit_log(previous_hash);

INSERT INTO tenants (name, slug) VALUES ('Default', 'default') ON CONFLICT (slug) DO NOTHING;
