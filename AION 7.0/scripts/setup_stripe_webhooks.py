import stripe, os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

BASE_URL = "https://engenheiro-producao-ai.onrender.com"

webhook_configs = [
    {"url": BASE_URL + "/api/webhook/stripe", "desc": "Eventos gerais Stripe"},
    {"url": BASE_URL + "/api/webhook/stripe/connect", "desc": "Eventos Stripe Connect"},
]

events = [
    "checkout.session.completed",
    "checkout.session.expired",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.paid",
    "invoice.payment_failed",
    "payment_intent.succeeded",
    "payment_intent.payment_failed",
]

existing = stripe.WebhookEndpoint.list(limit=20)
existing_urls = [e.url for e in existing.data]

for wh in webhook_configs:
    if wh["url"] in existing_urls:
        print(f"  [JA EXISTE] {wh['url']}")
    else:
        created = stripe.WebhookEndpoint.create(
            url=wh["url"],
            enabled_events=events,
            description=wh["desc"],
            api_version="2024-12-18.acacia"
        )
        secret = created.secret[:20]
        print(f"  [CRIADO] {wh['url']}")
        print(f"    Webhook Secret: {created.secret}")
