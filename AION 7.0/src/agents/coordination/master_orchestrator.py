from src.agents.base import BaseAgent
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MasterOrchestratorAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            agent_id="#49",
            name="Master Orchestrator",
            description="Orquestrador central: recebe objetivo, decompoe, delega e agrega resultados",
            group="coordination",
            price_brl=0.0,
            price_usd=0.0,
            tools=["planning", "delegation", "monitoring", "aggregation"],
            llm="claude",
            budget=500000
        )
        self.agent_registry = {}

    def register_agents(self, agents: Dict[str, BaseAgent]):
        self.agent_registry = agents

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        objective = context.get("objective", "")
        logger.info(f"Orchestrator received objective: {objective[:100]}...")

        plan = await self._create_plan(objective)
        results = await self._delegate(plan)
        synthesis = await self._synthesize(results)

        return {
            "objective": objective,
            "plan": plan,
            "results": results,
            "synthesis": synthesis,
            "agents_involved": len(plan)
        }

    async def _create_plan(self, objective: str) -> List[Dict]:
        return [{"step": 1, "agent_id": "auto", "task": objective, "priority": 1}]

    async def _delegate(self, plan: List[Dict]) -> List[Dict]:
        return [{"step": p["step"], "status": "delegated"} for p in plan]

    async def _synthesize(self, results: List[Dict]) -> str:
        return "Synthesis complete"
