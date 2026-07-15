from typing import Any


class PerformanceSelector:
    def __init__(self, performance_weight: float = 0.7, novelty_weight: float = 0.3):
        self.performance_weight = performance_weight
        self.novelty_weight = novelty_weight

    def select(self, agents: list[dict], top_n: int = 3) -> list[dict]:
        scored = []
        for agent in agents:
            perf = agent.get("success_rate", 0)
            novelty = agent.get("novelty", 0)
            score = (
                self.performance_weight * perf
                + self.novelty_weight * novelty
            )
            scored.append((score, agent))

        scored.sort(key=lambda x: -x[0])
        return [a for _, a in scored[:top_n]]

    def calculate_score(self, agent_data: dict) -> float:
        perf = agent_data.get("success_rate", 0)
        novelty = agent_data.get("novelty", 0)
        return self.performance_weight * perf + self.novelty_weight * novelty
