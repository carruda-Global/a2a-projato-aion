import httpx

key = "sbBX1ppramA"
deploy_id = "dep-d8u0ntfavr4c73a57sjg"

r = httpx.get(
    f"https://api.render.com/v1/services/srv-d8s3a4gjs32c73clngj0/deploys/{deploy_id}",
    params={"key": key},
    timeout=15,
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    d = r.json()
    status = d.get("status")
    created = d.get("createdAt")
    finished = d.get("finishedAt")
    commit = d.get("commit", {})
    print(f"Deploy status: {status}")
    print(f"Created: {created}")
    print(f"Finished: {finished}")
    print(f"Commit ID: {commit.get('id', 'N/A')}")
    print(f"Commit msg: {commit.get('message', 'N/A')}")
else:
    print(r.text[:500])
