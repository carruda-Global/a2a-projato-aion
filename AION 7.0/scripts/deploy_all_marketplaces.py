import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

import stripe
import yaml

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
OFFERS_DIR = Path(__file__).parent.parent / "offers"
CONFIG_DIR = Path(__file__).parent.parent / "config"

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

NEW_PRODUCTS = [
    {"id": "compliance_essencial", "name": "Compliance Essencial - NR-1 + LGPD", "price_brl": 59000, "price_usd": 14900},
    {"id": "regulatory_pro", "name": "Regulatory Pro - 5 Agentes", "price_brl": 149000, "price_usd": 37900},
    {"id": "esg_carbono", "name": "ESG + Carbono", "price_brl": 249000, "price_usd": 62900},
    {"id": "microsoft_pack", "name": "Microsoft Pack - 6 Agentes", "price_brl": 448200, "price_usd": 112900},
    {"id": "dynamics_pack", "name": "Dynamics 365 Pack", "price_brl": 399000, "price_usd": 99900},
    {"id": "agentforce_pack", "name": "Agentforce Pack", "price_brl": 369000, "price_usd": 92900},
    {"id": "oracle_pack", "name": "Oracle Fusion Pack", "price_brl": 399000, "price_usd": 99900},
    {"id": "sap_pack", "name": "SAP Integration Pack", "price_brl": 429000, "price_usd": 107900},
    {"id": "erp_full_bridge", "name": "ERP Full Bridge", "price_brl": 1299000, "price_usd": 329900},
    {"id": "tech_starter", "name": "Tech Starter", "price_brl": 199700, "price_usd": 49900},
    {"id": "tech_enterprise", "name": "Tech Enterprise", "price_brl": 599700, "price_usd": 149900},
    {"id": "full_suite", "name": "Full Suite - 71 Agentes", "price_brl": 1999700, "price_usd": 499900},
    {"id": "cross_sell_pack", "name": "Cross-Sell Pack", "price_brl": 29700, "price_usd": 7900},
]


def setup_stripe():
    if not stripe.api_key:
        print("[!] Stripe key not configured")
        return []
    price_ids = []
    for prod in NEW_PRODUCTS:
        try:
            existing = stripe.Product.search(query=f"name:'{prod['name']}'")
            if existing.data:
                product = existing.data[0]
            else:
                product = stripe.Product.create(
                    name=prod["name"],
                    description=f"Plano {prod['name']} - H-MAS EcoSystem",
                    metadata={"plan_id": prod["id"]}
                )
            price_brl = stripe.Price.create(
                product=product.id,
                unit_amount=prod["price_brl"],
                currency="brl",
                recurring={"interval": "month"}
            )
            price_usd = stripe.Price.create(
                product=product.id,
                unit_amount=prod["price_usd"],
                currency="usd",
                recurring={"interval": "month"}
            )
            price_ids.append({"plan_id": prod["id"], "product_id": product.id, "price_brl": price_brl.id, "price_usd": price_usd.id})
            print(f"  [OK] {prod['name']}: BRL={price_brl.id} USD={price_usd.id}")
        except Exception as e:
            print(f"  [ERR] {prod['name']}: {e}")
    return price_ids


def update_config_with_prices(price_ids):
    if not os.path.exists(CONFIG_PATH):
        print("[!] config.yaml not found")
        return
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    if "stripe" not in config:
        config["stripe"] = {}
    if "prices" not in config["stripe"]:
        config["stripe"]["prices"] = {}
    for p in price_ids:
        config["stripe"]["prices"][p["plan_id"]] = {"brl": p["price_brl"], "usd": p["price_usd"]}
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    print("  [OK] config.yaml updated with price IDs")


def generate_offers():
    OFFERS_DIR.mkdir(exist_ok=True)
    offer = {
        "id": "ecosystem-aion-71-agentes",
        "name": "AION - 71 Agentes de IA",
        "version": "6.0",
        "marketplaces": {
            "microsoft": {
                "plans": [
                    {"id": p["id"], "name": p["name"],
                     "prices_brl": p["price_brl"], "prices_usd": p["price_usd"]}
                    for p in NEW_PRODUCTS
                ],
                "fulfillment_url": "https://engenheiro-producao-ai.onrender.com/microsoft/fulfill",
                "webhook_url": "https://engenheiro-producao-ai.onrender.com/microsoft/webhook"
            },
            "google": {
                "plans": [{"id": p["id"], "name": p["name"], "price_usd": p["price_usd"]} for p in NEW_PRODUCTS]
            },
            "salesforce": {
                "plans": [{"id": p["id"], "name": p["name"], "price_usd": p["price_usd"]} for p in NEW_PRODUCTS]
            },
            "aws": {
                "plans": [{"id": p["id"], "name": p["name"], "price_usd": p["price_usd"]} for p in NEW_PRODUCTS]
            },
            "oracle": {
                "plans": [{"id": p["id"], "name": p["name"], "price_usd": p["price_usd"]} for p in NEW_PRODUCTS]
            },
            "sap": {
                "plans": [{"id": p["id"], "name": p["name"], "price_usd": p["price_usd"]} for p in NEW_PRODUCTS]
            },
            "hubspot": {
                "plans": [{"id": p["id"], "name": p["name"], "price_usd": p["price_usd"]} for p in NEW_PRODUCTS]
            },
            "pipefy": {
                "plans": [{"id": p["id"], "name": p["name"], "price_usd": p["price_usd"]} for p in NEW_PRODUCTS]
            }
        }
    }
    offer_path = OFFERS_DIR / "aion-71-agentes-offer.json"
    with open(offer_path, "w", encoding="utf-8") as f:
        json.dump(offer, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Offer generated: {offer_path}")


def update_microsoft_offer():
    offer_path = OFFERS_DIR / "ecosystem-aec-offer.json"
    if not os.path.exists(offer_path):
        print("[!] Microsoft offer not found, creating...")
        offer_data = {
            "$schema": "https://schema.mp.azure.com/schema/2024-03-01/offer.json",
            "id": "alias-compliance-regulatorio",
            "name": "Alias - AION 71 Agentes de IA",
            "description": "AION: 71 agentes de IA para Compliance Regulatorio, Engenharia, ERP, Vendas e Tecnologia",
            "kind": "SaaS",
            "categories": ["AI + Machine Learning", "Developer Tools", "Human Resources"],
            "plans": []
        }
    else:
        with open(offer_path, encoding="utf-8") as f:
            offer_data = json.load(f)

    offer_data["plans"] = [
        {
            "id": p["id"],
            "name": p["name"],
            "description": f"Plano {p['name']} - assinatura mensal",
            "pricing": {"type": "recurring", "interval": "month", "price_brl": p["price_brl"], "price_usd": p["price_usd"]}
        }
        for p in NEW_PRODUCTS
    ]

    with open(offer_path, "w", encoding="utf-8") as f:
        json.dump(offer_data, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Microsoft offer updated with {len(NEW_PRODUCTS)} plans")


def main():
    print("=" * 60)
    print("AION v6.0 - Deploy em TODOS os Marketplaces")
    print("=" * 60)

    print("\n[1/6] Stripe - Criando produtos e precos...")
    price_ids = setup_stripe()
    if price_ids:
        update_config_with_prices(price_ids)

    print("\n[2/6] Gerando ofertas unificadas...")
    generate_offers()

    print("\n[3/6] Microsoft Marketplace - Atualizando offer...")
    update_microsoft_offer()

    print("\n[4/6] Google Cloud Marketplace - Offer gerada")
    print("   Upload manual em: https://console.cloud.google.com/partners")

    print("\n[5/6] Salesforce AgentExchange - Offer gerada")
    print("   Upload manual em: https://partners.salesforce.com")

    print("\n[6/6] HubSpot App Marketplace - Configuracao manual")
    print("   Endpoints:")
    print("     Install:    https://engenheiro-producao-ai.onrender.com/hubspot/install")
    print("     OAuth:      https://engenheiro-producao-ai.onrender.com/hubspot/oauth/callback")
    print("     Webhook:    https://engenheiro-producao-ai.onrender.com/hubspot/webhook")
    print("     Compliance: https://engenheiro-producao-ai.onrender.com/hubspot/compliance-check")
    print("   Configurar em: https://developers.hubspot.com/")
    print("   Guia: marketplace-integration/hubspot/setup_guide.md")

    print("\n[7/7] Pipefy Ecosystem - Configuracao manual")
    print("   Endpoints:")
    print("     Webhook:    https://engenheiro-producao-ai.onrender.com/pipefy/webhook")
    print("     Run Check:  https://engenheiro-producao-ai.onrender.com/pipefy/run-check")
    print("   Criar Pipes de compliance NR-1, LGPD, EU AI Act")
    print("   Guia: marketplace-integration/pipefy/setup_guide.md")

    print("\n[8/8] AppSumo (Lifetime Deals) - Configuracao manual")
    print("   Webhook:    https://engenheiro-producao-ai.onrender.com/appsumo/webhook")
    print("   License:    https://engenheiro-producao-ai.onrender.com/appsumo/license/activate")
    print("   Guia: marketplace-integration/appsumo/setup_guide.md")

    print("\n[9/9] Zapier App Directory - Deploy via CLI")
    print("   cd zapier-integration && zapier push")
    print("   Guia: zapier-integration/README.md")

    print("\n[10/10] n8n Community Node - Publicar no npm")
    print("   cd n8n-nodes/aion-compliance && npm publish")
    print("   Guia: n8n-nodes/aion-compliance/README.md")

    print("\n" + "=" * 60)
    print("RESUMO - NOVAS PLATAFORMAS ADICIONADAS:")
    print("  ✅ HubSpot App Marketplace (faixa 1)")
    print("  ✅ Pipefy Ecosystem (faixa 2)")
    print("  ✅ Zapier App Directory (faixa 3)")
    print("  ✅ n8n Community Nodes (faixa 4)")
    print("  ✅ AppSumo (lifetime deals)")
    print("  🟡 G2 Crowd + Capterra (perfis prontos - precisa reviews)")
    print("  🟡 TAAFT + Futurepedia + Toolify.ai (listings prontos)")
    print("  🟡 Product Hunt (estrategia definida)")
    print("=" * 60)
    print()
    print("Stripe Agentic Commerce:")
    print("  Upload catalog: config/stripe_agentic_catalog.csv")
    print("  ACP config: config/acp_checkout_config.json")
    print("  Stripe Dashboard: https://dashboard.stripe.com/agentic-commerce")
    print()
    print("Replit Agent Market:")
    print("  https://replit.com/@global-engenharia/ecosystem-compliance-score")
    print()
    print("MindStudio:")
    print("  NR-1, LGPD, Regulatory Watch publicados")
    print("=" * 60)


if __name__ == "__main__":
    main()
