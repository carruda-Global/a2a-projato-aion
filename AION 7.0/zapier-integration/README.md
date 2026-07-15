# AION Compliance — Zapier Integration

## Pre-requisitos

```bash
npm install -g zapier-platform-cli
zapier login
```

## Deploy

```bash
cd zapier-integration
npm install
zapier push
```

## Triggers

| Trigger | Description |
|---------|-------------|
| New Compliance Check | Dispara quando um check de compliance é concluido |

## Actions

| Action | Description |
|--------|-------------|
| Run NR-1 Check | Executa diagnostico de riscos psicossociais NR-1 |
| Run LGPD Scan | Executa varredura de dados pessoais LGPD |
| Run EU AI Act Check | Classifica sistemas de IA conforme EU AI Act |
| Create Compliance Report | Gera relatorio consolidado de compliance |

## Searches

| Search | Description |
|--------|-------------|
| Find Subscription | Busca detalhes de assinatura AION |

## Zaps Sugeridos

1. **HubSpot Company Created → Run NR-1 Check → Create Note**
   - Quando uma empresa é criada no HubSpot, executa NR-1 check

2. **Pipefy Card Created → Run LGPD Scan → Update Card Field**
   - Quando um card é criado no Pipefy, executa LGPD scan

3. **New Compliance Check → Send Email → Create Spreadsheet Row**
   - Quando um check termina, notifica por email e registra em planilha

4. **Scheduled Trigger → Run EU AI Act Check → Post in Slack**
   - Verificacao semanal de conformidade EU AI Act
