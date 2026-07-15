import asyncio
import httpx
import logging
import os
from fastapi import APIRouter, BackgroundTasks
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/syndication", tags=["syndication"])
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a B2B SaaS content marketing expert writing for compliance and regulatory tech.
Write technical articles that rank on Google and convert readers to trial users.
Style: authoritative, data-driven, practical. Include statistics and deadlines.
Always end with a CTA linking to: https://global-engenharia.com/ecosystem
Output: title, intro (2 sentences), body (500-700 words with H2 subheadings), conclusion, tags (5 tags)"""

TOPICS = [
    "EU AI Act compliance checklist 2026",
    "CSRD reporting requirements for SMEs",
    "NR-1 Psicossocial — guia completo 2026",
    "DORA compliance for fintech companies",
    "SOC2 Type II — how to prepare in 6 months",
    "ISO 27001:2022 gap analysis template",
    "NIS2 Directive — who is affected and what to do",
    "LGPD compliance automation with AI",
    "ESG reporting automation tools 2026",
    "AI agents for regulatory compliance — ROI analysis",
]


@router.post("/generate-article")
async def generate_article(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    topic = data.get("topic", TOPICS[0])
    language = data.get("language", "en")
    prompt = f"Write a compliance article in {language} about: {topic}\nCTA: https://global-engenharia.com/ecosystem"
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"article": response, "topic": topic, "language": language}


@router.post("/publish-devto")
async def publish_devto(data: dict, background_tasks: BackgroundTasks):
    """Publish article to Dev.to automatically."""
    background_tasks.add_task(_publish_to_devto, data.get("topic", TOPICS[0]))
    return {"status": "publishing", "platform": "dev.to"}


async def _publish_to_devto(topic: str):
    api_key = os.getenv("DEVTO_API_KEY", "")
    if not api_key:
        logger.warning("DEVTO_API_KEY not set")
        return
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Write a Dev.to article about: {topic}\nCTA: https://global-engenharia.com/ecosystem"
    content = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://dev.to/api/articles",
                headers={"api-key": api_key, "Content-Type": "application/json"},
                json={
                    "article": {
                        "title": topic,
                        "published": True,
                        "body_markdown": str(content),
                        "tags": ["compliance", "ai", "regulation", "saas"],
                        "canonical_url": "https://global-engenharia.com/ecosystem",
                    }
                },
                timeout=30,
            )
        logger.info("Published to Dev.to: %s", topic)
    except Exception as e:
        logger.error("Dev.to publish error: %s", e)


@router.post("/daily-campaign")
async def daily_campaign(background_tasks: BackgroundTasks):
    """Publish one article per platform daily — call via cron."""
    import random
    topic = random.choice(TOPICS)
    background_tasks.add_task(_publish_to_devto, topic)
    return {"status": "daily_campaign_started", "topic": topic}


@router.get("/topics")
async def list_topics():
    return {"topics": TOPICS}
