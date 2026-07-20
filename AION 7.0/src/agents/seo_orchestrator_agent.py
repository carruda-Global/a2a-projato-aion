"""Unified status view over the SEO subsystems built 2026-07-16: combinatorial
page generation (seo_content_agent), backlink/directory outreach
(directory_submission_agent), and GSC performance feedback (seo_feedback_agent).
Ties them together as one checkable "SEO Agent" instead of separate silent crons."""
import os
from datetime import datetime, timezone
import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/seo/agent", tags=["seo_orchestrator"])


INDEXNOW_KEY = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"
INDEXNOW_URLS = [
    "https://global-engenharia.com/", "https://global-engenharia.com/vendas.html",
    "https://global-engenharia.com/blog", "https://global-engenharia.com/ai-receptionist-guide.html",
    "https://global-engenharia.com/blog/ai-receptionist-for-small-business-guide",
    "https://global-engenharia.com/blog/ai-receptionist-cost-2026",
    "https://global-engenharia.com/blog/signs-your-business-needs-ai-receptionist",
    "https://global-engenharia.com/blog/ai-receptionist-faq",
    "https://global-engenharia.com/blog/ai-receptionist-vs-voicemail",
    "https://global-engenharia.com/blog/ai-receptionist-data-security",
    "https://global-engenharia.com/blog/what-industries-use-ai-receptionists",
    "https://global-engenharia.com/how-to-choose-ai-receptionist.html",
    "https://global-engenharia.com/real-cost-of-a-missed-call.html",
    "https://global-engenharia.com/aion-vs-smith-ai.html", "https://global-engenharia.com/aion-vs-goodcall.html",
    "https://global-engenharia.com/aion-vs-retell-ai.html", "https://global-engenharia.com/aion-vs-synthflow.html",
    "https://global-engenharia.com/ai-receptionist-for-dental-clinics.html",
    "https://global-engenharia.com/ai-receptionist-for-real-estate.html",
    "https://global-engenharia.com/ai-receptionist-for-home-services.html",
]


BLOG_URLS = [u for u in INDEXNOW_URLS if "/blog" in u]


async def _log_indexnow_run(status_code: int) -> None:
    """Persist a timestamp for the last IndexNow batch so /status can report
    it -- before this, the cron ran every 6h but left no record anywhere,
    making it indistinguishable from silently having stopped."""
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not (supa_url and supa_key):
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                supa_url + "/rest/v1/sdr_growth_log",
                json={
                    "channel": "indexnow",
                    "item_key": f"batch-status-{status_code}",
                    "last_sent_at": datetime.now(timezone.utc).isoformat(),
                },
                headers={
                    "apikey": supa_key, "Authorization": "Bearer " + supa_key,
                    "Prefer": "resolution=merge-duplicates",
                },
            )
    except Exception:
        pass


async def auto_job_indexnow():
    """Called by the JOBS loop. IndexNow's public API rate-limits by source
    IP independent of our own key/quota, so a submission can 429 for reasons
    outside our control -- retrying on the normal cron cadence instead of
    blocking on a single attempt."""
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://api.indexnow.org/indexnow",
                json={
                    "host": "global-engenharia.com",
                    "key": INDEXNOW_KEY,
                    "keyLocation": f"https://global-engenharia.com/{INDEXNOW_KEY}.txt",
                    "urlList": INDEXNOW_URLS,
                },
            )
        await _log_indexnow_run(r.status_code)
        return {"status_code": r.status_code, "body": r.text[:200]}
    except Exception as e:
        return {"error": str(e)}


@router.post("/indexnow-now")
async def indexnow_now():
    return await auto_job_indexnow()


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

        # product=is.null caught rows the generator never tagged, but rows
        # from the pre-pivot catalog (RFI automation, PO reconciliation,
        # spend analysis, etc) DO have a product value -- just not
        # "voice_receptionist" -- so they were invisible to this count while
        # still being served live at /artigos/{slug} and diluting search
        # relevance for the current product (confirmed 2026-07-19 via real
        # GSC clicks landing on us-rfi-creation-automation-*, us-po-
        # reconciliation-*, us-spend-analysis-* pages). Broadened to catch both.
        legacy_r = await client.get(
            supa_url + "/rest/v1/seo_pages?or=(product.is.null,product.neq.voice_receptionist)"
            "&topic_kind=not.in.(guide,comparison)&select=slug",
            headers={**headers, "Prefer": "count=exact"},
        )
        legacy_stale_pages = int(legacy_r.headers.get("content-range", "0/0").split("/")[-1])

        dirs_r = await client.get(
            supa_url + "/rest/v1/sdr_growth_log?channel=eq.directory&select=item_key,last_sent_at&order=last_sent_at.desc&limit=10",
            headers=headers,
        )
        recent_directory_sends = dirs_r.json() if dirs_r.status_code == 200 else []

        indexnow_r = await client.get(
            supa_url + "/rest/v1/sdr_growth_log?channel=eq.indexnow&select=item_key,last_sent_at&order=last_sent_at.desc&limit=1",
            headers=headers,
        )
        indexnow_last = indexnow_r.json() if indexnow_r.status_code == 200 else []

        # Real per-run production report from the force=True migration cron
        # (2026-07-20) -- lets progress be checked here instead of
        # re-invoking an external agent just to ask "how far along is it".
        migration_r = await client.get(
            supa_url + "/rest/v1/sdr_growth_log?channel=eq.seo_migration_report&select=item_key,last_sent_at,notes&order=last_sent_at.desc&limit=1",
            headers=headers,
        )
        migration_rows = migration_r.json() if migration_r.status_code == 200 else []
        last_migration_report = migration_rows[0] if migration_rows else None

        blog_health = {}
        for url in BLOG_URLS:
            try:
                br = await client.head(url, timeout=10, follow_redirects=True)
                blog_health[url] = br.status_code
            except Exception as e:
                blog_health[url] = f"error: {e}"

    return {
        "combinatorial_pages": {"by_market": pages_by_market, "total": sum(pages_by_market.values())},
        "legacy_stale_pages_pending_cleanup": legacy_stale_pages,
        "recent_directory_outreach": recent_directory_sends,
        "blog": {
            "pages_checked": len(BLOG_URLS),
            "status_by_url": blog_health,
            "all_live": all(v == 200 for v in blog_health.values()),
        },
        "indexnow": {
            "last_run": indexnow_last[0] if indexnow_last else None,
            "urls_per_batch": len(INDEXNOW_URLS),
            "note": "IndexNow pushes to Bing/Yandex directly, but there is no automated read of Bing's own index count -- that requires a Bing Webmaster API key (not configured). Check bing.com/webmasters manually for indexed-page counts.",
        },
        "seo_migration_report": {
            "last_run": last_migration_report,
            "note": "Real per-market generated/skipped counts from the last force=True premium-template migration cron run. Requires the sdr_growth_log.notes column migration -- if last_run is null despite the cron having run, that migration probably hasn't been applied in Supabase yet.",
        },
        "cron_schedule": {
            "seo_page_generation": "every 3h, all 4 markets, force=True (premium-template migration in progress as of 2026-07-20)",
            "directory_outreach": "every 24h, 10 per run",
            "indexnow": "every 6h",
            "gsc_feedback": "every 7d (requires GSC_* env vars)",
        },
        "sitemap_url": "https://global-engenharia.com/sitemap.xml",
    }


@router.post("/cleanup-legacy")
async def cleanup_legacy_pages():
    """Unpublishes (not deletes -- reversible) every seo_pages row whose
    product isn't voice_receptionist: pre-pivot catalog leftovers (RFI
    automation, PO reconciliation, spend analysis, etc) still being served
    live at /artigos/{slug} alongside the current product, diluting search
    relevance (confirmed 2026-07-19: real GSC clicks landing on these)."""
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not (supa_url and supa_key):
        return {"error": "Supabase not configured"}
    headers = {"apikey": supa_key, "Authorization": "Bearer " + supa_key, "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30) as client:
        # Excludes topic_kind guide/comparison explicitly -- those are the
        # hand-written aion-vs-retell-ai/aion-vs-synthflow pages; whatever
        # their product field happens to be, they must never be swept up here.
        legacy_filter = "or=(product.is.null,product.neq.voice_receptionist)&topic_kind=not.in.(guide,comparison)"
        before = await client.get(
            supa_url + f"/rest/v1/seo_pages?{legacy_filter}&select=slug",
            headers={**headers, "Prefer": "count=exact"},
        )
        count = int(before.headers.get("content-range", "0/0").split("/")[-1])

        resp = await client.patch(
            supa_url + f"/rest/v1/seo_pages?{legacy_filter}",
            headers={**headers, "Prefer": "return=minimal"},
            json={"published": False},
        )
        return {
            "matched": count,
            "status_code": resp.status_code,
            "note": "Rows unpublished, not deleted -- get_seo_page() should treat published=false as 404. Re-run GET /api/seo/agent/status afterward to confirm legacy_stale_pages_pending_cleanup drops to 0.",
        }


@router.post("/gsc-feedback-now")
async def run_gsc_feedback_now():
    """Manual trigger for the weekly GSC feedback pull (2026-07-20), so the
    freshly-authorized GSC_CLIENT_ID/SECRET/REFRESH_TOKEN can be verified
    immediately instead of waiting up to 7 days for the cron."""
    from src.agents.seo_feedback_agent import SEOFeedbackAgent
    from src.config import Settings

    feedback = SEOFeedbackAgent(Settings())
    if not feedback.is_configured():
        return {"configured": False, "error": "GSC_CLIENT_ID/SECRET/REFRESH_TOKEN not set or invalid"}
    import asyncio
    result = await asyncio.to_thread(feedback.pull_and_store)
    return {"configured": True, "result": result}
