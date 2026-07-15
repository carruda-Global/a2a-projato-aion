import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SupabaseClient:

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_KEY", "")
        self.client = None
        if self.url and self.key:
            try:
                from supabase import create_client
                self.client = create_client(self.url, self.key)
            except ImportError:
                logger.warning("supabase-py not installed")
        else:
            logger.warning("Supabase credentials not configured")

    def get_subscriptions(self, status: str = "active") -> List[Dict]:
        if not self.client:
            logger.warning("Supabase client not initialized")
            return []
        try:
            response = self.client.table("subscriptions").select("*").eq("status", status).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch subscriptions: {e}")
            return []

    def create_subscription(self, data: dict) -> Optional[Dict]:
        if not self.client:
            return None
        try:
            response = self.client.table("subscriptions").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return None

    def get_tenants(self) -> List[Dict]:
        if not self.client:
            return []
        try:
            response = self.client.table("tenants").select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch tenants: {e}")
            return []
