import pytest
from src.agents.inventory import InventoryAgent


@pytest.mark.unit
class TestInventoryAgent:
    def test_check_stock_returns_dict(self, settings, llm_mock):
        agent = InventoryAgent(settings, llm_mock)
        items = [
            {
                "name": "Cimento",
                "stock": 10,
                "min_stock": 20,
                "daily_use": 5,
            }
        ]
        result = agent.check_stock(items)
        assert isinstance(result, dict)
        assert result["agent"] == "inventory"

    def test_check_stock_empty(self, settings, llm_mock):
        agent = InventoryAgent(settings, llm_mock)
        result = agent.check_stock([])
        assert isinstance(result, dict)

    def test_suggest_substitute_returns_string(self, settings, llm_mock):
        agent = InventoryAgent(settings, llm_mock)
        result = agent.suggest_substitute("Cimento CP-II", "Resistencia 40MPa")
        assert isinstance(result, str)

    def test_check_stock_calls_llm(self, settings, llm_mock):
        agent = InventoryAgent(settings, llm_mock)
        items = [{"name": "Tijolo", "stock": 100, "min_stock": 200, "daily_use": 50}]
        agent.check_stock(items)
        llm_mock.chat.assert_called_once()
