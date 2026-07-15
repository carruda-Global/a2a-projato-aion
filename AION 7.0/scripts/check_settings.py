import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.config import Settings

s = Settings()
print(f"stripe_secret_key: {getattr(s, 'stripe_secret_key', 'N/A')[:20]}...")
print(f"stripe_webhook_secret: {getattr(s, 'stripe_webhook_secret', 'N/A')[:20]}...")
print(f"plans_config: {getattr(s, 'plans_config', 'N/A')}")
