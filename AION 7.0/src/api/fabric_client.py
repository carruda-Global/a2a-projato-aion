import httpx
import os


class FabricIQClient:

    def __init__(self):
        self.base_url = "https://api.fabric.microsoft.com/v1"
        self.token = None

    async def get_org_context(self, tenant_id: str) -> dict:
        headers = {"Authorization": f"Bearer {await self._get_token()}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/workspaces/{tenant_id}/context", headers=headers)
        return resp.json()

    async def _get_token(self) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token",
                data={
                    "client_id": os.getenv("AZURE_CLIENT_ID"),
                    "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
                    "scope": "https://api.fabric.microsoft.com/.default",
                    "grant_type": "client_credentials"
                }
            )
        return resp.json()["access_token"]
