import logging
import os
from typing import Any

import httpx

from src.config import Settings

logger = logging.getLogger(__name__)


class MicrosoftMarketplaceClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tenant_id = settings.microsoft_tenant_id or os.getenv("AZURE_TENANT_ID", "")
        self.client_id = settings.microsoft_client_id or os.getenv("AZURE_CLIENT_ID", "")
        self.client_secret = settings.microsoft_client_secret or os.getenv("AZURE_CLIENT_SECRET", "")
        self.api_version = settings.microsoft_fulfillment_api_version
        self._access_token: str | None = None

    def _get_token(self) -> str | None:
        if self._access_token:
            return self._access_token

        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://marketplaceapi.microsoft.com/.default",
        }

        try:
            resp = httpx.post(url, data=data, timeout=30)
            resp.raise_for_status()
            body = resp.json()
            self._access_token = body.get("access_token")
            return self._access_token
        except Exception as e:
            logger.error("Erro ao obter token Azure: %s", e)
            return None

    def resolve_purchase(self, token: str) -> dict[str, Any] | None:
        access_token = self._get_token()
        if not access_token:
            return None

        url = (
            f"https://marketplaceapi.microsoft.com/api/"
            f"saas/subscriptions/resolve?api-version={self.api_version}"
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            resp = httpx.post(url, headers=headers, json={"token": token}, timeout=30)
            resp.raise_for_status()
            body = resp.json()
            return {
                "subscription_id": body.get("id", ""),
                "customer_id": body.get("subscriberId", ""),
                "customer_name": body.get("subscriberName", ""),
                "plan_id": body.get("planId", ""),
                "offer_id": body.get("offerId", ""),
                "status": body.get("saasSubscriptionStatus", ""),
                "purchaser_email": body.get("purchaser", {}).get("email", ""),
                "purchaser_tenant_id": body.get("purchaser", {}).get("tenantId", ""),
            }
        except Exception as e:
            logger.error("Erro ao resolver purchase Azure: %s", e)
            return None

    def activate_subscription(self, subscription_id: str, plan_id: str) -> bool:
        access_token = self._get_token()
        if not access_token:
            return False

        url = (
            f"https://marketplaceapi.microsoft.com/api/"
            f"saas/subscriptions/{subscription_id}/activate"
            f"?api-version={self.api_version}"
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        body = {"planId": plan_id}

        try:
            resp = httpx.post(url, headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            logger.info("Subscription ativada Azure: %s plan=%s", subscription_id, plan_id)
            return True
        except Exception as e:
            logger.error("Erro ao ativar subscription Azure: %s", e)
            return False

    def get_subscription(self, subscription_id: str) -> dict[str, Any] | None:
        access_token = self._get_token()
        if not access_token:
            return None

        url = (
            f"https://marketplaceapi.microsoft.com/api/"
            f"saas/subscriptions/{subscription_id}"
            f"?api-version={self.api_version}"
        )
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            resp = httpx.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            body = resp.json()
            return {
                "subscription_id": body.get("id", ""),
                "plan_id": body.get("planId", ""),
                "status": body.get("saasSubscriptionStatus", ""),
                "customer_id": body.get("subscriberId", ""),
                "is_free_trial": body.get("isFreeTrial", False),
                "created_at": body.get("created", ""),
            }
        except Exception as e:
            logger.error("Erro ao buscar subscription Azure: %s", e)
            return None

    def is_subscription_active(self, subscription_id: str) -> bool:
        sub = self.get_subscription(subscription_id)
        return sub is not None and sub.get("status") == "Subscribed"
