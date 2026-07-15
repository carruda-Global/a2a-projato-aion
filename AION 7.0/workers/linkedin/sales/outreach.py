import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

OUTREACH_TEMPLATES = {
    "default": {
        "subject": "Idea for {company}",
        "steps": [
            {
                "day": 0,
                "channel": "linkedin",
                "subject": "Connecting",
                "template": (
                    "Hi {name}, saw your work with {industry} at {company}. "
                    "We help agencies like yours {value_proposition}. "
                    "Worth a quick chat?"
                ),
            },
            {
                "day": 3,
                "channel": "email",
                "subject": "Idea for {company}",
                "template": (
                    "Hi {name},\n\n"
                    "Saw your work with {industry} at {company} and thought "
                    "this might help.\n\n"
                    "{value_proposition}\n\n"
                    "Got 15 minutes this week for a quick call?"
                ),
            },
            {
                "day": 7,
                "channel": "linkedin",
                "subject": "Follow-up",
                "template": (
                    "Hi {name}, just following up on my last message. "
                    "I think we could help {company} {value_proposition}. "
                    "Worth a quick chat?"
                ),
            },
        ],
    },
    "affiliate": {
        "subject": "Earn 20% recurring referring {company}'s clients",
        "steps": [
            {
                "day": 0,
                "channel": "linkedin",
                "subject": "Connecting",
                "template": (
                    "Hi {name}, saw {company}'s work in {industry}. "
                    "We run a referral program for consultants/agencies like yours -- "
                    "20% recurring commission for 12 months on every client you refer "
                    "to our AI Voice Receptionist. No selling required, just a link. "
                    "Worth a quick look?"
                ),
            },
            {
                "day": 3,
                "channel": "email",
                "subject": "20% recurring commission -- {company}",
                "template": (
                    "Hi {name},\n\n"
                    "You work with small businesses in {industry} at {company} -- "
                    "exactly the kind of client who loses leads to missed calls.\n\n"
                    "{value_proposition}\n\n"
                    "Refer them to our AI Voice Receptionist and earn 20% recurring "
                    "commission for 12 months per client, no cap. Free to join, "
                    "no selling on your end -- just your referral link.\n\n"
                    "Interested?"
                ),
            },
        ],
    },
    "regulatory": {
        "subject": "Adequação regulatória para {industry}",
        "steps": [
            {
                "day": 0,
                "channel": "linkedin",
                "subject": "Regulatório {industry}",
                "template": (
                    "Olá {name}, notei que {company} atua em {industry}. "
                    "Com as novas exigências regulatórias, desenvolvemos "
                    "uma solução que pode ajudar na adequação contínua. "
                    "Posso te mostrar?"
                ),
            },
            {
                "day": 4,
                "channel": "email",
                "subject": "Adequação {industry} - {company}",
                "template": (
                    "Oi {name},\n\n"
                    "Para empresas de {industry}, a conformidade regulatória "
                    "é um desafio constante. Nossa plataforma automatiza "
                    "todo o processo com agentes de IA especializados.\n\n"
                    "{value_proposition}\n\n"
                    "Agenda uma demo?"
                ),
            },
        ],
    },
    "cross_sell": {
        "subject": "Otimizando sua experiência",
        "steps": [
            {
                "day": 0,
                "channel": "email",
                "subject": "Novidade para sua empresa",
                "template": (
                    "Oi {name}, tudo bem?\n\n"
                    "Notei que sua empresa utiliza nossos serviços. "
                    "Temos um novo agente que pode ajudar com "
                    "{value_proposition}.\n\n"
                    "Clientes do seu segmento estão economizando "
                    "até 40% de tempo.\n\n"
                    "Vamos agendar uma conversa?"
                ),
            },
        ],
    },
}


def select_template(lead: dict) -> str:
    industry = (lead.get("industry") or "").lower()
    summary = (lead.get("summary") or "").lower()

    regulatory_keywords = ["lgpd", "regulatory", "compliance", "nr-", "norma"]
    if any(kw in summary for kw in regulatory_keywords):
        return "regulatory"
    if any(kw in industry for kw in ["regulatory", "compliance", "healthcare", "financial"]):
        return "regulatory"

    affiliate_keywords = ["marketing", "advertising", "consulting", "consultant", "freelance"]
    if any(kw in industry for kw in affiliate_keywords):
        return "affiliate"

    return "default"


def generate_outreach_sequence(
    lead: dict,
    value_proposition: str = "otimizar processos com IA especializada",
    template_name: str | None = None,
) -> list[dict]:
    template_name = template_name or select_template(lead)
    template = OUTREACH_TEMPLATES.get(template_name, OUTREACH_TEMPLATES["default"])

    fmt = {
        "name": lead.get("name", "?"),
        "company": lead.get("company", "sua empresa"),
        "industry": lead.get("industry", "mercado"),
        "value_proposition": value_proposition,
    }
    steps = []
    for step in template["steps"]:
        content = step["template"].format(**fmt)
        subject = step["subject"].format(**fmt)
        scheduled_at = datetime.utcnow() + timedelta(days=step["day"])
        steps.append({
            "step_number": step["day"],
            "channel": step["channel"],
            "subject": subject,
            "content": content,
            "scheduled_at": scheduled_at.isoformat(),
            "status": "pending",
        })

    return steps


def generate_linkedin_message(lead: dict, value_proposition: str = "") -> str:
    # Delegates to the same template dict as generate_outreach_sequence/
    # generate_email_content instead of a separately hardcoded string --
    # this used to be a standalone Portuguese-only message, which broke
    # outreach to the real English-speaking US/UK/CA/AU lead pool (e.g.
    # value_proposition text in English got spliced into a Portuguese
    # sentence).
    template_name = select_template(lead)
    template = OUTREACH_TEMPLATES.get(template_name, OUTREACH_TEMPLATES["default"])
    step = next((s for s in template["steps"] if s["channel"] == "linkedin"), template["steps"][0])
    fmt = {
        "name": lead.get("name", "?"),
        "company": lead.get("company", "your company"),
        "industry": lead.get("industry", "your market"),
        "value_proposition": value_proposition or "optimize processes with specialized AI",
    }
    return step["template"].format(**fmt)


def generate_email_content(lead: dict, value_proposition: str = "") -> dict:
    template_name = select_template(lead)
    template = OUTREACH_TEMPLATES.get(template_name, OUTREACH_TEMPLATES["default"])
    step = template["steps"][1] if len(template["steps"]) > 1 else template["steps"][0]

    fmt = {
        "name": lead.get("name", "?"),
        "company": lead.get("company", "sua empresa"),
        "industry": lead.get("industry", "mercado"),
        "value_proposition": value_proposition or "otimizar processos com IA especializada",
    }

    return {
        "to": lead.get("email", ""),
        "subject": step["subject"].format(**fmt),
        "content": step["template"].format(**fmt),
    }
