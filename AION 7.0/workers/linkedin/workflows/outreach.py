import logging
from datetime import datetime
from orchestrator.workflow_runner import WorkflowRunner
from sales.database import SessionLocal
from sales import models, outreach

logger = logging.getLogger(__name__)


async def run_outreach_workflow() -> dict:
    db = SessionLocal()
    try:
        leads = db.query(models.Lead).filter(
            models.Lead.score >= 60,
            models.Lead.status == models.LeadStatus.QUALIFIED.value,
        ).limit(20).all()

        results = []
        for lead in leads:
            lead_data = {
                "name": lead.name,
                "company": lead.company or "sua empresa",
                "industry": lead.industry or "mercado",
                "email": lead.email or "",
            }

            seq = outreach.generate_outreach_sequence(
                lead=lead_data,
                value_proposition="conhecer o EcoSystem AION gratuitamente",
            )

            for step in seq:
                db.add(models.OutreachStep(
                    lead_id=lead.id,
                    step_number=step["step_number"],
                    channel=step["channel"],
                    subject=step["subject"],
                    content=step["content"],
                    status="pending",
                ))

            lead.status = models.LeadStatus.CONTACTED.value
            results.append({"lead": lead.name, "steps": len(seq)})

        db.commit()
        return {
            "workflow": "Outreach Inicial AION",
            "leads_processed": len(results),
            "results": results,
            "completed_at": datetime.utcnow().isoformat(),
        }
    finally:
        db.close()
