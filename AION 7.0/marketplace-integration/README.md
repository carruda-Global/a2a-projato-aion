# 🌐 Marketplace Integration — EcoSystem AEC + Regulatory

Scripts e guias para publicar os 21 agentes nos marketplaces.

## Estrutura

```
marketplace-integration/
├── google/          # Google Cloud Marketplace
│   ├── create_offer.py    # Cria oferta via API
│   └── setup_guide.md     # Passo a passo manual
├── oracle/          # Oracle Cloud Marketplace
│   ├── wind_automation.py # Cria listagem via WIND CLI
│   └── setup_guide.md
├── salesforce/      # Salesforce AppExchange
│   ├── create_managed_package.py
│   ├── security_review.py
│   └── setup_guide.md
├── scripts/
│   ├── test_marketplaces.py
│   └── deploy_all.sh
├── requirements.txt
└── .env.example
```

## Pré-requisitos

1. Contas de partner em cada marketplace
2. Service Accounts / API Keys configuradas
3. Python 3.12+ com dependências instaladas

## Uso Rápido

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar credenciais
cp .env.example .env
# Editar .env com suas chaves

# 3. Executar cada marketplace
python google/create_offer.py
python oracle/wind_automation.py
python salesforce/create_managed_package.py

# 4. Testar
python scripts/test_marketplaces.py
```

## Fluxo de Publicação

1. **Google Cloud**: Criar oferta → Configurar entitlement → Ativar webhook
2. **Oracle Cloud**: Criar listagem → Configurar pricing → Associar subscription
3. **Salesforce**: Criar pacote → Security Review → Publicar
