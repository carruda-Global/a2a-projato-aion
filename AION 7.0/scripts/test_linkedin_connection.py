import httpx, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://127.0.0.1:9876/callback")

print(f"Client ID: {client_id}")
print(f"Client Secret: {'configurado' if client_secret else 'NAO configurado'}")
print(f"Redirect URI: {redirect_uri}")
print()

# Test 1: Check if auth URL resolves
auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=openid%20profile%20email%20w_member_social"

print("=== Test 1: Authorization URL ===")
print(f"URL: {auth_url}")
print("(Abra esta URL no navegador - deve mostrar a pagina de autorizacao do LinkedIn)")

# Test 2: Try to call LinkedIn API with invalid token to see if client_id is valid
import httpx
async def test():
    print()
    print("=== Test 2: Verificando client_id ===")
    async with httpx.AsyncClient(timeout=15) as http:
        url = f"{auth_url}"
        r = await http.get(url, follow_redirects=False)
        print(f"Auth page: HTTP {r.status_code}")
        if r.status_code == 302:
            loc = r.headers.get("location", "")
            print(f"  Redirects to: {loc[:80]}...")
            if "error" in loc.lower():
                print(f"  [ERRO] LinkedIn reportou erro: {loc}")
            else:
                print(f"  [OK] LinkedIn aceitou o client_id")
        elif r.status_code == 200:
            content = r.text[:500]
            if "client_id" in content.lower() and "not found" in content.lower():
                print("  [ERRO] Client ID nao encontrado")
            elif "authorize" in content.lower():
                print("  [OK] Pagina de autorizacao encontrada")
            else:
                print(f"  Response: {content[:300]}")
        else:
            print(f"  Response: {r.text[:300]}")

    # Test 3: Try token endpoint with invalid code
    print()
    print("=== Test 3: Token endpoint ===")
    async with httpx.AsyncClient(timeout=15) as http:
        r = await http.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": "test_invalid",
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        print(f"Token endpoint: HTTP {r.status_code}")
        body = r.json() if r.status_code in (200, 400, 401) else {}
        error = body.get("error", "") if isinstance(body, dict) else ""
        error_desc = body.get("error_description", "") if isinstance(body, dict) else ""
        
        if error == "invalid_request" and "code" in error_desc.lower():
            print("  [OK] Credenciais validas! Erro esperado (code invalido)")
            print(f"  LinkedIn: {error_desc[:200]}")
        elif error:
            print(f"  [ERRO] {error}: {error_desc[:200]}")
        else:
            print(f"  Response: {r.text[:300]}")

import asyncio
asyncio.run(test())
