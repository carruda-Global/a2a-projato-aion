"""Shared auth helpers for marketplace/subscription-activation endpoints.

These endpoints grant paid access (activate_subscription) and must never be
reachable without proof the request came from the real marketplace platform.
Fail CLOSED: if the expected secret isn't configured, reject the request
instead of skipping verification.
"""

import hashlib
import hmac
import logging

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


def require_marketplace_admin_secret(request: Request, configured_secret: str) -> None:
    """Guard for manual/testing activation helpers (e.g. GET /x/subscribe).

    Requires a shared secret via the `X-Admin-Secret` header (or
    `admin_secret` query param as a fallback) matching MARKETPLACE_ADMIN_SECRET.
    Fails closed if the secret isn't configured.
    """
    if not configured_secret:
        logger.error(
            "MARKETPLACE_ADMIN_SECRET nao configurado — rejeitando chamada "
            "administrativa de ativacao (fail closed)"
        )
        raise HTTPException(status_code=503, detail="Endpoint nao configurado")

    provided = request.headers.get("x-admin-secret") or request.query_params.get("admin_secret", "")
    if not provided or not hmac.compare_digest(provided, configured_secret):
        raise HTTPException(status_code=401, detail="Credencial administrativa invalida")


def verify_hmac_signature(payload: bytes, signature: str, configured_secret: str) -> bool:
    """Generic HMAC-SHA256 webhook signature check. Fails closed."""
    if not configured_secret:
        logger.error("Webhook secret nao configurado — rejeitando webhook (fail closed)")
        return False
    if not signature:
        return False
    expected = hmac.new(configured_secret.encode(), payload, hashlib.sha256).hexdigest()
    candidate = signature.split("=", 1)[-1] if "=" in signature else signature
    return hmac.compare_digest(expected, candidate)


def verify_static_secret_header(provided: str, configured_secret: str) -> bool:
    """Check a static shared-secret header. For platforms (e.g. Pipefy) whose
    webhooks don't compute a signature — they just echo back a custom header
    verbatim, so the only usable check is a constant-time string match.
    Fails closed."""
    if not configured_secret:
        logger.error("Webhook secret nao configurado — rejeitando webhook (fail closed)")
        return False
    if not provided:
        return False
    return hmac.compare_digest(provided, configured_secret)
