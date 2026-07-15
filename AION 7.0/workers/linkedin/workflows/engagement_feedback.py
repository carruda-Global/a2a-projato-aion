"""Reads the history of previously published posts/carousels, pulls real
engagement data from LinkedIn's analytics API per post, and aggregates it by
topic — so the next post/carousel selection is biased toward topics that
actually get more engagement, instead of picking uniformly at random.

History used to live in a local JSON file, which is wiped on every Render
redeploy (ephemeral filesystem) -- moved to Supabase so it survives deploys."""
import os
import logging
from datetime import datetime, timezone

import httpx

from integrations import LinkedInIntegration, LinkedInConfig

logger = logging.getLogger(__name__)

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
_TABLE = "linkedin_post_history"


def _load_history() -> list[dict]:
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return []
    try:
        r = httpx.get(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            params={"select": "post_id,topico_id,tipo,url,published_at", "order": "published_at.desc", "limit": "200"},
            headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            timeout=15,
        )
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        logger.warning("[LinkedIn] Falha ao ler historico do Supabase: %s", e)
        return []


def registrar_publicacao(post_id: str, topico_id: str, tipo: str, url: str = "") -> None:
    """Called right after a successful publish so the feedback loop has
    something to measure later."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return
    row = {
        "post_id": post_id, "topico_id": topico_id, "tipo": tipo,
        "url": url, "published_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        httpx.post(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            json=row,
            headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}", "Prefer": "resolution=merge-duplicates"},
            timeout=15,
        )
    except Exception as e:
        logger.warning("[LinkedIn] Falha ao gravar historico no Supabase: %s", e)


def contar_publicados_hoje() -> dict[str, int]:
    """Shared daily-cap check: counts posts already published today (UTC) by
    tipo ('post'/'carousel'), across ALL pipelines that call
    registrar_publicacao() (agent.py, daily_job.py, career_positioning.py).
    This is what lets 3 independent, uncoordinated schedulers stay within the
    intended 3 normal + 1 carousel per day instead of each publishing
    blind to what the others already did."""
    counts = {"post": 0, "carousel": 0}
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return counts
    hoje = datetime.now(timezone.utc).date().isoformat()
    try:
        r = httpx.get(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            params={"select": "tipo", "published_at": f"gte.{hoje}T00:00:00"},
            headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            timeout=15,
        )
        rows = r.json() if r.status_code == 200 else []
    except Exception as e:
        logger.warning("[LinkedIn] Falha ao contar posts de hoje: %s", e)
        return counts
    for row in rows:
        tipo = row.get("tipo")
        if tipo in counts:
            counts[tipo] += 1
    return counts


async def calcular_pesos_topico(linkedin: LinkedInIntegration | None = None, max_posts: int = 40) -> dict[str, float]:
    """Fetches real engagement (likes+comments+shares) for the most recent
    posts, sums it per topico_id, and normalizes into weights. Topics with no
    history yet default to weight 1.0 (neutral) so new topics still get a
    fair shot."""
    history = _load_history()[-max_posts:]
    if not history:
        return {}

    own_li = linkedin is None
    if own_li:
        linkedin = LinkedInIntegration(config=LinkedInConfig())
        await linkedin.initialize()

    pesos: dict[str, float] = {}
    try:
        for item in history:
            perf = await linkedin.analytics.get_post_performance(item["post_id"])
            elements = perf.get("analytics", {}).get("elements", [])
            score = 0.0
            for elem in elements:
                stats = elem.get("statisticalData", {})
                score += stats.get("likeCount", 0) + 2 * stats.get("commentCount", 0) + 3 * stats.get("shareCount", 0)
            pesos[item["topico_id"]] = pesos.get(item["topico_id"], 0.0) + score
    finally:
        if own_li:
            await linkedin.shutdown()

    if not pesos or max(pesos.values()) == 0:
        return {}
    maior = max(pesos.values())
    # Range widened 2026-07-14 (0.5-2.0 -> 0.05-2.5): AggregateAnalytics for
    # 2026-06-17/07-14 confirmed compliance-mill topics still average ~0 real
    # engagement while career-positioning-style content converts (best post:
    # 3 engagements on 43 impressions, a ~7% rate). The old 0.5 floor meant a
    # dead topic still posted at half the rate of the best performer; escolher_variacao
    # already clamps to a 0.1 floor, so scores below that collapse to the same
    # effective minimum instead of the topic staying in meaningful rotation.
    return {k: round(0.05 + (v / maior) * 2.45, 2) for k, v in pesos.items()}
