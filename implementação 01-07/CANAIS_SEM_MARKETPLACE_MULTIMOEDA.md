# AION — Canais 100% Automatizados (Sem Marketplace)
**Global Match Engenharia de Produção | Cristiano Arruda**
**Data:** 2026-06-24
**Critério:** apenas canais que NÃO dependem de aprovação de terceiro — Microsoft, Google, Salesforce, Oracle e SAP excluídos
**Moedas:** BRL, USD, EUR — multi-moeda real, sem spread bancário

---

## OS 9 CANAIS — TODOS SOB SEU CONTROLE TOTAL

| # | Canal | Moeda | Como gera receita | Status |
|---|-------|-------|-------------------|--------|
| 1 | Stripe direto + Site | BRL/USD/EUR | Link de checkout, cliente paga na hora | ✅ Ativo |
| 2 | SEO Programático (180 páginas) | BRL/USD | Google indexa, tráfego orgânico grátis | 🔧 Implementar |
| 3 | Visitor ID + Sales Agent | BRL/USD | Identifica empresa, agente vende sozinho | 🔧 Implementar |
| 4 | Pay-per-use (Stripe Usage) | USD | Cobra por uso, sem assinatura | 🔧 Implementar |
| 5 | Replit Agent Market | USD | Venda direta na plataforma | ✅ Publicado |
| 6 | MindStudio | USD | Tiers de assinatura nativos | ✅ Publicado |
| 7 | MCP Servers (Claude/Copilot/Gemini) | USD | Billing por chamada de ferramenta | ✅ No ar |
| 8 | GPT Store | USD | Revenue share via Stripe Connect | 🔧 Implementar |
| 9 | Hugging Face Spaces | USD | Doação/Pro tier | 🔧 Implementar |

**Nenhum desses canais espera aprovação de Microsoft, Google, Salesforce, Oracle ou SAP.**

---

## PARTE 1 — INFRAESTRUTURA FINANCEIRA MULTI-MOEDA

### 1.1 Wise Business — a peça central

```
PROBLEMA: Stripe converte automaticamente USD/EUR → BRL
          com spread de 3-6% sem você perceber

SOLUÇÃO: Conta Wise Business recebe na moeda original
         Você decide quando e como converter
```

**Setup (10 minutos):**
```
1. wise.com/business → criar conta
2. CNPJ Global Match Engenharia de Produção
3. Solicitar conta USD (número americano local)
4. Solicitar conta EUR (IBAN europeu)
5. Solicitar conta GBP (opcional — Reino Unido)
```

### 1.2 Configurar Stripe para multi-moeda real

```python
# src/config/stripe_payout_config.py
"""
Configuração de payout multi-moeda no Stripe.
Cada moeda pousa na conta Wise correspondente — sem conversão forçada.
"""

PAYOUT_CONFIG = {
    "BRL": {
        "destination": "conta_bancaria_brasil",
        "schedule": "daily"
    },
    "USD": {
        "destination": "wise_business_usd_account",
        "schedule": "weekly"
    },
    "EUR": {
        "destination": "wise_business_eur_account",
        "schedule": "weekly"
    }
}
```

**No Stripe Dashboard:**
```
Settings → Payouts → Add bank account
→ Adicionar conta Wise USD
→ Adicionar conta Wise EUR
→ Settings → Payout currency → Manter moeda original (não converter automaticamente)
```

### 1.3 Preços já em multi-moeda — atualizar Stripe

```python
# Cada plano precisa ter price_id separado por moeda
# Stripe permite múltiplas moedas no mesmo produto

STRIPE_PRICES = {
    "compliance_essencial": {
        "BRL": "price_brl_590",
        "USD": "price_usd_149",
        "EUR": "price_eur_139"
    },
    "regulatory_pro": {
        "BRL": "price_brl_1490",
        "USD": "price_usd_379",
        "EUR": "price_eur_349"
    }
}
```

---

## PARTE 2 — CANAL 1: STRIPE DIRETO MULTI-MOEDA (já ativo, otimizar)

### O que fazer agora
```python
# app/routers/checkout.py — adicionar detecção de moeda automática

@router.get("/checkout/{plan_id}")
async def get_checkout_link(plan_id: str, request: Request):
    """
    Detecta país do visitante via IP e retorna o link
    de checkout na moeda correta automaticamente.
    """
    country = await detect_country_from_ip(request.client.host)

    currency_map = {
        "BR": "BRL", "US": "USD", "PT": "EUR",
        "DE": "EUR", "FR": "EUR", "ES": "EUR",
        "GB": "GBP"
    }
    currency = currency_map.get(country, "USD")  # default USD

    price_id = STRIPE_PRICES[plan_id][currency]
    checkout_url = f"https://buy.stripe.com/{price_id}"

    return {"checkout_url": checkout_url, "currency": currency}
```

**No site:** o link de "Começar agora" já direciona automaticamente para a moeda certa baseado em quem está visitando.

---

## PARTE 3 — CANAL 2: SEO PROGRAMÁTICO MULTI-IDIOMA

### Expandir as 180 páginas para inglês e espanhol

```python
# src/agents/seo_content_agent.py — adicionar idiomas

IDIOMAS = {
    "pt-BR": {
        "normas": ["nr1-psicossocial", "lgpd-operacional", "cbs-ibs"],
        "moeda": "BRL"
    },
    "en-US": {
        "normas": ["data-privacy-compliance", "esg-reporting", "carbon-inventory"],
        "moeda": "USD"
    },
    "es": {
        "normas": ["proteccion-datos", "cumplimiento-laboral"],
        "moeda": "USD"
    }
}

# Gera páginas em inglês focadas em mercado internacional:
# /en/esg-ifrs-manufacturing-smb
# /en/carbon-inventory-export-eu (CBAM!)
# /en/data-privacy-compliance-startup
```

**Por que isso importa:** as páginas em inglês sobre ESG, Carbono e CBAM capturam buscas de empresas que exportam para a UE — esse é tráfego que já vem qualificado para pagar em USD/EUR.

---

## PARTE 4 — CANAL 3: VISITOR ID GLOBAL

### Identificar visitante de qualquer país

```python
# src/agents/visitor_id_agent.py — adicionar suporte internacional

class VisitorIDAgent:

    async def identify_visitor(self, ip: str, page_visited: str) -> dict:
        country = await self._get_country(ip)

        if country == "BR":
            company_data = await self._enrich_cnpj_brasil(ip)
        elif country in ["US", "CA"]:
            company_data = await self._enrich_clearbit(ip)  # API internacional
        elif country in ["DE", "FR", "ES", "PT", "IT"]:
            company_data = await self._enrich_eu_vat(ip)  # Base VAT europeia

        # Sales Agent contata na moeda e idioma certo
        await self._trigger_sales_agent(company_data, country)
```

### Enriquecimento internacional gratuito

```python
async def _enrich_clearbit(self, ip: str) -> dict:
    """Clearbit Reveal API - free tier disponível para identificar empresa por IP"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://reveal.clearbit.com/v1/companies/find?ip={ip}",
            headers={"Authorization": f"Bearer {os.getenv('CLEARBIT_KEY')}"}
        )
    return resp.json()
```

---

## PARTE 5 — CANAL 4: PAY-PER-USE GLOBAL (Stripe Usage-Based)

```python
# src/agents/usage_billing.py — NOVO
"""
Cobrança por uso via Stripe Meters — funciona em qualquer moeda.
Ideal para captar mercado internacional que não quer assinatura.
"""
import stripe

class UsageBillingAgent:

    PRICING_PER_USE = {
        "nr1_diagnostico": {"USD": 5.00, "EUR": 4.60, "BRL": 19.90},
        "lgpd_scan": {"USD": 8.00, "EUR": 7.40, "BRL": 29.90},
        "esg_diagnostic": {"USD": 15.00, "EUR": 13.80, "BRL": 59.90},
        "carbon_calculation": {"USD": 12.00, "EUR": 11.10, "BRL": 49.90},
    }

    async def record_usage(
        self, customer_id: str, agent_used: str, currency: str = "USD"
    ):
        """Registra uso e cobra automaticamente via Stripe Meters."""
        stripe.billing.MeterEvent.create(
            event_name=f"agent_usage_{agent_used}",
            payload={
                "stripe_customer_id": customer_id,
                "value": "1"
            }
        )

    async def create_usage_price(self, agent_id: str, currency: str):
        """Cria price de pay-per-use no Stripe para um agente específico."""
        price = stripe.Price.create(
            product=f"prod_{agent_id}",
            currency=currency.lower(),
            billing_scheme="per_unit",
            unit_amount=int(self.PRICING_PER_USE[agent_id][currency] * 100),
            recurring={
                "usage_type": "metered",
                "interval": "month"
            }
        )
        return price.id
```

**Setup no Stripe Dashboard:**
```
1. Products → Create meter
2. Nome: "agent_usage_nr1_diagnostico"
3. Aggregation: Sum
4. Price: USD 5.00 por unidade
5. Repetir para cada agente disponível em pay-per-use
```

---

## PARTE 6 — CANAL 5–6: REPLIT E MINDSTUDIO (já publicados, otimizar moeda)

### Confirmar billing em USD nativo
```
Replit: já cobra nativamente em USD — nada a fazer
MindStudio: já cobra nativamente em USD — confirmar tiers ativos
```

### Adicionar mais 3 micro-agentes em inglês para Replit/MindStudio
```
1. "ESG Compliance Score" — USD 29/mês
2. "Carbon Footprint Calculator" — USD 39/mês
3. "CBAM Export Checker" — USD 49/mês (foco exportadores para UE)
```

Esses 3 capturam diretamente o público internacional que já está nessas plataformas.

---

## PARTE 7 — CANAL 7: MCP SERVERS (já no ar, ativar billing)

```python
# src/mcp/base_server.py — adicionar billing multi-moeda

async def bill_usage(self, tenant_id: str, agent_id: str, tokens_used: int):
    """
    Detecta moeda do tenant e cobra via Stripe Meters.
    """
    tenant = await self.db.get_tenant(tenant_id)
    currency = tenant.get("currency", "USD")

    cost_per_1k_tokens = {
        "USD": 0.002,
        "EUR": 0.0019,
        "BRL": 0.008
    }

    cost = (tokens_used / 1000) * cost_per_1k_tokens[currency]
    await self._charge_stripe_meter(tenant_id, cost, currency)
```

---

## PARTE 8 — CANAL 8: GPT STORE

### Por que publicar
GPT Store fica dentro do ChatGPT — maior base de usuários de IA do mundo. Paga revenue share automaticamente via Stripe Connect, sem você gerenciar cobrança.

### Como publicar
```
1. platform.openai.com/gpts
2. Create a GPT
3. Nome: "NR-1 & LGPD Compliance Assistant"
4. Conectar Actions → seu endpoint MCP regulatory
5. Conectar Stripe Connect para monetização
6. Submit for review (editorial, 3-7 dias)
```

### Conectar suas Actions ao endpoint existente
```yaml
# openapi schema para o GPT Actions
openapi: 3.0.0
info:
  title: EcoSystem Compliance API
servers:
  - url: https://engenheiro-producao-ai.onrender.com
paths:
  /mcp/regulatory/tools/nr1_psicossocial:
    post:
      operationId: generateNR1Inventory
      summary: Gera inventário NR-1 Psicossocial
```

---

## PARTE 9 — CANAL 9: HUGGING FACE SPACES

### Por que publicar
5 milhões de desenvolvedores, comunidade global, zero review central — publica e já está visível.

### Como publicar
```
1. huggingface.co/new-space
2. SDK: Gradio (mais simples) ou Docker (usa seu FastAPI)
3. Nome: "ecosystem-compliance-brasil"
4. Conectar ao seu endpoint Render via API
5. Adicionar botão de doação/Pro tier
```

```python
# app.py para Hugging Face Space
import gradio as gr
import requests

def diagnostico_nr1(empresa, cnpj, funcionarios):
    resp = requests.post(
        "https://engenheiro-producao-ai.onrender.com/mcp/regulatory/tools/nr1_psicossocial",
        json={"empresa": empresa, "cnpj": cnpj, "num_funcionarios": funcionarios}
    )
    return resp.json()

demo = gr.Interface(
    fn=diagnostico_nr1,
    inputs=["text", "text", "number"],
    outputs="json",
    title="EcoSystem — Diagnóstico NR-1 Psicossocial",
    description="Gere seu inventário FRPRT em segundos. Plano completo: global-engenharia.com/ecosystem"
)
demo.launch()
```

---

## RESUMO — PROJEÇÃO SÓ DOS 9 CANAIS SEM MARKETPLACE

| Canal | MRR mês 3 | MRR mês 6 | MRR mês 12 |
|-------|-----------|-----------|------------|
| Stripe direto multi-moeda | R$ 8.500 | R$ 24.000 | R$ 68.000 |
| SEO Programático (180+ pág, 3 idiomas) | R$ 6.200 | R$ 31.000 | R$ 89.000 |
| Visitor ID + Sales Agent | R$ 4.800 | R$ 18.500 | R$ 52.000 |
| Pay-per-use | R$ 1.200 | R$ 5.800 | R$ 16.500 |
| Replit + MindStudio | R$ 3.400 | R$ 9.200 | R$ 22.000 |
| MCP Servers billing | R$ 1.800 | R$ 7.400 | R$ 24.000 |
| GPT Store | R$ 900 | R$ 4.200 | R$ 14.500 |
| Hugging Face Spaces | R$ 400 | R$ 1.800 | R$ 5.200 |
| **TOTAL MRR** | **R$ 27.200** | **R$ 101.900** | **R$ 291.200** |
| **ARR equivalente** | — | — | **R$ 3,49M** |

---

## CHECKLIST DE IMPLEMENTAÇÃO — ORDEM EXATA

### Semana 1 — Infraestrutura financeira
- [ ] Abrir conta Wise Business (USD + EUR)
- [ ] Configurar payout multi-moeda no Stripe
- [ ] Criar price_ids em BRL/USD/EUR para os planos principais

### Semana 2 — Canais que já existem, otimizar
- [ ] Adicionar detecção de país/moeda no checkout do site
- [ ] Confirmar billing ativo no Replit e MindStudio
- [ ] Ativar billing nos MCP servers (Stripe Meters)

### Semana 3 — Pay-per-use
- [ ] Criar Stripe Meters para 4 agentes principais
- [ ] Implementar `usage_billing.py`
- [ ] Testar cobrança por uso end-to-end

### Semana 4 — Expansão internacional
- [ ] Traduzir 20 páginas SEO para inglês (foco ESG/Carbono/CBAM)
- [ ] Publicar GPT na GPT Store
- [ ] Publicar Space no Hugging Face
- [ ] Conectar Clearbit para identificação internacional de visitantes

---

*Documento gerado em 2026-06-24 — apenas canais sem dependência de marketplace*
*Implementar com DeepSeek seguindo as 4 semanas*
*Revisão: validar Wise Business e price_ids multi-moeda antes de publicar GPT Store*
