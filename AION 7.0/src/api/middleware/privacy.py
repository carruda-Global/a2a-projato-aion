from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


PUBLIC_ROUTES = [
    "/api/privacy/policy",
    "/api/privacy/terms",
    "/api/privacy/acceptable-use",
    "/health",
    "/api/auth/login",
    "/api/auth/register",
    "/",
]


class PrivacyConsentMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(route) for route in PUBLIC_ROUTES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(status_code=401, content={"error": "Authentication required"})

        user_id = await self._extract_user_id(auth_header)
        if not user_id:
            return JSONResponse(status_code=401, content={"error": "Invalid token"})

        has_consent = await self._check_consent(user_id)
        if not has_consent:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Privacy consent required",
                    "message": "Voce precisa aceitar a Politica de Privacidade e Termos de Uso",
                    "policy_url": "/api/privacy/policy",
                    "terms_url": "/api/privacy/terms"
                }
            )

        return await call_next(request)

    async def _extract_user_id(self, token: str) -> str:
        return "user_123"

    async def _check_consent(self, user_id: str) -> bool:
        try:
            from src.database.supabase_client import supabase
            result = supabase.table("consents").select("consent_given").eq("user_id", user_id).execute()
            if not result.data:
                return False
            return result.data[0].get("consent_given", False)
        except Exception:
            return True
