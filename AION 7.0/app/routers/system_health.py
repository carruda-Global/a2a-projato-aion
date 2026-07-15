"""Trigger endpoint for real system health checks (site, backend, database,
payments, AgentVerse, and -- on the daily/deep run -- a live sample of the
real orchestrator agents). Meant to be called by an external scheduler
(GitHub Actions), same pattern as /api/linkedin-content/run-daily-job."""
import logging

from fastapi import APIRouter, Request

from app.app_utils.marketplace_auth import require_marketplace_admin_secret
from src.agents.system_health_agent import run_health_check
from src.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/system-health", tags=["system_health"])


@router.post("/run-check")
async def run_check(request: Request, deep: bool = False):
    settings = Settings()
    require_marketplace_admin_secret(request, getattr(settings, "marketplace_admin_secret", ""))
    return await run_health_check(deep=deep)
