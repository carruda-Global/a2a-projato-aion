import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import Settings
from src.database.supabase_client import SupabaseClient

settings = Settings()
print(f"supabase_url: {getattr(settings, 'supabase_url', 'N/A')}")
print(f"supabase_api_key: {getattr(settings, 'supabase_api_key', 'N/A')}")

client = SupabaseClient(settings)
ok = client.health_check()
print(f"Health check: {ok}")
