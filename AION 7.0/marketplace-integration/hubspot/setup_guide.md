# HubSpot App Marketplace — Setup Guide

## 1. Project Scaffold (HubSpot CLI)

The app is managed as a HubSpot developer **Project**, not a manually-created app in the old dashboard flow.

```bash
npm i -g @hubspot/cli
hs account auth --personal-access-key --use-default-name --default
hs project create --name="AION Compliance" --dest="hubspot-marketplace-app" \
  --project-base=app --distribution=marketplace --auth=oauth --features=webhooks
```

This scaffolds `hubspot-marketplace-app/` with:
- `src/app/app-hsmeta.json` — app config (name, description, OAuth, scopes, support info)
- `src/app/webhooks/webhooks-hsmeta.json` — webhook target and CRM subscriptions

Edit those two files directly, then validate and upload:

```bash
hs project validate
hs project upload --forceCreate   # first upload creates the app; auto-deploys on success
```

## 2. App Configuration (`app-hsmeta.json`)

- **Name:** AION Compliance
- **Description:** 19 deterministic AI Copilots covering NR-1, LGPD/Whistleblower (EU Directive 2019/1937), EU AI Act, CSRD Double Materiality, SOC 2 and ISO 27001, plus GHG Protocol carbon/Scope 3 inventory, Brazilian tax reform (CBS/IBS) and pay-equity readiness — automated regulatory readiness checks, backed by real regulatory catalogs (not LLM guesswork), directly from your CRM records.
- **Distribution:** `marketplace`
- **Redirect URL:** `https://engenheiro-producao-ai.onrender.com/hubspot/oauth/callback`
- **Required scopes** (must match the default scope list in `src/monetization/hubspot_client.py`):
  - `oauth`
  - `crm.objects.companies.read`
  - `crm.objects.companies.write`
  - `crm.objects.contacts.read`
  - `crm.objects.contacts.write`
  - `crm.objects.custom.read`
  - `crm.objects.custom.write`
  - `crm.schemas.companies.read`
  - `crm.schemas.contacts.read`
  - `crm.schemas.custom.read`

> Do not add CMS (`cms.*`) or developer-platform (`developer.*`) scopes — this app only reads/writes CRM records, and those scopes are rejected by the portal for this app type (`cms.source_code.read` failed deploy with "scope could not be recognized").

## 3. Configure Render

Once the app is created, get **Client ID** / **Client Secret** / **App ID** from the Developer Portal (`Auth` tab of the app project) and add them to Render (Dashboard → Environment):

```bash
HUBSPOT_CLIENT_ID=your-client-id
HUBSPOT_CLIENT_SECRET=your-client-secret
HUBSPOT_APP_ID=your-app-id
```

## 4. Webhooks (`webhooks-hsmeta.json`)

- **Target URL:** `https://engenheiro-producao-ai.onrender.com/hubspot/webhook`
- **Active subscriptions:** `object.creation` for `contact` and `company`

Backend endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/hubspot/install` | Redirects to HubSpot OAuth |
| GET | `/hubspot/oauth/callback` | OAuth callback — activates subscription |
| POST | `/hubspot/webhook` | Receives CRM events (contact/company/deal changes) |
| POST | `/hubspot/compliance-check` | Runs a compliance check on a HubSpot object |
| GET | `/hubspot/plans` | Lists available plans |

## 5. Submit to the Marketplace

1. In the Developer Portal, go to "App Marketplace" → "Manage listing"
2. Fill in:
   - **Listing description** — highlight NR-1, LGPD, EU AI Act
   - **Screenshots** — 4-6 screenshots of the flow
   - **Pricing** — "Free trial available" or "Starting at $49/month"
   - **Categories:** "Compliance & Legal", "AI & Machine Learning"
3. Submit for review

## 6. Test the Install Flow

```bash
# Simulate installation
curl "https://engenheiro-producao-ai.onrender.com/hubspot/install"

# After OAuth, check status
curl "https://engenheiro-producao-ai.onrender.com/hubspot/portal/{portal_id}/status"

# Run a compliance check
curl -X POST "https://engenheiro-producao-ai.onrender.com/hubspot/compliance-check" \
  -H "Content-Type: application/json" \
  -d '{"portal_id":"12345","access_token":"...","object_type":"company","object_id":"67890","service":"compliance-nr1"}'

# List plans
curl "https://engenheiro-producao-ai.onrender.com/hubspot/plans"
```
