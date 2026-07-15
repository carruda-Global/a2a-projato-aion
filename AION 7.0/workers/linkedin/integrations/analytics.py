import logging
from datetime import datetime, timedelta
from collections import defaultdict
from .config import LinkedInConfig
from .oauth import LinkedInOAuth
from .tools import LinkedInTools

logger = logging.getLogger(__name__)


class LinkedInAnalytics:
    def __init__(self, config: LinkedInConfig, oauth: LinkedInOAuth):
        self.config = config
        self.oauth = oauth
        self.tools = LinkedInTools(config, oauth)
        self._history: list[dict] = []

    async def get_post_performance(self, post_id: str) -> dict:
        analytics = await self.tools.get_post_analytics(post_id)
        post = await self.tools.get_post(post_id)
        return {
            "post_id": post_id,
            "post_content": post.get("commentary", "")[:200],
            "analytics": analytics,
            "retrieved_at": datetime.now().isoformat(),
        }

    async def get_recent_engagement(
        self, post_ids: list[str], since_hours: int = 24
    ) -> dict:
        results = {}
        for pid in post_ids:
            data = await self.get_post_performance(pid)
            results[pid] = data
        summary = {
            "total_posts": len(post_ids),
            "post_ids": post_ids,
            "since_hours": since_hours,
            "details": results,
            "retrieved_at": datetime.now().isoformat(),
        }
        return summary

    async def get_best_performing_posts(
        self, post_ids: list[str], metric: str = "likeCount", top_n: int = 5
    ) -> list[dict]:
        scored = []
        for pid in post_ids:
            data = await self.get_post_performance(pid)
            analytics = data.get("analytics", {})
            elements = analytics.get("elements", [])
            for elem in elements:
                statistics = elem.get("statisticalData", {})
                if metric == "likeCount":
                    score = statistics.get("likeCount", 0)
                elif metric == "commentCount":
                    score = statistics.get("commentCount", 0)
                elif metric == "shareCount":
                    score = statistics.get("shareCount", 0)
                elif metric == "impressionCount":
                    score = statistics.get("impressionCount", 0)
                else:
                    score = 0
                scored.append({
                    "post_id": pid,
                    "score": score,
                    "data": data,
                })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_n]

    async def generate_weekly_report(self, post_ids: list[str]) -> dict:
        total_likes = 0
        total_comments = 0
        total_shares = 0
        total_impressions = 0
        for pid in post_ids:
            data = await self.get_post_performance(pid)
            analytics = data.get("analytics", {})
            elements = analytics.get("elements", [])
            for elem in elements:
                stats = elem.get("statisticalData", {})
                total_likes += stats.get("likeCount", 0)
                total_comments += stats.get("commentCount", 0)
                total_shares += stats.get("shareCount", 0)
                total_impressions += stats.get("impressionCount", 0)
        n = max(len(post_ids), 1)
        return {
            "period": "weekly",
            "total_posts": len(post_ids),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_impressions": total_impressions,
            "avg_likes": round(total_likes / n, 1),
            "avg_comments": round(total_comments / n, 1),
            "avg_shares": round(total_shares / n, 1),
            "avg_impressions": round(total_impressions / n, 1),
            "generated_at": datetime.now().isoformat(),
        }

    def track_post(self, post_data: dict):
        self._history.append({
            **post_data,
            "tracked_at": datetime.now().isoformat(),
        })

    def get_history(self, limit: int = 50) -> list[dict]:
        return self._history[-limit:]

    async def get_audience_growth_rate(
        self, current_followers: int, previous_followers: int
    ) -> dict:
        if previous_followers <= 0:
            return {"growth_rate": 0, "status": "insufficient_data"}
        growth = ((current_followers - previous_followers) / previous_followers) * 100
        return {
            "current_followers": current_followers,
            "previous_followers": previous_followers,
            "growth_rate": round(growth, 2),
            "absolute_growth": current_followers - previous_followers,
            "status": "growing" if growth > 0 else "declining" if growth < 0 else "stable",
        }

    async def content_mix_analysis(self, post_ids: list[str]) -> dict:
        types = defaultdict(int)
        for pid in post_ids:
            data = await self.tools.get_post(pid)
            commentary = data.get("commentary", "")
            link = data.get("content", {}).get("article", {})
            if link.get("source"):
                types["link"] += 1
            elif len(commentary) > 500:
                types["long_form"] += 1
            else:
                types["short_form"] += 1
        total = sum(types.values()) or 1
        return {
            "total_analyzed": len(post_ids),
            "content_mix": {k: {"count": v, "percentage": round(v / total * 100, 1)} for k, v in types.items()},
        }
