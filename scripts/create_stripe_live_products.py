import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

plans = [
    ("Starter - Spec Analyst", 99700, "starter"),
    ("Professional - 3 Agentes", 239100, "professional"),
    ("Enterprise - 5 Agentes", 468500, "enterprise"),
    ("Full Suite - 21 Agentes", 949700, "full_suite"),
    ("Compliance Pack - PGRS/PGRSS", 239100, "compliance_pack"),
    ("Regulatory Starter - NR-1 + LGPD", 59000, "regulatory_starter"),
    ("Regulatory Professional - 5 Agentes", 149000, "regulatory_professional"),
    ("Regulatory Full - 9 Agentes", 349000, "regulatory_full"),
    ("ESG + Carbono", 249000, "esg_carbon_pack"),
    ("Microsoft Pack - 6 Agentes", 448200, "microsoft_pack"),
]

for name, amount, plan_id in plans:
    prod = stripe.Product.create(name=name, metadata={"plan_id": plan_id})
    price = stripe.Price.create(
        product=prod.id,
        unit_amount=amount,
        currency="brl",
        recurring={"interval": "month"},
        metadata={"plan_id": plan_id},
    )
    print(f"{plan_id}: {name} - R$ {amount/100:.2f}")
    print(f"  Product ID: {prod.id}")
    print(f"  Price ID: {price.id}")
    print()

print("Todos os produtos foram criados na conta LIVE!")
