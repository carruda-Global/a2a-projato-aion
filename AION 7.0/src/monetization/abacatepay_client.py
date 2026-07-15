import hashlib
import hmac
import json
import httpx
from src.config import Settings

ABACATEPAY_API_BASE = "https://api.abacatepay.com/v1"
ABACATEPAY_API_BASE_SANDBOX = "https://api.sandbox.abacatepay.com/v1"


class AbacatepayClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.abacatepay_api_key
        self.webhook_secret = settings.abacatepay_webhook_secret
        self.sandbox_mode = settings.abacatepay_sandbox_mode

    async def _http(self):
        base_url = ABACATEPAY_API_BASE_SANDBOX if self.sandbox_mode else ABACATEPAY_API_BASE
        return httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    async def create_pix_checkout(
        self,
        plan_id: str,
        customer_email: str | None = None,
        customer_name: str | None = None,
        success_url: str | None = None,
    ) -> dict | None:
        plan_config = self.settings.plans_config.get(plan_id)
        if not plan_config:
            return None

        payload = {
            "amount_cents": plan_config["amount_cents"],
            "currency": "BRL",
            "description": plan_config["name"],
            "methods": ["pix"],
            "metadata": {"plan_id": plan_id},
        }
        if customer_email:
            payload["customer_email"] = customer_email
        if customer_name:
            payload["customer_name"] = customer_name
        if success_url:
            payload["redirect_url"] = success_url

        async with await self._http() as http:
            resp = await http.post("/checkout", json=payload)
            if resp.status_code != 201:
                return None
            data = resp.json()

        return {
            "checkout_id": data.get("id", ""),
            "pix_code": data.get("pix_code", ""),
            "pix_qr_code": data.get("pix_qr_code", ""),
            "expires_at": data.get("expires_at", ""),
            "amount_cents": data.get("amount_cents", plan_config["amount_cents"]),
            "status": data.get("status", "pending"),
        }

    async def get_checkout_status(self, checkout_id: str) -> dict | None:
        async with await self._http() as http:
            resp = await http.get(f"/checkout/{checkout_id}")
            if resp.status_code != 200:
                return None
            data = resp.json()
        return {
            "checkout_id": data.get("id", ""),
            "status": data.get("status", "unknown"),
            "paid_at": data.get("paid_at"),
        }

    def verify_webhook(self, payload: bytes, signature: str) -> dict | None:
        if not self.webhook_secret:
            return None
        computed = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(computed, signature):
            return None
        data = json.loads(payload)
        return {
            "type": data.get("event", "unknown"),
            "data": data.get("data", {}),
        }

    async def close(self):
        await self.http.aclose()
