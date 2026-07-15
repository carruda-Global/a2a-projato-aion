import pytest
from src.monetization.plans import PLANS, get_plan, get_plan_for_agents


@pytest.mark.unit
class TestPlans:
    def test_plans_have_correct_structure(self):
        assert len(PLANS) == 14
        for plan in PLANS:
            assert "id" in plan
            assert "name" in plan
            assert "price" in plan
            assert "currency" in plan
            assert "agents" in plan
            assert "features" in plan

    def test_compliance_essencial_plan_price(self):
        plan = get_plan("compliance_essencial")
        assert plan is not None
        assert plan["price"] == 59000

    def test_full_suite_56_has_all_agents(self):
        plan = get_plan("full_suite_56")
        assert plan is not None
        assert len(plan["agents"]) >= 56

    def test_get_plan_invalid_returns_none(self):
        plan = get_plan("invalid_plan")
        assert plan is None

    def test_get_plan_for_agents_matches_correctly(self):
        plan = get_plan_for_agents(["nr1_psicossocial", "lgpd_operacional"])
        assert plan is not None
        assert plan["id"] == "compliance_essencial"

    def test_get_plan_for_agents_full_suite_56(self):
        all_agents = [
            "spec_analyst", "procurement", "inventory",
            "logistics", "field_execution",
            "bim_coordinator", "requirements_analyst",
            "engineering_assistant", "work_synopsis",
            "photo_intelligence", "rfi_creation", "compliance",
            "nr1_psicossocial", "tributario_cbs_ibs",
            "lgpd_operacional", "esg_ifrs",
            "inventario_carbono", "escopo3_fornecedores",
            "canal_denuncias", "igualdade_salarial",
            "compliance_anticorrupcao",
            "regulatory_analyst", "compliance_pm",
            "channel_agent", "knowledge_agent",
            "facilitator_agent", "dev_experience",
            "onboarding_funcionarios",
            "atendimento_cliente_ptbr",
            "conciliacao_financeira",
            "dynamics_sales", "dynamics_finance",
            "dynamics_supply_chain", "dynamics_hr",
            "dynamics_customer_service", "powerbi_compliance",
            "agentforce_sdr", "agentforce_field_service",
            "agentforce_contracts", "agentforce_revenue",
            "agentforce_sustainability",
            "oracle_erp_compliance", "oracle_hcm_regulatory",
            "oracle_supply_chain_esg", "oracle_cx_sales",
            "sap_compliance_bridge", "sap_predictive_maintenance",
            "sap_cbam_export",
            "master_orchestrator", "cross_platform_bridge",
            "regulatory_watch", "client_intelligence",
            "quality_critic", "meta_learning",
            "ecosystem_evolution", "federated_knowledge",
        ]
        plan = get_plan_for_agents(all_agents)
        assert plan is not None
        assert plan["id"] == "full_suite_56"

    def test_get_plan_for_agents_microsoft_pack(self):
        microsoft_agents = [
            "regulatory_analyst", "compliance_pm",
            "channel_agent", "knowledge_agent",
            "facilitator_agent", "dev_experience",
        ]
        plan = get_plan_for_agents(microsoft_agents)
        assert plan is not None
        assert plan["id"] == "microsoft_pack"

    def test_erp_full_bridge_has_18_agents(self):
        plan = get_plan("erp_full_bridge")
        assert plan is not None
        assert len(plan["agents"]) == 18
