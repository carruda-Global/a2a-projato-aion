import logging
from integrations import LinkedInIntegration
from sales.database import SessionLocal, init_db
from sales import pipeline
from sales.linkedin_flow import LinkedInSalesFlow

logger = logging.getLogger(__name__)


class ProspectAgent:
    def __init__(self, linkedin: LinkedInIntegration | None = None):
        init_db()
        self.linkedin = linkedin

    async def execute(self, context: dict) -> dict:
        """Real dispatcher -- workflow_runner.py only calls agent.execute(),
        never search_and_qualify() directly. Without this method, every
        workflow step routed to agent="prospect" (linkedin_workflow.yaml's
        search_leads/enrich_leads steps, run daily at 08:00) silently failed
        with "Agent prospect has no execute method" and the pipeline never
        got real leads -- the workflow still reported "completed" since the
        error was caught and stored, not raised."""
        action = context.get("action", "linkedin_search")
        filters = context.get("filters", [])
        merged_filters: dict = {}
        for f in filters:
            if isinstance(f, dict):
                merged_filters.update(f)

        if action in ("linkedin_search", "linkedin_enrich"):
            keywords = context.get("keywords", "")
            industry_list = merged_filters.get("industry", [])
            location_list = merged_filters.get("location", [])
            return await self.search_and_qualify(
                keywords=keywords,
                industry=", ".join(industry_list) if isinstance(industry_list, list) else str(industry_list),
                title=", ".join(merged_filters.get("seniority", [])) if isinstance(merged_filters.get("seniority"), list) else "",
                location=", ".join(location_list) if isinstance(location_list, list) else str(location_list),
                limit=context.get("limit", 25),
            )
        return {"error": f"Unknown action: {action}"}

    async def search_and_qualify(
        self,
        keywords: str = "",
        industry: str = "",
        title: str = "",
        location: str = "",
        limit: int = 25,
        auto_create_deals: bool = True,
    ) -> dict:
        if not self.linkedin:
            return {"error": "LinkedIn not connected"}

        db = SessionLocal()
        try:
            flow = LinkedInSalesFlow(self.linkedin, db)
            result = await flow.prospect_to_pipeline(
                keywords=keywords,
                industry=industry,
                title=title,
                location=location,
                limit=limit,
                auto_create_deals=auto_create_deals,
            )
            return result
        finally:
            db.close()
