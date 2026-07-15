import os
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/checkout", tags=["checkout"])

PLANS_CATALOG = {
    "compliance_essencial": {
        "name": "Compliance Essencial",
        "price_id": os.getenv("STRIPE_PRICE_COMPLIANCE_ESSENCIAL", ""),
        "price_brl": 590,
    },
    "regulatory_pro": {
        "name": "Regulatory Pro",
        "price_id": os.getenv("STRIPE_PRICE_REGULATORY_PRO", ""),
        "price_brl": 1490,
    },
    "esg_carbono": {
        "name": "ESG + Carbono",
        "price_id": os.getenv("STRIPE_PRICE_ESG_CARBONO", ""),
        "price_brl": 2490,
    },
    "tributario_cbs_ibs": {
        "name": "Tributário CBS/IBS",
        "price_id": os.getenv("STRIPE_PRICE_TRIBUTARIO", ""),
        "price_brl": 390,
    },
    "microsoft_pack": {
        "name": "Microsoft Pack",
        "price_id": os.getenv("STRIPE_PRICE_MICROSOFT_PACK", ""),
        "price_brl": 4482,
    },
    "full_suite": {
        "name": "Full Suite",
        "price_id": os.getenv("STRIPE_PRICE_FULL_SUITE", ""),
        "price_brl": 9497,
    },
    "micro_starter": {
        "name": "Micro Starter",
        "price_id": os.getenv("STRIPE_PRICE_MICRO_STARTER", ""),
        "price_brl": 199,
    },
    "micro_rh": {
        "name": "Micro RH",
        "price_id": os.getenv("STRIPE_PRICE_MICRO_RH", ""),
        "price_brl": 249,
    },
    "micro_dev": {
        "name": "Micro Dev",
        "price_id": os.getenv("STRIPE_PRICE_MICRO_DEV", ""),
        "price_brl": 249,
    },
    "micro_sales": {
        "name": "Micro Sales",
        "price_id": os.getenv("STRIPE_PRICE_MICRO_SALES", ""),
        "price_brl": 199,
    },
    "micro_full": {
        "name": "Micro Full (15 agentes)",
        "price_id": os.getenv("STRIPE_PRICE_MICRO_FULL", ""),
        "price_brl": 990,
    },
    "tech_starter": {
        "name": "Tech Starter",
        "price_id": os.getenv("STRIPE_PRICE_TECH_STARTER", ""),
        "price_brl": 1997,
    },
    "tech_professional": {
        "name": "Tech Professional",
        "price_id": os.getenv("STRIPE_PRICE_TECH_PROFESSIONAL", ""),
        "price_brl": 3497,
    },
    "tech_enterprise": {
        "name": "Tech Enterprise",
        "price_id": os.getenv("STRIPE_PRICE_TECH_ENTERPRISE", ""),
        "price_brl": 5997,
    },
}

BASE_URL = os.getenv("BASE_URL", "https://global-engenharia.com")
STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY", "")


class CheckoutRequest(BaseModel):
    plan_id: str
    customer_email: Optional[str] = None
    tenant_id: Optional[str] = None
    source: Optional[str] = None


class CheckoutResponse(BaseModel):
    id: str
    url: str


@router.post("/create-session", response_model=CheckoutResponse)
async def create_checkout_session(req: CheckoutRequest):
    plan = PLANS_CATALOG.get(req.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plano {req.plan_id} nao encontrado")

    price_id = plan["price_id"]
    if not price_id:
        raise HTTPException(status_code=500, detail=f"Price ID nao configurado para {req.plan_id}")

    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe API key nao configurada")

    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY

        PIX_MAX_BRL = 3000
        payment_method_types = ["card", "boleto"]
        if plan["price_brl"] <= PIX_MAX_BRL:
            payment_method_types.append("pix")

        session_params = {
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": f"{BASE_URL}/checkout/sucesso?session_id={{CHECKOUT_SESSION_ID}}&plan={req.plan_id}",
            "cancel_url": f"{BASE_URL}/ecosystem?canceled=true&plan={req.plan_id}",
            "branding_settings": {
                "display_name": "EcoSystem AION",
            },
            "payment_method_types": payment_method_types,
            "locale": "pt-BR",
            "allow_promotion_codes": True,
            "tax_id_collection": {"enabled": True},
        }

        if req.customer_email:
            session_params["customer_email"] = req.customer_email

        if req.tenant_id:
            session_params["client_reference_id"] = req.tenant_id

        if req.source:
            session_params["metadata"] = {"source": req.source}

        try:
            session = stripe.checkout.Session.create(**session_params)
        except stripe.error.InvalidRequestError as e:
            if "pix" in str(e).lower() and "pix" in session_params["payment_method_types"]:
                logger.warning("Pix ainda nao ativado na conta Stripe, tentando sem pix")
                session_params["payment_method_types"] = [
                    t for t in session_params["payment_method_types"] if t != "pix"
                ]
                session = stripe.checkout.Session.create(**session_params)
            else:
                raise

        logger.info(f"Checkout criado: {session.id} - {plan['name']}")
        return CheckoutResponse(id=session.id, url=session.url)

    except ImportError:
        raise HTTPException(status_code=500, detail="stripe library not installed. Run: pip install stripe")
    except Exception as e:
        logger.error(f"Erro ao criar checkout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans")
async def list_plans():
    return {
        "plans": [
            {
                "id": pid,
                "name": p["name"],
                "price_brl": p["price_brl"],
                "has_price_id": bool(p["price_id"]),
            }
            for pid, p in PLANS_CATALOG.items()
        ]
    }


class LeadCaptureRequest(BaseModel):
    email: str
    name: Optional[str] = None
    plan_id: Optional[str] = None
    page: Optional[str] = None
    source: Optional[str] = None
    linkedin_id: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


@router.post("/lead")
async def capture_lead(req: LeadCaptureRequest):
    """Salva o e-mail do visitante antes do redirect para o Stripe,
    para permitir remarketing mesmo se o checkout for abandonado."""
    try:
        from src.database.supabase_client import SupabaseClient
        from src.config import Settings

        db = SupabaseClient(Settings())
        db.client.table("chat_logs").insert({
            "message": "LEAD_CAPTURE",
            "response": (
                f"email={req.email} name={req.name or ''} plan={req.plan_id or ''} "
                f"source={req.source or ''} linkedin_id={req.linkedin_id or ''} "
                f"utm_source={req.utm_source or ''} utm_medium={req.utm_medium or ''} "
                f"utm_campaign={req.utm_campaign or ''}"
            ),
            "page": req.page or "",
            "market": "BR",
        }).execute()
    except Exception as e:
        logger.warning(f"Falha ao salvar lead capturado: {e}")
    return {"ok": True}


@router.get("/sucesso")
async def checkout_success(session_id: str = "", plan: str = ""):
    return {
        "message": "Assinatura realizada com sucesso!",
        "session_id": session_id,
        "plan": plan,
        "next_steps": [
            "Verifique seu email para instrucoes de acesso",
            "Em ate 48h seus agentes estarao ativos",
            "Em caso de duvidas, contate suporte@global-engenharia.com",
        ],
    }
