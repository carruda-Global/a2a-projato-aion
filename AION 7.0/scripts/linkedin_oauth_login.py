import sys, asyncio, logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)

from workers.linkedin.integrations.config import LinkedInConfig
from workers.linkedin.integrations.oauth import LinkedInOAuth

async def main():
    config = LinkedInConfig()
    oauth = LinkedInOAuth(config)

    # Build the REAL auth URL the same way oauth.authorize() does internally
    # (matching PKCE pair) instead of the old placeholder/mismatched URL that
    # would have made the token exchange fail even after a successful login.
    code_verifier, code_challenge = oauth._generate_pkce_pair()
    oauth._code_verifier = code_verifier
    real_auth_url = f"{config.auth_url}&code_challenge={code_challenge}&code_challenge_method=S256"

    print("=" * 60)
    print("SERVIDOR RODANDO NA PORTA 9876")
    print("=" * 60)
    print()
    print("AGORA abra este link no navegador:")
    print()
    print(real_auth_url)
    print()
    print("Aguardando autorizacao (120 segundos)...")
    print()

    try:
        # Call the callback server directly with the PKCE pair generated
        # above -- calling oauth.authorize() here would regenerate a NEW
        # (mismatched) pair and break the token exchange.
        auth_code = await oauth._start_callback_server()
        print()
        print("=" * 60)
        print("SUCESSO! Token obtido.")
        print("=" * 60)
        print(f"Code: {auth_code[:40]}...")

        import httpx
        token = oauth.access_token
        if token:
            async with httpx.AsyncClient(timeout=15) as http:
                r = await http.get(
                    "https://api.linkedin.com/v2/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if r.status_code == 200:
                    user = r.json()
                    print(f"Nome: {user.get('name')}")
                    print(f"Email: {user.get('email')}")
                    print(f"ID: {user.get('sub')}")
                    print()
                    print("Token salvo no disco. LinkedIn conectado!")
    except Exception as e:
        print(f"Erro: {e}")

asyncio.run(main())
