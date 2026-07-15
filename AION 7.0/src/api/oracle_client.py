import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

class OracleClient:
    def __init__(self):
        self.tenant_id = os.getenv("ORACLE_TENANT_ID", "")
        self.username = os.getenv("ORACLE_USERNAME", "")
        self.password = os.getenv("ORACLE_PASSWORD", "")
        self.erp_url = os.getenv("ORACLE_FUSION_ERP_URL", "")
        self.hcm_url = os.getenv("ORACLE_FUSION_HCM_URL", "")
        self.scm_url = os.getenv("ORACLE_FUSION_SCM_URL", "")
        self._available = bool(self.tenant_id and self.username and self.password)

    async def call_api(self, module: str, endpoint: str, method: str = "GET", data: dict | None = None) -> dict[str, Any]:
        if not self._available:
            logger.warning("Oracle not configured — returning simulated response")
            return {"simulated": True, "module": module, "endpoint": endpoint}
        base_urls = {"erp": self.erp_url, "hcm": self.hcm_url, "scm": self.scm_url}
        base = base_urls.get(module, self.erp_url)
        import httpx
        from base64 import b64encode
        auth = b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        url = f"{base}/fscmRestApi/resources/11.13.18.05/{endpoint}"
        async with httpx.AsyncClient() as client:
            if method == "GET":
                resp = await client.get(url, headers=headers)
            elif method == "POST":
                resp = await client.post(url, headers=headers, json=data or {})
            else:
                return {"error": f"Method {method} not supported"}
            resp.raise_for_status()
            return resp.json()
