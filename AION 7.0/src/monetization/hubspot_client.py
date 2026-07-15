import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class HubSpotClient:
    def __init__(self, client_id: str = "", client_secret: str = "", app_id: str = ""):
        self.client_id = client_id or os.getenv("HUBSPOT_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("HUBSPOT_CLIENT_SECRET", "")
        self.app_id = app_id or os.getenv("HUBSPOT_APP_ID", "")
        self._tokens: dict[str, dict] = {}

    def get_authorization_url(self, redirect_uri: str, scopes: list[str] | None = None) -> str:
        if scopes is None:
            scopes = [
                "crm.objects.companies.read",
                "crm.objects.companies.write",
                "crm.objects.contacts.read",
                "crm.objects.contacts.write",
                "crm.objects.custom.read",
                "crm.objects.custom.write",
                "crm.schemas.companies.read",
                "crm.schemas.contacts.read",
                "crm.schemas.custom.read",
            ]
        scope_str = "%20".join(scopes)
        return (
            f"https://app.hubspot.com/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope_str}"
        )

    async def exchange_code(self, code: str, redirect_uri: str) -> dict[str, Any] | None:
        url = "https://api.hubapi.com/oauth/v1/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.post(url, data=data, timeout=30)
                resp.raise_for_status()
                body = resp.json()
                return {
                    "access_token": body.get("access_token"),
                    "refresh_token": body.get("refresh_token"),
                    "expires_in": body.get("expires_in", 3600),
                    "token_type": body.get("token_type", "bearer"),
                    "hub_domain": body.get("hub_domain", ""),
                    "hub_id": body.get("hub_id", ""),
                    "user": body.get("user", ""),
                }
        except Exception as e:
            logger.error("Erro ao trocar code HubSpot: %s", e)
            return None

    async def refresh_token(self, refresh_token: str) -> dict[str, Any] | None:
        url = "https://api.hubapi.com/oauth/v1/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.post(url, data=data, timeout=30)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error("Erro ao refresh token HubSpot: %s", e)
            return None

    async def get_contact(self, access_token: str, contact_id: str) -> dict[str, Any] | None:
        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error("Erro ao buscar contato HubSpot: %s", e)
            return None

    async def get_company(self, access_token: str, company_id: str) -> dict[str, Any] | None:
        url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error("Erro ao buscar empresa HubSpot: %s", e)
            return None

    async def update_contact_properties(
        self, access_token: str, contact_id: str, properties: dict
    ) -> bool:
        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        body = {"properties": properties}
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.patch(url, headers=headers, json=body, timeout=30)
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error("Erro ao atualizar contato HubSpot: %s", e)
            return False

    async def create_note(
        self, access_token: str, object_type: str, object_id: str, body: str
    ) -> dict[str, Any] | None:
        url = "https://api.hubapi.com/crm/v3/objects/notes"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "properties": {"hs_note_body": body},
            "associations": [
                {
                    "to": {"id": object_id},
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            # 202 = note->contact, 189 = note->company (HubSpot default association type IDs)
                            "associationTypeId": 202 if object_type == "contact" else 189,
                        }
                    ],
                }
            ],
        }
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.post(url, headers=headers, json=payload, timeout=30)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error("Erro ao criar nota HubSpot: %s", e)
            return None

    async def create_custom_object(
        self, access_token: str, object_type_id: str, properties: dict
    ) -> dict[str, Any] | None:
        url = f"https://api.hubapi.com/crm/v3/objects/{object_type_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        body = {"properties": properties}
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.post(url, headers=headers, json=body, timeout=30)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error("Erro ao criar objeto custom HubSpot: %s", e)
            return None

    async def search_companies(
        self, access_token: str, filters: list[dict], limit: int = 50
    ) -> list[dict[str, Any]]:
        url = "https://api.hubapi.com/crm/v3/objects/companies/search"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        body = {"filterGroups": [{"filters": filters}], "limit": limit}
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.post(url, headers=headers, json=body, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                return data.get("results", [])
        except Exception as e:
            logger.error("Erro ao buscar empresas HubSpot: %s", e)
            return []

    async def register_webhook(
        self, access_token: str, target_url: str, event_types: list[str]
    ) -> bool:
        url = "https://api.hubapi.com/webhooks/v3/subscriptions"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        for event_type in event_types:
            body = {
                "eventType": event_type,
                "propertyName": "",
                "active": True,
            }
            try:
                async with httpx.AsyncClient() as http:
                    resp = await http.post(url, headers=headers, json=body, timeout=30)
                    resp.raise_for_status()
            except Exception as e:
                logger.error("Erro ao registrar webhook %s: %s", event_type, e)
                return False
        return True
