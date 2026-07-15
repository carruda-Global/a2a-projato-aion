from src.agents.base import BaseAgent
from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from typing import Dict, Any
import asyncio


class AntigravityBridge(BaseAgent):

    PLATFORM_CAPABILITIES = {
        "google_antigravity": ["code_generation", "parallel_execution", "scientific_analysis", "search", "data_analysis"],
        "microsoft_copilot": ["sharepoint", "teams", "outlook", "planner", "dynamics", "power_bi"],
        "ecosystem": ["compliance", "regulatory", "lgpd", "nr1", "esg", "carbon", "financial_reconciliation"]
    }

    def __init__(self):
        settings = Settings()
        llm = DeepSeekClient(settings)
        super().__init__(settings, llm)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        action = context.get("action", "route")
        if action == "route":
            return await self._route_workflow(
                context.get("workflow_id", ""),
                context.get("steps", []),
                context.get("tenant_id", "default")
            )
        elif action == "status":
            return {"workflow_id": context.get("workflow_id"), "status": "pending"}
        return {"error": f"Unknown action: {action}"}

    async def _route_workflow(self, workflow_id: str, steps: list, tenant_id: str) -> Dict:
        results = {}
        for i, step in enumerate(steps):
            platform = self._decide_platform(step)
            step_result = await self._execute_on_platform(platform, step, tenant_id)
            results[step.get("id", f"step_{i}")] = step_result
        return {
            "workflow_id": workflow_id,
            "completed_steps": len(steps),
            "results": results
        }

    async def _execute_on_platform(self, platform: str, step: dict, tenant_id: str) -> Dict:
        prompt = step.get("payload", {}).get("prompt", str(step))
        try:
            system = f"You are a {platform} specialist. Execute this workflow step."
            response = await asyncio.to_thread(self.llm.chat, system, prompt)
            return {"platform": platform, "status": "completed", "result": response}
        except Exception as e:
            return {"platform": platform, "status": "failed", "error": str(e)}

    def _decide_platform(self, step: dict) -> str:
        required = step.get("requires", [])
        for platform, capabilities in self.PLATFORM_CAPABILITIES.items():
            if any(req in capabilities for req in required):
                return platform
        return "ecosystem"
