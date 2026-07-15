"""Trigger endpoint for the daily personal career-positioning LinkedIn post.
Same pattern as linkedin_content.py's run-daily-job -- meant to be called
once a day by the 24/7 job loop in app/main.py, not self-scheduling."""
import sys
from pathlib import Path

import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.app_utils.marketplace_auth import require_marketplace_admin_secret
from src.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/career-positioning", tags=["career_positioning"])

_WORKERS_LINKEDIN = Path(__file__).resolve().parents[2] / "workers" / "linkedin"


@router.post("/run-daily-job")
async def run_daily_job(request: Request):
    settings = Settings()
    require_marketplace_admin_secret(request, getattr(settings, "marketplace_admin_secret", ""))

    if str(_WORKERS_LINKEDIN) not in sys.path:
        sys.path.insert(0, str(_WORKERS_LINKEDIN))
    from workflows.career_positioning import run_career_positioning_job

    try:
        return await run_career_positioning_job()
    except Exception as e:
        logger.exception("Career positioning post job failed")
        return JSONResponse(status_code=502, content={"error": str(e), "error_type": type(e).__name__})
