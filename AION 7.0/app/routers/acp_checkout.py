from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from src.config import Settings

router = APIRouter()
settings = Settings()


class ACPCheckoutRequest(BaseModel):
    acp_version: str = "1.0.0"
    product_id: str
    buyer_id: Optional[str] = None
    callback_url: Optional[str] = None


class ACPCheckoutResponse(BaseModel):
    acp_version: str
    checkout_id: str
    status: str
    redirect_url: Optional[str] = None
    payment_methods: list[str] = ["card", "stripe"]


class ACPFulfillmentRequest(BaseModel):
    checkout_id: str
    payment_intent_id: str
    status: str


PRODUCTS = {
    "spec-analyst": {"name": "Analisador de Especificações Técnicas", "price_cents": 99700, "currency": "BRL"},
    "procurement": {"name": "Processador de Ordens de Compra", "price_cents": 159700, "currency": "BRL"},
    "inventory": {"name": "Gestor de Estoque de Obra", "price_cents": 159700, "currency": "BRL"},
    "logistics": {"name": "Rastreador Logístico", "price_cents": 299700, "currency": "BRL"},
    "field-execution": {"name": "Gerador de Instruções", "price_cents": 350000, "currency": "BRL"},
    "full-suite": {"name": "Full Suite (5 agentes)", "price_cents": 350000, "currency": "BRL"},
}


@router.post("/checkout")
async def acp_checkout(req: ACPCheckoutRequest, x_acp_key: Optional[str] = Header(None)):
    if not settings.stripe_secret_key and not x_acp_key:
        raise HTTPException(status_code=401, detail="ACP authentication required")

    product = PRODUCTS.get(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Produto {req.product_id} não encontrado")

    from src.monetization.stripe_client import StripeClient

    stripe_client = StripeClient(settings)
    success_url = req.callback_url or "https://engenheiro-producao-ai.onrender.com/api/v1/acp/success"
    cancel_url = "https://engenheiro-producao-ai.onrender.com/api/v1/acp/cancel"

    checkout_url = stripe_client.create_checkout_session(
        plan_id=req.product_id,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    if not checkout_url:
        raise HTTPException(status_code=400, detail="Falha ao criar sessão de checkout")

    import uuid
    checkout_id = f"acp_{uuid.uuid4().hex[:12]}"

    return ACPCheckoutResponse(
        acp_version="1.0.0",
        checkout_id=checkout_id,
        status="redirect",
        redirect_url=checkout_url,
        payment_methods=["card", "stripe"],
    )


@router.get("/products")
async def acp_products():
    return {
        "acp_version": "1.0.0",
        "merchant": {
            "name": "Projato Engenharia",
            "website": "https://engenheiro-producao-ai.onrender.com",
        },
        "products": [
            {
                "id": pid,
                "name": info["name"],
                "price": {"amount": info["price_cents"], "currency": info["currency"]},
            }
            for pid, info in PRODUCTS.items()
        ],
    }


@router.post("/fulfill")
async def acp_fulfill(req: ACPFulfillmentRequest):
    if req.status == "completed":
        print(f"[ACP] Fulfilling order {req.checkout_id} (PI: {req.payment_intent_id})")
    return {"status": "fulfilled", "checkout_id": req.checkout_id}


@router.get("/success")
async def acp_success():
    return {"status": "success", "message": "Pagamento confirmado! Seu agente já está liberado."}


@router.get("/cancel")
async def acp_cancel():
    return {"status": "cancelled", "message": "Pagamento cancelado."}
