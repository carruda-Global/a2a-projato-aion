import stripe
from src.config import Settings
s = Settings()
stripe.api_key = s.stripe_secret_key

# Account info
acct = stripe.Account.retrieve()
print('=== CONTA STRIPE ===')
print('ID:', acct.id)
print('Nome:', acct.get('settings', {}).get('dashboard', {}).get('display_name', 'N/A'))
print('Pais:', acct.get('country', 'N/A'))
print('Moeda:', acct.get('default_currency', 'N/A'))
print('Payouts:', acct.get('payouts_enabled', False))
print('Charges:', acct.get('charges_enabled', False))

# Products
products = stripe.Product.list(limit=20, active=True)
print('\n=== PRODUTOS ===')
for p in products.data:
    print(f'  {p.id}: {p.name} | {p.get("description","")[:50]}')

# Prices
prices = stripe.Price.list(limit=20, active=True)
print('\n=== PRECOS ===')
for p in prices.data:
    prod_name = p.get('product', 'N/A')
    if isinstance(prod_name, str):
        try:
            prod = stripe.Product.retrieve(prod_name)
            prod_name = prod.name
        except:
            pass
    print(f'  {p.id}: {p.unit_amount/100:.2f} {p.currency.upper()} | {p.recurring.get("interval","one_time") if p.recurring else "one_time"} | {prod_name}')
