import stripe, os
from dotenv import load_dotenv
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PLANS = [
    ("physical_ai_starter", "Physical AI Starter", 396000, 99000),
    ("physical_ai_pro", "Physical AI Pro", 797000, 199000),
    ("physical_ai_enterprise", "Physical AI Enterprise", 1597000, 399000),
]

for plan_id, name, brl, usd in PLANS:
    try:
        existing = stripe.Product.search(query=f"name:'{name}'")
        product = existing.data[0] if existing.data else stripe.Product.create(name=name, metadata={"plan_id": plan_id})
        pb = stripe.Price.create(product=product.id, unit_amount=brl, currency="brl", recurring={"interval": "month"})
        pu = stripe.Price.create(product=product.id, unit_amount=usd, currency="usd", recurring={"interval": "month"})
        print(f"  [OK] {name}: BRL={pb.id} USD={pu.id}")
    except Exception as e:
        print(f"  [ERR] {name}: {e}")
