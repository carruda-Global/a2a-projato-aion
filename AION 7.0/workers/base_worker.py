import asyncio
import json
import logging
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis.asyncio as redis

from src.orchestrator import Orchestrator
from src.config import Settings

logger = logging.getLogger(__name__)


class BaseWorker:
    def __init__(self, stream: str, group: str, consumer: str, clusters: list[str] | None = None):
        self.stream = stream
        self.group = group
        self.consumer = consumer
        self.clusters = clusters
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis: redis.Redis | None = None
        self.orchestrator: Orchestrator | None = None

    async def start(self):
        self.redis = redis.from_url(self.redis_url, decode_responses=True)
        settings = Settings()
        self.orchestrator = Orchestrator(settings)
        try:
            await self.redis.xgroup_create(self.stream, self.group, id="0", mkstream=True)
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
        logger.info("Worker %s iniciado — stream: %s", self.consumer, self.stream)

    async def process(self, task: dict) -> dict[str, Any]:
        raise NotImplementedError

    async def run(self):
        await self.start()
        while True:
            try:
                results = await self.redis.xreadgroup(
                    self.group, self.consumer, {self.stream: ">"}, count=1, block=5000
                )
                if not results:
                    continue
                for stream_name, messages in results:
                    for msg_id, msg_data in messages:
                        task = {k: v for k, v in msg_data.items()}
                        logger.info("Task recebida: %s", task.get("task_id", msg_id))
                        try:
                            result = await self.process(task)
                            await self.redis.xadd(f"{self.stream}:results", {
                                "task_id": task.get("task_id", msg_id),
                                "status": "completed",
                                "result": json.dumps(result, default=str),
                            })
                        except Exception as e:
                            logger.exception("Erro na task %s", task.get("task_id", msg_id))
                            await self.redis.xadd(f"{self.stream}:results", {
                                "task_id": task.get("task_id", msg_id),
                                "status": "failed",
                                "error": str(e),
                            })
                        await self.redis.xack(self.stream, self.group, msg_id)
            except Exception as e:
                logger.error("Erro no loop do worker: %s", e)
                await asyncio.sleep(5)
