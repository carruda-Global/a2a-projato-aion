import logging
from typing import Any

from src.monetization.plans import PLANS, get_plan

logger = logging.getLogger(__name__)

import logging
from datetime import datetime, timedelta
from typing import Any

from src.monetization.plans import PLANS, get_plan

logger = logging.getLogger(__name__)

AGENT_CHAIN = [
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

UPGRADE_PATH = {
    "compliance_essencial": "regulatory_pro",
    "regulatory_pro": "full_suite_56",
    "esg_carbon": "full_suite_56",
    "aec_full": "full_suite_56",
    "microsoft_pack": "full_suite_56",
    "dynamics_pack": "erp_full_bridge",
    "agentforce_pack": "erp_full_bridge",
    "oracle_pack": "erp_full_bridge",
    "sap_pack": "erp_full_bridge",
    "erp_full_bridge": "full_suite_56",
}

JOURNEY_TRIGGERS = {
    "onboarding_funcionarios": {
        "next": "nr1_psicossocial",
        "trigger_condition": "employee_count > 0",
        "message": "Novo colaborador admitido requer inventario NR-1 psicossocial (Portaria MTE 1.419/2024)",
        "discount_pct": 15,
        "journey": "A",
    },
    "nr1_psicossocial": {
        "next": "igualdade_salarial",
        "trigger_condition": "payroll_data_available",
        "message": "Relatorio de Igualdade Salarial (Lei 14.611/2023) vence em marco — configure agora",
        "discount_pct": 15,
        "journey": "A",
    },
    "igualdade_salarial": {
        "next": "lgpd_operacional",
        "trigger_condition": "salary_data_collected",
        "message": "Dados salariais geram necessidade de LGPD — dados de RH sao dados pessoais sensiveis, RoPA obrigatorio (Lei 13.709/2018)",
        "discount_pct": 15,
        "journey": "A",
    },
    "lgpd_operacional": {
        "next": "canal_denuncias",
        "trigger_condition": "has_employee_data",
        "message": "Empresa com dados de funcionarios precisa de Canal de Denuncias (Lei 14.457/2022) — obrigatorio para empresas com CIPA",
        "discount_pct": 15,
        "journey": "A",
    },
    "canal_denuncias": {
        "next": "atendimento_cliente_ptbr",
        "trigger_condition": "ticket_volume > 50",
        "message": "Volume de atendimento alto — ative Atendimento ao Cliente PT-BR para resolver tickets L1 automaticamente via WhatsApp + Teams",
        "discount_pct": 15,
        "journey": "A",
    },
    "atendimento_cliente_ptbr": {
        "next": "conciliacao_financeira",
        "trigger_condition": "nf_volume > 100",
        "message": "Alto volume de transacoes — automatize a conciliacao financeira de NFs e extratos bancarios",
        "discount_pct": 15,
        "journey": "A",
    },
    "tributario_cbs_ibs": {
        "next": "compliance_anticorrupcao",
        "trigger_condition": "has_public_contracts or revenue > 500000",
        "message": "Empresa com contratos publicos precisa de programa de integridade (Lei 12.846/2013)",
        "discount_pct": 15,
        "journey": "B",
    },
    "compliance_anticorrupcao": {
        "next": "esg_ifrs",
        "trigger_condition": "in_public_bidding",
        "message": "Empresa em licitacao precisa de ESG para fornecedores — diagnostico ESG IFRS S1/S2 (Res. CVM 193/2023)",
        "discount_pct": 15,
        "journey": "B",
    },
    "esg_ifrs": {
        "next": "inventario_carbono",
        "trigger_condition": "esg_diagnosis_complete",
        "message": "Diagnostico ESG concluido — calcule Escopo 1/2 conforme Lei 15.042/2024 e GHG Protocol",
        "discount_pct": 15,
        "journey": "B",
    },
    "inventario_carbono": {
        "next": "escopo3_fornecedores",
        "trigger_condition": "scope_1_2_complete",
        "message": "Escopo 1/2 calculado — rastreie sua cadeia de fornecedores para CBAM e IFRS S2 (15 categorias GHG)",
        "discount_pct": 15,
        "journey": "B",
    },
    "escopo3_fornecedores": {
        "next": "lgpd_operacional",
        "trigger_condition": "supplier_data_collected",
        "message": "Dados de fornecedores podem conter dados pessoais — mapeamento LGPD obrigatorio",
        "discount_pct": 15,
        "journey": "B",
    },
    "compliance": {
        "next": "nr1_psicossocial",
        "trigger_condition": "has_workers",
        "message": "Obra com funcionarios requer inventario NR-1 psicossocial (Portaria MTE 1.419/2024)",
        "discount_pct": 15,
        "journey": "C",
    },
    "regulatory_analyst": {
        "next": "onboarding_funcionarios",
        "trigger_condition": "team_growing",
        "message": "Equipe crescendo — automatize o onboarding de novos colaboradores no Teams",
        "discount_pct": 15,
        "journey": "C",
    },
    "dev_experience": {
        "next": "atendimento_cliente_ptbr",
        "trigger_condition": "support_volume_high",
        "message": "Alto volume de demandas — ative o Atendimento ao Cliente PT-BR para resolver tickets via WhatsApp",
        "discount_pct": 15,
        "journey": "C",
    },
    "nr1_diagnostico_rapido": {
        "next": "nr1_psicossocial",
        "trigger_condition": "diagnostic_complete",
        "message": "Diagnostico concluido — gere seu plano de acao completo com NR-1 Psicossocial",
        "discount_pct": 15,
        "journey": "micro",
    },
    "lgpd_scanner": {
        "next": "lgpd_operacional",
        "trigger_condition": "scan_complete",
        "message": "Dados mapeados — gere o RoPA completo para a ANPD com LGPD Operacional",
        "discount_pct": 15,
        "journey": "micro",
    },
    "folha_equidade": {
        "next": "igualdade_salarial",
        "trigger_condition": "gap_detected",
        "message": "Gap identificado — gere o relatorio MTE e plano de correcao com Igualdade Salarial",
        "discount_pct": 15,
        "journey": "micro",
    },
    "contrato_review": {
        "next": "regulatory_analyst",
        "trigger_condition": "contract_analyzed",
        "message": "Contrato analisado — ative revisao continua de todos os contratos com Regulatory Analyst",
        "discount_pct": 10,
        "journey": "micro",
    },
    "teams_risk_monitor": {
        "next": "channel_agent",
        "trigger_condition": "risk_detected",
        "message": "Risco detectado em outros canais — expanda o monitoramento com Channel Agent",
        "discount_pct": 15,
        "journey": "micro",
    },
    "meeting_minutes": {
        "next": "facilitator_agent",
        "trigger_condition": "meetings_high_volume",
        "message": "Reunioes de compliance exigem facilitacao especializada — ative Facilitator Agent",
        "discount_pct": 15,
        "journey": "micro",
    },
    "pr_lgpd_checker": {
        "next": "dev_experience",
        "trigger_condition": "pr_volume > 10",
        "message": "Conformidade LGPD no codigo exige revisao continua de arquitetura — ative Dev Experience",
        "discount_pct": 15,
        "journey": "micro",
    },
    "admissao_checklist": {
        "next": "onboarding_funcionarios",
        "trigger_condition": "new_hires > 0",
        "message": "Automatize provisionamento de acesso para novos colaboradores com Onboarding Funcionarios",
        "discount_pct": 15,
        "journey": "micro",
    },
    "sales_pipeline_checker": {
        "next": "dynamics_sales",
        "trigger_condition": "pipeline_deals > 5",
        "message": "Automatize follow-ups e qualificacao de leads com Dynamics Sales Agent",
        "discount_pct": 10,
        "journey": "micro",
    },
    "expense_anomaly": {
        "next": "dynamics_finance",
        "trigger_condition": "anomalies_detected",
        "message": "Automatize conciliacao e fechamento mensal completo com Dynamics Finance Agent",
        "discount_pct": 10,
        "journey": "micro",
    },
    "compliance_score": {
        "next": "powerbi_compliance",
        "trigger_condition": "score_below_80",
        "message": "Mantenha score atualizado em tempo real com alertas automaticos — ative Power BI Compliance",
        "discount_pct": 15,
        "journey": "micro",
    },
    "lead_qualifier": {
        "next": "sales_agent",
        "trigger_condition": "leads_qualified > 0",
        "message": "Automatize proposta, desconto e upsell para leads qualificados com Sales Agent",
        "discount_pct": 15,
        "journey": "micro",
    },
    "code_reviewer": {
        "next": "software_engineering",
        "trigger_condition": "pr_volume > 5",
        "message": "Eleve a qualidade arquitetural e gere documentacao automatica com Software Engineering",
        "discount_pct": 15,
        "journey": "micro",
    },
    "headcount_alert": {
        "next": "workforce_orchestrator",
        "trigger_condition": "overload_detected",
        "message": "Automatize distribuicao de tarefas e gestao de alocacao com Workforce Orchestrator",
        "discount_pct": 10,
        "journey": "micro",
    },
    "regulatory_alert": {
        "next": "regulatory_watch",
        "trigger_condition": "norm_changed",
        "message": "Monitore todas as obrigacoes regulatorias da sua empresa com Regulatory Watch",
        "discount_pct": 15,
        "journey": "micro",
    },
    "dynamics_sales": {
        "next": "dynamics_customer_service",
        "trigger_condition": "sales_pipeline_size > 10",
        "message": "Pipeline de vendas ativo — complemente com Dynamics Customer Service para suporte pos-venda integrado",
        "discount_pct": 15,
        "journey": "D",
    },
}

REGULATORY_DEADLINES = {
    "nr1_psicossocial": {"regulation": "Portaria MTE 1.419/2024", "deadline_days": 180},
    "igualdade_salarial": {"regulation": "Lei 14.611/2023", "deadline_days": 90},
    "lgpd_operacional": {"regulation": "Lei 13.709/2018", "deadline_days": 30},
    "canal_denuncias": {"regulation": "Lei 14.457/2022", "deadline_days": 60},
    "tributario_cbs_ibs": {"regulation": "LC 214/2025", "deadline_days": 120},
    "esg_ifrs": {"regulation": "Res. CVM 193/2023", "deadline_days": 180},
    "inventario_carbono": {"regulation": "Lei 15.042/2024", "deadline_days": 90},
    "escopo3_fornecedores": {"regulation": "CBAM + IFRS S2", "deadline_days": 180},
    "compliance_anticorrupcao": {"regulation": "Lei 12.846/2013", "deadline_days": 120},
}


def eval_condition(condition: str, tenant_context: dict) -> bool:
    try:
        employee_count = tenant_context.get("employee_count", 0)
        payroll_data_available = tenant_context.get("payroll_data_available", False)
        salary_data_collected = tenant_context.get("salary_data_collected", False)
        has_employee_data = tenant_context.get("has_employee_data", False)
        ticket_volume = tenant_context.get("ticket_volume", 0)
        nf_volume = tenant_context.get("nf_volume", 0)
        has_public_contracts = tenant_context.get("has_public_contracts", False)
        revenue = tenant_context.get("revenue", 0)
        in_public_bidding = tenant_context.get("in_public_bidding", False)
        esg_diagnosis_complete = tenant_context.get("esg_diagnosis_complete", False)
        scope_1_2_complete = tenant_context.get("scope_1_2_complete", False)
        supplier_data_collected = tenant_context.get("supplier_data_collected", False)
        has_workers = tenant_context.get("has_workers", False)
        team_growing = tenant_context.get("team_growing", False)
        support_volume_high = tenant_context.get("support_volume_high", False)
        result = eval(condition)
        return bool(result)
    except Exception as e:
        logger.warning("Erro ao avaliar condicao '%s': %s", condition, e)
        return False


def get_regulatory_deadline(agent_id: str) -> dict | None:
    deadline_info = REGULATORY_DEADLINES.get(agent_id)
    if not deadline_info:
        return None
    days_remaining = deadline_info["deadline_days"]
    due_date = datetime.now() + timedelta(days=days_remaining)
    return {
        "regulation": deadline_info["regulation"],
        "deadline_days": days_remaining,
        "due_date": due_date.strftime("%Y-%m-%d"),
        "is_urgent": days_remaining <= 30,
    }


def get_cross_sell_recommendation(current_agent: str, tenant_context: dict) -> dict | None:
    trigger = JOURNEY_TRIGGERS.get(current_agent)
    if not trigger:
        return None
    if not eval_condition(trigger["trigger_condition"], tenant_context):
        return None
    return {
        "recommended_agent": trigger["next"],
        "recommended_agent_name": get_agent_name(trigger["next"]),
        "message": trigger["message"],
        "discount_pct": trigger["discount_pct"],
        "journey": trigger["journey"],
        "urgency": get_regulatory_deadline(trigger["next"]),
    }


def get_journey_progress(tenant_context: dict) -> dict:
    active_agents = tenant_context.get("active_agents", [])
    journeys = {"A": [], "B": [], "C": []}
    for agent_id in active_agents:
        for trigger_id, trigger in JOURNEY_TRIGGERS.items():
            if trigger_id == agent_id:
                j = trigger["journey"]
                journeys[j].append({
                    "current": agent_id,
                    "current_name": get_agent_name(agent_id),
                    "next": trigger["next"],
                    "next_name": get_agent_name(trigger["next"]),
                    "condition": trigger["trigger_condition"],
                    "can_advance": eval_condition(trigger["trigger_condition"], tenant_context),
                })
    return {
        "journeys": [{"id": k, "steps": v, "progress": f"{sum(1 for s in v if s['can_advance'])}/{len(v)}"} for k, v in journeys.items() if v],
        "total_recommendations": sum(1 for v in journeys.values() for s in v if s["can_advance"]),
    }


def get_next_upgrade(current_plan_id: str) -> dict | None:
    next_id = UPGRADE_PATH.get(current_plan_id)
    if next_id:
        return get_plan(next_id)
    return None


def get_upsell_plans(current_plan_id: str) -> list[dict]:
    plans = []
    if current_plan_id in ["compliance_essencial"]:
        pro = get_plan("regulatory_pro")
        if pro:
            plans.append(pro)
    next_up = get_next_upgrade(current_plan_id)
    if next_up:
        plans.append(next_up)
    if not plans:
        full = get_plan("full_suite")
        if full:
            plans.append(full)
    return plans


def get_agents_for_plan(plan_id: str) -> list[str]:
    plan = get_plan(plan_id)
    return plan["agents"] if plan else []


def get_missing_agents(current_agents: list[str], target_plan_id: str) -> list[str]:
    target_agents = get_agents_for_plan(target_plan_id)
    return [a for a in target_agents if a not in current_agents]


def estimate_monthly_savings(current_plan_id: str, target_plan_id: str) -> float:
    current = get_plan(current_plan_id)
    target = get_plan(target_plan_id)
    if not current or not target:
        return 0.0
    current_monthly = current["price"] / 100
    target_monthly = target["price"] / 100
    current_agents = len(current["agents"])
    target_agents = len(target["agents"])
    if current_agents == 0:
        return 0.0
    avg_cost_per_agent = current_monthly / current_agents
    hypothetical_cost = avg_cost_per_agent * target_agents
    savings = hypothetical_cost - target_monthly
    return max(0, savings)


def get_agent_name(agent_id: str) -> str:
    names = {
        "spec_analyst": "Spec Analyst",
        "procurement": "Procurement",
        "inventory": "Inventory",
        "logistics": "Logistics",
        "field_execution": "Field Execution",
        "bim_coordinator": "BIM Coordinator",
        "requirements_analyst": "Requirements Analyst",
        "engineering_assistant": "Engineering Assistant",
        "work_synopsis": "Work Synopsis",
        "photo_intelligence": "Photo Intelligence",
        "rfi_creation": "RFI Creation",
        "compliance": "Compliance Agent",
        "nr1_psicossocial": "NR-1 Psicossocial",
        "tributario_cbs_ibs": "Tributário CBS/IBS",
        "lgpd_operacional": "LGPD Operacional",
        "esg_ifrs": "ESG IFRS S1/S2",
        "inventario_carbono": "Inventário de Carbono",
        "escopo3_fornecedores": "Escopo 3 Fornecedores",
        "canal_denuncias": "Canal de Denúncias",
        "igualdade_salarial": "Igualdade Salarial",
        "compliance_anticorrupcao": "Compliance Anticorrupção",
        "regulatory_analyst": "Regulatory Analyst",
        "compliance_pm": "Compliance PM",
        "channel_agent": "Channel Agent Regulatório",
        "knowledge_agent": "Knowledge Agent",
        "facilitator_agent": "Facilitator Agent",
        "dev_experience": "Dev Experience Agent",
        "onboarding_funcionarios": "Onboarding de Funcionários",
        "atendimento_cliente_ptbr": "Atendimento ao Cliente PT-BR",
        "conciliacao_financeira": "Conciliação Financeira",
        "dynamics_sales": "Dynamics Sales Agent",
        "dynamics_finance": "Dynamics Finance Agent",
        "dynamics_supply_chain": "Dynamics Supply Chain Agent",
        "dynamics_hr": "Dynamics HR Agent",
        "dynamics_customer_service": "Dynamics Customer Service Agent",
        "powerbi_compliance": "Power BI Compliance Dashboard",
        "master_orchestrator": "Master Orchestrator Agent",
        "cross_platform_bridge": "Cross-Platform Bridge Agent",
        "regulatory_watch": "Regulatory Watch Agent",
        "client_intelligence": "Client Intelligence Agent",
        "quality_critic": "Quality Critic Agent",
        "meta_learning": "Meta-Learning Agent",
        "ecosystem_evolution": "Ecosystem Evolution Agent",
        "federated_knowledge": "Federated Knowledge Agent",
    }
    return names.get(agent_id, agent_id)
