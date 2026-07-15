import pytest
from src.agents.spec_analyst import SpecAnalystAgent


@pytest.mark.unit
class TestSpecAnalystAgent:
    def test_analyze_document_returns_dict(self, settings, llm_mock):
        agent = SpecAnalystAgent(settings, llm_mock)
        result = agent.analyze_document("Documento de teste")
        assert isinstance(result, dict)
        assert "agent" in result
        assert result["agent"] == "spec_analyst"

    def test_analyze_document_calls_llm(self, settings, llm_mock):
        agent = SpecAnalystAgent(settings, llm_mock)
        agent.analyze_document("Especificacao tecnica")
        llm_mock.chat.assert_called_once()

    def test_check_compliance_returns_string(self, settings, llm_mock):
        agent = SpecAnalystAgent(settings, llm_mock)
        result = agent.check_compliance("Especificacao", "NBR-6118")
        assert isinstance(result, str)

    def test_agent_has_correct_system_prompt(self, settings, llm_mock):
        agent = SpecAnalystAgent(settings, llm_mock)
        assert "engenheiro especialista" in agent.system_prompt.lower()
        assert "especificacoes" in agent.system_prompt.lower()
