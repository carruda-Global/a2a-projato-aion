import logging
from typing import Dict, Any, Optional
from .aip_registry import AIPRegistry

logger = logging.getLogger(__name__)


class AIPProxy:

    def __init__(self, registry: AIPRegistry):
        self.registry = registry

    async def enforce(self, agent_id: str, action: str, context: Dict[str, Any]) -> bool:
        if not self.registry.verify_agent(agent_id):
            logger.warning(f"Proxy blocked action '{action}' for unverified agent {agent_id}")
            return False

        logger.info(f"Proxy allowed action '{action}' for agent {agent_id}")
        return True
