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
            base_url=settings.openrouter_api_base,
        )
        self.fallback_llm = (
            OpenAI(api_key=settings.opencode_zen_api_key, base_url=settings.opencode_zen_api_base)
            if settings.opencode_zen_api_key
            else None
        )

    def _generate(self, prompt: str) -> str:
        try:
            resp = self.llm.chat.completions.create(
                model=self.settings.openrouter_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1800,
                response_format={"type": "json_object"},
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            if self.fallback_llm is None:
                raise
            # OpenRouter out of credits (402) or any other failure -- fall
            # back to OpenCode Zen's free-tier model. It's a reasoning model
            # (thinking tokens count against max_tokens before the actual
            # JSON answer), so it gets a larger budget than the primary call.
            print(f"[SEO] OpenRouter failed ({e!r}), falling back to OpenCode Zen")
            resp = self.fallback_llm.chat.completions.create(
                model=self.settings.opencode_zen_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
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
                    # tags" finding, confirmed 2026-07-19 audit). Keeps size
                    # out of the title (still in meta description) and drops
                    # the "AI Voice Receptionist —" prefix -- the renderer
                    # already appends " | AION Voice Receptionist" to every
                    # title, so repeating it here just wasted length: sampled
                    # titles were 77-128 chars (Semrush "title too long"
                    # finding, confirmed systemic, not a 21-page edge case).
                    "title": f"{topic.title_label} — {sector.replace('-', ' ').title()} ({market})",
                    "meta_description": (
                        f"AI voice receptionist for {sector.replace('-', ' ')} ({size_label.lower()}): "
                        f"{topic.dor.rstrip('.')}. See how our virtual receptionist handles it, 24/7."
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


@router.get("/debug/try-upsert/{market}")
async def debug_try_upsert(market: str):
    """Diagnostic-only: one bulk select (same pattern as the real function,
    not N+1) to find the first un-migrated slug, then attempts the real
    upsert OUTSIDE any swallow-and-continue handler so the actual DB
    exception (RLS, constraint, schema mismatch, etc) surfaces directly."""
    import traceback

    market = market.upper()
    plan = plan_slugs(market)
    language = LANGUAGE_BY_REGION[market]
    db = SupabaseClient(Settings())
    agent = SEOContentAgent(Settings())

    existing = db.client.table("seo_pages").select("slug,body").eq("market", market).execute()
    migrated_slugs = set()
    for row in existing.data or []:
        try:
            if isinstance(json.loads(row["body"]), dict):
                migrated_slugs.add(row["slug"])
        except (json.JSONDecodeError, TypeError):
            pass

    target = next(((t, s, sk, sl, slug) for t, s, sk, sl, slug in plan if slug not in migrated_slugs), None)
    if target is None:
        return {"stage": "all_migrated_already", "total_slugs": len(plan), "migrated": len(migrated_slugs)}
    topic, sector, size_key, size_label, slug = target

    try:
        prompt = _build_prompt(topic, sector, size_label, language)
        result = await agent._generate_unique_body(prompt, set())
    except Exception as e:
        return {"slug": slug, "stage": "generation_exception", "error": repr(e), "traceback": traceback.format_exc()}
    if result is None:
        return {"slug": slug, "stage": "generation_returned_none"}
    structured, content_hash = result

    page_data = {
        "slug": slug,
        "title": f"{topic.title_label} — {sector.replace('-', ' ').title()} ({market})",
        "meta_description": f"AI voice receptionist for {sector.replace('-', ' ')} ({size_label.lower()}): {topic.dor.rstrip('.')}. See how our virtual receptionist handles it, 24/7.",
        "body": json.dumps(structured, ensure_ascii=False),
        "stripe_link": topic.stripe_link,
        "market": market,
        "published": True,
        "topic_kind": topic.kind,
        "product": topic.product,
        "region": market,
        "content_hash": content_hash,
    }
    try:
        resp = db.client.table("seo_pages").upsert(page_data, on_conflict="slug").execute()
        return {"slug": slug, "stage": "upsert_ok", "returned_rows": len(resp.data or [])}
    except Exception as e:
        return {"slug": slug, "stage": "upsert_exception", "error": repr(e), "traceback": traceback.format_exc()}


@router.post("/debug/backfill-meta-descriptions")
async def debug_backfill_meta_descriptions():
    """One-off fix for a template bug found 2026-07-21: meta_description was
    built from raw sector slugs (hyphens left in, e.g. "real-estate-agencies")
    and duplicated "business"/"businesses" wording (size_label already reads
    "multi-location business", template appended another " businesses"), with
    no punctuation before "See how...". Pure string recompute from plan_slugs
    -- no LLM call, so this is cheap to run against all ~972 rows at once."""
    db = SupabaseClient(Settings())
    updated = 0
    errors = []
    for market in ["US", "UK", "CA", "AU"]:
        for topic, sector, size_key, size_label, slug in plan_slugs(market):
            new_desc = (
                f"AI voice receptionist for {sector.replace('-', ' ')} ({size_label.lower()}): "
                f"{topic.dor.rstrip('.')}. See how our virtual receptionist handles it, 24/7."
            )
            try:
                db.client.table("seo_pages").update({"meta_description": new_desc}).eq("slug", slug).execute()
                updated += 1
            except Exception as e:
                errors.append({"slug": slug, "error": repr(e)})
    return {"updated": updated, "errors": errors[:20], "error_count": len(errors)}


@router.post("/debug/backfill-titles")
async def debug_backfill_titles():
    """One-off fix for real audit finding 2026-07-21 (30 pages flagged "title
    element is too long", up to 103 chars): the 2026-07-19 title-length fix
    only applied to newly generated pages, never backfilled to existing
    rows -- same class of bug as the meta_description backfill above. Also
    now uses topic.title_label (short_title where set) instead of the full
    question-style topic.nome for especially verbose topics. Pure string
    recompute from plan_slugs -- no LLM call."""
    db = SupabaseClient(Settings())
    updated = 0
    errors = []
    for market in ["US", "UK", "CA", "AU"]:
        for topic, sector, size_key, size_label, slug in plan_slugs(market):
            new_title = f"{topic.title_label} — {sector.replace('-', ' ').title()} ({market})"
            try:
                db.client.table("seo_pages").update({"title": new_title}).eq("slug", slug).execute()
                updated += 1
            except Exception as e:
                errors.append({"slug": slug, "error": repr(e)})
    return {"updated": updated, "errors": errors[:20], "error_count": len(errors)}


@router.get("/debug/migration-progress")
async def debug_migration_progress():
    """Diagnostic-only: real count of combinatorial pages already migrated to
    the premium JSON template vs still on the old prose format, per market --
    a direct answer to "how far along is the migration" that doesn't depend
    on the sdr_growth_log report (which silently no-ops if that table's
    "notes" column migration hasn't landed yet)."""
    db = SupabaseClient(Settings())
    result = {}
    for market in ["US", "UK", "CA", "AU"]:
        rows = (
            db.client.table("seo_pages")
            .select("body")
            .eq("market", market)
            .not_.in_("topic_kind", ["guide", "comparison"])
            .execute()
        )
        total = len(rows.data or [])
        migrated = 0
        for row in rows.data or []:
            try:
                if isinstance(json.loads(row.get("body") or ""), dict):
                    migrated += 1
            except (json.JSONDecodeError, TypeError):
                pass
        result[market] = {"total": total, "migrated": migrated, "pending": total - migrated}
    grand_total = sum(v["total"] for v in result.values())
    grand_migrated = sum(v["migrated"] for v in result.values())
    return {
        "by_market": result,
        "overall": {
            "total": grand_total,
            "migrated": grand_migrated,
            "pending": grand_total - grand_migrated,
            "pct_migrated": round(100 * grand_migrated / grand_total, 1) if grand_total else 0,
        },
    }


@router.post("/gsc/run-now")
async def gsc_feedback_run_now():
    """Manual trigger for the GSC feedback pull -- normally only runs on the
    7-day cron. Added so GSC_CLIENT_ID/SECRET/REFRESH_TOKEN can be verified
    right after being set in Render, instead of waiting up to a week."""
    from src.agents.seo_feedback_agent import SEOFeedbackAgent

    feedback = SEOFeedbackAgent(Settings())
    if not feedback.is_configured():
        return {"configured": False, "error": "GSC_CLIENT_ID/SECRET/REFRESH_TOKEN not set or invalid"}
    result = feedback.pull_and_store()
    return {"configured": True, "result": result}


@router.get("/debug/list-static-pages")
async def debug_list_static_pages():
    """Diagnostic-only: lists every seo_pages row with topic_kind in
    (guide, comparison) -- these are the hand-written static pages whose
    real URL is a root-level .html file, not derivable from slug alone."""
    db = SupabaseClient(Settings())
    rows = db.client.table("seo_pages").select("slug,title,topic_kind,market").in_(
        "topic_kind", ["guide", "comparison"]
    ).execute()
    return {"count": len(rows.data or []), "rows": rows.data}


@router.get("/debug/raw-row/{slug}")
async def debug_raw_row(slug: str):
    """Diagnostic-only: returns exactly what's stored for one slug, no
    interpretation -- to see whether existing_slugs' 'is it valid JSON'
    check is classifying rows correctly."""
    db = SupabaseClient(Settings())
    row = db.client.table("seo_pages").select("slug,title,body").eq("slug", slug).execute()
    if not row.data:
        return {"found": False}
    r = row.data[0]
    body = r.get("body") or ""
    try:
        parsed = json.loads(body)
        is_json = isinstance(parsed, dict)
    except (json.JSONDecodeError, TypeError):
        is_json = False
    return {
        "found": True,
        "title": r.get("title"),
        "body_len": len(body),
        "body_preview": body[:300],
        "is_valid_json_dict": is_json,
        "row_count_for_slug": len(row.data),
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
