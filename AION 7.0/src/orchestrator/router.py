import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RouterAgent:

    def __init__(self, agent_registry: Dict[str, Any] = None):
        self.registry = agent_registry or {}

    async def route(self, task: Dict[str, Any]) -> Optional[str]:
        agent_type = task.get("agent", "default")
        if agent_type in self.registry:
            return agent_type
        logger.warning(f"No agent found for type: {agent_type}, using default")
        return "default"

    async def route_batch(self, tasks: List[Dict[str, Any]]) -> List[str]:
        return [await self.route(t) for t in tasks]
