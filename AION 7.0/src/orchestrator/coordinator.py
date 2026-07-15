import asyncio
import logging
import time
from typing import Dict, Any, List, Callable

from src.security.agent_execution_log import record_agent_execution

logger = logging.getLogger(__name__)


class CoordinatorAgent:

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_parallel(self, tasks: List[Dict], executor_map: Dict[str, Callable]) -> List[Dict[str, Any]]:
        async def _run(task: Dict) -> Dict[str, Any]:
            async with self.semaphore:
                agent_id = task.get("agent", "default")
                executor = executor_map.get(agent_id)
                if executor is None:
                    return {"task": task, "error": f"No executor for agent {agent_id}"}
                started = time.monotonic()
                try:
                    result = await executor(task)
                    await record_agent_execution(agent_id, int((time.monotonic() - started) * 1000), success=True)
                    return result
                except Exception as e:
                    logger.error(f"Agent {agent_id} failed: {e}")
                    await record_agent_execution(agent_id, int((time.monotonic() - started) * 1000), success=False, error_message=str(e))
                    return {"task": task, "error": str(e)}

        return await asyncio.gather(*[_run(t) for t in tasks])
