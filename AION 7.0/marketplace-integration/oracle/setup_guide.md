# Oracle Cloud Marketplace — Guia de Configuração

## Pré-requisitos

1. Conta de partner no [Oracle Partner Portal](https://partner.oracle.com)
2. Tenancy OCI configurado
3. WIND CLI instalado
4. Chaves de API OCI em `~/.oci/config`

## Passos

### 1. Configurar OCI

```bash
# Instalar WIND CLI
pip install wind-cli

# Configurar ~/.oci/config
oci setup config
# Region: sa-saopaulo-1
```

### 2. Gerar Config e Criar Listagem

```bash
cd marketplace-integration
python oracle/wind_automation.py
```

### 3. Configurar Assinatura via SaaS

- No Oracle Partner Portal, configurar o produto como SaaS
- Vincular o plano de assinatura ao endpoint:
  `https://engenheiro-producao-ai.onrender.com/api/v1/oracle-marketplace/activate`

### 4. Testar

```bash
python scripts/test_marketplaces.py
```

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/oracle-marketplace/activate` | Ativar assinatura |
| POST | `/api/v1/oracle-marketplace/webhook` | Webhook eventos |
| GET | `/api/v1/oracle-marketplace/subscriptions` | Listar assinaturas |
| GET | `/api/v1/oracle-marketplace/plans` | Listar planos |
