import logging
from datetime import datetime
from sqlalchemy.orm import Session
from . import models, pipeline, scoring, outreach
from integrations import LinkedInIntegration

logger = logging.getLogger(__name__)


class LinkedInSalesFlow:
    def __init__(self, linkedin: LinkedInIntegration, db: Session):
        self.linkedin = linkedin
        self.db = db

    async def prospect_to_pipeline(
        self,
        keywords: str | None = None,
        company: str | None = None,
        title: str | None = None,
        location: str | None = None,
        industry: str | None = None,
        limit: int = 10,
        auto_create_deals: bool = True,
    ) -> dict:
        logger.info(f"Prospecting LinkedIn: {keywords or ''} {company or ''} {title or ''}")

        results = await self.linkedin.tools.search_people(
            keywords=keywords,
            company=company,
            title=title,
            location=location,
            industry=industry,
            limit=limit,
        )

        leads_created = []
        for profile in results:
            linkedin_id = profile.get("id") or profile.get("urn", "").split(":")[-1]
            profile_url = f"https://www.linkedin.com/in/{linkedin_id}/"
            name = profile.get("name") or profile.get("localizedName", "Unknown")
            headline = profile.get("headline", "")

            lead = pipeline.create_lead(
                db=self.db,
                name=name,
                company=company or profile.get("company"),
                title=headline,
                linkedin_url=profile_url,
                linkedin_id=linkedin_id,
                source="linkedin",
                industry=industry,
                location=location,
            )

            if auto_create_deals and lead.score >= 60:
                deal = pipeline.create_deal(db=self.db, lead_id=lead.id)
                if deal:
                    logger.info(f"Deal auto-created for {lead.name} (score: {lead.score})")
                    seq = outreach.generate_outreach_sequence(
                        lead={"name": lead.name, "company": lead.company, "industry": lead.industry},
                    )
                    for step in seq:
                        self.db.add(models.OutreachStep(
                            lead_id=lead.id,
                            deal_id=deal.id,
                            step_number=step["step_number"],
                            channel=step["channel"],
                            subject=step["subject"],
                            content=step["content"],
                            status="pending",
                        ))
                    self.db.commit()

            leads_created.append({
                "id": lead.id,
                "name": lead.name,
                "score": lead.score,
                "label": (lead.score_breakdown or {}).get("label", "unknown"),
                "deal_created": auto_create_deals and lead.score >= 60,
            })

        return {
            "total_found": len(results),
            "leads_created": len(leads_created),
            "leads": leads_created,
            "pipeline": pipeline.get_pipeline_summary(self.db),
        }

    async def enrich_and_score(
        self,
        linkedin_id: str,
        auto_create_deal: bool = True,
    ) -> dict:
        profile = await self.linkedin.tools.get_profile(person_id=linkedin_id)

        existing = self.db.query(models.Lead).filter(
            models.Lead.linkedin_id == linkedin_id
        ).first()

        if existing:
            lead = pipeline.score_lead(self.db, existing.id)
        else:
            lead = pipeline.create_lead(
                db=self.db,
                name=profile.get("name", "Unknown"),
                title=profile.get("headline"),
                linkedin_id=linkedin_id,
                linkedin_url=f"https://www.linkedin.com/in/{linkedin_id}/",
                source="linkedin",
            )

        result = {
            "lead_id": lead.id,
            "name": lead.name,
            "score": lead.score,
            "score_breakdown": lead.score_breakdown,
            "label": (lead.score_breakdown or {}).get("label", "unknown"),
            "is_new": not existing,
        }

        if auto_create_deal and lead.score >= 60 and not lead.deals:
            deal = pipeline.create_deal(self.db, lead_id=lead.id)
            if deal:
                result["deal_created"] = True
                result["deal_id"] = deal.id

        return result

    async def generate_pipeline_report(self) -> dict:
        summary = pipeline.get_pipeline_summary(self.db)

        deals_at_risk = pipeline.get_deals_at_risk(self.db)
        summary["deals_at_risk"] = [
            {
                "id": d.id,
                "lead_name": d.lead.name,
                "stage": d.stage,
                "value": d.value,
                "days_inactive": (datetime.utcnow() - d.updated_at).days,
            }
            for d in deals_at_risk
        ]

        hot_leads = pipeline.get_leads_by_score(self.db, min_score=80)
        summary["hot_leads"] = [
            {
                "id": l.id,
                "name": l.name,
                "company": l.company,
                "score": l.score,
                "title": l.title,
            }
            for l in hot_leads
        ]

        return summary
