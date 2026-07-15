import logging
from datetime import datetime
from orchestrator.workflow_runner import WorkflowRunner
from integrations import LinkedInIntegration, LinkedInConfig

logger = logging.getLogger(__name__)


async def run_linkedin_workflow(linkedin: LinkedInIntegration | None = None) -> dict:
    if not linkedin:
        li_config = LinkedInConfig()
        linkedin = LinkedInIntegration(config=li_config)
        await linkedin.initialize()

    runner = WorkflowRunner(linkedin=linkedin)
    result = await runner.run_workflow("linkedin")
    await linkedin.shutdown()
    return result
