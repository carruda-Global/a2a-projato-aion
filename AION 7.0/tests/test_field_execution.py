import pytest
from src.agents.field_execution import FieldExecutionAgent


@pytest.mark.unit
class TestFieldExecutionAgent:
    def test_generate_instructions_returns_dict(self, settings, llm_mock):
        agent = FieldExecutionAgent(settings, llm_mock)
        result = agent.generate_field_instructions("Construcao de muro de arrimo")
        assert isinstance(result, dict)
        assert result["agent"] == "field_execution"

    def test_generate_instructions_empty(self, settings, llm_mock):
        agent = FieldExecutionAgent(settings, llm_mock)
        result = agent.generate_field_instructions("")
        assert isinstance(result, dict)

    def test_identify_deviations_returns_string(self, settings, llm_mock):
        agent = FieldExecutionAgent(settings, llm_mock)
        result = agent.identify_deviations("Executado", "Projetado")
        assert isinstance(result, str)

    def test_generate_instructions_calls_llm(self, settings, llm_mock):
        agent = FieldExecutionAgent(settings, llm_mock)
        agent.generate_field_instructions("Laje de concreto armado")
        llm_mock.chat.assert_called_once()
