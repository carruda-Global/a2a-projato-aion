import stripe, os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

ENTERPRISE_PLANS = [
    ("governance_starter", "Governance Starter", 199700, 49900),
    ("governance_pro", "Governance Pro", 597000, 149000),
    ("governance_enterprise", "Governance Enterprise", 999700, 249900),
    ("bridge_starter", "Bridge Starter", 196000, 49000),
    ("bridge_pro", "Bridge Pro", 597000, 149000),
    ("bridge_enterprise", "Bridge Enterprise", 797000, 199000),
    ("reviewer_starter", "Reviewer Starter", 39600, 9900),
    ("reviewer_pro", "Reviewer Pro", 119700, 29900),
    ("reviewer_enterprise", "Reviewer Enterprise", 199700, 49900),
    ("enterprise_full", "Enterprise Full Suite", 1597000, 399900),
]

for plan_id, name, price_brl, price_usd in ENTERPRISE_PLANS:
    try:
        existing = stripe.Product.search(query=f"name:'{name}'")
        if existing.data:
            product = existing.data[0]
        else:
            product = stripe.Product.create(name=name, metadata={"plan_id": plan_id})

        p_brl = stripe.Price.create(product=product.id, unit_amount=price_brl, currency="brl", recurring={"interval": "month"})
        p_usd = stripe.Price.create(product=product.id, unit_amount=price_usd, currency="usd", recurring={"interval": "month"})
        print(f"  [OK] {name}: BRL={p_brl.id} USD={p_usd.id}")
    except Exception as e:
        print(f"  [ERR] {name}: {e}")
