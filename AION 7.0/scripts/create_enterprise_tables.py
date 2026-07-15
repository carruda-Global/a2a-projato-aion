import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

SQL = """
CREATE TABLE IF NOT EXISTS audit_chain (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tenant_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    action_type TEXT NOT NULL,
    action_hash TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    risk_score DECIMAL(4,3),
    policy_result TEXT,
    approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS bridge_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    platform TEXT,
    result TEXT,
    tenant_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workflow_id, step_index)
);
CREATE TABLE IF NOT EXISTS code_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repo TEXT NOT NULL,
    pr_number INTEGER NOT NULL,
    risk_score INTEGER,
    tenant_id TEXT NOT NULL,
    reviewed_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_chain(tenant_id);
CREATE INDEX IF NOT EXISTS idx_bridge_workflow ON bridge_workflows(workflow_id);
CREATE INDEX IF NOT EXISTS idx_code_reviews_tenant ON code_reviews(tenant_id);
"""


def main():
    print("[OK] Tabelas enterprise geradas:")
    for line in SQL.strip().split("\n"):
        if "CREATE TABLE" in line:
            name = line.split("IF NOT EXISTS")[1].strip().split("(")[0].strip()
            print(f"  {name}")
    print()
    print("Execute no SQL Editor do Supabase.")


if __name__ == "__main__":
    main()
