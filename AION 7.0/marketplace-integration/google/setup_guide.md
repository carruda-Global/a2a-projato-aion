# Google Cloud Marketplace — Guia de Configuração

## Pré-requisitos

1. Conta de partner no [Google Cloud Partner Console](https://console.cloud.google.com/partners)
2. Projeto `global-engenharia-498823` criado
3. Service Account com permissão `Marketplace Admin`

## Passos

### 1. Criar Service Account

```bash
# No Cloud Console:
# IAM > Service Accounts > Criar SA
# Nome: marketplace-publisher
# Papel: Marketplace Admin (roles/cloudmarketplace.admin)
# Chave JSON: Baixar como service-account.json
```

### 2. Criar Oferta via API

```bash
cd marketplace-integration
pip install -r requirements.txt
cp .env.example .env
# Editar GOOGLE_APPLICATION_CREDENTIALS no .env
python google/create_offer.py
```

### 3. Configurar Webhook no Google Pub/Sub

- Criar tópico Pub/Sub: `ecosystem-aec-webhook`
- Configurar subscription para enviar ao endpoint:
  `https://engenheiro-producao-ai.onrender.com/api/v1/google-marketplace/webhook`
- Publicar eventos: `ENTITLEMENT_CREATED`, `ENTITLEMENT_CANCELLED`, etc.

### 4. Testar

```bash
python scripts/test_marketplaces.py
```

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/google-marketplace/subscribe` | Assinatura |
| POST | `/api/v1/google-marketplace/webhook` | Webhook Pub/Sub |
| POST | `/api/v1/google-marketplace/fulfill` | Fulfillment API |
| GET | `/api/v1/google-marketplace/entitlement/{id}` | Verificar entitlement |
| GET | `/api/v1/google-marketplace/plans` | Listar planos |
