import asyncio
import logging
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

REGULATORY_AGENTS = [
    "nr1_psicossocial", "tributario_cbs_ibs", "lgpd_operacional",
    "esg_ifrs", "inventario_carbono", "escopo3_fornecedores",
    "canal_denuncias", "igualdade_salarial", "compliance_anticorrupcao",
]


class RegulatoryWorker(BaseWorker):
    def __init__(self):
        super().__init__(
            stream="regulatory:tasks",
            group="regulatory-workers",
            consumer=f"regulatory-worker-{os.getpid()}",
        )

    async def process(self, task: dict) -> dict[str, Any]:
        agent_id = task.get("agent_id", "")
        if agent_id not in REGULATORY_AGENTS:
            agent_id = "nr1_psicossocial"
        payload = task.get("payload", {})
        result = self.orchestrator.run_agent(agent_id, payload)
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = RegulatoryWorker()
    asyncio.run(worker.run())
