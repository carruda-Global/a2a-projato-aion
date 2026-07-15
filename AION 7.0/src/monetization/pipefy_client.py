import json as json_mod
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class PipefyClient:
    def __init__(self, api_key: str = "", api_url: str = ""):
        self.api_key = api_key or os.getenv("PIPEFY_API_KEY", "")
        self.api_url = api_url or "https://api.pipefy.com/graphql"
        self._headers: dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def graphql(self, query: str, variables: dict | None = None) -> dict[str, Any] | None:
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        try:
            async with httpx.AsyncClient() as http:
                resp = await http.post(self.api_url, headers=self._headers, json=payload, timeout=30)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error("Erro Pipefy GraphQL: %s", e)
            return None

    async def get_pipe(self, pipe_id: str) -> dict[str, Any] | None:
        q = """
        query($id: ID!) {
          pipe(id: $id) {
            id name description color icon
            phases { id name }
            start_form_fields { id label type required }
          }
        }
        """
        result = await self.graphql(q, {"id": pipe_id})
        return result.get("data", {}).get("pipe") if result else None

    async def create_card(self, pipe_id: str, title: str, fields: dict | None = None) -> str | None:
        q = """
        mutation($input: CreateCardInput!) {
          createCard(input: $input) {
            card { id title }
          }
        }
        """
        variables = {
            "input": {
                "pipe_id": pipe_id,
                "title": title,
            }
        }
        if fields:
            variables["input"]["fields_attributes"] = [
                {"field_id": k, "field_value": v} for k, v in fields.items()
            ]
        result = await self.graphql(q, variables)
        if result and result.get("data", {}).get("createCard"):
            return result["data"]["createCard"]["card"]["id"]
        return None

    async def get_cards(self, pipe_id: str, search: str = "", limit: int = 10) -> list[dict]:
        q = """
        query($pipeId: ID!, $search: String, $first: Int) {
          cards(pipe_id: $pipeId, search: $search, first: $first) {
            edges {
              node {
                id title createdAt
                assignees { name email }
                fields { name value }
                currentPhase { name }
              }
            }
          }
        }
        """
        result = await self.graphql(q, {"pipeId": pipe_id, "search": search, "first": limit})
        if result:
            edges = result.get("data", {}).get("cards", {}).get("edges", [])
            return [e["node"] for e in edges]
        return []

    async def create_webhook(self, pipe_id: str, name: str, url: str, events: list[str]) -> bool:
        q = """
        mutation($input: CreateWebhookInput!) {
          createWebhook(input: $input) {
            webhook { id name }
          }
        }
        """
        variables = {
            "input": {
                "pipe_id": pipe_id,
                "name": name,
                "url": url,
                "events": events,
                "headers": json_mod.dumps({"Content-Type": "application/json"}),
            }
        }
        result = await self.graphql(q, variables)
        return result is not None and "createWebhook" in result.get("data", {})

    async def get_organization_members(self) -> list[dict]:
        q = """
        query {
          organization {
            members {
              id
              user { id name email }
              role
            }
          }
        }
        """
        result = await self.graphql(q)
        if result:
            org = result.get("data", {}).get("organization", {})
            return org.get("members", [])
        return []

    async def update_card_field(self, card_id: str, field_id: str, value: str) -> bool:
        q = """
        mutation($input: UpdateCardFieldInput!) {
          updateCardField(input: $input) {
            card { id }
            success
          }
        }
        """
        variables = {"input": {"card_id": card_id, "field_id": field_id, "new_value": value}}
        result = await self.graphql(q, variables)
        return bool(result and result.get("data", {}).get("updateCard", {}).get("success"))