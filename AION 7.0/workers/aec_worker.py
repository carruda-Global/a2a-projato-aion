import asyncio
import logging
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

AEC_AGENTS = [
    "spec_analyst", "procurement", "inventory", "logistics", "field_execution",
    "bim_coordinator", "requirements_analyst", "engineering_assistant", "work_synopsis",
    "photo_intelligence", "rfi_creation", "compliance",
]


class AECWorker(BaseWorker):
    def __init__(self):
        super().__init__(
            stream="aec:tasks",
            group="aec-workers",
            consumer=f"aec-worker-{os.getpid()}",
        )

    async def process(self, task: dict) -> dict[str, Any]:
        agent_id = task.get("agent_id", "")
        if agent_id not in AEC_AGENTS:
            agent_id = "spec_analyst"
        payload = task.get("payload", {})
        result = self.orchestrator.run_agent(agent_id, payload)
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = AECWorker()
    asyncio.run(worker.run())
