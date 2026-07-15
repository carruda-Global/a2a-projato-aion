# 🚀 PLANO DE AÇÃO — INTEGRAÇÃO COM MARKETPLACES (Google, Oracle, Salesforce)

**Projeto:** EcoSystem AEC + Regulatory — 21 Agentes de IA
**Proprietário:** Cristiano Arruda | Global Match Engenharia de Produção
**Versão:** 2.0
**Data:** 22/06/2026

---

## 📋 ÍNDICE

1. [Status Atual](#status-atual)
2. [Fase 0: Preparação](#fase-0-preparação)
3. [Fase 1: Google Cloud Marketplace](#fase-1-google-cloud-marketplace)
4. [Fase 2: Oracle Cloud Marketplace](#fase-2-oracle-cloud-marketplace)
5. [Fase 3: Salesforce AppExchange](#fase-3-salesforce-appexchange)
6. [Fase 4: Testes e Validação](#fase-4-testes-e-validação)
7. [Checklist Final](#checklist-final)

---

## STATUS ATUAL

| Marketplace | Código | Conta | Publicado |
|-------------|--------|-------|-----------|
| Google Cloud | ✅ `app/routers/google_marketplace.py` | 🔧 Projeto criado | ⬜ |
| Oracle Cloud | ✅ `app/routers/oracle_marketplace.py` | ⬜ Partner | ⬜ |
| Salesforce | ✅ `app/routers/salesforce_marketplace.py` | ⬜ Developer | ⬜ |
| AWS | ✅ `app/routers/aws_marketplace.py` | ⬜ Partner | ⬜ |

---

## FASE 0: PREPARAÇÃO

### 0.1 Contas e Credenciais (Manual)

| # | Tarefa | Onde Fazer | Prioridade |
|---|--------|------------|------------|
| 0.1 | 🔴 Ativar partner no Google Cloud | [Partner Console](https://console.cloud.google.com/partners) | Alta |
| 0.2 | 🔴 Criar Service Account e baixar JSON | GCP > IAM > Service Accounts | Alta |
| 0.3 | 🟡 Criar conta partner Oracle | [Oracle Partner Portal](https://partner.oracle.com) | Média |
| 0.4 | 🟡 Instalar/configurar WIND CLI | `pip install wind-cli` | Média |
| 0.5 | 🟢 Criar conta Salesforce Developer | [Developer Edition](https://developer.salesforce.com) | Baixa |
| 0.6 | 🟢 Configurar Connected App no Salesforce | Setup > App Manager | Baixa |

### 0.2 Estrutura do Projeto (Já Implementada)

```
engenheiro-producao-ai/
├── marketplace-integration/          # Scripts de publicação
│   ├── google/create_offer.py        # Cria oferta no GCP
│   ├── oracle/wind_automation.py     # Cria listagem na Oracle
│   ├── salesforce/create_managed_package.py
│   ├── salesforce/security_review.py
│   └── scripts/test_marketplaces.py
│
├── app/routers/
│   ├── google_marketplace.py         # Webhook + Fulfillment + Subscribe
│   ├── oracle_marketplace.py         # Activate + Webhook + Subscriptions
│   ├── salesforce_marketplace.py     # Subscribe + Webhook
│   ├── aws_marketplace.py            # Subscribe + SNS + Entitlement
│   └── cross_selling.py             # Upgrade paths
│
├── src/monetization/
│   ├── google_client.py             # GoogleCloudMarketplaceClient
│   ├── oracle_client.py             # OracleMarketplaceClient
│   ├── aws_client.py                # AWSMarketplaceClient
│   └── plans.py                     # 9 planos de assinatura
│
└── config.yaml                      # Config centralizada
```

---

## FASE 1: Google Cloud Marketplace

### 1.1 Criar Service Account (Manual — 10 min)

```bash
# Acessar: https://console.cloud.google.com/iam-admin/serviceaccounts
# Projeto: global-engenharia-498823

# 1. Criar SA "marketplace-publisher"
# 2. Papel: "Marketplace Admin" (roles/cloudmarketplace.admin)
# 3. Gerar chave JSON → salvar como marketplace-integration/service-account.json
```

### 1.2 Criar Oferta (Automático)

```bash
cd marketplace-integration
pip install -r requirements.txt
cp .env.example .env
# Editar GOOGLE_APPLICATION_CREDENTIALS
python google/create_offer.py
```

### 1.3 Configurar Webhook (Manual — 15 min)

```bash
# 1. No GCP: Pub/Sub > Criar tópico "ecosystem-aec-webhook"
# 2. Criar subscription: push para:
#    https://engenheiro-producao-ai.onrender.com/api/v1/google-marketplace/webhook
# 3. Eventos: ENTITLEMENT_CREATED, CANCELLED, SUSPENDED, RENEWED
```

### 1.4 Endpoints Publicados

| Método | Endpoint | Função |
|--------|----------|--------|
| GET | `/api/v1/google-marketplace/subscribe` | Assinar plano |
| POST | `/api/v1/google-marketplace/webhook` | Webhook Pub/Sub |
| POST | `/api/v1/google-marketplace/fulfill` | Fulfillment API |
| GET | `/api/v1/google-marketplace/entitlement/{id}` | Verificar entitlement |
| GET | `/api/v1/google-marketplace/plans` | Listar planos |

---

## FASE 2: Oracle Cloud Marketplace

### 2.1 Conta Partner (Manual — 30 min)

- Acessar: https://partner.oracle.com
- Criar conta como "Independent Software Vendor"
- Configurar perfil de pagamento

### 2.2 Configurar OCI (Manual — 15 min)

```
# Instalar WIND CLI
pip install wind-cli

# Configurar OCI
oci setup config
# Region: sa-saopaulo-1
# Tenancy OCID, User OCID, fingerprint, private key
```

### 2.3 Criar Listagem (Automático + Manual)

```bash
cd marketplace-integration
python oracle/wind_automation.py
# Comando gerado: wind marketplace create-listing --config listing_config.yaml
```

### 2.4 Endpoints Publicados

| Método | Endpoint | Função |
|--------|----------|--------|
| GET | `/api/v1/oracle-marketplace/activate` | Ativar assinatura |
| POST | `/api/v1/oracle-marketplace/webhook` | Webhook eventos |
| GET | `/api/v1/oracle-marketplace/subscriptions` | Listar assinaturas |
| GET | `/api/v1/oracle-marketplace/subscription/{id}` | Verificar assinatura |
| GET | `/api/v1/oracle-marketplace/plans` | Listar planos |

---

## FASE 3: Salesforce AppExchange

### 3.1 Ambiente Developer (Manual — 20 min)

- Criar conta em: https://developer.salesforce.com
- Setup > App Manager > New Connected App
- OAuth: Full access + Refresh token

### 3.2 Criar Pacote (Automático)

```bash
cd marketplace-integration
cp .env.example .env
# Editar SALESFORCE_USERNAME, SALESFORCE_PASSWORD
python salesforce/create_managed_package.py
```

### 3.3 Security Review (Automático + Manual)

```bash
python salesforce/security_review.py
# Completar itens pendentes no relatório gerado
```

### 3.4 Endpoints Publicados

| Método | Endpoint | Função |
|--------|----------|--------|
| GET | `/api/v1/salesforce-marketplace/subscribe` | Assinar plano |
| POST | `/api/v1/salesforce-marketplace/webhook` | Webhook eventos |
| GET | `/api/v1/salesforce-marketplace/plans` | Listar planos |

---

## FASE 4: Testes e Validação

### 4.1 Testes Automatizados

```bash
cd marketplace-integration
python scripts/test_marketplaces.py
```

### 4.2 Testes Manuais

- Google: Assinar → Verificar entitlement → Cancelar
- Oracle: Ativar → Listar subscriptions → Verificar status
- Salesforce: Assinar → Simular webhook → Verificar

---

## CHECKLIST FINAL

### 🔴 Faça Primeiro (Google Cloud)

- [ ] Conta partner ativada no Google Cloud
- [ ] Service Account criada com permissão Marketplace Admin
- [ ] GOOGLE_APPLICATION_CREDENTIALS configurado
- [ ] Executar `python google/create_offer.py`
- [ ] Configurar webhook Pub/Sub
- [ ] Testar assinatura completa

### 🟡 Faça Depois (Oracle Cloud)

- [ ] Conta partner Oracle criada
- [ ] OCI configurado (~/.oci/config)
- [ ] WIND CLI instalado
- [ ] Executar `python oracle/wind_automation.py`
- [ ] Configurar produto SaaS no portal
- [ ] Testar ativação

### 🟢 Faça por Último (Salesforce)

- [ ] Conta Developer criada
- [ ] Connected App configurado
- [ ] Executar `python salesforce/create_managed_package.py`
- [ ] Executar `python salesforce/security_review.py`
- [ ] Submeter Security Review
- [ ] Publicar no AppExchange
