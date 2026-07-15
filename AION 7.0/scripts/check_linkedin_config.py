import os
from pathlib import Path

os.chdir(Path(__file__).parent)

from dotenv import load_dotenv
load_dotenv()

linkedin_vars = [
    "LINKEDIN_CLIENT_ID",
    "LINKEDIN_CLIENT_SECRET",
    "LINKEDIN_REDIRECT_URI",
    "LINKEDIN_MCP_HOST",
    "LINKEDIN_MCP_PORT",
]

print("=== LinkedIn Config Status ===")
for var in linkedin_vars:
    val = os.getenv(var, "")
    if val:
        if "SECRET" in var or "KEY" in var:
            print(f"  [OK] {var}: configurado ({len(val)} chars)")
        else:
            print(f"  [OK] {var}: {val}")
    else:
        print(f"  [--] {var}: NAO configurado")

print()

# Check if token file exists
from workers.linkedin.integrations.config import LinkedInConfig
config = LinkedInConfig()
if config.is_configured:
    print(f"LinkedIn Config: OK")
    token_file = config.token_file
    if token_file.exists():
        import json
        data = json.loads(token_file.read_text())
        print(f"Token: obtido em {data.get('created_at', '?')}")
        print(f"Expira: {data.get('expires_at', '?')} (faltam {int(data.get('expires_at',0) - __import__('time').time())}s)")
    else:
        print("Token: NAO obtido - precisa rodar OAuth flow")
else:
    print("LinkedIn Config: NAO configurado")
    print()
    print("Para conectar:")
    print("1. Va em https://www.linkedin.com/developers/")
    print("2. Crie um App (ou use existente)")
    print("3. Copie Client ID e Client Secret")
    print("4. Configure redirect URI: http://127.0.0.1:9876/callback")
    print("5. Adicione no .env:")
    print("   LINKEDIN_CLIENT_ID=seu-client-id")
    print("   LINKEDIN_CLIENT_SECRET=seu-client-secret")
