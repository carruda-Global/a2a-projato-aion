import httpx, json, sys

base = "https://engenheiro-producao-ai.onrender.com"
results = []

tests = [
    ("GET", "/", None),
    ("GET", "/api/agents/health", None),
    ("GET", "/api/status/default", None),
    ("GET", "/salesforce/plans", None),
    ("GET", "/.well-known/agent-card.json", None),
    ("POST", "/api/agents/initialize", {"tenant": "test", "clusters": ["production"]}),
]

for method, path, body in tests:
    try:
        if method == "GET":
            r = httpx.get(base + path, timeout=15)
        else:
            r = httpx.post(base + path, json=body, timeout=15)

        ok = "OK" if r.status_code in (200, 201) else "WARN"
        print(f"[{ok}] {method} {path}: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                for k, v in list(data.items())[:3]:
                    print(f"  {k}: {str(v)[:80]}")
    except Exception as e:
        print(f"[ERR] {method} {path}: {type(e).__name__}")
