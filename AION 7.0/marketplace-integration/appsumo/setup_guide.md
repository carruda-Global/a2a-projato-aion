# AppSumo — Setup Guide

## 1. Create a Partner/Vendor Account

1. Go to https://appsumo.com/sell/
2. Create a partner account
3. Fill in the company profile (Global Match Engenharia)
4. Once approved, AppSumo issues a single **API Key** — this is used for both
   the Partner API and for signing webhooks (there is no separate webhook
   secret; per the [AppSumo Licensing API v2 docs](https://docs.licensing.appsumo.com/webhook/webhook__security.html),
   "AppSumo and the partner share an API Key used for both encryption and
   API requests").

## 2. Create the Deal

In the AppSumo Vendor Dashboard:

- **Product Name:** AION Compliance
- **Tagline:** AI Copilots for SOC2, ISO27001, EU AI Act and engineering compliance
- **Description:** Deterministic AI Copilots — real regulatory catalogs (AICPA, ISO 27001 Annex A, EU AI Act Articles 5/50/Annex III), not LLM guesswork. Audit-ready reports in 48h.
- **Category:** "SaaS" → "Compliance" / "AI"

### Suggested Pricing Tiers

| Tier | Internal Plan | AppSumo Price | Original Price |
|------|---------------|----------------|-----------------|
| Tier 1 (Starter) | `compliance_essencial` | $49 | $149/mo |
| Tier 2 (Growth) | `regulatory_pro` | $149 | $379/mo |
| Tier 3 (Ultimate) | `full_suite` | $299 | $4,999/mo |

## 3. Configure the Webhook

In the AppSumo Vendor Dashboard:

- **Webhook URL:** `https://engenheiro-producao-ai.onrender.com/appsumo/webhook`
- **Secret:** use the same API Key AppSumo issued in step 1, set as
  `APPSUMO_WEBHOOK_SECRET` in Render.

### How AppSumo signs webhooks (real spec, not assumed)

Every webhook carries two headers:
- `X-Appsumo-Timestamp` — a timestamp
- `X-Appsumo-Signature` — HMAC-SHA256 of `timestamp + raw request body`, keyed
  with the shared API Key

`app/routers/appsumo_marketplace.py`'s `_verify_signature()` implements this
exact scheme and fails closed (401) if `APPSUMO_WEBHOOK_SECRET` isn't set or
the signature doesn't match. **Before going live, send one real test webhook
from the AppSumo dashboard and confirm it verifies** — the exact
timestamp+body concatenation format (no separator vs. a delimiter) wasn't
fully confirmed from the public docs alone.

## 4. License API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/appsumo/webhook` | Receives activate/refund/cancel events |
| POST | `/appsumo/license/activate` | Activates an AppSumo license key |
| POST | `/appsumo/license/validate` | Validates a license key |
| GET | `/appsumo/plans` | Lists AppSumo tiers |

## 5. User Flow

1. User buys on AppSumo
2. AppSumo sends an `activate` webhook with `plan_id` and `activation_email`
3. AION generates a license key and activates the subscription
4. User does a POST to `/appsumo/license/activate` with the license key
5. User gets dashboard access with lifetime access (lifetime deal)

## 6. Configure in Render

```bash
APPSUMO_WEBHOOK_SECRET=<the API Key AppSumo issued in step 1>
```

## 7. Test

```bash
# Simulate AppSumo activation — the signature below is for illustration only;
# generate a real one with the actual secret and timestamp before testing.
curl -X POST "https://engenheiro-producao-ai.onrender.com/appsumo/webhook" \
  -H "Content-Type: application/json" \
  -H "x-appsumo-timestamp: 1735776000" \
  -H "x-appsumo-signature: <hmac-sha256(timestamp + body, APPSUMO_WEBHOOK_SECRET)>" \
  -d '{"action":"activate","plan_id":"aion_compliance_tier1","uuid":"test-uuid-123","activation_email":"customer@example.com"}'
```
