"""LinkedIn content scheduling for the AI Voice Receptionist product.

Reddit posting used to live here too, but it duplicated (and diverged
from) src/agents/directory_submission_agent.py's Reddit poster -- that one
already handles Reddit properly (per-subreddit unique content, required by
Reddit's Responsible Builder Policy against posting identical content
across subreddits). Running both would have double-posted stale
compliance-product content to the wrong subreddits under a different env
var name (REDDIT_SECRET vs REDDIT_CLIENT_SECRET), so it was removed here
rather than fixed in two places.
"""
import os
import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from fastapi import APIRouter
router = APIRouter(prefix="/api/social-auto", tags=["social_auto"])

LINKEDIN_POSTS = [
    "Small businesses lose real revenue to missed calls -- every single day.\n\n"
    "97% of small businesses using an AI voice agent reported an increase in revenue.\n\n"
    "AION Voice Receptionist answers your business phone 24/7, texts back missed calls "
    "instantly, and captures every lead as a message.\n\n"
    "$89/mo flat. No per-call fees. Live in under 20 minutes.\n\n"
    "#SmallBusiness #AIVoiceAgent #CustomerService",

    "Most AI receptionists charge per call ($1.60-1.90/call) or cap how many unique "
    "customers you can serve per month.\n\n"
    "We built AION Voice Receptionist to avoid both: flat $89/mo, 300 minutes included, "
    "no customer cap.\n\n"
    "There's a live demo line you can call right now, no signup needed.\n\n"
    "#AI #VoiceAI #SaaS",

    "The AI voice agent market is growing from $2.4B in 2024 to a projected $47.5B by "
    "2034 (34.8% CAGR).\n\n"
    "For a dental clinic, law firm, or salon, that growth shows up as one simple fact: "
    "every missed call is a customer calling your competitor next.\n\n"
    "AION Voice Receptionist answers every call, 24/7, so that stops being a risk.\n\n"
    "#VoiceAI #SmallBusiness #Growth",

    "Just shipped: multi-location support for AION Voice Receptionist.\n\n"
    "Our Growth plan now covers up to 2 phone lines -- one per location -- each with "
    "its own personalized AI receptionist trained on that location's hours and details.\n\n"
    "$179/mo, 750 minutes included.\n\n"
    "#ProductUpdate #AI #SmallBusiness",

    "Self-service setup, start to finish: enter your business name, we pull your hours "
    "from your Google Business Profile automatically, your dedicated AI receptionist "
    "phone number goes live in under 20 minutes.\n\n"
    "No developer, no sales call, no onboarding meeting.\n\n"
    "#AI #Automation #SmallBusiness",
]


async def auto_job_linkedin_content():
    """Every 24h: prepares today's LinkedIn post and pushes it to a Zapier
    webhook if one is configured (ZAPIER_LINKEDIN_WEBHOOK) -- otherwise it's
    just logged for manual posting."""
    idx = (datetime.now(timezone.utc).timetuple().tm_yday) % len(LINKEDIN_POSTS)
    post = LINKEDIN_POSTS[idx]
    logger.info("[CRON] LinkedIn content ready:\n%s", post)
    zapier_hook = os.getenv("ZAPIER_LINKEDIN_WEBHOOK", "")
    if not zapier_hook:
        return
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            await client.post(zapier_hook, json={"post": post, "platform": "linkedin"})
            logger.info("[CRON] LinkedIn post sent to Zapier webhook")
    except Exception as e:
        logger.error("[CRON] LinkedIn job error: %s", e)


@router.get("/linkedin-today")
async def get_linkedin_post():
    """Returns today's LinkedIn post -- can be wired to Buffer/Zapier."""
    idx = (datetime.now(timezone.utc).timetuple().tm_yday) % len(LINKEDIN_POSTS)
    return {"post": LINKEDIN_POSTS[idx], "platform": "linkedin", "char_count": len(LINKEDIN_POSTS[idx])}
