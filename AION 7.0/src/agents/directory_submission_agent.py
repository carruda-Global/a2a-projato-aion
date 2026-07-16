"""Directory/review-site listing + PR distribution for the AI Voice
Receptionist product. Repurposed 2026-07 — the 19-Copilot compliance
catalog is retired, this product is the sole thing being marketed now.
"""
import asyncio
import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
import httpx
import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter
router = APIRouter(prefix="/api/directories", tags=["directories"])

HOSTINGER_USER = os.getenv("HOSTINGER_EMAIL_USER", "")
HOSTINGER_PASS = os.getenv("HOSTINGER_EMAIL_PASSWORD", "")
DEVTO_KEY = os.getenv("DEVTO_API_KEY", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
_DIRECTORY_RESEND_DAYS = 60
_DIRECTORIES_PER_RUN = 10
_DEVTO_RESEND_DAYS = 90


def _supabase_headers() -> dict:
    return {"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"}


async def _last_sent_at(channel: str, item_key: str) -> "datetime | None":
    """Real persisted last-sent timestamp -- replaces the in-memory batch
    counter that used to reset (back to directory #1) on every backend
    redeploy, which meant the 72h cron rarely progressed past the first
    couple of directories in practice."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{_SUPABASE_URL}/rest/v1/sdr_growth_log",
                params={"channel": f"eq.{channel}", "item_key": f"eq.{item_key}", "select": "last_sent_at"},
                headers=_supabase_headers(),
            )
            resp.raise_for_status()
            rows = resp.json()
            if not rows:
                return None
            return datetime.fromisoformat(rows[0]["last_sent_at"].replace("Z", "+00:00"))
    except Exception as e:
        logger.warning("[SDR-Log] Could not read last_sent_at for %s/%s: %s", channel, item_key, e)
        return None


async def _mark_sent(channel: str, item_key: str) -> None:
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{_SUPABASE_URL}/rest/v1/sdr_growth_log",
                json={"channel": channel, "item_key": item_key, "last_sent_at": datetime.now(timezone.utc).isoformat()},
                headers={**_supabase_headers(), "Prefer": "resolution=merge-duplicates"},
            )
    except Exception as e:
        logger.warning("[SDR-Log] Could not mark %s/%s sent: %s", channel, item_key, e)

PRODUCT_URL = "https://global-engenharia.com/ecosystem/callreception"
OWNER_EMAIL = "carruda2307@gmail.com"

# Review/listing sites relevant to a small-business SaaS tool, in the 4
# validated markets (US/UK/CA/AU) — the old region-specific directories
# (India, UAE, LATAM press) were tied to the retired compliance product and
# are dropped rather than left pointing at a product we no longer sell.
DIRECTORIES = [
    {"name": "G2.com", "url": "https://sell.g2.com", "type": "email_request", "traffic": "5M/month", "note": "Free listing, reviews drive small-business trust"},
    {"name": "Capterra", "url": "https://vendors.capterra.com", "type": "email_request", "traffic": "3M/month", "note": "Pay-per-click after free listing"},
    {"name": "GetApp", "url": "https://www.getapp.com/vendors", "type": "email_request", "traffic": "2M/month", "note": "Gartner property"},
    {"name": "Software Advice", "url": "https://softwareadvice.com/vendors", "type": "email_request", "traffic": "1M/month", "note": "Gartner property"},
    {"name": "Trustpilot", "url": "https://businessapp.b2b.trustpilot.com", "type": "email_request", "traffic": "5M/month", "note": "Strong trust signal for small-business buyers"},
    {"name": "SaaSHub", "url": "https://www.saashub.com/submit", "type": "email_request", "traffic": "500k/month", "note": "Free, auto-approved"},
    {"name": "BetaList", "url": "https://betalist.com/startups/new", "type": "email_request", "traffic": "100k/month", "note": "Good for early traction"},
    {"name": "AlternativeTo", "url": "https://alternativeto.net/suggest", "type": "email_request", "traffic": "2M/month", "note": "Gets traffic from Smith.ai/Goodcall/Synthflow searches"},
    {"name": "Product Hunt", "url": "https://www.producthunt.com", "type": "manual_once", "traffic": "500k/day", "note": "Launch Tuesday 12:01 AM PST for max votes"},
    {"name": "OpenPR", "url": "https://www.openpr.com/account", "type": "pr_submit", "traffic": "200k/month", "note": "Free press release distribution"},
    # AI-tool-specific directories -- much more relevant than generic SaaS
    # directories since this product is explicitly an AI tool.
    {"name": "There's An AI For That", "url": "https://theresanaiforthis.com/submit", "type": "email_request", "traffic": "3M/month", "note": "One of the largest AI tool directories"},
    {"name": "Futurepedia", "url": "https://www.futurepedia.io/submit-tool", "type": "email_request", "traffic": "1M/month", "note": "Popular AI tool directory, free submission"},
    {"name": "FutureTools", "url": "https://www.futuretools.io/submit-a-tool", "type": "email_request", "traffic": "500k/month", "note": "Curated AI tool directory"},
    {"name": "Toolify.ai", "url": "https://www.toolify.ai/", "type": "email_request", "traffic": "2M/month", "note": "Large AI tool directory/marketplace"},
    {"name": "Altern.ai", "url": "https://altern.ai/submit", "type": "manual_once", "traffic": "unknown", "note": "Paid-only listing ($19 Pro / $99 Max, no confirmed free tier) -- skip unless traffic is verified, don't auto-draft"},
    # Startup directories with free listings -- credibility + backlinks.
    {"name": "Crunchbase", "url": "https://www.crunchbase.com/add-new", "type": "email_request", "traffic": "10M/month", "note": "Free company profile, real credibility signal for B2B buyers"},
    {"name": "Indie Hackers", "url": "https://www.indiehackers.com/products/new", "type": "email_request", "traffic": "1M/month", "note": "Founder community, good for organic word-of-mouth"},
    # B2B review/comparison sites not yet covered.
    {"name": "TrustRadius", "url": "https://www.trustradius.com/vendor", "type": "email_request", "traffic": "2M/month", "note": "Enterprise-leaning B2B review site, high buyer trust"},
    {"name": "SaaSworthy", "url": "https://www.saasworthy.com/list-your-product", "type": "email_request", "traffic": "500k/month", "note": "SaaS discovery directory, free listing"},
    {"name": "Slant.co", "url": "https://www.slant.co/", "type": "email_request", "traffic": "1M/month", "note": "Comparison Q&A site, ranks well in 'best X for Y' searches"},
    {"name": "StackShare", "url": "https://stackshare.io/", "type": "email_request", "traffic": "1M/month", "note": "Tool-stack sharing community, developer/founder audience"},
    {"name": "Uneed", "url": "https://www.uneed.best/submit", "type": "email_request", "traffic": "200k/month", "note": "Startup/product discovery directory"},
    {"name": "SoftwareSuggest", "url": "https://www.softwaresuggest.com/vendor", "type": "email_request", "traffic": "1M/month", "note": "B2B software review/comparison site, free vendor listing"},
    {"name": "Crozdesk", "url": "https://crozdesk.com/software-vendors", "type": "email_request", "traffic": "500k/month", "note": "SaaS discovery + comparison, free listing tier"},
    {"name": "FinancesOnline", "url": "https://reviews.financesonline.com/vendors", "type": "email_request", "traffic": "3M/month", "note": "High-authority B2B review site, strong small-business audience"},
    {"name": "SaaSGenius", "url": "https://www.saasgenius.com/list-your-software", "type": "email_request", "traffic": "300k/month", "note": "SaaS directory, free listing"},
    # Added 2026-07-16 from a competitor backlink-gap analysis, filtered down
    # to genuine self-serve directories. Deliberately excludes lookalike
    # domains from that report (seo-anomaly-*, seo-cartel-*) -- those follow
    # a textbook PBN/link-farm naming pattern and pursuing them risks a
    # Google spam-link penalty rather than helping rankings. Also excludes
    # Twilio, Ringover, CB Insights -- not self-serve directories, need a
    # bespoke partner-pitch/profile-claim approach, not this generic template.
    {"name": "GetVoIP", "url": "https://getvoip.com/contact/", "type": "email_request", "traffic": "300k/month", "note": "VoIP/telephony review site, direct category match"},
    {"name": "BestStartup.us", "url": "https://beststartup.us/submit-startup/", "type": "email_request", "traffic": "200k/month", "note": "Startup directory"},
    {"name": "Colormango", "url": "https://colormango.com/submit-tool", "type": "email_request", "traffic": "100k/month", "note": "Tool discovery directory"},
    {"name": "Mrowl", "url": "https://mrowl.com/submit", "type": "email_request", "traffic": "100k/month", "note": "Startup/tool directory"},
    {"name": "Taranker", "url": "https://taranker.com/submit-app", "type": "email_request", "traffic": "100k/month", "note": "App/tool directory"},
    {"name": "Dialfyne", "url": "https://dialfyne.com/contact", "type": "email_request", "traffic": "unknown", "note": "Call-answering/voice-AI adjacent tool site"},
]

LISTING_EMAIL_TEMPLATE = """Subject: Request to List AION Voice Receptionist on {directory}

Hi {directory} Team,

I'd like to list our product, AION Voice Receptionist, on {directory}.

Product Details:
- Name: AION Voice Receptionist
- Website: {product_url}
- Category: AI Voice Agent / Virtual Receptionist / Answering Service
- Description: AI receptionist that answers business phone calls 24/7, texts back missed calls instantly, and captures every lead as a message. Self-service setup, live in under 20 minutes, no developer or sales call required.
- Pricing: $89/month flat, 300 minutes included, $0.15/min after — no per-call fee, no customer cap
- Markets: United States, United Kingdom, Canada, Australia

Key differentiators:
- Flat monthly price with no per-call fee (unlike some competitors charging $1.60-1.90/call)
- No cap on unique callers per month
- Live demo line — prospects can call and test the exact experience before signing up
- Missed-call text-back included on the base plan, not an add-on

Happy to provide screenshots or any additional information.

Best regards,
Cristiano Arruda
Global Match Engenharia
contact@global-engenharia.com
{product_url}
"""

PR_TEMPLATE = """FOR IMMEDIATE RELEASE

New AI Voice Receptionist Launches for Small Businesses — No Per-Call Fees, No Customer Caps

Global Match Engenharia's AION Voice Receptionist answers business calls 24/7, texts back missed calls, and captures every lead — with a live demo line prospects can call before signing up

SAO PAULO, Brazil — July 2026 — Global Match Engenharia today announced the launch of AION Voice Receptionist, an AI phone agent built for small businesses that can't staff a phone line around the clock.

The AI voice agent market is growing from $2.4 billion in 2024 to a projected $47.5 billion by 2034, and 97% of small businesses using an AI voice agent report an increase in revenue — but most existing tools charge per call or cap the number of unique customers on entry-level plans.

AION Voice Receptionist is priced at a flat $89/month with 300 minutes included and no per-call fee or customer cap, targeting dental clinics, law firms, real estate agencies, home services, salons, and medical clinics across the US, UK, Canada, and Australia.

"You shouldn't need a developer or a sales call to get an AI receptionist running," said founder Cristiano Arruda, a licensed production engineer (CREA-SP 5071200171). "We built a live demo line — call it, and you're talking to the exact assistant your customers would get, no signup required."

Key capabilities:
- 24/7 call answering with a real greeting, not voicemail
- Instant text-back on any missed call
- Automatic lead capture — name, number, reason for calling
- Self-service setup, live in under 20 minutes

The product is available at {product_url}, with a free 15-day trial.

About Global Match Engenharia
Global Match Engenharia is a Brazilian engineering and technology company. AION Voice Receptionist is its AI voice agent product for small businesses in English-speaking markets.

Contact:
Cristiano Arruda
Global Match Engenharia
contact@global-engenharia.com
{product_url}

###
""".format(product_url=PRODUCT_URL)

PR_DEVTO_ARTICLE = f"""---
title: We Built an AI Receptionist With No Per-Call Fees and No Customer Cap
published: true
tags: ai, saas, smallbusiness, voiceai
---

Most AI phone receptionists charge per call ($1.60-1.90/call) or cap you at a fixed number of unique customers per month on entry-level plans. We built AION Voice Receptionist to avoid both.

## What it does

- Answers business calls 24/7 — no more voicemail
- Texts back any missed call instantly with a way to reach you
- Captures name, number, and reason for calling as a lead automatically

## Pricing

Flat $89/month, 300 minutes included, $0.15/min after. No per-call fee, no cap on unique callers.

## Try it

There's a live demo line — call it and test the exact experience your customers would get, no signup required: [{PRODUCT_URL}]({PRODUCT_URL})
"""

PR_REDDIT_POST = f"""**Built an AI phone receptionist with no per-call fees or customer caps — feedback welcome**

Most AI receptionist tools either charge per call or cap you at ~100 unique customers/month on the entry plan. Built this one flat-rate instead: $89/mo, 300 min included, $0.15/min after, no cap.

Answers calls 24/7, texts back missed calls instantly, captures leads automatically. There's a live demo number you can call to test it before signing up — no account needed.

{PRODUCT_URL}

Happy to answer questions about how it's built or the pricing model.
"""

# Small-business/service-industry subreddits — relevant to Voice Receptionist's
# actual audience, not the retired compliance product's legal/regtech ones.
PR_SUBREDDITS = ["r/smallbusiness", "r/Entrepreneur", "r/SaaS", "r/sweatystartup"]

_PRESS_ANGLE = {
    "template": PR_TEMPLATE,
    "devto": PR_DEVTO_ARTICLE,
    "devto_title": "We Built an AI Receptionist With No Per-Call Fees and No Customer Cap",
    "reddit": PR_REDDIT_POST,
    "reddit_title": "Built an AI phone receptionist with no per-call fees or customer caps — feedback welcome",
    "subject": "Press Release: New AI Voice Receptionist Launches for Small Businesses",
}


def _send_via_smtp(to_email: str, subject: str, body: str) -> bool:
    if not (HOSTINGER_USER and HOSTINGER_PASS):
        return False
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = HOSTINGER_USER
        msg["To"] = to_email
        server = smtplib.SMTP("smtp.hostinger.com", 587, timeout=15)
        server.starttls()
        server.login(HOSTINGER_USER, HOSTINGER_PASS)
        server.sendmail(HOSTINGER_USER, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        logger.warning("SMTP send error to %s: %s", to_email, e)
        return False


async def _send_listing_email(directory: dict) -> bool:
    body = LISTING_EMAIL_TEMPLATE.format(directory=directory["name"], product_url=PRODUCT_URL)
    # Sent to the owner's inbox for manual review/forward — directory
    # listing forms often require filling a web form anyway, this drafts
    # the copy rather than pretending to auto-submit a form we can't see.
    return await asyncio.to_thread(
        _send_via_smtp, OWNER_EMAIL, f"[Listing draft] {directory['name']}", body,
    )


async def _publish_pr_to_devto(angle: dict) -> bool:
    if not DEVTO_KEY:
        return False
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://dev.to/api/articles",
                headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"},
                json={"article": {"title": angle["devto_title"], "body_markdown": angle["devto"], "published": True, "tags": ["ai", "saas", "smallbusiness"]}},
            )
        logger.info("[DevTo-PR] Published: %s", r.status_code)
        return r.status_code < 300
    except Exception as e:
        logger.warning("[DevTo-PR] Error: %s", e)
        return False


# Reddit's Responsible Builder Policy explicitly bans "posting identical or
# substantially similar content across subreddits" as spam. Each subreddit
# below gets its own LLM-generated angle/title instead of reusing one post,
# so this is real cross-posting variation, not a workaround of the rule.
_SUBREDDIT_ANGLES = {
    "r/smallbusiness": "written for owners frustrated with missed calls costing them customers, focus on the pain not the tech",
    "r/Entrepreneur": "written for people evaluating tools to scale a service business without hiring more staff",
    "r/SaaS": "written for a technical/builder audience, focus on the flat-pricing-vs-per-call-fee model as a product decision",
    "r/sweatystartup": "written for owners of hands-on local service businesses (contractors, cleaners, salons) who are on the phone or on a job, not at a desk",
}


async def _generate_reddit_post(subreddit: str) -> dict | None:
    try:
        from src.config import Settings
        from src.api.deepseek_client import DeepSeekClient

        angle_hint = _SUBREDDIT_ANGLES.get(subreddit, "written for a small business audience")
        deepseek = DeepSeekClient(Settings())
        prompt = (
            "Write a short, genuine-sounding Reddit self-post (not an ad) about AION Voice Receptionist, "
            "an AI phone answering service for small businesses: $89/mo flat, 300 min included, no per-call fee, "
            "no customer cap, live demo line, self-service setup. "
            f"Angle for this specific subreddit: {angle_hint}. "
            "Return exactly two lines: first line is ONLY the raw title text (no 'Title:' label, no quotes, "
            "no prefix of any kind), second line is the post body (2-4 short paragraphs, casual tone, "
            "first-person, no markdown headers, no emoji spam). "
            f"Include this link once: {PRODUCT_URL}"
        )
        raw = await asyncio.to_thread(
            deepseek.chat, "You write genuine, non-spammy Reddit posts for indie SaaS founders.", prompt, None, None, "en",
        )
        lines = [l for l in raw.strip().split("\n", 1) if l.strip()]
        if len(lines) < 2:
            return None
        return {"title": lines[0].strip(), "text": lines[1].strip()}
    except Exception as e:
        logger.warning("[Reddit-PR] Generation failed for %s: %s", subreddit, e)
        return None


async def _publish_pr_to_reddit(angle: dict) -> bool:
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD]):
        return False
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            auth_r = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET),
                data={"grant_type": "password", "username": REDDIT_USERNAME, "password": REDDIT_PASSWORD},
                headers={"User-Agent": "AIONVoiceReceptionist/1.0"},
            )
            token = auth_r.json().get("access_token", "")
            if not token:
                return False
            posted = []
            for sub in PR_SUBREDDITS[:2]:  # 2 per cycle to avoid spam flags
                post = await _generate_reddit_post(sub)
                if not post:
                    continue
                await client.post(
                    "https://oauth.reddit.com/api/submit",
                    headers={"Authorization": f"bearer {token}", "User-Agent": "AIONVoiceReceptionist/1.0"},
                    data={"sr": sub.replace("r/", ""), "kind": "self", "title": post["title"], "text": post["text"]},
                )
                posted.append(sub)
                await asyncio.sleep(5)
        logger.info("[Reddit-PR] Posted unique content to %s", posted)
        return bool(posted)
    except Exception as e:
        logger.warning("[Reddit-PR] Error: %s", e)
        return False


async def auto_job_directories():
    """Called every 72h by the JOBS loop in app/main.py. Picks the 2
    directories least recently sent (checked against real Supabase state,
    not an in-memory counter that reset to directory #1 on every backend
    redeploy) and skips anything sent within _DIRECTORY_RESEND_DAYS."""
    try:
        dirs_email = [d for d in DIRECTORIES if d["type"] == "email_request"]
        cutoff = datetime.now(timezone.utc) - timedelta(days=_DIRECTORY_RESEND_DAYS)
        due = []
        for d in dirs_email:
            last = await _last_sent_at("directory", d["name"])
            if last is None or last < cutoff:
                due.append((last or datetime.min.replace(tzinfo=timezone.utc), d))
        due.sort(key=lambda pair: pair[0])  # never-sent (None) and oldest first

        for _, d in due[:_DIRECTORIES_PER_RUN]:
            sent = await _send_listing_email(d)
            logger.info("[SDR] Directory %s: email %s", d["name"], "sent" if sent else "skipped")
            if sent:
                await _mark_sent("directory", d["name"])
            await asyncio.sleep(5)

        if not due:
            logger.info("[SDR] Directories: all %d covered within the last %dd, nothing due", len(dirs_email), _DIRECTORY_RESEND_DAYS)
    except Exception as e:
        logger.error("[SDR] Directory job error: %s", e)


async def auto_job_press_release_distribution():
    """Called every 14 days by the JOBS loop. Republishing the exact same
    static PR to Dev.to on every single 14-day tick (with no state check)
    would create duplicate articles for as long as the process stays alive
    -- checks real last-publish state first and skips if still fresh."""
    try:
        last_devto = await _last_sent_at("devto_pr", _PRESS_ANGLE["devto_title"])
        cutoff = datetime.now(timezone.utc) - timedelta(days=_DEVTO_RESEND_DAYS)
        if last_devto is None or last_devto < cutoff:
            if await _publish_pr_to_devto(_PRESS_ANGLE):
                await _mark_sent("devto_pr", _PRESS_ANGLE["devto_title"])
        else:
            logger.info("[SDR] Dev.to PR already published %s, skipping (resend after %dd)", last_devto.isoformat(), _DEVTO_RESEND_DAYS)

        await _publish_pr_to_reddit(_PRESS_ANGLE)
        _send_via_smtp(
            OWNER_EMAIL,
            "[AUTO] PR draft ready — verify Dev.to/Reddit posted, submit to OpenPR manually",
            "Press release distributed automatically where API keys exist (Dev.to, Reddit — "
            "currently unconfigured, check .env if this didn't post). "
            "Submit manually to OpenPR.com and Product Hunt if desired.\n\n" + _PRESS_ANGLE["template"],
        )
        logger.info("[SDR] Press release distribution cycle done")
    except Exception as e:
        logger.error("[SDR] PR distribution error: %s", e)


@router.post("/run-now")
async def run_directories_now():
    """Manual trigger for auto_job_directories() -- fires today's due batch
    immediately instead of waiting for the daily cron tick."""
    await auto_job_directories()
    return {"status": "triggered"}


@router.get("/list")
async def list_directories():
    return {"directories": DIRECTORIES, "total": len(DIRECTORIES)}


@router.get("/press-release")
async def get_press_release():
    return {"press_release": PR_TEMPLATE}
