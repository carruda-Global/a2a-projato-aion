import os
import logging
from datetime import datetime, timezone
from collections import defaultdict
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/pricing", tags=["pricing_optimizer"])
logger = logging.getLogger(__name__)

# ── Preços base por segmento (equilibrio conversão x margem) ─────────────────
# Estratégia: preço de entrada baixo para capturar HR/Safety e PMEs,
# preço enterprise para CFO/CTO — margeia gradativamente conforme vendas.
BASE_PRICING = {
    # Perfil entry (HR/Safety, PME BR) — fácil conversão, volume
    "entry": {
        "usd": 99,
        "brl": 399,
        "label": "Entry — NR-1 + LGPD Essencial",
        "agents": ["nr1", "lgpd", "pcmso"],
        "target_profiles": ["HR / Safety Manager", "CEO / Founder SME"],
        "target_countries": ["BR"],
    },
    # Perfil mid (Legal/Compliance, CTO) — ticket médio, alta conversão
    "mid": {
        "usd": 199,
        "brl": 990,
        "label": "Mid — Compliance Core",
        "agents": ["lgpd", "gdpr", "iso27001", "nis2"],
        "target_profiles": ["Legal/Compliance Manager", "CTO / IT Director"],
        "target_countries": ["BR", "PT", "ES", "MX", "CO", "AR"],
    },
    # Perfil pro (CFO, enterprise EU) — alto valor, menor volume
    "pro": {
        "usd": 349,
        "brl": 1749,
        "label": "Pro — EU Regulatory Pack",
        "agents": ["csrd", "dora", "nis2", "eu_ai_act", "soc2"],
        "target_profiles": ["CFO / Finance Director", "Legal/Compliance Manager"],
        "target_countries": ["DE", "FR", "NL", "IT", "ES", "PT", "BE", "SE", "PL"],
    },
    # Perfil enterprise (boardroom, M&A) — máximo valor
    "enterprise": {
        "usd": 799,
        "brl": 3990,
        "label": "Enterprise — Full Compliance Suite",
        "agents": ["all_86"],
        "target_profiles": ["CFO / Finance Director", "CEO / Founder SME"],
        "target_countries": ["US", "UK", "DE", "FR", "AE", "SG", "JP"],
    },
}

# Fatores de ajuste por país (PPP + maturidade regulatória + concorrência)
COUNTRY_PRICE_FACTOR = {
    "BR": 0.60,   # Preço em BRL, mercado sensível a preço
    "MX": 0.65,
    "CO": 0.55,
    "AR": 0.50,
    "PT": 0.80,
    "ES": 0.85,
    "IT": 0.90,
    "FR": 1.00,
    "DE": 1.05,
    "NL": 1.05,
    "BE": 1.00,
    "SE": 1.00,
    "PL": 0.75,
    "US": 1.10,
    "UK": 1.05,
    "AE": 1.20,
    "SG": 1.15,
    "JP": 1.00,
    "AU": 1.00,
    "DEFAULT": 0.90,
}

# Histórico em memória: acumula eventos de preço/conversão
_history: list[dict] = []
_conversion_by_segment: dict[str, dict] = defaultdict(lambda: {"views": 0, "conversions": 0, "revenue": 0.0})
_conversion_by_country: dict[str, dict] = defaultdict(lambda: {"views": 0, "conversions": 0, "revenue": 0.0})

# Thresholds para escalar preço
SCALE_UP_THRESHOLD = 0.15    # Se conversão > 15% → aumenta 10%
SCALE_DOWN_THRESHOLD = 0.04  # Se conversão < 4% → reduz 10%
MAX_PRICE_MULTIPLIER = 2.0   # Teto: 2x o preço base
MIN_PRICE_MULTIPLIER = 0.50  # Piso: 50% do preço base

# Multiplicador atual (começa em 1.0, ajusta sozinho)
_price_multiplier: dict[str, float] = {seg: 1.0 for seg in BASE_PRICING}


def get_price_for_visitor(country: str, profile: str) -> dict:
    """Retorna o preço otimizado para o perfil + país do visitante."""
    factor = COUNTRY_PRICE_FACTOR.get(country, COUNTRY_PRICE_FACTOR["DEFAULT"])

    # Detecta segmento pelo perfil
    segment = "mid"
    if profile in ("HR / Safety Manager",) and country == "BR":
        segment = "entry"
    elif profile in ("CFO / Finance Director",) and country not in ("BR", "MX", "CO", "AR"):
        segment = "enterprise"
    elif profile in ("Legal/Compliance Manager", "CTO / IT Director"):
        segment = "pro" if country in COUNTRY_PRICE_FACTOR and factor >= 0.85 else "mid"
    elif profile == "CEO / Founder SME":
        segment = "entry" if factor < 0.70 else "mid"

    base = BASE_PRICING[segment]
    multiplier = _price_multiplier[segment]
    optimized_usd = round(base["usd"] * factor * multiplier)
    optimized_brl = round(base["brl"] * multiplier)

    # Arredonda para preço psicológico (x9 ou x7)
    optimized_usd = _psychological_price(optimized_usd)
    optimized_brl = _psychological_price(optimized_brl, step=10)

    return {
        "segment": segment,
        "profile": profile,
        "country": country,
        "price_usd": optimized_usd,
        "price_brl": optimized_brl,
        "label": base["label"],
        "agents": base["agents"],
        "multiplier": round(multiplier, 3),
        "country_factor": factor,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _psychological_price(price: float, step: int = 1) -> int:
    """Arredonda para preço psicológico terminado em 9 ou 7."""
    if step == 10:
        base = round(price / 10) * 10
        return max(base - 1, 9)
    base = int(price)
    endings = [9, 7]
    for e in endings:
        candidate = (base // 10) * 10 + e
        if candidate <= base:
            return candidate
    return base - 1 if base > 1 else 1


def record_event(segment: str, country: str, event: str, revenue: float = 0.0) -> None:
    """Registra view ou conversão no histórico."""
    _history.append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "segment": segment,
        "country": country,
        "event": event,  # "view" | "checkout" | "paid"
        "revenue": revenue,
        "multiplier": _price_multiplier.get(segment, 1.0),
    })
    _conversion_by_segment[segment]["views" if event == "view" else "conversions"] += 1
    _conversion_by_segment[segment]["revenue"] += revenue
    _conversion_by_country[country]["views" if event == "view" else "conversions"] += 1
    _conversion_by_country[country]["revenue"] += revenue


def _adjust_prices() -> list[dict]:
    """Analisa histórico e ajusta multiplicadores automaticamente."""
    adjustments = []
    for seg, stats in _conversion_by_segment.items():
        views = stats["views"]
        convs = stats["conversions"]
        if views < 20:
            continue  # Sem dados suficientes
        rate = convs / views
        current = _price_multiplier[seg]
        if rate > SCALE_UP_THRESHOLD and current < MAX_PRICE_MULTIPLIER:
            new = min(round(current * 1.10, 3), MAX_PRICE_MULTIPLIER)
            _price_multiplier[seg] = new
            adjustments.append({"segment": seg, "action": "increase_10pct", "from": current, "to": new, "rate": round(rate, 3)})
            logger.info("[PRICING] %s: conversão %.1f%% → preço +10%% (%.2f→%.2f)", seg, rate*100, current, new)
        elif rate < SCALE_DOWN_THRESHOLD and current > MIN_PRICE_MULTIPLIER:
            new = max(round(current * 0.90, 3), MIN_PRICE_MULTIPLIER)
            _price_multiplier[seg] = new
            adjustments.append({"segment": seg, "action": "decrease_10pct", "from": current, "to": new, "rate": round(rate, 3)})
            logger.info("[PRICING] %s: conversão %.1f%% → preço -10%% (%.2f→%.2f)", seg, rate*100, current, new)
    return adjustments


def _detect_patterns() -> list[dict]:
    """Detecta padrões no histórico para tomada de decisão."""
    patterns = []
    if len(_history) < 10:
        return [{"pattern": "insufficient_data", "message": "Menos de 10 eventos registrados — continue acumulando dados"}]

    # Padrão: país com maior receita
    top_country = max(_conversion_by_country.items(), key=lambda x: x[1]["revenue"], default=(None, {}))
    if top_country[0]:
        patterns.append({"pattern": "top_revenue_country", "country": top_country[0], "revenue": top_country[1]["revenue"], "action": "Aumentar orçamento SDR + ads neste país"})

    # Padrão: segmento com melhor conversão
    best_seg = max(
        ((s, d["conversions"] / max(d["views"], 1)) for s, d in _conversion_by_segment.items() if d["views"] > 0),
        key=lambda x: x[1], default=(None, 0)
    )
    if best_seg[0]:
        patterns.append({"pattern": "best_converting_segment", "segment": best_seg[0], "rate": round(best_seg[1], 3), "action": f"Priorizar tráfego para segmento '{best_seg[0]}'"})

    # Padrão: segmento com preço muito alto (baixa conversão)
    for seg, stats in _conversion_by_segment.items():
        if stats["views"] > 20 and stats["conversions"] == 0:
            patterns.append({"pattern": "zero_conversion", "segment": seg, "views": stats["views"], "action": f"Reduzir preço do segmento '{seg}' ou revisar oferta"})

    return patterns


async def auto_job_price_optimizer() -> None:
    """Roda a cada 24h: analisa histórico e ajusta preços automaticamente."""
    adjustments = _adjust_prices()
    patterns = _detect_patterns()
    logger.info("[PRICING] Ciclo de otimização: %d ajustes, %d padrões detectados", len(adjustments), len(patterns))
    for a in adjustments:
        logger.info("[PRICING] Ajuste: %s", a)
    for p in patterns:
        logger.info("[PRICING] Padrão: %s", p)


# ── Endpoints ────────────────────────────────────────────────────────────────

class VisitorRequest(BaseModel):
    country: str = "BR"
    profile: str = "HR / Safety Manager"

class EventRequest(BaseModel):
    segment: str
    country: str
    event: str  # "view" | "checkout" | "paid"
    revenue: float = 0.0


@router.post("/quote")
async def get_quote(req: VisitorRequest):
    """Retorna preço otimizado para o perfil + país do visitante."""
    return get_price_for_visitor(req.country, req.profile)


@router.post("/event")
async def record_pricing_event(req: EventRequest):
    """Registra evento de conversão no histórico."""
    record_event(req.segment, req.country, req.event, req.revenue)
    return {"recorded": True, "history_size": len(_history)}


@router.get("/analysis")
async def pricing_analysis():
    """Análise completa: histórico, padrões, multiplicadores atuais e preços por segmento."""
    adjustments = _adjust_prices()
    patterns = _detect_patterns()
    current_prices = {
        seg: {
            "multiplier": _price_multiplier[seg],
            "price_usd": _psychological_price(BASE_PRICING[seg]["usd"] * _price_multiplier[seg]),
            "price_brl": _psychological_price(BASE_PRICING[seg]["brl"] * _price_multiplier[seg], step=10),
            "label": BASE_PRICING[seg]["label"],
            "conversions": _conversion_by_segment[seg]["conversions"],
            "views": _conversion_by_segment[seg]["views"],
            "revenue_usd": round(_conversion_by_segment[seg]["revenue"], 2),
        }
        for seg in BASE_PRICING
    }
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_prices": current_prices,
        "multipliers": _price_multiplier,
        "adjustments_this_cycle": adjustments,
        "patterns": patterns,
        "by_country": dict(_conversion_by_country),
        "history_size": len(_history),
        "strategy": {
            "scale_up_at": f">{SCALE_UP_THRESHOLD*100:.0f}% conversão",
            "scale_down_at": f"<{SCALE_DOWN_THRESHOLD*100:.0f}% conversão",
            "max_multiplier": MAX_PRICE_MULTIPLIER,
            "min_multiplier": MIN_PRICE_MULTIPLIER,
            "note": "Preços aumentam 10% a cada ciclo com conversão alta; reduzem 10% com baixa. Gradual e automático.",
        },
    }


@router.get("/matrix")
async def price_matrix():
    """Tabela de preços por país e segmento — para exibir no dashboard."""
    matrix = []
    profiles = list({p for seg in BASE_PRICING.values() for p in seg["target_profiles"]})
    countries_sample = ["BR", "US", "DE", "PT", "MX", "AE"]
    for country in countries_sample:
        for profile in profiles:
            price = get_price_for_visitor(country, profile)
            matrix.append(price)
    return {"matrix": matrix, "total": len(matrix)}
