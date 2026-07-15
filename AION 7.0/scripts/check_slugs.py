from src.config import Settings
from src.database.supabase_client import SupabaseClient
s = Settings()
db = SupabaseClient(s)
for m in ['BR']:
    r = db.client.table('seo_pages').select('slug').eq('market', m).limit(5).execute()
    for x in r.data[:5]:
        print(f'  {x["slug"]}')
