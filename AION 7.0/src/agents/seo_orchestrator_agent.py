"""Unified status view over the SEO subsystems built 2026-07-16: combinatorial
page generation (seo_content_agent), backlink/directory outreach
(directory_submission_agent), and GSC performance feedback (seo_feedback_agent).
Ties them together as one checkable "SEO Agent" instead of separate silent crons."""
import os
import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/seo/agent", tags=["seo_orchestrator"])


@router.get("/status")
async def seo_agent_status():
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not (supa_url and supa_key):
        return {"error": "Supabase not configured"}
    headers = {"apikey": supa_key, "Authorization": "Bearer " + supa_key}

    async with httpx.AsyncClient(timeout=15) as client:
        pages_by_market = {}
        for market in ("US", "UK", "CA", "AU"):
            r = await client.get(
                supa_url + f"/rest/v1/seo_pages?market=eq.{market}&product=eq.voice_receptionist&select=slug",
                headers={**headers, "Prefer": "count=exact"},
            )
            pages_by_market[market] = int(r.headers.get("content-range", "0/0").split("/")[-1])

        legacy_r = await client.get(
            supa_url + "/rest/v1/seo_pages?product=is.null&select=slug",
            headers={**headers, "Prefer": "count=exact"},
        )
        legacy_stale_pages = int(legacy_r.headers.get("content-range", "0/0").split("/")[-1])

        dirs_r = await client.get(
            supa_url + "/rest/v1/sdr_growth_log?channel=eq.directory&select=item_key,last_sent_at&order=last_sent_at.desc&limit=10",
            headers=headers,
        )
        recent_directory_sends = dirs_r.json() if dirs_r.status_code == 200 else []

    return {
        "combinatorial_pages": {"by_market": pages_by_market, "total": sum(pages_by_market.values())},
        "legacy_stale_pages_pending_cleanup": legacy_stale_pages,
        "recent_directory_outreach": recent_directory_sends,
        "cron_schedule": {
            "seo_page_generation": "every 6h, all 4 markets",
            "directory_outreach": "every 24h, 10 per run",
            "gsc_feedback": "every 7d (requires GSC_* env vars)",
        },
        "sitemap_url": "https://global-engenharia.com/sitemap.xml",
    }
