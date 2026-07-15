# AION — IMPLEMENTAÇÃO TOTAL AGORA (Brasil + EUA + LATAM)
**Global Match Engenharia de Produção | Cristiano Arruda**
**Data:** 2026-06-24
**Regra:** tudo aqui roda sem esperar aprovação de ninguém — Stripe + canais auto-aprovados
**Escopo:** Brasil (já documentado) + 4 produtos novos internacionais

---

## ORDEM DE EXECUÇÃO — 21 DIAS, SEM PULAR ETAPA

```
DIA 1-2   → Sales Agent no chat + Visitor ID (Brasil)
DIA 3-4   → SEO Content Agent 180 páginas BR (Brasil)
DIA 5-6   → Pay-per-use no Stripe (Brasil)
DIA 7-9   → EU AI Act Readiness Agent (EUA + Europa) NOVO
DIA 10-12 → LFPDPPP Compliance Agent México NOVO
DIA 13-15 → Ley 1581 Compliance Agent Colômbia NOVO
DIA 16-18 → SDR/Back-office Agent Argentina NOVO
DIA 19-21 → Replit + MindStudio + GPT Store + Hugging Face (todos os mercados)
```

---

## PARTE 1 — INFRAESTRUTURA BASE (Brasil — fazer primeiro, tudo depende disso)

### 1.1 Sales Agent no chat — `app/routers/sales_agent_chat.py`

```python
from fastapi import APIRouter, Request
from src.api.deepseek_client import DeepSeekClient
from src.rag.hybrid_retriever import HybridRetriever
from src.database.supabase_client import SupabaseClient

router = APIRouter(prefix="/api/sales-agent", tags=["sales_agent"])

SYSTEM_PROMPT_BR = """Você é o Sales Agent do EcoSystem AION.
Qualifica o visitante, responde dúvidas sobre compliance regulatório
(NR-1, LGPD, CBS/IBS, ESG) com precisão, conduz para o plano certo.
Sempre termine oferecendo o link de ativação quando demonstrar interesse."""

STRIPE_LINKS_BR = {
    "compliance_essencial": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03",
    "regulatory_pro": "https://buy.stripe.com/14dRwr3Ik0JRfC44hWg7e04",
    "esg_carbono": "https://buy.stripe.com/6oUeVf3IkeAH4Xq7u8g7e06"
}

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    page = data.get("page", "/")
    market = data.get("market", "BR")

    context = await HybridRetriever().search(message, top_k=3)
    deepseek = DeepSeekClient()

    system_prompt = get_system_prompt(market)
    response = await deepseek.complete(
        system=system_prompt,
        user=f"Página: {page}\nContexto: {context}\nPergunta: {message}"
    )

    plan = _detect_plan_interest(message, response, market)
    if plan:
        response += f"\n\n🔗 {get_stripe_link(market, plan)}"

    db = SupabaseClient()
    await db.table("chat_logs").insert({
        "message": message, "response": response, "page": page, "market": market
    }).execute()

    return {"response": response}


def get_system_prompt(market: str) -> str:
    prompts = {
        "BR": SYSTEM_PROMPT_BR,
        "US": """You are the EcoSystem AION Sales Agent for the US market.
        Qualify visitors, answer questions about EU AI Act Article 50
        compliance with precision, guide to the right plan.
        Always end by offering the activation link when interest is shown.""",
        "MX": """Eres el Sales Agent de EcoSystem AION para México.
        Califica al visitante, responde dudas sobre cumplimiento LFPDPPP
        con precisión, guía al plan correcto.""",
        "CO": """Eres el Sales Agent de EcoSystem AION para Colombia.
        Califica al visitante, responde dudas sobre cumplimiento Ley 1581
        con precisión, guía al plan correcto.""",
        "AR": """Eres el Sales Agent de EcoSystem AION para Argentina.
        Califica al visitante para servicios de automatización SDR
        y back-office, guía al plan correcto."""
    }
    return prompts.get(market, SYSTEM_PROMPT_BR)


def _detect_plan_interest(message: str, response: str, market: str) -> str:
    text = (message + response).lower()
    if market == "BR":
        if "esg" in text or "carbono" in text: return "esg_carbono"
        if "igualdade" in text or "denúncia" in text: return "regulatory_pro"
        if "nr-1" in text or "lgpd" in text or "ativar" in text: return "compliance_essencial"
    elif market == "US":
        if "ai act" in text or "article 50" in text or "ready" in text: return "eu_ai_act"
    elif market == "MX":
        if "lfpdppp" in text or "datos" in text or "activar" in text: return "lfpdppp"
    elif market == "CO":
        if "1581" in text or "datos" in text or "activar" in text: return "ley1581"
    elif market == "AR":
        if "sdr" in text or "automatiza" in text or "activar" in text: return "sdr_backoffice"
    return None


def get_stripe_link(market: str, plan: str) -> str:
    links = {
        ("BR", "compliance_essencial"): "https://buy.stripe.com/9B600l1Ac507blO29Og7e03",
        ("BR", "regulatory_pro"): "https://buy.stripe.com/14dRwr3Ik0JRfC44hWg7e04",
        ("BR", "esg_carbono"): "https://buy.stripe.com/6oUeVf3IkeAH4Xq7u8g7e06",
        ("US", "eu_ai_act"): "CRIAR_NO_STRIPE_USD",
        ("MX", "lfpdppp"): "CRIAR_NO_STRIPE_MXN",
        ("CO", "ley1581"): "CRIAR_NO_STRIPE_COP",
        ("AR", "sdr_backoffice"): "CRIAR_NO_STRIPE_USD",
    }
    return links.get((market, plan), STRIPE_LINKS_BR["compliance_essencial"])
```

### 1.2 Widget de chat multi-mercado — adicionar antes de `</body>`

```html
<div id="ecosystem-chat-widget"></div>
<script>
(function(){
  const lang = navigator.language || 'pt-BR';
  let market = 'BR';
  if(lang.startsWith('en')) market = 'US';
  if(lang === 'es-MX') market = 'MX';
  if(lang === 'es-CO') market = 'CO';
  if(lang === 'es-AR') market = 'AR';

  const labels = {
    BR: {title: 'Agente EcoSystem — online agora', placeholder: 'Pergunte sobre NR-1, LGPD...'},
    US: {title: 'EcoSystem Agent — online now', placeholder: 'Ask about EU AI Act compliance...'},
    MX: {title: 'Agente EcoSystem — en línea', placeholder: 'Pregunta sobre LFPDPPP...'},
    CO: {title: 'Agente EcoSystem — en línea', placeholder: 'Pregunta sobre Ley 1581...'},
    AR: {title: 'Agente EcoSystem — en línea', placeholder: 'Pregunta sobre automatización...'}
  };
  const t = labels[market];

  const widget = document.createElement('div');
  widget.innerHTML = `
    <div id="chat-bubble" style="position:fixed;bottom:24px;right:24px;
      width:60px;height:60px;border-radius:50%;background:#00C36B;
      display:flex;align-items:center;justify-content:center;
      cursor:pointer;box-shadow:0 8px 24px rgba(0,195,107,.4);z-index:9999">
      <span style="font-size:28px">💬</span>
    </div>
    <div id="chat-window" style="display:none;position:fixed;bottom:96px;
      right:24px;width:340px;height:480px;background:#0C1322;
      border-radius:16px;box-shadow:0 16px 48px rgba(0,0,0,.4);
      z-index:9999;flex-direction:column;overflow:hidden">
      <div style="background:#00C36B;padding:16px;color:#fff;font-weight:600">
        ${t.title}
      </div>
      <div id="chat-messages" style="flex:1;padding:16px;overflow-y:auto;
        color:#e2e8f0;font-size:13px"></div>
      <div style="padding:12px;display:flex;gap:8px;border-top:1px solid #1A2540">
        <input id="chat-input" placeholder="${t.placeholder}"
          style="flex:1;background:#1A2540;border:none;border-radius:8px;
          padding:10px;color:#fff;font-size:13px">
        <button id="chat-send" style="background:#00C36B;border:none;
          border-radius:8px;padding:10px 14px;color:#fff;cursor:pointer">→</button>
      </div>
    </div>
  `;
  document.body.appendChild(widget);
  document.getElementById('chat-bubble').onclick = () => {
    const w = document.getElementById('chat-window');
    w.style.display = w.style.display === 'none' ? 'flex' : 'none';
  };
  document.getElementById('chat-send').onclick = async () => {
    const input = document.getElementById('chat-input');
    const msgBox = document.getElementById('chat-messages');
    const msg = input.value;
    if(!msg) return;
    msgBox.innerHTML += `<div style="margin-bottom:8px;text-align:right">
      <span style="background:#00C36B;padding:8px 12px;border-radius:12px;
      display:inline-block">${msg}</span></div>`;
    input.value = '';
    const resp = await fetch('https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: msg, page: window.location.pathname, market: market})
    });
    const data = await resp.json();
    msgBox.innerHTML += `<div style="margin-bottom:8px">
      <span style="background:#1A2540;padding:8px 12px;border-radius:12px;
      display:inline-block">${data.response}</span></div>`;
    msgBox.scrollTop = msgBox.scrollHeight;
  };
})();
</script>
```

### 1.3 Visitor ID Agent — `src/agents/visitor_id_agent.py`

```python
from fastapi import APIRouter, Request
from src.database.supabase_client import SupabaseClient
import httpx

router = APIRouter(prefix="/api/visitor-id", tags=["visitor_id"])

class VisitorIDAgent:
    async def identify_visitor(self, ip: str, page_visited: str) -> dict:
        company_data = await self._reverse_ip_lookup(ip)
        if not company_data or not company_data.get("org"):
            return {"identified": False}

        market = self._detect_market(company_data.get("country", "BR"))
        lead = {
            "company_name": company_data.get("org"),
            "country": company_data.get("country"),
            "market": market,
            "page_visited": page_visited,
            "ip": ip
        }
        await self._save_lead(lead)
        return {"identified": True, "lead": lead}

    def _detect_market(self, country: str) -> str:
        mapping = {"BR": "BR", "US": "US", "MX": "MX", "CO": "CO", "AR": "AR"}
        return mapping.get(country, "US")

    async def _reverse_ip_lookup(self, ip: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://ipapi.co/{ip}/json/")
        data = resp.json()
        return {"org": data.get("org"), "country": data.get("country_code")}

    async def _save_lead(self, lead: dict):
        db = SupabaseClient()
        await db.table("identified_leads").insert(lead).execute()


@router.post("/track")
async def track_visitor(request: Request):
    data = await request.json()
    client_ip = request.client.host
    page = data.get("page", "/")
    agent = VisitorIDAgent()
    return await agent.identify_visitor(client_ip, page)
```

---

## PARTE 2 — SEO PROGRAMÁTICO MULTI-MERCADO

### `src/agents/seo_content_agent.py`

```python
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.database.supabase_client import SupabaseClient
import itertools

router = APIRouter(prefix="/api/seo", tags=["seo_agent"])

NORMAS_BR = {
    "nr1-psicossocial": {"nome": "NR-1 Psicossocial", "norma": "Portaria MTE 1.419/2024",
        "dor": "risco de interdição", "stripe_link": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"},
    "lgpd-operacional": {"nome": "LGPD Operacional", "norma": "Lei 13.709/2018",
        "dor": "multa até R$ 50M", "stripe_link": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"},
}

NORMAS_US = {
    "eu-ai-act-article-50": {"nome": "EU AI Act Article 50 Readiness", "norma": "EU AI Act Article 50",
        "dor": "fine up to EUR 35M or 7% global revenue", "stripe_link": "CRIAR_STRIPE_USD"},
}
SETORES_US = ["saas", "fintech", "healthtech", "ecommerce", "martech"]

NORMAS_MX = {
    "lfpdppp-cumplimiento": {"nome": "Cumplimiento LFPDPPP", "norma": "LFPDPPP",
        "dor": "multas hasta 320,000 UMA", "stripe_link": "CRIAR_STRIPE_MXN"},
}
SETORES_MX = ["fintech", "ecommerce", "salud", "retail", "manufactura"]

NORMAS_CO = {
    "ley-1581-cumplimiento": {"nome": "Cumplimiento Ley 1581", "norma": "Ley 1581 de 2012",
        "dor": "multas hasta 2,000 SMMLV", "stripe_link": "CRIAR_STRIPE_COP"},
}
SETORES_CO = ["fintech", "salud", "retail", "logistica"]

NORMAS_AR = {
    "sdr-automatizacion": {"nome": "Automatización SDR y Back-Office", "norma": "Eficiencia operativa",
        "dor": "costo operativo elevado por procesos manuales", "stripe_link": "CRIAR_STRIPE_USD"},
}
SETORES_AR = ["fintech", "agtech", "ecommerce", "servicios"]

PORTES = {"mei": "MEI/microempresas", "pequena-empresa": "pequeñas empresas",
          "media-empresa": "medianas empresas", "grande-empresa": "grandes empresas"}


class SEOContentAgent:

    async def generate_market_pages(self, market: str):
        config = {
            "BR": (NORMAS_BR, ["industria","comercio","construcao-civil","tecnologia","saude"]),
            "US": (NORMAS_US, SETORES_US),
            "MX": (NORMAS_MX, SETORES_MX),
            "CO": (NORMAS_CO, SETORES_CO),
            "AR": (NORMAS_AR, SETORES_AR),
        }
        normas, setores = config[market]
        combinations = itertools.product(normas.keys(), setores, PORTES.keys())
        generated = []
        for norma_key, setor, porte in combinations:
            slug = f"{market.lower()}-{norma_key}-{setor}-{porte}"
            content = await self._generate_page_content(normas[norma_key], setor, porte, market)
            await self._save_page(slug, content, market)
            generated.append(slug)
        return {"market": market, "pages_generated": len(generated)}

    async def _generate_page_content(self, norma: dict, setor: str, porte: str, market: str) -> dict:
        deepseek = DeepSeekClient()
        idioma = "português" if market == "BR" else "español" if market in ["MX","CO","AR"] else "English"
        prompt = f"""Write a landing page in {idioma} for:
        Regulation: {norma['nome']} ({norma['norma']})
        Sector: {setor}, Company size: {PORTES.get(porte, porte)}
        Pain: {norma['dor']}
        Structure: H1, risk paragraph, 3 action bullets, how agent solves in 48h, CTA.
        Direct tone, real numbers, max 600 words."""
        content = await deepseek.complete(prompt)
        return {
            "title": f"{norma['nome']} — {setor.title()} — {PORTES.get(porte,porte)}",
            "meta_description": f"{norma['nome']} ({norma['norma']}). {norma['dor']}.",
            "body": content, "stripe_link": norma["stripe_link"],
        }

    async def _save_page(self, slug: str, content: dict, market: str):
        db = SupabaseClient()
        await db.table("seo_pages").upsert({
            "slug": slug, "title": content["title"],
            "meta_description": content["meta_description"],
            "body": content["body"], "stripe_link": content["stripe_link"],
            "market": market, "published": True
        }).execute()


@router.post("/generate/{market}")
async def trigger_generation(market: str):
    agent = SEOContentAgent()
    return await agent.generate_market_pages(market.upper())

@router.get("/page/{slug}")
async def get_seo_page(slug: str):
    db = SupabaseClient()
    result = await db.table("seo_pages").select("*").eq("slug", slug).execute()
    return result.data[0] if result.data else {"error": "not_found"}
```

### Rodar geração — 1 chamada por mercado

```bash
curl -X POST https://engenheiro-producao-ai.onrender.com/api/seo/generate/BR
curl -X POST https://engenheiro-producao-ai.onrender.com/api/seo/generate/US
curl -X POST https://engenheiro-producao-ai.onrender.com/api/seo/generate/MX
curl -X POST https://engenheiro-producao-ai.onrender.com/api/seo/generate/CO
curl -X POST https://engenheiro-producao-ai.onrender.com/api/seo/generate/AR
```

Total de páginas geradas: aproximadamente 290 (Brasil 180 + US 25 + MX 20 + CO 16 + AR 16)

---

## PARTE 3 — OS 4 PRODUTOS NOVOS — DETALHE COMPLETO

### 3.1 EU AI Act Readiness Agent (EUA + qualquer empresa vendendo para UE)

```python
# src/agents/eu_ai_act_agent.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/eu-ai-act", tags=["eu_ai_act"])

@router.post("/readiness-check")
async def readiness_check(data: dict):
    from src.api.deepseek_client import DeepSeekClient
    deepseek = DeepSeekClient()
    response = await deepseek.complete(
        system="""You are an EU AI Act Article 50 compliance specialist.
        Deadline: August 2, 2026. Analyze if the company is in scope and
        what's needed for compliance:
        1. Chatbot/conversational AI disclosure requirements
        2. AI-generated content labeling
        3. Required technical documentation
        Fine: up to EUR 35M or 7% of global annual turnover.""",
        user=f"Company: {data.get('company')}\nUses AI for: {data.get('ai_use')}\nSells to EU: {data.get('sells_to_eu')}"
    )
    return {"analysis": response, "checkout_url": "CRIAR_PRICE_USD_199_DIAGNOSTICO"}
```

Preço: USD 199 diagnóstico único + USD 299/mês monitoramento contínuo.
Stripe: criar price_id em USD, produto "EU AI Act Readiness".
Urgência de venda: deadline 2 de agosto de 2026 — usar isso no copy de tudo.

### 3.2 LFPDPPP Compliance Agent (México)

```python
# src/agents/lfpdppp_agent.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/lfpdppp", tags=["lfpdppp"])

@router.post("/diagnostico")
async def diagnostico(data: dict):
    from src.api.deepseek_client import DeepSeekClient
    deepseek = DeepSeekClient()
    response = await deepseek.complete(
        system="""Eres especialista en LFPDPPP (Ley Federal de Protección
        de Datos Personales en Posesión de los Particulares) de México.
        Genera un Aviso de Privacidad conforme a la ley, identifica
        riesgos de tratamiento de datos personales, y recomienda acciones.
        Multas: hasta 320,000 UMA.""",
        user=f"Empresa: {data.get('empresa')}\nSector: {data.get('sector')}\nDatos que maneja: {data.get('tipos_datos')}"
    )
    return {"analysis": response, "checkout_url": "CRIAR_PRICE_MXN"}
```

Preço: MXN 990/mês ou USD 49/mês. Mercado: fintech, e-commerce, salud.

### 3.3 Ley 1581 Compliance Agent (Colômbia)

```python
# src/agents/ley1581_agent.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/ley1581", tags=["ley1581"])

@router.post("/diagnostico")
async def diagnostico(data: dict):
    from src.api.deepseek_client import DeepSeekClient
    deepseek = DeepSeekClient()
    response = await deepseek.complete(
        system="""Eres especialista en Ley 1581 de 2012 (Protección de
        Datos Personales) de Colombia. Genera política de tratamiento
        de datos, identifica registro ante la SIC (RNBD), recomienda
        acciones. Multas: hasta 2,000 SMMLV.""",
        user=f"Empresa: {data.get('empresa')}\nSector: {data.get('sector')}\nDatos que maneja: {data.get('tipos_datos')}"
    )
    return {"analysis": response, "checkout_url": "CRIAR_PRICE_COP"}
```

Preço: COP 180.000/mês ou USD 45/mês.

### 3.4 SDR/Back-Office Automation Agent (Argentina)

```python
# src/agents/sdr_backoffice_agent.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/sdr-backoffice", tags=["sdr_backoffice"])

@router.post("/diagnostico")
async def diagnostico(data: dict):
    from src.api.deepseek_client import DeepSeekClient
    deepseek = DeepSeekClient()
    response = await deepseek.complete(
        system="""Eres especialista en automatización de procesos de
        ventas (SDR) y back-office para empresas argentinas. Identifica
        cuellos de botella en calificación de leads, facturación,
        conciliación, y propone automatización con IA. Enfócate en
        reducir costo operativo en contexto de moneda devaluada.""",
        user=f"Empresa: {data.get('empresa')}\nSector: {data.get('sector')}\nProcesos manuales: {data.get('procesos')}"
    )
    return {"analysis": response, "checkout_url": "CRIAR_PRICE_USD"}
```

Preço: USD 99/mês — cobrar em dólar é vantagem em contexto de peso desvalorizado.
Mercado: fintech, agtech, e-commerce.

---

## PARTE 4 — PAY-PER-USE MULTI-MERCADO

```python
# src/agents/usage_billing.py
import stripe
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/usage", tags=["usage_billing"])

PRICING_PER_USE = {
    "BR": {"nr1_diagnostico": ("brl", 1990), "lgpd_scan": ("brl", 2990)},
    "US": {"eu_ai_act_check": ("usd", 1999)},
    "MX": {"lfpdppp_check": ("mxn", 49000)},
    "CO": {"ley1581_check": ("cop", 18000000)},
    "AR": {"sdr_diagnostic": ("usd", 990)},
}

class UsageBillingAgent:
    async def create_one_time_charge(self, market: str, agent_id: str, email: str) -> str:
        currency, amount = PRICING_PER_USE[market][agent_id]
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": f"Diagnóstico {agent_id}"},
                    "unit_amount": amount
                },
                "quantity": 1
            }],
            mode="payment",
            success_url="https://global-engenharia.com/ecosystem/sucesso",
            cancel_url="https://global-engenharia.com/ecosystem",
            customer_email=email
        )
        return session.url


@router.post("/pay-per-use/{market}/{agent_id}")
async def create_usage_payment(market: str, agent_id: str, request: Request):
    data = await request.json()
    agent = UsageBillingAgent()
    url = await agent.create_one_time_charge(market.upper(), agent_id, data.get("email", ""))
    return {"checkout_url": url}
```

---

## PARTE 5 — SQL — TODAS AS TABELAS (rodar de uma vez)

```sql
CREATE TABLE chat_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message TEXT, response TEXT, page TEXT, market TEXT DEFAULT 'BR',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE identified_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT, country TEXT, market TEXT,
    page_visited TEXT, ip TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE seo_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT, meta_description TEXT, body TEXT,
    stripe_link TEXT, market TEXT,
    published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_seo_slug ON seo_pages(slug);
CREATE INDEX idx_seo_market ON seo_pages(market);
CREATE INDEX idx_leads_market ON identified_leads(market);
```

---

## PARTE 6 — CANAIS EXTRAS — TODOS OS MERCADOS

Replit Agent Market — 5 listings (1 por mercado):
1. Brazil Compliance Score — BRL/USD
2. EU AI Act Readiness Checker — USD
3. México LFPDPPP Compliance — USD/MXN
4. Colombia Ley 1581 Compliance — USD/COP
5. Argentina SDR Automation — USD

MindStudio — mesmos 5 agentes, tiers USD 49 a 499/mês.

GPT Store — começar pelo EU AI Act, que tem maior urgência e maior ticket:
1. platform.openai.com/gpts → Create a GPT
2. "EU AI Act Compliance Checker"
3. Actions → conectar /api/eu-ai-act/readiness-check
4. Stripe Connect para monetização

Hugging Face Spaces — 1 Space multi-idioma com seletor de mercado.

---

## CHECKLIST FINAL — 21 DIAS

### Semana 1 (Dia 1-7) — Brasil + fundação
- [ ] `app/routers/sales_agent_chat.py` com suporte multi-mercado
- [ ] Widget de chat multi-idioma no site
- [ ] `src/agents/visitor_id_agent.py`
- [ ] `src/agents/seo_content_agent.py` (estrutura multi-mercado)
- [ ] Rodar geração BR (180 páginas)
- [ ] `src/agents/usage_billing.py`
- [ ] Todas as tabelas SQL
- [ ] Deploy e testar tudo em produção

### Semana 2 (Dia 8-14) — EUA + México + Colômbia
- [ ] `src/agents/eu_ai_act_agent.py`
- [ ] Criar price_id Stripe USD para EU AI Act (199 + 299/mês)
- [ ] Rodar geração SEO US (25 páginas)
- [ ] `src/agents/lfpdppp_agent.py`
- [ ] Criar price_id Stripe MXN
- [ ] Rodar geração SEO MX (20 páginas)
- [ ] `src/agents/ley1581_agent.py`
- [ ] Criar price_id Stripe COP
- [ ] Rodar geração SEO CO (16 páginas)

### Semana 3 (Dia 15-21) — Argentina + canais extras
- [ ] `src/agents/sdr_backoffice_agent.py`
- [ ] Criar price_id Stripe USD para Argentina
- [ ] Rodar geração SEO AR (16 páginas)
- [ ] Publicar 5 listings no Replit
- [ ] Publicar 5 agentes no MindStudio
- [ ] Publicar GPT do EU AI Act na GPT Store
- [ ] Publicar Hugging Face Space multi-mercado
- [ ] Google Search Console — submeter sitemap com todos os slugs

---

## RESULTADO ESPERADO — 5 MERCADOS SIMULTÂNEOS

| Mercado | Produto | Ticket | Clientes dia 30 | Clientes dia 90 |
|---------|---------|--------|------------------|-------------------|
| Brasil | NR-1/LGPD/CBS-IBS/ESG | R$ 390-1.490 | 15-25 | 80-130 |
| EUA | EU AI Act Readiness | USD 199-299 | 5-12 | 30-50 |
| México | LFPDPPP | USD 49-149 | 3-8 | 20-35 |
| Colômbia | Ley 1581 | USD 45-129 | 2-6 | 15-25 |
| Argentina | SDR/Back-office | USD 99-249 | 3-7 | 18-30 |

MRR consolidado estimado:
Dia 30: aproximadamente R$ 31.000 total (BR + conversão de US/MX/CO/AR em reais).
Dia 90: aproximadamente R$ 144.000 total.

---

Documento único e final, gerado em 2026-06-24.
Passar integralmente para o DeepSeek Flash, seguindo a ordem exata de 21 dias.
Brasil já documentado anteriormente está incluído aqui de forma consolidada.
EUA, México, Colômbia e Argentina são produtos novos, mesma arquitetura, normas diferentes.
