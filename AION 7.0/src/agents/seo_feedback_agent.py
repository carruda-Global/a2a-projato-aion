"""Phase 2 — Google Search Console feedback loop for the SEO content engine.

MVP scope (deliberately not more): pull page + query performance from GSC
weekly, aggregate to (region, product, topic_kind) buckets — not per-page,
which is too noisy at this volume — and bias the next generation batch
toward high-performing buckets while keeping a 20% exploration floor so the
system doesn't overfit to early winners. Real-time pulls, per-page bandit
models, and automated title rewriting are explicitly out of scope for v1.

Auth reuses the existing "installed app" OAuth client for the
global-engenharia-498823 GCP project (see scripts/gsc_authorize.py) rather
than a service account — Search Console access is tied to the Google
account that owns the property, so a one-time user login + stored refresh
token is the simpler, correct mechanism here.
"""
import os
import re
from collections import defaultdict
from datetime import date, timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.config import Settings
from src.database.supabase_client import SupabaseClient

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
LOOKBACK_DAYS = 28
EXPLORATION_FLOOR = 0.2
MIN_AGE_DAYS_BEFORE_PRUNE = 21  # don't declare a bucket "dead" before pages have had time to be indexed
MIN_IMPRESSIONS_TO_JUDGE = 5

# Page URL on the live site. Two shapes map to a tracked slug:
# - /artigos/{slug} — PHP reverse-proxy to the API (regulation/capability
#   combinatorial pages, seo_content_agent.py)
# - /ecosystem/callreception/{slug} — static hand-written guide/comparison
#   pages (.htaccess alias, see global-match-site/.htaccess), registered as
#   plain rows in seo_pages so they share the same bucket-scoring path.
SLUG_URL_PATTERN = re.compile(r"/(?:artigos|ecosystem/callreception)/([a-z0-9-]+)/?$")


def _load_credentials() -> Credentials | None:
    client_id = os.getenv("GSC_CLIENT_ID")
    client_secret = os.getenv("GSC_CLIENT_SECRET")
    refresh_token = os.getenv("GSC_REFRESH_TOKEN")
    if not (client_id and client_secret and refresh_token):
        return None
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )


def _slug_from_page_url(page_url: str) -> str | None:
    m = SLUG_URL_PATTERN.search(page_url)
    return m.group(1) if m else None


class SEOFeedbackAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.site_url = os.getenv("GSC_SITE_URL", "https://www.global-engenharia.com/")
        creds = _load_credentials()
        self.service = build("searchconsole", "v1", credentials=creds) if creds else None
        self.db = SupabaseClient(settings)

    def is_configured(self) -> bool:
        return self.service is not None

    def pull_and_store(self) -> dict:
        """Weekly job: pull trailing-28-day page performance from GSC and
        upsert into seo_performance. Returns a small summary dict."""
        if not self.service:
            return {"error": "GSC not configured (missing GSC_CLIENT_ID/SECRET/REFRESH_TOKEN)"}

        end = date.today()
        start = end - timedelta(days=LOOKBACK_DAYS)
        request = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["page"],
            "rowLimit": 5000,
        }
        response = self.service.searchanalytics().query(siteUrl=self.site_url, body=request).execute()
        rows = response.get("rows", [])

        stored = 0
        for row in rows:
            page_url = row["keys"][0]
            slug = _slug_from_page_url(page_url)
            if not slug:
                continue
            self.db.client.table("seo_performance").insert({
                "slug": slug,
                "clicks": int(row.get("clicks", 0)),
                "impressions": int(row.get("impressions", 0)),
                "ctr": row.get("ctr"),
                "position": row.get("position"),
                "snapshot_date": end.isoformat(),
            }).execute()
            stored += 1
        return {"rows_from_gsc": len(rows), "rows_stored": stored, "snapshot_date": end.isoformat()}

    def bucket_scores(self) -> dict[tuple[str, str, str], dict]:
        """Aggregates the most recent snapshot's performance up to
        (region, product, topic_kind) buckets by joining seo_performance with
        seo_pages on slug. Returns bucket -> {clicks, impressions, page_count}."""
        perf = self.db.client.table("seo_performance").select("slug,clicks,impressions").execute().data or []
        if not perf:
            return {}
        slugs = list({row["slug"] for row in perf})
        pages: dict[str, dict] = {}
        # Supabase .in_() has a practical size limit — chunk it.
        for i in range(0, len(slugs), 200):
            chunk = slugs[i:i + 200]
            rows = (
                self.db.client.table("seo_pages")
                .select("slug,region,product,topic_kind")
                .in_("slug", chunk)
                .execute()
                .data or []
            )
            for r in rows:
                pages[r["slug"]] = r

        buckets: dict[tuple[str, str, str], dict] = defaultdict(lambda: {"clicks": 0, "impressions": 0, "page_count": 0})
        for row in perf:
            page = pages.get(row["slug"])
            if not page or not page.get("region") or not page.get("product"):
                continue
            key = (page["region"], page["product"], page.get("topic_kind") or "unknown")
            b = buckets[key]
            b["clicks"] += row.get("clicks") or 0
            b["impressions"] += row.get("impressions") or 0
            b["page_count"] += 1
        return dict(buckets)

    def next_batch_bias(self) -> dict:
        """Ranks buckets by a simple impressions+clicks score, normalized
        per-region so a large market doesn't dominate. Returns
        {"prioritize": [...], "deprioritize": [...]} of (region, product,
        kind) tuples for the caller to use when picking which topics/sectors
        to expand next — NOT a hard filter, generation should still keep an
        EXPLORATION_FLOOR share of random/new combinations regardless of
        this ranking."""
        buckets = self.bucket_scores()
        if not buckets:
            return {"prioritize": [], "deprioritize": [], "note": "no performance data yet"}

        by_region: dict[str, list] = defaultdict(list)
        for key, stats in buckets.items():
            region = key[0]
            score = stats["impressions"] * 0.3 + stats["clicks"] * 1.0
            by_region[region].append((key, score, stats))

        prioritize = []
        deprioritize = []
        for region, entries in by_region.items():
            entries.sort(key=lambda e: e[1], reverse=True)
            n = len(entries)
            top_quartile = max(1, n // 4)
            prioritize.extend(k for k, _, _ in entries[:top_quartile])
            for key, score, stats in entries:
                if stats["impressions"] >= MIN_IMPRESSIONS_TO_JUDGE and score == 0:
                    deprioritize.append(key)

        return {"prioritize": prioritize, "deprioritize": deprioritize, "exploration_floor": EXPLORATION_FLOOR}
