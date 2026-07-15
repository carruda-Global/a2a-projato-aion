import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

SQL = """
CREATE TABLE IF NOT EXISTS consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    consent_given BOOLEAN DEFAULT FALSE,
    consent_version TEXT DEFAULT '1.0',
    privacy_policy_accepted BOOLEAN DEFAULT FALSE,
    terms_of_service_accepted BOOLEAN DEFAULT FALSE,
    ip_address TEXT,
    user_agent TEXT,
    previous_versions JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS consent_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS privacy_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id TEXT NOT NULL UNIQUE,
    user_id TEXT NOT NULL,
    email TEXT NOT NULL,
    request_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    details TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    response JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_consents_user_id ON consents(user_id);
CREATE INDEX IF NOT EXISTS idx_privacy_requests_user_id ON privacy_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_consent_history_user_id ON consent_history(user_id);
"""


def create_tables():
    print("[OK] SQL para tabelas de privacidade gerado:")
    print()
    for line in SQL.strip().split("\n"):
        if line.strip().startswith("CREATE TABLE"):
            table_name = line.split("CREATE TABLE IF NOT EXISTS")[1].strip().split("(")[0].strip()
            print(f"  Tabela: {table_name}")
    print()
    print("Execute no SQL Editor do Supabase ou via:")
    print("  python scripts/run_supabase_sql.py")
    print()
    print("Ou copie e cole o SQL acima no dashboard do Supabase.")


if __name__ == "__main__":
    create_tables()
