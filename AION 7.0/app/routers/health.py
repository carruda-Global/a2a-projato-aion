from fastapi import APIRouter
from src.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    settings = get_settings()
    try:
        from src.api.deepseek_client import DeepSeekClient
        llm = DeepSeekClient(settings)
        llm_ok = llm.health_check()
    except Exception:
        llm_ok = False
    return {
        "status": "healthy" if llm_ok else "degraded",
        "version": "3.0.0",
        "deepseek": "connected" if llm_ok else "disconnected",
        "environment": settings.app_env,
    }
