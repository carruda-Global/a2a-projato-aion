import httpx

key = "sbBX1ppramA"
headers = {"Accept": "application/json"}

r = httpx.get(
    "https://api.render.com/v1/services",
    headers=headers,
    params={"key": key},
    timeout=10,
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    for s in r.json():
        print(f"Name: {s.get('name')}")
        print(f"  ID: {s.get('id')}")
        print(f"  Repo: {s.get('repo')}")
        print(f"  Branch: {s.get('branch')}")
        print(f"  Env: {s.get('env')}")
        print(f"  ServiceURL: {s.get('serviceDetails', {}).get('url', 'N/A')}")
        print()
else:
    print(r.text[:500])
