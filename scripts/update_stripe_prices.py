import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

updates = [
    ("prod_UkKdUR0DRGwDSV", 99700, "starter"),
    ("prod_UkKdzUZEFG4Y82", 239100, "professional"),
    ("prod_UkKdLhqJXpZRcR", 468500, "enterprise"),
    ("prod_UkKdfiPbRmnnmy", 949700, "full_suite"),
]

for prod_id, amount, plan_id in updates:
    old_prices = stripe.Price.list(product=prod_id, limit=10)
    for old in old_prices:
        if old.active:
            stripe.Price.modify(old.id, active=False)

    new_price = stripe.Price.create(
        product=prod_id,
        unit_amount=amount,
        currency="brl",
        recurring={"interval": "month"},
        metadata={"plan_id": plan_id},
    )
    print(f"Produto {plan_id}: novo precos {amount/100:.2f} -> Price ID: {new_price.id}")

print("\nAtualizacao concluida!")
