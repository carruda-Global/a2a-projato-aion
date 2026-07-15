# Bridge de Cross-Sell Vertical + RAG como Diferencial
**EcoSystem AEC + Regulatory | Global Match Engenharia de Produção**
**Versão:** 1.0 | **Data:** 2026-06-24

---

## 1. O QUE É A BRIDGE

A bridge conecta agentes de grupos diferentes em uma jornada de compra contínua.
O cliente entra por um agente e é conduzido verticalmente pelos demais sem novo ciclo de venda.

A arquitetura RAG híbrida (BM25 + grafos + vetorial) já implementada no `config.yaml`
é o **argumento técnico** que justifica essa bridge — e que responde exatamente
à pergunta do vídeo: como arquitetar RAG em produção com múltiplos agentes,
controle de custo por token e fallback.

---

## 2. ARQUITETURA RAG DO ECOSSYSTEM — ARGUMENTO DE VENDA

### Como está implementado (config.yaml)
```yaml
rag:
  hybrid:
    enabled: true
    top_k: 5
    fusion_strategy: reciprocal_rank   # combina BM25 + vetorial com ranking ponderado
    cache_size: 500
  text_retriever:
    method: bm25                        # busca léxica — rápida e barata
  graph_retriever:
    max_depth: 3                        # grafo de conhecimento regulatório

budget:
  per_task_default: 0.10               # controle de custo por token por tarefa
  auto_fallback: true
  fallback_model: deepseek-chat        # fallback automático quando budget estoura

llm_routing:
  default: deepseek                    # agentes AEC e ESG — custo baixo
  sensitive_llm: gemini                # agentes RH/LGPD — dados sensíveis, Brasil
```

### O que isso significa em linguagem de venda
- **RAG híbrido** = respostas mais precisas que qualquer chatbot genérico porque
  combina busca semântica + busca exata + grafo de normas regulatórias
- **Controle de custo por token** = cliente nunca tem surpresa na fatura —
  budget por tarefa com fallback automático para modelo mais barato
- **Fallback automático** = sistema nunca para — se o modelo principal
  falhar ou estoura budget, cai para DeepSeek sem intervenção humana
- **Memória híbrida** = agente lembra do contexto da empresa entre sessões —
  não precisa reexplicar o CNPJ e o setor toda vez

---

## 3. BRIDGES VERTICAIS — 3 JORNADAS PRINCIPAIS

### Jornada A — Entrada RH → Financeiro → Compliance
**Canal:** Microsoft + Salesforce
**Cliente típico:** PME com 50–500 funcionários
**Agentes novos inseridos:** Onboarding (#N1), Atendimento PT-BR (#N2), Conciliação Financeira (#N3)

```
[ENTRADA]
Onboarding de Funcionários (#N1 — NOVO)
R$ 490/mês
"Automatize admissão, contratos e provisionamento de acesso"
        ↓
        Cross-sell trigger: funcionário admitido gera obrigação NR-1
        ↓
[UPSELL 1]
NR-1 Psicossocial (#13)
+ R$ 390/mês → total R$ 880/mês
"Inventário FRPRT obrigatório para o novo colaborador"
        ↓
        Cross-sell trigger: folha cresceu = obrigação Igualdade Salarial
        ↓
[UPSELL 2]
Igualdade Salarial (#20)
+ R$ 490/mês → total R$ 1.370/mês
"Relatório MTE anual — multa R$ 140,6/funcionário/dia"
        ↓
        Cross-sell trigger: dados salariais geram necessidade de LGPD
        ↓
[UPSELL 3]
LGPD Operacional (#15)
+ R$ 290/mês → total R$ 1.660/mês
"Dados de RH são dados pessoais sensíveis — RoPA obrigatório"
        ↓
        Cross-sell trigger: empresa tem dados → precisa de canal de denúncias
        ↓
[UPSELL 4]
Canal de Denúncias (#19)
+ R$ 290/mês → total R$ 1.950/mês
"Lei 14.457/2022 — obrigatório para empresas com CIPA"
        ↓
        Cross-sell trigger: dúvidas de clientes aumentam com equipe maior
        ↓
[UPSELL 5]
Atendimento ao Cliente PT-BR (#N2 — NOVO)
+ R$ 390/mês → total R$ 2.340/mês
"Resolva tickets L1 automaticamente via WhatsApp + Teams em português"
        ↓
        Cross-sell trigger: volume de transações cresce com equipe maior
        ↓
[UPSELL 6]
Conciliação Financeira (#N3 — NOVO)
+ R$ 790/mês → total R$ 3.130/mês
"Feche o mês sem erros — conciliação automática de NFs e extratos"
```

**LTV potencial jornada A:** R$ 3.130/mês por cliente
**Ticket médio de entrada:** R$ 490
**Multiplicador:** 6,4x sem novo ciclo de venda

---

### Jornada B — Entrada Fiscal → ESG → Carbono
**Canal:** Google Cloud + Oracle (Q1 2027)
**Cliente típico:** Média empresa com obrigações fiscais e ESG

```
[ENTRADA]
Tributário CBS/IBS (#14)
R$ 390/mês
"Classifique NCM e simule impacto CBS/IBS antes da virada"
        ↓
        Cross-sell trigger: empresa com compliance fiscal quer compliance total
        ↓
[UPSELL 1]
Compliance Anticorrupção (#21)
+ R$ 390/mês → total R$ 780/mês
"Programa de integridade exigido em licitações públicas"
        ↓
        Cross-sell trigger: empresa em licitação precisa de ESG para fornecedores
        ↓
[UPSELL 2]
ESG IFRS S1/S2 (#16)
+ R$ 490/mês → total R$ 1.270/mês
"Diagnóstico ESG e relatórios IFRS para fornecedores de grandes empresas"
        ↓
        Cross-sell trigger: ESG exige inventário de carbono
        ↓
[UPSELL 3]
Inventário Carbono (#17)
+ R$ 890/mês → total R$ 2.160/mês
"Cálculo Escopo 1/2 conforme Lei 15.042/2024 e GHG Protocol"
        ↓
        Cross-sell trigger: carbono próprio calculado → rastrear cadeia
        ↓
[UPSELL 4]
Escopo 3 Fornecedores (#18)
+ R$ 690/mês → total R$ 2.850/mês
"15 categorias GHG + CBAM para exportadores para a UE"
        ↓
        Cross-sell trigger: dados de fornecedores geram obrigação LGPD
        ↓
[UPSELL 5]
LGPD Operacional (#15)
+ R$ 290/mês → total R$ 3.140/mês
"Dados de fornecedores são dados pessoais — mapeamento obrigatório"
```

        ↓
        Cross-sell trigger: operação ESG cresceu = mais transações financeiras
        ↓
[UPSELL 6]
Conciliação Financeira (#N3 — NOVO)
+ R$ 790/mês → total R$ 3.930/mês
"Concilie NFs de fornecedores ESG e extratos bancários automaticamente"
        ↓
[UPSELL 7]
Atendimento ao Cliente PT-BR (#N2 — NOVO)
+ R$ 390/mês → total R$ 4.320/mês
"Responda dúvidas ESG e LGPD de clientes via WhatsApp sem intervenção humana"
```

**LTV potencial jornada B:** R$ 4.320/mês por cliente
**Ticket médio de entrada:** R$ 390
**Multiplicador:** 11x sem novo ciclo de venda

---

### Jornada C — Entrada AEC → Regulatório → Microsoft
**Canal:** Google Cloud → Microsoft (co-sell)
**Cliente típico:** Construtora ou escritório de engenharia

```
[ENTRADA]
Compliance PGRS (#12)
R$ 897/mês
"Gestão de conformidade PGRS/PGRSS com alertas legais"
        ↓
        Cross-sell trigger: obra tem funcionários = obrigação NR-1
        ↓
[UPSELL 1]
NR-1 Psicossocial (#13)
+ R$ 390/mês → total R$ 1.287/mês
        ↓
[UPSELL 2]
Canal de Denúncias (#19)
+ R$ 290/mês → total R$ 1.577/mês
        ↓
        Cross-sell trigger: empresa cresce → precisa de Microsoft Pack
        ↓
[UPSELL 3 — CO-SELL MICROSOFT]
Regulatory Analyst (#22) + Knowledge Agent (#25)
+ R$ 1.694/mês → total R$ 3.271/mês
"Análise de contratos via SharePoint + busca inteligente de normas"
        ↓
        Cross-sell trigger: equipe de obra cresce = mais admissões
        ↓
[UPSELL 4]
Onboarding de Funcionários (#N1 — NOVO)
+ R$ 490/mês → total R$ 3.761/mês
"Automatize admissão de novos colaboradores da obra no Teams"
        ↓
        Cross-sell trigger: obras geram dúvidas de clientes e fornecedores
        ↓
[UPSELL 5]
Atendimento ao Cliente PT-BR (#N2 — NOVO)
+ R$ 390/mês → total R$ 4.151/mês
"Resolva dúvidas de fornecedores e clientes da obra via WhatsApp"
        ↓
        Cross-sell trigger: volume financeiro de obra exige conciliação
        ↓
[UPSELL 6]
Conciliação Financeira (#N3 — NOVO)
+ R$ 790/mês → total R$ 4.941/mês
"Concilie medições, NFs de materiais e extratos automaticamente"
```

**LTV potencial jornada C:** R$ 4.941/mês
**Multiplicador:** 5,5x + ativa co-sell Microsoft

---

## 4. IMPLEMENTAÇÃO TÉCNICA — CROSS-SELL ENGINE

### Trigger automático no orchestrator
```python
# src/cross_selling.py — adicionar lógica de trigger por jornada

JOURNEY_TRIGGERS = {
    "onboarding_funcionarios": {
        "next": "nr1_psicossocial",
        "trigger_condition": "employee_count > 0",
        "message": "Novo colaborador admitido requer inventário NR-1 psicossocial (Portaria MTE 1.419/2024)"
    },
    "nr1_psicossocial": {
        "next": "igualdade_salarial",
        "trigger_condition": "payroll_data_available",
        "message": "Relatório de Igualdade Salarial (Lei 14.611/2023) vence em março — configure agora"
    },
    "tributario_cbs_ibs": {
        "next": "compliance_anticorrupcao",
        "trigger_condition": "has_public_contracts or revenue > 500000",
        "message": "Empresa com contratos públicos precisa de programa de integridade (Lei 12.846/2013)"
    },
    "onboarding_funcionarios": {
        "next": "nr1_psicossocial",
        "trigger_condition": "employee_count > 0",
        "message": "Novo colaborador admitido requer inventário NR-1 psicossocial (Portaria MTE 1.419/2024)"
    },
    "atendimento_cliente_ptbr": {
        "next": "canal_denuncias",
        "trigger_condition": "ticket_volume > 50",
        "message": "Volume de atendimento alto — ative Canal de Denúncias para casos trabalhistas (Lei 14.457/2022)"
    },
    "conciliacao_financeira": {
        "next": "tributario_cbs_ibs",
        "trigger_condition": "nf_volume > 100",
        "message": "Alto volume de NFs identificado — simule impacto CBS/IBS antes da virada fiscal (LC 214/2025)"
    },
    "esg_ifrs": {
        "next": "inventario_carbono",
        "trigger_condition": "esg_diagnosis_complete",
        "message": "Diagnóstico ESG concluído — calcule Escopo 1/2 conforme Lei 15.042/2024"
    },
    "inventario_carbono": {
        "next": "escopo3_fornecedores",
        "trigger_condition": "scope_1_2_complete",
        "message": "Escopo 1/2 calculado — rastreie sua cadeia de fornecedores para CBAM e IFRS S2"
    }
}

def get_cross_sell_recommendation(current_agent: str, tenant_context: dict) -> dict:
    trigger = JOURNEY_TRIGGERS.get(current_agent)
    if not trigger:
        return None
    condition = trigger["trigger_condition"]
    if eval_condition(condition, tenant_context):
        return {
            "recommended_agent": trigger["next"],
            "message": trigger["message"],
            "discount": "15%",  # desconto de ativação para converter
            "urgency": get_regulatory_deadline(trigger["next"])
        }
```

### Notificação no dashboard do cliente
```python
# Após cada sessão completada, exibir no portal:

def generate_upsell_notification(tenant_id: str, completed_agent: str):
    rec = get_cross_sell_recommendation(completed_agent, get_tenant_context(tenant_id))
    if rec:
        return {
            "type": "cross_sell",
            "title": f"Próximo passo recomendado",
            "body": rec["message"],
            "cta": f"Ativar {rec['recommended_agent']} com {rec['discount']} de desconto",
            "urgency": rec["urgency"]
        }
```

---

## 5. ARGUMENTO DE VENDA TÉCNICO — RESPOSTA À PERGUNTA DO VÍDEO

Use este script nos listings do Microsoft Marketplace e AgentExchange:

```
"Como arquitetamos RAG em produção com múltiplos agentes,
controle de custo e fallback:"

✓ RAG híbrido (BM25 + vetorial + grafo de normas)
  → respostas precisas sobre legislação brasileira sem alucinação

✓ Controle de custo por token (budget: R$ 0,10/tarefa)
  → cliente nunca tem surpresa na fatura

✓ Fallback automático (DeepSeek → Gemini por agente)
  → sistema nunca para, dados sensíveis nunca saem do Brasil

✓ Memória híbrida entre sessões
  → agente lembra do contexto da empresa, não precisa reexplicar

✓ 30 agentes orquestrados em um único painel
  → cliente começa por R$ 390/mês e expande conforme obrigações surgem
```

---

## 6. CO-SELL — SCRIPT PARA PARCEIROS

Para escritórios de contabilidade, consultorias SST e MSPs Microsoft:

```
"Seu cliente tem obrigação [NR-1 / LGPD / CBS/IBS]?

Ofereça o EcoSystem como ferramenta de automação —
você mantém a consultoria, o agente faz o trabalho operacional.

Comissão de 20% recorrente sobre MRR do cliente indicado.
Sem setup, sem contrato mínimo, ativa em 24h."
```

---

## 7. CHECKLIST DE IMPLEMENTAÇÃO

- [x] Adicionar `JOURNEY_TRIGGERS` ao `src/cross_selling.py`
- [x] Criar notificação de upsell no `dashboard/portal` → `components/UpsellNotification.jsx`
- [x] Adicionar campo `recommended_next_agent` na resposta da API de cada agente → exibido no `AgentDetail.jsx`
- [x] Criar endpoint `GET /api/cross-sell/recommend/{tenant_id}` no `app/routers/cross_selling.py`
- [ ] Adicionar desconto de ativação (15%) no Stripe para cross-sell triggers → script `scripts/setup_stripe_agentic_commerce.py` (executar manualmente)
- [ ] Atualizar listings Microsoft e Salesforce com argumento RAG técnico (seção 5) — documentação manual
- [x] Criar página de "jornada do cliente" no portal → `pages/Journey.jsx` (rota `/journey`)

---

*Documento gerado em 2026-06-24 | Atualizar com DeepSeek após implementação do cross_selling.py*
