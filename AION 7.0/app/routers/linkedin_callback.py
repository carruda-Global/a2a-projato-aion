from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/linkedin", tags=["linkedin"])

_linkedin_codes: dict[str, str] = {}


@router.get("/callback", response_class=HTMLResponse)
async def linkedin_callback(code: str = Query(default=""), error: str = Query(default=""), error_description: str = Query(default="")):
    if error:
        return HTMLResponse(content=f"""<html><body style="font-family:sans-serif;max-width:600px;margin:40px auto">
<h1 style="color:red">Erro de Autenticacao LinkedIn</h1>
<p><strong>{error}</strong></p>
<p>{error_description}</p>
</body></html>""")

    if not code:
        return HTMLResponse(content="""<html><body style="font-family:sans-serif;max-width:600px;margin:40px auto">
<h1>Callback LinkedIn</h1><p>Nenhum authorization code recebido.</p></body></html>""")

    import secrets
    token = secrets.token_urlsafe(8)
    _linkedin_codes[token] = code
    logger.info(f"LinkedIn code capturado: token={token} code={code[:20]}...")

    return HTMLResponse(content=f"""<html><body style="font-family:sans-serif;max-width:600px;margin:40px auto;text-align:center">
<h1 style="color:green">LinkedIn Autorizado!</h1>
<p>Authorization code recebido com sucesso.</p>
<p style="font-size:24px;font-family:monospace;background:#eee;padding:10px">{code[:30]}...</p>
<p><strong>Code Token:</strong> {token}</p>
<p>Voce pode fechar esta janela.</p>
</body></html>""")


@router.get("/exchange/{token}")
async def exchange_code(token: str):
    code = _linkedin_codes.pop(token, None)
    if not code:
        return {"error": "Token invalido ou expirado"}

    import os
    import httpx
    from dotenv import load_dotenv
    load_dotenv()

    client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    redirect_uri = "https://engenheiro-producao-ai.onrender.com/linkedin/callback"

    async with httpx.AsyncClient(timeout=30) as http:
        resp = await http.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code != 200:
            return {"error": f"Token exchange failed: {resp.status_code}", "detail": resp.text[:300]}

        token_data = resp.json()
        access_token = token_data.get("access_token", "")
        expires_in = token_data.get("expires_in", 0)

        import json
        from pathlib import Path
        from datetime import datetime, timezone

        token_file = Path.home() / ".config" / "aion" / "linkedin" / "tokens" / "access_token.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(json.dumps({
            "access_token": access_token,
            "refresh_token": token_data.get("refresh_token", ""),
            "expires_in": expires_in,
            "scope": token_data.get("scope", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }, indent=2))

        logger.info(f"LinkedIn token salvo em {token_file}")

        return {
            "status": "success",
            "expires_in": expires_in,
            "token_saved": str(token_file),
        }
