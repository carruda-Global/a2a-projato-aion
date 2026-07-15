import subprocess, json

r = subprocess.run(
    ["node", "C:\\Users\\crist\\AppData\\Roaming\\npm\\node_modules\\@salesforce\\cli\\bin\\run.js", "org", "display", "--verbose", "-o", "ecosystem", "--json"],
    capture_output=True, text=True, timeout=15, shell=True
)
d = json.loads(r.stdout)
res = d.get("result", {})
print(f"Instance: {res.get('instanceUrl')}")
access_token = res.get("accessToken", "")
print(f"Token: {access_token[:50]}...")
