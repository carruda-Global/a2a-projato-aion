import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

DECISION_MAKER_TITLES = [
    "ceo", "cto", "cfo", "coo", "cmo", "cio", "vp", "vice president",
    "director", "head", "founder", "owner", "partner", "president",
    "chief", "svp", "evp", "managing director",
]

INFLUENCER_TITLES = [
    "manager", "coordinator", "supervisor", "lead", "senior",
    "specialist", "analyst", "consultant",
]

HIGH_BUDGET_INDUSTRIES = [
    "technology", "software", "fintech", "healthtech", "biotech",
    "financial services", "banking", "insurance", "consulting",
    "energy", "oil", "gas", "mining", "engineering",
    "construction", "real estate", "manufacturing",
    "pharmaceutical", "logistics", "telecom",
]

REGULATORY_INDUSTRIES = [
    "healthcare", "financial services", "banking", "insurance",
    "pharmaceutical", "energy", "oil", "gas", "construction",
    "manufacturing", "mining", "legal",
]


@dataclass
class BANTScores:
    budget: float = 0
    authority: float = 0
    need: float = 0
    timeline: float = 0

    @property
    def total(self) -> float:
        return round(self.budget + self.authority + self.need + self.timeline, 1)

    @property
    def label(self) -> str:
        if self.total >= 80:
            return "hot"
        elif self.total >= 60:
            return "warm"
        elif self.total >= 40:
            return "tepid"
        return "cold"

    def to_dict(self) -> dict:
        return {
            "budget": self.budget,
            "authority": self.authority,
            "need": self.need,
            "timeline": self.timeline,
            "total": self.total,
            "label": self.label,
        }


def score_title(title: str) -> float:
    if not title:
        return 0
    t = title.lower()
    for pattern in DECISION_MAKER_TITLES:
        if re.search(rf"\b{pattern}\b", t):
            return 30
    for pattern in INFLUENCER_TITLES:
        if re.search(rf"\b{pattern}\b", t):
            return 15
    return 5


def score_industry(industry: str) -> float:
    if not industry:
        return 10
    ind = industry.lower()
    for hb in HIGH_BUDGET_INDUSTRIES:
        if hb in ind:
            return 25
    return 10


def score_company_size(size: str) -> float:
    if not size:
        return 5
    s = size.lower()
    if "10000" in s or "10,000" in s:
        return 25
    if "5000" in s or "5,000" in s:
        return 25
    if "1000" in s or "1,000" in s:
        return 20
    if "500" in s:
        return 15
    if "200" in s:
        return 10
    if "50" in s:
        return 5
    if "10" in s or "small" in s:
        return 3
    return 10


def score_regulatory_need(industry: str, title: str, summary: str = "") -> float:
    need = 0
    ind = (industry or "").lower()
    tit = (title or "").lower()
    summ = (summary or "").lower()

    for reg in REGULATORY_INDUSTRIES:
        if reg in ind:
            need += 15
            break

    regulatory_keywords = [
        "lgpd", "regulatory", "compliance", "nr-", "norma", "seguranca",
        "quality", "iso", "audit", "risk", "gestao", "documentacao",
    ]
    for kw in regulatory_keywords:
        if kw in summ or kw in tit:
            need += 5

    return min(need, 25)


def score_engagement(posts: list | None = None) -> float:
    if not posts:
        return 0
    score = 0
    for post in posts[:10]:
        reactions = post.get("reactions", post.get("likes", 0))
        comments = post.get("comments", 0)
        if isinstance(reactions, (int, float)):
            score += min(reactions * 0.5, 5)
        if isinstance(comments, (int, float)):
            score += min(comments * 1, 3)
    return min(score, 20)


def score_bant(
    title: str | None = None,
    industry: str | None = None,
    company_size: str | None = None,
    summary: str | None = None,
    recent_posts: list | None = None,
    source: str | None = None,
) -> BANTScores:
    budget = score_industry(industry) + score_company_size(company_size)
    authority = score_title(title)
    need = score_regulatory_need(industry, title, summary)
    timeline = 0

    if source == "linkedin":
        timeline += 5
    if any(kw in (summary or "").lower() for kw in ["urgent", "looking for", "need", "help", "problem"]):
        timeline += 10
    if any(kw in (industry or "").lower() for kw in REGULATORY_INDUSTRIES):
        timeline += 10

    timeline += score_engagement(recent_posts)

    budget = min(budget, 25)
    authority = min(authority, 30)
    need = min(need, 25)
    timeline = min(timeline, 20)

    return BANTScores(budget=budget, authority=authority, need=need, timeline=timeline)
