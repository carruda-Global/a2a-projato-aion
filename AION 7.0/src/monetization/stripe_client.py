import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StripeClient:

    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self.connect_webhook_secret = os.getenv("STRIPE_CONNECT_WEBHOOK_SECRET", "")
        self.client = None
        if self.api_key:
            try:
                import stripe
                stripe.api_key = self.api_key
                stripe.webhook_secret = self.webhook_secret
                stripe.connect_webhook_secret = self.connect_webhook_secret
                self.client = stripe
            except ImportError:
                logger.warning("stripe not installed")
        else:
            logger.warning("Stripe API key not configured")

    def create_checkout_session(self, price_id: str, tenant_id: str, success_url: str, cancel_url: str) -> Optional[Dict]:
        if not self.client:
            return None
        try:
            session = self.client.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                client_reference_id=tenant_id,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return {"id": session.id, "url": session.url}
        except Exception as e:
            logger.error(f"Failed to create checkout session: {e}")
            return None

    def create_subscription(self, customer_id: str, price_id: str) -> Optional[Dict]:
        if not self.client:
            return None
        try:
            subscription = self.client.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
            )
            return {"id": subscription.id, "status": subscription.status}
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return None

    def handle_webhook(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        if not self.client or not self.webhook_secret:
            return None
        try:
            event = self.client.Webhook.construct_event(payload, sig_header, self.webhook_secret)
            return {"type": event.type, "data": event.data.object}
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return None
