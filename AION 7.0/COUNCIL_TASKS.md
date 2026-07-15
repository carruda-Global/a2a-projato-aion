# Council Report — H-MAS EcoSystem v3.0
**Auditoria técnica** · 25 Jun 2026 · FastAPI + Supabase + Stripe + Abacatepay + Azure Marketplace

---

## Scores

| Dimensão | Nota | Motivo |
|---|---|---|
| Confiabilidade | 5/10 | Estado de assinaturas em memória volátil |
| Segurança | 6/10 | Webhook Microsoft sem autenticação, CORS aberto |
| Performance | 6/10 | Settings relida do disco em todo request |
| Arquitetura | 7/10 | Boa separação de routers e services |
| Monetização | 8/10 | PIX + Stripe + Azure bem estruturados |

---

## 🔴 CRÍTICO — Executar hoje

### C1 · Webhooks Stripe e Abacatepay não ativam assinaturas

**Arquivo:** `app/routers/subscriptions.py` — linhas 129–139 e 160–163

**Problema:** Os handlers `checkout.session.completed` (Stripe) e `checkout.paid` (Abacatepay) fazem apenas `print()` com dados do evento. A função `activate_subscription()` nunca é chamada. Clientes que pagam via cartão ou PIX não têm acesso liberado.

**O que fazer:**
- No handler `checkout.session.completed`: extrair `subscription_id`, `customer_id`, `customer_email` do objeto Stripe e chamar `activate_subscription(source="stripe", external_id=subscription_id, ...)`
- No handler `checkout.paid` do Abacatepay: extrair `checkout_id` e `plan_id` do `metadata` e chamar `activate_subscription(source="abacatepay", external_id=checkout_id, ...)`
- No handler `customer.subscription.deleted`: chamar `deactivate_subscription("stripe", data.id)`

---

### C2 · Estado de assinaturas perdido a cada restart

**Arquivo:** `src/monetization/subscription_activator.py` — variável `_active_subscriptions`

**Problema:** O dicionário `_active_subscriptions: dict[str, dict] = {}` existe apenas em memória RAM do processo Python. Qualquer deploy, restart ou crash do Render.com apaga todos os clientes ativos. Em multi-instância, as instâncias não compartilham o estado.

**O que fazer:**
1. Criar tabela `subscriptions` no Supabase com schema:
   ```sql
   CREATE TABLE subscriptions (
     id TEXT PRIMARY KEY,          -- "{source}_{external_id}"
     source TEXT NOT NULL,         -- "stripe" | "microsoft" | "abacatepay"
     external_id TEXT NOT NULL,
     customer_id TEXT NOT NULL,
     customer_email TEXT,
     customer_name TEXT,
     plan_id TEXT NOT NULL,
     status TEXT NOT NULL DEFAULT 'active',
     activated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
     cancelled_at TIMESTAMPTZ,
     UNIQUE(source, external_id)
   );
   ```
2. Substituir as funções em `subscription_activator.py` por queries async usando `supabase_client.py` (já existe no projeto em `src/database/supabase_client.py`)
3. O índice `UNIQUE(source, external_id)` garante idempotência sem lógica adicional

---

### C3 · httpx.AsyncClient vaza conexões por request

**Arquivo:** `src/monetization/abacatepay_client.py` — `__init__` + `app/routers/subscriptions.py`

**Problema:** Cada chamada aos endpoints `/checkout/pix` e `/checkout/pix/{id}` instancia um novo `AbacatepayClient`, que abre um `httpx.AsyncClient` no `__init__`. O método `close()` existe mas nunca é chamado. Em produção com volume, haverá esgotamento do pool de conexões do sistema operacional.

**O que fazer:**
- Opção A (simples): substituir `self.http = httpx.AsyncClient(...)` no `__init__` por criação local com `async with httpx.AsyncClient(...) as http:` dentro de cada método
- Opção B (correta): instanciar `AbacatepayClient` no lifespan da aplicação e armazenar em `app.state.abacatepay`, reutilizando o mesmo client entre requests

---

### C4 · print() em vez de logger nos webhooks

**Arquivo:** `app/routers/subscriptions.py` — linhas 132, 134, 137, 163

**Problema:** Os handlers de webhook usam `print(f"[{env}] ...")`. Isso não aparece nos logs estruturados do Render.com nem no Grafana, não tem severity level, e pode vazar emails de clientes em stdout sem passar pelo mascaramento PII do sistema.

**O que fazer:**
- Adicionar `logger = logging.getLogger(__name__)` no topo do arquivo
- Substituir todos os `print()` por `logger.info()` ou `logger.warning()`

---

### C5 · URL do dashboard hardcoded no código

**Arquivo:** `app/routers/microsoft_marketplace.py` — linha 149

**Problema:** A string `"https://engenheiro-producao-ai.onrender.com/dashboard"` está hardcoded. `settings.base_url` já existe com exatamente esse valor via variável de ambiente `BASE_URL`. Se o domínio mudar, o redirecionamento do Azure Marketplace quebra silenciosamente.

**O que fazer:**
- Substituir a string hardcoded por `f"{settings.base_url}/dashboard?subscription_id={subscription_id}&source=microsoft"`

---

### C6 · Settings.validate() nunca é chamada no startup

**Arquivo:** `src/config.py` linha 94 + `app/main.py`

**Problema:** O método `validate()` que verifica `DEEPSEEK_API_KEY` e `STRIPE_SECRET_KEY` existe mas não é chamado durante a inicialização da aplicação. Erros de configuração são descobertos apenas quando o primeiro request chega, causando falha silenciosa em produção.

**O que fazer:**
- No evento de startup em `app/main.py`, adicionar:
  ```python
  settings = Settings()
  errors = settings.validate()
  if errors:
      raise RuntimeError(f"Configuração inválida: {errors}")
  ```

---

## 🟠 ALTA PRIORIDADE — Esta semana

### H1 · resolve_purchase() engole todas as exceções silenciosamente

**Arquivo:** `app/routers/microsoft_marketplace.py` — linhas 53–55 e 118–120

**Problema:** `except Exception: resolved = None` silencia qualquer erro (timeout, 401 Azure, falha de rede). No endpoint `/fulfill`, em vez de retornar erro, retorna um objeto fictício com `preview_{uuid}` como subscription_id, fazendo parecer que o fulfillment funcionou quando falhou. Isso pode criar registros inválidos e impedir diagnóstico de problemas com a Azure.

**O que fazer:**
- Logar a exceção com `logger.exception("resolve_purchase failed: token=%s", payload.token[:20])`
- Retornar HTTP 502 com mensagem clara em vez do fallback de "preview customer"
- Remover o bloco de retorno fictício das linhas 58–65

---

### H2 · Webhook Microsoft sem verificação de assinatura

**Arquivo:** `app/routers/microsoft_marketplace.py` — linhas 164–187

**Problema:** O endpoint `POST /microsoft/webhook` aceita qualquer JSON sem validar autenticidade. Qualquer pessoa pode enviar `{"eventType": "Unsubscribe", "subscriptionId": "xyz"}` e cancelar uma assinatura legítima de um cliente.

**O que fazer:**
- A Microsoft envia um Bearer JWT no header `Authorization` assinado pelo Azure AD
- Validar o token usando a biblioteca `python-jose` já no `requirements.txt`
- Verificar issuer (`https://sts.windows.net/{tenant_id}/`), audience e assinatura com a chave pública do Azure AD

---

### H3 · Settings() relê config.yaml em todo request

**Arquivo:** `app/routers/subscriptions.py` (linhas 35, 64, 91, 106), `microsoft_marketplace.py` (linha 41), `salesforce_marketplace.py`

**Problema:** `Settings()` é instanciada em cada handler de endpoint, o que abre e lê `config.yaml` do disco, faz parse YAML completo e resolve ~50 variáveis de ambiente — a cada request. Com 100 req/s isso é I/O de disco e CPU desnecessários.

**O que fazer:**
```python
# src/config.py
from functools import lru_cache

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
```
- Em todos os routers, substituir `settings = Settings()` por injeção via dependência:
  ```python
  from fastapi import Depends
  from src.config import get_settings, Settings

  @router.post("/checkout")
  async def create_checkout(req: ..., settings: Settings = Depends(get_settings)):
      ...
  ```

---

## 🟡 MÉDIA PRIORIDADE — Próximo sprint

### M1 · Webhooks sem idempotência

**Arquivo:** `app/routers/subscriptions.py` — webhooks Stripe e Abacatepay

**Problema:** Stripe e Abacatepay garantem entrega *at-least-once*. Se o webhook for reentregue (timeout, retry), `activate_subscription()` será chamado duas vezes. Quando a persistência for migrada para Supabase (task C2), isso causará tentativas de inserção duplicada.

**O que fazer:**
- A tabela `subscriptions` com `UNIQUE(source, external_id)` já resolve o caso de ativação duplicada por constraint
- Para maior controle, criar tabela `processed_webhook_events(event_id TEXT PRIMARY KEY, processed_at TIMESTAMPTZ)` e verificar antes de processar
- O Stripe envia `event.id` no objeto do webhook; o Abacatepay envia `data.id`

---

### M2 · Conversão BRL → USD hardcoded

**Arquivo:** `app/routers/microsoft_marketplace.py` — linha 212

**Problema:** `p['price'] / 600` assume câmbio fixo de R$6,00/USD. Quando o câmbio variar, os preços exibidos no Azure Marketplace ficam incorretos e podem gerar reclamações ou chargebacks.

**O que fazer:**
- Adicionar campo `price_usd` em cada plano no `config.yaml`:
  ```yaml
  compliance_essencial:
    price_usd: 110  # USD cents, revisado manualmente
  ```
- Usar `plan_config.get("price_usd", plan_config["amount_cents"] // 600)` como fallback

---

### M3 · Mutação de dict por referência sem proteção de concorrência

**Arquivo:** `app/routers/microsoft_marketplace.py` — linha 180

**Problema:** `sub["plan_id"] = new_plan_id` modifica diretamente o dict retornado por `get_active_sub()`, que é uma referência ao objeto em `_active_subscriptions`. Em ambiente assíncrono com múltiplas coroutines, pode causar condição de corrida.

**O que fazer:**
- Criar função `update_subscription_plan(source, external_id, new_plan_id)` em `subscription_activator.py` que realiza a atualização de forma controlada
- Após migrar para Supabase (C2), isso será resolvido automaticamente com UPDATE atômico

---

### M4 · response_model ausente nos endpoints principais

**Arquivo:** `app/routers/subscriptions.py`, `microsoft_marketplace.py`, `salesforce_marketplace.py`

**Problema:** A maioria dos endpoints retorna dicts Python sem `response_model=`. O FastAPI não valida nem filtra a resposta, o Swagger mostra apenas `200: {}` sem schema definido, e dados internos podem vazar acidentalmente na resposta.

**O que fazer:**
- Definir modelos Pydantic para respostas dos endpoints principais:
  - `CheckoutResponse`, `PlanResponse`, `SubscriptionResponse`, `WebhookAckResponse`
- Adicionar `response_model=NomeDoModelo` nos decorators

---

### M5 · CORS wildcard em produção

**Arquivo:** `app/main.py`

**Problema:** `allow_origins=["*"]` em produção permite que qualquer domínio faça requests com credenciais à API.

**O que fazer:**
- Em produção (`APP_ENV == "production"`), restringir a `[settings.base_url, "https://portal-dominio.com"]`
- Nunca combinar `allow_origins=["*"]` com `allow_credentials=True`
- Usar `settings.app_env` para derivar a configuração correta:
  ```python
  origins = ["*"] if settings.app_env != "production" else [settings.base_url]
  ```

---

## 🟢 MANUTENÇÃO — Backlog

### B1 · Testes unitários para os módulos de monetização

**Cobertura atual estimada:** < 20% nos módulos modificados

**O que cobrir:**
- `abacatepay_client.py`: mock do `httpx.AsyncClient`, testar `verify_webhook()` com HMAC válido e inválido
- `subscription_activator.py`: testar activate, deactivate, list
- `stripe_client.py`: testar `handle_webhook()` com eventos mockados
- Webhook handlers dos routers: testar com payload válido e assinatura inválida

**Meta:** 80% de cobertura nos módulos de monetização (pytest + pytest-asyncio + httpx mock)

---

### B2 · Logs estruturados com mascaramento PII

**Arquivo:** Todos os routers

**Problema:** Emails e IDs de clientes aparecem em mensagens de log sem mascaramento. O sistema já tem `src/security/pii_masker.py` mas não é usado nos logs dos routers.

**O que fazer:**
- Criar um `logging.Filter` que aplica o `PiiMasker` nas mensagens antes de emitir
- Registrar o filtro no logger raiz durante o startup

---

### B3 · Salesforce webhook sem verificação de assinatura

**Arquivo:** `app/routers/salesforce_marketplace.py`

**Problema:** Similar ao C4 do Microsoft, verificar se o webhook Salesforce está validando a assinatura HMAC presente no header `X-Salesforce-Signature`.

**O que fazer:**
- Verificar implementação atual em `salesforce_marketplace.py`
- Se ausente, adicionar verificação HMAC-SHA256 usando `SALESFORCE_WEBHOOK_SECRET`

---

### B4 · Remover importações dentro de funções

**Arquivo:** `app/routers/subscriptions.py` — linhas 33, 62, 88, 104

**Problema:** `from src.monetization.stripe_client import StripeClient` e similares dentro dos handlers. Importações dentro de funções são executadas a cada chamada e dificultam análise estática.

**O que fazer:**
- Mover todas as importações para o topo do arquivo

---

### B5 · Documentação do fluxo de ativação de assinatura

Após resolver C1 e C2, documentar o fluxo completo:

```
Cliente paga → Webhook recebido → Assinatura salva no Supabase → 
Agentes do plano liberados → Email de confirmação enviado
```

Adicionar diagrama em `docs/subscription_flow.md` e atualizar `AGENTS.md` com o status de cada integração.

---

## Resumo executivo

| # | Task | Severidade | Arquivo principal | Esforço |
|---|---|---|---|---|
| C1 | Ativar assinatura nos webhooks | 🔴 CRÍTICO | `routers/subscriptions.py` | 1h |
| C2 | Persistir assinaturas no Supabase | 🔴 CRÍTICO | `subscription_activator.py` | 4h |
| C3 | Fechar httpx.AsyncClient | 🔴 CRÍTICO | `abacatepay_client.py` | 30min |
| C4 | Trocar print() por logger | 🔴 CRÍTICO | `routers/subscriptions.py` | 15min |
| C5 | Usar settings.base_url no redirect | 🔴 CRÍTICO | `microsoft_marketplace.py` | 5min |
| C6 | Chamar validate() no startup | 🔴 CRÍTICO | `app/main.py` | 15min |
| H1 | Não engolir exceções do Azure resolve | 🟠 ALTA | `microsoft_marketplace.py` | 30min |
| H2 | Autenticar webhook Microsoft com JWT | 🟠 ALTA | `microsoft_marketplace.py` | 2h |
| H3 | Settings singleton com lru_cache | 🟠 ALTA | `src/config.py` + routers | 1h |
| M1 | Idempotência nos webhooks | 🟡 MÉDIA | `routers/subscriptions.py` | 2h |
| M2 | Preços USD no config.yaml | 🟡 MÉDIA | `config.yaml` + router | 30min |
| M3 | Função update_subscription_plan | 🟡 MÉDIA | `subscription_activator.py` | 20min |
| M4 | response_model nos endpoints | 🟡 MÉDIA | todos os routers | 2h |
| M5 | CORS restrito em produção | 🟡 MÉDIA | `app/main.py` | 20min |
| B1 | Testes dos módulos de monetização | 🟢 BACKLOG | `tests/` | 1 dia |
| B2 | Logs com mascaramento PII | 🟢 BACKLOG | todos os routers | 3h |
| B3 | Salesforce webhook signature | 🟢 BACKLOG | `salesforce_marketplace.py` | 1h |
| B4 | Remover imports dentro de funções | 🟢 BACKLOG | `routers/subscriptions.py` | 10min |
| B5 | Documentar fluxo de assinatura | 🟢 BACKLOG | `docs/` | 1h |

**Esforço total estimado:**
- 🔴 Crítico: ~6h
- 🟠 Alta: ~3.5h
- 🟡 Média: ~5h
- 🟢 Backlog: ~1.5 dias
