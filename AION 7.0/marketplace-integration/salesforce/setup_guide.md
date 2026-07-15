# Salesforce AppExchange — Guia de Configuração

## Pré-requisitos

1. Conta [Salesforce Developer](https://developer.salesforce.com)
2. Ambiente Salesforce configurado
3. simple_salesforce instalado

## Passos

### 1. Criar Connected App

- Setup > App Manager > New Connected App
- Enable OAuth Settings
- Callback URL: `https://engenheiro-producao-ai.onrender.com/oauth/callback`
- Scopes: Full access, Refresh token

### 2. Criar Pacote

```bash
cd marketplace-integration
cp .env.example .env
# Editar credenciais Salesforce
python salesforce/create_managed_package.py
```

### 3. Security Review

```bash
python salesforce/security_review.py
```

O relatório `security_review.md` será gerado com o checklist completo.
Complete os itens pendentes antes de submeter.

### 4. Publicar

- Submeter pacote no [Salesforce Partner Portal](https://partners.salesforce.com)
- Anexar relatório de segurança
- Aguardar aprovação do Security Review

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/salesforce-marketplace/subscribe` | Assinatura |
| POST | `/api/v1/salesforce-marketplace/webhook` | Webhook eventos |
| GET | `/api/v1/salesforce-marketplace/plans` | Listar planos |
