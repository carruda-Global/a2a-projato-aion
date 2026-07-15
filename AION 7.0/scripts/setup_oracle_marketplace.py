"""
Script de setup do Oracle Cloud Marketplace.
Cria o listing SaaS e configura os planos de precificacao.

Uso:
    python scripts/setup_oracle_marketplace.py --create-listing
    python scripts/setup_oracle_marketplace.py --status
    python scripts/setup_oracle_marketplace.py --list-subscriptions

Requer:
    - oci CLI configurado (~/.oci/config) ou Instance Principal
    - Variaveis de ambiente: OCI_CONFIG_FILE, OCI_PROFILE
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.monetization.oracle_client import OracleMarketplaceClient


def main():
    parser = argparse.ArgumentParser(description="Setup Oracle Cloud Marketplace")
    parser.add_argument("--create-listing", action="store_true", help="Criar listing SaaS no OCI Marketplace")
    parser.add_argument("--status", action="store_true", help="Verificar status da integracao")
    parser.add_argument("--list-subscriptions", action="store_true", help="Listar assinaturas ativas")
    args = parser.parse_args()

    settings = Settings()
    oracle = OracleMarketplaceClient(settings)

    if args.status:
        print("=== Oracle Marketplace - Status ===")
        print(f"  Product ID: {settings.oracle_product_id or 'N/A'}")
        print(f"  Seller ID:  {settings.oracle_seller_id or 'N/A'}")
        print(f"  Enabled:    {settings.oracle_enabled}")
        print()
        if settings.oracle_product_id:
            print("  Testando conexao...")
            subs = oracle.list_subscriptions()
            print(f"  Assinaturas ativas: {len(subs)}")
            for s in subs:
                print(f"    - {s['subscription_id'][:20]}... ({s['state']})")

    elif args.create_listing:
        print("=== Criando Listing no Oracle Marketplace ===")
        print()
        print("Para criar um listing SaaS no Oracle Cloud Marketplace,")
        print("use o OCI Console em: Marketplace > Publisher > Listings")
        print()
        print("Ou use o CLI:")
        print()
        print("  oci marketplace-publisher listing create \\")
        print("    --compartment-id <compartment_ocid> \\")
        print("    --name 'Engenheiro de Producao AI' \\")
        print("    --listing-type OCI_APPLICATION \\")
        print("    --package-type SAAS")
        print()
        print("  oci marketplace-publisher listing-revision create \\")
        print("    --listing-id <listing_id> \\")
        print("    --headline 'Sistema Multiagente para AEC' \\")
        print("    --categories '[\"ARTIFICIAL_INTELLIGENCE\"]'")
        print()
        print("  Partner Provisioning URL:")
        print(f"    {settings.app_env}/api/v1/oracle-marketplace/activate")
        print()
        print("Planos disponiveis (configurados em config.yaml):")
        plans = settings.config.get("marketplace", {}).get("oracle", {}).get("plans", {})
        for pid, pinfo in plans.items():
            print(f"    - {pid}: ${pinfo['price_monthly_usd']}/mes - {pinfo['description']}")

    elif args.list_subscriptions:
        print("=== Assinaturas Oracle Marketplace ===")
        subs = oracle.list_subscriptions()
        if not subs:
            print("  Nenhuma assinatura encontrada.")
        for s in subs:
            print(f"  ID:     {s['subscription_id']}")
            print(f"  Tenant: {s['tenant_id']}")
            print(f"  Status: {s['state']}")
            print(f"  Criado: {s['time_created']}")
            print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
