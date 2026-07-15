from .config import LinkedInConfig
from .oauth import LinkedInOAuth
from .mcp_client import LinkedInMCPServer
from .tools import LinkedInTools
from .scheduler import LinkedInScheduler
from .analytics import LinkedInAnalytics


class LinkedInIntegration:
    def __init__(self, config: LinkedInConfig | None = None):
        self.config = config or LinkedInConfig()
        self.oauth = LinkedInOAuth(self.config)
        self.mcp = LinkedInMCPServer(self.config, self.oauth)
        self.tools = LinkedInTools(self.config, self.oauth)
        self.scheduler = LinkedInScheduler(self.config, self.oauth)
        self.analytics = LinkedInAnalytics(self.config, self.oauth)

    async def initialize(self):
        await self.oauth.ensure_token()
        await self.scheduler.start()

    async def shutdown(self):
        await self.scheduler.stop()

    def get_mcp_server(self) -> "LinkedInMCPServer":
        return self.mcp

    def get_tools(self) -> "LinkedInTools":
        return self.tools

    def get_analytics(self) -> "LinkedInAnalytics":
        return self.analytics

    def get_scheduler(self) -> "LinkedInScheduler":
        return self.scheduler


__all__ = [
    "LinkedInConfig", "LinkedInOAuth", "LinkedInMCPServer",
    "LinkedInTools", "LinkedInScheduler", "LinkedInAnalytics",
    "LinkedInIntegration",
]
