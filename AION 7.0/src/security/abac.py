import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AttributeType(Enum):
    USER_ROLE = "user_role"
    AGENT_GROUP = "agent_group"
    DATA_SENSITIVITY = "data_sensitivity"
    ACTION = "action"
    TENANT = "tenant"


class ABACEngine:

    def __init__(self):
        self.policies: List[Dict] = [
            {"effect": "deny", "subjects": ["anonymous"], "actions": ["*"], "resources": ["*"]},
            {"effect": "allow", "subjects": ["admin"], "actions": ["*"], "resources": ["*"]},
            {"effect": "allow", "subjects": ["user"], "actions": ["read", "execute"], "resources": ["agent:*"]},
        ]

    def evaluate(self, subject: Dict[str, Any], action: str, resource: Dict[str, Any]) -> bool:
        for policy in self.policies:
            if not self._match_subject(policy.get("subjects", []), subject):
                continue
            if not self._match_action(policy.get("actions", []), action):
                continue
            if not self._match_resource(policy.get("resources", []), resource):
                continue

            if policy["effect"] == "deny":
                logger.warning(f"ABAC denied {action} for {subject.get('role')}")
                return False
            if policy["effect"] == "allow":
                return True

        logger.info(f"ABAC default deny for {action}")
        return False

    def _match_subject(self, patterns: List[str], subject: Dict) -> bool:
        role = subject.get("role", "anonymous")
        return any(p == role or p == "*" for p in patterns)

    def _match_action(self, patterns: List[str], action: str) -> bool:
        return any(p == action or p == "*" for p in patterns)

    def _match_resource(self, patterns: List[str], resource: Dict) -> bool:
        res_type = resource.get("type", "*")
        return any(p == res_type or p == "*" or res_type.startswith(p.replace("*", "")) for p in patterns)
