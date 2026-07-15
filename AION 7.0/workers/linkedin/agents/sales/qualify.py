import logging
from datetime import datetime
from sales.database import SessionLocal, init_db
from sales import models, pipeline, scoring
from integrations.site.analytics import SiteAnalytics

logger = logging.getLogger(__name__)


class LeadQualifier:
    def __init__(self):
        init_db()
        self.db = SessionLocal()
        self.analytics = SiteAnalytics()

    def close(self):
        self.db.close()
        self.analytics.close()

    async def execute(self, context: dict) -> dict:
        """Real dispatcher -- same missing-method gap as ProspectAgent: had
        no execute(), so workflow steps routed to agent="lead_qualifier"
        (score_leads, store_leads in linkedin_workflow.yaml; qualify_engagement
        in outreach_workflow.yaml) failed immediately with "Agent
        lead_qualifier has no execute method", never actually scoring or
        moving a single real lead."""
        action = context.get("action", "score_lead")
        if action == "score_lead":
            lead_id = context.get("lead_id")
            if lead_id:
                return await self.score_lead(lead_id)
            new_leads = pipeline.get_leads_by_score(self.db, min_score=0, limit=100)
            scored = [await self.score_lead(l.id) for l in new_leads if l.score == 0]
            return {"scored_count": len(scored), "results": scored}
        if action == "save_to_pipeline":
            status = context.get("status", "prospected")
            min_score = context.get("thresholds", {}).get("medium_score", 50) if "thresholds" in context else 0
            leads = pipeline.get_leads_by_score(self.db, min_score=min_score, limit=100)
            for lead in leads:
                lead.status = status
            self.db.commit()
            return {"updated_count": len(leads), "status": status}
        if action == "update_lead_score":
            lead_id = context.get("lead_id")
            increase = context.get("increase", 0)
            if not lead_id:
                return {"error": "lead_id required"}
            lead = self.db.query(models.Lead).filter(models.Lead.id == lead_id).first()
            if not lead:
                return {"error": "Lead not found"}
            lead.score = min(lead.score + increase, 100)
            self.db.commit()
            return {"lead_id": lead_id, "new_score": lead.score}
        return {"error": f"Unknown action: {action}"}

    async def score_lead(self, lead_id: int) -> dict:
        lead = pipeline.score_lead(self.db, lead_id)
        if not lead:
            return {"error": "Lead not found"}

        behavior = self.analytics.get_lead_score_by_behavior(lead_id)

        total_score = min(lead.score + behavior.get("behavior_score", 0), 100)
        label = "hot" if total_score >= 80 else "warm" if total_score >= 60 else "tepid" if total_score >= 40 else "cold"

        result = {
            "lead_id": lead.id,
            "name": lead.name,
            "bant_score": lead.score,
            "behavior_score": behavior.get("behavior_score", 0),
            "total_score": total_score,
            "label": label,
        }

        if total_score >= 80:
            lead.status = models.LeadStatus.QUALIFIED.value
            self.db.commit()
            result["action"] = "schedule_demo"
            result["message"] = "Lead qualificado para demonstracao"
        elif total_score >= 60:
            result["action"] = "start_nurture"
            result["message"] = "Iniciar nutricao automatica"
        else:
            result["action"] = "continue_nurture"
            result["message"] = "Continuar nutricao"

        return result

    async def get_qualified_for_demo(self, min_score: int = 80) -> list[dict]:
        leads = pipeline.get_leads_by_score(self.db, min_score=min_score)
        return [
            {
                "id": l.id,
                "name": l.name,
                "company": l.company,
                "score": l.score,
                "email": l.email,
                "phone": l.phone,
            }
            for l in leads
        ]
