import os
import logging
import stripe
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/usage", tags=["usage_billing"])
logger = logging.getLogger(__name__)

STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# ── Pay-per-diagnosis — preço por diagnóstico completo ───────────────────────
# Alinhado ao valor entregue: diagnóstico que evita multas de €10M–€35M
# Regra: preço mínimo = 1% do risco que mitiga

PRICING_PER_DIAGNOSIS = {
    # Brasil — preço em BRL (fator 0.60 vs USD)
    "BR": {
        "nr1_diagnostico":      ("brl",  9900,  "Diagnóstico NR-1 Riscos Psicossociais — evita multa R$10k/empregado"),
        "lgpd_scan":            ("brl", 14900,  "Scan LGPD completo — evita sanção ANPD até R$50M"),
        "esg_diagnostico":      ("brl", 19900,  "Diagnóstico ESG IFRS S1/S2 completo"),
        "carbono_inventario":   ("brl", 24900,  "Inventário GHG Protocol Escopo 1+2"),
        "anticorrupcao_check":  ("brl", 19900,  "Diagnóstico integridade CGU/Lei 12.846"),
        "tributario_cbs_ibs":   ("brl", 14900,  "Classificação CBS/IBS reforma tributária"),
    },
    # US / Global — preço em USD
    "US": {
        "eu_ai_act_check":      ("usd",  9900,  "EU AI Act readiness — avoids fines up to €35M or 7% global turnover"),
        "csrd_assessment":      ("usd", 14900,  "CSRD double materiality assessment — mandatory for 50k+ EU companies"),
        "dora_gap_analysis":    ("usd", 14900,  "DORA gap analysis — ICT risk, incident reporting, TLPT"),
        "soc2_gap":             ("usd",  9900,  "SOC2 Type II gap analysis — required by US enterprise clients"),
        "iso27001_gap":         ("usd",  9900,  "ISO 27001:2022 gap analysis & ISMS roadmap"),
        "nis2_check":           ("usd",  9900,  "NIS2 scope determination & implementation roadmap"),
        "vendor_risk_scan":     ("usd",  7900,  "Vendor risk assessment — 3rd party compliance scoring"),
        "contract_risk":        ("usd",  4900,  "Contract risk analysis & DPA compliance check"),
        "whistleblower_setup":  ("usd",  9900,  "EU Directive 2019/1937 whistleblower channel setup"),
        "sanctions_screen":     ("usd",  2900,  "Sanctions screening for M&A / onboarding"),
        "ma_due_diligence":     ("usd", 19900,  "M&A compliance due diligence — full report"),
        "regulatory_impact":    ("usd",  4900,  "Regulatory change impact analysis — 50+ jurisdictions"),
        "board_esg_report":     ("usd", 14900,  "Board ESG report — executive dashboard + audit committee"),
    },
    # México
    "MX": {
        "lfpdppp_check":        ("mxn", 199000, "Diagnóstico LFPDPPP — evita multa hasta MXN$4.8M"),
        "eu_ai_act_check":      ("usd",  9900,  "EU AI Act readiness assessment"),
    },
    # Colômbia
    "CO": {
        "ley1581_check":        ("cop", 35000000, "Diagnóstico Ley 1581 protección de datos"),
    },
    # Argentina
    "AR": {
        "sdr_diagnostic":       ("usd",  4900,  "Diagnóstico SDR + pipeline de vendas"),
    },
    # Europa (EUR)
    "EU": {
        "eu_ai_act_check":      ("eur",  9900,  "EU AI Act readiness — August 2026 deadline"),
        "csrd_assessment":      ("eur", 14900,  "CSRD double materiality assessment"),
        "dora_gap_analysis":    ("eur", 14900,  "DORA gap analysis for financial entities"),
        "nis2_check":           ("eur",  9900,  "NIS2 scope & implementation roadmap"),
        "gdpr_scan":            ("eur",  9900,  "GDPR compliance scan & DPA review"),
        "whistleblower_setup":  ("eur",  9900,  "EU Directive 2019/1937 channel setup"),
    },
}

# ── Pay-per-call metered — $0.50/chamada para enterprise via A2A ─────────────
# Stripe Metered Billing: empresa paga no final do mês pelo uso real
# Ideal para integrações via A2A protocol (Google ADK, Vertex AI, etc.)

METERED_PRICE_USD_CENTS = 50  # $0.50 por chamada de agente

# Stripe Price IDs para metered billing (criar via API na primeira vez)
# Estes IDs são gerados pelo Stripe e armazenados como env vars
METERED_PRICE_IDS = {
    "eu_ai_act_check":  os.getenv("STRIPE_METER_EU_AI_ACT", ""),
    "csrd_assessment":  os.getenv("STRIPE_METER_CSRD", ""),
    "dora_gap_analysis": os.getenv("STRIPE_METER_DORA", ""),
    "nr1_diagnostico":  os.getenv("STRIPE_METER_NR1", ""),
    "lgpd_scan":        os.getenv("STRIPE_METER_LGPD", ""),
    "default":          os.getenv("STRIPE_METER_DEFAULT", ""),
}


class PayPerUseRequest(BaseModel):
    email: str
    agent_id: str
    market: str = "US"


class MeteredUsageRequest(BaseModel):
    subscription_item_id: str  # Stripe subscription item ID do cliente enterprise
    agent_id: str
    quantity: int = 1


def _stripe():
    stripe.api_key = STRIPE_KEY
    return stripe


async def _create_checkout(currency: str, amount_cents: int, description: str, email: str) -> str:
    try:
        s = _stripe()
        session = s.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": description},
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://global-engenharia.com/ecosystem?sucesso=1",
            cancel_url="https://global-engenharia.com/ecosystem",
            customer_email=email,
            metadata={"agent": description, "currency": currency},
        )
        return session.url
    except Exception as e:
        logger.error("[BILLING] Checkout error: %s", e)
        return ""


async def _report_metered_usage(subscription_item_id: str, quantity: int) -> bool:
    """Reporta uso para Stripe Metered Billing — cobra $0.50 x quantity no final do mês."""
    try:
        s = _stripe()
        s.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=quantity,
            action="increment",
        )
        logger.info("[BILLING] Metered: %d calls reported for %s", quantity, subscription_item_id)
        return True
    except Exception as e:
        logger.error("[BILLING] Metered usage error: %s", e)
        return False


async def _create_metered_subscription(email: str, price_id: str) -> str:
    """Cria assinatura metered para enterprise — cobra por chamada no final do mês."""
    try:
        s = _stripe()
        customer = s.Customer.create(email=email)
        session = s.checkout.Session.create(
            customer=customer["id"],
            payment_method_types=["card"],
            line_items=[{"price": price_id}],
            mode="subscription",
            success_url="https://global-engenharia.com/ecosystem?enterprise=1",
            cancel_url="https://global-engenharia.com/ecosystem",
        )
        return session.url
    except Exception as e:
        logger.error("[BILLING] Metered subscription error: %s", e)
        return ""


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/pay-per-use/{market}/{agent_id}")
async def create_usage_payment(market: str, agent_id: str, request: Request):
    """Pay-per-diagnosis: gera link Stripe Checkout para diagnóstico único."""
    data = await request.json()
    email = data.get("email", "")
    market = market.upper()

    catalog = PRICING_PER_DIAGNOSIS.get(market, PRICING_PER_DIAGNOSIS["US"])
    if agent_id not in catalog:
        return {"error": f"Agent '{agent_id}' not available for market '{market}'", "available": list(catalog.keys())}

    currency, amount_cents, description = catalog[agent_id]
    checkout_url = await _create_checkout(currency, amount_cents, description, email)
    return {
        "checkout_url": checkout_url,
        "agent_id": agent_id,
        "market": market,
        "price": f"{currency.upper()} {amount_cents/100:.2f}",
        "description": description,
    }


@router.post("/metered/report")
async def report_metered_usage(req: MeteredUsageRequest):
    """Enterprise metered billing: reporta uso de agente ($0.50/chamada)."""
    ok = await _report_metered_usage(req.subscription_item_id, req.quantity)
    return {"reported": ok, "calls": req.quantity, "agent": req.agent_id, "rate": "$0.50/call"}


@router.post("/metered/subscribe")
async def create_metered_subscription(request: Request):
    """Enterprise: cria assinatura metered para billing por chamada de agente."""
    data = await request.json()
    email = data.get("email", "")
    agent_id = data.get("agent_id", "default")
    price_id = METERED_PRICE_IDS.get(agent_id) or METERED_PRICE_IDS.get("default", "")
    if not price_id:
        return {"error": "Metered price not configured. Contact sales: contact@global-engenharia.com"}
    checkout_url = await _create_metered_subscription(email, price_id)
    return {"checkout_url": checkout_url, "model": "metered", "rate": "$0.50 per agent call"}


@router.get("/catalog/{market}")
async def get_catalog(market: str):
    """Retorna catálogo de preços pay-per-use para o mercado."""
    market = market.upper()
    catalog = PRICING_PER_DIAGNOSIS.get(market, PRICING_PER_DIAGNOSIS["US"])
    return {
        "market": market,
        "model_diagnosis": {
            agent: {"currency": v[0].upper(), "price": f"{v[1]/100:.2f}", "description": v[2]}
            for agent, v in catalog.items()
        },
        "model_metered": {
            "rate": "$0.50 per API call",
            "billing": "monthly (end of month)",
            "min_commitment": "none",
            "best_for": "Enterprise integrations via A2A protocol",
        },
    }


@router.get("/catalog")
async def get_all_catalogs():
    """Todos os catálogos por mercado."""
    return {
        market: {
            agent: {"currency": v[0].upper(), "price": f"{v[1]/100:.2f}", "description": v[2]}
            for agent, v in catalog.items()
        }
        for market, catalog in PRICING_PER_DIAGNOSIS.items()
    }
