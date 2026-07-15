import httpx

r = httpx.post(
    "https://engenheiro-producao-ai.onrender.com/api/subscriptions/checkout",
    json={
        "plan_id": "starter",
        "success_url": "https://portal-three-chi-59.vercel.app/success",
        "cancel_url": "https://portal-three-chi-59.vercel.app/cancel",
    },
    timeout=30,
)
print(f"Checkout: {r.status_code}")
if r.status_code == 200:
    url = r.json().get("checkout_url", "")
    print(f"URL: {url[:80]}...")
else:
    print(r.text[:500])
