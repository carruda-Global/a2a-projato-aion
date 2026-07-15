# EcoSystem 2.0 — Marketplace Playbook
**Global Match Engenharia de Produção | CREA-SP 5071200171 | Cristiano Arruda**
**Versão:** 3.1 | **Data:** 2026-06-24
**LLM para atualização deste doc:** DeepSeek-V4-Flash

---

## 1. SITUAÇÃO ATUAL — O QUE ESTÁ PUBLICADO (E O PROBLEMA)

### O que subiu nos marketplaces
- **Salesforce AgentExchange:** listagem ativa com os 27 agentes do portfólio completo
- **Microsoft Marketplace:** listagem ativa com 21 agentes (API v2)

### O problema crítico dos listings atuais
Os anúncios estão posicionados como **"plataforma de 27 agentes"** — isso mata a conversão em PME.

PME não compra plataforma. PME compra solução para um problema específico com urgência legal.

O listing correto para PME tem:
1. Um agente / um problema / um preço de entrada visível
2. Gancho regulatório com prazo (multa, fiscalização, deadline legal)
3. Upsell natural depois da primeira compra

---

## 2. QUAIS AGENTES TRABALHAR AGORA — PRIORIDADE POR CANAL

### Regra geral de decisão
```
Agente tem urgência legal ativa em 2026? → SIM → publicar
Agente depende de ART/habilitação que você ainda não tem? → NÃO publicar (PGR)
Agente é AEC (#1–#9)? → Apenas Google Cloud, não Salesforce/Microsoft
```

### Fase 1 — Q3 2026 (AGORA — publicar/otimizar imediatamente)

| # | Agente | ID config | Norma | Canal | Status |
|---|--------|-----------|-------|-------|--------|
| 13 | NR-1 Psicossocial | `nr1_psicossocial` | Portaria MTE 1.419/2024 | Google + Salesforce + Microsoft | Publicar |
| 15 | LGPD Operacional | `lgpd_operacional` | Lei 13.709/2018 | Google + Salesforce + Microsoft | Publicar |
| 19 | Canal de Denúncias | `canal_denuncias` | Lei 14.457/2022 | Google + Salesforce + Microsoft | Publicar |
| 20 | Igualdade Salarial | `igualdade_salarial` | Lei 14.611/2023 | Google + Salesforce + Microsoft | Publicar |

**Produto de entrada Q3:** NR-1 + LGPD juntos = `regulatory_starter` a R$ 590/mês

### Fase 2 — Q4 2026

| # | Agente | ID config | Norma | Canal |
|---|--------|-----------|-------|-------|
| 14 | Tributário CBS/IBS | `tributario_cbs_ibs` | LC 214/2025 | Google + Salesforce |
| 21 | Compliance Anticorrupção | `compliance_anticorrupcao` | Lei 12.846/2013 | Google + Salesforce + Microsoft |

### Fase 3 — Q1 2027

| # | Agente | ID config | Norma | Canal |
|---|--------|-----------|-------|-------|
| 16 | ESG IFRS S1/S2 | `esg_ifrs` | Res. CVM 193/2023 | Google + Oracle |
| 17 | Inventário Carbono | `inventario_carbono` | Lei 15.042/2024 | Google + Oracle |
| 18 | Escopo 3 Fornecedores | `escopo3_fornecedores` | SBCE + CBAM + IFRS S2 | Google + Oracle |

### Agentes AEC — canal exclusivo Google Cloud
Grupos #1–#12 continuam apenas no Google Cloud Marketplace. Salesforce e Microsoft não são canais adequados para AEC/construção no mercado PME brasileiro.

### Agentes Microsoft Pack (#22–#27) — manter mas reposicionar
Listing atual com ticket R$ 4.482/mês não converte em self-serve. Mudar abordagem para co-sell com parceiros Microsoft (MSPs). Não é canal de self-serve PME.

---

## 3. ESTRUTURA DE PREÇOS — O QUE MANTER, O QUE MUDAR, O QUE CRIAR

### Problema atual no config.yaml
O `config.yaml` tem 10 planos no Stripe. Paradoxo da escolha — PME trava. Manter os `price_id` existentes no Stripe (não recriar), mas reorganizar a **apresentação** nos listings.

### Estrutura de preços recomendada (6 planos visíveis nos listings)

#### PLANO DE ENTRADA — porta obrigatória
```
Nome:     Compliance Essencial
Agentes:  #13 NR-1 Psicossocial + #15 LGPD Operacional
Preço:    R$ 590/mês
Price ID: price_1TlxVVQn4rfjkSvEpiBqaCSf  (regulatory_starter — já existe)
Gancho:   "Atenda às 2 obrigações legais com multa ativa em 2026"
Posição:  PRIMEIRO card em todos os listings. Destacado com badge "Mais popular"
```

#### PLANO PRO — upsell natural após entrada
```
Nome:     Regulatory Pro
Agentes:  #13 + #15 + #19 + #20 + #21 (NR-1 + LGPD + Denúncias + Igualdade + Anticorrupção)
Preço:    R$ 1.490/mês
Price ID: price_1TlxVVQn4rfjkSvEam443ZCP  (regulatory_professional — já existe)
Gancho:   "Compliance trabalhista completo. 5 obrigações legais em um painel"
```

#### PLANO ESG + CARBONO — fase 3 (Q1 2027)
```
Nome:     ESG + Carbono PME
Agentes:  #16 + #17 + #18
Preço:    R$ 2.490/mês
Price ID: price_1TlxVXQn4rfjkSvEl6uCfYgk  (esg_carbon_pack — já existe)
Gancho:   "IFRS S1/S2, GHG Protocol e SBCE para fornecedores e empresas abertas"
```

#### PLANO TRIBUTÁRIO — fase 2 (Q4 2026)
```
Nome:     Tributário CBS/IBS
Agentes:  #14
Preço:    R$ 390/mês (entrada) → R$ 1.490/mês (full)
Price ID: criar novo no Stripe (não existe isolado)
Gancho:   "Classifique NCM, simule impacto CBS/IBS e gere DeRE antes da virada"
Nota:     Lançar em outubro 2026 com urgência LC 214/2025
```

#### PLANO MICROSOFT PACK — co-sell apenas
```
Nome:     Microsoft Compliance Pack
Agentes:  #22 a #27
Preço:    R$ 4.482/mês
Price ID: price_1TlxVXQn4rfjkSvExSnW6XmL  (microsoft_pack — já existe)
Canal:    Co-sell com MSPs. Não colocar em destaque no self-serve.
```

#### PLANO FULL SUITE — âncora de preço
```
Nome:     Full Suite
Agentes:  Todos os 27
Preço:    R$ 9.497/mês
Price ID: price_1TlxVTQn4rfjkSvEn41gegAl  (full_suite — já existe)
Função:   Âncora de percepção de valor. Não é meta de venda inicial.
```

### Planos a desativar/ocultar dos listings (manter no Stripe, só sumir da vitrine)
- `starter` (R$ 997 — Spec Analyst isolado, confunde com o Regulatory Starter)
- `professional` (R$ 2.391 — 3 agentes AEC, não faz sentido em listing Salesforce/Microsoft)
- `enterprise` (R$ 4.685 — 5 agentes AEC, idem)
- `compliance_pack` (R$ 2.391 — PGRS/PGRSS, canal específico Google, não Salesforce/Microsoft)
- `regulatory_full` (R$ 3.490 — absorvido pelo Regulatory Pro + ESG separados)

---

## 4. OTIMIZAÇÕES NO config.yaml

### 4.1 Versão — sincronizar
```yaml
# ANTES
app:
  version: "3.0.0"  # diverge do AGENTS.md que está em 2.1.0

# DEPOIS
app:
  version: "2.1.0"  # ou definir 3.0.0 em ambos — o que importa é ser igual
```

### 4.2 Azure — mover IDs hardcoded para env
```yaml
# ANTES
marketplace:
  microsoft:
    tenant_id: "cb5ac0c5-38eb-4805-b0f7-097dddbca380"
    client_id: "9d781521-1c9c-4604-9e49-03f29c0f3091"

# DEPOIS
marketplace:
  microsoft:
    tenant_id: ${AZURE_TENANT_ID}
    client_id: ${AZURE_CLIENT_ID}
    client_secret: ${AZURE_CLIENT_SECRET}
```

### 4.3 Clusters — renomear para refletir os agentes reais
```yaml
# ANTES — clusters industriais genéricos (production/logistics/quality)
# que não correspondem aos grupos do AGENTS.md

# DEPOIS — nomear por grupo de produto
clusters:
  aec_core:          # agentes #1–#5
  aec_specialized:   # agentes #6–#9
  aec_compliance:    # agentes #10–#12
  regulatory:        # agentes #13–#21
  microsoft:         # agentes #22–#27
```

### 4.4 LLM — segmentação por sensibilidade de dados (LGPD)
```yaml
# Adicionar bloco de roteamento de LLM por agente

llm_routing:
  default: deepseek          # agentes AEC e ESG/Carbono
  sensitive_agents:          # agentes com dados pessoais sensíveis
    - nr1_psicossocial       # dados de saúde mental de funcionários
    - lgpd_operacional       # mapeamento de dados pessoais
    - canal_denuncias        # denúncias (dado ultra-sensível)
    - igualdade_salarial     # dados salariais
    - compliance_anticorrupcao
  sensitive_llm: gemini      # ou claude-api — processamento dentro do Brasil/EUA
  # Nota: DeepSeek NÃO deve processar dados dos agentes sensitive_agents
  # Art. 33 LGPD — transferência internacional exige DPA específico
```

### 4.5 Stripe — adicionar plano tributário faltante
```yaml
# Adicionar após esg_carbon_pack:
    tributario_entrada:
      name: "Tributário CBS/IBS - Starter"
      amount_cents: 39000
      price_id: "CRIAR_NO_STRIPE"  # criar price_id novo no dashboard Stripe
    tributario_full:
      name: "Tributário CBS/IBS - Full"
      amount_cents: 149000
      price_id: "CRIAR_NO_STRIPE"
```

### 4.6 Monitoramento — prometheus_port conflito
```yaml
# ANTES — porta 8000 conflita com o orchestrator
monitoring:
  metrics:
    prometheus_port: 8000

# DEPOIS
monitoring:
  metrics:
    prometheus_port: 9091   # 9090 já é do Prometheus container, usar 9091
```

---

## 5. OTIMIZAÇÕES NO AGENTS.md

### 5.1 Agentes para ATIVAR no listing (alterar `status` para `active`)
```
#13 nr1_psicossocial     → active  (Q3 2026)
#15 lgpd_operacional     → active  (Q3 2026)
#19 canal_denuncias      → active  (Q3 2026)
#20 igualdade_salarial   → active  (Q3 2026)
#14 tributario_cbs_ibs   → scheduled_q4_2026
#21 compliance_anticorrupcao → scheduled_q4_2026
#16 esg_ifrs             → scheduled_q1_2027
#17 inventario_carbono   → scheduled_q1_2027
#18 escopo3_fornecedores → scheduled_q1_2027
```

### 5.2 Agentes AEC (#1–#12) — manter no Google Cloud, NÃO listar no Salesforce/Microsoft
Nenhuma alteração de funcionalidade — apenas canal restrito a Google Cloud Marketplace.

### 5.3 Agentes Microsoft (#22–#27) — reposicionar como co-sell
Alterar descrição do canal de "self-serve" para "co-sell via parceiros Microsoft (MSPs)".
Não remover do Microsoft Marketplace — apenas ajustar o pitch de self-serve para parceiro.

---

## 6. COPY DOS LISTINGS — SALESFORCE E MICROSOFT

### 6.1 Listing principal (produto de entrada) — usar em AMBOS os marketplaces

**Título do listing:**
```
Compliance Essencial — NR-1 Psicossocial + LGPD | Agente de IA para PMEs
```

**Subtítulo / tagline:**
```
Atenda 2 obrigações legais com prazo ativo em 2026 — sem contratar consultoria
```

**Descrição curta (até 300 chars):**
```
Agente de IA que gera inventário de riscos psicossociais (NR-1/Portaria MTE 1.419/2024)
e mapeamento de dados LGPD (RoPA/ANPD) de forma automatizada. Para PMEs que precisam
de compliance sem equipe interna. Resultado em 48h.
```

**Descrição longa:**
```
## O que resolve

Sua empresa está sujeita a multas por descumprir:
- Portaria MTE 1.419/2024 — Riscos Psicossociais (NR-1): obrigatória para todas as empresas
- Lei 13.709/2018 — LGPD: sanções ANPD de até R$ 50M por infração

## Como funciona

1. Você responde um formulário guiado pelo agente (20 min)
2. O agente gera o inventário FRPRT, plano de ação e documentação NR-1
3. O agente mapeia seus fluxos de dados e gera o RoPA (Registro de Operações)
4. Você recebe os documentos prontos para auditoria e fiscalização

## O que você recebe

- Inventário de Riscos Psicossociais (FRPRT) conforme Portaria MTE 1.419/2024
- Plano de ação com prazos e responsáveis
- Relatórios para CIPA e gestão
- RoPA — Registro de Atividades de Tratamento (LGPD)
- Mapeamento de dados pessoais da empresa
- Relatório de conformidade ANPD

## Para quem é

PMEs com 10 a 500 funcionários que ainda não têm compliance NR-1 psicossocial
e LGPD implementados e não querem contratar consultoria cara.

## Preço

R$ 590/mês — cancele quando quiser.
```

**Keywords para ambos os marketplaces:**
```
NR-1, riscos psicossociais, LGPD, compliance, PME, IA, agente, MTE, ANPD,
portaria 1419, lei 13709, RoPA, inventário FRPRT, engenharia de produção
```

---

### 6.2 Listing secundário — Salesforce AgentExchange específico

**Título:**
```
Regulatory AI Agent — Compliance Trabalhista e LGPD para PMEs Brasileiras
```

**Categoria no AgentExchange:** `Human Resources` + `Legal & Compliance`

**Integração a destacar:**
```
Integra com Salesforce Service Cloud para abertura de casos de denúncia
e com Salesforce HR via Flow para disparar inventário NR-1 automaticamente
em novos funcionários.
```

**Nota:** No AgentExchange, o gancho deve ser a integração com o ecossistema Salesforce — não apenas o agente standalone.

---

### 6.3 Listing Microsoft Marketplace específico

**Título:**
```
EcoSystem Regulatory — Compliance NR-1, LGPD e Trabalhista via Microsoft 365
```

**Categoria:** `Human Resources` + `Legal + Compliance`

**Integração a destacar:**
```
Agente disponível no Microsoft Teams. Resultados e documentos salvos
automaticamente no SharePoint. Tarefas de plano de ação criadas no Planner.
Funciona com licença Microsoft 365 Business ou superior.
```

**Plano de entrada no Microsoft listing:**
```
Compliance Essencial: R$ 590/mês
```
*(Não colocar o Microsoft Pack de R$ 4.482 como card principal)*

---

## 7. CANAIS — O QUE ATIVAR, PAUSAR E PRIORIZAR

| Canal | Ação Q3 2026 | Produto de entrada | Observação |
|-------|-------------|-------------------|------------|
| Google Cloud Marketplace | ✅ Foco total | Regulatory Starter R$ 590 | Canal primário — não diluir esforço |
| Microsoft Marketplace | ✅ Otimizar listing | Compliance Essencial R$ 590 | Self-serve apenas para o bundle de entrada |
| Salesforce AgentExchange | ✅ Otimizar listing | Compliance Essencial R$ 590 | Gancho de integração Salesforce é obrigatório |
| Oracle Cloud Marketplace | ⏸ Pausar | — | Ativar Q1 2027 com ESG/Carbono |
| AWS Marketplace | ⏸ Pausar | — | Ativar só com ARR > R$ 3M |
| SAP AI Agent Hub | 🎯 Avaliar entrada | CBS/IBS R$ 390 | Janela LC 214/2025, €100M fundo ISV ativo |
| MuleRun / NexusGPT | ✅ Manter | — | Custo zero, boa para awareness |
| SwarmSync / OpenStall | ⏸ Pausar | — | Protocolo A2A ainda imaturo |

---

## 8. CHECKLIST DE EXECUÇÃO

### Semana 1 — Listings (prioridade máxima)
- [ ] Atualizar título e descrição do listing Salesforce com copy da seção 6.2
- [ ] Atualizar título e descrição do listing Microsoft com copy da seção 6.3
- [ ] Colocar `Compliance Essencial` (R$ 590) como primeiro plano visível nos dois marketplaces
- [ ] Ocultar/desativar planos AEC dos listings Salesforce e Microsoft
- [ ] Adicionar keywords regulatórias (seção 6.1) nos dois listings
- [ ] Configurar badge "Mais popular" no plano de entrada

### Semana 1 — config.yaml (DeepSeek atualiza)
- [ ] Sincronizar `version` com AGENTS.md
- [ ] Mover `tenant_id` e `client_id` Azure para `${AZURE_TENANT_ID}` / `${AZURE_CLIENT_ID}`
- [ ] Corrigir `prometheus_port` de 8000 para 9091
- [ ] Adicionar bloco `llm_routing` com segregação de agentes sensíveis
- [ ] Renomear clusters de `production/logistics/quality` para `aec_core/aec_specialized/aec_compliance/regulatory/microsoft`
- [ ] Criar price_ids do Tributário no Stripe e adicionar ao config.yaml

### Semana 2 — AGENTS.md (DeepSeek atualiza)
- [ ] Adicionar campo `status` em cada agente (active / scheduled_q4_2026 / scheduled_q1_2027)
- [ ] Adicionar campo `channels` em cada agente (google / salesforce / microsoft / oracle)
- [ ] Adicionar campo `llm_tier` em cada agente (default / sensitive)
- [ ] Remover referência a planos desativados da seção de planos
- [ ] Atualizar seção de Marketplaces com status correto por canal

### Mês 2 — Infraestrutura
- [ ] Migrar agentes sensitive_agents de DeepSeek para Gemini/Claude API
- [ ] Reduzir stack Docker de 14 para 6 serviços
- [ ] Configurar Vault para todos os secrets (Stripe, Supabase, DeepSeek, Azure)
- [ ] Criar `.dockerignore` definitivo

---

## 9. PROJEÇÃO DE RECEITA — COM ESTRUTURA OTIMIZADA

### Base de cálculo (modelo conservador Q3–Q4 2026)

| Fase | Agentes ativos | Plano entrada | Meta clientes | MRR |
|------|---------------|---------------|---------------|-----|
| Q3 2026 | #13 + #15 + #19 + #20 | R$ 590 | 50 clientes | R$ 29.500 |
| Q4 2026 | + #14 + #21 | R$ 590–1.490 | 150 clientes | R$ 103.000 |
| Q1 2027 | + #16 + #17 + #18 | R$ 590–2.490 | 300 clientes | R$ 199.000 |

**ARR projetado em 12 meses:** ~R$ 2,4M (base) / R$ 2,7M (otimista)

### Ticket médio esperado por canal
- Google Cloud Marketplace: R$ 780/mês (mix entrada + upsell)
- Salesforce AgentExchange: R$ 1.200/mês (perfil enterprise leve)
- Microsoft Marketplace: R$ 590/mês (self-serve, sem co-sell)

---

## 10. REFERÊNCIAS REGULATÓRIAS (para copy e pitch)

| Norma | Deadline / Urgência | Multa / Consequência |
|-------|--------------------|--------------------|
| Portaria MTE 1.419/2024 (NR-1 Psicossocial) | Vigente desde maio/2025 | Interdição + autuação fiscal |
| Lei 13.709/2018 (LGPD) | Vigente | R$ 50M por infração / 2% faturamento |
| Lei 14.457/2022 (Canal Denúncias) | Vigente | Irregularidade trabalhista |
| Lei 14.611/2023 (Igualdade Salarial) | Relatório anual MTE | Multa R$ 140,6 por funcionário/dia |
| LC 214/2025 (CBS/IBS) | Implementação 2026–2027 | Risco tributário na transição |
| Lei 12.846/2013 (Anticorrupção) | Vigente | Até 20% do faturamento bruto |
| Lei 15.042/2024 (SBCE/Carbono) | Regulamentação 2025–2026 | Exclusão de licitações públicas |
| Res. CVM 193/2023 (IFRS S1/S2) | Companhias abertas 2026 | Exigência de divulgação |

---

*Documento gerado por análise council completa em 2026-06-24.*
*Atualizar este arquivo com DeepSeek após cada sprint de desenvolvimento.*
*Próxima revisão: setembro 2026 (avaliação Q3 + preparação Q4).*
