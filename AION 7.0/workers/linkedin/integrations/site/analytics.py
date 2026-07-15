import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sales.database import SessionLocal
from sales import models

logger = logging.getLogger(__name__)


class SiteAnalytics:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def track_pageview(self, lead_id: int, page: str, referrer: str = "", utm_source: str = "", utm_medium: str = ""):
        activity = models.Activity(
            lead_id=lead_id,
            type="pageview",
            subject=f"Visitou: {page}",
            description=f"Ref: {referrer} | UTM: {utm_source}/{utm_medium}",
            outcome="pending",
        )
        self.db.add(activity)
        self.db.commit()

    def track_form_start(self, lead_id: int, form_name: str):
        activity = models.Activity(
            lead_id=lead_id,
            type="form_start",
            subject=f"Iniciou formulario: {form_name}",
            outcome="pending",
        )
        self.db.add(activity)
        self.db.commit()

    def track_diagnostic_request(self, lead_id: int, diagnostic_type: str):
        activity = models.Activity(
            lead_id=lead_id,
            type="diagnostic",
            subject=f"Solicitou diagnostico: {diagnostic_type}",
            outcome="pending",
        )
        self.db.add(activity)
        self.db.commit()

    def get_lead_score_by_behavior(self, lead_id: int) -> dict:
        lead = self.db.query(models.Lead).filter(models.Lead.id == lead_id).first()
        if not lead:
            return {"score": 0}

        activities = self.db.query(models.Activity).filter(
            models.Activity.lead_id == lead_id,
            models.Activity.created_at >= datetime.utcnow() - timedelta(days=30),
        ).all()

        pageviews = sum(1 for a in activities if a.type == "pageview")
        form_starts = sum(1 for a in activities if a.type == "form_start")
        diagnostics = sum(1 for a in activities if a.type == "diagnostic")

        engagement_score = min(pageviews * 5, 30)
        intent_score = min(form_starts * 15, 30)
        diagnostic_score = min(diagnostics * 20, 40)

        total = engagement_score + intent_score + diagnostic_score
        return {
            "behavior_score": total,
            "pageviews": pageviews,
            "form_starts": form_starts,
            "diagnostics": diagnostics,
            "engagement": engagement_score,
            "intent": intent_score,
            "diagnostic_score": diagnostic_score,
        }

    def get_conversion_metrics(self) -> dict:
        total = self.db.query(models.Lead).count()
        from_site = self.db.query(models.Lead).filter(models.Lead.source == "site_landing_page").count()
        qualified = self.db.query(models.Lead).filter(models.Lead.score >= 60).count()
        deals = self.db.query(models.Deal).count()
        won = self.db.query(models.Deal).filter(models.Deal.stage == models.DealStage.CLOSED_WON.value).count()

        return {
            "total_leads": total,
            "from_site": from_site,
            "qualified": qualified,
            "conversion_rate": round(qualified / max(total, 1) * 100, 1),
            "deals_created": deals,
            "deals_won": won,
            "win_rate": round(won / max(deals, 1) * 100, 1),
        }
