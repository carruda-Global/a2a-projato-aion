import pytest
from src.agents.logistics import LogisticsAgent


@pytest.mark.unit
class TestLogisticsAgent:
    def test_track_shipment_returns_dict(self, settings, llm_mock):
        agent = LogisticsAgent(settings, llm_mock)
        shipment = {
            "product": "Cimento",
            "origin": "SP",
            "destination": "RJ",
            "expected_date": "2026-07-01",
            "status": "em_transito",
        }
        result = agent.track_shipment(shipment)
        assert isinstance(result, dict)
        assert result["agent"] == "logistics"

    def test_track_shipment_empty(self, settings, llm_mock):
        agent = LogisticsAgent(settings, llm_mock)
        result = agent.track_shipment({})
        assert isinstance(result, dict)

    def test_check_delivery_issues_returns_string(self, settings, llm_mock):
        agent = LogisticsAgent(settings, llm_mock)
        deliveries = [
            {"order_id": "123", "status": "atrasado", "eta": "2026-06-25"},
            {"order_id": "456", "status": "em_transito", "eta": "2026-06-28"},
        ]
        result = agent.check_delivery_issues(deliveries)
        assert isinstance(result, str)

    def test_track_shipment_calls_llm(self, settings, llm_mock):
        agent = LogisticsAgent(settings, llm_mock)
        agent.track_shipment({"product": "Aco", "status": "pendente"})
        llm_mock.chat.assert_called_once()
