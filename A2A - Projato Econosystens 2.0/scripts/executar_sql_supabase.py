import sys
sys.path.insert(0, r"C:\Users\crist\Projetos\A2A - Projato Econosystens 2.0\Ecosystem 2.0")

from supabase import create_client
from src.config import Settings

s = Settings()
client = create_client(s.supabase_url, s.supabase_api_key)

tabelas = [
    "subscriptions",
    "processed_webhook_events",
    "agent_executions",
    "agent_registry",
    "audit_log",
]

for tabela in tabelas:
    try:
        client.table(tabela).select("id").limit(1).execute()
        print(f"OK: {tabela} ja existe")
    except Exception:
        print(f"Criando: {tabela}...")
        try:
            client.rpc("exec_sql", {"sql": f"CREATE TABLE IF NOT EXISTS {tabela} (id TEXT PRIMARY KEY);"}).execute()
            print(f"  {tabela} criada")
        except Exception as e:
            print(f"  ERRO ao criar {tabela}: {e}")

print("\nPronto! Verifique no SQL Editor do Supabase se as tabelas estao la.")
