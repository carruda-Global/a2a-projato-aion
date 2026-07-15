from dataclasses import dataclass, field
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LinkedInConfig:
    client_id: str = field(default_factory=lambda: os.getenv("LINKEDIN_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: os.getenv("LINKEDIN_CLIENT_SECRET", ""))
    redirect_uri: str = field(default_factory=lambda: os.getenv("LINKEDIN_REDIRECT_URI", "https://f8acb0ea52b9c1.lhr.life/callback"))
    # w_member_social (needed to actually publish posts/carousels) requires
    # the separate "Share on LinkedIn" product, which is NOT auto-approved
    # like "Sign In with LinkedIn using OpenID Connect" -- confirmed via the
    # app's own OIDC discovery doc, which only lists openid/profile/email
    # under scopes_supported. Until that product is approved, requesting
    # w_member_social makes the whole token exchange fail with a generic
    # invalid_client error. Add it back once LinkedIn approves the product.
    scopes: list[str] = field(default_factory=lambda: [
        "profile", "email", "openid",
    ])
    token_storage_path: Path = field(
        default_factory=lambda: Path.home() / ".config" / "aion" / "linkedin" / "tokens"
    )
    mcp_host: str = field(default_factory=lambda: os.getenv("LINKEDIN_MCP_HOST", "127.0.0.1"))
    mcp_port: int = int(os.getenv("LINKEDIN_MCP_PORT", "9800"))
    api_base_url: str = "https://api.linkedin.com/v2"
    api_restli: str = "https://api.linkedin.com/rest"
    mcp_transport: str = field(default_factory=lambda: os.getenv("LINKEDIN_MCP_TRANSPORT", "stdio"))
    scheduler_check_interval: int = 300
    default_schedule_timezone: str = "America/Sao_Paulo"

    @property
    def token_file(self) -> Path:
        self.token_storage_path.mkdir(parents=True, exist_ok=True)
        return self.token_storage_path / "access_token.json"

    @property
    def auth_url(self) -> str:
        params = (
            f"response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={'%20'.join(self.scopes)}"
        )
        return f"https://www.linkedin.com/oauth/v2/authorization?{params}"

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)
