import logging
from datetime import datetime
from pydantic import BaseModel, EmailStr
from sales.database import SessionLocal
from sales import models, pipeline, scoring

logger = logging.getLogger(__name__)


class LeadCapture(BaseModel):
    name: str
    email: str
    company: str = ""
    phone: str = ""
    source: str = "site_landing_page"
    utm_source: str = ""
    utm_medium: str = ""
    utm_campaign: str = ""


async def receive_lead(data: dict) -> dict:
    capture = LeadCapture(**data)

    db = SessionLocal()
    try:
        existing = db.query(models.Lead).filter(models.Lead.email == capture.email).first()
        if existing:
            logger.info(f"Lead ja existe: {capture.email}")
            return {"status": "exists", "lead_id": existing.id}

        lead = pipeline.create_lead(
            db=db,
            name=capture.name,
            company=capture.company,
            email=capture.email,
            phone=capture.phone,
            source=capture.source,
        )

        db.commit()
        db.refresh(lead)

        score_data = {"score": lead.score, "label": (lead.score_breakdown or {}).get("label", "unknown")}

        logger.info(f"Lead capturado: {lead.name} ({lead.email}) - Score: {lead.score}")
        return {
            "status": "created",
            "lead_id": lead.id,
            "name": lead.name,
            "score": score_data,
        }
    except Exception as e:
        logger.error(f"Erro ao capturar lead: {e}")
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()


async def start_nurture_campaign(lead_id: int, campaign_type: str = "welcome") -> dict:
    from sales.outreach import generate_outreach_sequence

    db = SessionLocal()
    try:
        lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
        if not lead:
            return {"status": "error", "detail": "Lead not found"}

        lead_data = {
            "name": lead.name,
            "company": lead.company or "",
            "industry": lead.industry or "",
            "email": lead.email or "",
            "summary": lead.summary or "",
        }

        sequence = generate_outreach_sequence(
            lead=lead_data,
            value_proposition="testar o EcoSystem AION gratuitamente por 15 dias",
            template_name="default",
        )

        for step in sequence:
            seq_step = models.OutreachStep(
                lead_id=lead.id,
                step_number=step["step_number"],
                channel=step["channel"],
                subject=step["subject"],
                content=step["content"],
                status="pending",
            )
            db.add(seq_step)

        db.commit()
        logger.info(f"Nurture campaign iniciada para lead {lead_id}: {len(sequence)} steps")
        return {"status": "started", "steps": len(sequence)}
    except Exception as e:
        logger.error(f"Erro ao iniciar nurture: {e}")
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()
