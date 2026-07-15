import asyncio
import logging
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

MICROSOFT_AGENTS = [
    "regulatory_analyst", "compliance_pm", "channel_agent",
    "knowledge_agent", "facilitator_agent", "dev_experience",
    "dynamics_sales", "dynamics_finance", "dynamics_supply_chain",
    "dynamics_hr", "dynamics_customer_service", "powerbi_compliance",
]


class MicrosoftWorker(BaseWorker):
    def __init__(self):
        super().__init__(
            stream="microsoft:tasks",
            group="microsoft-workers",
            consumer=f"microsoft-worker-{os.getpid()}",
        )

    async def process(self, task: dict) -> dict[str, Any]:
        agent_id = task.get("agent_id", "")
        if agent_id not in MICROSOFT_AGENTS:
            agent_id = "regulatory_analyst"
        payload = task.get("payload", {})
        result = self.orchestrator.run_agent(agent_id, payload)
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = MicrosoftWorker()
    asyncio.run(worker.run())
