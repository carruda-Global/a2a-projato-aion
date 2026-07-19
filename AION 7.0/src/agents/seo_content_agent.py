import asyncio
import hashlib
import json
from fastapi import APIRouter, BackgroundTasks
from openai import OpenAI
from src.database.supabase_client import SupabaseClient
from src.config import Settings
from src.agents.seo_topics import Topic, LANGUAGE_BY_REGION, topics_for_market

router = APIRouter(prefix="/api/seo", tags=["seo_agent"])

MAX_REGEN_ATTEMPTS = 2

# JSON schema the LLM must fill -- rendered by seo_pages_router.py into the
# premium landing-page template (hero, TOC, comparison table, FAQ w/ schema,
# etc). Keeping this as structured JSON (not a prose blob) is what lets one
# template serve all ~1000 combinatorial pages consistently.
_CONTENT_SCHEMA_INSTRUCTIONS = """
Respond with ONLY a valid JSON object (no markdown fences, no commentary), with exactly these keys:
{
  "intro": "150-250 word intro paragraph framing the problem, in __LANGUAGE__",
  "how_it_works": ["step 1 (short phrase)", "step 2", "step 3", "step 4"],
  "benefits": [{"title": "short benefit title", "desc": "1-2 sentence explanation"}, ... 5 items],
  "comparison": [{"criterion": "e.g. Availability", "human": "human/manual answer", "ai": "AI agent answer"}, ... 5 rows covering Availability, Cost, Scalability, Response Time, Consistency],
  "real_example": {"before": "1-2 sentences describing the pain before", "after": "1-2 sentences describing the outcome after", "result": "one concrete metric-style result phrase"},
  "industries": ["industry 1", "industry 2", "industry 3", "industry 4"],
  "faq": [{"q": "question", "a": "80-150 word answer"}, ... 6 items]
}
All text in __LANGUAGE__. Be concrete and specific to the sector/topic given, not generic. No invented statistics presented as fact -- use realistic, qualitative framing instead (e.g. "significantly fewer missed calls" not a fabricated percentage).
"""


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
    schema = _CONTENT_SCHEMA_INSTRUCTIONS.replace("__LANGUAGE__", language)
    if topic.kind == "regulation":
        context = (
            f"Regulation: {topic.nome} ({topic.norma})\n"
            f"Sector: {sector}, Company size: {size_label}\n"
            f"Pain: {topic.dor}\n"
            f"Frame 'how_it_works' as how the agent resolves this in 48h. "
            f"Frame 'comparison' as Manual/Legal-team handling vs the agent."
        )
    else:
        context = (
            f"Workflow automated: {topic.nome} ({topic.norma})\n"
            f"Sector: {sector}, Company size: {size_label}\n"
            f"Pain today without automation: {topic.dor}\n"
            f"Avoid legal/fine framing — this is a workflow-automation pitch, "
            f"not a compliance penalty pitch."
        )
    return f"{context}\n\n{schema}"


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
            max_tokens=1800,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content or ""

    def _validate_structured(self, raw: str) -> dict | None:
        """Confirms the LLM actually returned the required sections -- a
        malformed/truncated JSON response would otherwise silently render as
        a broken page (empty FAQ, missing comparison table, etc)."""
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None
        required = ("intro", "how_it_works", "benefits", "comparison", "real_example", "industries", "faq")
        if not all(k in data for k in required):
            return None
        if len(data.get("intro", "")) < 100 or len(data.get("faq", [])) < 3:
            return None
        return data

    async def _generate_unique_body(self, prompt: str, seen_hashes: set[str]) -> tuple[dict, str] | None:
        """Generates a structured page body, retrying once with a nudge if
        it's malformed, too thin, or a hash-duplicate of something already
        produced this run. Returns (structured_dict, hash) or None."""
        current_prompt = prompt
        for attempt in range(MAX_REGEN_ATTEMPTS):
            raw = await asyncio.to_thread(self._generate, current_prompt)
            data = self._validate_structured(raw)
            if data is not None:
                h = _content_hash(data["intro"] + "".join(f["q"] for f in data["faq"]))
                if h not in seen_hashes:
                    return data, h
            current_prompt = prompt + (
                "\nPrevious attempt was malformed, too short, or too generic — "
                "return valid JSON matching the schema exactly, with a longer, "
                "more specific, distinct angle."
            )
        return None

    async def generate_market_pages(
        self,
        market: str,
        product_filter: str | None = None,
        kind_filter: str | None = None,
        limit: int | None = None,
        force: bool = False,
    ) -> dict:
        """force=True regenerates pages that already exist (used for the
        2026-07-19 premium-template migration -- rewrites old plain-text
        `body` rows into the structured JSON the new template renders)."""
        plan = plan_slugs(market, product_filter, kind_filter)
        if not plan:
            return {"error": f"No topics configured for market: {market}"}
        language = LANGUAGE_BY_REGION[market]
        db = SupabaseClient(self.settings)

        existing = (
            db.client.table("seo_pages").select("slug,body").eq("market", market).execute()
        )
        if force:
            # Skip rows already migrated to the structured-JSON template so
            # repeated batched calls make real progress instead of
            # regenerating the same first `limit` slugs every time.
            existing_slugs = set()
            for row in existing.data or []:
                try:
                    if isinstance(json.loads(row["body"]), dict):
                        existing_slugs.add(row["slug"])
                except (json.JSONDecodeError, TypeError):
                    pass
        else:
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
                structured, content_hash = result
                seen_hashes.add(content_hash)
                page_data = {
                    "slug": slug,
                    # market must be in the title -- without it, the same
                    # topic/sector/size combo across US/UK/CA/AU produces an
                    # identical <title> string (Semrush "duplicate title
                    # tags" finding, confirmed 2026-07-19 audit: e.g.
                    # us-missed-call-text-back-home-services-multi-location
                    # and ca-missed-call-text-back-home-services-multi-location
                    # both rendered "Missed-Call Text-Back — Home-Services —
                    # multi-location business").
                    "title": f"AI Voice Receptionist — {topic.nome} — {market} {sector.title()} ({size_label})",
                    "meta_description": (
                        f"AI voice receptionist for {sector} {size_label.lower()} businesses: "
                        f"{topic.dor} See how our virtual receptionist handles it, 24/7."
                    ),
                    "body": json.dumps(structured, ensure_ascii=False),
                    "stripe_link": topic.stripe_link,
                    "market": market,
                    "published": True,
                    "topic_kind": topic.kind,
                    "product": topic.product,
                    "region": market,
                    "content_hash": content_hash,
                }
                # on_conflict="slug" is required -- slug is UNIQUE but not the
                # primary key (id is), so a plain upsert() targets the PK by
                # default. Since page_data has no id, every upsert against an
                # EXISTING slug (i.e. every force=true regeneration) was
                # silently INSERTing and hitting the slug UNIQUE constraint,
                # caught by the except below and counted as "skipped" -- this
                # is why force=true regeneration never visibly progressed.
                db.client.table("seo_pages").upsert(page_data, on_conflict="slug").execute()
                generated.append(slug)
            except Exception as e:
                print(f"Erro ao gerar {slug}: {e}")
                skipped.append(slug)
        return {
            "market": market,
            "pages_generated": len(generated),
            "pages_skipped": len(skipped),
        }


@router.get("/debug/generate-one/{market}")
async def debug_generate_one(market: str):
    """Diagnostic-only: runs one generation synchronously against the first
    not-yet-migrated slug and returns the raw LLM output plus why validation
    passed/failed -- background_tasks swallows exceptions into server logs
    we can't otherwise see. Safe to leave in; makes no DB writes."""
    plan = plan_slugs(market.upper())
    if not plan:
        return {"error": f"No topics for market {market}"}
    topic, sector, size_key, size_label, slug = plan[0]
    language = LANGUAGE_BY_REGION[market.upper()]
    prompt = _build_prompt(topic, sector, size_label, language)
    agent = SEOContentAgent(Settings())
    try:
        raw = await asyncio.to_thread(agent._generate, prompt)
    except Exception as e:
        return {"slug": slug, "stage": "llm_call", "error": repr(e)}
    validated = agent._validate_structured(raw)
    return {
        "slug": slug,
        "raw_len": len(raw),
        "raw_preview": raw[:1500],
        "valid": validated is not None,
    }


@router.get("/debug/generate-one-sync/{market}")
async def debug_generate_one_sync(market: str):
    """Diagnostic-only: runs the REAL generate_market_pages() pipeline
    synchronously (limit=1, force=true) so exceptions that background_tasks
    would otherwise swallow into unreachable server logs surface directly
    in the HTTP response. This DOES write to the DB (real upsert)."""
    agent = SEOContentAgent(Settings())
    try:
        result = await agent.generate_market_pages(market.upper(), limit=1, force=True)
        return {"stage": "ok", "result": result}
    except Exception as e:
        import traceback
        return {"stage": "exception", "error": repr(e), "traceback": traceback.format_exc()}


@router.post("/generate/{market}")
async def trigger_generation(
    market: str, background_tasks: BackgroundTasks, limit: int | None = None, force: bool = False
):
    """Fire-and-forget: the structured-JSON generation is slow enough per page
    (LLM call + validation) that even limit=1 can exceed the platform's ~100s
    reverse-proxy timeout, so this returns immediately and runs in the
    background. Poll /api/seo/agent/status for the updated page counts.
    Without force, already-generated slugs are skipped so batching resumes
    where the previous call left off; with force=true, existing pages are
    regenerated (used for the premium-template migration)."""
    agent = SEOContentAgent(Settings())
    background_tasks.add_task(agent.generate_market_pages, market.upper(), limit=limit, force=force)
    return {"market": market.upper(), "status": "started", "limit": limit, "force": force}


# SEO page rendering movido para src/agents/seo_pages_router.py
