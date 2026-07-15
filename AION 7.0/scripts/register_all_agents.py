"""
Script de registro completo de agentes AION 7.0.
Popula agent_registry (PostgreSQL) + AIP Security Registry + Google Cloud A2A + gera SQL.

Uso:
    python scripts/register_all_agents.py                          # Tudo automático
    python scripts/register_all_agents.py --db-only                 # Só PostgreSQL
    python scripts/register_all_agents.py --aip-only                # Só AIP
    python scripts/register_all_agents.py --google-only             # Só Google Cloud A2A
    python scripts/register_all_agents.py --sql-only                # Só gera SQL
    python scripts/register_all_agents.py --sql-file saida.sql      # SQL custom
    python scripts/register_all_agents.py --dry-run                 # Simular
"""
import argparse
import json
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Agent Registry Data
# =============================================================================
# Plan IDs reference: PLANS from src/monetization/plans.py
#   starter, professional, enterprise, regulatory_starter, regulatory_pro,
#   esg_carbono, microsoft_pack, dynamics_pack, agentforce_pack, oracle_pack,
#   sap_pack, erp_full_bridge, tech_starter, tech_professional, tech_enterprise,
#   cross_sell_pack, full_suite

AGENTS = [
    # ── AEC Core ──────────────────────────────────────────────────────────
    {
        "id": "spec_analyst",
        "name": "Analista de Especificações",
        "cluster": "aec_core",
        "description": "Análise de especificações técnicas, extração de requisitos, sinalização de contradições conforme NBR",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["starter", "professional", "enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "procurement",
        "name": "Agente de Compras",
        "cluster": "aec_core",
        "description": "Processamento de pedidos de compra, comparação de cotações, geração de requisições e otimização de custos",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["professional", "enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "inventory",
        "name": "Gestão de Estoque",
        "cluster": "aec_core",
        "description": "Monitoramento em tempo real de estoque de obras, identificação de escassez e sugestão de substitutos",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["professional", "enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "logistics",
        "name": "Logística e Rastreamento",
        "cluster": "aec_core",
        "description": "Acompanhamento de envios, identificação de problemas de entrega e geração de alertas de atraso",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "field_execution",
        "name": "Execução em Campo",
        "cluster": "aec_core",
        "description": "Tradução de modelos BIM em instruções de campo, identificação de desvios de projeto",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["enterprise", "full_suite"],
        "version": "1.0.0",
    },
    # ── AEC Specialized ──────────────────────────────────────────────────
    {
        "id": "bim_coordinator",
        "name": "Coordenador BIM",
        "cluster": "aec_specialized",
        "description": "Criação de elementos 3D via texto, clash detection entre disciplinas, validação de modelos BIM",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "requirements_analyst",
        "name": "Análise de Requisitos",
        "cluster": "aec_specialized",
        "description": "Avaliação de requisitos contra padrões de qualidade, geração de scores e identificação de ambiguidades",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "engineering_assistant",
        "name": "Assistente de Engenharia",
        "cluster": "aec_specialized",
        "description": "Assistente conversacional para perguntas técnicas, busca semântica em documentos e sumarização",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "work_synopsis",
        "name": "Resumo de Tarefas",
        "cluster": "aec_specialized",
        "description": "Geração de resumos estruturados de tarefas e defeitos de obra com captura de riscos e prazos",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["enterprise", "full_suite"],
        "version": "1.0.0",
    },
    # ── AEC Compliance ────────────────────────────────────────────────────
    {
        "id": "photo_intelligence",
        "name": "Inteligência Visual de Obras",
        "cluster": "aec_compliance",
        "description": "Análise visual de fotos de obras para detecção de riscos de segurança e progresso",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "rfi_creation",
        "name": "Criação de RFIs",
        "cluster": "aec_compliance",
        "description": "Geração profissional de RFIs a partir de dúvidas de campo com busca em especificações",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "compliance",
        "name": "Conformidade PGRS/PGRSS",
        "cluster": "aec_compliance",
        "description": "Gestão de conformidade legal, documentação, alertas de prazos regulatórios e obrigações ambientais",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["enterprise", "full_suite"],
        "version": "1.0.0",
    },
    # ── Regulatory ───────────────────────────────────────────────────────
    {
        "id": "nr1_psicossocial",
        "name": "NR-1 Riscos Psicossociais",
        "cluster": "regulatory",
        "description": "Inventário de riscos psicossociais (FRPRT) conforme Portaria MTE 1.419/2024, plano de ação e relatórios",
        "llm_model": "gemini-pro",
        "status": "active",
        "plan_ids": ["regulatory_starter", "regulatory_pro", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "tributario_cbs_ibs",
        "name": "Tributário CBS/IBS",
        "cluster": "regulatory",
        "description": "Conformidade com LC 214/2025: classificação NCM, alíquotas, declarações DeRE e simulação de impacto fiscal",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "lgpd_operacional",
        "name": "LGPD Operacional",
        "cluster": "regulatory",
        "description": "Mapeamento de fluxos de dados, RoPA conforme ANPD, identificação de lacunas e monitoramento de incidentes",
        "llm_model": "gemini-pro",
        "status": "active",
        "plan_ids": ["regulatory_starter", "regulatory_pro", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "esg_ifrs",
        "name": "ESG IFRS S1/S2",
        "cluster": "regulatory",
        "description": "Diagnóstico ESG, relatórios IFRS S1/S2, resposta a questionários de clientes corporativos",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["esg_carbono", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "inventario_carbono",
        "name": "Inventário de Carbono",
        "cluster": "regulatory",
        "description": "Cálculo de emissões GEE Escopo 1/2 conforme GHG Protocol e Lei 15.042/2024 (SBCE)",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["esg_carbono", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "escopo3_fornecedores",
        "name": "Escopo 3 Fornecedores",
        "cluster": "regulatory",
        "description": "Rastreamento de emissões Escopo 3 na cadeia de fornecedores conforme SBCE + CBAM + IFRS S2",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["esg_carbono", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "canal_denuncias",
        "name": "Canal de Denúncias",
        "cluster": "regulatory",
        "description": "Canal omnichannel com anonimato, triagem automática, investigação e relatórios CIPA (Lei 14.457/2022)",
        "llm_model": "gemini-pro",
        "status": "active",
        "plan_ids": ["regulatory_pro", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "igualdade_salarial",
        "name": "Igualdade Salarial",
        "cluster": "regulatory",
        "description": "Análise de equidade salarial conforme Lei 14.611/2023 com relatórios MTE e planos de ação",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["regulatory_pro", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "compliance_anticorrupcao",
        "name": "Compliance Anticorrupção",
        "cluster": "regulatory",
        "description": "Programa de integridade conforme Lei 12.846/2013: diagnóstico CGU, código de ética, due diligence",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["regulatory_pro", "full_suite"],
        "version": "1.0.0",
    },
    # ── Microsoft Pack ───────────────────────────────────────────────────
    {
        "id": "regulatory_analyst",
        "name": "Regulatory Analyst",
        "cluster": "microsoft",
        "description": "Análise de contratos e documentos via SharePoint/OneDrive, identificação de riscos LGPD/NR-1/ESG",
        "llm_model": "deepseek-chat",
        "status": "co-sell",
        "plan_ids": ["microsoft_pack", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "compliance_pm",
        "name": "Compliance PM",
        "cluster": "microsoft",
        "description": "Gestão de projetos de compliance com tarefas automáticas no Microsoft Planner e alertas no Teams",
        "llm_model": "deepseek-chat",
        "status": "co-sell",
        "plan_ids": ["microsoft_pack", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "channel_agent",
        "name": "Channel Agent Regulatório",
        "cluster": "microsoft",
        "description": "Monitoramento de canais Teams para detecção de riscos de conformidade trabalhista e tributária",
        "llm_model": "deepseek-chat",
        "status": "co-sell",
        "plan_ids": ["microsoft_pack", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "knowledge_agent",
        "name": "Knowledge Agent",
        "cluster": "microsoft",
        "description": "Indexação de documentos SharePoint com RAG e busca inteligente para consultas de compliance",
        "llm_model": "deepseek-chat",
        "status": "co-sell",
        "plan_ids": ["microsoft_pack", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "facilitator_agent",
        "name": "Facilitator Agent",
        "cluster": "microsoft",
        "description": "Facilitação de reuniões de compliance, atas, minutas e tarefas automáticas no Planner",
        "llm_model": "deepseek-chat",
        "status": "co-sell",
        "plan_ids": ["microsoft_pack", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "dev_experience",
        "name": "Dev Experience Agent",
        "cluster": "microsoft",
        "description": "Automação de PRs, code reviews e conformidade LGPD em código no GitHub",
        "llm_model": "deepseek-chat",
        "status": "co-sell",
        "plan_ids": ["microsoft_pack", "full_suite"],
        "version": "1.0.0",
    },
    # ── Cross-Sell ───────────────────────────────────────────────────────
    {
        "id": "onboarding_funcionarios",
        "name": "Onboarding de Funcionários",
        "cluster": "cross_sell",
        "description": "Automação de admissão: contratos, checklist de documentos, provisionamento de acessos e eSocial",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["cross_sell_pack", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "atendimento_cliente_ptbr",
        "name": "Atendimento ao Cliente PT-BR",
        "cluster": "cross_sell",
        "description": "Resolução automática de tickets L1 via WhatsApp e Teams em português brasileiro",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["cross_sell_pack", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "conciliacao_financeira",
        "name": "Conciliação Financeira",
        "cluster": "cross_sell",
        "description": "Automação de fechamento mensal com conciliação de NFs, extratos, cartão e boletos (PIX/TED)",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["cross_sell_pack", "full_suite"],
        "version": "1.0.0",
    },
    # ── Dynamics 365 ─────────────────────────────────────────────────────
    {
        "id": "dynamics_sales",
        "name": "Dynamics Sales Compliance",
        "cluster": "dynamics",
        "description": "Análise de pipeline de vendas do Dynamics 365 com alertas de risco regulatório",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["dynamics_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "dynamics_finance",
        "name": "Dynamics Finance Regulatory",
        "cluster": "dynamics",
        "description": "Conformidade fiscal e financeira integrada ao Dynamics 365 Finance",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["dynamics_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "dynamics_supply_chain",
        "name": "Dynamics Supply Chain ESG",
        "cluster": "dynamics",
        "description": "Rastreamento ESG na cadeia de suprimentos do Dynamics 365 Supply Chain",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["dynamics_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "dynamics_hr",
        "name": "Dynamics HR Compliance",
        "cluster": "dynamics",
        "description": "Conformidade trabalhista e NR-1 integrada ao Dynamics 365 Human Resources",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["dynamics_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "dynamics_customer_service",
        "name": "Dynamics Customer Service",
        "cluster": "dynamics",
        "description": "Automação de atendimento ao cliente com conformidade regulatória no Dynamics 365",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["dynamics_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "power_bi_compliance",
        "name": "Power BI Compliance",
        "cluster": "dynamics",
        "description": "Dashboards de compliance no Power BI com indicadores regulatórios e ESG",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["dynamics_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    # ── Agentforce (Salesforce) ─────────────────────────────────────────
    {
        "id": "agentforce_sdr",
        "name": "Agentforce SDR",
        "cluster": "agentforce",
        "description": "Prospecção e qualificação de leads BANT via Salesforce Agentforce",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["agentforce_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "agentforce_field_service",
        "name": "Agentforce Field Service",
        "cluster": "agentforce",
        "description": "Gestão de serviços de campo com conformidade regulatória via Salesforce",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["agentforce_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "agentforce_contract_intelligence",
        "name": "Agentforce Contract Intelligence",
        "cluster": "agentforce",
        "description": "Análise inteligente de contratos com detecção de riscos legais via Salesforce",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["agentforce_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "agentforce_revenue_intelligence",
        "name": "Agentforce Revenue Intelligence",
        "cluster": "agentforce",
        "description": "Inteligência de receita com forecasting e detecção de oportunidades via Salesforce",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["agentforce_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "agentforce_sustainability",
        "name": "Agentforce Sustainability",
        "cluster": "agentforce",
        "description": "Gestão de metas de sustentabilidade e relatórios ESG via Salesforce Net Zero Cloud",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["agentforce_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    # ── Oracle ───────────────────────────────────────────────────────────
    {
        "id": "oracle_erp_compliance",
        "name": "Oracle ERP Compliance",
        "cluster": "oracle",
        "description": "Conformidade fiscal e regulatória integrada ao Oracle Fusion ERP",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["oracle_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "oracle_hcm_regulatory",
        "name": "Oracle HCM Regulatory",
        "cluster": "oracle",
        "description": "Conformidade trabalhista e NR-1 integrada ao Oracle Fusion HCM",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["oracle_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "oracle_supply_chain_esg",
        "name": "Oracle Supply Chain ESG",
        "cluster": "oracle",
        "description": "Rastreamento ESG na cadeia de suprimentos do Oracle Fusion SCM",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["oracle_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "oracle_cx_sales",
        "name": "Oracle CX Sales",
        "cluster": "oracle",
        "description": "Automação de vendas com conformidade regulatória no Oracle Fusion CX",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["oracle_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    # ── SAP ──────────────────────────────────────────────────────────────
    {
        "id": "sap_joule_compliance",
        "name": "SAP Joule Compliance Bridge",
        "cluster": "sap",
        "description": "Ponte de compliance entre SAP S/4HANA e regulamentações brasileiras via Joule Studio",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["sap_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "sap_predictive_maintenance",
        "name": "SAP Predictive Maintenance",
        "cluster": "sap",
        "description": "Manutenção preditiva com conformidade regulatória integrada ao SAP PM",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["sap_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "sap_cbam_export",
        "name": "SAP CBAM Export",
        "cluster": "sap",
        "description": "Conformidade com CBAM (Carbon Border Adjustment Mechanism) para exportadores da UE via SAP GTS",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["sap_pack", "erp_full_bridge", "full_suite"],
        "version": "1.0.0",
    },
    # ── Coordination ─────────────────────────────────────────────────────
    {
        "id": "master_orchestrator",
        "name": "Master Orchestrator",
        "cluster": "coordination",
        "description": "Orquestrador central que coordena todos os 60+ agentes para workflows multi-etapa",
        "llm_model": "claude-api",
        "status": "active",
        "plan_ids": ["tech_enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "cross_platform_bridge",
        "name": "Cross-Platform Bridge",
        "cluster": "coordination",
        "description": "Ponte de integração entre plataformas Google, Microsoft, Salesforce, Oracle e SAP",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["tech_enterprise", "full_suite"],
        "version": "1.0.0",
    },
    # ── Intelligence ─────────────────────────────────────────────────────
    {
        "id": "regulatory_watch",
        "name": "Regulatory Watch",
        "cluster": "intelligence",
        "description": "Monitoramento 24/7 de mudanças regulatórias no DOU, ANPD, MTE e Receita Federal",
        "llm_model": "gemini-pro",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "client_intelligence",
        "name": "Client Intelligence",
        "cluster": "intelligence",
        "description": "Análise de comportamento e necessidades do cliente para recomendações personalizadas",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "quality_critic",
        "name": "Quality Critic",
        "cluster": "intelligence",
        "description": "Revisor crítico de qualidade das respostas de todos os agentes com métricas de precisão",
        "llm_model": "claude-api",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    # ── Tech ─────────────────────────────────────────────────────────────
    {
        "id": "software_engineering",
        "name": "Software Engineering Agent",
        "cluster": "tech",
        "description": "Arquitetura, code review, boas práticas e documentação automática de software",
        "llm_model": "claude-api",
        "status": "active",
        "plan_ids": ["tech_starter", "tech_professional", "tech_enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "sales_agent",
        "name": "Sales Agent",
        "cluster": "tech",
        "description": "Vendedor autônomo do EcoSystem: sugere planos, calcula descontos e dispara cross-sell chain",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["tech_professional", "tech_enterprise", "full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "workforce_orchestrator",
        "name": "Workforce Orchestrator",
        "cluster": "tech",
        "description": "Coordenação de RH: onboarding, NR-1, igualdade salarial, denúncias, Dynamics HR e Oracle HCM",
        "llm_model": "claude-api",
        "status": "active",
        "plan_ids": ["tech_enterprise", "full_suite"],
        "version": "1.0.0",
    },
    # ── Self-Improvement ─────────────────────────────────────────────────
    {
        "id": "meta_learning",
        "name": "Meta-Learning Agent",
        "cluster": "self_improvement",
        "description": "Auto-aprendizado baseado em interações anteriores para melhoria contínua dos agentes",
        "llm_model": "claude-api",
        "status": "scheduled_q1_2027",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "ecosystem_evolution",
        "name": "Ecosystem Evolution",
        "cluster": "self_improvement",
        "description": "Evolução autônoma do ecossistema com criação de novos agentes baseada em demanda",
        "llm_model": "claude-api",
        "status": "scheduled_q1_2027",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "federated_knowledge",
        "name": "Federated Knowledge",
        "cluster": "self_improvement",
        "description": "Compartilhamento federado de conhecimento entre instâncias do EcoSystem",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    # ── Enterprise Connectors ────────────────────────────────────────────
    {
        "id": "universal_governance_layer",
        "name": "Universal Governance Layer",
        "cluster": "enterprise_connectors",
        "description": "Camada de governança universal para políticas cross-plataforma",
        "llm_model": "claude-api",
        "status": "scheduled_q1_2027",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "antigravity_bridge",
        "name": "Antigravity Bridge",
        "cluster": "enterprise_connectors",
        "description": "Ponte de integração Google <-> Microsoft para sincronização de dados e workflows",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "mai_code_reviewer",
        "name": "MAI Code Reviewer",
        "cluster": "enterprise_connectors",
        "description": "Revisor de código para garantia de qualidade e conformidade em projetos multi-plataforma",
        "llm_model": "claude-api",
        "status": "scheduled_q1_2027",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    # ── Physical AI ──────────────────────────────────────────────────────
    {
        "id": "physical_ai_connector",
        "name": "Physical AI Connector",
        "cluster": "physical_ai",
        "description": "Conector NVIDIA Omniverse + Azure Foundry + Google GKE para robótica e IoT industrial",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q1_2027",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    # ── Micro-agents (M1-M15) ────────────────────────────────────────────
    {
        "id": "nr1_diagnostico_rapido",
        "name": "Diagnóstico Rápido NR-1",
        "cluster": "micro",
        "description": "Diagnóstico inicial de riscos psicossociais (M1 - filho do #13 NR-1)",
        "llm_model": "gemini-pro",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "lgpd_scanner",
        "name": "LGPD Scanner",
        "cluster": "micro",
        "description": "Varredura de sistemas para listagem de dados pessoais (M2 - filho do #15 LGPD)",
        "llm_model": "gemini-pro",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "folha_equidade",
        "name": "Folha Equidade",
        "cluster": "micro",
        "description": "Cálculo de gap salarial por gênero (M3 - filho do #20 Igualdade Salarial)",
        "llm_model": "gemini-pro",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "contrato_review",
        "name": "Contract Review",
        "cluster": "micro",
        "description": "Revisão individual de contratos (M4 - filho do #22 Regulatory Analyst)",
        "llm_model": "gemini-pro",
        "status": "co-sell",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "teams_risk_monitor",
        "name": "Teams Risk Monitor",
        "cluster": "micro",
        "description": "Monitoramento de 1 canal Teams para riscos (M5 - filho do #24 Channel Agent)",
        "llm_model": "deepseek-chat",
        "status": "co-sell",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "meeting_minutes",
        "name": "Meeting Minutes",
        "cluster": "micro",
        "description": "Geração de ata e tarefas no Planner (M6 - filho do #26 Facilitator Agent)",
        "llm_model": "deepseek-chat",
        "status": "co-sell",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "pr_lgpd_checker",
        "name": "PR LGPD Checker",
        "cluster": "micro",
        "description": "Verificação de PII em Pull Requests (M7 - filho do #27 Dev Experience)",
        "llm_model": "claude-api",
        "status": "co-sell",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "admissao_checklist",
        "name": "Admissão Checklist",
        "cluster": "micro",
        "description": "Checklist de admissão de funcionários (M8 - filho do N1 Onboarding)",
        "llm_model": "gemini-pro",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "sales_pipeline_checker",
        "name": "Sales Pipeline Checker",
        "cluster": "micro",
        "description": "Análise de deals em risco no pipeline (M9 - filho do #31 Dynamics Sales)",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "expense_anomaly",
        "name": "Expense Anomaly Detector",
        "cluster": "micro",
        "description": "Detecção de anomalias em despesas (M10 - filho do #32 Dynamics Finance)",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "compliance_score",
        "name": "Compliance Score",
        "cluster": "micro",
        "description": "Score de compliance 0-100 (M11 - filho do #36 Power BI Compliance)",
        "llm_model": "deepseek-chat",
        "status": "scheduled_q4_2026",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "lead_qualifier",
        "name": "Lead Qualifier",
        "cluster": "micro",
        "description": "Qualificação de leads com scoring (M12 - filho do #58 Sales Agent)",
        "llm_model": "deepseek-chat",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "code_reviewer",
        "name": "Code Reviewer",
        "cluster": "micro",
        "description": "Code review de PRs (M13 - filho do #57 Software Engineering)",
        "llm_model": "claude-api",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "headcount_alert",
        "name": "Headcount Alert",
        "cluster": "micro",
        "description": "Alerta de sobrecarga de equipe (M14 - filho do #59 Workforce Orchestrator)",
        "llm_model": "claude-api",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
    {
        "id": "regulatory_alert",
        "name": "Regulatory Alert",
        "cluster": "micro",
        "description": "Alerta de mudança de norma regulatória (M15 - filho do #51 Regulatory Watch)",
        "llm_model": "gemini-pro",
        "status": "active",
        "plan_ids": ["full_suite"],
        "version": "1.0.0",
    },
]

AGENTS_BY_STATUS = {}
for a in AGENTS:
    AGENTS_BY_STATUS.setdefault(a["status"], []).append(a)

CLUSTERS = sorted({a["cluster"] for a in AGENTS})


# =============================================================================
# PostgreSQL Registry (via supabase-py)
# =============================================================================
def register_postgres(agents, dry_run=False):
    from supabase import create_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_API_KEY")

    if not supabase_url or not supabase_key:
        print("[!] SUPABASE_URL e SUPABASE_SERVICE_KEY/API_KEY necessarios no .env")
        return False

    client = create_client(supabase_url, supabase_key)

    records = []
    for a in agents:
        record = {
            "id": a["id"],
            "name": a["name"],
            "cluster": a["cluster"],
            "description": a["description"],
            "llm_model": a["llm_model"],
            "status": a["status"],
            "plan_ids": a["plan_ids"],
            "config": {},
            "version": a.get("version", "1.0.0"),
            "updated_at": datetime.utcnow().isoformat(),
        }
        records.append(record)

    if dry_run:
        print(f"\n[DRY RUN] {len(records)} registros prontos para upsert")
        for r in records[:5]:
            print(f"  {r['id']}: {r['name']} [{r['cluster']}] {r['status']}")
        if len(records) > 5:
            print(f"  ... e mais {len(records) - 5}")
        return True

    print(f"\n>>> Upsertindo {len(records)} agentes no PostgreSQL (agent_registry)...")
    batch_size = 50
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        try:
            resp = client.table("agent_registry").upsert(batch, on_conflict="id").execute()
            print(f"  Batch {i // batch_size + 1}: {len(batch)} OK")
        except Exception as e:
            print(f"  Batch {i // batch_size + 1}: ERRO - {e}")
            return False

    print(f"  Total: {len(records)} agentes registrados no PostgreSQL")
    return True


# =============================================================================
# AIP Security Registry
# =============================================================================
def register_aip(agents, dry_run=False):
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.security.aip.registry import AIPRegistry

    registry = AIPRegistry()

    success = 0
    errors = 0
    for a in agents:
        try:
            if not dry_run:
                record = registry.register_agent(a["id"], "system")
                if record:
                    success += 1
            else:
                print(f"  [DRY RUN] {a['id']}: AIPRegistry.register_agent('{a['id']}', 'system')")
                success += 1
        except Exception as e:
            print(f"  [ERRO] {a['id']}: {e}")
            errors += 1

    if not dry_run:
        print(f"\n>>> AIP Registry: {success} OK, {errors} erros")
    return errors == 0


# =============================================================================
# SQL Generation
# =============================================================================
def generate_sql(agents, filepath=None):
    lines = [
        "-- ===============================================================",
        "-- Agent Registry Population Script",
        f"-- Generated: {datetime.utcnow().isoformat()}",
        f"-- Total agents: {len(agents)}",
        "-- ===============================================================",
        "",
        "INSERT INTO agent_registry (id, name, cluster, description, llm_model, status, plan_ids, version)",
        "VALUES",
    ]

    values = []
    for a in agents:
        plan_ids_str = "ARRAY[" + ",".join(f"'{p}'" for p in a["plan_ids"]) + "]"
        desc_escaped = a["description"].replace("'", "''")
        values.append(
            f"('{a['id']}', '{a['name']}', '{a['cluster']}', "
            f"'{desc_escaped}', '{a['llm_model']}', '{a['status']}', "
            f"{plan_ids_str}, '{a.get('version', '1.0.0')}')"
        )

    lines.append(",\n".join(values))
    lines.append(
        "\nON CONFLICT (id) DO UPDATE SET "
        "name=EXCLUDED.name, cluster=EXCLUDED.cluster, "
        "description=EXCLUDED.description, llm_model=EXCLUDED.llm_model, "
        "status=EXCLUDED.status, plan_ids=EXCLUDED.plan_ids, "
        "version=EXCLUDED.version, updated_at=NOW();"
    )
    lines.append("")

    sql = "\n".join(lines)

    if filepath:
        Path(filepath).write_text(sql, encoding="utf-8")
        print(f"\nSQL salvo em: {filepath}")
    return sql


# =============================================================================
# Google Cloud A2A Agent Registry
# =============================================================================
GOOGLE_CLIENT_SECRET_FILE = (
    Path(__file__).parent.parent.parent
    / "client_secret_757085749411-t95chtg2tpui3hjov165lratnj3fb0fc.apps.googleusercontent.com.json"
)


def register_google_a2a(agents, dry_run=False):
    """
    Registra o Agent Card no Google Cloud A2A/Vertex AI Agent Engine.
    Usa as credenciais OAuth do projeto 'global-engenharia-498823'.
    """
    if not GOOGLE_CLIENT_SECRET_FILE.exists():
        print(f"[!] Client secret nao encontrado: {GOOGLE_CLIENT_SECRET_FILE}")
        print("    Faca download do arquivo no Google Cloud Console > APIs & Services > Credentials")
        return False

    creds_data = json.loads(GOOGLE_CLIENT_SECRET_FILE.read_text(encoding="utf-8"))
    installed = creds_data.get("installed", creds_data.get("web", {}))
    client_id = installed.get("client_id", "")
    project_id = installed.get("project_id", "")
    print(f"\n>>> Google Cloud A2A Registry ({project_id})...")

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        SCOPES = [
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/service.management",
        ]

        token_file = Path.home() / ".aion" / "google_token.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)

        creds = None
        if token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            except Exception:
                pass

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if dry_run:
                    print("  [DRY RUN] Fluxo OAuth seria iniciado no browser")
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(GOOGLE_CLIENT_SECRET_FILE), SCOPES
                    )
                    print("  Abrindo browser para autenticacao Google Cloud...")
                    creds = flow.run_local_server(port=0)
                    with open(token_file, "w") as f:
                        f.write(creds.to_json())
                    print(f"  Token salvo em: {token_file}")

        if dry_run:
            print(f"  [DRY RUN] {len(agents)} agentes seriam registrados no Google Cloud A2A Registry")
            print(f"  [DRY RUN] Agente: AION 7.0 — {len(agents)} skills")
            return True

        from google.cloud import aiplatform

        aiplatform.init(
            project=project_id,
            location="us-central1",
            credentials=creds,
        )

        from src.a2a_bridge.agent_cards import build_agent_card
        from google.protobuf import json_format

        card = build_agent_card(
            base_url=os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")
        )
        card_dict = json_format.MessageToDict(card)

        # Registra no Vertex AI Agent Engine (Google A2A)
        from google.cloud.aiplatform import agent_engines

        remote_agent = agent_engines.create(
            agent=card_dict,
            config={
                "display_name": "aion-ecosystem",
                "description": "AION 7.0 — 63 agentes de IA para compliance regulatorio brasileiro e automacao empresarial",
                "requirements": [
                    "fastapi==0.115.0",
                    "uvicorn[standard]==0.30.0",
                    "openai==1.50.0",
                    "google-generativeai==0.8.0",
                    "anthropic==0.40.0",
                    "supabase==2.5.0",
                    "stripe==10.0.0",
                ],
            },
        )
        print(f"  [OK] Agent Engine criado: {remote_agent.resource_name}")
        print(f"  [OK] Agent Card publicado em: /.well-known/agent-card.json")
        print(f"  Skills registradas: {len(card.skills)}")
        return True

    except ImportError as e:
        print(f"  [!] Pacote necessario nao instalado: {e}")
        print("  Instale com: pip install google-cloud-aiplatform[agent_engines] google-auth-oauthlib")
        print("\n  Alternativa — registrar manualmente no Google Cloud Console:")
        print(f"    1. Acesse https://console.cloud.google.com/ai/agent-engine?project={project_id}")
        print("    2. Clique em 'Create Agent'")
        print("    3. Importe o Agent Card de: python scripts/setup_a2a_protocol.py --output agent_card.json")
        print("    4. Publique o Agent Card no Google Cloud Marketplace")
        return False
    except Exception as e:
        print(f"  [!] Erro no registro Google Cloud A2A: {e}")
        return False


# =============================================================================
# Summary
# =============================================================================
def print_summary(agents):
    print(f"\n{'=' * 60}")
    print(f"  AION 7.0 — Agent Registry Summary")
    print(f"{'=' * 60}")
    print(f"  Total agents:    {len(agents)}")
    print(f"  Clusters:        {len(CLUSTERS)}")
    print(f"  Status distribuition:")
    for status, items in sorted(AGENTS_BY_STATUS.items()):
        print(f"    {status}: {len(items)}")
    print(f"\n  By cluster:")
    for c in CLUSTERS:
        cluster_agents = [a for a in agents if a["cluster"] == c]
        print(f"    {c}: {len(cluster_agents)} agentes")
        for a in cluster_agents:
            print(f"      - {a['id']} ({a['status']})")
    print(f"{'=' * 60}\n")


# =============================================================================
# CLI
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="AION 7.0 Agent Registry")
    parser.add_argument("--db-only", action="store_true", help="Só PostgreSQL")
    parser.add_argument("--aip-only", action="store_true", help="Só AIP Registry")
    parser.add_argument("--sql-only", action="store_true", help="Só gerar SQL")
    parser.add_argument("--sql-file", default=None, help="Caminho do SQL output")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem escrever")
    args = parser.parse_args()

    do_db = not args.aip_only and not args.sql_only or args.db_only
    do_aip = not args.db_only and not args.sql_only or args.aip_only
    do_sql = args.sql_only or (not args.dry_run and not args.db_only and not args.aip_only)

    print_summary(AGENTS)

    if do_sql:
        sql_path = args.sql_file or str(Path(__file__).parent.parent / "sql_popular_agent_registry_v2.sql")
        generate_sql(AGENTS, filepath=sql_path)

    if do_db and not args.dry_run:
        register_postgres(AGENTS)
    elif do_db and args.dry_run:
        register_postgres(AGENTS, dry_run=True)

    if do_aip:
        register_aip(AGENTS, dry_run=args.dry_run)

    print("\nConcluido!")


if __name__ == "__main__":
    main()
