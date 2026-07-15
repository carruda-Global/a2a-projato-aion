from src.config import Settings
from src.database.supabase_client import SupabaseClient
s = Settings()
db = SupabaseClient(s)
for m in ['BR','US','MX','CO','AR']:
    r = db.client.table('seo_pages').select('slug').eq('market', m).execute()
    print(f'{m}: {len(r.data)} paginas')
