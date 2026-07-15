import os
import jwt
import time
import requests
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()

key_path = os.getenv(
    "SALESFORCE_KEY_PATH",
    "marketplace-integration/salesforce/salesforce.key"
)

with open(key_path, "rb") as f:
    key = serialization.load_pem_private_key(f.read(), password=None)

payload = {
    "iss": os.getenv("SALESFORCE_CLIENT_ID"),
    "sub": os.getenv("SALESFORCE_USERNAME"),
    "aud": "https://login.salesforce.com",
    "exp": int(time.time()) + 300,
    "iat": int(time.time()),
}

token = jwt.encode(payload, key, algorithm="RS256")
print("Token gerado (primeiros 50 chars):", token[:50])

r = requests.post(
    "https://login.salesforce.com/services/oauth2/token",
    data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": token,
    },
)

if r.status_code == 200:
    data = r.json()
    print("Conectado ao Salesforce via JWT!")
    print("Instancia:", data["instance_url"])
    print("Access Token:", data["access_token"][:40])
else:
    err = r.json().get("error_description", "unknown")
    print("Erro:", r.status_code, "-", err)
