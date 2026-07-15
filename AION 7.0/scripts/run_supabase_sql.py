import httpx, os
from pathlib import Path

url = os.environ.get("SUPABASE_URL", "https://gveuivwuilhhwhzjdnvg.supabase.co")
key = os.environ.get("SUPABASE_API_KEY", "")
headers = {
    "apikey": key,
    "Authorization": "Bearer " + key,
    "Content-Type": "application/json",
}

sql_path = Path(__file__).parent / "init-db.sql"
sql = sql_path.read_text(encoding="utf-8")

r = httpx.post(
    f"{url}/rest/v1/rpc/",
    headers=headers,
    json={"query": sql},
    timeout=60,
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("Tabelas criadas com sucesso!")
else:
    print(f"Resposta: {r.text[:500]}")
