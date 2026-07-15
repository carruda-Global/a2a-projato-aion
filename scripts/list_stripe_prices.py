import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

products = stripe.Product.list(limit=10)
for prod in products:
    prices = stripe.Price.list(product=prod.id, limit=1)
    price = prices.data[0] if prices.data else None
    interval = price.recurring.interval if price and price.recurring else "one-time"
    curr = price.currency.upper() if price else "N/A"
    amount = f"{price.unit_amount/100:.2f}" if price else "N/A"
    print(f"Product: {prod.name}")
    print(f"  ID: {prod.id}")
    if price:
        print(f"  Price ID: {price.id} | {curr} {amount} | {interval}")
    print()
