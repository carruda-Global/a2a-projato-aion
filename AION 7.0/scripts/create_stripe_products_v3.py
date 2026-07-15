import stripe
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

NEW_PLANS = [
    {"name": "Dynamics 365 Pack", "id": "dynamics_pack", "amount_cents": 399000, "description": "6 agentes Dynamics 365: Sales, Finance, Supply Chain, HR, CS, Power BI"},
    {"name": "Salesforce Agentforce Pack", "id": "agentforce_pack", "amount_cents": 369000, "description": "5 agentes Agentforce: SDR, Field Service, Contracts, Revenue, Sustainability"},
    {"name": "Oracle Fusion Pack", "id": "oracle_pack", "amount_cents": 399000, "description": "4 agentes Oracle: ERP Compliance, HCM Regulatory, Supply Chain ESG, CX Sales"},
    {"name": "SAP Integration Pack", "id": "sap_pack", "amount_cents": 429000, "description": "3 agentes SAP: Compliance Bridge, Predictive Maintenance, CBAM Export"},
    {"name": "ERP Full Bridge", "id": "erp_full_bridge", "amount_cents": 1299000, "description": "18 agentes ERP: Dynamics + Agentforce + Oracle + SAP"},
    {"name": "Full Suite 56", "id": "full_suite_56", "amount_cents": 1999700, "description": "Todos os 56 agentes do EcoSystem 3.0"},
    {"name": "Onboarding Funcionarios", "id": "onboarding_funcionarios", "amount_cents": 49000, "description": "Automacao de admissao, contratos, provisionamento M365"},
    {"name": "Atendimento PT-BR", "id": "atendimento_plus", "amount_cents": 39000, "description": "Tickets L1 automaticos via WhatsApp + Teams"},
    {"name": "Conciliacao Pro", "id": "conciliacao_pro", "amount_cents": 79000, "description": "Conciliacao de NFs com extratos bancarios"},
]

def create_products():
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
    if not stripe.api_key:
        print("ERRO: STRIPE_SECRET_KEY nao configurada")
        print("Use: $env:STRIPE_SECRET_KEY='sk_test_...'")
        sys.exit(1)

    is_live = stripe.api_key.startswith("sk_live_")
    print(f"Modo: {'🔴 LIVE' if is_live else '🟢 TEST'}")

    output = []
    for plan in NEW_PLANS:
        try:
            product = stripe.Product.create(
                name=plan["name"],
                description=plan["description"],
                metadata={"plan_id": plan["id"], "ecosystem_version": "3.0.0"},
            )
            price = stripe.Price.create(
                product=product.id,
                unit_amount=plan["amount_cents"],
                currency="brl",
                recurring={"interval": "month"},
                metadata={"plan_id": plan["id"]},
            )
            entry = {
                "plan_id": plan["id"],
                "product_id": product.id,
                "price_id": price.id,
                "amount_cents": plan["amount_cents"],
                "name": plan["name"],
            }
            output.append(entry)
            print(f"  ✅ {plan['name']}: price_id = {price.id}")
        except Exception as e:
            print(f"  ❌ {plan['name']}: {e}")

    print("\n--- Copie os price_ids abaixo para o config.yaml ---")
    for entry in output:
        print(f'    {entry["plan_id"]}:')
        print(f'      name: "{entry["name"]}"')
        print(f'      amount_cents: {entry["amount_cents"]}')
        print(f'      price_id: "{entry["price_id"]}"')
        print()

if __name__ == "__main__":
    create_products()
