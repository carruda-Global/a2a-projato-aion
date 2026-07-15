import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import ASGITransport, AsyncClient

from app.main import app

import_mark = pytest.mark.asyncio

skip_integration = pytest.mark.skipif(
    True,
    reason="Integration tests require running API",
)


@pytest.mark.unit
class TestOracleMarketplaceRouter:
    @pytest.fixture
    def client(self):
        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    @skip_integration
    async def test_activate_missing_token(self, client):
        response = await client.get("/api/v1/oracle-marketplace/activate")
        assert response.status_code == 400
        data = response.json()
        assert "token" in data["detail"].lower()

    async def test_plans_endpoint(self, client):
        response = await client.get("/api/v1/oracle-marketplace/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) >= 4

    async def test_plans_have_pricing(self, client):
        response = await client.get("/api/v1/oracle-marketplace/plans")
        data = response.json()
        for plan in data["plans"]:
            assert "price_brl" in plan
            assert "price_usd" in plan


@pytest.mark.unit
class TestOracleClient:
    def test_client_creation(self):
        from src.config import Settings
        from src.monetization.oracle_client import OracleMarketplaceClient

        settings = Settings()
        client = OracleMarketplaceClient(settings)
        assert client.product_id == settings.oracle_product_id

    @patch("oci.self.PartnerIntegerationClient")
    def test_resolve_subscription_success(self, mock_client_class):
        from src.config import Settings
        from src.monetization.oracle_client import OracleMarketplaceClient

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_response = MagicMock()
        mock_sub = MagicMock()
        mock_sub.id = "sub_123"
        mock_sub.tenant_id = "tenancy_abc"
        mock_sub.lifecycle_state = "PENDING_ACTIVATION"
        mock_sub.subscription_details = {"plan_name": "Enterprise", "plan_id": "enterprise"}
        mock_response.data.subscription = mock_sub
        mock_instance.resolve_subscription.return_value = mock_response

        settings = Settings()
        client = OracleMarketplaceClient(settings)
        result = client.resolve_subscription("test_jwt_token")

        assert result is not None
        assert result["subscription_id"] == "sub_123"
        assert result["state"] == "PENDING_ACTIVATION"

    @patch("oci.self.PartnerIntegerationClient")
    def test_activate_subscription_success(self, mock_client_class):
        from src.config import Settings
        from src.monetization.oracle_client import OracleMarketplaceClient

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.activate_subscription.return_value = MagicMock()

        settings = Settings()
        client = OracleMarketplaceClient(settings)
        result = client.activate_subscription("sub_123")
        assert result is True

    @patch("oci.self.PartnerIntegerationClient")
    def test_activate_subscription_failure(self, mock_client_class):
        import oci.exceptions
        from src.config import Settings
        from src.monetization.oracle_client import OracleMarketplaceClient

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.activate_subscription.side_effect = oci.exceptions.ServiceError(
            status=400, code=None, message="Error", headers={}
        )

        settings = Settings()
        client = OracleMarketplaceClient(settings)
        result = client.activate_subscription("sub_123")
        assert result is False

    @patch("oci.self.PartnerIntegerationClient")
    def test_list_subscriptions(self, mock_client_class):
        from src.config import Settings
        from src.monetization.oracle_client import OracleMarketplaceClient

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_response = MagicMock()
        mock_item = MagicMock()
        mock_item.id = "sub_1"
        mock_item.tenant_id = "tenancy_1"
        mock_item.lifecycle_state = "ACTIVE"
        mock_item.time_created = None
        mock_response.data.items = [mock_item]
        mock_instance.listing_subscriptions.return_value = mock_response

        settings = Settings()
        client = OracleMarketplaceClient(settings)
        result = client.list_subscriptions()
        assert len(result) == 1
        assert result[0]["subscription_id"] == "sub_1"
        assert result[0]["state"] == "ACTIVE"
