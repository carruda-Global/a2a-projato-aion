import httpx, json, os

token = os.environ.get("GCP_ACCESS_TOKEN", "")
headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

r = httpx.get("https://oauth2.googleapis.com/tokeninfo?access_token=" + token, timeout=10)
print(f"Token info: {r.status_code}")
if r.status_code == 200:
    info = r.json()
    print(f"Email: {info.get('email', 'N/A')}")
    print(f"Scopes: {info.get('scope', 'N/A')}")

r2 = httpx.get(
    "https://cloudresourcemanager.googleapis.com/v1/projects/global-engenharia-498823",
    headers=headers,
    timeout=10,
)
print(f"\nProject: {r2.status_code}")
if r2.status_code == 200:
    print(json.dumps(r2.json(), indent=2)[:300])
else:
    print(r2.text[:300])
