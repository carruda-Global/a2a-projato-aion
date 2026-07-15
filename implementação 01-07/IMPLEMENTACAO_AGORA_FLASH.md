# AION — IMPLEMENTAÇÃO IMEDIATA (DeepSeek Flash)
**Global Match Engenharia de Produção | Cristiano Arruda**
**Data:** 2026-06-24
**Objetivo:** começar a ganhar dinheiro AGORA — sem marketplace, sem Wise, só Stripe
**Regra:** tudo neste documento roda sem esperar aprovação de ninguém

---

## ORDEM DE EXECUÇÃO — NÃO PULAR ETAPAS

```
DIA 1-2   → Widget de chat + Visitor ID (capta quem já visita)
DIA 3-4   → SEO Content Agent (180 páginas gerando tráfego sozinho)
DIA 5-6   → Pay-per-use no Stripe (cobra sem precisar fechar contrato)
DIA 7-10  → Replit + MindStudio + GPT Store + Hugging Face (4 canais extras)
DIA 11-14 → EU AI Act Readiness Agent (produto novo, prazo urgente agosto/2026)
```

---

## PARTE 1 — WIDGET DE CHAT NO SITE (Sales Agent ativo)

### Arquivo: `app/routers/sales_agent_chat.py`

```python
from fastapi import APIRouter, Request
from src.api.deepseek_client import DeepSeekClient
from src.rag.hybrid_retriever import HybridRetriever
from src.database.supabase_client import SupabaseClient

router = APIRouter(prefix="/api/sales-agent", tags=["sales_agent"])

SYSTEM_PROMPT = """Você é o Sales Agent do EcoSystem AION.
Seu objetivo é qualificar o visitante, responder dúvidas sobre
compliance regulatório (NR-1, LGPD, CBS/IBS, ESG) com precisão,
e conduzir para o plano certo. Sempre termine oferecendo o link
de ativação quando o visitante demonstrar interesse real.
Seja direto, use números reais (multas, prazos), nunca genérico."""

STRIPE_LINKS = {
    "compliance_essencial": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03",
    "regulatory_pro": "https://buy.stripe.com/14dRwr3Ik0JRfC44hWg7e04",
    "esg_carbono": "https://buy.stripe.com/6oUeVf3IkeAH4Xq7u8g7e06"
}

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    page = data.get("page", "/")

    context = await HybridRetriever().search(message, top_k=3)

    deepseek = DeepSeekClient()
    response = await deepseek.complete(
        system=SYSTEM_PROMPT,
        user=f"Página atual: {page}\nContexto regulatório: {context}\nPergunta: {message}"
    )

    plan = _detect_plan_interest(message, response)
    if plan:
        response += f"\n\n🔗 Ative agora: {STRIPE_LINKS[plan]}"

    db = SupabaseClient()
    await db.table("chat_logs").insert({
        "message": message, "response": response, "page": page
    }).execute()

    return {"response": response}

def _detect_plan_interest(message: str, response: str) -> str:
    text = (message + response).lower()
    if "esg" in text or "carbono" in text:
        return "esg_carbono"
    if "igualdade" in text or "denúncia" in text or "anticorrup" in text:
        return "regulatory_pro"
    if "nr-1" in text or "nr1" in text or "lgpd" in text or "ativar" in text:
        return "compliance_essencial"
    return None
```

### Registrar no `app/main.py`
```python
from app.routers.sales_agent_chat import router as sales_chat_router
app.include_router(sales_chat_router)
```

### Widget HTML — adicionar em `vendas_otimizado.html` antes de `</body>`
```html
<div id="ecosystem-chat-widget"></div>
<script>
(function(){
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
        Agente EcoSystem — online agora
      </div>
      <div id="chat-messages" style="flex:1;padding:16px;overflow-y:auto;
        color:#e2e8f0;font-size:13px"></div>
      <div style="padding:12px;display:flex;gap:8px;border-top:1px solid #1A2540">
        <input id="chat-input" placeholder="Pergunte sobre NR-1, LGPD..."
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
      body: JSON.stringify({message: msg, page: window.location.pathname})
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

---

## PARTE 2 — VISITOR ID AGENT (identifica quem visita, mesmo sem form)

### Arquivo: `src/agents/visitor_id_agent.py`

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

        lead = {
            "company_name": company_data.get("org"),
            "city": company_data.get("city"),
            "page_visited": page_visited,
            "ip": ip,
            "source": "anonymous_identification"
        }
        await self._save_lead(lead)
        await self._trigger_outreach(lead)
        return {"identified": True, "lead": lead}

    async def _reverse_ip_lookup(self, ip: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://ipapi.co/{ip}/json/")
        data = resp.json()
        return {"org": data.get("org"), "city": data.get("city")}

    async def _save_lead(self, lead: dict):
        db = SupabaseClient()
        await db.table("identified_leads").insert(lead).execute()

    async def _trigger_outreach(self, lead: dict):
        """Salva como lead quente para follow-up. Email manual ou automático depois."""
        db = SupabaseClient()
        await db.table("hot_leads_queue").insert({
            "company_name": lead["company_name"],
            "page_visited": lead["page_visited"],
            "status": "pending_contact"
        }).execute()


@router.post("/track")
async def track_visitor(request: Request):
    data = await request.json()
    client_ip = request.client.host
    page = data.get("page", "/")
    agent = VisitorIDAgent()
    result = await agent.identify_visitor(client_ip, page)
    return result
```

### Snippet de tracking — adicionar no `<head>` do site
```html
<script>
fetch('https://engenheiro-producao-ai.onrender.com/api/visitor-id/track', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({page: window.location.pathname})
});
</script>
```

---

## PARTE 3 — SEO CONTENT AGENT (180 páginas, tráfego grátis)

### Arquivo: `src/agents/seo_content_agent.py`

```python
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.database.supabase_client import SupabaseClient
import itertools

router = APIRouter(prefix="/api/seo", tags=["seo_agent"])

NORMAS = {
    "nr1-psicossocial": {
        "nome": "NR-1 Psicossocial", "norma": "Portaria MTE 1.419/2024",
        "dor": "risco de interdição e autuação fiscal", "stripe_link": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"
    },
    "lgpd-operacional": {
        "nome": "LGPD Operacional", "norma": "Lei 13.709/2018",
        "dor": "multa de até R$ 50 milhões", "stripe_link": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"
    },
    "cbs-ibs": {
        "nome": "CBS/IBS Tributário", "norma": "LC 214/2025",
        "dor": "passivo fiscal na transição tributária", "stripe_link": "https://buy.stripe.com/cNi5kF3Ik64bdt75aGkg7e0a"
    },
    "igualdade-salarial": {
        "nome": "Igualdade Salarial", "norma": "Lei 14.611/2023",
        "dor": "multa de R$ 140,6 por funcionário/dia", "stripe_link": "https://buy.stripe.com/14dRwr3Ik0JRfC44hWg7e04"
    },
    "canal-denuncias": {
        "nome": "Canal de Denúncias", "norma": "Lei 14.457/2022",
        "dor": "irregularidade trabalhista", "stripe_link": "https://buy.stripe.com/14dRwr3Ik0JRfC44hWg7e04"
    }
}

SETORES = ["industria", "comercio", "construcao-civil", "tecnologia",
           "saude", "servicos", "varejo", "logistica", "alimenticio"]

PORTES = {
    "mei": "MEI e microempresas",
    "pequena-empresa": "pequenas empresas (até 49 funcionários)",
    "media-empresa": "médias empresas (50-499 funcionários)",
    "grande-empresa": "grandes empresas (500+ funcionários)"
}


class SEOContentAgent:

    async def generate_all_pages(self):
        combinations = itertools.product(NORMAS.keys(), SETORES, PORTES.keys())
        generated = []
        for norma_key, setor, porte in combinations:
            slug = f"{norma_key}-{setor}-{porte}"
            content = await self._generate_page_content(norma_key, setor, porte)
            await self._save_page(slug, content)
            generated.append(slug)
        return {"pages_generated": len(generated), "slugs": generated}

    async def _generate_page_content(self, norma_key: str, setor: str, porte: str) -> dict:
        norma = NORMAS[norma_key]
        deepseek = DeepSeekClient()
        prompt = f"""Escreva uma landing page de SEO para:
        Norma: {norma['nome']} ({norma['norma']})
        Setor: {setor}
        Porte: {PORTES[porte]}
        Dor principal: {norma['dor']}

        Estrutura: H1 com norma+setor, parágrafo do risco específico,
        3 bullets do que fazer, como o agente resolve em 48h, CTA final.
        Tom direto, números reais, máximo 600 palavras."""
        content = await deepseek.complete(prompt)
        return {
            "title": f"{norma['nome']} para {setor.replace('-',' ').title()} — {PORTES[porte]}",
            "meta_description": f"{norma['nome']} ({norma['norma']}) para {setor}. Risco: {norma['dor']}. Resolva em 48h.",
            "body": content,
            "stripe_link": norma["stripe_link"],
            "keywords": [norma['nome'].lower(), setor, porte, norma['norma'].lower()]
        }

    async def _save_page(self, slug: str, content: dict):
        db = SupabaseClient()
        await db.table("seo_pages").upsert({
            "slug": slug, "title": content["title"],
            "meta_description": content["meta_description"],
            "body": content["body"], "stripe_link": content["stripe_link"],
            "keywords": content["keywords"], "published": True
        }).execute()


@router.post("/generate")
async def trigger_generation():
    agent = SEOContentAgent()
    return await agent.generate_all_pages()

@router.get("/page/{slug}")
async def get_seo_page(slug: str):
    db = SupabaseClient()
    result = await db.table("seo_pages").select("*").eq("slug", slug).execute()
    return result.data[0] if result.data else {"error": "not_found"}
```

### Rodar geração (1 vez, depois fica publicado para sempre)
```bash
curl -X POST https://engenheiro-producao-ai.onrender.com/api/seo/generate
```

### Google Search Console (você faz, 5 minutos)
```
1. search.google.com/search-console
2. Adicionar propriedade: global-engenharia.com
3. Verificar via DNS ou HTML tag
4. Enviar sitemap (DeepSeek gera sitemap.xml automaticamente)
```

---

## PARTE 4 — PAY-PER-USE NO STRIPE (sem precisar fechar contrato)

### Arquivo: `src/agents/usage_billing.py`

```python
import stripe
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/usage", tags=["usage_billing"])

PRICING_PER_USE = {
    "nr1_diagnostico": 1990,      # R$ 19,90 em centavos
    "lgpd_scan": 2990,            # R$ 29,90
    "esg_diagnostic": 5990,       # R$ 59,90
    "carbon_calculation": 4990,   # R$ 49,90
}

class UsageBillingAgent:

    async def create_one_time_charge(self, agent_id: str, customer_email: str) -> str:
        """
        Gera link de pagamento único (não assinatura) via Stripe Checkout.
        Cliente paga 1x, recebe o diagnóstico, sem compromisso de mensalidade.
        """
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "brl",
                    "product_data": {"name": f"Diagnóstico {agent_id.replace('_',' ').title()}"},
                    "unit_amount": PRICING_PER_USE[agent_id]
                },
                "quantity": 1
            }],
            mode="payment",
            success_url="https://global-engenharia.com/ecosystem/sucesso",
            cancel_url="https://global-engenharia.com/ecosystem",
            customer_email=customer_email
        )
        return session.url


@router.post("/pay-per-use/{agent_id}")
async def create_usage_payment(agent_id: str, request: Request):
    data = await request.json()
    agent = UsageBillingAgent()
    url = await agent.create_one_time_charge(agent_id, data.get("email", ""))
    return {"checkout_url": url}
```

### Botões no site — adicionar seção "Teste avulso"
```html
<div class="card" style="margin-top:1rem">
  <h3>Não quer assinar ainda? Teste avulso:</h3>
  <button onclick="payPerUse('nr1_diagnostico')">Diagnóstico NR-1 — R$ 19,90</button>
  <button onclick="payPerUse('lgpd_scan')">Scan LGPD — R$ 29,90</button>
</div>
<script>
async function payPerUse(agentId){
  const email = prompt('Seu email:');
  const resp = await fetch(`https://engenheiro-producao-ai.onrender.com/api/usage/pay-per-use/${agentId}`, {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({email})
  });
  const data = await resp.json();
  window.location.href = data.checkout_url;
}
</script>
```

---

## PARTE 5 — SQL — TODAS AS TABELAS NECESSÁRIAS

```sql
CREATE TABLE chat_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message TEXT, response TEXT, page TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE identified_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT, city TEXT, page_visited TEXT,
    ip TEXT, source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE hot_leads_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT, page_visited TEXT,
    status TEXT DEFAULT 'pending_contact',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE seo_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT, meta_description TEXT, body TEXT,
    stripe_link TEXT, keywords JSONB,
    published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_seo_slug ON seo_pages(slug);
CREATE INDEX idx_leads_company ON identified_leads(company_name);
```

---

## PARTE 6 — CANAIS EXTRAS (publicar, zero aprovação complexa)

### Replit Agent Market
```
1. replit.com → Create Repl Python → "ecosystem-compliance-score"
2. Código Flask simples chamando seu endpoint /api/sales-agent/chat
3. Tools → Publish → Agent Market
4. Preço: USD 29/mês
```

### MindStudio
```
1. mindstudio.ai → New Agent
2. System Prompt: copiar o SYSTEM_PROMPT da Parte 1
3. Deploy → Marketplace
4. Tiers: USD 49 / USD 149 / USD 499
```

### GPT Store
```
1. platform.openai.com/gpts → Create a GPT
2. Nome: "NR-1 & LGPD Compliance Assistant"
3. Actions → conectar /api/sales-agent/chat via OpenAPI schema
4. Conectar Stripe Connect para monetização
5. Submit for review
```

### Hugging Face Spaces
```python
# app.py para Hugging Face
import gradio as gr
import requests

def diagnostico(pergunta):
    resp = requests.post(
        "https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat",
        json={"message": pergunta, "page": "/huggingface"}
    )
    return resp.json()["response"]

demo = gr.Interface(
    fn=diagnostico, inputs="text", outputs="text",
    title="EcoSystem — Compliance Brasil",
    description="Pergunte sobre NR-1, LGPD, CBS/IBS. Plano completo: global-engenharia.com/ecosystem"
)
demo.launch()
```

---

## PARTE 7 — PRODUTO NOVO: EU AI ACT READINESS AGENT (prazo agosto/2026)

### Por que isso importa agora
Deadline 2 de agosto de 2026 — menos de 5 semanas. Empresas americanas e
europeias que vendem para a UE precisam de Article 50 disclosure compliance.
Multa: até €35M ou 7% do faturamento global.

### Arquivo: `src/agents/eu_ai_act_agent.py`

```python
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient

router = APIRouter(prefix="/api/eu-ai-act", tags=["eu_ai_act"])

@router.post("/readiness-check")
async def readiness_check(data: dict):
    """
    Diagnóstico rápido: a empresa está em escopo do EU AI Act?
    O que falta para Article 50 compliance até agosto/2026?
    """
    deepseek = DeepSeekClient()
    response = await deepseek.complete(
        system="""Você é especialista em EU AI Act Article 50.
        Analise se a empresa está em escopo e o que falta para
        compliance até 2 de agosto de 2026. Seja específico sobre:
        1. Disclosure de chatbot/IA conversacional
        2. Labeling de conteúdo gerado por IA
        3. Documentação técnica necessária""",
        user=f"Empresa: {data.get('empresa')}\nUsa IA para: {data.get('uso_ia')}\nVende para UE: {data.get('vende_ue')}"
    )
    return {"analysis": response, "stripe_link": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"}
```

### Preço — USD 199 diagnóstico único + USD 299/mês monitoramento contínuo

---

## CHECKLIST FINAL — MARCAR CONFORME IMPLEMENTA

### Dia 1-2
- [ ] Criar `app/routers/sales_agent_chat.py`
- [ ] Registrar router em `app/main.py`
- [ ] Adicionar widget de chat HTML no site
- [ ] Criar `src/agents/visitor_id_agent.py`
- [ ] Adicionar snippet de tracking no `<head>` do site
- [ ] Criar tabelas SQL (Parte 5)
- [ ] Deploy no Render e testar

### Dia 3-4
- [ ] Criar `src/agents/seo_content_agent.py`
- [ ] Rodar geração das 180 páginas (1x via curl)
- [ ] Criar rota dinâmica `/[slug]` no site para renderizar páginas SEO
- [ ] Cadastrar no Google Search Console
- [ ] Enviar sitemap

### Dia 5-6
- [ ] Criar `src/agents/usage_billing.py`
- [ ] Adicionar seção "Teste avulso" no site
- [ ] Testar pagamento único end-to-end

### Dia 7-10
- [ ] Publicar Replit Agent Market
- [ ] Publicar MindStudio
- [ ] Publicar GPT Store
- [ ] Publicar Hugging Face Space

### Dia 11-14
- [ ] Criar `src/agents/eu_ai_act_agent.py`
- [ ] Criar página `/eu-ai-act-readiness` no site
- [ ] Criar price_id no Stripe para o novo produto
- [ ] Anunciar no LinkedIn (urgência do prazo agosto/2026)

---

## RESULTADO ESPERADO — SEM MARKETPLACE, SEM WISE

| Período | Canais ativos | MRR estimado |
|---------|---------------|--------------|
| Dia 14 | Chat + Visitor ID + SEO publicado | R$ 3.000–6.000 |
| Dia 30 | + Pay-per-use + Replit + MindStudio | R$ 12.000–22.000 |
| Dia 60 | + SEO indexado + GPT Store + HF Spaces | R$ 35.000–58.000 |
| Dia 90 | + EU AI Act Agent + cross-sell girando | R$ 70.000–110.000 |

---

*Documento único de implementação — 2026-06-24*
*Passar integralmente para o DeepSeek Flash seguir a ordem exata*
*Sem Wise, sem marketplace — 100% Stripe + canais auto-aprovados*
