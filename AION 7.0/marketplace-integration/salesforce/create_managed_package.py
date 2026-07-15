"""
Cria pacote gerenciado para Salesforce AppExchange.

Pré-requisitos:
- Conta Salesforce Developer
- simple_salesforce instalado (pip install simple-salesforce)
- Connected App configurado no Salesforce

Uso:
    python create_managed_package.py

Saída:
    - Pacote gerenciado criado no Salesforce
    - ID do pacote exibido no console
"""

import os
from dotenv import load_dotenv

load_dotenv()

SALESFORCE_USERNAME = os.getenv("SALESFORCE_USERNAME", "")
SALESFORCE_PASSWORD = os.getenv("SALESFORCE_PASSWORD", "")
SALESFORCE_INSTANCE_URL = os.getenv("SALESFORCE_INSTANCE_URL", "https://login.salesforce.com")
SALESFORCE_CLIENT_ID = os.getenv("SALESFORCE_CLIENT_ID", "")
SALESFORCE_CLIENT_SECRET = os.getenv("SALESFORCE_CLIENT_SECRET", "")


def create_managed_package():
    try:
        from simple_salesforce import Salesforce
    except ImportError:
        print("❌ simple_salesforce não instalado. Execute: pip install simple-salesforce")
        return

    if not all([SALESFORCE_USERNAME, SALESFORCE_PASSWORD]):
        print("❌ Credenciais Salesforce não configuradas no .env")
        print("   Necessário: SALESFORCE_USERNAME, SALESFORCE_PASSWORD")
        return

    sf = Salesforce(
        instance_url=SALESFORCE_INSTANCE_URL,
        client_id=SALESFORCE_CLIENT_ID,
        client_secret=SALESFORCE_CLIENT_SECRET,
        username=SALESFORCE_USERNAME,
        password=SALESFORCE_PASSWORD,
    )

    package_data = {
        "Name": "EcoSystem AEC - Regulatory Agents",
        "NamespacePrefix": "eco_aec",
        "Description": (
            "21 agentes de IA para Arquitetura, Engenharia, "
            "Construcao e Conformidade Regulatoria Brasileira"
        ),
        "Version": "1.0.0",
        "Publisher": "Global Match Engenharia de Producao",
        "PublisherUrl": "https://global-engenharia.com",
    }

    try:
        result = sf.Metadata.create_metadata(
            metadata_type="Package",
            metadata=package_data,
        )
        print(f"✅ Pacote criado: {result.id}")
        print(f"   Nome: {package_data['Name']}")
        print(f"   Namespace: {package_data['NamespacePrefix']}")
        return result.id
    except Exception as e:
        print(f"❌ Erro ao criar pacote: {e}")
        return None


if __name__ == "__main__":
    print("🚀 Criando pacote Salesforce...")
    create_managed_package()
