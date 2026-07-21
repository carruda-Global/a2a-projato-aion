# AION Voice Receptionist — Zapier Integration

Real REST Hook app backed by `app/routers/zapier_integration.py` and `app/routers/voice_agent.py` in the main AION 7.0 backend. Not yet published to Zapier's app directory — this is the code, waiting on `zapier register` + `zapier push` (interactive, requires a Zapier developer login).

## Pre-requisitos

```bash
npm install -g zapier-platform-cli
zapier login
```

## Primeira publicação (só uma vez)

Este app ainda não tem um App ID registrado na Zapier (diferente do `zapier-integration/` do AION Compliance, que já tem). Rodar, dentro desta pasta:

```bash
cd zapier-integration-voice
npm install
zapier register "AION Voice Receptionist"
```

Isso gera um `.zapierapprc` real com o App ID — depois disso, os deploys seguintes usam `zapier push` normalmente. Depois de registrado e publicado (mesmo em modo privado/"unlisted"), o app aparece pesquisável dentro do editor de Zaps de quem tiver o link de convite, e submeter pra revisão pública da Zapier o torna buscável no diretório geral — e isso sozinho já é um backlink de zapier.com pra global-engenharia.com.

## Deploy (após o primeiro registro)

```bash
npm install
zapier push
```

## Authentication

Custom auth: `customer_email` + `base_url` (default: o backend de produção). Testado contra `GET /api/v1/subscriptions/by-email/{email}` — o mesmo endpoint genérico usado pelo app de Compliance, já cobre qualquer plano incluindo os da Voice Receptionist.

## Triggers

| Trigger | Description |
|---------|-------------|
| New Call Completed | Dispara quando a recepcionista de IA termina uma ligação — duração, desfecho, transcript |
| New Lead Captured | Dispara quando a recepcionista captura nome, telefone e motivo da ligação de um lead |

Ambos são REST Hooks reais: `performSubscribe`/`performUnsubscribe` chamam `POST /zapier/webhook/subscribe` e `DELETE /zapier/webhook/subscribe/{id}` (já em produção), com `performList` como fallback de polling pro passo de teste da Zapier, usando `GET /api/voice-agent/calls/{email}`.

## Searches

| Search | Description |
|--------|-------------|
| Find Subscription | Busca detalhes da assinatura AION Voice Receptionist |

## Zaps sugeridos pra vitrine na listagem

- "New Lead Captured" → cria contato no HubSpot/Pipedrive
- "New Call Completed" → registra linha numa planilha do Google Sheets
- "New Lead Captured" → envia SMS de follow-up via Twilio
