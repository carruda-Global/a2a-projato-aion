# EcoSystem 3.0 — Master Document
**Global Match Engenharia de Produção | CREA-SP 5071200171 | Cristiano Arruda**
**Versão:** 3.0.0 | **Data:** 2026-06-24
**LLM para implementação:** DeepSeek-V4-Flash (operacional) + Gemini southamerica-east1 (sensível) + Claude API (raciocínio complexo)
**Portfólio:** 59 agentes em 4 camadas | **ARR projetado ano 5:** R$ 312M

---

## ÍNDICE

1. [Arquitetura Geral](#1-arquitetura-geral)
2. [Correções Críticas de Segurança](#2-correções-críticas-de-segurança)
3. [Infraestrutura e Stack](#3-infraestrutura-e-stack)
4. [Todos os 56 Agentes](#4-todos-os-56-agentes)
5. [MCP Servers](#5-mcp-servers)
6. [Cross-Sell e Jornadas](#6-cross-sell-e-jornadas)
7. [Marketplace e GTM](#7-marketplace-e-gtm)
8. [Estrutura de Preços](#8-estrutura-de-preços)
9. [Roadmap de Implementação](#9-roadmap-de-implementação)
10. [Projeção de Faturamento](#10-projeção-de-faturamento)

---

## 1. ARQUITETURA GERAL

### Visão em camadas

```
┌─────────────────────────────────────────────────────────────────┐
│  CAMADA 4 — AUTO-APRIMORAMENTO (Q1–Q2 2027)                    │
│  #54 Meta-Learning · #55 Ecosystem Evolution · #56 Federated   │
├─────────────────────────────────────────────────────────────────┤
│  CAMADA 3 — INTELIGÊNCIA (Q4 2026)                             │
│  #51 Regulatory Watch · #52 Client Intel · #53 Quality Critic  │
├─────────────────────────────────────────────────────────────────┤
│  CAMADA 2 — COORDENAÇÃO (Imediato)                             │
│  #49 Master Orchestrator · #50 Cross-Platform Bridge           │
├─────────────────────────────────────────────────────────────────┤
│  CAMADA 1 — AGENTES ESPECIALIZADOS (51 agentes)                │
│  AEC #1–#12 | Regulatório #13–#21 | Microsoft #22–#27         │
│  Tech #28–#30 | Novos #N1–#N3 | Dynamics #31–#36              │
│  Agentforce #37–#41 | Oracle #42–#45 | SAP #46–#48             │
├─────────────────────────────────────────────────────────────────┤
│  CAMADA 0 — MCP SERVERS + A2A PROTOCOL                        │
│  ecosystem-regulatory-mcp · ecosystem-esg-mcp · ecosystem-erp-mcp│
│  → Microsoft Copilot Studio · Salesforce Agentforce            │
│  → Google Gemini · Claude (Anthropic)                          │
└─────────────────────────────────────────────────────────────────┘
```

### Stack técnico

| Componente | Tecnologia | Observação |
|-----------|-----------|------------|
| LLM Operacional | DeepSeek-V4-Flash | Agentes AEC, ESG, ERP |
| LLM Sensível | Gemini (southamerica-east1) | NR-1, LGPD, Denúncias, RH |
| LLM Raciocínio | Claude API | Orchestrator, Critic, Evolution |
| API Framework | FastAPI + Uvicorn | |
| Orquestração | LangGraph (stateful) + n8n | Substituir LangChain simples |
| Banco relacional | TimescaleDB (PostgreSQL) | Unificar — remove Postgres separado |
| Banco vetorial | ChromaDB local + Pinecone | ChromaDB dev, Pinecone prod |
| Grafo | Neo4j | Relações entre normas e agentes |
| Cache | Redis Streams | Substituir Kafka — overhead menor |
| Storage | MinIO | Documentos gerados pelos agentes |
| Pagamentos | Stripe + Abacatepay (PIX) | |
| Email | Brevo | |
| Protocolo | Google A2A + MCP (Anthropic) | Dual protocol |
| Hospedagem | Render.com + Google Cloud | Render para API, GCP para dados |
| Monitoramento | Prometheus + Grafana + Loki | ELK substituído por Loki |
| Secrets | HashiCorp Vault | Já no docker-compose — usar de fato |
| Containers | Docker + docker-compose | |

### LLM Routing — regra de segregação LGPD

```yaml
llm_routing:
  default: deepseek
  sensitive_llm: gemini
  reasoning_llm: claude-api
  sensitive_agents:
    - nr1_psicossocial
    - lgpd_operacional
    - canal_denuncias
    - igualdade_salarial
    - compliance_anticorrupcao
    - dynamics_hr
    - oracle_hcm_regulatory
    - onboarding_funcionarios
  reasoning_agents:
    - master_orchestrator
    - quality_critic
    - ecosystem_evolution
```

---

## 2. CORREÇÕES CRÍTICAS DE SEGURANÇA

### Ação imediata — antes de qualquer deploy

| Credencial | Arquivo comprometido | Ação |
|-----------|---------------------|------|
| `sk_live_51Tkp…` (Stripe live) | `.env` | Revogar no dashboard Stripe |
| `whsec_ObbQv…` (webhook secret) | `.env`, `EcoSystem_2_0.env` | Revogar e regenerar |
| `sk-b71dff…` (DeepSeek key) | 3 arquivos | Revogar no painel DeepSeek |
| `ghp_RdncAhD1…` (GitHub PAT) | `chave_api.txt` | Revogar em GitHub Settings |
| `sk-3987e4…` (Swarms key) | `chave_api.txt` | Revogar no painel Swarms |
| `hmas_root_token_2024` (Vault) | `.env`, `docker-compose.yml` | Trocar + configurar Vault |
| `cb5ac0c5-…` (Azure tenant_id) | `config.yaml` | Mover para `${AZURE_TENANT_ID}` |

### Criar `.dockerignore`

```
.env
.env.*
EcoSystem_2_0.env
chave_api.txt
*.key
*.pem
*.log
data/
tests/
.git/
__pycache__/
*.pyc
.pytest_cache/
monitoring/
```

### Dockerfile corrigido

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/lists/* \
    && addgroup --system appgroup && adduser --system --ingroup appgroup appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R appuser:appgroup /app
USER appuser
ENV PYTHONPATH=/app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### config.yaml — correções críticas

```yaml
app:
  version: "3.0.0"  # sincronizar com AGENTS.md

marketplace:
  microsoft:
    tenant_id: ${AZURE_TENANT_ID}      # remover hardcoded
    client_id: ${AZURE_CLIENT_ID}      # remover hardcoded
    client_secret: ${AZURE_CLIENT_SECRET}

monitoring:
  metrics:
    prometheus_port: 9091              # era 8000 — conflito com orchestrator
```

---

## 3. INFRAESTRUTURA E STACK

### docker-compose simplificado (de 14 para 8 serviços)

```
REMOVER:           MANTER:
- postgres         + timescaledb (já inclui postgres)
- kafka            + redis (streams substituem kafka)
- zookeeper        + neo4j
- elasticsearch    + chromadb
- logstash         + minio
- kibana           + prometheus
                   + grafana (com Loki plugin)
                   + vault
```

### Novos serviços MCP a adicionar

```yaml
mcp-regulatory:
  ports: 8010
  command: uvicorn src.mcp.regulatory_server:regulatory_app --port 8010

mcp-esg:
  ports: 8011
  command: uvicorn src.mcp.esg_server:esg_app --port 8011

mcp-erp:
  ports: 8012
  command: uvicorn src.mcp.erp_server:erp_app --port 8012  # Q3 2026
```

### Estrutura de arquivos — adições ao projeto

```
src/
├── mcp/
│   ├── base_server.py
│   ├── regulatory_server.py      # 8 tools
│   ├── esg_server.py             # 4 tools
│   └── erp_server.py             # Q3 2026
├── agents/
│   ├── [existentes #1–#21]
│   ├── onboarding_funcionarios.py    # #N1
│   ├── atendimento_cliente_ptbr.py   # #N2
│   ├── conciliacao_financeira.py     # #N3
│   ├── dynamics_sales.py             # #31
│   ├── dynamics_finance.py           # #32
│   ├── dynamics_supply_chain.py      # #33
│   ├── dynamics_hr.py                # #34
│   ├── dynamics_customer_service.py  # #35
│   ├── powerbi_compliance.py         # #36
│   ├── agentforce_sdr.py             # #37
│   ├── agentforce_field_service.py   # #38
│   ├── agentforce_contracts.py       # #39
│   ├── agentforce_revenue.py         # #40
│   ├── agentforce_sustainability.py  # #41
│   ├── oracle_erp_compliance.py      # #42
│   ├── oracle_hcm_regulatory.py      # #43
│   ├── oracle_supply_chain_esg.py    # #44
│   ├── oracle_cx_sales.py            # #45
│   ├── sap_compliance_bridge.py      # #46
│   ├── sap_predictive_maintenance.py # #47
│   ├── sap_cbam_export.py            # #48
│   ├── master_orchestrator.py        # #49
│   ├── cross_platform_bridge.py      # #50
│   ├── regulatory_watch.py           # #51
│   ├── client_intelligence.py        # #52
│   ├── quality_critic.py             # #53
│   ├── meta_learning.py              # #54
│   ├── ecosystem_evolution.py        # #55
│   └── federated_knowledge.py        # #56
├── api/
│   ├── deepseek_client.py
│   ├── gemini_client.py              # NOVO — LLM sensível
│   ├── claude_client.py              # NOVO — LLM raciocínio
│   ├── dynamics_client.py            # NOVO
│   ├── oracle_client.py              # NOVO
│   └── sap_client.py                 # NOVO
└── bridge/
    └── cross_platform.py             # NOVO — sincronização entre plataformas
```

---

## 4. TODOS OS 56 AGENTES

### GRUPO 1 — Núcleo AEC (#1–#5)
**Canal:** Google Cloud exclusivo | **Cluster:** aec_core

| # | ID | Nome | Descrição | Preço | LLM |
|---|----|----|-----------|-------|-----|
| 1 | `spec_analyst` | Spec Analyst | Análise de especificações técnicas, extrai requisitos, sinaliza contradições | R$ 997/mês | DeepSeek |
| 2 | `procurement` | Procurement | Compras automáticas, cotações, requisições | R$ 597/mês | DeepSeek |
| 3 | `inventory` | Inventory | Estoque real, escassez, substitutos | R$ 797/mês | DeepSeek |
| 4 | `logistics` | Logistics | Logística, rastreamento, NFs | R$ 797/mês | DeepSeek |
| 5 | `field_execution` | Field Execution | BIM em RA, guia trabalhadores | R$ 1.497/mês | DeepSeek |

### GRUPO 2 — Especializados (#6–#9)
**Canal:** Google Cloud | **Cluster:** aec_specialized

| # | ID | Nome | Descrição | Preço | LLM |
|---|----|----|-----------|-------|-----|
| 6 | `bim_coordinator` | BIM Coordinator | Elementos 3D, clash detection | R$ 897/mês | DeepSeek |
| 7 | `requirements_analyst` | Requirements Analyst | Qualidade de requisitos | R$ 697/mês | DeepSeek |
| 8 | `engineering_assistant` | Engineering Assistant | Busca semântica, sumarização | R$ 497/mês | DeepSeek |
| 9 | `work_synopsis` | Work Synopsis | Resumo de tarefas e defeitos | R$ 597/mês | DeepSeek |

### GRUPO 3 — Conformidade AEC (#10–#12)
**Canal:** Google Cloud | **Cluster:** aec_compliance

| # | ID | Nome | Descrição | Preço | LLM |
|---|----|----|-----------|-------|-----|
| 10 | `photo_intelligence` | Photo Intelligence | Análise visual de obras, EPI | R$ 797/mês | DeepSeek |
| 11 | `rfi_creation` | RFI Creation | RFIs automáticos | R$ 697/mês | DeepSeek |
| 12 | `compliance` | Compliance Agent | PGRS/PGRSS, alertas legais | R$ 897/mês | DeepSeek |

### GRUPO 4 — Regulatórios (#13–#21)
**Canal:** Google + Salesforce + Microsoft | **Cluster:** regulatory
**LLM:** Gemini southamerica-east1 (dados pessoais sensíveis)

| # | ID | Nome | Norma | Preço | Status |
|---|----|----|-------|-------|--------|
| 13 | `nr1_psicossocial` | NR-1 Psicossocial | Portaria MTE 1.419/2024 | R$ 390–1.390/mês | ✅ Q3 2026 |
| 14 | `tributario_cbs_ibs` | Tributário CBS/IBS | LC 214/2025 | R$ 390–3.900/mês | Q4 2026 |
| 15 | `lgpd_operacional` | LGPD Operacional | Lei 13.709/2018 | R$ 290–990/mês | ✅ Q3 2026 |
| 16 | `esg_ifrs` | ESG IFRS S1/S2 | Res. CVM 193/2023 | R$ 490–2.490/mês | Q1 2027 |
| 17 | `inventario_carbono` | Inventário Carbono | Lei 15.042/2024 | R$ 890–4.900/mês | Q1 2027 |
| 18 | `escopo3_fornecedores` | Escopo 3 Fornecedores | SBCE + CBAM + IFRS S2 | R$ 690–3.490/mês | Q1 2027 |
| 19 | `canal_denuncias` | Canal de Denúncias | Lei 14.457/2022 | R$ 290–990/mês | ✅ Q3 2026 |
| 20 | `igualdade_salarial` | Igualdade Salarial | Lei 14.611/2023 | R$ 490–1.490/mês | ✅ Q3 2026 |
| 21 | `compliance_anticorrupcao` | Compliance Anticorrupção | Lei 12.846/2013 | R$ 390–1.490/mês | Q4 2026 |

### GRUPO 5 — Microsoft 365 (#22–#27)
**Canal:** Microsoft Marketplace (co-sell MSPs) | **Cluster:** microsoft

| # | ID | Nome | Descrição | Preço | LLM |
|---|----|----|-----------|-------|-----|
| 22 | `regulatory_analyst` | Regulatory Analyst | Contratos SharePoint/OneDrive | R$ 997/mês | Gemini |
| 23 | `compliance_pm` | Compliance PM | PGRS, Carbono, Igualdade no Planner | R$ 797/mês | DeepSeek |
| 24 | `channel_agent` | Channel Agent | Monitoramento Teams | R$ 597/mês | DeepSeek |
| 25 | `knowledge_agent` | Knowledge Agent | RAG em SharePoint | R$ 697/mês | DeepSeek |
| 26 | `facilitator_agent` | Facilitator Agent | Reuniões, atas, minutas | R$ 497/mês | DeepSeek |
| 27 | `dev_experience` | Dev Experience | PRs, LGPD em código | R$ 897/mês | DeepSeek |

### GRUPO 6 — Novos Agentes (#N1–#N3)
**Canal:** Microsoft + Salesforce + Google | **Cluster:** new_agents

| # | ID | Nome | Descrição | Preço BR | Preço Global | LLM |
|---|----|----|-----------|----------|-------------|-----|
| N1 | `onboarding_funcionarios` | Onboarding Funcionários | Admissão, contratos, provisionamento M365 | R$ 490/mês | USD 99/mês | Gemini |
| N2 | `atendimento_cliente_ptbr` | Atendimento Cliente PT-BR | Tickets L1/L2, WhatsApp, SLA | R$ 390/mês | USD 99/mês | Gemini |
| N3 | `conciliacao_financeira` | Conciliação Financeira | Extratos, NFs, ERP, anomalias | R$ 790/mês | USD 199/mês | DeepSeek |

### GRUPO 7 — Microsoft Dynamics 365 (#31–#36)
**Canal:** Microsoft Marketplace + Google Cloud | **Cluster:** dynamics
**Extensão de:** Agentes existentes + conectores Dynamics 365

| # | ID | Nome | Integração | Preço BR | Preço Global | LLM |
|---|----|----|------------|----------|-------------|-----|
| 31 | `dynamics_sales` | Dynamics Sales Agent | Dynamics 365 Sales + Teams + Outlook | R$ 790/mês | USD 199/mês | DeepSeek |
| 32 | `dynamics_finance` | Dynamics Finance Agent | Dynamics 365 Finance + Power BI | R$ 990/mês | USD 249/mês | DeepSeek |
| 33 | `dynamics_supply_chain` | Dynamics Supply Chain | Dynamics 365 SCM + Power Automate | R$ 890/mês | USD 229/mês | DeepSeek |
| 34 | `dynamics_hr` | Dynamics HR Agent | Dynamics 365 HR + Teams | R$ 790/mês | USD 199/mês | Gemini |
| 35 | `dynamics_customer_service` | Dynamics CS Agent | Dynamics 365 CS + WhatsApp | R$ 590/mês | USD 149/mês | Gemini |
| 36 | `powerbi_compliance` | Power BI Compliance Dashboard | Power BI + SharePoint | R$ 490/mês | USD 129/mês | DeepSeek |

### GRUPO 8 — Salesforce Agentforce (#37–#41)
**Canal:** Salesforce AgentExchange + Microsoft | **Cluster:** agentforce

| # | ID | Nome | Integração | Preço BR | Preço Global | LLM |
|---|----|----|------------|----------|-------------|-----|
| 37 | `agentforce_sdr` | Agentforce SDR Agent | Sales Cloud + Einstein + Email | R$ 690/mês | USD 179/mês | DeepSeek |
| 38 | `agentforce_field_service` | Agentforce Field Service | Field Service + Maps + WhatsApp | R$ 890/mês | USD 229/mês | DeepSeek |
| 39 | `agentforce_contracts` | Agentforce Contract Intelligence | CRM + DocuSign + SharePoint | R$ 990/mês | USD 249/mês | Gemini |
| 40 | `agentforce_revenue` | Agentforce Revenue Intelligence | Revenue Cloud + Tableau | R$ 1.190/mês | USD 299/mês | DeepSeek |
| 41 | `agentforce_sustainability` | Agentforce Sustainability | Net Zero Cloud + SAP | R$ 890/mês | USD 229/mês | DeepSeek |

### GRUPO 9 — Oracle Fusion (#42–#45)
**Canal:** Oracle Agent Marketplace + Google Cloud | **Cluster:** oracle

| # | ID | Nome | Integração | Preço BR | Preço Global | LLM |
|---|----|----|------------|----------|-------------|-----|
| 42 | `oracle_erp_compliance` | Oracle ERP Compliance | Oracle Fusion ERP + Agent Studio | R$ 1.190/mês | USD 299/mês | DeepSeek |
| 43 | `oracle_hcm_regulatory` | Oracle HCM Regulatory | Oracle Fusion HCM + Analytics | R$ 990/mês | USD 249/mês | Gemini |
| 44 | `oracle_supply_chain_esg` | Oracle Supply Chain ESG | Oracle SCM + CBAM API UE | R$ 1.490/mês | USD 379/mês | DeepSeek |
| 45 | `oracle_cx_sales` | Oracle CX Sales Intelligence | Oracle Fusion CX + Analytics | R$ 890/mês | USD 229/mês | DeepSeek |

### GRUPO 10 — SAP (#46–#48)
**Canal:** SAP Store (BTP) + Oracle Cloud | **Cluster:** sap

| # | ID | Nome | Integração | Preço BR | Preço Global | LLM |
|---|----|----|------------|----------|-------------|-----|
| 46 | `sap_compliance_bridge` | SAP Joule Compliance Bridge | S/4HANA + Joule Studio + GRC | R$ 1.490/mês | USD 379/mês | DeepSeek |
| 47 | `sap_predictive_maintenance` | SAP Predictive Maintenance | SAP PM + IoT + Teams | R$ 1.290/mês | USD 329/mês | DeepSeek |
| 48 | `sap_cbam_export` | SAP CBAM Export Compliance | SAP GTS + CBAM API UE + Oracle SCM | R$ 1.990/mês | USD 499/mês | DeepSeek |

### GRUPO 11 — Coordenação (#49–#50)
**Camada:** 2 — Coordenação | **Implementação:** Imediata

| # | ID | Nome | Função | Preço | LLM |
|---|----|----|--------|-------|-----|
| 49 | `master_orchestrator` | Master Orchestrator Agent | Recebe objetivo → decompõe → delega para agentes → agrega resultado | Incluído Pro+ | Claude API |
| 50 | `cross_platform_bridge` | Cross-Platform Bridge Agent | Sincroniza dados entre Microsoft, Salesforce, Oracle, SAP sem duplicação | R$ 990/mês standalone | DeepSeek |

**Implementação #49 — Master Orchestrator:**
```python
# src/agents/master_orchestrator.py
# Estende orchestrator.py com LangGraph stateful
# Input: objetivo em linguagem natural
# Output: plano de agentes sequenciados com prioridade e prazo
# LLM: Claude API (raciocínio complexo de planejamento)

ORCHESTRATOR_SYSTEM_PROMPT = """
Você é o orquestrador central do EcoSystem 3.0.
Dado um objetivo do cliente, você:
1. Identifica quais obrigações legais estão ativas
2. Ordena os agentes por urgência (multa, prazo, risco)
3. Cria um plano de 30/60/90 dias
4. Delega para os agentes especializados via A2A
5. Monitora resultados e ajusta o plano
Sempre priorize obrigações com multa ativa antes de otimizações.
"""
```

### GRUPO 12 — Inteligência (#51–#53)
**Camada:** 3 — Inteligência | **Implementação:** Q4 2026

| # | ID | Nome | Função | Preço | LLM |
|---|----|----|--------|-------|-----|
| 51 | `regulatory_watch` | Regulatory Watch Agent | Monitora DOU/ANPD/MTE 24/7, atualiza bases dos agentes automaticamente | R$ 790/mês | Gemini |
| 52 | `client_intelligence` | Client Intelligence Agent | Aprende perfil do cliente, recomenda proativamente antes do prazo | Incluído Pro+ | DeepSeek |
| 53 | `quality_critic` | Quality Critic Agent | Revisa outputs de todos os agentes antes de entregar — valida contra norma vigente | Incluído em todos | Claude API |

**Implementação #51 — Regulatory Watch:**
```python
# src/agents/regulatory_watch.py
# Fontes monitoradas:
REGULATORY_SOURCES = [
    "https://www.in.gov.br/servicos/pesquisa-dou",  # Diário Oficial
    "https://www.gov.br/anpd/pt-br",                 # ANPD
    "https://www.gov.br/trabalho-e-emprego",          # MTE
    "https://www.gov.br/receita/pt-br",               # Receita Federal
    "https://www.cvm.gov.br",                          # CVM
]
# A cada 6h: busca mudanças → valida relevância → 
# atualiza RAG dos agentes afetados → notifica tenants impactados
```

**Implementação #53 — Quality Critic:**
```python
# src/agents/quality_critic.py
# Estende governance/critic_agent.py já existente
# Adiciona: validação jurídica por norma específica
# Padrão: Agent-as-a-Judge com feedback intermediário
# Roda ANTES de qualquer entrega ao cliente
CRITIC_CHECKS = [
    "norma_vigente",        # output cita a versão correta da lei?
    "completude",           # todos os campos obrigatórios presentes?
    "consistencia_interna", # dados internamente consistentes?
    "pii_masking",          # nenhum dado pessoal exposto no output?
    "alucinacao_detector",  # referências verificáveis?
]
```

### GRUPO 13 — Auto-aprimoramento (#54–#56)
**Camada:** 4 — Auto-aprimoramento | **Implementação:** Q1–Q2 2027

| # | ID | Nome | Função | Preço | LLM |
|---|----|----|--------|-------|-----|
| 54 | `meta_learning` | Meta-Learning Agent | Analisa padrões de uso, cria templates, reduz tokens/tarefa em 30–40% | Interno | DeepSeek |
| 55 | `ecosystem_evolution` | Ecosystem Evolution Agent | Pesquisa mercado semanalmente, propõe novos agentes e melhorias | Interno | Claude API |
| 56 | `federated_knowledge` | Federated Knowledge Agent | Aprende com dados anonimizados de todos os clientes por setor | Interno | DeepSeek |

**Implementação #54 — Meta-Learning:**
```python
# src/agents/meta_learning.py
# Estende evolution/gea já implementado no config.yaml
# Adiciona: skill acquisition — prompts otimizados salvos como templates
# Analogia: "Lessons Learned" que sobrevivem entre sessões
# Ativa config.yaml: evolution.reflection + performance_selection
```

**Implementação #56 — Federated Knowledge:**
```python
# src/agents/federated_knowledge.py
# Ativa config.yaml: rl.federated (hoje disabled=true)
# Dados anonimizados por setor → padrões de risco por indústria
# LGPD: federated learning — nunca compartilha dados individuais
# Resultado: agentes mais precisos para setores com mais clientes
```

---

## 5. MCP SERVERS

### Arquitetura MCP

```
1 MCP server publicado → aparece em 4 plataformas simultaneamente
Copilot Studio + Agentforce + Claude + Gemini
Sem certificação separada. Sem comissão de marketplace.
```

### 3 servers a implementar

#### ecosystem-regulatory-mcp (porta 8010)
**Tools:** `nr1_psicossocial`, `lgpd_operacional`, `tributario_cbs_ibs`,
`canal_denuncias`, `igualdade_salarial`, `compliance_anticorrupcao`,
`onboarding_funcionarios`, `conciliacao_financeira`

#### ecosystem-esg-mcp (porta 8011)
**Tools:** `esg_ifrs_diagnostico`, `inventario_carbono`,
`escopo3_fornecedores`, `cbam_certificate`

#### ecosystem-erp-mcp (porta 8012 — Q3 2026)
**Tools:** `dynamics_sales`, `dynamics_finance`, `dynamics_hr`,
`agentforce_sdr`, `oracle_erp_compliance`, `sap_cbam_export`

### URLs de produção

```
Regulatory: https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse
ESG:        https://engenheiro-producao-ai.onrender.com/mcp/esg/sse
ERP:        https://engenheiro-producao-ai.onrender.com/mcp/erp/sse
Registry:   https://engenheiro-producao-ai.onrender.com/mcp/servers
```

### Como conectar por plataforma

**Microsoft Copilot Studio:**
```
Settings → Actions → Add MCP Server
URL: .../mcp/regulatory/sse
Auth: X-API-Key header
```

**Salesforce Agentforce:**
```
Setup → Agentforce → MCP Servers → New
URL: .../mcp/esg/sse
Auth: Custom Header → X-API-Key
```

**Claude Desktop:**
```json
{
  "mcpServers": {
    "ecosystem-regulatory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sse"],
      "env": {
        "MCP_SERVER_URL": ".../mcp/regulatory/sse",
        "X-API-Key": "CHAVE_DO_CLIENTE"
      }
    }
  }
}
```

### Billing MCP

```yaml
mcp:
  billing:
    model: per_tool_call
    fallback_to_subscription: true
    free_calls_trial: 10
  auth:
    type: api_key
    header: X-API-Key
    tenant_header: X-Tenant-ID
```

### Tabelas Supabase para MCP

```sql
CREATE TABLE mcp_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    api_key TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE mcp_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    platform TEXT,
    called_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE mcp_cross_sell (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    triggered_by TEXT NOT NULL,
    recommended_agent TEXT NOT NULL,
    discount_pct INTEGER,
    converted_at TIMESTAMPTZ
);
```

---

## 6. CROSS-SELL E JORNADAS

### Triggers automáticos — src/cross_selling.py

```python
JOURNEY_TRIGGERS = {
    "onboarding_funcionarios":    {"next": "nr1_psicossocial",       "trigger": "employee_count > 0"},
    "nr1_psicossocial":           {"next": "igualdade_salarial",     "trigger": "payroll_data_available"},
    "igualdade_salarial":         {"next": "lgpd_operacional",       "trigger": "salary_data_processed"},
    "lgpd_operacional":           {"next": "canal_denuncias",        "trigger": "data_mapping_complete"},
    "canal_denuncias":            {"next": "atendimento_cliente_ptbr","trigger": "ticket_volume > 50"},
    "atendimento_cliente_ptbr":   {"next": "conciliacao_financeira", "trigger": "transaction_volume > 100"},
    "tributario_cbs_ibs":         {"next": "compliance_anticorrupcao","trigger": "has_public_contracts"},
    "compliance_anticorrupcao":   {"next": "esg_ifrs",              "trigger": "public_bids_detected"},
    "esg_ifrs":                   {"next": "inventario_carbono",     "trigger": "esg_diagnosis_complete"},
    "inventario_carbono":         {"next": "escopo3_fornecedores",   "trigger": "scope_1_2_complete"},
    "escopo3_fornecedores":       {"next": "lgpd_operacional",       "trigger": "supplier_data_mapped"},
    "conciliacao_financeira":     {"next": "tributario_cbs_ibs",    "trigger": "nf_volume > 100"},
    "dynamics_hr":                {"next": "nr1_psicossocial",       "trigger": "new_employee_onboarded"},
    "agentforce_sustainability":  {"next": "inventario_carbono",     "trigger": "esg_data_collected"},
    "sap_cbam_export":            {"next": "escopo3_fornecedores",   "trigger": "cbam_calculated"},
}
```

### Jornada A — RH + Financeiro (Microsoft + Salesforce)

```
Onboarding #N1 R$490 → NR-1 #13 +R$390 → Igualdade #20 +R$490
→ LGPD #15 +R$290 → Denúncias #19 +R$290 → Atendimento #N2 +R$390
→ Conciliação #N3 +R$790
LTV: R$ 3.130/mês | Multiplicador: 6,4x
```

### Jornada B — Fiscal + ESG (Google + Oracle)

```
CBS/IBS #14 R$390 → Anticorrupção #21 +R$390 → ESG #16 +R$490
→ Carbono #17 +R$890 → Escopo3 #18 +R$690 → LGPD #15 +R$290
→ Conciliação #N3 +R$790 → Atendimento #N2 +R$390
LTV: R$ 4.320/mês | Multiplicador: 11x
```

### Jornada C — AEC + Microsoft (Google → Microsoft)

```
PGRS #12 R$897 → NR-1 #13 +R$390 → Denúncias #19 +R$290
→ MS Pack #22+#25 +R$1.694 → Onboarding #N1 +R$490
→ Atendimento #N2 +R$390 → Conciliação #N3 +R$790
LTV: R$ 4.941/mês | Multiplicador: 5,5x + co-sell Microsoft
```

---

## 7. MARKETPLACE E GTM

### Canal por grupo de agentes

| Grupo | Canal primário | Canal secundário | Abordagem |
|-------|---------------|-----------------|-----------|
| AEC #1–#12 | Google Cloud | — | Self-serve |
| Regulatórios #13–#21 | Google Cloud | Microsoft + Salesforce | Self-serve |
| Microsoft #22–#27 | Microsoft Marketplace | — | Co-sell MSPs |
| Novos #N1–#N3 | Microsoft + Salesforce | Google Cloud | Self-serve |
| Dynamics #31–#36 | Microsoft Marketplace | Google Cloud | Self-serve + co-sell |
| Agentforce #37–#41 | Salesforce AgentExchange | Microsoft | Self-serve |
| Oracle #42–#45 | Oracle Agent Marketplace | Google Cloud | Co-sell |
| SAP #46–#48 | SAP Store (BTP) | Oracle Cloud | Co-sell |
| MCP Servers | Todos (via protocolo) | — | Auto-discovery |

### Fases de publicação

**Q3 2026 — Publicar agora:**
- Google Cloud: todos os regulatórios (#13–#21 fases 1 e 2)
- Microsoft: Compliance Essencial como produto de entrada
- Salesforce: Compliance Essencial + Atendimento PT-BR
- MCP Servers: regulatory + esg publicados

**Q4 2026:**
- Oracle Agent Marketplace: #42–#44
- SAP Store: #46–#48
- MCP Server ERP publicado
- Microsoft: Dynamics Pack (#31–#36)

**Q1 2027:**
- ESG global cluster: #16–#18 + #41 + #44 + #48
- Salesforce: Agentforce Pack completo
- Todos os MCP servers em produção

### Copy do listing principal (todos os canais)

**Título:** Compliance Essencial — NR-1 Psicossocial + LGPD | Agente de IA para PMEs

**Tagline:** Atenda 2 obrigações legais com multa ativa em 2026 — sem contratar consultoria

**Gancho regulatório:**
- Portaria MTE 1.419/2024 → risco de interdição + autuação
- Lei 13.709/2018 → multa até R$ 50M por infração ANPD

**Preço de entrada:** R$ 590/mês | Trial 15 dias grátis

---

## 8. ESTRUTURA DE PREÇOS

### Planos visíveis nos listings (6 planos)

| Plano | Agentes | Preço BR | Preço Global | Price ID Stripe |
|-------|---------|----------|-------------|----------------|
| Compliance Essencial | #13 + #15 | R$ 590/mês | USD 149/mês | price_1TlxVVQn4rfjkSvEpiBqaCSf |
| Regulatory Pro | #13+#15+#19+#20+#21 | R$ 1.490/mês | USD 379/mês | price_1TlxVVQn4rfjkSvEam443ZCP |
| ESG + Carbono | #16+#17+#18 | R$ 2.490/mês | USD 629/mês | price_1TlxVXQn4rfjkSvEl6uCfYgk |
| Microsoft Pack | #22–#27 | R$ 4.482/mês | USD 1.129/mês | price_1TlxVXQn4rfjkSvExSnW6XmL |
| Microsoft Dynamics Pack | #31–#36 | R$ 3.990/mês | USD 999/mês | CRIAR NO STRIPE |
| Salesforce Agentforce Pack | #37–#41 | R$ 3.690/mês | USD 929/mês | CRIAR NO STRIPE |
| Oracle Fusion Pack | #42–#45 | R$ 3.990/mês | USD 999/mês | CRIAR NO STRIPE |
| SAP Integration Pack | #46–#48 | R$ 4.290/mês | USD 1.079/mês | CRIAR NO STRIPE |
| ERP Full Bridge | #31–#48 | R$ 12.990/mês | USD 3.299/mês | CRIAR NO STRIPE |
| Full Suite | Todos 56 | R$ 19.997/mês | USD 4.999/mês | Atualizar price_1TlxVTQn4rfjkSvEn41gegAl |

### Planos a ocultar dos listings (manter no Stripe)
`starter`, `professional`, `enterprise`, `compliance_pack`, `regulatory_full`

### Agentes individualmente (sem plano)
Cada agente tem seu próprio buy link Stripe — manter conforme AGENTS.md atual
para clientes que querem agente único.

---

## 9. ROADMAP DE IMPLEMENTAÇÃO

### SEMANA 1 — Segurança (bloqueante)
- [ ] Revogar todas as credenciais expostas (Stripe, Supabase, DeepSeek, GitHub, Swarms, Vault)
- [ ] Criar `.dockerignore`
- [ ] Corrigir Dockerfile (não-root + healthcheck)
- [ ] Mover Azure IDs do config.yaml para env vars
- [ ] Corrigir prometheus_port de 8000 para 9091
- [ ] Separar Stripe secrets por ambiente (test vs production)
- [ ] Corrigir path hardcoded em test_jwt.py

### SEMANA 2 — MCP Servers (receita imediata)
- [ ] `pip install mcp sse-starlette`
- [ ] Criar `src/mcp/base_server.py`
- [ ] Criar `src/mcp/regulatory_server.py` (8 tools)
- [ ] Criar `src/mcp/esg_server.py` (4 tools)
- [ ] Adicionar serviços mcp-regulatory e mcp-esg no docker-compose
- [ ] Deploy no Render
- [ ] Testar no Claude Desktop
- [ ] Publicar URLs no MCP Registry

### SEMANA 3 — Novos agentes (#N1, #N2, #N3)
- [ ] `src/agents/onboarding_funcionarios.py`
- [ ] `src/agents/atendimento_cliente_ptbr.py`
- [ ] `src/agents/conciliacao_financeira.py`
- [ ] Solicitar acesso WhatsApp Business API (Meta) para #N2
- [ ] Adicionar 3 agentes ao `src/agents/__init__.py`
- [ ] Adicionar ao MCP regulatory server
- [ ] Adicionar triggers no `src/cross_selling.py`

### SEMANA 4 — Master Orchestrator + Quality Critic (#49, #53)
- [ ] Migrar LangChain → LangGraph para orchestrator.py
- [ ] `src/agents/master_orchestrator.py` com Claude API
- [ ] `src/agents/quality_critic.py` estendendo critic_agent.py
- [ ] `src/api/claude_client.py` + `src/api/gemini_client.py`
- [ ] Adicionar bloco `llm_routing` no config.yaml
- [ ] Testar pipeline: input → orchestrator → agente → critic → output

### MÊS 2 — Dynamics + Agentforce (#31–#41)
- [ ] `src/api/dynamics_client.py` (Microsoft Graph + Dynamics API)
- [ ] Criar agentes #31–#36 (Dynamics)
- [ ] Criar agentes #37–#41 (Agentforce)
- [ ] `src/mcp/erp_server.py` com tools Dynamics + Salesforce
- [ ] Submeter MCP connector para Microsoft Marketplace
- [ ] Submeter para Salesforce AppExchange
- [ ] Criar price_ids no Stripe para Dynamics Pack e Agentforce Pack
- [ ] Simplificar docker-compose (remover Kafka, ELK)

### MÊS 3 — Oracle + SAP + Regulatory Watch (#42–#48, #51)
- [ ] `src/api/oracle_client.py` + `src/api/sap_client.py`
- [ ] Criar agentes #42–#48
- [ ] `src/agents/regulatory_watch.py` com web scraping DOU
- [ ] Conta SAP Store (BTP Partner Center)
- [ ] Oracle Agent Marketplace listing
- [ ] Criar price_ids no Stripe para Oracle e SAP packs

### Q4 2026 — Inteligência (#51–#53) + Client Intel (#52)
- [ ] `src/agents/regulatory_watch.py` em produção com alertas
- [ ] `src/agents/client_intelligence.py` com memória episódica
- [ ] Atualizar listings com badge "Atualização automática de normas"

### Q1 2027 — Auto-aprimoramento (#54–#56)
- [ ] `src/agents/meta_learning.py` ativando `evolution.gea`
- [ ] `src/agents/ecosystem_evolution.py` com pesquisa semanal
- [ ] `src/agents/federated_knowledge.py` ativando `rl.federated`
- [ ] ESG global cluster em produção (#16–#18 + #41 + #44 + #48)

---

## 10. PROJEÇÃO DE FATURAMENTO

### Comparativo: sem MCP vs com MCP (ARR em R$ milhões)

| Ano | Sem MCP | Com MCP | Driver |
|-----|---------|---------|--------|
| 1 | R$ 2,4M | R$ 2,4M | Brasil — regulatórios Q3 |
| 2 | R$ 11M | R$ 14M | Dynamics + Agentforce + MCP elimina gargalo |
| 3 | R$ 27M | R$ 58M | Oracle + SAP + ESG global + Cluster CBAM |
| 4 | R$ 59M | R$ 148M | Compounding MCP + auto-aprimoramento ativo |
| 5 | R$ 124M | R$ 312M | 56 agentes + 4 plataformas + federated knowledge |

### ARR ano 5 por canal (com MCP)

| Canal | ARR ano 5 |
|-------|-----------|
| Microsoft Copilot Studio | R$ 82M |
| Salesforce Agentforce | R$ 68M |
| Google Gemini + GCP | R$ 42M |
| Claude (Anthropic via MCP) | R$ 28M |
| Oracle + SAP | R$ 34M |
| Brasil direto (Stripe) | R$ 26M |
| Cluster ESG Global (CBAM UE) | R$ 32M |
| **TOTAL** | **R$ 312M** |

### Ticket médio por canal

| Canal | Ticket médio/mês |
|-------|-----------------|
| Google Cloud | R$ 780 |
| Microsoft Marketplace | R$ 1.490 |
| Salesforce AgentExchange | R$ 1.200 |
| Oracle Agent Marketplace | USD 499 |
| SAP Store | USD 799 |
| MCP (todos os clients) | USD 249 (média) |

---

## REFERÊNCIAS REGULATÓRIAS

| Norma | Deadline | Multa/Risco |
|-------|----------|------------|
| Portaria MTE 1.419/2024 (NR-1) | Vigente desde maio/2025 | Interdição + autuação |
| Lei 13.709/2018 (LGPD) | Vigente | R$ 50M por infração |
| Lei 14.457/2022 (Canal Denúncias) | Vigente | Irregularidade trabalhista |
| Lei 14.611/2023 (Igualdade Salarial) | Relatório anual MTE | R$ 140,6/funcionário/dia |
| LC 214/2025 (CBS/IBS) | Implementação 2026–2027 | Passivo fiscal |
| Lei 12.846/2013 (Anticorrupção) | Vigente | Até 20% faturamento bruto |
| Lei 15.042/2024 (SBCE/Carbono) | Regulamentação 2025–2026 | Exclusão de licitações |
| Res. CVM 193/2023 (IFRS S1/S2) | Companhias abertas 2026 | Exigência de divulgação |
| CBAM Reg. UE 2023/956 | Vigente para exportadores | Barreira de acesso ao mercado UE |

---

*Master document gerado em 2026-06-24 | Versão 3.0.0*
*Atualizar com DeepSeek após cada sprint de desenvolvimento*
*Próxima revisão: setembro 2026 (avaliação Q3 + preparação Oracle/SAP)*
*Documento de referência único — substitui todos os MDs anteriores desta sessão*
