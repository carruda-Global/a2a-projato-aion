# oracle_marketplace/oci_auth.py
import os
from oci.config import from_file

def get_oracle_config():
    """Obtém configuração da Oracle Cloud a partir de variáveis de ambiente"""
    return {
        "tenancy": os.getenv("ORACLE_TENANCY_OCID"),
        "user": os.getenv("ORACLE_USER_OCID"),
        "fingerprint": os.getenv("ORACLE_FINGERPRINT"),
        "key_file": os.getenv("ORACLE_PRIVATE_KEY_PATH"),
        "region": os.getenv("ORACLE_REGION", "sa-saopaulo-1")
    }

def test_oracle_connection():
    """Testa conexão com Oracle Cloud"""
    from oci.marketplace import MarketplaceClient
    config = get_oracle_config()
    client = MarketplaceClient(config)
    response = client.list_public_packages()
    print(f"✅ Conexão Oracle OK: {len(response.data)} pacotes encontrados")