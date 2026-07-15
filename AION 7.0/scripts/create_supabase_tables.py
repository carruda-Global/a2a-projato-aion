import httpx, os

url = os.environ.get("SUPABASE_URL", "https://gveuivwuilhhwhzjdnvg.supabase.co")
key = os.environ.get("SUPABASE_API_KEY", "")
headers = {
    "apikey": key,
    "Authorization": "Bearer " + key,
    "Content-Type": "application/json",
}

r = httpx.get(
    "https://api.supabase.com/v1/projects/gveuivwuilhhwhzjdnvg",
    headers=headers,
    timeout=10,
)
print(f"Project info: {r.status_code}")
if r.status_code == 200:
    print(r.json().get("name", ""))
else:
    print(r.text[:300])
