import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ExperienceLibrary:

    def __init__(self):
        self.experiences: Dict[str, List[Dict]] = {}
        self.max_experiences_per_agent = 100

    async def add(self, agent_id: str, context: Dict, result: Dict, score: float = 1.0) -> bool:
        if agent_id not in self.experiences:
            self.experiences[agent_id] = []

        experience = {
            "id": f"{agent_id}_{len(self.experiences[agent_id])}",
            "agent_id": agent_id,
            "context": context,
            "result": result,
            "score": score,
            "timestamp": str(datetime.now())
        }

        self.experiences[agent_id].append(experience)

        if len(self.experiences[agent_id]) > self.max_experiences_per_agent:
            self._prune(agent_id)

        return True

    async def merge(self, source_agent: str, target_agent: str) -> int:
        if source_agent not in self.experiences:
            return 0
        if target_agent not in self.experiences:
            self.experiences[target_agent] = []

        transferred = 0
        for exp in self.experiences[source_agent]:
            if exp["score"] >= 0.7:
                merged_exp = {**exp, "id": f"{target_agent}_{len(self.experiences[target_agent])}", "merged_from": source_agent}
                self.experiences[target_agent].append(merged_exp)
                transferred += 1

        return transferred

    def _prune(self, agent_id: str):
        if agent_id not in self.experiences:
            return
        self.experiences[agent_id].sort(key=lambda x: x.get("score", 0), reverse=True)
        self.experiences[agent_id] = self.experiences[agent_id][:self.max_experiences_per_agent]

    async def query(self, agent_id: str, similarity_threshold: float = 0.7) -> List[Dict]:
        if agent_id not in self.experiences:
            return []
        return [e for e in self.experiences[agent_id] if e.get("score", 0) >= similarity_threshold]

    def get_stats(self, agent_id: str) -> Dict:
        if agent_id not in self.experiences:
            return {"count": 0, "avg_score": 0}
        scores = [e.get("score", 0) for e in self.experiences[agent_id]]
        return {
            "count": len(self.experiences[agent_id]),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "max_score": max(scores) if scores else 0
        }
