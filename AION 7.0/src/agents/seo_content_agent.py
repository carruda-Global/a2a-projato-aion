import asyncio
import hashlib
from fastapi import APIRouter
from openai import OpenAI
from src.database.supabase_client import SupabaseClient
from src.config import Settings
from src.agents.seo_topics import Topic, LANGUAGE_BY_REGION, topics_for_market

router = APIRouter(prefix="/api/seo", tags=["seo_agent"])

MIN_BODY_LEN = 350  # chars — cheap floor against near-empty/truncated LLM output
MAX_REGEN_ATTEMPTS = 2


def _normalize(text: str) -> str:
    return " ".join(text.split()).lower()


def _content_hash(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()


def plan_slugs(
    market: str,
    product_filter: str | None = None,
    kind_filter: str | None = None,
) -> list[tuple[Topic, str, str, str, str]]:
    """Pure planning — no LLM/DB calls. Returns
    (topic, sector, size_key, size_label, slug) tuples for a market, optionally
    narrowed to one product or topic kind. Used by --dry-run and by the real
    generation loop, so the plan shown to the user is exactly what gets run."""
    plan: list[tuple[Topic, str, str, str, str]] = []
    for topic in topics_for_market(market):
        if product_filter and topic.product != product_filter:
            continue
        if kind_filter and topic.kind != kind_filter:
            continue
        sectors = topic.sectors_for(market)
        sizes = topic.sizes_for(market)
        for sector in sectors:
            for size_key, size_label in sizes.items():
                slug = f"{market.lower()}-{topic.key}-{sector}-{size_key}"
                plan.append((topic, sector, size_key, size_label, slug))
    return plan


def _build_prompt(topic: Topic, sector: str, size_label: str, language: str) -> str:
    if topic.kind == "regulation":
        return (
            f"Write a landing page in {language} for:\n"
            f"Regulation: {topic.nome} ({topic.norma})\n"
            f"Sector: {sector}, Company size: {size_label}\n"
            f"Pain: {topic.dor}\n"
            f"Structure: H1, risk paragraph, 3 action bullets, "
            f"how the agent solves it in 48h, CTA.\n"
            f"Direct tone, real numbers, max 600 words."
        )
    return (
        f"Write a landing page in {language} for:\n"
        f"Workflow automated: {topic.nome} ({topic.norma})\n"
        f"Sector: {sector}, Company size: {size_label}\n"
        f"Pain today without automation: {topic.dor}\n"
        f"Structure: H1, current-state pain paragraph, 3 outcome bullets "
        f"(time saved, error reduction, cost avoided), how the agent does "
        f"it end-to-end, CTA.\n"
        f"Direct tone, real numbers, max 600 words. Avoid legal/fine framing "
        f"— this is a workflow-automation pitch, not a compliance penalty pitch."
    )


class SEOContentAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def _generate(self, prompt: str) -> str:
        resp = self.llm.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        return resp.choices[0].message.content or ""

    async def _generate_unique_body(self, prompt: str, seen_hashes: set[str]) -> tuple[str, str] | None:
        """Generates a body, retrying once with a higher-variance nudge if it's
        too short or a hash-duplicate of something already produced this run.
        Returns (body, hash) or None if still bad after MAX_REGEN_ATTEMPTS."""
        current_prompt = prompt
        for attempt in range(MAX_REGEN_ATTEMPTS):
            content = await asyncio.to_thread(self._generate, current_prompt)
            h = _content_hash(content)
            if len(content.strip()) >= MIN_BODY_LEN and h not in seen_hashes:
                return content, h
            current_prompt = prompt + (
                "\nPrevious attempt was too short or too generic — write a "
                "longer, more specific version with concrete numbers and a "
                "distinct angle."
            )
        return None

    async def generate_market_pages(
        self,
        market: str,
        product_filter: str | None = None,
        kind_filter: str | None = None,
        limit: int | None = None,
    ) -> dict:
        plan = plan_slugs(market, product_filter, kind_filter)
        if not plan:
            return {"error": f"No topics configured for market: {market}"}
        language = LANGUAGE_BY_REGION[market]
        db = SupabaseClient(self.settings)

        existing = (
            db.client.table("seo_pages").select("slug").eq("market", market).execute()
        )
        existing_slugs = {row["slug"] for row in (existing.data or [])}

        seen_hashes: set[str] = set()
        generated: list[str] = []
        skipped: list[str] = []

        for topic, sector, size_key, size_label, slug in plan:
            if limit is not None and len(generated) >= limit:
                break
            if slug in existing_slugs:
                continue
            prompt = _build_prompt(topic, sector, size_label, language)
            try:
                result = await self._generate_unique_body(prompt, seen_hashes)
                if result is None:
                    skipped.append(slug)
                    continue
                content, content_hash = result
                seen_hashes.add(content_hash)
                page_data = {
                    "slug": slug,
                    "title": f"{topic.nome} — {sector.title()} — {size_label}",
                    "meta_description": f"{topic.nome} ({topic.norma}). {topic.dor}.",
                    "body": content,
                    "stripe_link": topic.stripe_link,
                    "market": market,
                    "published": True,
                    "topic_kind": topic.kind,
                    "product": topic.product,
                    "region": market,
                    "content_hash": content_hash,
                }
                db.client.table("seo_pages").upsert(page_data).execute()
                generated.append(slug)
            except Exception as e:
                print(f"Erro ao gerar {slug}: {e}")
                skipped.append(slug)
        return {
            "market": market,
            "pages_generated": len(generated),
            "pages_skipped": len(skipped),
        }


@router.post("/generate/{market}")
async def trigger_generation(market: str, limit: int | None = None):
    """limit caps how many NEW pages this call generates — keeps a single
    request comfortably under the platform's reverse-proxy timeout. Safe to
    call repeatedly: already-generated slugs are skipped, so batching just
    resumes where the previous call left off."""
    agent = SEOContentAgent(Settings())
    return await agent.generate_market_pages(market.upper(), limit=limit)


# SEO page rendering movido para src/agents/seo_pages_router.py
