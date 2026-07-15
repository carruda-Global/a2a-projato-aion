import json, re
from typing import Any
from enum import Enum


class ValidationResult(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REVIEW_NEEDED = "review_needed"


class OutputValidator:
    def __init__(self):
        self.high_impact_actions = ["delete", "write", "update", "create", "execute"]
        self.sensitive_patterns = [
            r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
            r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        ]

    def validate_output(self, output: dict[str, Any], action: dict[str, Any]) -> ValidationResult:
        if self._is_high_impact(action):
            if self._contains_sensitive_data(output):
                return ValidationResult.REVIEW_NEEDED
            if not self._validate_schema(output):
                return ValidationResult.REJECTED
        return ValidationResult.APPROVED

    def _is_high_impact(self, action: dict[str, Any]) -> bool:
        at = action.get("type", "").lower()
        return any(p in at for p in self.high_impact_actions)

    def _contains_sensitive_data(self, output: dict[str, Any]) -> bool:
        s = json.dumps(output)
        return any(re.search(p, s) for p in self.sensitive_patterns)

    def _validate_schema(self, output: dict[str, Any]) -> bool:
        return all(f in output for f in ["status", "result"])
