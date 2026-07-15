import logging
from datetime import datetime
from integrations.site.webhook import receive_lead, start_nurture_campaign
from agents.sales.qualify import LeadQualifier
from integrations.site.analytics import SiteAnalytics

logger = logging.getLogger(__name__)


async def process_site_lead(data: dict) -> dict:
    result = await receive_lead(data)

    if result.get("status") == "created":
        qualifier = LeadQualifier()
        score = await qualifier.score_lead(result["lead_id"])
        qualifier.close()

        if score.get("total_score", 0) >= 60:
            await start_nurture_campaign(result["lead_id"], "welcome")

        result["qualification"] = score

    return result


async def get_site_metrics() -> dict:
    analytics = SiteAnalytics()
    metrics = analytics.get_conversion_metrics()
    analytics.close()
    return metrics
