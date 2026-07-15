import asyncio
import os
import httpx
import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter
router = APIRouter(prefix="/api/nurture", tags=["nurture"])

RESEND_KEY = os.getenv("RESEND_API_KEY", "")
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# Sequência de emails automáticos para cada novo cliente Stripe
ONBOARDING_SEQUENCE = [
    {
        "day": 1,
        "subject": "Bem-vindo ao EcoSystem AEC — próximos passos",
        "body": """Olá,

Obrigado por assinar o EcoSystem AEC! Você agora tem acesso à plataforma mais completa de compliance AI do mercado.

Comece por aqui:
1. Acesse: https://engenheiro-producao-ai.onrender.com/docs
2. Teste o agente mais relevante para o seu setor
3. Integre via API REST (documentação completa disponível)

Nossos agentes mais populares esta semana:
• NR-1 Psicossocial — empresas com 20+ funcionários
• CSRD Reporting — empresas EU com FY2024
• DORA Compliance — setor financeiro
• SOC2 Readiness — SaaS e tech

Qualquer dúvida, responda este email.

Equipe EcoSystem AEC
https://global-engenharia.com/ecosystem""",
    },
    {
        "day": 7,
        "subject": "Como está indo? + dica de compliance desta semana",
        "body": """Olá,

Já faz uma semana desde que você começou com o EcoSystem AEC.

Dica desta semana: o prazo do EU AI Act (agosto 2026) está chegando.
Se a sua empresa usa sistemas de IA, rode nosso agente de readiness check:
POST https://engenheiro-producao-ai.onrender.com/api/eu-ai-act/readiness-check

Você sabia que 73% das empresas ainda não avaliaram se seus sistemas são 'alto risco' sob o EU AI Act?

Precisa de ajuda com algum agente específico? Responda aqui.

Equipe EcoSystem AEC""",
    },
    {
        "day": 30,
        "subject": "Sua opinião importa — deixe uma avaliação no G2",
        "body": """Olá,

Você está conosco há um mês. Esperamos que o EcoSystem AEC esteja economizando tempo e reduzindo risco de compliance para você.

Você poderia nos ajudar deixando uma avaliação?

👉 G2: https://g2.com (busque "EcoSystem AEC")
👉 Capterra: https://capterra.com (busque "EcoSystem AEC")

Leva menos de 3 minutos e ajuda outras empresas a nos encontrar.

Como agradecimento, ao enviar o screenshot da avaliação para carruda2307@gmail.com, você ganha 1 mês grátis na próxima renovação.

Obrigado!
Equipe EcoSystem AEC""",
    },
]

REACTIVATION_EMAIL = {
    "subject": "Sentimos sua falta — oferta especial para retornar",
    "body": """Olá,

Notamos que você cancelou sua assinatura do EcoSystem AEC.

Sabemos que o custo importa. Por isso, temos uma oferta especial:

🎁 Retorne hoje e ganhe 30% de desconto nos próximos 3 meses.

Use o código: RETORNO30
Link: https://global-engenharia.com/ecosystem

Além disso, lançamos 15 novos agentes desde que você saiu:
• Vendor Risk Assessment
• Board ESG Reporting
• M&A Due Diligence
• Whistleblower Management
• Contract Risk Analysis
• Regulatory Monitor (50+ jurisdições)
• Zapier/Make.com Integration

Tem 30 dias para usar o código.

Equipe EcoSystem AEC""",
}


async def _send_email(to: str, subject: str, body: str) -> bool:
    if not RESEND_KEY or not to:
        return False
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
                json={"from": "equipe@global-engenharia.com", "to": [to], "subject": subject, "text": body},
            )
        return r.status_code < 300
    except Exception as e:
        logger.warning("Email send error: %s", e)
        return False


async def _get_stripe_customers() -> list[dict]:
    if not STRIPE_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                "https://api.stripe.com/v1/customers",
                params={"limit": 100},
                auth=(STRIPE_KEY, ""),
            )
            return r.json().get("data", [])
    except Exception as e:
        logger.warning("Stripe customers error: %s", e)
        return []


async def _get_canceled_subscriptions() -> list[dict]:
    if not STRIPE_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                "https://api.stripe.com/v1/subscriptions",
                params={"limit": 50, "status": "canceled"},
                auth=(STRIPE_KEY, ""),
            )
            return r.json().get("data", [])
    except Exception as e:
        logger.warning("Stripe canceled error: %s", e)
        return []


async def auto_job_nurture_sequence():
    """Every 24h: sends onboarding emails to new Stripe customers based on days since signup."""
    await asyncio.sleep(9000)  # 2.5h warm-up
    while True:
        try:
            customers = await _get_stripe_customers()
            import time
            now = time.time()
            sent = 0
            for c in customers:
                email = c.get("email", "")
                created = c.get("created", 0)
                days_old = int((now - created) / 86400)
                for step in ONBOARDING_SEQUENCE:
                    if days_old == step["day"]:
                        ok = await _send_email(email, step["subject"], step["body"])
                        if ok:
                            sent += 1
                            logger.info("[NURTURE] Day-%d email sent to %s", step["day"], email[:20])
                        await asyncio.sleep(1)
            logger.info("[CRON] Nurture sequence: %d emails sent", sent)
        except Exception as e:
            logger.error("[CRON] Nurture error: %s", e)
        await asyncio.sleep(86400)  # 24h


async def auto_job_reactivation():
    """Every 7 days: sends reactivation email to canceled Stripe subscribers."""
    await asyncio.sleep(14400)  # 4h warm-up
    while True:
        try:
            canceled = await _get_canceled_subscriptions()
            sent = 0
            for sub in canceled:
                customer_id = sub.get("customer", "")
                if not customer_id:
                    continue
                async with httpx.AsyncClient(timeout=10) as client:
                    cr = await client.get(
                        f"https://api.stripe.com/v1/customers/{customer_id}",
                        auth=(STRIPE_KEY, ""),
                    )
                    email = cr.json().get("email", "")
                if email:
                    ok = await _send_email(email, REACTIVATION_EMAIL["subject"], REACTIVATION_EMAIL["body"])
                    if ok:
                        sent += 1
                    await asyncio.sleep(2)
            logger.info("[CRON] Reactivation: %d emails sent to canceled subscribers", sent)
        except Exception as e:
            logger.error("[CRON] Reactivation error: %s", e)
        await asyncio.sleep(604800)  # 7 dias


@router.get("/sequence")
async def get_sequence():
    return {"sequence": ONBOARDING_SEQUENCE, "reactivation": REACTIVATION_EMAIL}

@router.post("/trigger-welcome")
async def trigger_welcome(data: dict):
    """Trigger welcome email manually (called by Stripe webhook on new subscription)."""
    email = data.get("email", "")
    if email:
        ok = await _send_email(email, ONBOARDING_SEQUENCE[0]["subject"], ONBOARDING_SEQUENCE[0]["body"])
        return {"sent": ok, "to": email}
    return {"sent": False, "error": "no email provided"}
