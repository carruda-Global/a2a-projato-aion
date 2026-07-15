import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import models
from .scoring import score_bant

logger = logging.getLogger(__name__)

STAGE_PROBABILITY = {
    models.DealStage.DISCOVERY.value: 10,
    models.DealStage.QUALIFIED.value: 25,
    models.DealStage.PROPOSAL.value: 50,
    models.DealStage.NEGOTIATION.value: 75,
    models.DealStage.CLOSED_WON.value: 100,
    models.DealStage.CLOSED_LOST.value: 0,
}

STAGE_ORDER = {
    models.DealStage.DISCOVERY.value: 0,
    models.DealStage.QUALIFIED.value: 1,
    models.DealStage.PROPOSAL.value: 2,
    models.DealStage.NEGOTIATION.value: 3,
    models.DealStage.CLOSED_WON.value: 4,
    models.DealStage.CLOSED_LOST.value: 4,
}


def create_lead(
    db: Session,
    name: str,
    company: str | None = None,
    title: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    linkedin_url: str | None = None,
    linkedin_id: str | None = None,
    source: str = "other",
    industry: str | None = None,
    company_size: str | None = None,
    location: str | None = None,
    summary: str | None = None,
    skills: list | None = None,
    recent_posts: list | None = None,
) -> models.Lead:
    lead = models.Lead(
        name=name,
        company=company,
        title=title,
        email=email,
        phone=phone,
        linkedin_url=linkedin_url,
        linkedin_id=linkedin_id,
        source=source,
        industry=industry,
        company_size=company_size,
        location=location,
        summary=summary,
        skills=skills,
        recent_posts=recent_posts,
        status=models.LeadStatus.NEW.value,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    lead = score_lead(db, lead.id)
    return lead


def score_lead(db: Session, lead_id: int) -> models.Lead:
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise ValueError(f"Lead {lead_id} not found")

    scores = score_bant(
        title=lead.title,
        industry=lead.industry,
        company_size=lead.company_size,
        summary=lead.summary,
        recent_posts=lead.recent_posts,
        source=lead.source,
    )

    lead.bant_budget = scores.budget
    lead.bant_authority = scores.authority
    lead.bant_need = scores.need
    lead.bant_timeline = scores.timeline
    lead.score = scores.total
    lead.score_breakdown = scores.to_dict()

    db.commit()
    db.refresh(lead)
    logger.info(f"Lead {lead.name} scored: {scores.total}/100 ({scores.label})")
    return lead


def qualify_lead(db: Session, lead_id: int) -> models.Lead | None:
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        return None

    if lead.score >= 60:
        lead.status = models.LeadStatus.QUALIFIED.value
        db.commit()
        db.refresh(lead)
        return lead
    return None


def create_deal(db: Session, lead_id: int, value: float = 0) -> models.Deal | None:
    lead = qualify_lead(db, lead_id)
    if not lead:
        logger.warning(f"Lead {lead_id} not qualified for deal (score < 60)")
        return None

    deal = models.Deal(
        lead_id=lead_id,
        stage=models.DealStage.DISCOVERY.value,
        value=value,
        probability=STAGE_PROBABILITY[models.DealStage.DISCOVERY.value],
    )
    db.add(deal)
    lead.status = models.LeadStatus.CONVERTED.value
    db.commit()
    db.refresh(deal)
    logger.info(f"Deal created for lead {lead.name}, value: R${value:,.2f}")
    return deal


def move_deal(db: Session, deal_id: int, new_stage: str) -> models.Deal | None:
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        return None

    deal.stage = new_stage
    deal.probability = STAGE_PROBABILITY.get(new_stage, 10)
    db.commit()
    db.refresh(deal)
    logger.info(f"Deal {deal_id} moved to {new_stage}")
    return deal


def add_activity(
    db: Session,
    lead_id: int,
    type: str,
    subject: str,
    description: str = "",
    deal_id: int | None = None,
    outcome: str = "pending",
) -> models.Activity:
    activity = models.Activity(
        lead_id=lead_id,
        deal_id=deal_id,
        type=type,
        subject=subject,
        description=description,
        outcome=outcome,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_pipeline_summary(db: Session) -> dict:
    stages = {}
    for stage in models.DealStage:
        deals = db.query(models.Deal).filter(models.Deal.stage == stage.value).all()
        stages[stage.value] = {
            "count": len(deals),
            "total_value": sum(d.value for d in deals),
            "deals": [
                {
                    "id": d.id,
                    "lead_name": d.lead.name,
                    "company": d.lead.company,
                    "value": d.value,
                    "probability": d.probability,
                }
                for d in deals
            ],
        }

    weighted_pipeline = sum(
        d.value * (d.probability / 100)
        for d in db.query(models.Deal).all()
        if d.stage not in (models.DealStage.CLOSED_WON.value, models.DealStage.CLOSED_LOST.value)
    )

    return {
        "stages": stages,
        "total_deals": sum(s["count"] for s in stages.values()),
        "total_pipeline_value": sum(s["total_value"] for s in stages.values()),
        "weighted_pipeline": round(weighted_pipeline, 2),
        "won_deals": stages.get(models.DealStage.CLOSED_WON.value, {}).get("count", 0),
        "won_value": stages.get(models.DealStage.CLOSED_WON.value, {}).get("total_value", 0),
    }


def get_leads_by_score(db: Session, min_score: int = 0, limit: int = 50) -> list[models.Lead]:
    return (
        db.query(models.Lead)
        .filter(models.Lead.score >= min_score)
        .order_by(models.Lead.score.desc())
        .limit(limit)
        .all()
    )


def get_deals_at_risk(db: Session, days_inactive: int = 7) -> list[models.Deal]:
    cutoff = datetime.utcnow() - timedelta(days=days_inactive)
    return (
        db.query(models.Deal)
        .filter(
            models.Deal.updated_at < cutoff,
            models.Deal.stage.notin_(
                [models.DealStage.CLOSED_WON.value, models.DealStage.CLOSED_LOST.value]
            ),
        )
        .all()
    )


def import_linkedin_prospect(
    db: Session,
    profile: dict,
    linkedin_url: str,
    source: str = "linkedin",
) -> models.Lead:
    existing = db.query(models.Lead).filter(
        models.Lead.linkedin_id == profile.get("sub")
    ).first()
    if existing:
        return existing

    lead = create_lead(
        db=db,
        name=profile.get("name", profile.get("localizedName", "Unknown")),
        title=profile.get("headline", profile.get("title")),
        company=profile.get("company"),
        linkedin_url=linkedin_url,
        linkedin_id=profile.get("sub") or profile.get("id"),
        location=profile.get("location", {}).get("name") if isinstance(profile.get("location"), dict) else profile.get("location"),
        summary=profile.get("summary"),
        source=source,
    )
    return lead
