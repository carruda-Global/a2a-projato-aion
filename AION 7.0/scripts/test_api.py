import httpx

base = "http://localhost:8000"

r = httpx.get(f"{base}/", timeout=5)
print(f"GET /: {r.status_code}")
print(r.json())

r2 = httpx.get(f"{base}/api/agents/health", timeout=5)
print(f"\nGET /api/agents/health: {r2.status_code}")
data = r2.json()
print(f"Total agents: {data['total_agents']}")
items = list(data['agents'].items())[:3]
print(f"Sample: {items}")

r3 = httpx.get(f"{base}/api/status/default", timeout=5)
print(f"\nGET /api/status/default: {r3.status_code}")
print(str(r3.json())[:300])
