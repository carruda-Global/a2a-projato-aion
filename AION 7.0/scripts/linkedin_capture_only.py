"""Capture-only OAuth callback -- prints the raw auth code WITHOUT exchanging
it, so we can test the token exchange manually via curl and rule out a bug in
the Python exchange code itself."""
import sys, secrets, hashlib, base64
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from workers.linkedin.integrations.config import LinkedInConfig

config = LinkedInConfig()

verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()

auth_url = f"{config.auth_url}&code_challenge={challenge}&code_challenge_method=S256"
print("Open this URL:")
print(auth_url)
print()
print(f"code_verifier (save this): {verifier}")
print()
print("Waiting for callback (120s)...")

auth_code = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = self.path.split("?", 1)[-1] if "?" in self.path else ""
        params = parse_qs(query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<html><body>Got it. Close this tab.</body></html>")
    def log_message(self, *a): pass

server = HTTPServer(("127.0.0.1", 9876), Handler)
server.timeout = 120
server.handle_request()
server.server_close()

print()
print("AUTH CODE:", auth_code)
print("CODE VERIFIER:", verifier)
print("REDIRECT URI:", config.redirect_uri)
