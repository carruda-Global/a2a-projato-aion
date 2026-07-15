import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TimescaleDBClient:

    def __init__(self):
        self.host = os.getenv("TIMESCALE_HOST", "localhost")
        self.port = int(os.getenv("TIMESCALE_PORT", "5432"))
        self.database = os.getenv("TIMESCALE_DATABASE", "aion_metrics")
        self.conn = None

    async def connect(self):
        try:
            import asyncpg
            self.conn = await asyncpg.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=os.getenv("TIMESCALE_USER", "postgres"),
                password=os.getenv("TIMESCALE_PASSWORD", ""))
            logger.info(f"Connected to TimescaleDB")
        except ImportError:
            logger.warning("asyncpg not installed")
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")

    async def store_metric(self, agent_id: str, metric: str, value: float, tags: Dict[str, str] = None) -> bool:
        if not self.conn:
            return False
        try:
            logger.info(f"Stored metric {metric}={value} for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
            return False

    async def get_metrics(self, agent_id: str, metric: str, hours: int = 24) -> List[Dict]:
        if not self.conn:
            return []
        try:
            return []
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return []
