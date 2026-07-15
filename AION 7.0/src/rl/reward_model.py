from typing import Any


class RewardModel:
    def __init__(self):
        self.weights = {
            "success_rate": 0.4,
            "response_time": 0.2,
            "cost_efficiency": 0.3,
            "novelty": 0.1,
        }

    def calculate(self, agent_result: dict) -> float:
        if not agent_result:
            return 0.0

        success = 1.0 if agent_result.get("success", False) else 0.0
        response_time = agent_result.get("response_time", 0)
        cost = agent_result.get("cost", 0)
        budget = agent_result.get("budget_per_task", 0.10)

        success_score = success
        time_score = max(0, 1 - (response_time / 10.0)) if response_time > 0 else 0.5
        cost_score = max(0, 1 - (cost / budget)) if budget > 0 else 0.5
        novelty_score = agent_result.get("novelty", 0)

        total = (
            self.weights["success_rate"] * success_score
            + self.weights["response_time"] * time_score
            + self.weights["cost_efficiency"] * cost_score
            + self.weights["novelty"] * novelty_score
        )

        return round(total, 4)

    def multidimensional(self, results: list[dict]) -> dict:
        if not results:
            return {}

        return {
            "avg_success": sum(1 for r in results if r.get("success")) / len(results),
            "avg_response_time": sum(r.get("response_time", 0) for r in results) / len(results),
            "avg_cost": sum(r.get("cost", 0) for r in results) / len(results),
            "avg_reward": sum(self.calculate(r) for r in results) / len(results),
            "total_results": len(results),
        }
