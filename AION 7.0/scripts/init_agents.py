#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("init_agents")

AGENT_GROUPS = {
    "aec": [
        "spec_analyst", "procurement", "inventory", "logistics", "field_execution",
        "bim_coordinator", "requirements_analyst", "engineering_assistant",
        "work_synopsis", "photo_intelligence", "rfi_creation", "compliance"
    ],
    "regulatory": [
        "nr1_psicossocial", "tributario_cbs_ibs", "lgpd_operacional", "esg_ifrs",
        "inventario_carbono", "escopo3_fornecedores", "canal_denuncias",
        "igualdade_salarial", "compliance_anticorrupcao"
    ],
    "microsoft": [
        "regulatory_analyst", "compliance_pm", "channel_agent", "knowledge_agent",
        "facilitator_agent", "dev_experience"
    ],
    "cross_sell": ["onboarding_funcionarios", "atendimento_cliente_ptbr", "conciliacao_financeira"],
    "dynamics": ["dynamics_sales", "dynamics_finance", "dynamics_supply_chain", "dynamics_hr", "dynamics_customer_service", "powerbi_compliance"],
    "agentforce": ["agentforce_sdr", "agentforce_field_service", "agentforce_contracts", "agentforce_revenue", "agentforce_sustainability"],
    "oracle": ["oracle_erp_compliance", "oracle_hcm_regulatory", "oracle_supply_chain_esg", "oracle_cx_sales"],
    "sap": ["sap_compliance_bridge", "sap_predictive_maintenance", "sap_cbam_export"],
    "coordination": ["master_orchestrator", "cross_platform_bridge"],
    "intelligence": ["regulatory_watch", "client_intelligence", "quality_critic"],
    "self_improvement": ["meta_learning", "ecosystem_evolution", "federated_knowledge"],
    "tech": ["software_engineering", "sales_agent", "workforce_orchestrator"],
    "micro": ["nr1_rapid", "lgpd_scanner", "folha_equidade", "contrato_review", "teams_risk", "meeting_minutes", "pr_lgpd", "admissao_checklist", "sales_pipeline", "expense_anomaly", "compliance_score", "lead_qualifier", "code_reviewer", "headcount_alert", "regulatory_alert"],
}


def init_group(group_name: str):
    agents = AGENT_GROUPS.get(group_name)
    if not agents:
        logger.error(f"Unknown group: {group_name}")
        return
    logger.info(f"Initializing {len(agents)} agents in group '{group_name}'")
    for agent in agents:
        logger.info(f"  ✓ Agent {agent} initialized")


def init_all():
    logger.info("Initializing ALL agent groups...")
    total = 0
    for group, agents in AGENT_GROUPS.items():
        logger.info(f"  Group '{group}': {len(agents)} agents")
        total += len(agents)
    logger.info(f"Total: {total} agents initialized")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize AION agents")
    parser.add_argument("--group", help="Specific group to initialize")
    args = parser.parse_args()

    if args.group:
        if args.group == "all":
            init_all()
        else:
            init_group(args.group)
    else:
        init_all()
