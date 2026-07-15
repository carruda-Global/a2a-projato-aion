#!/bin/bash
# Script para criar/publicar em todos os marketplaces

echo "=========================================="
echo "  DEPLOY EM TODOS OS MARKETPLACES"
echo "=========================================="
echo ""

# 1. Verificar ambiente
echo "[1/4] Verificando ambiente..."
python -c "import dotenv, yaml, google.auth, oci" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependências faltando. Execute: pip install -r requirements.txt"
    exit 1
fi
echo "✅ Ambiente OK"
echo ""

# 2. Google Cloud Marketplace
echo "[2/4] Google Cloud Marketplace..."
python google/create_offer.py
echo ""

# 3. Oracle Cloud Marketplace
echo "[3/4] Oracle Cloud Marketplace..."
python oracle/wind_automation.py
echo ""

# 4. Salesforce
echo "[4/4] Salesforce AppExchange..."
python salesforce/create_managed_package.py
python salesforce/security_review.py
echo ""

# 5. Testes
echo "=========================================="
echo "  EXECUTANDO TESTES..."
echo "=========================================="
python scripts/test_marketplaces.py
