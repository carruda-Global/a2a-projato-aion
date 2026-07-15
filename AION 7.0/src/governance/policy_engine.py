import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

Rule = dict[str, Any]


class PolicyEngine:
    def __init__(self):
        self.rules: list[Rule] = []
        self.agent_rules: dict[str, list[Rule]] = {}

    def load_rules(self, path: str | Path) -> int:
        path = Path(path)
        if not path.exists():
            logger.warning("Arquivo de regras nao encontrado: %s", path)
            return 0
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for rule in data.get("rules", []):
            self.rules.append(rule)
            for agent_id in rule.get("agents", ["*"]):
                self.agent_rules.setdefault(agent_id, []).append(rule)
                count += 1
        logger.info("PolicyEngine: %d regras carregadas de %s", count, path)
        return count

    def evaluate(self, agent_id: str, output: dict) -> list[dict[str, Any]]:
        violations = []
        applicable = self.agent_rules.get(agent_id, []) + self.agent_rules.get("*", [])
        for rule in applicable:
            result = self._check_rule(rule, output)
            if result:
                violations.append(result)
        return violations

    def _check_rule(self, rule: Rule, output: dict) -> dict[str, Any] | None:
        field = rule.get("field", "")
        expected_type = rule.get("type", "string")
        required = rule.get("required", False)
        min_length = rule.get("min_length", 0)
        forbidden_keywords = rule.get("forbidden_keywords", [])

        value = self._get_nested(output, field)

        if required and value is None:
            return {
                "rule_id": rule.get("id", "unknown"),
                "field": field,
                "violation": "campo_obrigatorio_ausente",
                "severity": rule.get("severity", "high"),
            }

        if value is not None:
            if expected_type == "string" and not isinstance(value, str):
                return {
                    "rule_id": rule.get("id", "unknown"),
                    "field": field,
                    "violation": f"tipo_esperado_{expected_type}",
                    "severity": rule.get("severity", "medium"),
                }

            if isinstance(value, str) and len(value) < min_length:
                return {
                    "rule_id": rule.get("id", "unknown"),
                    "field": field,
                    "violation": f"tamanho_minimo_{min_length}",
                    "severity": rule.get("severity", "low"),
                }

            for kw in forbidden_keywords:
                if isinstance(value, str) and kw.lower() in value.lower():
                    return {
                        "rule_id": rule.get("id", "unknown"),
                        "field": field,
                        "violation": f"palavra_proibida_{kw}",
                        "severity": rule.get("severity", "high"),
                    }

        return None

    def _get_nested(self, data: dict, path: str) -> Any:
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current
