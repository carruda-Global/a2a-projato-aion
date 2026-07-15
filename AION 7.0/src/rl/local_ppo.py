from typing import Any
import numpy as np


class LocalPPO:
    def __init__(self, agent_id: str, learning_rate: float = 0.001):
        self.agent_id = agent_id
        self.learning_rate = learning_rate
        self.discount_factor = 0.95
        self.clip_epsilon = 0.2
        self.policy: dict[str, float] = {}
        self.rewards: list[float] = []
        self.step_count = 0

    def select_action(self, state: dict) -> str:
        actions = ["direct", "delegate", "escalate", "skip"]
        probs = [self.policy.get(a, 0.25) for a in actions]
        probs = np.array(probs) / sum(probs)
        return np.random.choice(actions, p=probs)

    def update(self, reward: float) -> None:
        self.rewards.append(reward)
        self.step_count += 1

        if len(self.rewards) > 100:
            self.rewards = self.rewards[-100:]

        avg_reward = np.mean(self.rewards[-20:]) if len(self.rewards) >= 20 else reward
        self.policy["direct"] = 0.25 + 0.1 * avg_reward
        self.policy["delegate"] = 0.25 + 0.05 * avg_reward
        self.policy["escalate"] = 0.25 - 0.05 * avg_reward
        self.policy["skip"] = 0.25 - 0.1 * avg_reward

        total = sum(self.policy.values())
        for k in self.policy:
            self.policy[k] /= total

    def get_stats(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "steps": self.step_count,
            "avg_reward": round(np.mean(self.rewards[-20:]), 4) if self.rewards else 0,
            "policy": {k: round(v, 4) for k, v in self.policy.items()},
        }
