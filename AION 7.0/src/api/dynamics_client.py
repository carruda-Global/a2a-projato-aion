import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

class DynamicsClient:
    def __init__(self):
        self.tenant_id = os.getenv("DYNAMICS_TENANT_ID", "")
        self.client_id = os.getenv("DYNAMICS_CLIENT_ID", "")
        self.client_secret = os.getenv("DYNAMICS_CLIENT_SECRET", "")
        self.sales_url = os.getenv("DYNAMICS_SALES_URL", "")
        self.finance_url = os.getenv("DYNAMICS_FINANCE_URL", "")
        self._available = bool(self.tenant_id and self.client_id and self.client_secret)
        self._token = None

    async def _get_token(self) -> str:
        if not self._available:
            return ""
        import httpx
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": f"{self.sales_url}/.default" if self.sales_url else "https://api.businesscentral.dynamics.com/.default",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=data)
            resp.raise_for_status()
            self._token = resp.json().get("access_token", "")
        return self._token

    async def call_api(self, endpoint: str, method: str = "GET", data: dict | None = None) -> dict[str, Any]:
        if not self._available:
            logger.warning("Dynamics not configured — returning simulated response")
            return {"simulated": True, "endpoint": endpoint}
        token = await self._get_token()
        base_url = self.finance_url if "finance" in endpoint.lower() else self.sales_url
        import httpx
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"{base_url}/api/data/v9.2/{endpoint}"
        async with httpx.AsyncClient() as client:
            if method == "GET":
                resp = await client.get(url, headers=headers)
            elif method == "POST":
                resp = await client.post(url, headers=headers, json=data or {})
            elif method == "PATCH":
                resp = await client.patch(url, headers=headers, json=data or {})
            else:
                return {"error": f"Method {method} not supported"}
            resp.raise_for_status()
            return resp.json()
