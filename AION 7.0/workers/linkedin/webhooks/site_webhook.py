import logging
from datetime import datetime
from fastapi import FastAPI, Request
from integrations.site.webhook import receive_lead, start_nurture_campaign
from agents.sales.qualify import LeadQualifier

logger = logging.getLogger(__name__)

app = FastAPI(title="AION Site Webhook")


@app.post("/webhook/lead")
async def webhook_receive_lead(request: Request):
    data = await request.json()
    logger.info(f"Lead recebido do site: {data.get('name', '?')}")

    result = await receive_lead(data)

    if result.get("status") == "created":
        qualifier = LeadQualifier()
        score = await qualifier.score_lead(result["lead_id"])
        qualifier.close()

        if score.get("total_score", 0) >= 60:
            await start_nurture_campaign(result["lead_id"], "welcome")

        result["qualification"] = score

    return result


@app.post("/webhook/diagnostic")
async def webhook_diagnostic(request: Request):
    data = await request.json()
    logger.info(f"Diagnostico solicitado: {data.get('name', '?')}")

    lead_result = await receive_lead(data)
    if lead_result.get("status") == "created":
        from integrations.site.analytics import SiteAnalytics
        analytics = SiteAnalytics()
        analytics.track_diagnostic_request(lead_result["lead_id"], data.get("diagnostic_type", "compliance"))
        analytics.close()

        await start_nurture_campaign(lead_result["lead_id"], "diagnostic")

    return lead_result


@app.get("/webhook/metrics")
async def webhook_metrics():
    from integrations.site.analytics import SiteAnalytics
    analytics = SiteAnalytics()
    metrics = analytics.get_conversion_metrics()
    analytics.close()
    return metrics
