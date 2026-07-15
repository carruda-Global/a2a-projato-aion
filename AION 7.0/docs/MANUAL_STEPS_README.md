# AION v6.0 — Itens Manuais (🔴) para nota 10/10

## 1. Revogar e Regenerar Credenciais Comprometidas

Acessar cada dashboard e revogar as chaves abaixo, depois regenerar:

| Credencial | Dashboard | Ação |
|---|---|---|
| Stripe live key (`sk_live_...`) | https://dashboard.stripe.com/apikeys | Revogar → criar nova |
| Stripe webhook secret (`whsec_...`) | https://dashboard.stripe.com/webhooks | Regenerar signing secret |
| Supabase anon/key | https://supabase.com/dashboard → Settings → API | Revogar → criar nova |
| DeepSeek API key (`sk-...`) | https://platform.deepseek.com/api_keys | Revogar → criar nova |
| GitHub PAT (`ghp_...`) | https://github.com/settings/tokens | Revogar → criar novo |
| Swarms API key | https://swarms.world/dashboard | Revogar → criar nova |
| Vault root token | Servidor Vault | `vault token revoke <token>` → `vault token create` |

## 2. Configurar Variáveis de Ambiente no Render

Acessar https://dashboard.render.com → hmas-orchestrator → Environment:

```
AZURE_TENANT_ID=<seu-tenant-id>
AZURE_CLIENT_ID=<seu-client-id>
AZURE_CLIENT_SECRET=<seu-client-secret>
SUPABASE_URL=https://<seu-projeto>.supabase.co
DATABASE_URL=postgresql://<user>:<pass>@<host>:<port>/<db>
```

## 3. Partner Center — Configuração Técnica

Acessar https://partner.microsoft.com → Offer → Technical Configuration:

| Campo | Valor |
|---|---|
| Landing Page URL | `https://engenheiro-producao-ai.onrender.com/` |
| Privacy URL | `https://engenheiro-producao-ai.onrender.com/api/privacy/policy` |
| Terms URL | `https://engenheiro-producao-ai.onrender.com/api/privacy/terms` |
| Fulfillment Webhook | `https://engenheiro-producao-ai.onrender.com/microsoft/fulfill` |
| Webhook URL | `https://engenheiro-producao-ai.onrender.com/microsoft/webhook` |

## 4. Separar Webhooks Stripe (Test vs Production)

No Stripe Dashboard, criar **2 endpoints separados**:

| Ambiente | URL | Secret |
|---|---|---|
| Test | `https://engenheiro-producao-ai.onrender.com/api/webhook/stripe` | `whsec_test_...` |
| Production | `https://engenheiro-producao-ai.onrender.com/api/webhook/stripe` | `whsec_live_...` |

Configurar `.env` com `STRIPE_WEBHOOK_SECRET` apontando para o correto conforme ambiente.
