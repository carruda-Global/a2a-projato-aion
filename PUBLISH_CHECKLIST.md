# Checklist de Publicação — Troca de Links

## ⚠️ Antes de publicar no Microsoft / Salesforce, alterar:

### 1. Render.yaml
- [ ] `A2A_BASE_URL` → novo domínio Render
- [ ] `repo` → (se mudou de repo)

### 2. Config do Settings (src/config.py)
- [ ] `base_url` default (linha 79) — já está como env var `BASE_URL`, só precisa setar no Render

### 3. Arquivos com `engenheiro-producao-ai.onrender.com` hardcoded

**CRÍTICOS (afetam validação Microsoft):**
- [ ] `app/routers/microsoft_marketplace.py` — redirect_url
- [ ] `app/routers/salesforce_marketplace.py` — redirect_url
- [ ] `app/routers/google_marketplace.py` — redirect_url
- [ ] `app/routers/aws_marketplace.py` — redirect_url
- [ ] `app/routers/oracle_marketplace.py` — redirect_url
- [ ] `app/routers/acp_checkout.py` — success_url, cancel_url, website
- [ ] `offers/ecosystem-aec-offer.json` — provisioning_url (6 ocorrências)
- [ ] `render.yaml` — A2A_BASE_URL

**SALESFORCE (managed package):**
- [ ] `salesforce-package/force-app/main/default/connectedApps/EcoSystemAEC.connectedApp-meta.xml` → callbackUrl
- [ ] `salesforce-package/force-app/main/default/namedCredentials/EcoSystemAEC.namedCredential-meta.xml` → parameterValue
- [ ] `salesforce-package/force-app/main/default/namedCredentials/ALMDevOpsCenterHub.namedCredential-meta.xml` → parameterValue
- [ ] `salesforce-package/force-app/main/default/connectedApps/EcoSystemAEC.connectedApp-meta.xml` → contactEmail (se mudou)

**SCRIPTS / DEV:**
- [ ] `.env.example` — A2A_BASE_URL, AWS_SUBSCRIBE_REDIRECT_URL
- [ ] `marketplace-integration/.env.example` — API_BASE_URL
- [ ] `marketplace-integration/scripts/test_marketplaces.py` — BASE_URL
- [ ] `marketplace-integration/salesforce/setup_guide.md`
- [ ] `marketplace-integration/oracle/setup_guide.md`
- [ ] `marketplace-integration/google/setup_guide.md`
- [ ] `dashboard/portal/vercel.json` — VITE_API_URL
- [ ] `dashboard/portal/.env.example` — VITE_API_URL
- [ ] `scripts/setup_stripe_agentic_commerce.py` — image_url, website, support_url, terms_url, privacy_url, endpoint, agent urls
- [ ] `scripts/setup_aws_marketplace.py` — eula_url, support_url, subscribe url
- [ ] `scripts/generate_microsoft_marketplace.py` — base url, subscribe/webhook paths
- [ ] `scripts/test_render.py` — base
- [ ] `scripts/setup_a2a_protocol.py` — comentário
- [ ] `scripts/setup_producao.py` — prints
- [ ] `scripts/publish_swarms_cloud.py` — API_BASE
- [ ] `offers/architecture.txt`
- [ ] `src/a2a_bridge/executors.py` — texto de assinatura
- [ ] `src/a2a_bridge/agent_cards.py` — documentation_url
- [ ] `scripts/test_live_checkout.py`

### 4. Variáveis de ambiente no Render
- [ ] `BASE_URL=https://seu-novo-dominio.onrender.com`
- [ ] `AZURE_TENANT_ID`
- [ ] `AZURE_CLIENT_ID`
- [ ] `AZURE_CLIENT_SECRET`

### 5. Microsoft Partner Center
- [ ] Landging page URL (termo, privacidade, suporte) — deve apontar para o site global-match, NÃO para o Render
- [ ] Fulfillment webhook URL → `https://seu-novo-dominio.onrender.com/microsoft/fulfill`
- [ ] Webhook URL → `https://seu-novo-dominio.onrender.com/microsoft/webhook`

### 6. Salesforce AppExchange
- [ ] Managed package namespace registrado no Partner Portal
- [ ] `sfdx-project.json` → namespace preenchido
- [ ] Security review (se necessário)
- [ ] Package version criada e upload feita
