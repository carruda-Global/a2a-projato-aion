import httpx
import os


class CopilotClient:

    async def execute_agent_step(self, step: dict, context: dict, tenant_id: str) -> dict:
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.powerplatform.com/copilotstudio/v1/agents/execute",
                headers=headers,
                json={"step": step, "context": context}
            )
        return resp.json()

    async def _get_token(self) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/v2.0/token",
                data={
                    "client_id": os.getenv("AZURE_CLIENT_ID"),
                    "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
                    "scope": "https://api.powerplatform.com/.default",
                    "grant_type": "client_credentials"
                }
            )
        return resp.json()["access_token"]
