# n8n-nodes-aion-compliance

n8n community node for AION Compliance. Run compliance checks against the
AION Copilot platform (SOC2, ISO27001, EU AI Act, Contract Risk, Vendor Risk,
NR-1, and more) directly from your n8n workflows.

## Installation

### Self-hosted n8n

```bash
npm install n8n-nodes-aion-compliance
```

### n8n Cloud / Desktop

Settings → Community Nodes → Install → `n8n-nodes-aion-compliance`

## Credentials

| Field | Description |
|-------|-------------|
| Customer Email | The email address used at checkout for your AION subscription. Access is granted per active subscription — there is no separate API key. |
| Base URL | AION API base URL (default: `https://engenheiro-producao-ai.onrender.com`) |

Your subscription must include the service you're calling — the API checks
your plan's agent list on every request and rejects services outside it.

## Available Services

| Service | Description |
|---------|-------------|
| NR-1 Psychosocial Risk (Brazil) | Occupational psychosocial risk assessment |
| LGPD Privacy Scan (Brazil) | Personal data mapping and RoPA |
| EU AI Act Readiness | Classifies AI systems against Regulation (EU) 2024/1689 |
| CSRD Double Materiality | ESG double materiality assessment |
| Carbon Inventory Scope 1+2 | GHG Protocol carbon inventory |
| Vendor Risk Assessment | Third-party risk scoring against 13 real criteria (NIST SP 800-161, ISO 27036-2) |
| Contract Risk Analysis | Contract gap analysis against 15 real clause types |
| M&A Due Diligence | Compliance due diligence for M&A |

## Publishing to the n8n Community Registry

1. Build: `npm run build && npm pack`
2. Publish to npm: `npm publish`
3. The n8n Community Registry indexes it automatically

## Suggested Workflows

1. **Webhook → NR-1 Check → Email Report**
   Receives data via webhook, runs the NR-1 check, emails the report.

2. **Schedule → EU AI Act Check → Slack Notification**
   Weekly EU AI Act readiness check with a Slack alert.

3. **HubSpot Trigger → Vendor Risk Check → Update CRM**
   When a company is created in HubSpot, runs a vendor risk check and
   updates the CRM record.
