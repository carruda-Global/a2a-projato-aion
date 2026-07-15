from typing import Any
from collections import defaultdict
from datetime import datetime, date


class BudgetController:
    def __init__(self):
        self.per_agent_budget: dict[str, float] = defaultdict(lambda: 100.0)
        self.per_tenant_budget: dict[str, float] = defaultdict(lambda: 1000.0)
        self.agent_spent: dict[str, float] = defaultdict(float)
        self.tenant_spent: dict[str, float] = defaultdict(float)
        self.daily_reset: dict[str, date] = {}

    def check_agent_budget(self, agent_id: str, task_cost: float = 0.10) -> bool:
        return self.agent_spent[agent_id] + task_cost <= self.per_agent_budget[agent_id]

    def check_tenant_budget(self, tenant_id: str, task_cost: float = 0.10) -> bool:
        return self.tenant_spent[tenant_id] + task_cost <= self.per_tenant_budget[tenant_id]

    def spend(self, agent_id: str, tenant_id: str, cost: float) -> None:
        self.agent_spent[agent_id] += cost
        self.tenant_spent[tenant_id] += cost

    def get_usage(self, agent_id: str = None, tenant_id: str = None) -> dict:
        result = {}
        if agent_id:
            result["agent"] = {
                "budget": self.per_agent_budget[agent_id],
                "spent": round(self.agent_spent[agent_id], 2),
                "remaining": round(self.per_agent_budget[agent_id] - self.agent_spent[agent_id], 2),
                "usage_pct": round(self.agent_spent[agent_id] / self.per_agent_budget[agent_id] * 100, 1) if self.per_agent_budget[agent_id] > 0 else 0,
            }
        if tenant_id:
            result["tenant"] = {
                "budget": self.per_tenant_budget[tenant_id],
                "spent": round(self.tenant_spent[tenant_id], 2),
                "remaining": round(self.per_tenant_budget[tenant_id] - self.tenant_spent[tenant_id], 2),
                "usage_pct": round(self.tenant_spent[tenant_id] / self.per_tenant_budget[tenant_id] * 100, 1) if self.per_tenant_budget[tenant_id] > 0 else 0,
            }
        return result
