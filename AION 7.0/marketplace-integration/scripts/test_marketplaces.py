"""
Testes de conectividade com os marketplaces.

Uso:
    python scripts/test_marketplaces.py

Saída:
    - Status de cada marketplace (✅ / ❌)
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "https://engenheiro-producao-ai.onrender.com")


def test_google_marketplace():
    print("\n🔵 Google Cloud Marketplace")
    print("-" * 50)

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")

    if not creds_path or not os.path.exists(creds_path):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS não encontrado")
        print(f"   Caminho: {creds_path}")
        return False

    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT_ID não configurado")
        return False

    try:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_file(creds_path)
        print(f"✅ Credenciais OK: {creds.service_account_email}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_oracle_marketplace():
    print("\n🟠 Oracle Cloud Marketplace")
    print("-" * 50)

    config_path = os.path.expanduser("~/.oci/config")
    if not os.path.exists(config_path):
        print("❌ ~/.oci/config não encontrado")
        return False

    try:
        import oci
        config = oci.config.from_file()
        print(f"✅ Config OCI OK: {config.get('user', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_salesforce():
    print("\n🟢 Salesforce AppExchange")
    print("-" * 50)

    username = os.getenv("SALESFORCE_USERNAME", "")
    password = os.getenv("SALESFORCE_PASSWORD", "")

    if not username or not password:
        print("❌ Credenciais Salesforce não configuradas")
        return False

    try:
        from simple_salesforce import Salesforce
        sf = Salesforce(username=username, password=password)
        print(f"✅ Conexão OK: {sf.session_id[:20]}...")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_api_endpoints():
    print("\n🌐 API Endpoints")
    print("-" * 50)

    try:
        import requests
        health = requests.get(f"{BASE_URL}/health", timeout=10)
        if health.status_code == 200:
            print(f"✅ Health check OK: {health.status_code}")
        else:
            print(f"❌ Health check: {health.status_code}")

        plans = requests.get(f"{BASE_URL}/api/v1/google-marketplace/plans", timeout=10)
        if plans.status_code == 200:
            plans_data = plans.json()
            print(f"✅ Google plans: {len(plans_data.get('plans', []))} planos")
        else:
            print(f"❌ Google plans: {plans.status_code}")

        oracle_plans = requests.get(f"{BASE_URL}/api/v1/oracle-marketplace/plans", timeout=10)
        if oracle_plans.status_code == 200:
            print(f"✅ Oracle plans OK")
        else:
            print(f"❌ Oracle plans: {oracle_plans.status_code}")

        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ API não disponível em {BASE_URL}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("   TESTES DE CONECTIVIDADE - MARKETPLACES")
    print("=" * 60)

    results = [
        ("Google Cloud Marketplace", test_google_marketplace()),
        ("Oracle Cloud Marketplace", test_oracle_marketplace()),
        ("Salesforce AppExchange", test_salesforce()),
        ("API Endpoints", test_api_endpoints()),
    ]

    print("\n" + "=" * 60)
    print("   RESUMO")
    print("=" * 60)
    for name, ok in results:
        icon = "✅" if ok else "❌"
        print(f"   {icon} {name}")
