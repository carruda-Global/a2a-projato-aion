import logging
from datetime import datetime
from sales.database import SessionLocal
from sales import models

logger = logging.getLogger(__name__)


class ActivationAgent:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    async def activate_agents(self, lead_id: int, plan_id: str = "compliance_essencial") -> dict:
        lead = self.db.query(models.Lead).filter(models.Lead.id == lead_id).first()
        if not lead:
            return {"error": "Lead not found"}

        agent_map = {
            "compliance_essencial": ["nr1_psicossocial", "lgpd_operacional"],
            "regulatory_pro": ["nr1_psicossocial", "lgpd_operacional", "canal_denuncias", "igualdade_salarial", "compliance_anticorrupcao"],
            "esg_carbono": ["esg_ifrs", "inventario_carbono", "escopo3_fornecedores"],
            "microsoft_pack": ["regulatory_analyst", "compliance_pm", "channel_agent", "knowledge_agent", "facilitator_agent", "dev_experience"],
            "full_suite": [
                "spec_analyst", "procurement", "inventory", "logistics", "field_execution",
                "bim_coordinator", "requirements_analyst", "engineering_assistant", "work_synopsis",
                "photo_intelligence", "rfi_creation", "compliance",
                "nr1_psicossocial", "tributario_cbs_ibs", "lgpd_operacional",
                "esg_ifrs", "inventario_carbono", "escopo3_fornecedores",
                "canal_denuncias", "igualdade_salarial", "compliance_anticorrupcao",
                "regulatory_analyst", "compliance_pm", "channel_agent", "knowledge_agent",
                "facilitator_agent", "dev_experience",
                "linkedin_content", "linkedin_prospect", "linkedin_analytics",
            ],
        }

        agents = agent_map.get(plan_id, [])
        if not agents:
            return {"error": f"Plan {plan_id} not found"}

        activity = models.Activity(
            lead_id=lead.id,
            type="activation",
            subject=f"Ativacao do plano: {plan_id}",
            description=f"{len(agents)} agentes ativados: {', '.join(agents[:5])}...",
            outcome="positive",
        )
        self.db.add(activity)

        lead.status = models.LeadStatus.CONVERTED.value

        deal = self.db.query(models.Deal).filter(models.Deal.lead_id == lead.id).first()
        if deal:
            deal.stage = models.DealStage.CLOSED_WON.value
            deal.probability = 100

        self.db.commit()

        logger.info(f"Agentes ativados para {lead.name}: {plan_id} ({len(agents)} agentes)")
        return {
            "status": "activated",
            "lead_name": lead.name,
            "plan": plan_id,
            "agents_activated": len(agents),
            "agents": agents,
        }

    async def get_activation_status(self, lead_id: int) -> dict:
        lead = self.db.query(models.Lead).filter(models.Lead.id == lead_id).first()
        if not lead:
            return {"error": "Lead not found"}

        activities = self.db.query(models.Activity).filter(
            models.Activity.lead_id == lead.id,
            models.Activity.type == "activation",
        ).all()

        return {
            "lead_name": lead.name,
            "status": lead.status,
            "activations": len(activities),
            "last_activation": activities[-1].created_at.isoformat() if activities else None,
        }
