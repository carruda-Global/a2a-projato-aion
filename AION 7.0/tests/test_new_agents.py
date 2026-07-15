import pytest
from unittest.mock import MagicMock

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient


@pytest.fixture
def settings():
    s = Settings()
    s.deepseek_api_key = "test-key"
    return s


@pytest.fixture
def llm_mock():
    mock = MagicMock(spec=DeepSeekClient)
    mock.chat.return_value = "Analise concluida com sucesso."
    return mock


@pytest.mark.unit
class TestBIMCoordinatorAgent:
    def test_generate_bim_element_returns_dict(self, settings, llm_mock):
        from src.agents.bim_coordinator import BIMCoordinatorAgent
        agent = BIMCoordinatorAgent(settings, llm_mock)
        result = agent.generate_bim_element("Criar parede de concreto 3m x 2.8m")
        assert isinstance(result, dict)
        assert "bim_element" in result

    def test_clash_detection_returns_string(self, settings, llm_mock):
        from src.agents.bim_coordinator import BIMCoordinatorAgent
        agent = BIMCoordinatorAgent(settings, llm_mock)
        result = agent.clash_detection("Projeto estrutural com vigas e pilares")
        assert isinstance(result, str)


@pytest.mark.unit
class TestRequirementsAnalystAgent:
    def test_analyze_requirements_returns_dict(self, settings, llm_mock):
        from src.agents.requirements_analyst import RequirementsAnalystAgent
        agent = RequirementsAnalystAgent(settings, llm_mock)
        result = agent.analyze_requirements("Fundacao deve suportar carga de 50kN")
        assert isinstance(result, dict)
        assert "quality_analysis" in result

    def test_check_consistency_returns_string(self, settings, llm_mock):
        from src.agents.requirements_analyst import RequirementsAnalystAgent
        agent = RequirementsAnalystAgent(settings, llm_mock)
        result = agent.check_consistency("Req A", "Req B")
        assert isinstance(result, str)


@pytest.mark.unit
class TestEngineeringAssistantAgent:
    def test_answer_question_returns_dict(self, settings, llm_mock):
        from src.agents.engineering_assistant import EngineeringAssistantAgent
        agent = EngineeringAssistantAgent(settings, llm_mock)
        result = agent.answer_question("O que e NBR-6118?")
        assert isinstance(result, dict)
        assert "answer" in result

    def test_summarize_document_returns_string(self, settings, llm_mock):
        from src.agents.engineering_assistant import EngineeringAssistantAgent
        agent = EngineeringAssistantAgent(settings, llm_mock)
        result = agent.summarize_document("Documento tecnico longo")
        assert isinstance(result, str)


@pytest.mark.unit
class TestWorkSynopsisAgent:
    def test_generate_synopsis_returns_dict(self, settings, llm_mock):
        from src.agents.work_synopsis import WorkSynopsisAgent
        agent = WorkSynopsisAgent(settings, llm_mock)
        result = agent.generate_synopsis("Defeito: trinca na viga V-03")
        assert isinstance(result, dict)
        assert "synopsis" in result

    def test_summarize_project_status_returns_string(self, settings, llm_mock):
        from src.agents.work_synopsis import WorkSynopsisAgent
        agent = WorkSynopsisAgent(settings, llm_mock)
        result = agent.summarize_project_status("Obra avancou 15% esta semana")
        assert isinstance(result, str)


@pytest.mark.unit
class TestPhotoIntelligenceAgent:
    def test_analyze_photo_returns_dict(self, settings, llm_mock):
        from src.agents.photo_intelligence import PhotoIntelligenceAgent
        agent = PhotoIntelligenceAgent(settings, llm_mock)
        result = agent.analyze_photo("Foto do canteiro com trabalhadores sem EPI")
        assert isinstance(result, dict)
        assert "visual_analysis" in result

    def test_compare_with_schedule_returns_string(self, settings, llm_mock):
        from src.agents.photo_intelligence import PhotoIntelligenceAgent
        agent = PhotoIntelligenceAgent(settings, llm_mock)
        result = agent.compare_with_schedule("Foto da fundacao", "30% concluido")
        assert isinstance(result, str)


@pytest.mark.unit
class TestRFICreationAgent:
    def test_create_rfi_returns_dict(self, settings, llm_mock):
        from src.agents.rfi_creation import RFICreationAgent
        agent = RFICreationAgent(settings, llm_mock)
        result = agent.create_rfi("Qual a resistencia do concreto?")
        assert isinstance(result, dict)
        assert "rfi_document" in result

    def test_search_specification_returns_string(self, settings, llm_mock):
        from src.agents.rfi_creation import RFICreationAgent
        agent = RFICreationAgent(settings, llm_mock)
        result = agent.search_specification("Resistencia minima?", "NBR-6118")
        assert isinstance(result, str)


@pytest.mark.unit
class TestComplianceAgent:
    def test_check_compliance_returns_dict(self, settings, llm_mock):
        from src.agents.compliance import ComplianceAgent
        agent = ComplianceAgent(settings, llm_mock)
        result = agent.check_compliance("Obra com geracao de 5 ton de residuos")
        assert isinstance(result, dict)
        assert "compliance_report" in result

    def test_monitor_deadlines_returns_string(self, settings, llm_mock):
        from src.agents.compliance import ComplianceAgent
        agent = ComplianceAgent(settings, llm_mock)
        result = agent.monitor_deadlines("Licenca ambiental vence em 30 dias")
        assert isinstance(result, str)


@pytest.mark.unit
class TestRegulatoryAnalystAgent:
    def test_analisar_documento_returns_dict(self, settings, llm_mock):
        from src.agents.regulatory_analyst import RegulatoryAnalystAgent
        agent = RegulatoryAnalystAgent(settings, llm_mock)
        result = agent.analisar_documento("Contrato de prestacao de servicos")
        assert isinstance(result, dict)
        assert "analise_documento" in result

    def test_gerar_relatorio_riscos_returns_dict(self, settings, llm_mock):
        from src.agents.regulatory_analyst import RegulatoryAnalystAgent
        agent = RegulatoryAnalystAgent(settings, llm_mock)
        result = agent.gerar_relatorio_riscos("Analise completa")
        assert isinstance(result, dict)
        assert "relatorio_riscos" in result

    def test_revisar_documento_sharepoint_returns_dict(self, settings, llm_mock):
        from src.agents.regulatory_analyst import RegulatoryAnalystAgent
        agent = RegulatoryAnalystAgent(settings, llm_mock)
        result = agent.revisar_documento_sharepoint("https://sharepoint.com/doc")
        assert isinstance(result, dict)
        assert "revisao_sharepoint" in result


@pytest.mark.unit
class TestCompliancePMAgent:
    def test_gerenciar_projeto_returns_dict(self, settings, llm_mock):
        from src.agents.compliance_pm import CompliancePMAgent
        agent = CompliancePMAgent(settings, llm_mock)
        result = agent.gerenciar_projeto("Compliance - Obra XYZ")
        assert isinstance(result, dict)
        assert "plano_projeto" in result

    def test_criar_tarefa_planner_returns_dict(self, settings, llm_mock):
        from src.agents.compliance_pm import CompliancePMAgent
        agent = CompliancePMAgent(settings, llm_mock)
        result = agent.criar_tarefa_planner("Revisar documentos de compliance")
        assert isinstance(result, dict)
        assert "tarefa_planner" in result

    def test_monitorar_prazos_returns_dict(self, settings, llm_mock):
        from src.agents.compliance_pm import CompliancePMAgent
        agent = CompliancePMAgent(settings, llm_mock)
        result = agent.monitorar_prazos("Projeto A, Projeto B")
        assert isinstance(result, dict)
        assert "monitoramento_prazos" in result


@pytest.mark.unit
class TestChannelAgentAgent:
    def test_monitorar_canal_returns_dict(self, settings, llm_mock):
        from src.agents.channel_agent import ChannelAgentAgent
        agent = ChannelAgentAgent(settings, llm_mock)
        result = agent.monitorar_canal("Conversas do time financeiro")
        assert isinstance(result, dict)
        assert "monitoramento_canal" in result

    def test_detectar_riscos_returns_dict(self, settings, llm_mock):
        from src.agents.channel_agent import ChannelAgentAgent
        agent = ChannelAgentAgent(settings, llm_mock)
        result = agent.detectar_riscos("Mensagens sobre bonus nao declarados")
        assert isinstance(result, dict)
        assert "deteccao_riscos" in result

    def test_gerar_alerta_returns_dict(self, settings, llm_mock):
        from src.agents.channel_agent import ChannelAgentAgent
        agent = ChannelAgentAgent(settings, llm_mock)
        result = agent.gerar_alerta("Risco trabalhista detectado")
        assert isinstance(result, dict)
        assert "alerta_compliance" in result


@pytest.mark.unit
class TestKnowledgeAgent:
    def test_indexar_documento_returns_dict(self, settings, llm_mock):
        from src.agents.knowledge_agent import KnowledgeAgent
        agent = KnowledgeAgent(settings, llm_mock)
        result = agent.indexar_documento("Politica de privacidade 2025")
        assert isinstance(result, dict)
        assert "documento_indexado" in result

    def test_pesquisar_returns_dict(self, settings, llm_mock):
        from src.agents.knowledge_agent import KnowledgeAgent
        agent = KnowledgeAgent(settings, llm_mock)
        result = agent.pesquisar("Politica de compliance")
        assert isinstance(result, dict)
        assert "resultado_pesquisa" in result

    def test_gerar_resposta_returns_dict(self, settings, llm_mock):
        from src.agents.knowledge_agent import KnowledgeAgent
        agent = KnowledgeAgent(settings, llm_mock)
        result = agent.gerar_resposta("Contexto sobre LGPD")
        assert isinstance(result, dict)
        assert "resposta_rag" in result


@pytest.mark.unit
class TestFacilitatorAgentAgent:
    def test_facilitar_reuniao_returns_dict(self, settings, llm_mock):
        from src.agents.facilitator_agent import FacilitatorAgentAgent
        agent = FacilitatorAgentAgent(settings, llm_mock)
        result = agent.facilitar_reuniao("Pauta: revisao de conformidade")
        assert isinstance(result, dict)
        assert "reuniao_estruturada" in result

    def test_gerar_minuta_returns_dict(self, settings, llm_mock):
        from src.agents.facilitator_agent import FacilitatorAgentAgent
        agent = FacilitatorAgentAgent(settings, llm_mock)
        result = agent.gerar_minuta("Discussao sobre prazos de entrega")
        assert isinstance(result, dict)
        assert "minuta_reuniao" in result

    def test_criar_tarefas_planner_returns_dict(self, settings, llm_mock):
        from src.agents.facilitator_agent import FacilitatorAgentAgent
        agent = FacilitatorAgentAgent(settings, llm_mock)
        result = agent.criar_tarefas_planner("Decisoes da reuniao")
        assert isinstance(result, dict)
        assert "tarefas_planner" in result


@pytest.mark.unit
class TestDevExperienceAgent:
    def test_revisar_pr_returns_dict(self, settings, llm_mock):
        from src.agents.dev_experience import DevExperienceAgent
        agent = DevExperienceAgent(settings, llm_mock)
        result = agent.revisar_pr("PR #42: Adiciona modulo de login")
        assert isinstance(result, dict)
        assert "revisao_pr" in result

    def test_verificar_compliance_returns_dict(self, settings, llm_mock):
        from src.agents.dev_experience import DevExperienceAgent
        agent = DevExperienceAgent(settings, llm_mock)
        result = agent.verificar_compliance("codigo_fonte.py")
        assert isinstance(result, dict)
        assert "verificacao_compliance" in result

    def test_gerar_relatorio_qualidade_returns_dict(self, settings, llm_mock):
        from src.agents.dev_experience import DevExperienceAgent
        agent = DevExperienceAgent(settings, llm_mock)
        result = agent.gerar_relatorio_qualidade("org/repo")
        assert isinstance(result, dict)
        assert "relatorio_qualidade" in result
