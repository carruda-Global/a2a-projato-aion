import stripe
from src.config import Settings
s = Settings()
stripe.api_key = s.stripe_secret_key

subs = stripe.Subscription.list(limit=20, status='active')
print('Assinaturas ativas:', len(subs.data))
for sub in subs.data:
    plan = sub.get('plan', {})
    print('  ', sub.get('customer_email'), '|', plan.get('nickname', 'N/A'), '|', sub.status)

payments = stripe.PaymentIntent.list(limit=10)
total = sum(p.amount for p in payments.data if p.status == 'succeeded')
print('Total recebido (sempre):', total/100)
