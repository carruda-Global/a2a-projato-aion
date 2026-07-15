import pytest
from unittest.mock import MagicMock
from src.fulfillment.provisioning.activate_tenant import TenantsAPI


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    db.client.table.return_value.insert.return_value.execute.return_value.data = [{}]
    return db


class TestTenantsAPI:
    def test_get_tenant_not_found(self, mock_db):
        api = TenantsAPI(mock_db)
        result = api.get_tenant("inexistente")
        assert result is None

    def test_get_tenant_by_email_not_found(self, mock_db):
        api = TenantsAPI(mock_db)
        result = api.get_tenant_by_email("nao@existe.com")
        assert result is None
