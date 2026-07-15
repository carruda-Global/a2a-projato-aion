import asyncio
import json
import logging
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers.base_worker import BaseWorker
from src.cross_selling import get_cross_sell_recommendation, get_journey_progress

logger = logging.getLogger(__name__)


class CrossSellWorker(BaseWorker):
    def __init__(self):
        super().__init__(
            stream="cross_sell:tasks",
            group="cross_sell-workers",
            consumer=f"cross_sell-worker-{os.getpid()}",
        )

    async def process(self, task: dict) -> dict[str, Any]:
        current_agent = task.get("current_agent", "")
        tenant_context = task.get("tenant_context", {})
        recommendation = get_cross_sell_recommendation(current_agent, tenant_context)
        journey = get_journey_progress(tenant_context)
        return {
            "recommendation": recommendation,
            "journey_progress": journey,
            "tenant_id": task.get("tenant_id", "default"),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = CrossSellWorker()
    asyncio.run(worker.run())
