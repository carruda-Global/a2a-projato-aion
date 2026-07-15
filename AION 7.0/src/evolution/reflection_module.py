from typing import Any
from datetime import datetime, timezone
from collections import Counter


class ReflectionModule:
    def __init__(self):
        self.pattern_history: list[dict] = []
        self.insights: list[dict] = []

    def analyze_patterns(self, recent_results: list[dict]) -> dict:
        if not recent_results:
            return {"patterns": [], "insights": []}

        success_rates = Counter()
        error_types = Counter()
        slow_agents = []

        for r in recent_results:
            agent_id = r.get("agent_id", "unknown")
            success = r.get("success", False)
            response_time = r.get("response_time", 0)

            if success:
                success_rates[agent_id] += 1
            else:
                error_type = r.get("error", "unknown")[:50]
                error_types[error_type] += 1

            if response_time > 5.0:
                slow_agents.append(agent_id)

        insight = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_executions": len(recent_results),
            "top_errors": error_types.most_common(3),
            "slow_agents": list(set(slow_agents)),
            "success_distribution": dict(success_rates.most_common(5)),
        }

        self.pattern_history.append(insight)

        if len(self.pattern_history) > 100:
            self.pattern_history = self.pattern_history[-100:]

        if error_types:
            self.insights.append({
                "timestamp": insight["timestamp"],
                "type": "error_pattern",
                "message": f"Erros mais frequentes: {error_types.most_common(1)[0][0]}",
                "severity": "high" if error_types.most_common(1)[1] > 5 else "medium",
            })

        return insight
