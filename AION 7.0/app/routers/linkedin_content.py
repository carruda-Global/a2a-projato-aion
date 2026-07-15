"""Trigger endpoint for the daily LinkedIn content job (1 text post).
Meant to be called once a day by an external scheduler (Render Cron Job or
GitHub Actions scheduled workflow) — this process does not self-schedule."""
import sys
from pathlib import Path

import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.app_utils.marketplace_auth import require_marketplace_admin_secret
from src.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/linkedin-content", tags=["linkedin_content"])

_WORKERS_LINKEDIN = Path(__file__).resolve().parents[2] / "workers" / "linkedin"


@router.post("/run-daily-job")
async def run_daily_job(request: Request):
    settings = Settings()
    require_marketplace_admin_secret(request, getattr(settings, "marketplace_admin_secret", ""))

    if str(_WORKERS_LINKEDIN) not in sys.path:
        sys.path.insert(0, str(_WORKERS_LINKEDIN))
    from workflows.daily_job import run_daily_content_job

    try:
        return await run_daily_content_job()
    except Exception as e:
        logger.exception("LinkedIn daily content job failed")
        return JSONResponse(status_code=502, content={"error": str(e), "error_type": type(e).__name__})
