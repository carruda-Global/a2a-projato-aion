# 1. Clonar estrutura
cd marketplace-integration

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Editar .env com suas credenciais

# 5. Criar oferta no Google
python google_marketplace/create_offer.py

# 6. Criar listagem na Oracle
python oracle_marketplace/wind_automation.py

# 7. Criar pacote Salesforce
python salesforce_marketplace/create_managed_package.py

# 8. Executar testes
python scripts/test_marketplaces.py