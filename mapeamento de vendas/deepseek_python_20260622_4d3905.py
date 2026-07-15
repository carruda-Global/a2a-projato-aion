# salesforce_marketplace/create_managed_package.py
from simple_salesforce import Salesforce
import os

def create_managed_package():
    sf = Salesforce(
        instance_url=os.getenv('SALESFORCE_INSTANCE_URL'),
        client_id=os.getenv('SALESFORCE_CLIENT_ID'),
        client_secret=os.getenv('SALESFORCE_CLIENT_SECRET'),
        username=os.getenv('SALESFORCE_USERNAME'),
        password=os.getenv('SALESFORCE_PASSWORD')
    )
    
    # 1. Cria pacote gerenciado
    package = {
        "Name": "EcoSystem AEC - Regulatory Agents",
        "NamespacePrefix": "eco_aec",
        "Description": "21 agentes de IA para compliance regulatório"
    }
    
    result = sf.Metadata.create_metadata(
        metadata_type="Package",
        metadata=package
    )
    
    print(f"✅ Pacote criado: {result.id}")
    
    # 2. Adiciona componentes
    # ... código para adicionar Apex, Lightning, etc.
    
    return result.id

if __name__ == '__main__':
    create_managed_package()