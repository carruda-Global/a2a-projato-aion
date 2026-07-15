# Plano de Execução — H-MAS EcoSystem
**Guia completo de implementação** · Junho 2026 · Sem dependência de Azure ou serviços externos novos

> **Premissa:** Toda a infraestrutura necessária já existe no projeto (`docker-compose.yml`).
> O trabalho é conectar o que está lá, não construir do zero.
> Estimativa total: **~30h de desenvolvimento** distribuídas em 4 fases.

---

## Visão geral das fases

| Fase | Nome | Esforço | Resultado |
|---|---|---|---|
| 1 | Estabilização | 8h | Sistema confiável, sem perda de dados |
| 2 | Banco de dados local | 6h | Independente do Supabase |
| 3 | Kafka + Workers assíncronos | 10h | Suporta 60+ agentes e centenas de clientes simultâneos |
| 4 | Agent Registry | 6h | Adicionar agentes sem deploy |

---

---

# FASE 1 — Estabilização (8h)
> Resolver os bugs críticos antes de qualquer escala. Sem isso, escalar só amplifica os problemas.

---

## 1.1 · Trocar print() por logger em subscriptions.py
**Arquivo:** `app/routers/subscriptions.py`
**Tempo:** 15 min

No topo do arquivo, após as importações existentes, adicionar:
```python
import logging
logger = logging.getLogger(__name__)
```

Substituir cada ocorrência de `print(...)` por:
- `print(f"[{env}] Novo checkout concluido: ...")` → `logger.info("Checkout concluído: customer=%s sub=%s env=%s", customer_email, subscription_id, env)`
- `print(f"[{env}] Assinatura atualizada: ...")` → `logger.info("Assinatura atualizada: id=%s status=%s env=%s", data.id, data.status, env)`
- `print(f"[{env}] Assinatura cancelada: ...")` → `logger.warning("Assinatura cancelada: id=%s env=%s", data.id, env)`
- `print(f"[PIX] Checkout pago: ...")` → `logger.info("PIX checkout pago: id=%s plan=%s", checkout_id, plan_id)`

**Regra:** nunca logar email completo — usar apenas os primeiros 3 chars + `***` para mascarar PII.

---

## 1.2 · Ativar assinatura no webhook Stripe
**Arquivo:** `app/routers/subscriptions.py`
**Tempo:** 30 min

Adicionar import no topo do arquivo:
```python
from src.monetization.subscription_activator import activate_subscription, deactivate_subscription
```

Localizar o bloco `if event_type == "checkout.session.completed":` e substituir o `print()` por:
```python
if event_type == "checkout.session.completed":
    customer_details = data.get("customer_details", {})
    customer_email = customer_details.get("email", "")
    customer_name = customer_details.get("name", "")
    subscription_id = data.get("subscription", "")
    customer_id = data.get("customer", "")
    # metadata vem do checkout session criado em stripe_client.py
    plan_id = data.get("metadata", {}).get("plan_id", "")
    activate_subscription(
        source="stripe",
        external_id=subscription_id,
        customer_id=customer_id,
        plan_id=plan_id,
        customer_email=customer_email,
        customer_name=customer_name,
    )
    logger.info("Assinatura Stripe ativada: sub=%s plan=%s", subscription_id, plan_id)
```

Localizar `elif event_type == "customer.subscription.deleted":` e substituir:
```python
elif event_type == "customer.subscription.deleted":
    deactivate_subscription("stripe", data.id)
    logger.warning("Assinatura Stripe cancelada: id=%s", data.id)
```

---

## 1.3 · Ativar assinatura no webhook Abacatepay (PIX)
**Arquivo:** `app/routers/subscriptions.py`
**Tempo:** 20 min

Localizar o bloco `if event_type == "checkout.paid":` e substituir:
```python
if event_type == "checkout.paid":
    checkout_id = data.get("id", "")
    plan_id = data.get("metadata", {}).get("plan_id", "")
    customer_email = data.get("customer_email", "")
    customer_name = data.get("customer_name", "")
    activate_subscription(
        source="abacatepay",
        external_id=checkout_id,
        customer_id=checkout_id,  # Abacatepay não tem customer_id separado
        plan_id=plan_id,
        customer_email=customer_email,
        customer_name=customer_name,
    )
    logger.info("Assinatura PIX ativada: checkout=%s plan=%s", checkout_id, plan_id)
```

---

## 1.4 · Fechar httpx.AsyncClient corretamente
**Arquivo:** `src/monetization/abacatepay_client.py`
**Tempo:** 30 min

Remover `self.http = httpx.AsyncClient(...)` do `__init__`.

Guardar apenas a configuração:
```python
def __init__(self, settings: Settings):
    self.settings = settings
    self.api_key = settings.abacatepay_api_key
    self.webhook_secret = settings.abacatepay_webhook_secret
    self.sandbox_mode = settings.abacatepay_sandbox_mode
    self._base_url = (
        ABACATEPAY_API_BASE_SANDBOX if self.sandbox_mode else ABACATEPAY_API_BASE
    )
    self._headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json",
    }
```

Reescrever `create_pix_checkout` para abrir e fechar o client localmente:
```python
async def create_pix_checkout(self, plan_id, customer_email=None, customer_name=None, success_url=None):
    plan_config = self.settings.plans_config.get(plan_id)
    if not plan_config:
        return None
    payload = {
        "amount_cents": plan_config["amount_cents"],
        "currency": "BRL",
        "description": plan_config["name"],
        "methods": ["pix"],
        "metadata": {"plan_id": plan_id},
    }
    if customer_email:
        payload["customer_email"] = customer_email
    if customer_name:
        payload["customer_name"] = customer_name
    if success_url:
        payload["redirect_url"] = success_url

    async with httpx.AsyncClient(base_url=self._base_url, headers=self._headers) as http:
        resp = await http.post("/checkout", json=payload)
    if resp.status_code != 201:
        return None
    data = resp.json()
    return {
        "checkout_id": data.get("id", ""),
        "pix_code": data.get("pix_code", ""),
        "pix_qr_code": data.get("pix_qr_code", ""),
        "expires_at": data.get("expires_at", ""),
        "amount_cents": data.get("amount_cents", plan_config["amount_cents"]),
        "status": data.get("status", "pending"),
    }
```

Fazer o mesmo padrão `async with` em `get_checkout_status`.
Remover o método `close()` — não é mais necessário.

---

## 1.5 · Settings singleton com lru_cache
**Arquivo:** `src/config.py`
**Tempo:** 20 min

Adicionar no topo do arquivo:
```python
from functools import lru_cache
```

Adicionar ao final do arquivo, após a classe `Settings`:
```python
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
```

Em **todos** os routers (`subscriptions.py`, `microsoft_marketplace.py`, `salesforce_marketplace.py`, e demais), substituir o padrão:
```python
# ANTES (em cada endpoint)
settings = Settings()

# DEPOIS (no topo do arquivo, fora dos endpoints)
from src.config import get_settings, Settings
from fastapi import Depends
```

E nos endpoints que usam `settings`, adicionar como parâmetro:
```python
@router.post("/checkout")
async def create_checkout(
    req: CreateCheckoutRequest,
    settings: Settings = Depends(get_settings),
):
    ...
```

---

## 1.6 · Usar settings.base_url no redirect Microsoft
**Arquivo:** `app/routers/microsoft_marketplace.py`
**Tempo:** 5 min

Localizar linha 149:
```python
# ANTES
redirect_url = (
    f"https://engenheiro-producao-ai.onrender.com/dashboard?"
    f"subscription_id={subscription_id}&source=microsoft"
)

# DEPOIS
redirect_url = (
    f"{settings.base_url}/dashboard?"
    f"subscription_id={subscription_id}&source=microsoft"
)
```

---

## 1.7 · Chamar validate() no startup e logar exceção do Azure
**Arquivo:** `app/main.py`
**Tempo:** 20 min

No evento de startup da aplicação (procurar `@app.on_event("startup")` ou o lifespan):
```python
@app.on_event("startup")
async def startup():
    settings = get_settings()
    errors = settings.validate()
    if errors:
        import sys
        print(f"[STARTUP ERROR] Configuração inválida: {errors}", file=sys.stderr)
        # Não fazer raise aqui para não derrubar o processo no Render antes do healthcheck
        # mas logar claramente para que o operador veja nos logs

    # ... resto do startup existente
```

**Arquivo:** `app/routers/microsoft_marketplace.py`

Localizar os dois blocos `except Exception: resolved = None` e substituir:
```python
# ANTES
try:
    resolved = client.resolve_purchase(payload.token)
except Exception:
    resolved = None

# DEPOIS
try:
    resolved = client.resolve_purchase(payload.token)
except Exception:
    logger.exception("Falha ao resolver token Azure Marketplace: token_prefix=%s", payload.token[:20])
    resolved = None
```

No bloco `/fulfill`, remover o fallback fictício (linhas 58–65 que retornam `preview_{uuid}`) e substituir por:
```python
if not resolved:
    raise HTTPException(
        status_code=502,
        detail="Falha ao validar token com Azure Marketplace. Token inválido, expirado ou erro de rede."
    )
```

---

## 1.8 · Autenticar webhook Microsoft com JWT
**Arquivo:** `app/routers/microsoft_marketplace.py`
**Tempo:** 2h

Instalar dependência (já está no requirements.txt: `python-jose`).

No handler `POST /webhook`, antes de processar o payload, adicionar:
```python
@router.post("/webhook")
async def handle_webhook(request: Request, settings: Settings = Depends(get_settings)):
    # Validar Bearer JWT enviado pela Microsoft
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.warning("Microsoft webhook sem Authorization header")
        raise HTTPException(status_code=401, detail="Authorization header ausente")

    token = auth_header[7:]
    try:
        from jose import jwt, JWTError
        import httpx

        # Buscar JWKS da Microsoft (cachear em produção com TTL de 1h)
        tenant_id = settings.microsoft_tenant_id
        jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        async with httpx.AsyncClient() as http:
            jwks_resp = await http.get(jwks_url)
        jwks = jwks_resp.json()

        payload_jwt = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.microsoft_client_id,
            issuer=f"https://sts.windows.net/{tenant_id}/",
        )
        logger.info("Microsoft webhook JWT válido: sub=%s", payload_jwt.get("sub"))
    except Exception:
        logger.exception("Microsoft webhook com JWT inválido")
        raise HTTPException(status_code=401, detail="Token Microsoft inválido")

    # ... continua com o processamento existente do payload
```

> **Nota:** O JWKS deve ser cacheado em Redis para não fazer request externo em todo webhook. Implementar na Fase 2 junto com Redis.

---

---

# FASE 2 — Banco de Dados Local (6h)
> Eliminar dependência do Supabase nos fluxos críticos. Usar PostgreSQL do próprio Render.

---

## 2.1 · Criar banco PostgreSQL no Render

1. No dashboard do Render.com, ir em **New → PostgreSQL**
2. Nome: `hmas-database`
3. Região: mesma do serviço `hmas-orchestrator` (para latência mínima)
4. Plano: Starter ($7/mês) para desenvolvimento, Standard ($97/mês) para produção
5. Copiar a **Internal Database URL** (formato: `postgresql://user:pass@host/dbname`)
6. No serviço `hmas-orchestrator` no Render, adicionar variável de ambiente:
   - `DATABASE_URL` = a Internal Database URL copiada

---

## 2.2 · Criar as tabelas no banco

Conectar ao banco (via psql, DBeaver, ou Render Shell) e executar:

```sql
-- Extensão para UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabela de assinaturas (substitui o dict em memória)
CREATE TABLE subscriptions (
    id TEXT PRIMARY KEY,                    -- "{source}_{external_id}"
    source TEXT NOT NULL,                   -- "stripe" | "microsoft" | "abacatepay" | "salesforce"
    external_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    customer_email TEXT DEFAULT '',
    customer_name TEXT DEFAULT '',
    plan_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',  -- "active" | "cancelled" | "suspended"
    activated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    cancelled_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(source, external_id)
);

CREATE INDEX idx_subscriptions_customer_id ON subscriptions(customer_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_plan_id ON subscriptions(plan_id);

-- Tabela de eventos de webhook processados (idempotência)
CREATE TABLE processed_webhook_events (
    event_id TEXT PRIMARY KEY,              -- ID único do evento (Stripe event.id, etc)
    source TEXT NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    event_type TEXT NOT NULL,
    payload JSONB DEFAULT '{}'
);

CREATE INDEX idx_webhook_events_source ON processed_webhook_events(source);

-- Tabela de execuções de agentes (para histórico e billing)
CREATE TABLE agent_executions (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',   -- "queued" | "running" | "completed" | "failed"
    input_summary TEXT,
    result_summary TEXT,
    llm_tokens_used INTEGER DEFAULT 0,
    cost_brl NUMERIC(10,4) DEFAULT 0,
    queued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE INDEX idx_agent_executions_tenant ON agent_executions(tenant_id);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);
CREATE INDEX idx_agent_executions_agent ON agent_executions(agent_id);

-- Tabela de registro de agentes (substitui config.yaml para definições de agentes)
CREATE TABLE agent_registry (
    id TEXT PRIMARY KEY,                    -- "nr1_psicossocial", "spec_analyst", etc
    name TEXT NOT NULL,
    cluster TEXT NOT NULL,                  -- "regulatory", "aec_core", "microsoft", etc
    description TEXT,
    llm_model TEXT NOT NULL DEFAULT 'deepseek-chat',
    status TEXT NOT NULL DEFAULT 'active',  -- "active" | "inactive" | "beta"
    plan_ids TEXT[] DEFAULT '{}',           -- planos que incluem este agente
    config JSONB DEFAULT '{}',              -- configurações específicas do agente
    version TEXT DEFAULT '1.0.0',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Audit trail (substitui arquivos em data/audit/)
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT,
    actor TEXT NOT NULL,                    -- user_id ou system
    action TEXT NOT NULL,                   -- "subscription.activated", "agent.executed", etc
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    details JSONB DEFAULT '{}',
    ip_address TEXT,
    hash TEXT NOT NULL,                     -- hash encadeado para imutabilidade
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_log_tenant ON audit_log(tenant_id);
CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
```

---

## 2.3 · Criar cliente PostgreSQL async
**Novo arquivo:** `src/database/postgres_client.py`

```python
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def init_pool() -> None:
    global _pool
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        logger.warning("DATABASE_URL não configurada — banco de dados indisponível")
        return
    _pool = await asyncpg.create_pool(
        database_url,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )
    logger.info("Pool PostgreSQL inicializado")


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


@asynccontextmanager
async def get_conn() -> AsyncGenerator[asyncpg.Connection, None]:
    if not _pool:
        raise RuntimeError("Pool PostgreSQL não inicializado — chamar init_pool() no startup")
    async with _pool.acquire() as conn:
        yield conn
```

Adicionar `asyncpg>=0.29.0` ao `requirements.txt` (já deve estar).

---

## 2.4 · Migrar subscription_activator para PostgreSQL
**Arquivo:** `src/monetization/subscription_activator.py`
**Tempo:** 1.5h

Reescrever o arquivo completamente:

```python
import logging
from datetime import datetime, timezone
from src.database.postgres_client import get_conn

logger = logging.getLogger(__name__)


async def activate_subscription(
    source: str,
    external_id: str,
    customer_id: str,
    plan_id: str,
    customer_email: str = "",
    customer_name: str = "",
) -> dict:
    sub_id = f"{source}_{external_id}"
    async with get_conn() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO subscriptions (id, source, external_id, customer_id,
                customer_email, customer_name, plan_id, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, 'active')
            ON CONFLICT (source, external_id) DO UPDATE
                SET status = 'active',
                    plan_id = EXCLUDED.plan_id,
                    updated_at = now()
            RETURNING *
            """,
            sub_id, source, external_id, customer_id,
            customer_email, customer_name, plan_id,
        )
    record = dict(row)
    logger.info("Assinatura ativada: source=%s sub=%s plan=%s", source, sub_id, plan_id)
    return record


async def deactivate_subscription(source: str, external_id: str) -> bool:
    sub_id = f"{source}_{external_id}"
    async with get_conn() as conn:
        result = await conn.execute(
            """
            UPDATE subscriptions
            SET status = 'cancelled', cancelled_at = now(), updated_at = now()
            WHERE id = $1 AND status != 'cancelled'
            """,
            sub_id,
        )
    updated = result.split()[-1] != "0"
    if updated:
        logger.info("Assinatura cancelada: %s", sub_id)
    return updated


async def get_subscription(source: str, external_id: str) -> dict | None:
    async with get_conn() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM subscriptions WHERE source = $1 AND external_id = $2",
            source, external_id,
        )
    return dict(row) if row else None


async def list_active_subscriptions() -> list[dict]:
    async with get_conn() as conn:
        rows = await conn.fetch(
            "SELECT * FROM subscriptions WHERE status = 'active' ORDER BY activated_at DESC"
        )
    return [dict(r) for r in rows]


async def update_subscription_plan(source: str, external_id: str, new_plan_id: str) -> bool:
    async with get_conn() as conn:
        result = await conn.execute(
            """
            UPDATE subscriptions
            SET plan_id = $3, updated_at = now()
            WHERE source = $1 AND external_id = $2
            """,
            source, external_id, new_plan_id,
        )
    return result.split()[-1] != "0"
```

> **Atenção:** Como as funções viraram `async`, todos os callers precisam ser ajustados com `await`. Nos routers, as chamadas como `activate_subscription(...)` viram `await activate_subscription(...)`.

---

## 2.5 · Adicionar idempotência nos webhooks
**Arquivo:** `app/routers/subscriptions.py`
**Tempo:** 45 min

Criar função auxiliar:
```python
async def _is_event_processed(event_id: str, source: str) -> bool:
    from src.database.postgres_client import get_conn
    async with get_conn() as conn:
        row = await conn.fetchrow(
            "SELECT 1 FROM processed_webhook_events WHERE event_id = $1",
            event_id,
        )
    return row is not None


async def _mark_event_processed(event_id: str, source: str, event_type: str) -> None:
    from src.database.postgres_client import get_conn
    async with get_conn() as conn:
        await conn.execute(
            """
            INSERT INTO processed_webhook_events (event_id, source, event_type)
            VALUES ($1, $2, $3)
            ON CONFLICT (event_id) DO NOTHING
            """,
            event_id, source, event_type,
        )
```

No handler do Stripe, logo após construir o `event`:
```python
event_id = event.id
if await _is_event_processed(event_id, "stripe"):
    logger.info("Evento Stripe já processado: %s", event_id)
    return {"received": True, "type": event_type, "status": "already_processed"}
await _mark_event_processed(event_id, "stripe", event_type)
```

Mesmo padrão no handler Abacatepay, usando `data.get("id")` como event_id.

---

## 2.6 · Inicializar pool no startup e fechar no shutdown
**Arquivo:** `app/main.py`
**Tempo:** 20 min

No startup event:
```python
from src.database.postgres_client import init_pool, close_pool

@app.on_event("startup")
async def startup():
    await init_pool()
    settings = get_settings()
    errors = settings.validate()
    if errors:
        logger.error("Configuração inválida: %s", errors)
    # ... resto do startup existente

@app.on_event("shutdown")
async def shutdown():
    await close_pool()
```

---

## 2.7 · Atualizar render.yaml com DATABASE_URL
**Arquivo:** `render.yaml`

Adicionar nas envVars do serviço `hmas-orchestrator`:
```yaml
- key: DATABASE_URL
  fromDatabase:
    name: hmas-database
    property: connectionString
```

E adicionar o banco como recurso:
```yaml
databases:
  - name: hmas-database
    plan: starter
    databaseName: hmas
    user: hmas_user
    region: ohio  # mesma região do serviço
```

---

## 2.8 · Popular agent_registry com os 30 agentes atuais

Executar no banco após criação das tabelas:

```sql
INSERT INTO agent_registry (id, name, cluster, llm_model, plan_ids) VALUES
-- AEC Core
('spec_analyst', 'Analista de Especificações', 'aec_core', 'deepseek-chat', ARRAY['aec_full','full_suite']),
('procurement', 'Agente de Compras', 'aec_core', 'deepseek-chat', ARRAY['aec_full','full_suite']),
('inventory', 'Gestão de Estoque', 'aec_core', 'deepseek-chat', ARRAY['aec_full','full_suite']),
('logistics', 'Logística e Rastreamento', 'aec_core', 'deepseek-chat', ARRAY['aec_full','full_suite']),
('field_execution', 'Execução em Campo', 'aec_core', 'deepseek-chat', ARRAY['aec_full','full_suite']),
-- AEC Specialized
('bim_coordinator', 'Coordenador BIM', 'aec_specialized', 'deepseek-chat', ARRAY['aec_full','full_suite']),
('requirements_analyst', 'Análise de Requisitos', 'aec_specialized', 'deepseek-chat', ARRAY['aec_full','full_suite']),
('engineering_assistant', 'Assistente de Engenharia', 'aec_specialized', 'deepseek-chat', ARRAY['aec_full','full_suite']),
('work_synopsis', 'Resumo de Tarefas', 'aec_specialized', 'deepseek-chat', ARRAY['aec_full','full_suite']),
-- AEC Compliance
('photo_intelligence', 'Inteligência Visual de Obras', 'aec_compliance', 'deepseek-chat', ARRAY['aec_full','full_suite']),
('rfi_creation', 'Criação de RFIs', 'aec_compliance', 'deepseek-chat', ARRAY['aec_full','full_suite']),
('compliance', 'Conformidade PGRS', 'aec_compliance', 'deepseek-chat', ARRAY['aec_full','full_suite']),
-- Regulatory
('nr1_psicossocial', 'NR-1 Riscos Psicossociais', 'regulatory', 'gemini-pro', ARRAY['compliance_essencial','regulatory_pro','full_suite']),
('tributario_cbs_ibs', 'Tributário CBS/IBS', 'regulatory', 'deepseek-chat', ARRAY['tributario_entrada','tributario_full','full_suite']),
('lgpd_operacional', 'LGPD Operacional', 'regulatory', 'gemini-pro', ARRAY['compliance_essencial','regulatory_pro','full_suite']),
('esg_ifrs', 'ESG IFRS S1/S2', 'regulatory', 'deepseek-chat', ARRAY['esg_carbon','regulatory_pro','full_suite']),
('inventario_carbono', 'Inventário de Carbono', 'regulatory', 'deepseek-chat', ARRAY['esg_carbon','full_suite']),
('escopo3_fornecedores', 'Escopo 3 Fornecedores', 'regulatory', 'deepseek-chat', ARRAY['esg_carbon','full_suite']),
('canal_denuncias', 'Canal de Denúncias', 'regulatory', 'gemini-pro', ARRAY['regulatory_pro','full_suite']),
('igualdade_salarial', 'Igualdade Salarial', 'regulatory', 'deepseek-chat', ARRAY['regulatory_pro','full_suite']),
('compliance_anticorrupcao', 'Compliance Anticorrupção', 'regulatory', 'deepseek-chat', ARRAY['regulatory_pro','full_suite']),
-- Microsoft Pack
('regulatory_analyst', 'Analista Regulatório MS', 'microsoft', 'deepseek-chat', ARRAY['microsoft_pack','full_suite']),
('compliance_pm', 'Compliance PM', 'microsoft', 'deepseek-chat', ARRAY['microsoft_pack','full_suite']),
('channel_agent', 'Agente de Canal', 'microsoft', 'deepseek-chat', ARRAY['microsoft_pack','full_suite']),
('knowledge_agent', 'Agente de Conhecimento', 'microsoft', 'deepseek-chat', ARRAY['microsoft_pack','full_suite']),
('facilitator_agent', 'Agente Facilitador', 'microsoft', 'deepseek-chat', ARRAY['microsoft_pack','full_suite']),
('dev_experience', 'Developer Experience', 'microsoft', 'deepseek-chat', ARRAY['microsoft_pack','full_suite']),
-- Cross-Sell
('onboarding_funcionarios', 'Onboarding RH', 'cross_sell', 'deepseek-chat', ARRAY['cross_sell_harmony','full_suite']),
('atendimento_cliente_ptbr', 'Atendimento L1 PT-BR', 'cross_sell', 'deepseek-chat', ARRAY['atendimento_plus','full_suite']),
('conciliacao_financeira', 'Conciliação Financeira', 'cross_sell', 'deepseek-chat', ARRAY['conciliacao_pro','full_suite']);
```

---

---

# FASE 3 — Kafka + Workers Assíncronos (10h)
> Desacoplar execução de agentes do request HTTP. Base para suportar 60+ agentes e centenas de clientes simultâneos.

---

## 3.1 · Definir tópicos Kafka

No `docker-compose.yml`, o Kafka já existe. Criar os tópicos ao iniciar:

```yaml
# No serviço kafka do docker-compose, adicionar command de inicialização:
KAFKA_CREATE_TOPICS: >
  aec.tasks:3:1,
  regulatory.tasks:3:1,
  microsoft.tasks:2:1,
  cross_sell.tasks:2:1,
  admin.tasks:1:1,
  audit.events:1:1,
  task.results:3:1
```

Os números após `:` são `partitions:replication_factor`.

---

## 3.2 · Criar Producer (API → Kafka)
**Novo arquivo:** `src/messaging/producer.py`

```python
import json
import logging
import os
from datetime import datetime, timezone

from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None

CLUSTER_TO_TOPIC = {
    "aec_core": "aec.tasks",
    "aec_specialized": "aec.tasks",
    "aec_compliance": "aec.tasks",
    "regulatory": "regulatory.tasks",
    "microsoft": "microsoft.tasks",
    "cross_sell": "cross_sell.tasks",
}


async def init_producer() -> None:
    global _producer
    kafka_url = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    _producer = AIOKafkaProducer(
        bootstrap_servers=kafka_url,
        value_serializer=lambda v: json.dumps(v).encode(),
        key_serializer=lambda k: k.encode() if k else None,
    )
    await _producer.start()
    logger.info("Kafka producer iniciado: %s", kafka_url)


async def close_producer() -> None:
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None


async def enqueue_agent_task(
    task_id: str,
    tenant_id: str,
    agent_id: str,
    cluster: str,
    task_type: str,
    payload: dict,
) -> None:
    if not _producer:
        raise RuntimeError("Kafka producer não inicializado")

    topic = CLUSTER_TO_TOPIC.get(cluster, "admin.tasks")
    message = {
        "task_id": task_id,
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "cluster": cluster,
        "task_type": task_type,
        "payload": payload,
        "queued_at": datetime.now(timezone.utc).isoformat(),
    }
    await _producer.send_and_wait(topic, value=message, key=tenant_id)
    logger.info("Task enfileirada: task=%s agent=%s topic=%s", task_id, agent_id, topic)
```

---

## 3.3 · Modificar endpoint de execução para ser assíncrono
**Arquivo:** `app/main.py` — endpoint `POST /api/agents/execute`

```python
import uuid
from src.messaging.producer import enqueue_agent_task
from src.database.postgres_client import get_conn

@app.post("/api/agents/execute")
async def execute_agent(request: AgentExecuteRequest):
    task_id = str(uuid.uuid4())

    # Registrar task no banco com status "queued"
    async with get_conn() as conn:
        await conn.execute(
            """
            INSERT INTO agent_executions
                (id, tenant_id, agent_id, task_type, status, input_summary)
            VALUES ($1, $2, $3, $4, 'queued', $5)
            """,
            task_id,
            request.tenant_id,
            request.agent_id,
            request.task_type,
            str(request.payload)[:500],  # resumo para não guardar dados sensíveis
        )

    # Buscar cluster do agente no registry
    async with get_conn() as conn:
        row = await conn.fetchrow(
            "SELECT cluster FROM agent_registry WHERE id = $1 AND status = 'active'",
            request.agent_id,
        )
    if not row:
        raise HTTPException(status_code=404, detail=f"Agente {request.agent_id} não encontrado ou inativo")

    # Enfileirar no Kafka — retorna imediatamente
    await enqueue_agent_task(
        task_id=task_id,
        tenant_id=request.tenant_id,
        agent_id=request.agent_id,
        cluster=row["cluster"],
        task_type=request.task_type,
        payload=request.payload,
    )

    return {
        "task_id": task_id,
        "status": "queued",
        "poll_url": f"/api/tasks/{task_id}",
        "message": "Task enfileirada. Use poll_url para acompanhar o resultado.",
    }


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    async with get_conn() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM agent_executions WHERE id = $1",
            task_id,
        )
    if not row:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    return dict(row)
```

---

## 3.4 · Criar Worker por cluster
**Novo arquivo:** `workers/aec_worker.py`

Criar um arquivo similar para cada cluster. Exemplo para AEC:

```python
"""
Worker do cluster AEC — consome tópico aec.tasks e executa agentes.
Executado como processo separado no Render.
"""
import asyncio
import json
import logging
import os
import sys

from aiokafka import AIOKafkaConsumer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.postgres_client import init_pool, close_pool, get_conn
from src.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aec_worker")

TOPIC = "aec.tasks"
GROUP_ID = "aec-worker-group"


async def process_task(task: dict) -> None:
    task_id = task["task_id"]
    agent_id = task["agent_id"]
    tenant_id = task["tenant_id"]

    # Marcar como "running"
    async with get_conn() as conn:
        await conn.execute(
            "UPDATE agent_executions SET status='running', started_at=now() WHERE id=$1",
            task_id,
        )

    try:
        # Carregar e executar o agente
        # Importação dinâmica baseada no agent_id do registry
        module = __import__(f"src.agents.{agent_id}", fromlist=["agent"])
        agent_class = getattr(module, "agent", None)

        settings = get_settings()
        result = await agent_class.execute(task["payload"], settings)

        # Marcar como "completed"
        async with get_conn() as conn:
            await conn.execute(
                """
                UPDATE agent_executions
                SET status='completed', completed_at=now(),
                    result_summary=$2, llm_tokens_used=$3
                WHERE id=$1
                """,
                task_id,
                str(result)[:1000],
                result.get("tokens_used", 0) if isinstance(result, dict) else 0,
            )
        logger.info("Task concluída: task=%s agent=%s", task_id, agent_id)

    except Exception:
        logger.exception("Erro ao processar task=%s agent=%s", task_id, agent_id)
        async with get_conn() as conn:
            await conn.execute(
                """
                UPDATE agent_executions
                SET status='failed', completed_at=now(), error_message=$2
                WHERE id=$1
                """,
                task_id,
                "Erro interno no worker — ver logs",
            )


async def run_worker() -> None:
    await init_pool()
    kafka_url = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=kafka_url,
        group_id=GROUP_ID,
        value_deserializer=lambda v: json.loads(v.decode()),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()
    logger.info("AEC Worker iniciado — consumindo tópico: %s", TOPIC)

    try:
        async for msg in consumer:
            task = msg.value
            logger.info("Task recebida: task=%s agent=%s", task.get("task_id"), task.get("agent_id"))
            await process_task(task)
            await consumer.commit()
    finally:
        await consumer.stop()
        await close_pool()


if __name__ == "__main__":
    asyncio.run(run_worker())
```

Criar `workers/regulatory_worker.py`, `workers/microsoft_worker.py`, `workers/cross_sell_worker.py` com o mesmo padrão, alterando apenas `TOPIC` e `GROUP_ID`.

---

## 3.5 · Adicionar workers no render.yaml

```yaml
services:
  # API Gateway (já existe)
  - type: web
    name: hmas-orchestrator
    # ... config existente

  # Workers por cluster (novos)
  - type: worker
    name: hmas-worker-aec
    buildCommand: pip install -r requirements.txt
    startCommand: python workers/aec_worker.py
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: hmas-database
          property: connectionString
      - key: KAFKA_BOOTSTRAP_SERVERS
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false

  - type: worker
    name: hmas-worker-regulatory
    buildCommand: pip install -r requirements.txt
    startCommand: python workers/regulatory_worker.py
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: hmas-database
          property: connectionString
      - key: KAFKA_BOOTSTRAP_SERVERS
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false

  - type: worker
    name: hmas-worker-microsoft
    buildCommand: pip install -r requirements.txt
    startCommand: python workers/microsoft_worker.py
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: hmas-database
          property: connectionString
      - key: KAFKA_BOOTSTRAP_SERVERS
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false

  - type: worker
    name: hmas-worker-crosssell
    buildCommand: pip install -r requirements.txt
    startCommand: python workers/cross_sell_worker.py
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: hmas-database
          property: connectionString
      - key: KAFKA_BOOTSTRAP_SERVERS
        sync: false
      - key: DEEPSEEK_API_KEY
        sync: false
```

> **Kafka em produção:** usar Confluent Cloud (free tier: 10GB/mês) ou Upstash Kafka (~$0,20/GB). Adicionar `KAFKA_BOOTSTRAP_SERVERS` como variável no Render apontando para o cluster cloud.

---

## 3.6 · Adicionar variáveis ao .env.example

```bash
# Banco de dados local
DATABASE_URL=postgresql://user:password@localhost:5432/hmas

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Gemini (agentes sensíveis LGPD/NR-1)
GEMINI_API_KEY=your_gemini_api_key
```

---

---

# FASE 4 — Agent Registry Dinâmico (6h)
> Adicionar novos agentes sem alterar código ou fazer deploy da API.

---

## 4.1 · Criar endpoint de consulta ao registry
**Arquivo:** `app/routers/agents.py`

Adicionar endpoints para gerenciar o registry:

```python
@router.get("/registry")
async def list_agent_registry(
    cluster: str | None = None,
    status: str = "active",
):
    from src.database.postgres_client import get_conn
    query = "SELECT * FROM agent_registry WHERE status = $1"
    params = [status]
    if cluster:
        query += " AND cluster = $2"
        params.append(cluster)
    query += " ORDER BY cluster, name"

    async with get_conn() as conn:
        rows = await conn.fetch(query, *params)
    return {"agents": [dict(r) for r in rows]}


@router.get("/registry/{agent_id}")
async def get_agent_from_registry(agent_id: str):
    from src.database.postgres_client import get_conn
    async with get_conn() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM agent_registry WHERE id = $1", agent_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    return dict(row)
```

---

## 4.2 · Criar loader dinâmico de agentes
**Novo arquivo:** `src/core/agent_loader.py`

```python
import importlib
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Cache em memória dos últimos 60 agentes carregados
_agent_cache: dict = {}


def load_agent(agent_id: str):
    """
    Carrega um agente pelo ID dinamicamente.
    O arquivo deve existir em src/agents/{agent_id}.py
    e ter uma variável `agent` no módulo.
    """
    if agent_id in _agent_cache:
        return _agent_cache[agent_id]

    try:
        module = importlib.import_module(f"src.agents.{agent_id}")
        agent = getattr(module, "agent", None)
        if agent is None:
            raise AttributeError(f"src/agents/{agent_id}.py não tem variável 'agent'")
        _agent_cache[agent_id] = agent
        logger.info("Agente carregado dinamicamente: %s", agent_id)
        return agent
    except ModuleNotFoundError:
        raise ValueError(f"Arquivo de agente não encontrado: src/agents/{agent_id}.py")


def unload_agent(agent_id: str) -> None:
    """Remove agente do cache (ex: após atualização de config)."""
    _agent_cache.pop(agent_id, None)
```

---

## 4.3 · Procedimento para adicionar novo agente (60, 70, N...)

Com o Agent Registry no banco, adicionar um novo agente é:

**Passo 1** — criar o arquivo Python:
```
src/agents/nome_do_novo_agente.py
```
O arquivo deve ter no mínimo:
```python
from src.agents.base import BaseAgent

class NomeDoNovoAgente(BaseAgent):
    async def execute(self, payload: dict, settings) -> dict:
        # lógica do agente
        return {"result": "..."}

agent = NomeDoNovoAgente(
    agent_id="nome_do_novo_agente",
    name="Nome Legível",
    cluster="regulatory",  # ou o cluster correspondente
)
```

**Passo 2** — inserir no banco:
```sql
INSERT INTO agent_registry (id, name, cluster, llm_model, plan_ids, description)
VALUES (
    'nome_do_novo_agente',
    'Nome Legível do Agente',
    'regulatory',
    'deepseek-chat',
    ARRAY['regulatory_pro', 'full_suite'],
    'Descrição do que o agente faz'
);
```

**Passo 3** — se necessário, adicionar ao plano via config.yaml ou na tabela `subscriptions` → `plan_ids`.

**Não é necessário:**
- ❌ Reiniciar a API
- ❌ Alterar config.yaml
- ❌ Fazer deploy
- ❌ Alterar nenhum outro arquivo

Os workers já buscam o `cluster` do agente no banco e carregam o módulo dinamicamente.

---

---

# Variáveis de ambiente — referência completa

Todas as variáveis que o sistema precisa em produção no Render:

```bash
# App
APP_ENV=production
LOG_LEVEL=INFO
BASE_URL=https://engenheiro-producao-ai.onrender.com
A2A_ENABLED=true

# Banco de dados (gerado automaticamente pelo Render ao criar o PostgreSQL)
DATABASE_URL=postgresql://...

# LLMs
DEEPSEEK_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Abacatepay
ABACATEPAY_API_KEY=...
ABACATEPAY_WEBHOOK_SECRET=...
ABACATEPAY_SANDBOX_MODE=false

# Microsoft Azure Marketplace
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...

# Kafka (Confluent Cloud ou Upstash)
KAFKA_BOOTSTRAP_SERVERS=pkc-xxx.region.confluent.cloud:9092
KAFKA_API_KEY=...
KAFKA_API_SECRET=...

# Redis (Render managed ou Upstash)
REDIS_URL=redis://...
```

---

# Checklist de execução

## Fase 1 — Estabilização
- [x] 1.1 Trocar print() por logger em subscriptions.py
- [x] 1.2 Ativar assinatura no webhook Stripe (checkout.session.completed)
- [x] 1.3 Ativar assinatura no webhook Abacatepay (checkout.paid)
- [x] 1.4 Reescrever AbacatepayClient com `async with` no httpx
- [x] 1.5 Criar get_settings() com @lru_cache e injetar via Depends
- [x] 1.6 Substituir URL hardcoded por settings.base_url no Microsoft router
- [x] 1.7 Chamar validate() no startup + logar exceções do Azure resolve_purchase
- [x] 1.8 Validar JWT do Azure no webhook Microsoft

## Fase 2 — Banco de dados local
- [ ] 2.1 Criar PostgreSQL no Render (ou usar o do docker-compose local) — **manual**
- [ ] 2.2 Executar SQL de criação das tabelas — **manual**
- [x] 2.3 Criar src/database/postgres_client.py
- [ ] 2.4 Reescrever subscription_activator.py para usar o banco — **pendente (async)**
- [ ] 2.5 Adicionar idempotência nos webhooks (tabela processed_webhook_events) — **manual + código**
- [x] 2.6 Inicializar pool no startup e fechar no shutdown
- [x] 2.7 Atualizar render.yaml com DATABASE_URL
- [ ] 2.8 Popular tabela agent_registry com os 30 agentes atuais — **manual (SQL)**

## Fase 3 — Kafka + Workers
- [ ] 3.1 Configurar tópicos Kafka (docker-compose ou Confluent Cloud) — **manual**
- [x] 3.2 Criar src/messaging/producer.py
- [x] 3.3 Modificar POST /api/agents/execute para enfileirar no Kafka
- [x] 3.4 Criar workers/aec_worker.py + regulatory + microsoft + cross_sell
- [ ] 3.5 Adicionar worker services no render.yaml — **parcial (só DB), workers precisam do Kafka cloud**
- [x] 3.6 Atualizar .env.example com novas variáveis

## Fase 4 — Agent Registry
- [x] 4.1 Criar endpoints GET /agents/registry no router
- [x] 4.2 Criar src/core/agent_loader.py com carregamento dinâmico
- [ ] 4.3 Testar adição de agente 31 sem deploy — **manual (após banco + Kafka)**
- [ ] 4.4 Documentar procedimento de adição de novo agente — **manual**

---

# Resumo de custos estimados (produção)

| Serviço | Provedor | Plano | Custo/mês |
|---|---|---|---|
| API (3 instâncias) | Render | Standard | ~$150 |
| Worker AEC + Regulatory | Render | Worker | ~$100 |
| Worker Microsoft + Cross-sell | Render | Worker | ~$50 |
| PostgreSQL | Render | Standard | $97 |
| Redis | Render / Upstash | Managed | ~$30 |
| Kafka | Confluent Cloud | Basic | ~$50 |
| **Total infra** | | | **~$477/mês** |
| DeepSeek API | DeepSeek | Pay-per-token | variável |
| Gemini API | Google | Pay-per-token | variável |

**Receita mínima para cobrir infra:** 1 cliente no plano Compliance Essencial (R$590/mês ≈ $100) já cobre 20% da infra.
Com 5 clientes no plano básico, a infra está paga.
