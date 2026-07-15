import asyncio
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

_CORE_AEC_AGENTS = [
    "architect_agent", "structural_engineer", "mep_engineer", "bim_coordinator",
    "cost_estimator", "scheduler_agent", "quality_inspector", "safety_officer",
]


class PlannerAgent:

    def __init__(self, llm_client=None):
        self.llm = llm_client

    async def decompose(self, query: str, available_agents: List[str]) -> List[Dict[str, Any]]:
        logger.info(f"Decomposing query: {query[:50]}...")
        routable = [a for a in _CORE_AEC_AGENTS if a in available_agents] or _CORE_AEC_AGENTS

        if self.llm is None:
            return [{"step": 1, "agent": routable[0], "task": query, "priority": 1}]

        options = ", ".join(routable)
        classify_prompt = (
            f'User request: "{query}"\n\n'
            f"Which of these specialists should handle this request? "
            f"Pick 1 to 3, the most relevant ones: {options}\n"
            f"Reply with ONLY the chosen IDs, comma-separated, no explanation."
        )
        try:
            raw = await asyncio.to_thread(
                self.llm.chat,
                "You route architecture/engineering/construction requests to the right specialist.",
                classify_prompt,
                0.0,
                60,
                "en",
            )
        except Exception as e:
            logger.warning("Planner classification failed (%s), using default agent", e)
            return [{"step": 1, "agent": routable[0], "task": query, "priority": 1}]

        chosen = [a.strip() for a in raw.replace("\n", ",").split(",")]
        chosen = [a for a in chosen if a in routable]
        if not chosen:
            chosen = [routable[0]]

        return [
            {"step": i + 1, "agent": agent_id, "task": query, "priority": 1}
            for i, agent_id in enumerate(chosen)
        ]

    async def create_plan(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await self.decompose(query, context.get("agents", []))
