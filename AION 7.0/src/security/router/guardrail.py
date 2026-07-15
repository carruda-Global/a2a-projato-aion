from typing import Any
from enum import Enum


class RequestType(Enum):
    LOOKUP = "lookup"
    REASONING = "reasoning"
    BLOCKED = "blocked"


class GuardrailRouter:
    def __init__(self):
        self.lookup_keywords = ["consulta", "buscar", "obter", "verificar", "mostrar"]
        self.reasoning_keywords = ["analisar", "raciocinar", "planejar", "criar", "desenvolver"]
        self.blocked_patterns = ["delete all", "drop table", "rm -rf"]

    def route(self, request: dict[str, Any]) -> RequestType:
        content = request.get("content", "").lower()
        for p in self.blocked_patterns:
            if p in content:
                return RequestType.BLOCKED
        for k in self.lookup_keywords:
            if k in content:
                return RequestType.LOOKUP
        for k in self.reasoning_keywords:
            if k in content:
                return RequestType.REASONING
        return RequestType.REASONING

    def get_constraints(self, request_type: RequestType) -> dict[str, Any]:
        if request_type == RequestType.LOOKUP:
            return {"max_tokens": 1000, "no_tools": True, "budget_usd": 0.001}
        elif request_type == RequestType.REASONING:
            return {"max_tokens": 5000, "tools": ["search", "compute"], "budget_usd": 0.01}
        return {"blocked": True, "reason": "policy_violation"}
