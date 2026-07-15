from typing import Any
from collections import defaultdict
import numpy as np


class GlobalRL:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.learning_rate = 0.0005
        self.discount_factor = 0.9
        self.agent_rewards: dict[str, list[float]] = defaultdict(list)
        self.global_rewards: list[float] = []
        self.episode_count = 0
        self.q_table: dict[str, dict[str, float]] = defaultdict(
            lambda: {"cooperate": 0.5, "compete": 0.5, "ignore": 0.0}
        )

    def update(self, results: dict) -> None:
        self.episode_count += 1

        for agent_id, result in results.items():
            reward = self._calculate_reward(result)
            self.agent_rewards[agent_id].append(reward)

            if agent_id in self.q_table:
                for action in self.q_table[agent_id]:
                    td_error = reward - self.q_table[agent_id][action]
                    self.q_table[agent_id][action] += self.learning_rate * td_error

        global_reward = np.mean([r for r in results.values() if isinstance(r, dict) and r.get("success", False)])
        self.global_rewards.append(global_reward)

        if len(self.global_rewards) > 1000:
            self.global_rewards = self.global_rewards[-1000:]

    def _calculate_reward(self, result: Any) -> float:
        if isinstance(result, Exception):
            return -1.0
        if isinstance(result, dict):
            success = result.get("success", False)
            response_time = result.get("response_time", 0)
            confidence = result.get("confidence", 1.0)

            base = 1.0 if success else -0.5
            time_penalty = max(0, (response_time - 5.0) * 0.1) if response_time > 5.0 else 0
            confidence_bonus = confidence * 0.2

            return base - time_penalty + confidence_bonus
        return 0.5

    def select_action(self, agent_id: str) -> str:
        q_values = self.q_table[agent_id]
        return max(q_values, key=q_values.get)

    def get_stats(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "episodes": self.episode_count,
            "agents_tracked": len(self.agent_rewards),
            "avg_global_reward": round(np.mean(self.global_rewards[-100:]), 4) if self.global_rewards else 0,
            "q_table_size": len(self.q_table),
        }
