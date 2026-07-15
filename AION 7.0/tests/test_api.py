import pytest
from unittest.mock import patch, MagicMock
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio


@pytest.mark.integration
class TestAPI:
    @pytest.fixture
    def client(self):
        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    async def test_health_endpoint(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data

    async def test_list_agents_endpoint(self, client):
        response = await client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total" in data

    async def test_list_plans(self, client):
        response = await client.get("/api/v1/subscriptions/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data

    async def test_get_plan_by_id(self, client):
        response = await client.get("/api/v1/subscriptions/plans/compliance_essencial")
        assert response.status_code == 200
        assert response.json()["plan"]["id"] == "compliance_essencial"

    async def test_get_plan_not_found(self, client):
        response = await client.get("/api/v1/subscriptions/plans/invalid")
        assert response.status_code == 404
