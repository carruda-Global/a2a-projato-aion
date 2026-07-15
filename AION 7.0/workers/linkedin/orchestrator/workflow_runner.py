import asyncio
import logging
import yaml
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowRunner:
    def __init__(self, linkedin=None):
        self.linkedin = linkedin
        self.config_dir = Path(__file__).resolve().parent.parent.parent / "config"

    def load_workflow(self, name: str) -> dict:
        path = self.config_dir / f"{name}_workflow.yaml"
        if not path.exists():
            path = self.config_dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Workflow {name} not found")
        with open(path) as f:
            return yaml.safe_load(f)

    async def run_workflow(self, workflow_name: str, params: dict = None) -> dict:
        workflow = self.load_workflow(workflow_name)
        logger.info(f"Executando workflow: {workflow['name']}")
        results = {}

        for step in workflow.get("steps", []):
            step_id = step["id"]
            agent_type = step["agent"]
            action = step["action"]
            step_params = step.get("params", {})

            logger.info(f"  Step {step_id}: agent={agent_type}, action={action}")
            try:
                result = await self._execute_step(agent_type, action, step_params)
                results[step_id] = result
            except Exception as e:
                logger.error(f"  Step {step_id} failed: {e}")
                results[step_id] = {"error": str(e)}

        return {
            "workflow": workflow["name"],
            "steps": len(workflow.get("steps", [])),
            "results": results,
            "completed_at": datetime.utcnow().isoformat(),
        }

    async def _execute_step(self, agent_type: str, action: str, params: dict) -> dict:
        from sales.agent import SalesAgent
        from agents.sales.prospect import ProspectAgent
        from agents.sales.qualify import LeadQualifier
        from sales import outreach

        agent_map = {
            "prospect": ProspectAgent(linkedin=self.linkedin) if self.linkedin else None,
            "lead_qualifier": LeadQualifier(),
            "outreach": SalesAgent(linkedin=self.linkedin) if self.linkedin else None,
            "content": SalesAgent(linkedin=self.linkedin) if self.linkedin else None,
            "site_webhook": SalesAgent(),
        }

        agent = agent_map.get(agent_type)
        if not agent:
            return {"error": f"Agent {agent_type} not available"}

        if hasattr(agent, "execute"):
            context = {"action": action, **params}
            return await agent.execute(context)

        return {"error": f"Agent {agent_type} has no execute method"}

    async def run_all(self) -> dict:
        results = {}
        workflows = ["linkedin", "outreach", "content"]
        for wf in workflows:
            try:
                results[wf] = await self.run_workflow(wf)
            except Exception as e:
                results[wf] = {"error": str(e)}
        return results
