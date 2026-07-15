"""Single source of truth for SEO page topics — the combinatorial input to
seo_content_agent.py and scripts/generate_seo_pages.py.

Repurposed (2026-07) to sell exclusively the AI Voice Receptionist product —
the 19-Copilot compliance catalog generated zero confirmed real revenue this
session, while "ai receptionist" showed real, growing Google search demand
(8,100/mo, +84% YoY) validated via Keyword Planner. Every topic below is an
industry vertical for the Voice Receptionist ("AI Receptionist for Dental
Clinics", "for Law Firms", etc.) rather than a regulation, targeting the 4
countries with real, validated demand and Google Ads spend: US, UK, CA, AU.
"""
from dataclasses import dataclass
from typing import Literal

TopicKind = Literal["regulation", "capability"]

BASE_URL = "https://engenheiro-producao-ai.onrender.com"
VOICE_RECEPTIONIST_CHECKOUT = "https://buy.stripe.com/28E4gBa6Ibov2PicOsg7e0x"


@dataclass(frozen=True)
class ProductInfo:
    display_name: str
    is_public: bool = True


# Only real, live, customer-facing product surfaces. Do NOT add
# master_orchestrator / quality_critic / regulatory_watch /
# universal_governance / workforce_orchestrator here — those are internal
# infrastructure agents, never sold standalone, never a SEO target.
PRODUCTS: dict[str, ProductInfo] = {
    "voice_receptionist": ProductInfo("AI Voice Receptionist"),
}


@dataclass(frozen=True)
class Topic:
    key: str
    kind: TopicKind
    product: str
    nome: str
    norma: str  # regulation name, or workflow name for capability topics
    dor: str  # pain point / consequence the copy leads with
    stripe_link: str  # real Stripe checkout, or a live product page URL
    markets: tuple[str, ...]
    # Per-market overrides — falls back to SECTORS_BY_REGION/SIZES_BY_REGION
    # when a market isn't present in the override dict.
    sectors_override: dict[str, tuple[str, ...]] | None = None
    sizes_override: dict[str, tuple[str, ...]] | None = None

    def __post_init__(self):
        info = PRODUCTS.get(self.product)
        if info is None:
            raise ValueError(f"Topic {self.key!r} references unknown product {self.product!r}")
        if not info.is_public:
            raise ValueError(f"Topic {self.key!r} references non-public product {self.product!r}")

    def sectors_for(self, market: str) -> tuple[str, ...]:
        if self.sectors_override and market in self.sectors_override:
            return self.sectors_override[market]
        return SECTORS_BY_REGION[market]

    def sizes_for(self, market: str) -> dict[str, str]:
        if self.sizes_override and market in self.sizes_override:
            keys = self.sizes_override[market]
            return {k: SIZES_BY_REGION[market][k] for k in keys}
        return SIZES_BY_REGION[market]


# ── Single source of truth for sector/size vocabulary per region ──────────
# Industry verticals that actually search for and buy an AI phone
# receptionist — not compliance sectors. Same 4 countries validated this
# session via real Google Ads Keyword Planner data (US/UK/CA/AU).

SECTORS_BY_REGION: dict[str, list[str]] = {
    "US": ["dental-clinics", "law-firms", "real-estate-agencies", "home-services", "salons-and-spas", "medical-clinics", "auto-repair-shops", "restaurants"],
    "UK": ["dental-clinics", "law-firms", "estate-agents", "home-services", "salons-and-spas", "medical-clinics", "auto-repair-shops"],
    "CA": ["dental-clinics", "law-firms", "real-estate-agencies", "home-services", "salons-and-spas", "medical-clinics"],
    "AU": ["dental-clinics", "law-firms", "real-estate-agencies", "home-services", "salons-and-spas", "medical-clinics"],
}

SIZES_BY_REGION: dict[str, dict[str, str]] = {
    "US": {"solo": "solo practice", "small": "small business", "multi-location": "multi-location business"},
    "UK": {"solo": "sole trader", "small": "small business", "multi-location": "multi-location business"},
    "CA": {"solo": "solo practice", "small": "small business", "multi-location": "multi-location business"},
    "AU": {"solo": "sole trader", "small": "small business", "multi-location": "multi-location business"},
}

LANGUAGE_BY_REGION: dict[str, str] = {
    "US": "English", "UK": "English", "CA": "English", "AU": "English",
}


# ── Regulation topics — retired along with the compliance product line.
# Kept as an empty list (not deleted) so any stray import of
# REGULATION_TOPICS doesn't crash; ALL_TOPICS below no longer includes it.
REGULATION_TOPICS: list[Topic] = []


# ── Capability topics — one per Voice Receptionist feature, combined with
# the industry verticals above via topics_for_market() + the existing
# sector/size combinatorial loop in seo_content_agent.py. ──────────────────
CAPABILITY_TOPICS: list[Topic] = [
    Topic(
        key="ai-receptionist-24-7-answering", kind="capability", product="voice_receptionist",
        nome="24/7 AI Phone Answering", norma="AI Voice Receptionist — Always-On Answering",
        dor="missed calls going straight to voicemail and lost to a competitor",
        stripe_link=VOICE_RECEPTIONIST_CHECKOUT,
        markets=("US", "UK", "CA", "AU"),
    ),
    Topic(
        key="missed-call-text-back", kind="capability", product="voice_receptionist",
        nome="Missed-Call Text-Back", norma="AI Voice Receptionist — Instant Text-Back",
        dor="a missed call with no follow-up is a lost customer",
        stripe_link=VOICE_RECEPTIONIST_CHECKOUT,
        markets=("US", "UK", "CA", "AU"),
    ),
    Topic(
        key="ai-lead-capture-by-phone", kind="capability", product="voice_receptionist",
        nome="AI Phone Lead Capture", norma="AI Voice Receptionist — Lead Capture",
        dor="phone leads never logged anywhere, no follow-up, no record",
        stripe_link=VOICE_RECEPTIONIST_CHECKOUT,
        markets=("US", "UK", "CA", "AU"),
    ),
    Topic(
        key="ai-appointment-info-line", kind="capability", product="voice_receptionist",
        nome="AI Appointment Info Line", norma="AI Voice Receptionist — Hours & Booking Info",
        dor="staff interrupted constantly just to repeat hours and availability",
        stripe_link=VOICE_RECEPTIONIST_CHECKOUT,
        markets=("US", "UK", "CA", "AU"),
    ),
]


ALL_TOPICS: list[Topic] = REGULATION_TOPICS + CAPABILITY_TOPICS

# Markets the scheduled/bulk generation loop iterates over — the 4 countries
# with real, Keyword-Planner-validated "ai receptionist" search demand.
ALL_MARKETS: tuple[str, ...] = ("US", "UK", "CA", "AU")


def topics_for_market(market: str) -> list[Topic]:
    return [t for t in ALL_TOPICS if market in t.markets]
