import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TrustScorer:
    def __init__(self, history_path: str | None = None):
        self.history_path = Path(history_path) if history_path else None
        self.scores: dict[str, dict[str, Any]] = {
            "spec_analyst": {"score": 0.85, "total_reviews": 0, "approved": 0},
            "procurement": {"score": 0.80, "total_reviews": 0, "approved": 0},
            "inventory": {"score": 0.82, "total_reviews": 0, "approved": 0},
            "logistics": {"score": 0.78, "total_reviews": 0, "approved": 0},
            "field_execution": {"score": 0.75, "total_reviews": 0, "approved": 0},
            "bim_coordinator": {"score": 0.70, "total_reviews": 0, "approved": 0},
            "requirements_analyst": {"score": 0.80, "total_reviews": 0, "approved": 0},
            "engineering_assistant": {"score": 0.85, "total_reviews": 0, "approved": 0},
            "work_synopsis": {"score": 0.75, "total_reviews": 0, "approved": 0},
            "photo_intelligence": {"score": 0.70, "total_reviews": 0, "approved": 0},
            "rfi_creation": {"score": 0.78, "total_reviews": 0, "approved": 0},
            "compliance": {"score": 0.80, "total_reviews": 0, "approved": 0},
        }
        if self.history_path and self.history_path.exists():
            self._load()

    def get_score(self, agent_id: str) -> float:
        data = self.scores.get(agent_id, {})
        return data.get("score", 0.5)

    def record_review(self, agent_id: str, approved: bool):
        if agent_id not in self.scores:
            self.scores[agent_id] = {"score": 0.5, "total_reviews": 0, "approved": 0}
        data = self.scores[agent_id]
        data["total_reviews"] += 1
        if approved:
            data["approved"] += 1
        ratio = data["approved"] / max(data["total_reviews"], 1)
        data["score"] = round(0.3 + 0.7 * ratio, 2)
        self._save()

    def get_all_scores(self) -> dict[str, float]:
        return {aid: data["score"] for aid, data in self.scores.items()}

    def get_summary(self) -> dict[str, Any]:
        scores = self.get_all_scores()
        return {
            "average": round(sum(scores.values()) / max(len(scores), 1), 2),
            "min_agent": min(scores, key=scores.get),
            "max_agent": max(scores, key=scores.get),
            "scores": scores,
            "total_reviews": sum(d["total_reviews"] for d in self.scores.values()),
        }

    def _load(self):
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for agent_id, info in data.items():
                    if agent_id in self.scores:
                        self.scores[agent_id].update(info)
        except Exception as e:
            logger.warning("Erro ao carregar historico de trust: %s", e)

    def _save(self):
        if not self.history_path:
            return
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=2)
        except Exception as e:
            logger.warning("Erro ao salvar historico de trust: %s", e)
