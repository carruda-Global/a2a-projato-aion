import pytest
from src.agents.procurement import ProcurementAgent


@pytest.mark.unit
class TestProcurementAgent:
    def test_process_order_returns_dict(self, settings, llm_mock):
        agent = ProcurementAgent(settings, llm_mock)
        materials = [{"name": "Cimento", "quantity": 100, "unit": "kg"}]
        result = agent.process_order(materials)
        assert isinstance(result, dict)
        assert result["agent"] == "procurement"

    def test_process_order_empty_list(self, settings, llm_mock):
        agent = ProcurementAgent(settings, llm_mock)
        result = agent.process_order([])
        assert isinstance(result, dict)

    def test_compare_quotes_returns_string(self, settings, llm_mock):
        agent = ProcurementAgent(settings, llm_mock)
        quotes = [
            {"supplier": "Fornecedor A", "price": 1000, "lead_time": "5 dias"},
            {"supplier": "Fornecedor B", "price": 1200, "lead_time": "3 dias"},
        ]
        result = agent.compare_quotes(quotes)
        assert isinstance(result, str)

    def test_process_order_calls_llm(self, settings, llm_mock):
        agent = ProcurementAgent(settings, llm_mock)
        materials = [{"name": "Aco", "quantity": 50, "unit": "un"}]
        agent.process_order(materials)
        llm_mock.chat.assert_called_once()
