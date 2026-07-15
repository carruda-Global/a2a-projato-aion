import json
import time
import logging
import secrets
import hashlib
import base64
from urllib.parse import parse_qs, urlencode
import httpx
import asyncio
from .config import LinkedInConfig

logger = logging.getLogger(__name__)


class LinkedInOAuthError(Exception):
    pass


class LinkedInOAuth:
    def __init__(self, config: LinkedInConfig):
        self.config = config
        self._access_token: str | None = None
        self._expires_at: float = 0
        self._refresh_token: str | None = None
        self._code_verifier: str | None = None
        self._load_token()

    def _load_token(self):
        """Local dev: reads the token file saved by the OAuth login script.
        Production (Render): the container filesystem is ephemeral and never
        ran that script, so fall back to env vars set once from the same
        file's contents (LINKEDIN_ACCESS_TOKEN / LINKEDIN_REFRESH_TOKEN /
        LINKEDIN_TOKEN_EXPIRES_AT)."""
        import os

        token_file = self.config.token_file
        if token_file.exists():
            try:
                data = json.loads(token_file.read_text())
                self._access_token = data.get("access_token")
                self._expires_at = data.get("expires_at", 0)
                self._refresh_token = data.get("refresh_token")
                return
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load token file: {e}")

        env_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        if env_token:
            self._access_token = env_token
            self._refresh_token = os.getenv("LINKEDIN_REFRESH_TOKEN") or None
            try:
                self._expires_at = float(os.getenv("LINKEDIN_TOKEN_EXPIRES_AT", "0"))
            except ValueError:
                self._expires_at = 0
            logger.info("LinkedIn token loaded from environment variables (no local token file)")

    def _save_token(self, data: dict):
        token_data = {
            "access_token": data.get("access_token"),
            "expires_at": time.time() + data.get("expires_in", 3600),
            "refresh_token": data.get("refresh_token"),
            "scope": data.get("scope", ""),
            "created_at": time.time(),
        }
        self.config.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.token_file.write_text(json.dumps(token_data, indent=2))
        self.config.token_file.chmod(0o600)

        self._access_token = token_data["access_token"]
        self._expires_at = token_data["expires_at"]
        self._refresh_token = token_data.get("refresh_token")

    def _generate_pkce_pair(self) -> tuple[str, str]:
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()
        return code_verifier, code_challenge

    async def authorize(self) -> str:
        code_verifier, code_challenge = self._generate_pkce_pair()
        self._code_verifier = code_verifier
        auth_url = f"{self.config.auth_url}&code_challenge={code_challenge}&code_challenge_method=S256"
        logger.info(f"Open this URL in your browser and authorize:\n{auth_url}")
        logger.info("")
        logger.info("Aguardando callback em http://127.0.0.1:9876/callback...")
        logger.info("Se o navegador nao redirecionar, copie a URL final e cole abaixo:")
        return await self._start_callback_server()

    async def _start_callback_server(self) -> str:
        import socket
        from http.server import HTTPServer, BaseHTTPRequestHandler

        auth_code: str | None = None

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code
                query = self.path.split("?", 1)[-1] if "?" in self.path else ""
                logger.info(f"Callback recebido: {self.path}")
                params = parse_qs(query)
                auth_code = params.get("code", [None])[0]
                if auth_code:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        "<html><body><h1>Autenticado!</h1>"
                        "<p>Voce pode fechar esta janela.</p></body></html>".encode("utf-8")
                    )
                else:
                    error = params.get("error", [""])[0]
                    error_desc = params.get("error_description", ["Erro desconhecido"])[0]
                    logger.error(f"Erro LinkedIn OAuth: {error} - {error_desc}")
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        f"<html><body><h1>Erro de Autenticacao</h1>"
                        f"<p><strong>{error}</strong></p><p>{error_desc}</p>"
                        f"</body></html>".encode()
                    )

            def log_message(self, fmt, *args):
                pass

        server = HTTPServer(("127.0.0.1", 9876), CallbackHandler)
        server.timeout = 120

        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, server.handle_request)
        except socket.timeout:
            pass
        server.server_close()

        if not auth_code:
            fallback = input("Cole a URL completa do navegador (ou pressione Enter para pular): ").strip()
            if fallback:
                params = parse_qs(fallback.split("?", 1)[-1] if "?" in fallback else "")
                auth_code = params.get("code", [None])[0]
                if not auth_code:
                    error = params.get("error", ["desconhecido"])[0]
                    error_desc = params.get("error_description", [""])[0]
                    raise LinkedInOAuthError(f"Erro LinkedIn: {error} - {error_desc}")

        if not auth_code:
            raise LinkedInOAuthError("Authorization code not received")

        await self._exchange_code(auth_code)
        return auth_code

    async def _exchange_code(self, code: str):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": self.config.redirect_uri,
        }
        if self._code_verifier:
            data["code_verifier"] = self._code_verifier
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if resp.status_code != 200:
                raise LinkedInOAuthError(f"Token exchange failed ({resp.status_code}): {resp.text}")
            self._save_token(resp.json())
            logger.info("LinkedIn OAuth token obtained and saved")

    async def refresh(self):
        if not self._refresh_token:
            raise LinkedInOAuthError("No refresh token available")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if resp.status_code != 200:
                raise LinkedInOAuthError(f"Token refresh failed: {resp.text}")
            self._save_token(resp.json())
            logger.info("LinkedIn token refreshed")

    async def ensure_token(self) -> str:
        """authorize() opens an interactive browser flow — only safe to call
        when one is actually available (local dev). On a server (no token
        file, token supplied via env var) there is no way to complete that
        flow, so we skip straight to using what we have and let the API call
        itself surface a clear 401 instead of crashing here."""
        import os

        interactive_ok = self.config.token_file.exists() or not os.getenv("LINKEDIN_ACCESS_TOKEN")
        if not self._access_token:
            if interactive_ok:
                await self.authorize()
            else:
                raise LinkedInOAuthError("No LinkedIn token available and no interactive session to authorize one")
        elif self._refresh_token and time.time() > self._expires_at - 300:
            try:
                await self.refresh()
            except LinkedInOAuthError:
                if interactive_ok:
                    logger.warning("Token refresh failed, re-authorizing")
                    await self.authorize()
                else:
                    logger.warning("Token refresh failed and no interactive session available — using existing token as-is")
        return self._access_token or ""

    @property
    def access_token(self) -> str | None:
        return self._access_token

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    @property
    def restli_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202503",
        }
