"""312-variation content bank (24 topics x 13 hooks) with anti-repeat tracking
and performance-weighted topic selection. No post/carousel repeats until all
312 combinations have been used once.

Anti-repeat state used to live in a local JSON file, wiped on every Render
redeploy (ephemeral filesystem) -- same bug class already fixed for
linkedin_post_history/sdr_outreach_log. Every redeploy reset the cycle back
to "all 312 available", which combined with the (separately broken) engagement
weighting meant selection was effectively uniform-random across all topics --
old, proven-low-engagement compliance topics kept resurfacing constantly."""
import os
import random
import logging
from datetime import datetime, timezone

import httpx

from config.topics import TOPICS
from config.hooks import HOOKS
from integrations.agent_bridge import ask_real_architecture

logger = logging.getLogger(__name__)

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
_TABLE = "linkedin_used_combos"

# Topics making a "look what our AI can actually do" claim get a real,
# live example from the real architecture instead of just asserting it.
_LIVE_PROOF_AGENTS = {
    "case-voicereceptionist": "architect_agent",
    "consultoria-ia": "structural_engineer",
    "dev-personalizado": "cost_estimator",
}
_LIVE_PROOF_QUERY = "In one or two sentences, give a concrete example of a question you can help answer."


def _load_used() -> list[str]:
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return []
    try:
        r = httpx.get(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            params={"select": "combo_id"},
            headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            timeout=15,
        )
        return [row["combo_id"] for row in r.json()] if r.status_code == 200 else []
    except Exception as e:
        logger.warning("[LinkedIn] Falha ao ler combos usados do Supabase: %s", e)
        return []


def _mark_used(combo_id: str) -> None:
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return
    try:
        httpx.post(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            json={"combo_id": combo_id, "used_at": datetime.now(timezone.utc).isoformat()},
            headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}", "Prefer": "resolution=merge-duplicates"},
            timeout=15,
        )
    except Exception as e:
        logger.warning("[LinkedIn] Falha ao gravar combo usado no Supabase: %s", e)


def _reset_used() -> None:
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return
    try:
        httpx.delete(
            f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
            params={"combo_id": "not.is.null"},
            headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            timeout=15,
        )
    except Exception as e:
        logger.warning("[LinkedIn] Falha ao resetar combos usados no Supabase: %s", e)


def _combo_id(topic_idx: int, hook_idx: int) -> str:
    return f"{TOPICS[topic_idx]['id']}::{hook_idx}"


def gerar_link_comentario(topico: dict, canal: str = "post") -> str:
    return (
        f"https://global-engenharia.com/ecosystem?utm_source=linkedin&utm_medium=organic"
        f"&utm_campaign={topico['utm']}&utm_content={canal}"
    )


async def escolher_variacao(pesos_topico: dict[str, float] | None = None) -> dict:
    """Picks the next unused (topic, hook) combo. When all 200 have been used,
    the cycle resets. If pesos_topico (topic_id -> engagement weight) is
    given, candidates are drawn proportionally to weight instead of uniformly
    — topics that performed better historically get picked more often."""
    used = _load_used()
    all_ids = [_combo_id(ti, hi) for ti in range(len(TOPICS)) for hi in range(len(HOOKS))]
    available = [cid for cid in all_ids if cid not in used]
    if not available:
        _reset_used()
        available = all_ids

    if pesos_topico:
        weights = [max(pesos_topico.get(cid.split("::")[0], 1.0), 0.1) for cid in available]
        chosen = random.choices(available, weights=weights, k=1)[0]
    else:
        chosen = random.choice(available)

    topic_id, hook_idx = chosen.split("::")
    hook_idx = int(hook_idx)
    topico = next(t for t in TOPICS if t["id"] == topic_id)
    texto = HOOKS[hook_idx](topico)

    proof_agent = _LIVE_PROOF_AGENTS.get(topic_id)
    if proof_agent:
        live = await ask_real_architecture(proof_agent, _LIVE_PROOF_QUERY)
        if live:
            texto += f"\n\nExemplo real, agora mesmo: \"{live.strip()[:220]}\""

    _mark_used(chosen)

    return {
        "combo_id": chosen,
        "topico": topico,
        "hook_index": hook_idx,
        "texto": texto,
        "link_comentario": gerar_link_comentario(topico),
        "gerado_em": datetime.utcnow().isoformat(),
    }


def total_variacoes() -> int:
    return len(TOPICS) * len(HOOKS)
