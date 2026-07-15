# Estratégias de Visibilidade Global Automatizável — AION / EcoSystem AEC

## 1. Diretórios B2B Globais (submissão automatizada)

| Plataforma | URL | API/Automação | Custo |
|---|---|---|---|
| **G2** (+ Capterra/GetApp) | g2.com | Formulário vendor; review API após aprovação | Free listing |
| **Product Hunt** | producthunt.com | **API REST OAuth2** — `api.producthunt.com/v2` | Gratuito |
| **SourceForge** | sourceforge.net | Form self-serve via `requests` | Gratuito |
| **AlternativeTo** | alternativeto.net | API pública para embed | Gratuito |
| **Crozdesk** | crozdesk.com | API JSON de parceiros documentada | Gratuito |
| **SaaSHub** | saashub.com | POST via `httpx` | Gratuito |

## 2. Programas de Afiliados/Parceiros (comissão recorrente)

| Programa | Comissão | Como Automatizar |
|---|---|---|
| **Deel Partner** | 20% recorrente 12 meses | Impact.com API |
| **Vanta Affiliate** | $500–$2.000/cliente | Impact.com API |
| **Secureframe Partner** | ~20% recorrente | Formulário + webhook |
| **Impact.com** (rede central) | Variável | **API REST completa** — tracking + payouts |

## 3. Press Release por Email (automação Resend)

| Publicação | Email |
|---|---|
| FinTech Global | news@fintech.global |
| A-Team Insight | editorial@a-teaminsight.com |
| RegTech Analyst | press@regtechanalyst.com |
| Compliance Week | newsroom@complianceweek.com |
| ACAMS Today | editor@acams.org |
| **JD Supra** | **API REST** — upload automatizado de artigos |

## 4. Distribuição de Press Release (API)

| Serviço | API | Custo |
|---|---|---|
| **EIN Presswire** | REST API documentada | $66/release (pacote 15) |
| **PRWeb (Cision)** | API com token | $110/release |
| **PRLog** | API XML | **Gratuito** |
| **OpenPR** | Form POST automatizável | **Gratuito** |

## 5. Comunidades Reddit/LinkedIn/Discord

| Comunidade | Plataforma | Automação |
|---|---|---|
| r/compliance | Reddit | `praw` — posts semanais |
| r/legalops | Reddit | `praw` — conteúdo educativo |
| r/RegTech | Reddit | `praw` — monitorar + responder |
| Compliance Officers (500k+) | LinkedIn Group | LinkedIn API |
| CLOC Legal Ops | LinkedIn/Slack | Email membership |
| RegTech Rising | Discord | `discord.py` bot |

## Prioridade de Implementação

1. EIN Presswire API + G2/Capterra/SourceForge (submissão gratuita) ← **já implementado**
2. Reddit Bot (`praw`) — r/compliance, r/legalops, r/RegTech  ← **já implementado**
3. Impact.com para centralizar afiliados (Deel, Vanta, Secureframe) ← pendente
4. JD Supra API para artigos + lista press release email ← **já implementado**
5. Product Hunt launch via API + LinkedIn scheduling ← **já implementado** (falta o launch manual em si)

**Ainda faltam do plano original:** Crozdesk, Impact.com, PRLog, Discord bot, grupos LinkedIn
(Compliance Officers 500k+, CLOC Legal Ops) — baixo esforço, podem ser adicionados ao
`directory_submission_agent.py` a qualquer momento.

---

## 6. ADENDO — Canais Novos para 2026 (não cobertos na pesquisa original)

A pesquisa original é forte em SEO/PR clássico (2020-2023). Para "conhecida mundialmente"
em 2026 faltam os canais onde descoberta acontece agora: motores de resposta de IA e
o próprio ecossistema agent-to-agent que a AION já está integrando.

### 6.1 `llms.txt` — descoberta por IA (maior alavancagem, custo zero) 🔴

Padrão emergente (llmstxt.org) onde ChatGPT, Perplexity, Claude e Gemini leem um arquivo
`/llms.txt` na raiz do site para entender do que a empresa trata antes de citá-la em respostas.
A AION já gera ~290 páginas de SEO programático mas **nenhuma otimização para motores de
resposta de IA** (GEO — Generative Engine Optimization, sucessor do SEO tradicional).
Sem isso, quando alguém pergunta "qual o melhor agente de IA para compliance NR-1" no
ChatGPT/Perplexity, a AION não aparece.

- Criar `global-engenharia.com/llms.txt` com descrição, lista de agentes, preços, links
- Adicionar `schema.org/SoftwareApplication` com `aggregateRating` nas páginas de vendas
- Formato markdown simples, gerável automaticamente a partir do `config.yaml` existente

### 6.2 Registries MCP (Model Context Protocol) — tráfego de desenvolvedores 🔴

A AION já expõe 4 servidores MCP (`regulatory`, `esg`, `erp`, `microsoft`) mas não está
listada em nenhum diretório MCP. Esses diretórios são o "Product Hunt dos agentes" em 2026:

| Diretório | URL | Tipo |
|---|---|---|
| MCP oficial (Anthropic) | modelcontextprotocol.io/registry | PR no GitHub |
| Smithery | smithery.ai | Submit form |
| Glama | glama.ai/mcp/servers | API |
| PulseMCP | pulsemcp.com | Submit form |
| mcp.so | mcp.so | Submit form |

### 6.3 Diretórios regionais dos mercados já codificados 🟡

A pesquisa original é genérica EUA/Europa. A AION já tem agentes prontos para Índia, UAE
e LATAM (`india_multilingual_agent.py`, `uae_government_agent.py`) mas **zero listagem
regional** nesses mercados:

| Região | Diretório | Observação |
|---|---|---|
| Índia | Tracxn, Inc42 Startup Directory | Alto tráfego de compradores B2B locais |
| UAE/MENA | MAGNiTT, Dubai Chamber Startup Directory | Cobre o agente UAE já existente |
| Europa | EU-Startups.com database | Cobre CSRD/DORA/NIS2 já existentes |
| LATAM | LatamList | Cobre MX/CO/AR já existentes |

### 6.4 Cross-promoção no próprio ecossistema A2A 🟡

A AION acabou de implementar x402 + registro em 9 marketplaces A2A (Agentic.Market,
AgentVerse, Bitte, Virtuals Protocol etc.). Isso é, em si, uma história de PR inédita:
**"primeiro agente de compliance com pagamentos x402 ao vivo em produção"**. Nenhum
concorrente de compliance/RegTech está nesse estágio ainda — vale um press release
específico sobre isso (RegTech + Web3/A2A é um ângulo que nenhuma publicação da lista
original cobriria por padrão).

### 6.5 Presença em vídeo — ❌ descartado

Canal descartado — usuário optou por não produzir vídeo. Não sugerir roteiros/vídeo
neste projeto.

### 6.6 Perfis de legitimidade institucional 🟢

Crunchbase e Wellfound (AngelList) — perfis gratuitos que aparecem no Knowledge Panel do
Google e são usados como fonte por LLMs ao responderem "o que é a AION/EcoSystem AEC".
Não requer API, só cadastro manual único.

### Prioridade do adendo

1. 🔴 `llms.txt` — maior impacto, menor esforço, zero dependência de terceiros
2. 🔴 Registries MCP — tráfego de devs já qualificado para os MCP servers existentes
3. 🟡 Press release "primeiro agente RegTech com x402 em produção" — ângulo inédito
4. 🟡 Diretórios regionais (Índia/UAE/LATAM/EU) — mercados já codificados, zero listagem
5. 🟢 Vídeo + Crunchbase/Wellfound — alcance incremental, baixo esforço
