import tomllib
from typing import Dict, Any, Optional
from enum import Enum


class Decision(Enum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


class AbacusEngine:

    def __init__(self, policy_path: str = "config/policies.toml"):
        self.policy_path = policy_path
        self.policies = self._load_policies()

    def _load_policies(self) -> Dict[str, Any]:
        try:
            with open(self.policy_path, "rb") as f:
                return tomllib.load(f)
        except FileNotFoundError:
            return self._default_policies()

    def _default_policies(self) -> Dict[str, Any]:
        return {
            "default": {
                "data_access": {
                    "public": {"effect": "allow"},
                    "internal": {"effect": "allow"},
                    "confidential": {"effect": "ask"},
                    "restricted": {"effect": "deny"}
                },
                "tool_access": {
                    "read": {"effect": "allow"},
                    "write": {"effect": "ask"},
                    "delete": {"effect": "deny"},
                    "execute": {"effect": "ask"}
                }
            },
            "agent_specific": {}
        }

    def evaluate(self, agent_id: str, action_type: str, resource: str, context: Dict[str, Any]) -> Decision:
        agent_policy = self.policies.get("agent_specific", {}).get(agent_id)
        if agent_policy:
            decision = self._check_policy(agent_policy, action_type, resource, context)
            if decision != Decision.ALLOW:
                return decision
        default_policy = self.policies.get("default", {})
        return self._check_policy(default_policy, action_type, resource, context)

    def _check_policy(self, policy: Dict[str, Any], action_type: str, resource: str, context: Dict[str, Any]) -> Decision:
        category = "data_access" if "read" in action_type or "get" in action_type else "tool_access"
        permissions = policy.get(category, {})
        for pattern, rule in permissions.items():
            if pattern == "*" or pattern in resource:
                effect = rule.get("effect", "deny")
                conditions = rule.get("conditions", {})
                if self._check_conditions(context, conditions):
                    return Decision(effect)
        return Decision.DENY

    def _check_conditions(self, context: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        for key, value in conditions.items():
            if key not in context or context[key] != value:
                return False
        return True
