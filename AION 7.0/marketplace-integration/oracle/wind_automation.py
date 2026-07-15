"""
Cria listagem no Oracle Cloud Marketplace via WIND CLI.

Pré-requisitos:
- WIND CLI instalado (pip install wind-cli ou binary)
- Oracle Partner Account configurada
- ~/.oci/config com credenciais

Uso:
    python wind_automation.py

Saída:
    - Arquivo listing_config.yaml gerado
    - Comando WIND exibido para execução manual
"""

import json
import os
import subprocess
import yaml
from dotenv import load_dotenv

load_dotenv()

ORACLE_PRODUCT_ID = os.getenv("ORACLE_PRODUCT_ID", "ecosystem-aec-v2")
ORACLE_SELLER_ID = os.getenv("ORACLE_SELLER_ID", "")
ORACLE_REGION = os.getenv("ORACLE_REGION", "sa-saopaulo-1")


def create_listing_config():
    base_plans = [
        {"name": "Starter", "price_usd": 199.00, "price_brl": 997.00},
        {"name": "Professional", "price_usd": 399.00, "price_brl": 2391.00},
        {"name": "Enterprise", "price_usd": 799.00, "price_brl": 4685.00},
        {"name": "Full Suite", "price_usd": 1599.00, "price_brl": 9497.00},
        {"name": "Compliance Pack", "price_usd": 399.00, "price_brl": 2391.00},
        {"name": "Regulatory Starter", "price_usd": 119.00, "price_brl": 590.00},
        {"name": "Regulatory Professional", "price_usd": 299.00, "price_brl": 1490.00},
        {"name": "Regulatory Full", "price_usd": 699.00, "price_brl": 3490.00},
        {"name": "ESG + Carbono", "price_usd": 499.00, "price_brl": 2490.00},
    ]

    plans = []
    for p in base_plans:
        plans.append({
            "name": p["name"],
            "price_usd": p["price_usd"],
            "price_brl": p["price_brl"],
            "contract_duration": "MONTHLY",
            "billing_frequency": "MONTHLY",
        })
        plans.append({
            "name": p["name"] + " (Annual)",
            "price_usd": p["price_usd"],
            "price_brl": p["price_brl"],
            "contract_duration": "ANNUAL",
            "billing_frequency": "MONTHLY",
        })

    config = {
        "display_name": "EcoSystem AEC - Regulatory Agents",
        "short_description": (
            "21 agentes de IA para Arquitetura, Engenharia, "
            "Construcao e Conformidade Regulatoria Brasileira"
        ),
        "long_description": (
            "Sistema multiagente com 21 agentes de IA especializados:\n\n"
            "AEC (12 agentes): Spec Analyst, Procurement, Inventory, "
            "Logistics, Field Execution, BIM Coordinator, etc.\n\n"
            "Regulatorios (9 agentes): NR-1 Psicossocial, Tributario "
            "CBS/IBS, LGPD, ESG IFRS S1/S2, Inventario de Carbono, "
            "Escopo 3, Canal de Denuncias, Igualdade Salarial e "
            "Compliance Anticorrupcao."
        ),
        "category": "AI_AGENTS_AND_TOOLS",
        "pricing": {
            "type": "SUBSCRIPTION",
            "currencies": ["USD", "BRL"],
            "plans": plans,
        },
        "seller": {
            "id": ORACLE_SELLER_ID,
            "name": "Global Match Engenharia de Producao",
            "email": "contato@global-engenharia.com",
            "website": "https://global-engenharia.com",
        },
        "support": {
            "email": "suporte@global-engenharia.com",
            "phone": "",
            "hours": "24/7",
        },
        "region": ORACLE_REGION,
    }

    with open("listing_config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print("✅ Configuração gerada: listing_config.yaml")
    return config


def execute_wind():
    cmd = [
        "wind",
        "marketplace",
        "create-listing",
        "--config", "listing_config.yaml",
    ]

    print(f"\n🚀 Comando para criar listagem:")
    print(f"   {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✅ Listagem criada com sucesso!")
        else:
            print(f"❌ Erro: {result.stderr}")
    except FileNotFoundError:
        print("⚠️  WIND CLI não encontrada. Execute manualmente o comando acima.")


if __name__ == "__main__":
    print("🚀 Gerando configuração para Oracle Cloud Marketplace...")
    create_listing_config()

    should_execute = input("\nExecutar WIND CLI agora? (s/N): ").strip().lower()
    if should_execute == "s":
        execute_wind()
    else:
        print("\nPara criar manualmente:")
        print("  wind marketplace create-listing --config listing_config.yaml")
