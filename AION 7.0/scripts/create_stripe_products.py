"""
Cria produtos e precos no Stripe para os 5 planos do EcoSystem AEC.
Atualiza automaticamente o config.yaml com os price_ids gerados.

Uso:
    python scripts/create_stripe_products.py
    python scripts/create_stripe_products.py --dry-run

Requer:
    - STRIPE_SECRET_KEY no .env
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

import stripe
import yaml

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRODUCTS = [
    {"id": "starter", "name": "Starter - Spec Analyst", "price": 99700,
     "agents": ["spec_analyst"],
     "description": "Analise de especificacoes tecnicas com IA"},
    {"id": "professional", "name": "Professional - 3 Agentes", "price": 239100,
     "agents": ["spec_analyst", "procurement", "inventory"],
     "description": "Analise, compras e estoque automatizados"},
    {"id": "enterprise", "name": "Enterprise - 5 Agentes", "price": 468500,
     "agents": ["spec_analyst", "procurement", "inventory", "logistics", "field_execution"],
     "description": "Suite completa de 5 agentes para construtoras"},
    {"id": "full_suite", "name": "Full Suite - 12 Agentes", "price": 949700,
     "agents": ["spec_analyst", "procurement", "inventory", "logistics",
                "field_execution", "bim_coordinator", "requirements_analyst",
                "engineering_assistant", "work_synopsis", "photo_intelligence",
                "rfi_creation", "compliance"],
     "description": "Ecossistema completo de 12 agentes de IA para AEC"},
    {"id": "compliance_pack", "name": "Compliance Pack", "price": 239100,
     "agents": ["photo_intelligence", "rfi_creation", "compliance"],
     "description": "Pacote de conformidade legal com IA"},
]

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def main():
    parser = argparse.ArgumentParser(description="Criar produtos Stripe")
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostrar o que seria criado")
    args = parser.parse_args()

    if not stripe.api_key or stripe.api_key.startswith("sk_test_") is False:
        print("ERRO: STRIPE_SECRET_KEY nao configurada ou invalida no .env")
        sys.exit(1)

    results = []
    for p in PRODUCTS:
        if args.dry_run:
            print(f"[DRY-RUN] {p['name']:30s} | R$ {p['price']/100:.2f}")
            continue

        try:
            prod = stripe.Product.create(
                name=p["name"],
                description=p["description"],
                metadata={"agents": json.dumps(p["agents"]), "plan_id": p["id"]},
            )
            price = stripe.Price.create(
                product=prod.id,
                unit_amount=p["price"],
                currency="brl",
                recurring={"interval": "month"},
                metadata={"plan_id": p["id"]},
            )
            results.append({"plan_id": p["id"], "product_id": prod.id, "price_id": price.id})
            print(f"  OK  {p['name']:30s} | Produto: {prod.id[:20]:20s} | Preco: {price.id}")
        except Exception as e:
            print(f"  ERRO {p['name']:30s} | {e}")

    if results and not args.dry_run:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        for r in results:
            plan_id = r["plan_id"]
            if plan_id in config.get("stripe", {}).get("plans", {}):
                config["stripe"]["plans"][plan_id]["price_id"] = r["price_id"]

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        print(f"\nconfig.yaml atualizado com {len(results)} price_ids!")


if __name__ == "__main__":
    main()
