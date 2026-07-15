import json
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from src.config import get_settings, Settings
from src.database.supabase_client import SupabaseClient
from src.monetization.microsoft_client import MicrosoftMarketplaceClient
from src.monetization.plans import PLANS, get_plan
from src.monetization.subscription_activator import (
    activate_subscription,
    deactivate_subscription,
    get_subscription as get_active_sub,
    get_subscription_by_id,
    update_subscription_plan,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/microsoft", tags=["microsoft"])


class MicrosoftActivationResponse(BaseModel):
    status: str
    subscription_id: str | None = None
    customer_id: str | None = None
    plan: str | None = None
    redirect_url: str | None = None
    message: str | None = None


class MicrosoftWebhookResponse(BaseModel):
    received: bool
    event_type: str | None = None
    subscription_id: str | None = None


class MicrosoftFulfillmentRequest(BaseModel):
    token: str


def _get_settings() -> Settings:
    return get_settings()


async def _validate_microsoft_jwt(request: Request, settings: Settings) -> None:
    tenant_id = settings.microsoft_tenant_id
    client_id = settings.microsoft_client_id

    if not tenant_id or not client_id:
        logger.warning(
            "AZURE_TENANT_ID/AZURE_CLIENT_ID nao configurados — "
            "pulando validacao JWT do webhook Microsoft"
        )
        return

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.warning("Microsoft webhook sem Authorization header")
        raise HTTPException(status_code=401, detail="Authorization header ausente")

    token = auth_header[7:]
    try:
        from jose import jwt
        import httpx as _httpx

        jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        async with _httpx.AsyncClient() as http:
            jwks_resp = await http.get(jwks_url, timeout=10)
        jwks = jwks_resp.json()

        jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=client_id,
            issuer=f"https://sts.windows.net/{tenant_id}/",
        )
    except ImportError:
        logger.warning("python-jose nao instalado; pulando validacao JWT do webhook Microsoft")
    except Exception:
        logger.exception("Microsoft webhook com JWT invalido")
        raise HTTPException(status_code=401, detail="Token Microsoft invalido")


@router.get("/landing")
async def landing_page(token: str = Query(default="")):
    if not token:
        return RedirectResponse(url="https://global-engenharia.com/?ms_error=missing_token")

    settings = get_settings()

    try:
        db = SupabaseClient(settings)
        db.client.table("microsoft_subscriptions").insert({
            "token": token,
            "status": "pending_activation",
            "source": "microsoft_marketplace",
        }).execute()
    except Exception as e:
        logger.warning("Supabase indisponivel no landing: %s", e)

    try:
        client = MicrosoftMarketplaceClient(settings)
        resolved = client.resolve_purchase(token)

        if resolved and resolved.get("subscription_id"):
            subscription_id = resolved["subscription_id"]
            plan_id = resolved.get("plan_id", "compliance_essencial")
            customer_id = resolved["customer_id"]
            customer_email = resolved.get("purchaser_email", "")
            customer_name = resolved.get("customer_name", "")

            activate_subscription(
                source="microsoft",
                external_id=subscription_id,
                customer_id=customer_id,
                plan_id=plan_id,
                customer_email=customer_email,
                customer_name=customer_name,
            )

            client.activate_subscription(subscription_id, plan_id)

            logger.info(
                "Landing page fulfillment: sub=%s customer=%s plan=%s",
                subscription_id, customer_id, plan_id,
            )

            return RedirectResponse(
                url=(
                    f"https://global-engenharia.com/ms-ativacao/"
                    f"?activated=true"
                    f"&plan={plan_id}"
                    f"&email={customer_email}"
                    f"&sub={subscription_id}"
                )
            )
    except Exception as e:
        logger.exception("Erro no fulfillment do landing page: %s", e)

    return RedirectResponse(
        url=f"https://global-engenharia.com/ms-ativacao/?ms_error=activation_failed&token={token}"
    )


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
):
    await _validate_microsoft_jwt(request, settings)

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Microsoft uses "action" in fulfillment webhooks, "eventType" in newer event-based
    action = payload.get("action") or payload.get("eventType", "")
    subscription_id = payload.get("subscriptionId", "")
    logger.info("Microsoft webhook: %s sub=%s", action, subscription_id)

    if action == "Unsubscribe":
        background_tasks.add_task(deactivate_subscription, "microsoft", subscription_id)

    elif action == "ChangePlan":
        new_plan_id = payload.get("planId", "")
        background_tasks.add_task(
            update_subscription_plan, "microsoft", subscription_id, new_plan_id
        )

    elif action == "Suspend":
        background_tasks.add_task(_handle_suspend, subscription_id)

    elif action == "Reinstate":
        background_tasks.add_task(_handle_reinstate, subscription_id)

    elif action == "Subscribed":
        plan_id = payload.get("planId", "")
        purchaser = payload.get("purchaser", {})
        background_tasks.add_task(
            activate_subscription,
            source="microsoft",
            external_id=subscription_id,
            customer_id=purchaser.get("objectId", subscription_id),
            plan_id=plan_id,
            customer_email=purchaser.get("emailId", ""),
            customer_name=payload.get("subscriberName", ""),
        )

    return MicrosoftWebhookResponse(
        received=True,
        event_type=action,
        subscription_id=subscription_id,
    )


def _handle_suspend(subscription_id: str) -> None:
    from src.monetization.subscription_activator import _active_subscriptions, _init_supabase
    sub_id = f"microsoft_{subscription_id}"
    if sub_id in _active_subscriptions:
        _active_subscriptions[sub_id]["status"] = "suspended"
    try:
        db = _init_supabase()
        if db:
            db.table("subscriptions").update({"status": "suspended"}).eq("id", sub_id).execute()
    except Exception as e:
        logger.warning("Falha ao suspender subscription %s: %s", subscription_id, e)
    logger.info("Subscription suspensa: %s", sub_id)


def _handle_reinstate(subscription_id: str) -> None:
    from src.monetization.subscription_activator import _active_subscriptions, _init_supabase
    sub_id = f"microsoft_{subscription_id}"
    if sub_id in _active_subscriptions:
        _active_subscriptions[sub_id]["status"] = "active"
    try:
        db = _init_supabase()
        if db:
            db.table("subscriptions").update({"status": "active"}).eq("id", sub_id).execute()
    except Exception as e:
        logger.warning("Falha ao reativar subscription %s: %s", subscription_id, e)
    logger.info("Subscription reativada: %s", sub_id)


@router.post("/fulfill")
async def fulfill_subscription(payload: MicrosoftFulfillmentRequest):
    if not payload.token:
        raise HTTPException(status_code=400, detail="token é obrigatório")

    settings = _get_settings()
    client = MicrosoftMarketplaceClient(settings)

    try:
        resolved = client.resolve_purchase(payload.token)
    except Exception as e:
        logger.exception("resolve_purchase failed: token=%s", payload.token[:20])
        raise HTTPException(status_code=502, detail=f"Falha ao resolver token Azure: {e}")

    if not resolved:
        raise HTTPException(
            status_code=502, detail="Token Azure resolvido mas sem dados de subscription"
        )

    subscription_id = resolved["subscription_id"]
    plan_id = resolved.get("plan_id", "compliance_essencial")
    customer_id = resolved["customer_id"]
    customer_email = resolved.get("purchaser_email", "")
    customer_name = resolved.get("customer_name", "Microsoft Customer")

    activate_subscription(
        source="microsoft",
        external_id=subscription_id,
        customer_id=customer_id,
        plan_id=plan_id,
        customer_email=customer_email,
        customer_name=customer_name,
    )

    activated = client.activate_subscription(subscription_id, plan_id)

    logger.info(
        "Fulfillment Azure: sub=%s customer=%s plan=%s activated=%s",
        subscription_id, customer_id, plan_id, activated,
    )

    return {
        "subscriptionId": subscription_id,
        "planId": plan_id,
        "customerId": customer_id,
        "customerName": customer_name,
        "saasSubscriptionStatus": "Subscribed" if activated else "PendingFulfillmentStart",
        "status": "fulfilled" if activated else "pending",
    }


@router.get("/subscribe")
async def subscribe(
    token: str = Query(default="", alias="token"),
    plan: str = Query(default="compliance_essencial"),
):
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Token Azure Marketplace nao fornecido. Faca subscribe via Azure Marketplace.",
        )

    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    settings = _get_settings()
    client = MicrosoftMarketplaceClient(settings)

    try:
        resolved = client.resolve_purchase(token)
    except Exception:
        resolved = None

    if not resolved:
        raise HTTPException(
            status_code=400,
            detail="Falha ao validar token Azure Marketplace. Token invalido ou expirado.",
        )

    subscription_id = resolved["subscription_id"]
    customer_id = resolved["customer_id"]
    customer_email = resolved.get("purchaser_email", "")
    customer_name = resolved.get("customer_name", "")

    activate_subscription(
        source="microsoft",
        external_id=subscription_id,
        customer_id=customer_id,
        plan_id=plan,
        customer_email=customer_email,
        customer_name=customer_name,
    )

    activated = client.activate_subscription(subscription_id, plan)

    logger.info(
        "Microsoft subscribe: customer=%s plan=%s sub=%s activated=%s",
        customer_id, plan, subscription_id, activated,
    )

    redirect_url = (
        f"{settings.base_url}/dashboard?"
        f"subscription_id={subscription_id}&source=microsoft"
    )

    return MicrosoftActivationResponse(
        status="active" if activated else "pending_activation",
        subscription_id=subscription_id,
        customer_id=customer_id,
        plan=plan,
        redirect_url=redirect_url,
        message="Assinatura ativada com sucesso!" if activated else "Assinatura pendente de ativacao.",
    )


@router.get("/subscription/{subscription_id}")
async def get_subscription(subscription_id: str):
    sub = get_active_sub("microsoft", subscription_id)
    if not sub:
        sub = get_subscription_by_id(subscription_id)
    if not sub:
        settings = _get_settings()
        client = MicrosoftMarketplaceClient(settings)
        remote = client.get_subscription(subscription_id)
        if remote:
            return remote
        raise HTTPException(status_code=404, detail="Assinatura nao encontrada")
    return sub


@router.get("/plans")
async def list_plans():
    return {
        "plans": [
            {
                "id": p["id"],
                "name": p["name"],
                "price_usd": f"${p['price'] / 550:,.2f}",
                "agents": p["agents"],
                "features": p["features"],
            }
            for p in PLANS
        ]
    }
