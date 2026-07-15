# AION 7.0 — AUDITORIA COMPLETA DO PROJETO
**Última atualização:** 02/07/2026 (sessão 3)
**Propósito:** Documentação completa do estado atual de todos os componentes do EcoSystem AION.

---

## 1. PROJETO — Overview

| Campo | Valor |
|-------|-------|
| **Nome** | AION — Agents Intelligence Orchestration Network |
| **Versão** | 7.0.0 |
| **Proprietário** | Cristiano Arruda \| Global Match Engenharia de Produção \| CREA-SP 5071200171 |
| **LLM Core** | DeepSeek-V4-Flash (API OpenAI compatible) + OpenRouter/Kimi-K2 (fallback) + Gemini (agentes sensíveis LGPD) + Claude API (raciocínio complexo) |
| **Framework** | Python + FastAPI + A2A Protocol |
| **Hosting** | Render.com (produção) + Supabase (banco de dados) |
| **Repositório** | `github.com/carruda-Global/engenheiro-producao-ai.git` (branch `main`) |
| **API Produção** | `https://engenheiro-producao-ai.onrender.com/` |
| **Site/Vendas** | `global-engenharia.com` (Netlify) |
| **Email** | carruda2307@gmail.com |

### LLM Tier

| Tier | LLM | Agentes |
|------|-----|---------|
| `default` | DeepSeek-V4-Flash | Agentes AEC, ESG/Carbono, Microsoft |
| `fallback` | OpenRouter (Kimi-K2) | Automático quando DeepSeek falha |
| `sensitive` | Gemini | Agentes com dados pessoais sensíveis (NR-1, LGPD, Denúncias, Igualdade Salarial, Anticorrupção) |
| `reasoning` | Claude API | Orquestrador, Quality Critic, Evolução |

---

## 2. STATUS ATUAL (o que está rodando AGORA)

### 2.1 API em Produção
- **URL:** `https://engenheiro-producao-ai.onrender.com/`
- **Status:** ✅ Operacional — 59 agentes reportados no startup
- **Último commit:** `a77ca5f` — fix: resolve AgentVerse timeout (01/07/2026)
- **Serviços adicionais no Render:**
  - `hmas-mcp-regulatory` — MCP Regulatory Server (porta 8010)
  - `hmas-mcp-esg` — MCP ESG Server (porta 8011)
  - `hmas-mcp-erp` — MCP ERP Server (porta 8012)
  - `hmas-mcp-microsoft` — MCP Microsoft Server (porta 8013)
  - `aion-linkedin-agent` — Worker LinkedIn (Dockerfile.worker)
- **Banco:** Supabase PostgreSQL (`gveuivwuilhhwhzjdnvg.supabase.co`)

### 2.2 Chrome Extension
- **Nome:** "SallesJam Compliance - NR-1, LGPD e mais"
- **Status:** ✅ **PUBLICADO** no Chrome Web Store
- **Link:** `https://chromewebstore.google.com/search/SallesJam%20Compliance`
- **Versão:** 1.0.0 (Manifest V3)

### 2.3 Google Workspace Add-on
- **Status:** ⏳ **REJEITADO** — precisa re-submissão
- **Problemas:** OAuth verification pendente, ícones/screenshots, DNS verification

### 2.4 GPT Store (OpenAI) (02/07)
- **Status:** ✅ **PUBLICADO** — GPT Store
- **Link:** `https://chatgpt.com/g/g-6a4722571f8c8191be8098dc58c86173-aion-compliance`
- **Nome:** AION Compliance
- **Endpoints:** NR-1, EU AI Act, CSRD, Pricing (4 endpoints)
- **Schema:** `gpt_store_openapi.yaml` (OpenAPI 3.1.0)
- **Auth:** API Key → Bearer → `sk-svcacct-...`

### 2.5 Hugging Face Space (02/07)
- **Status:** ✅ **PRONTO** — arquivos prontos em `huggingface_space/`
- **Aguardando:** Upload manual em huggingface.co/new-space (SDK: Gradio)
- **Tabs:** NR-1, EU AI Act, CSRD (3 tabs) Office Add-in (Microsoft)
- **Status:** 🔄 **SUBMETENDO** ao Partner Center
- **Manifest:** `AION 7.0/templates/office-addin/manifest.xml`

### 2.5 x402 v2 HTTP Payment Protocol (NOVO — 01/07)
- **Status:** ✅ **FUNCIONANDO** — validator confirma "Implementation Looks Correct / All checks pass"
- **Endpoint base:** `https://engenheiro-producao-ai.onrender.com/api/marketplace/execute/{service_id}`
- **Protocolo:** x402 v2 com header `PAYMENT-REQUIRED` (base64)
- **Facilitador CDP:** `https://api.cdp.coinbase.com/platform/v2/x402/facilitator`
- **Rede de pagamento:** USDC on Base mainnet (eip155:8453)
- **Contrato USDC:** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **Carteira recebedora:** `0xadf695146d93281dCfaa711F2B38719CF520DD9A`
- **Pendência:** CDP Bazaar indexa o endpoint somente após o primeiro pagamento USDC real (verify+settle)

### 2.6 AgentVerse (Fetch.ai) (NOVO — 01/07)
- **Status:** 🔄 **Deploy em andamento** — fix de timeout aplicado, aguardando Render redeploy
- **Nome do agente:** "EcoSystem Compliance"
- **Endereço:** `agent1qwfezkcfvjaze692t5s0kjfcw0v8drd599r4npax6vkwmgd88ehzxx6x96f`
- **Endpoint:** `https://engenheiro-producao-ai.onrender.com/api/agentverse/messages`
- **Bug corrigido:** timeout do AgentVerse (~10-15s) vs LLM call (30-60s) → respostas agora são templates pré-construídos em <1ms
- **Arquivo:** `src/agents/agentverse_handler.py`

### 2.7 Marketplaces A2A (NOVO — 01/07)
Todos registrados automaticamente a cada 7 dias via `auto_job_marketplace_registration()`.

| Marketplace | URL | Status | Obs |
|-------------|-----|--------|-----|
| Agentic.Market | agentic.market | 🔄 Aguarda 1º USDC payment | CDP Bazaar indexa após verify+settle |
| Prism | prism.xyz | 🔄 Registro automático | `PRISM_KEY` necessário |
| Obol Stack | obol.xyz | 🔄 Registro automático | `OBOL_KEY` necessário |
| Theoriq | theoriq.ai | 🔄 Registro automático | `THEORIQ_API_KEY` necessário |
| Virtuals Protocol | virtuals.io | 🔄 Registro automático | `VIRTUALS_API_KEY` necessário |
| Nevermined | nevermined.io | 🔄 Registro automático | `NEVERMINED_API_KEY` necessário |
| AgentVerse | agentverse.ai | 🔄 Fix aplicado | `AGENTVERSE_KEY` + `AGENT_SEED_PHRASE` |
| Bitte Protocol | bitte.ai | 🔄 Parcial | Conectado via AgentVerse. NEAR wallet configurada |
| Masa | masa.ai | 🔄 Registro automático | `MASA_API_KEY` necessário |

### 2.8 OpenRouter Fallback (NOVO — 01/07)
- **Status:** ✅ Implementado em `src/api/deepseek_client.py`
- **Modelo:** `moonshotai/kimi-k2` via OpenRouter
- **Chave:** `OPENROUTER_API_KEY` (usuário confirmou que está no Render)
- **Comportamento:** Se DeepSeek falha → fallback automático para Kimi-K2 via OpenRouter

### 2.9 SDR + LinkedIn + WhatsApp Prospecção Automática (NOVO — 02/07)

#### LinkedIn OAuth
- **Status:** ✅ **CONECTADO** — token salvo em `.config/aion/linkedin/tokens/`
- **Conta:** Cristiano Arruda (cristiano_aa@yahoo.com.br)
- **Escopos:** profile, email, openid, w_member_social
- **Limitação:** API search requer Sales Navigator (pago)

#### SDR Pipeline Automático
- **Status:** ✅ **FUNCIONANDO** — roda a cada 12h no job 24/7
- **Fluxo:** OpenRouter gera leads → DeepSeek escreve msg humanizada → WhatsApp + Email
- **Setores:** Construção (NR-1 + Spec Analyst), Indústria (NR-1 + Carbono), Tecnologia (NR-1 + Code Review)
- **Arquivos:** `scripts/sdr_pipeline.py`, `data/sdr/`

#### WhatsApp Bot
- **Status:** ✅ **FUNCIONANDO** — `whatsapp-bot/send.js`
- **Tecnologia:** whatsapp-web.js (WhatsApp Web)
- **Comportamento:** Verifica se número tem WhatsApp → envia direto ou salva rascunho
- **Queue:** `data/sdr/whatsapp_queue.json` (27 prospects acumulados)
- **Fila de emails:** `data/sdr/email_queue.json` (pendentes até domínio Resend verificar)

#### Resend Email
- **Status:** 🔄 Configurado — domínio `global-engenharia.com` aguardando verificação DNS
- **Chave:** `RESEND_API_KEY` configurada no `.env`
- **Sender:** `onboarding@resend.dev` (teste) → `cristiano.arruda@global-engenharia.com` (produção)

### 2.10 LGPD Agent Removido (02/07)
- **Status:** ❌ **REMOVIDO** de todas as plataformas de venda
- GPT Store, Hugging Face, SDR combos, WhatsApp queue — sem LGPD

---

## 3. CARTEIRAS E IDENTIDADES

### 3.1 Carteira USDC (Base network) — Pagamentos x402
- **Endereço:** `0xadf695146d93281dCfaa711F2B38719CF520DD9A`
- **Rede:** Base mainnet (eip155:8453)
- **Explorer:** `https://basescan.org/address/0xadf695146d93281dCfaa711F2B38719CF520DD9A`
- **Uso:** Recebe pagamentos de TODOS os marketplaces (x402, CDP Bazaar, Agentic.Market)

### 3.2 Agente AgentVerse (Fetch.ai)
- **Nome:** EcoSystem Compliance
- **Endereço:** `agent1qwfezkcfvjaze692t5s0kjfcw0v8drd599r4npax6vkwmgd88ehzxx6x96f`
- **Seed phrase:** `anxiety alert aware arrest alone alpha art access arrest awful attitude armor`
- **Endpoint:** `https://engenheiro-producao-ai.onrender.com/api/agentverse/messages`

### 3.3 Carteira NEAR (HOT Wallet — Bitte.ai)
- **Endereço:** `53iUFs9bd1bYAxH7W5vccVi79vG4XQnhEGHsTYZwE8EbcvoiQNFVupmDjjZtcQ4mhJ1faREJHNovDnw7LuuFv8nL`
- **Uso:** Bitte.ai, NEAR Protocol, pagamentos em NEAR/USDC via NEAR

---

## 4. ARQUITETURA

### 4.1 Estrutura do Projeto (`AION 7.0/`)

```
AION 7.0/
├── AGENTS.md                  # Documentação completa dos agentes
├── config.yaml                # Configuração central (agentes, planos, marketplaces)
├── requirements.txt           # Dependências Python (inclui uagents-core>=0.1.0)
├── Dockerfile                 # Containerização do orquestrador
├── Dockerfile.worker          # Containerização do worker LinkedIn
├── docker-compose.yml         # Orquestração Docker (8+ serviços)
├── render.yaml                # Deploy Render.com (5 serviços web + 1 worker)
├── pytest.ini                 # Configuração de testes
├── .env                       # Variáveis de ambiente (API keys REAIS — ver seção 13)
├── .env.example               # Template de variáveis
├── gpt_store_openapi.yaml     # Schema OpenAPI para GPT Store (4 endpoints) ← NOVO
│
├── app/
│   ├── main.py                # FastAPI app — ~700 linhas, 15 jobs, 51+ routers
│   └── routers/               # 26 arquivos de rotas
│
├── src/
│   ├── agents/
│   │   ├── agent_marketplace.py   # x402 v2 + 9 marketplace registrations ← NOVO
│   │   ├── agentverse_handler.py  # Fetch.ai uAgents handler (timeout fixado) ← NOVO
│   │   └── [103+ outros agentes]
│   │
│   └── api/
│       └── deepseek_client.py     # LLM client com OpenRouter fallback ← ATUALIZADO
│
├── huggingface_space/
│   ├── app.py                 # Gradio UI (4 tabs: NR-1, LGPD, EU AI Act, CSRD) ← NOVO
│   └── requirements.txt       # Deps do Space
│
├── chrome-extension/          # Chrome Extension (publicada)
├── templates/                 # Google Add-on, Office Add-in, widget HTML
├── tests/                     # 22+ arquivos de teste
├── scripts/                   # 66+ scripts de automação/deploy
└── stripe-app/                # Stripe App files
```

### 4.2 Infraestrutura Docker (`docker-compose.yml`)

| Serviço | Porta | Função |
|---------|-------|--------|
| **timescaledb** | 5432 | PostgreSQL + TimescaleDB |
| **redis** | 6379 | Cache e filas |
| **neo4j** | 7474/7687 | Banco de grafos |
| **chromadb** | 8001 | Banco vetorial |
| **minio** | 9000/9001 | Armazenamento S3-compatible |
| **prometheus** | 9090 | Métricas |
| **grafana** | 3000 | Dashboards |
| **vault** | 8200 | Gerenciamento de segredos |

> **⚠ Importante:** Docker **NÃO** está instalado localmente. Tudo roda standalone via `uvicorn`.

---

## 5. AGENTES (106 total)

### 5.1 Grupos de Agentes

| Categoria | Quantidade | Status |
|-----------|-----------|--------|
| Núcleo AEC (#1-5) | 5 | active |
| Especializados (#6-9) | 4 | active |
| Conformidade AEC (#10-12) | 3 | active |
| Regulatórios BR (#13-21) | 9 | 5 active, 4 scheduled |
| Microsoft (#22-27) | 6 | co-sell |
| Cross-Sell (#N1-N3) | 3 | active |
| Dynamics 365 (#31-36) | 6 | active |
| Agentforce Salesforce (#37-41) | 5 | active |
| Oracle CX (#42-45) | 4 | active |
| Coordenação + Inteligência | 5 | active |
| SAP | 3 | active |
| Self-Improvement | 3 | active |
| Tech (#57-59) | 3 | active |
| Enterprise Connectors (#60-62) | 3 | em implementação |
| Índia + UAE | 2 | active |
| Europeus (CSRD, DORA, NIS2, SOC2, ISO27001) | 5 | active |
| Automação Marketing/Vendas | 18 | active |
| Mercado (EUA, MX, CO, AR) | 4 | active |
| Micro-agentes (M1-M15) | 15 | active |
| **TOTAL** | **~106 agentes** | — |

### 5.2 Serviços de Compliance com Preço USDC (x402 — NOVO)

Estes 8 serviços são vendidos via protocolo x402 em todos os marketplaces A2A:

| Service ID | Nome | Preço USDC | Endpoint |
|-----------|------|-----------|---------|
| `compliance-nr1` | NR-1 Psychosocial Risk Diagnosis | 0.50 USDC | `/api/marketplace/execute/compliance-nr1` |
| `compliance-lgpd` | LGPD Data Privacy Scan | 0.75 USDC | `/api/marketplace/execute/compliance-lgpd` |
| `compliance-eu-ai-act` | EU AI Act Readiness Check | 1.00 USDC | `/api/marketplace/execute/compliance-eu-ai-act` |
| `compliance-csrd` | CSRD Double Materiality Assessment | 1.50 USDC | `/api/marketplace/execute/compliance-csrd` |
| `carbon-inventory` | Carbon Inventory Scope 1+2 | 1.00 USDC | `/api/marketplace/execute/carbon-inventory` |
| `vendor-risk` | Vendor Risk Assessment | 0.50 USDC | `/api/marketplace/execute/vendor-risk` |
| `contract-risk` | Contract Risk Analysis | 0.50 USDC | `/api/marketplace/execute/contract-risk` |
| `ma-due-diligence` | M&A Compliance Due Diligence | 2.00 USDC | `/api/marketplace/execute/ma-due-diligence` |

**Fluxo x402:**
1. `GET /api/marketplace/execute/{service_id}` sem `X-PAYMENT` → retorna HTTP 402 com header `PAYMENT-REQUIRED` (base64)
2. Cliente paga USDC → obtém token de pagamento
3. `POST /api/marketplace/execute/{service_id}` com `X-PAYMENT` → verifica via CDP → executa serviço

---

## 6. MERCADOS E PAÍSES

| País/Mercado | Agente Principal | Status | Moeda |
|-------------|-----------------|--------|-------|
| **Brasil** (primário) | NR-1, LGPD, CBS/IBS, ESG, Denúncias, Igualdade, Anticorrupção | ✅ **Ativo** | BRL / USD |
| **EUA** (EU AI Act) | EU AI Act Readiness Agent — Article 50 (deadline: 2 Aug 2026) | ✅ **Ativo** | USD |
| **México** | LFPDPPP Compliance Agent | ✅ **Ativo** | MXN / USD |
| **Colômbia** | Ley 1581 Compliance Agent | ✅ **Ativo** | COP / USD |
| **Argentina** | SDR/Back-office Automation Agent | ✅ **Ativo** | USD |
| **Índia** | India Multilingual Support Agent | ✅ **Codificado** | INR |
| **Emirados Árabes** | UAE Government Process Agent | ✅ **Codificado** | AED |
| **União Europeia** | CSRD, DORA, NIS2, SOC2, ISO27001 Agents | ✅ **Codificado** | EUR |

---

## 7. PLANOS E PREÇOS

### 7.1 Planos de Assinatura (Stripe — BRL)

| Plano | Price ID | Preço |
|-------|----------|-------|
| Compliance Essencial | `price_1TlxVVQn4rfjkSvEpiBqaCSf` | R$ 590/mês |
| Regulatory Pro | `price_1TlxVVQn4rfjkSvEam443ZCP` | R$ 1.490/mês |
| Tributário CBS/IBS Starter | `price_1Tm0gYQn4rfjkSvE1YFsQqq1` | R$ 390/mês |
| Tributário CBS/IBS Full | `price_1TmLJzQn4rfjkSvEWrh5bHV6` | R$ 1.490/mês |
| ESG + Carbono PME | `price_1TlxVXQn4rfjkSvEl6uCfYgk` | R$ 2.490/mês |
| Microsoft Compliance Pack | `price_1TlxVXQn4rfjkSvExSnW6XmL` | R$ 4.482/mês |
| Cross-Sell Harmony | `price_1TmLJtQn4rfjkSvETvw4iHjI` | R$ 490/mês |
| AEC Full | `price_1TlxVSQn4rfjkSvEXodTHfNA` | R$ 4.685/mês |
| Full Suite | `price_1TlxVTQn4rfjkSvEn41gegAl` | R$ 9.497/mês |
| Tech Starter | `CRIAR_NO_STRIPE` | R$ 1.997/mês |
| Tech Professional | `CRIAR_NO_STRIPE` | R$ 3.497/mês |
| Tech Enterprise | `CRIAR_NO_STRIPE` | R$ 5.997/mês |

### 7.2 Planos USD (global)
Todos os planos BRL têm equivalente USD com price IDs próprios (ver README v1 seção 6.2).

### 7.3 Stripe Integration Status
- ✅ **Conta Stripe:** Ativa (produção) — chaves `sk_live_*` e `pk_live_*` configuradas no Render
- ✅ **Webhooks:** Configurados (`whsec_lh0FM0KRx2nISA6vJGcIr1WjnCze2r7U`)
- ❌ **Clientes pagantes:** **0 (zero)** — nenhuma assinatura ativa

---

## 8. PLUGINS E MARKETPLACES — STATUS DETALHADO

### 8.1 Chrome Extension
- **Status:** ✅ **PUBLICADO** — Chrome Web Store
- **Link:** `https://chromewebstore.google.com/search/SallesJam%20Compliance`

### 8.2 Google Workspace Add-on
- **Status:** ⏳ **REJEITADO** — precisa re-submissão
- **Bloqueadores:** OAuth verification, DNS verification, ícones

### 8.3 Office Add-in (Microsoft)
- **Status:** 🔄 **SUBMETENDO** ao Partner Center

### 8.3b GPT Store (OpenAI) — NOVO (02/07)
- **Status:** ✅ **PUBLICADO**
- **Link:** `https://chatgpt.com/g/g-6a4722571f8c8191be8098dc58c86173-aion-compliance`
- **Endpoints:** NR-1, EU AI Act, CSRD, Pricing
- **Schema:** `gpt_store_openapi.yaml` (OpenAPI 3.1.0)

### 8.3c Hugging Face Space — NOVO (02/07)
- **Status:** ✅ Pronto para upload
- **Arquivos:** `huggingface_space/app.py` + `requirements.txt`
- **Tabs:** NR-1, EU AI Act, CSRD (Gradio)

### 8.3d NVS Marketplaces — NOVO (02/07)

| Plataforma | Tipo | Status |
|-----------|------|--------|
| **HubSpot App Marketplace** | API | Código pronto (`hubspot_client.py` + router) |
| **Pipefy Ecosystem** | API | Código pronto (`pipefy_client.py` GraphQL + router) |
| **Zapier App Directory** | API | `zapier-integration/` pronto pra deploy |
| **n8n Community Nodes** | API | `n8n-nodes/aion-compliance/` pronto pra npm |
| **AppSumo** | Deals | Router + license validation pronto |
| **G2 + Capterra** | Reviews | Guia de perfil pronto |
| **TAAFT + Futurepedia + Toolify** | Diretórios IA | Guia de submissão pronto |
| **Product Hunt** | Lançamento | Estratégia definida (EU AI Act Agent) |

### 8.4 Microsoft Marketplace (Azure)
- **Status:** ❌ **Bloqueado** — `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` não configurados no Render

### 8.5 Salesforce AppExchange
- **Status:** ❌ **Não submetido** — certificados prontos em `marketplace-integration/salesforce/`

### 8.6 Google Cloud Marketplace
- **Status:** ❌ **Bloqueado** — erro no Producer Portal (suporte aberto)
- **Product ID:** `global-engenharia-498823`

### 8.7 Oracle Cloud Marketplace
- **Status:** ⏸ **Pausado** — ativar Q1 2027 com ESG/Carbono

### 8.8 AWS Marketplace
- **Status:** ⏸ **Pausado** — ativar somente com ARR > R$ 3M

### 8.9 Outros Canais / A2A Marketplaces

| Canal | Status | Observação |
|-------|--------|------------|
| **Agentic.Market** (CDP Bazaar) | 🔄 Aguarda 1º USDC payment | x402 v2 implementado, validator ✅ |
| **Prism** | 🔄 Auto-registro ativo | `PRISM_KEY` no Render necessário |
| **Obol Stack** | 🔄 Auto-registro ativo | `OBOL_KEY` no Render necessário |
| **Theoriq** | 🔄 Auto-registro ativo | `THEORIQ_API_KEY` no Render necessário |
| **Virtuals Protocol** | 🔄 Auto-registro ativo | `VIRTUALS_API_KEY` no Render necessário |
| **Nevermined** | 🔄 Auto-registro ativo | `NEVERMINED_API_KEY` no Render necessário |
| **AgentVerse (Fetch.ai)** | 🔄 Fix aplicado — aguarda deploy | `AGENTVERSE_KEY` + `AGENT_SEED_PHRASE` |
| **Bitte Protocol** | 🔄 Parcial | Conectado via AgentVerse. NEAR wallet: `53iUFs9...` |
| **Masa** | 🔄 Auto-registro ativo | `MASA_API_KEY` no Render necessário |
| GPT Store (OpenAI) | ❌ **Não submetido** | `gpt_store_openapi.yaml` pronto — colar em platform.openai.com/gpts |
| Hugging Face Spaces | ❌ **Não submetido** | `huggingface_space/app.py` pronto — upload manual |
| Replit Agent Market | ❌ **Não submetido** | Código pronto |
| MindStudio | ❌ **Não submetido** | Código pronto |
| MuleRun | ✅ **Mantido** | Custo zero, awareness |
| NexusGPT | ✅ **Mantido** | Custo zero, awareness |
| AI Agents Directory | ✅ **Mantido** | Custo zero, awareness |

---

## 9. AUTOMATION JOBS RODANDO 24/7

São **15 jobs** iniciados no `startup_event()` via `asyncio.create_task()`:

| # | Job | Função | Intervalo |
|---|-----|--------|-----------|
| 1 | **Keep-Alive** | Pinga `/api/agentverse/warmup` — evita sleep Render free tier | **10 min** |
| 2 | **SEO-Ecosystem** | ~40 páginas SEO/dia para 5 mercados (BR, US, MX, CO, AR) | 6h |
| 3 | **Dev.to** | 3 artigos/dia no Dev.to | 8h |
| 4 | **SDR-Emails** | Campanhas de 100 emails para 5 setores | 12h |
| 5 | **Press-Release** | Gera press release via Zapier | 7 dias |
| 6 | **Reddit** | Publica conteúdo no Reddit | 48h |
| 7 | **LinkedIn** | Publica conteúdo no LinkedIn | 24h |
| 8 | **Directories** | Submete em diretórios | 72h |
| 9 | **PR-Distribution** | Distribui press releases | 14 dias |
| 10 | **Regtech-Press** | Press releases regtech | 7 dias |
| 11 | **Nurture-Emails** | Sequência de nurture emails | 24h |
| 12 | **Reactivation** | Reativação de leads inativos | 7 dias |
| 13 | **PMOC-SEO** | 70 páginas PMOC em ciclo (bairros/empresas/problemas) | 12h |
| 14 | **Price-Optimizer** | Otimização de preços | 24h |
| 15 | **A2A-Marketplace** | Registro automático nos 9 marketplaces A2A | 7 dias |

---

## 10. VARIÁVEIS DE AMBIENTE

### 10.1 Configuradas no Render ✅

| Variável | Serviço | Status |
|----------|---------|--------|
| `DEEPSEEK_API_KEY` | LLM inference | ✅ |
| `OPENROUTER_API_KEY` | Fallback LLM (Kimi-K2) | ✅ (usuário confirmou) |
| `OPENROUTER_MODEL` | `moonshotai/kimi-k2` | default |
| `SUPABASE_URL` | Database | ✅ |
| `SUPABASE_API_KEY` | Database | ✅ |
| `STRIPE_SECRET_KEY` | Pagamentos (LIVE) | ✅ |
| `STRIPE_WEBHOOK_SECRET` | Webhooks Stripe | ✅ |
| `RESEND_API_KEY` | Outbound email SDR | ✅ |
| `DEVTO_API_KEY` | Content syndication | ✅ |
| `GEMINI_API_KEY` | LLM sensível | ✅ |
| `MERCHANT_WALLET_ADDRESS` | Carteira USDC x402 | ✅ (hardcoded default: `0xadf695...`) |
| `BASE_URL` | URL da API | ✅ |

### 10.2 FALTANDO no Render ❌

| Variável | Serviço | Impacto |
|----------|---------|---------|
| `AGENTVERSE_KEY` | Fetch.ai AgentVerse | Registro do agente no AgentVerse falha |
| `AGENT_SEED_PHRASE` | Fetch.ai uAgents | Identidade do agente AgentVerse |
| `AGENTIC_MARKET_KEY` | Agentic.Market | Registro falha silenciosamente |
| `PRISM_KEY` | Prism marketplace | Registro falha silenciosamente |
| `OBOL_KEY` | Obol Stack | Registro falha silenciosamente |
| `THEORIQ_API_KEY` | Theoriq | Registro falha silenciosamente |
| `VIRTUALS_API_KEY` | Virtuals Protocol | Registro falha silenciosamente |
| `NEVERMINED_API_KEY` | Nevermined | Registro falha silenciosamente |
| `BITTE_API_KEY` | Bitte Protocol | Registro falha silenciosamente |
| `MASA_API_KEY` | Masa | Registro falha silenciosamente |
| `AZURE_TENANT_ID` | Microsoft Marketplace | Assinaturas Azure não ativam |
| `AZURE_CLIENT_ID` | Microsoft Marketplace | Assinaturas Azure não ativam |
| `AZURE_CLIENT_SECRET` | Microsoft Marketplace | Assinaturas Azure não ativam |

---

## 11. PENDÊNCIAS CRÍTICAS

### 🔴 Alta Prioridade (bloqueia receita)

| # | Pendência | O que fazer | Impacto |
|---|-----------|------------|---------|
| 1 | **0 clientes pagantes** | Conseguir 1º cliente | Projeto não gera receita |
| 2 | **Azure credentials faltando** | Criar App Registration no Azure Portal → adicionar `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` no Render | Microsoft Marketplace bloqueado |
| 3 | **Stripe prices faltando** | Criar `tech_starter`, `tech_professional`, `tech_enterprise` no Stripe Dashboard | 3 planos não funcionam |
| 4 | **Primeiro pagamento USDC** | Fazer 1 transação real (verify+settle) via CDP → Agentic.Market indexa automaticamente | Visibilidade em todos os marketplaces A2A |
| 5 | **Google Workspace Add-on rejeitado** | Completar OAuth verification para escopos Gmail | Add-on não publicado |
| 6 | **DNS verification Google Search Console** | Verificar domínio `global-engenharia.com` | SEO e Add-on bloqueados |

### 🟡 Média Prioridade

| # | Pendência | O que fazer |
|---|-----------|------------|
| 7 | **Keys de marketplace A2A** | Adicionar as 8 API keys faltantes ao Render (ver seção 10.2) |
| 8 | **GPT Store** | Colar `gpt_store_openapi.yaml` em platform.openai.com/gpts |
| 9 | **Hugging Face Space** | Upload manual de `huggingface_space/app.py` + `requirements.txt` |
| 10 | **vendas.html deploy** | Fazer upload da versão atualizada (visitor tracking + multi-currency + pay-per-use) no Netlify |
| 11 | **Bitte.ai** | Completar registro do agente com NEAR wallet `53iUFs9...` |
| 12 | **AgentVerse teste automático** | Verificar se "Couldn't send message" foi resolvido após deploy do fix de timeout |
| 13 | **Office Add-in** | Finalizar submissão no Partner Center |
| 14 | **Salesforce AppExchange** | Submeter listing (certificados prontos em `marketplace-integration/salesforce/`) |
| 15 | **Google Cloud Marketplace** | Resolver erro no Producer Portal (suporte aberto) |
| 16 | **Stripe prices LATAM** | Criar prices em MXN, COP para mercados México e Colômbia |
| 17 | **G2/Capterra profiles** | Criar perfis gratuitos — geram leads B2B orgânicos |

### 🟢 Baixa Prioridade

| # | Pendência | Detalhes |
|---|-----------|----------|
| 18 | Replit + MindStudio | Código pronto, falta submissão |
| 19 | AWS Marketplace | Pausado — ativar só com ARR > R$ 3M |
| 20 | Oracle Marketplace | Pausado — ativar Q1 2027 |
| 21 | Hetzner deployment | Script pronto (`deploy/hetzner-setup.sh`) — criar servidor CX31 (€12/mês) |
| 22 | Docker local | Instalar Docker para testar `docker-compose.yml` localmente |

---

## 12. ENDPOINTS DA API

### 12.1 Core

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/` | Status + total de agentes |
| GET | `/docs` | Swagger UI |
| POST | `/api/agents/execute` | Executa tarefa em agente |
| GET | `/api/tasks/{task_id}` | Poll de status |
| GET | `/api/agents/health` | Health check de todos |
| GET | `/.well-known/agent-card.json` | Agent Card A2A (10 skills) |

### 12.2 Compliance (API direta — sem x402)

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `/api/eu-ai-act/readiness-check` | EU AI Act |
| POST | `/api/lfpdppp/diagnostico` | México LFPDPPP |
| POST | `/api/ley1581/diagnostico` | Colômbia Ley 1581 |
| POST | `/api/csrd/assessment` | CSRD |
| POST | `/api/dora/assessment` | DORA |
| POST | `/api/vendor-risk/assessment` | Vendor Risk |
| POST | `/api/contract-risk/analysis` | Contract Risk |
| POST | `/api/ma-diligence/check` | M&A Due Diligence |

### 12.3 A2A Marketplace e AgentVerse (NOVOS)

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/api/marketplace/execute/{service_id}` | Retorna 402 com PAYMENT-REQUIRED header |
| POST | `/api/marketplace/execute/{service_id}` | Verifica pagamento x402 e executa |
| GET | `/api/marketplace/services` | Lista serviços e preços USDC |
| GET | `/api/marketplace/health` | Health check marketplace |
| POST | `/api/agentverse/messages` | Recebe mensagens uAgents do AgentVerse |
| GET | `/api/agentverse/messages` | Info do agente AgentVerse |
| GET | `/api/agentverse/warmup` | Keep-alive (previne cold start) |

### 12.4 Vendas e Marketing

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `/api/sales-agent/chat` | Chat multi-mercado |
| POST | `/api/visitor-id/track` | Tracking de visitante por IP |
| POST | `/api/usage/pay-per-use/{market}/{agent_id}` | Pagamento pay-per-use |
| POST | `/api/seo/generate/{market}` | Gera páginas SEO |

### 12.5 MCP e A2A

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/mcp/servers` | Lista servidores MCP |
| GET | `/mcp/toolspec.json` | Tool specification |
| POST | `/a2a/jsonrpc` | JSON-RPC A2A |
| GET | `/a2a/rest` | REST A2A |

---

## 13. CONFIGURAÇÕES DE SEGURANÇA

### 13.1 Chaves Expostas no `.env` Local (⚠️ CRÍTICO — NÃO commitar)

| Chave | Risco |
|-------|-------|
| `STRIPE_SECRET_KEY` = `sk_live_51Tkpu...` | 🔴⬆️ CRÍTICO — chave LIVE de produção |
| `STRIPE_WEBHOOK_SECRET` = `whsec_lh0FM0...` | 🔴 Webhook spoofing |
| `SUPABASE_API_KEY` / `SUPABASE_SERVICE_KEY` | 🔴 Acesso total ao banco |
| `DEEPSEEK_API_KEY` / `OPENROUTER_API_KEY` | 🔴 Abuso de API |
| `GEMINI_API_KEY` | 🔴 Uso não autorizado |
| `GOOGLE_CLIENT_SECRET` = `GOCSPX-qt1M...` | 🔴 OAuth compromise |

> ⚠️ O `.env` **NÃO** está no git (`.gitignore`). Chaves ficam apenas no Render e no arquivo local. Rotacionar se houver suspeita de vazamento.

### 13.2 `k8s/secrets.yaml`
- Hardcoded secrets removidos — arquivo com `""` vazio
- External Secrets Operator não configurado

---

## 14. TESTES

| Arquivo | Status |
|---------|--------|
| `test_sallesjam_agents.py` | ✅ 15/15 passando |
| `test_orchestrator.py` | ✅ Passando |
| `test_plans.py` | ✅ Passando |
| Total reportado em AGENTS.md | ✅ 75/75 |

> ⚠️ Alguns testes exigem env vars (`DEEPSEEK_API_KEY`, `SUPABASE_URL`) para passar localmente.

---

## 15. HISTÓRICO DE COMMITS RECENTES

| Commit | Mensagem | Data |
|--------|----------|------|
| `a77ca5f` | fix: resolve AgentVerse timeout by removing LLM from message handler | 01/07/2026 |
| `4707e93` | [commit anterior] | 01/07/2026 |

---

## 16. O QUE FOI IMPLEMENTADO NESTA SESSÃO (01/07 — tarde)

### ✅ Concluído

1. **x402 v2 HTTP Payment Protocol** (`src/agents/agent_marketplace.py`)
   - Endpoint GET retorna HTTP 402 com header `PAYMENT-REQUIRED` em base64
   - Envelope `{x402Version:2, accepts:[], resource:{}, extensions:{bazaar:{schema:...}}}`
   - Facilitador: `https://api.cdp.coinbase.com/platform/v2/x402/facilitator`
   - **Validator status: "Implementation Looks Correct / All checks pass" ✅**

2. **9 Marketplace Registrations** (`auto_job_marketplace_registration`)
   - Agentic.Market, Prism, Obol, Theoriq, Virtuals, Nevermined, AgentVerse, Bitte, Masa
   - Roda automaticamente a cada 7 dias

3. **AgentVerse Handler** (`src/agents/agentverse_handler.py`)
   - POST `/api/agentverse/messages` — recebe mensagens uAgents
   - **Bug corrigido:** timeout (LLM 30-60s vs AgentVerse ~10s) → templates pré-construídos em <1ms
   - Parsing robusto: aceita payload como dict, JSON string, ou base64
   - Extrai empresa/setor/AI systems do texto livre via regex
   - Retorna no formato Chat Protocol: `{type: "agent_message", content: [{type: "text", text: "..."}]}`

4. **OpenRouter Fallback** (`src/api/deepseek_client.py`)
   - Se DeepSeek falha → fallback automático para Kimi-K2 via `openrouter.ai/api/v1`
   - Configura headers `HTTP-Referer` e `X-Title` obrigatórios

5. **Keep-Alive Job** (`app/main.py`)
   - Pinga `/api/agentverse/warmup` a cada 10 minutos
   - Previne cold start do Render free tier (que causava o "Couldn't send message")

6. **GPT Store OpenAPI Schema** (`gpt_store_openapi.yaml`)
   - 4 paths: NR-1, LGPD, EU AI Act, CSRD
   - Pronto para colar em platform.openai.com/gpts

7. **Hugging Face Space** (`huggingface_space/app.py`)
   - Interface Gradio com 4 tabs (NR-1, LGPD, EU AI Act, CSRD)
   - Chama API do Render e exibe resultados

8. **vendas.html atualizada** (`global-match-site/vendas.html`)
   - Visitor tracking → POST `/api/visitor-id/track`
   - Multi-currency (7 países via ipapi.co)
   - Seção pay-per-use com 4 cards e função `payPerUse(agentId)`

### 🔄 Em Andamento

- **AgentVerse teste automático** — fix commitado e pusheado (`a77ca5f`), aguardando Render redeploy (~2-3 min). Após deploy, testar na plataforma AgentVerse.

### ❌ Ainda Pendente

- Adicionar API keys dos marketplaces ao Render (ver seção 10.2)
- Fazer 1º pagamento USDC para ativar CDP Bazaar indexing
- Upload do Hugging Face Space
- Submissão no GPT Store
- Deploy do vendas.html no Netlify
- Completar Bitte.ai com NEAR wallet
- Azure credentials para Microsoft Marketplace

---

## 17. RESUMO EXECUTIVO

### O que funciona ✅
- API em produção no Render com 59 agentes ativos (15 jobs 24/7)
- Chrome Extension publicada no Chrome Web Store
- Sistema de planos e preços no Stripe (12+ planos BRL + USD)
- Chat multi-mercado (BR, US, MX, CO, AR)
- SEO programático (~290 páginas geradas automaticamente)
- Protocolo A2A configurado com 10 skills no agent card
- x402 v2 implementado e validado ✅
- OpenRouter fallback para quando DeepSeek cai
- 9 marketplaces A2A com registro automático
- AgentVerse handler com timeout fixado

### O que NÃO funciona / está pendente ❌
- **0 clientes pagantes** — sem receita
- Google Workspace Add-on rejeitado
- Office Add-in em submissão
- Azure credentials faltando (Microsoft Marketplace bloqueado)
- Stripe prices faltando para tech plans e LATAM
- Marketplaces A2A dependem de API keys que ainda precisam ser adicionadas ao Render
- CDP Bazaar não indexa até o primeiro pagamento USDC real
- Nenhum marketplace enterprise submetido (Salesforce, Google Cloud)

### Próximos 3 passos mais impactantes
1. 🔴 **Adicionar keys dos marketplaces** ao Render e configurar `AZURE_TENANT_ID/CLIENT_ID/SECRET`
2. 🔴 **Fazer 1 pagamento USDC** para ativar CDP Bazaar (Agentic.Market aparece no buscador)
3. 🟡 **Submeter GPT Store + Hugging Face** (código pronto — só falta colar/upload)

---

*Documento atualizado em 01/07/2026 — Sessão 2 (tarde)*
*Commit atual: `a77ca5f` no branch `main`*
