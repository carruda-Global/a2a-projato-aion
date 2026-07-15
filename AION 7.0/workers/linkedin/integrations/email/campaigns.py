import logging
from datetime import datetime, timedelta
from sales.database import SessionLocal
from sales import models, outreach

logger = logging.getLogger(__name__)

DRIP_CAMPAIGNS = {
    "welcome": {
        "name": "Boas-vindas EcoSystem AION",
        "days": [0, 2, 5, 10],
        "channels": ["email", "email", "email", "linkedin"],
        "subjects": [
            "Bem-vindo ao EcoSystem AION - proximos passos",
            "Conheca nossos 59 agentes de IA",
            "Caso de uso: Compliance com IA",
            "Pronto para comecar? Trial gratis",
        ],
        "templates": [
            "Ola {name}, obrigado pelo interesse no EcoSystem AION. Em ate 48h seus agentes estarao prontos.",
            "Oi {name}, sabia que temos agente especifico para {industry}? Agende uma demonstracao.",
            "{name}, veja como a {company} pode automatizar compliance com IA em apenas 48h.",
            "{name}, quer testar gratuitamente? Seu trial de 15 dias esta pronto em global-engenharia.com/ecosystem",
        ],
    },
    "diagnostic": {
        "name": "Diagnostico Gratuito",
        "days": [1, 4, 8],
        "channels": ["email", "email", "linkedin"],
        "subjects": [
            "Seu diagnostico de compliance esta pronto",
            "Resultados do diagnostico - proximos passos",
            "Veja como resolver os pontos criticos",
        ],
        "templates": [
            "Ola {name}, seu diagnostico gratuito ficou pronto. Acesse o link para ver os resultados.",
            "Oi {name}, com base no diagnostico, recomendamos comecar pelo plano Compliance Essencial.",
            "{name}, quer agendar uma call para discutirmos os resultados?",
        ],
    },
    "abandoned_cart": {
        "name": "Carrinho Abandonado",
        "days": [1, 3, 7],
        "channels": ["email", "email", "linkedin"],
        "subjects": [
            "Voce deixou algo para tras",
            "Ainda esta avaliando?",
            "Ultima chance - trial gratuito",
        ],
        "templates": [
            "Ola {name}, notei que voce estava avaliando nossos planos. Posso ajudar com alguma duvida?",
            "Oi {name}, quer testar gratuitamente por 15 dias? Sem compromisso.",
            "{name}, seu trial gratuito esta esperando. Mais de 59 agentes prontos para sua empresa.",
        ],
    },
}


async def start_drip_campaign(lead_id: int, campaign_type: str = "welcome") -> dict:
    campaign = DRIP_CAMPAIGNS.get(campaign_type)
    if not campaign:
        return {"status": "error", "detail": f"Campaign {campaign_type} not found"}

    db = SessionLocal()
    try:
        lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
        if not lead:
            return {"status": "error", "detail": "Lead not found"}

        lead_data = {
            "name": lead.name,
            "company": lead.company or "sua empresa",
            "industry": lead.industry or "mercado",
        }

        count = 0
        for i, day in enumerate(campaign["days"]):
            channel = campaign["channels"][i] if i < len(campaign["channels"]) else "email"
            subject = campaign["subjects"][i] if i < len(campaign["subjects"]) else "Continuacao"
            template = campaign["templates"][i] if i < len(campaign["templates"]) else "Ola {name}"

            content = template.format(**lead_data)
            scheduled_at = datetime.utcnow() + timedelta(days=day)

            step = models.OutreachStep(
                lead_id=lead.id,
                step_number=day,
                channel=channel,
                subject=subject,
                content=content,
                status="pending",
            )
            db.add(step)
            count += 1

        db.commit()
        logger.info(f"Drip campaign '{campaign_type}' iniciada para lead {lead_id}: {count} steps")
        return {"status": "started", "campaign": campaign_type, "steps": count}
    except Exception as e:
        logger.error(f"Erro ao iniciar drip campaign: {e}")
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()


async def process_due_steps() -> list:
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        due = db.query(models.OutreachStep).filter(
            models.OutreachStep.status == "pending",
            models.OutreachStep.scheduled_at <= now,
        ).limit(50).all()

        processed = []
        for step in due:
            step.status = "sent"
            step.sent_at = now
            processed.append({
                "step_id": step.id,
                "lead_id": step.lead_id,
                "channel": step.channel,
                "subject": step.subject,
            })

        db.commit()
        return processed
    finally:
        db.close()
