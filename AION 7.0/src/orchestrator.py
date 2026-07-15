import logging
from typing import Any

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from src.api.openai_client import OpenAIClient
from src.api.gemini_client import GeminiClient
from src.api.claude_client import ClaudeClient
from src.agents import (
    SpecAnalystAgent, ProcurementAgent, InventoryAgent, LogisticsAgent,
    FieldExecutionAgent, BIMCoordinatorAgent, RequirementsAnalystAgent,
    EngineeringAssistantAgent, WorkSynopsisAgent, PhotoIntelligenceAgent,
    RFICreationAgent, ComplianceAgent,
    NR1PsicossocialAgent, TributarioCBSIBSAgent, LgpdOperacionalAgent,
    ESGIFRSAgent, InventarioCarbonoAgent, Escopo3FornecedoresAgent,
    CanalDenunciasAgent, IgualdadeSalarialAgent, ComplianceAnticorrupcaoAgent,
    RegulatoryAnalystAgent, CompliancePMAgent, ChannelAgent,
    KnowledgeAgent, FacilitatorAgentAgent, DevExperienceAgent,
    OnboardingFuncionariosAgent, AtendimentoClientePTBRAgent,
    ConciliacaoFinanceiraAgent,
    DynamicsSalesAgent, DynamicsFinanceAgent, DynamicsSupplyChainAgent,
    DynamicsHRAgent, DynamicsCustomerServiceAgent, PowerBIComplianceAgent,
    MasterOrchestratorAgent, CrossPlatformBridgeAgent,
    RegulatoryWatchAgent, ClientIntelligenceAgent, QualityCriticAgent,
    MetaLearningAgent, EcosystemEvolutionAgent, FederatedKnowledgeAgent,
    SoftwareEngineeringAgent, SalesAgent, WorkforceOrchestratorAgent,
)


class Orchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = DeepSeekClient(settings)
        self.openrouter = OpenAIClient(settings)
        self.gemini = GeminiClient()
        self.claude = ClaudeClient()
        self.logger = logging.getLogger(__name__)
        self.agents: dict[str, Any] = {}
        self._init_agents()

    async def initialize(self) -> None:
        # _init_agents() ja roda no __init__ — este metodo existe para compatibilidade com o startup async do FastAPI
        self.logger.info("Orchestrator pronto: %d agentes ativos", len(self.agents))

    def _init_agents(self):
        agent_config = self.settings.agents_config
        llm_routing = self.settings.llm_routing_config
        sensitive_agents = llm_routing.get("sensitive_agents", [])
        reasoning_agents = llm_routing.get("reasoning_agents", [])

        def _pick_llm(agent_id: str):
            if agent_id in reasoning_agents:
                return self.claude
            if agent_id in sensitive_agents:
                return self.gemini
            provider = self.settings.llm_default_provider
            if provider == "openrouter":
                return self.openrouter
            return self.llm

        _agent_map = {
            "spec_analyst": SpecAnalystAgent, "procurement": ProcurementAgent,
            "inventory": InventoryAgent, "logistics": LogisticsAgent,
            "field_execution": FieldExecutionAgent,
            "bim_coordinator": BIMCoordinatorAgent,
            "requirements_analyst": RequirementsAnalystAgent,
            "engineering_assistant": EngineeringAssistantAgent,
            "work_synopsis": WorkSynopsisAgent,
            "photo_intelligence": PhotoIntelligenceAgent,
            "rfi_creation": RFICreationAgent, "compliance": ComplianceAgent,
            "nr1_psicossocial": NR1PsicossocialAgent,
            "tributario_cbs_ibs": TributarioCBSIBSAgent,
            "lgpd_operacional": LgpdOperacionalAgent,
            "esg_ifrs": ESGIFRSAgent,
            "inventario_carbono": InventarioCarbonoAgent,
            "escopo3_fornecedores": Escopo3FornecedoresAgent,
            "canal_denuncias": CanalDenunciasAgent,
            "igualdade_salarial": IgualdadeSalarialAgent,
            "compliance_anticorrupcao": ComplianceAnticorrupcaoAgent,
            "regulatory_analyst": RegulatoryAnalystAgent,
            "compliance_pm": CompliancePMAgent,
            "channel_agent": ChannelAgent,
            "knowledge_agent": KnowledgeAgent,
            "facilitator_agent": FacilitatorAgentAgent,
            "dev_experience": DevExperienceAgent,
            "onboarding_funcionarios": OnboardingFuncionariosAgent,
            "atendimento_cliente_ptbr": AtendimentoClientePTBRAgent,
            "conciliacao_financeira": ConciliacaoFinanceiraAgent,
            "dynamics_sales": DynamicsSalesAgent,
            "dynamics_finance": DynamicsFinanceAgent,
            "dynamics_supply_chain": DynamicsSupplyChainAgent,
            "dynamics_hr": DynamicsHRAgent,
            "dynamics_customer_service": DynamicsCustomerServiceAgent,
            "powerbi_compliance": PowerBIComplianceAgent,
            "master_orchestrator": MasterOrchestratorAgent,
            "cross_platform_bridge": CrossPlatformBridgeAgent,
            "regulatory_watch": RegulatoryWatchAgent,
            "client_intelligence": ClientIntelligenceAgent,
            "quality_critic": QualityCriticAgent,
            "meta_learning": MetaLearningAgent,
            "ecosystem_evolution": EcosystemEvolutionAgent,
            "federated_knowledge": FederatedKnowledgeAgent,
            "software_engineering": SoftwareEngineeringAgent,
            "sales_agent": SalesAgent,
            "workforce_orchestrator": WorkforceOrchestratorAgent,
        }

        for agent_id, agent_class in _agent_map.items():
            llm = _pick_llm(agent_id)
            self.agents[agent_id] = agent_class(self.settings, llm)

        self.logger.info("Agents initialized: %s", ", ".join(self.agents.keys()))

    def process_workflow(self, initial_input: dict) -> list[dict]:
        results = []
        current_context = initial_input

        workflow_chain = [
            "spec_analyst", "procurement", "inventory", "logistics", "field_execution",
            "bim_coordinator", "requirements_analyst", "engineering_assistant", "work_synopsis",
            "photo_intelligence", "rfi_creation", "compliance",
            "nr1_psicossocial", "tributario_cbs_ibs", "lgpd_operacional",
            "esg_ifrs", "inventario_carbono", "escopo3_fornecedores",
            "canal_denuncias", "igualdade_salarial", "compliance_anticorrupcao",
            "regulatory_analyst", "compliance_pm", "channel_agent", "knowledge_agent",
            "facilitator_agent", "dev_experience",
            "onboarding_funcionarios", "atendimento_cliente_ptbr", "conciliacao_financeira",
            "dynamics_sales", "dynamics_finance", "dynamics_supply_chain", "dynamics_hr",
            "dynamics_customer_service", "powerbi_compliance",
        ]

        for agent_id in workflow_chain:
            if agent_id in self.agents:
                result = self._run_agent_step(agent_id, current_context)
                if result:
                    results.append(result)
                    current_context[f"last_{agent_id}"] = result
                    self.logger.info("%s executed", agent_id)

        if results and "quality_critic" in self.agents:
            try:
                critic = self.agents["quality_critic"]
                last_result = results[-1]
                review = critic.review_output(workflow_chain[-1] if results else "unknown", last_result)
                results.append(review)
                self.logger.info("quality_critic reviewed: %s", review.get("status"))
            except Exception as e:
                self.logger.warning("quality_critic review failed: %s", e)

        return results

    def run_agent(self, agent_id: str, input_data: dict) -> dict:
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' nao encontrado")

        agent = self.agents[agent_id]

        dispatch = {
            "spec_analyst": lambda: agent.analyze_document(input_data.get("document", "")),
            "procurement": lambda: agent.process_order(input_data.get("materials", [])),
            "inventory": lambda: agent.check_stock(input_data.get("items", [])),
            "logistics": lambda: agent.track_shipment(input_data.get("shipment", {})),
            "field_execution": lambda: agent.generate_field_instructions(input_data.get("specs", "")),
            "bim_coordinator": lambda: agent.generate_bim_element(input_data.get("description", "")),
            "requirements_analyst": lambda: agent.analyze_requirements(input_data.get("requirements", "")),
            "engineering_assistant": lambda: agent.answer_question(input_data.get("question", ""), input_data.get("context", "")),
            "work_synopsis": lambda: agent.generate_synopsis(input_data.get("task_data", "")),
            "photo_intelligence": lambda: agent.analyze_photo(input_data.get("photo_description", "")),
            "rfi_creation": lambda: agent.create_rfi(input_data.get("question", ""), input_data.get("context", "")),
            "compliance": lambda: agent.check_compliance(input_data.get("project_data", "")),
            "nr1_psicossocial": lambda: agent.avaliar_riscos(input_data.get("dados_empresa", "")),
            "tributario_cbs_ibs": lambda: agent.classificar_produto(input_data.get("descricao", "")),
            "lgpd_operacional": lambda: agent.mapear_fluxos_dados(input_data.get("dados_empresa", "")),
            "esg_ifrs": lambda: agent.diagnosticar_maturidade(input_data.get("dados_empresa", "")),
            "inventario_carbono": lambda: agent.calcular_emissoes(input_data.get("dados_consumo", "")),
            "escopo3_fornecedores": lambda: agent.avaliar_fornecedores(input_data.get("dados_cadeia", "")),
            "canal_denuncias": lambda: agent.classificar_denuncia(input_data.get("denuncia", "")),
            "igualdade_salarial": lambda: agent.analisar_equidade(input_data.get("dados_folha", "")),
            "compliance_anticorrupcao": lambda: agent.diagnosticar_maturidade(input_data.get("dados_empresa", "")),
            "regulatory_analyst": lambda: agent.analisar_documento(input_data.get("documento", ""), input_data.get("lang", "pt")),
            "compliance_pm": lambda: agent.gerenciar_projeto(input_data.get("projeto", ""), input_data.get("lang", "pt")),
            "channel_agent": lambda: agent.monitorar_canal(input_data.get("conversas", ""), input_data.get("lang", "pt")),
            "knowledge_agent": lambda: agent.indexar_documento(input_data.get("documento", ""), input_data.get("lang", "pt")),
            "facilitator_agent": lambda: agent.facilitar_reuniao(input_data.get("ata", ""), input_data.get("lang", "pt")),
            "dev_experience": lambda: agent.revisar_pr(input_data.get("pr_data", ""), input_data.get("lang", "pt")),
            "onboarding_funcionarios": lambda: agent.gerar_checklist_admissao(input_data.get("dados_funcionario", ""), input_data.get("lang", "pt")),
            "atendimento_cliente_ptbr": lambda: agent.responder_ticket(input_data.get("mensagem_cliente", ""), input_data.get("contexto", ""), input_data.get("lang", "pt")),
            "conciliacao_financeira": lambda: agent.conciliar_extrato_nf(input_data.get("extrato", ""), input_data.get("notas_fiscais", ""), input_data.get("lang", "pt")),
            "dynamics_sales": lambda: agent.analyze_pipeline(input_data.get("sales_data", ""), input_data.get("lang", "pt")),
            "dynamics_finance": lambda: agent.analyze_cashflow(input_data.get("period", "current_month"), input_data.get("lang", "pt")),
            "dynamics_supply_chain": lambda: agent.analyze_inventory_risk(input_data.get("supply_data", ""), input_data.get("lang", "pt")),
            "dynamics_hr": lambda: agent.analyze_payroll_equity(input_data.get("payroll_data", ""), input_data.get("lang", "pt")),
            "dynamics_customer_service": lambda: agent.classify_ticket(input_data.get("ticket_text", ""), input_data.get("lang", "pt")),
            "powerbi_compliance": lambda: agent.generate_compliance_dashboard(input_data.get("tenant_data", ""), input_data.get("lang", "pt")),
            "master_orchestrator": lambda: agent.create_plan(input_data.get("objective", ""), input_data.get("tenant_context", {})),
            "cross_platform_bridge": lambda: agent.sync_entity(
                input_data.get("entity_type", ""), input_data.get("source", ""),
                input_data.get("target", ""), input_data.get("data", {})),
            "regulatory_watch": lambda: agent.check_updates(),
            "client_intelligence": lambda: agent.analyze_profile(
                input_data.get("tenant_id", "default"), input_data.get("tenant_context", {})),
            "quality_critic": lambda: agent.review_output(
                input_data.get("agent_id", ""), input_data.get("agent_output", {}),
                input_data.get("regulation", "")),
            "meta_learning": lambda: agent.extract_pattern(
                input_data.get("agent_id", ""), input_data.get("execution_data", {})),
            "ecosystem_evolution": lambda: agent.research_market(),
            "federated_knowledge": lambda: agent.aggregate_insights(input_data.get("industry", "")),
        }

        handler = dispatch.get(agent_id)
        if handler:
            return handler()
        return {"error": "Agente nao implementado"}

    def _run_agent_step(self, agent_id: str, context: dict) -> dict | None:
        agent = self.agents[agent_id]
        if agent_id == "spec_analyst":
            doc = context.get("document", "")
            return agent.analyze_document(doc) if doc else None
        elif agent_id == "procurement":
            analysis = context.get("last_spec_analyst", {}).get("analysis", "")
            if analysis and self._needs_procurement(analysis):
                materials = self._extract_materials(analysis)
                return agent.process_order(materials)
        elif agent_id == "inventory":
            order = context.get("last_procurement", {})
            if order:
                items = self._build_stock_items(order)
                return agent.check_stock(items)
        elif agent_id == "logistics":
            stock = context.get("last_inventory", {})
            if stock:
                return agent.track_shipment(
                    {"status": "pending", "product": "materials"}
                )
        elif agent_id == "field_execution":
            doc = context.get("document", "")
            return agent.generate_field_instructions(doc) if doc else None
        elif agent_id == "bim_coordinator":
            doc = context.get("document", "")
            return agent.generate_bim_element(doc[:500]) if doc else None
        elif agent_id == "requirements_analyst":
            analysis = context.get("last_spec_analyst", {}).get("analysis", "")
            return agent.analyze_requirements(analysis) if analysis else None
        elif agent_id == "engineering_assistant":
            doc = context.get("document", "")
            return agent.answer_question("Sumarize este documento", doc) if doc else None
        elif agent_id == "work_synopsis":
            doc = context.get("document", "")
            return agent.generate_synopsis(doc[:500]) if doc else None
        elif agent_id == "photo_intelligence":
            doc = context.get("document", "")
            return agent.analyze_photo(doc[:500]) if doc else None
        elif agent_id == "rfi_creation":
            analysis = context.get("last_spec_analyst", {}).get("analysis", "")
            return agent.create_rfi("Duvida sobre especificacao", analysis) if analysis else None
        elif agent_id == "compliance":
            doc = context.get("document", "")
            return agent.check_compliance(doc) if doc else None
        elif agent_id == "nr1_psicossocial":
            dados = context.get("document", "") or context.get("dados_empresa", "")
            return agent.avaliar_riscos(dados) if dados else None
        elif agent_id == "tributario_cbs_ibs":
            desc = context.get("descricao", "")
            return agent.classificar_produto(desc) if desc else None
        elif agent_id == "lgpd_operacional":
            dados = context.get("document", "") or context.get("dados_empresa", "")
            return agent.mapear_fluxos_dados(dados) if dados else None
        elif agent_id == "esg_ifrs":
            dados = context.get("document", "") or context.get("dados_empresa", "")
            return agent.diagnosticar_maturidade(dados) if dados else None
        elif agent_id == "inventario_carbono":
            dados = context.get("document", "") or context.get("dados_consumo", "")
            return agent.calcular_emissoes(dados) if dados else None
        elif agent_id == "escopo3_fornecedores":
            dados = context.get("document", "") or context.get("dados_cadeia", "")
            return agent.avaliar_fornecedores(dados) if dados else None
        elif agent_id == "canal_denuncias":
            denuncia = context.get("denuncia", "")
            return agent.classificar_denuncia(denuncia) if denuncia else None
        elif agent_id == "igualdade_salarial":
            dados = context.get("document", "") or context.get("dados_folha", "")
            return agent.analisar_equidade(dados) if dados else None
        elif agent_id == "compliance_anticorrupcao":
            dados = context.get("document", "") or context.get("dados_empresa", "")
            return agent.diagnosticar_maturidade(dados) if dados else None
        elif agent_id == "regulatory_analyst":
            doc = context.get("document", "") or context.get("documento", "")
            return agent.analisar_documento(doc) if doc else None
        elif agent_id == "compliance_pm":
            proj = context.get("document", "") or context.get("projeto", "")
            return agent.gerenciar_projeto(proj) if proj else None
        elif agent_id == "channel_agent":
            conv = context.get("document", "") or context.get("conversas", "")
            return agent.monitorar_canal(conv) if conv else None
        elif agent_id == "knowledge_agent":
            doc = context.get("document", "") or context.get("documento", "")
            return agent.indexar_documento(doc) if doc else None
        elif agent_id == "facilitator_agent":
            ata = context.get("document", "") or context.get("ata", "")
            return agent.facilitar_reuniao(ata) if ata else None
        elif agent_id == "dev_experience":
            pr = context.get("document", "") or context.get("pr_data", "")
            return agent.revisar_pr(pr) if pr else None
        elif agent_id == "onboarding_funcionarios":
            dados = context.get("document", "") or context.get("dados_funcionario", "")
            return agent.gerar_checklist_admissao(dados) if dados else None
        elif agent_id == "atendimento_cliente_ptbr":
            msg = context.get("document", "") or context.get("mensagem_cliente", "")
            return agent.responder_ticket(msg) if msg else None
        elif agent_id == "conciliacao_financeira":
            extrato = context.get("document", "") or context.get("extrato", "")
            nfs = context.get("notas_fiscais", "")
            return agent.conciliar_extrato_nf(extrato, nfs) if extrato else None
        elif agent_id == "dynamics_sales":
            sales = context.get("document", "") or context.get("sales_data", "")
            return agent.analyze_pipeline(sales) if sales else None
        elif agent_id == "dynamics_finance":
            period = context.get("period", "current_month")
            return agent.analyze_cashflow(period)
        elif agent_id == "dynamics_supply_chain":
            data = context.get("document", "") or context.get("supply_data", "")
            return agent.analyze_inventory_risk(data) if data else None
        elif agent_id == "dynamics_hr":
            data = context.get("document", "") or context.get("payroll_data", "")
            return agent.analyze_payroll_equity(data) if data else None
        elif agent_id == "dynamics_customer_service":
            data = context.get("document", "") or context.get("ticket_text", "")
            return agent.classify_ticket(data) if data else None
        elif agent_id == "powerbi_compliance":
            data = context.get("document", "") or context.get("tenant_data", "")
            return agent.generate_compliance_dashboard(data) if data else None
        elif agent_id == "master_orchestrator":
            objective = context.get("objective", context.get("document", ""))
            return agent.create_plan(objective, context) if objective else None
        elif agent_id == "cross_platform_bridge":
            return agent.sync_entity(context.get("entity_type", ""), context.get("source", ""), context.get("target", ""), context.get("data", {}))
        elif agent_id == "regulatory_watch":
            return agent.check_updates()
        elif agent_id == "client_intelligence":
            return agent.analyze_profile(context.get("tenant_id", "default"), context)
        elif agent_id == "quality_critic":
            return agent.review_output(context.get("agent_id", ""), context.get("agent_output", {}))
        elif agent_id == "meta_learning":
            return agent.extract_pattern(context.get("agent_id", ""), context.get("execution_data", {}))
        elif agent_id == "ecosystem_evolution":
            return agent.research_market()
        elif agent_id == "federated_knowledge":
            return agent.aggregate_insights(context.get("industry", ""))
        elif agent_id == "software_engineering":
            req = context.get("document", "") or context.get("requisitos", "")
            return agent.analisar_requisitos(req) if req else None
        elif agent_id == "sales_agent":
            segmento = context.get("segmento", "") or context.get("document", "")
            regiao = context.get("regiao", "Brasil")
            return agent.prospectar(segmento, regiao) if segmento else None
        elif agent_id == "workforce_orchestrator":
            tarefa = context.get("document", "") or context.get("tarefa", "")
            return agent.planejar_workflow(tarefa) if tarefa else None
        return None

    def _needs_procurement(self, analysis: str) -> bool:
        keywords = ["material", "compra", "fornecedor", "insumo", "equipamento"]
        return any(k in analysis.lower() for k in keywords)

    def _extract_materials(self, analysis: str) -> list[dict]:
        return [{"name": "Material identificado", "quantity": 1, "unit": "un"}]

    def _build_stock_items(self, order_info: dict) -> list[dict]:
        return [
            {
                "name": "Item do pedido",
                "stock": 10,
                "min_stock": 20,
                "daily_use": 2,
            }
        ]

    def health_check(self) -> dict:
        return {
            "status": "healthy",
            "agents": list(self.agents.keys()),
            "llm_connected": self.llm.health_check(),
        }
