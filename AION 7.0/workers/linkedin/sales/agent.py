import logging
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from . import models, pipeline, scoring, outreach
from .linkedin_flow import LinkedInSalesFlow

logger = logging.getLogger(__name__)


class SalesAgent:
    def __init__(self, linkedin=None, db: Session | None = None):
        self.linkedin = linkedin
        self.db = db or SessionLocal()
        init_db()

    def close(self):
        self.db.close()

    async def execute(self, context: dict) -> dict:
        action = context.get("action", "pipeline_summary")
        handlers = {
            "pipeline_summary": self._pipeline_summary,
            "create_lead": self._create_lead,
            "score_lead": self._score_lead,
            "qualify_lead": self._qualify_lead,
            "create_deal": self._create_deal,
            "move_deal": self._move_deal,
            "get_leads": self._get_leads,
            "get_deals": self._get_deals,
            "get_deals_at_risk": self._get_deals_at_risk,
            "generate_outreach": self._generate_outreach,
            "linkedin_prospect": self._linkedin_prospect,
            "linkedin_enrich": self._linkedin_enrich,
            "full_prospect_flow": self._full_prospect_flow,
        }
        handler = handlers.get(action)
        if not handler:
            return {"error": f"Unknown action: {action}"}
        return await handler(context)

    async def _pipeline_summary(self, context: dict) -> dict:
        return pipeline.get_pipeline_summary(self.db)

    async def _create_lead(self, context: dict) -> dict:
        lead = pipeline.import_linkedin_prospect(
            db=self.db,
            profile=context.get("profile", {}),
            linkedin_url=context.get("linkedin_url", ""),
            source=context.get("source", "other"),
        )
        return {
            "lead_id": lead.id,
            "name": lead.name,
            "score": lead.score,
            "score_breakdown": lead.score_breakdown,
        }

    async def _score_lead(self, context: dict) -> dict:
        lead = pipeline.score_lead(self.db, context["lead_id"])
        return {"lead_id": lead.id, "score": lead.score, "breakdown": lead.score_breakdown}

    async def _qualify_lead(self, context: dict) -> dict:
        lead = pipeline.qualify_lead(self.db, context["lead_id"])
        if not lead:
            return {"qualified": False, "message": "Lead score below 60 threshold"}
        return {"qualified": True, "lead_id": lead.id, "score": lead.score}

    async def _create_deal(self, context: dict) -> dict:
        deal = pipeline.create_deal(
            self.db,
            lead_id=context["lead_id"],
            value=context.get("value", 0),
        )
        if not deal:
            return {"error": "Lead not qualified for deal"}
        return {"deal_id": deal.id, "stage": deal.stage, "value": deal.value}

    async def _move_deal(self, context: dict) -> dict:
        deal = pipeline.move_deal(self.db, context["deal_id"], context["stage"])
        if not deal:
            return {"error": "Deal not found"}
        return {"deal_id": deal.id, "stage": deal.stage, "probability": deal.probability}

    async def _get_leads(self, context: dict) -> dict:
        leads = pipeline.get_leads_by_score(
            self.db,
            min_score=context.get("min_score", 0),
            limit=context.get("limit", 50),
        )
        return {
            "total": len(leads),
            "leads": [
                {
                    "id": l.id,
                    "name": l.name,
                    "company": l.company,
                    "title": l.title,
                    "score": l.score,
                    "label": (l.score_breakdown or {}).get("label", "unknown"),
                    "status": l.status,
                    "source": l.source,
                }
                for l in leads
            ],
        }

    async def _get_deals(self, context: dict) -> dict:
        stage = context.get("stage")
        query = self.db.query(models.Deal)
        if stage:
            query = query.filter(models.Deal.stage == stage)
        deals = query.order_by(models.Deal.updated_at.desc()).limit(context.get("limit", 50)).all()
        return {
            "total": len(deals),
            "deals": [
                {
                    "id": d.id,
                    "lead_name": d.lead.name,
                    "company": d.lead.company,
                    "stage": d.stage,
                    "value": d.value,
                    "probability": d.probability,
                }
                for d in deals
            ],
        }

    async def _get_deals_at_risk(self, context: dict) -> dict:
        deals = pipeline.get_deals_at_risk(self.db, days_inactive=context.get("days_inactive", 7))
        return {
            "total": len(deals),
            "deals": [
                {
                    "id": d.id,
                    "lead_name": d.lead.name,
                    "stage": d.stage,
                    "value": d.value,
                    "days_inactive": (datetime.utcnow() - d.updated_at).days,
                }
                for d in deals
            ],
        }

    async def _generate_outreach(self, context: dict) -> dict:
        lead_data = {
            "name": context.get("name", ""),
            "company": context.get("company", ""),
            "industry": context.get("industry", ""),
            "summary": context.get("summary", ""),
            "email": context.get("email", ""),
        }
        vp = context.get("value_proposition", "otimizar processos com IA especializada")

        seq = outreach.generate_outreach_sequence(lead_data, value_proposition=vp)
        linkedin_msg = outreach.generate_linkedin_message(lead_data, value_proposition=vp)
        email = outreach.generate_email_content(lead_data, value_proposition=vp)

        return {
            "sequence": seq,
            "linkedin_message": linkedin_msg,
            "email": email,
        }

    async def _linkedin_prospect(self, context: dict) -> dict:
        if not self.linkedin:
            return {"error": "LinkedIn not connected"}
        flow = LinkedInSalesFlow(self.linkedin, self.db)
        return await flow.prospect_to_pipeline(
            keywords=context.get("keywords"),
            company=context.get("company"),
            title=context.get("title"),
            location=context.get("location"),
            industry=context.get("industry"),
            limit=context.get("limit", 10),
            auto_create_deals=context.get("auto_create_deals", True),
        )

    async def _linkedin_enrich(self, context: dict) -> dict:
        if not self.linkedin:
            return {"error": "LinkedIn not connected"}
        flow = LinkedInSalesFlow(self.linkedin, self.db)
        return await flow.enrich_and_score(
            linkedin_id=context.get("linkedin_id", ""),
            auto_create_deal=context.get("auto_create_deal", True),
        )

    async def _full_prospect_flow(self, context: dict) -> dict:
        if not self.linkedin:
            return {"error": "LinkedIn not connected"}
        flow = LinkedInSalesFlow(self.linkedin, self.db)
        prospect_result = await flow.prospect_to_pipeline(
            keywords=context.get("keywords"),
            company=context.get("company"),
            title=context.get("title"),
            limit=context.get("limit", 10),
            auto_create_deals=True,
        )
        report = await flow.generate_pipeline_report()
        return {
            "prospecting": prospect_result,
            "pipeline_report": report,
        }
