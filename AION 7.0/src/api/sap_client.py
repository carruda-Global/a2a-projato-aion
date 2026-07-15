import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

class SAPClient:
    def __init__(self):
        self.btp_url = os.getenv("SAP_BTP_URL", "")
        self.client_id = os.getenv("SAP_BTP_CLIENT_ID", "")
        self.client_secret = os.getenv("SAP_BTP_CLIENT_SECRET", "")
        self._available = bool(self.btp_url and self.client_id and self.client_secret)
        self._token = None

    async def _get_token(self) -> str:
        if not self._available:
            return ""
        import httpx
        auth_url = f"{self.btp_url}/oauth/token"
        data = {"grant_type": "client_credentials", "client_id": self.client_id, "client_secret": self.client_secret}
        async with httpx.AsyncClient() as client:
            resp = await client.post(auth_url, data=data)
            resp.raise_for_status()
            self._token = resp.json().get("access_token", "")
        return self._token

    async def call_api(self, endpoint: str, method: str = "GET", data: dict | None = None) -> dict[str, Any]:
        if not self._available:
            logger.warning("SAP BTP not configured — returning simulated response")
            return {"simulated": True, "endpoint": endpoint}
        token = await self._get_token()
        import httpx
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"{self.btp_url}/{endpoint}"
        async with httpx.AsyncClient() as client:
            if method == "GET":
                resp = await client.get(url, headers=headers)
            elif method == "POST":
                resp = await client.post(url, headers=headers, json=data or {})
            else:
                return {"error": f"Method {method} not supported"}
            resp.raise_for_status()
            return resp.json()
