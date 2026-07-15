# Pipefy Ecosystem — Setup Guide

## Status: provisioned

The 3 compliance Pipes and their webhooks were created programmatically via
the Pipefy GraphQL API (`createPipe` / `createWebhook` / `updateWebhook`
mutations) under the "Global Match Engenharia" organization (org id
`302509017`):

| Pipe | Pipe ID | Function |
|------|---------|----------|
| AION NR-1 Psicossocial | `307234078` | Psychosocial risk diagnosis |
| AION LGPD Scanner | `307234079` | Personal data sweep |
| AION EU AI Act | `307234080` | AI system classification |

Each Pipe has phases (Pending → Processing → Completed) and start-form
fields: `service` (short_text), `card_id` (short_text), `status` (select:
pending/processing/completed/error), `result` (long_text).

## Webhook Authentication

Pipefy webhooks do **not** compute a request signature — `createWebhook`'s
`headers` field lets you attach a static header that Pipefy echoes back
verbatim on every call. All 3 webhooks are configured with:

```
X-Pipefy-Webhook-Secret: <PIPEFY_WEBHOOK_SECRET value>
```

`app/routers/pipefy_marketplace.py`'s `/webhook` handler verifies this
header with a constant-time comparison (`verify_static_secret_header` in
`app/app_utils/marketplace_auth.py`) and fails closed (401) if
`PIPEFY_WEBHOOK_SECRET` isn't configured or doesn't match.

## Configure in Render

```bash
PIPEFY_API_KEY=<personal access token from app.pipefy.com>
PIPEFY_ORG_ID=302509017
PIPEFY_PIPE_COMPLIANCE_NR1=307234078
PIPEFY_PIPE_COMPLIANCE_LGPD=307234079
PIPEFY_PIPE_COMPLIANCE_EU_AI_ACT=307234080
PIPEFY_WEBHOOK_SECRET=<the value configured on the 3 webhooks>
```

## 5. Endpoints da API

| Metodo | Path | Descricao |
|--------|------|-----------|
| POST | `/pipefy/webhook` | Recebe eventos Pipefy |
| POST | `/pipefy/run-check` | Executa check de compliance em card |
| GET | `/pipefy/subscribe` | Ativa assinatura para organizacao |
| GET | `/pipefy/plans` | Lista planos |

## 6. Fluxo de Uso

1. Instala o app AION no Pipefy Ecosystem
2. Adiciona o Pipe "AION Compliance" ao seu organization
3. Cria um card no Pipe com os dados da empresa
4. O webhook dispara e o AION executa o check de compliance
5. Resultado é escrito de volta no card
