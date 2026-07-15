import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "Ecosystem 2.0"))

from supabase import create_client
from src.config import Settings

settings = Settings()

if not settings.supabase_url or not settings.supabase_api_key:
    print("ERRO: SUPABASE_URL ou SUPABASE_API_KEY nao configurados")
    sys.exit(1)

client = create_client(settings.supabase_url, settings.supabase_api_key)

SQL = """
CREATE TABLE IF NOT EXISTS subscriptions (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  external_id TEXT NOT NULL,
  customer_id TEXT NOT NULL,
  customer_email TEXT,
  customer_name TEXT,
  plan_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  activated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  cancelled_at TIMESTAMPTZ,
  UNIQUE(source, external_id)
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_source_external ON subscriptions(source, external_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer ON subscriptions(customer_id);
"""

try:
    result = client.rpc("exec_sql", {"sql": SQL}).execute()
    print("Tabela 'subscriptions' criada/verificada com sucesso!")
except Exception:
    try:
        result = client.table("subscriptions").select("id").limit(1).execute()
        print("Tabela 'subscriptions' ja existe!")
    except Exception:
        print("NOTA: Nao foi possivel criar via API. Execute o SQL manualmente no SQL Editor do Supabase:")
        print()
        print(SQL)
        sys.exit(1)

print("\nTabela e indices criados. Pronto para migrar o subscription_activator.")
