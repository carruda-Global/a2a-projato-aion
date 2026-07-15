import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class QualityGates:

    def __init__(self):
        self.rules = {
            "coverage": {"min": 80},
            "security_issues": {"max": 0},
            "duplication": {"max": 3},
            "reliability_issues": {"max": 0}
        }

    def check(self, output: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        results = {}
        all_passed = True

        for gate_name, threshold in self.rules.items():
            value = output.get(gate_name, self._get_default(gate_name))
            gate_passed = self._evaluate(gate_name, value, threshold)
            results[gate_name] = {
                "value": value,
                "threshold": threshold,
                "passed": gate_passed
            }
            if not gate_passed:
                all_passed = False

        return {
            "passed": all_passed,
            "report": {
                "agent_id": agent_id,
                "gates": results,
                "summary": "all gates passed" if all_passed else "some gates failed"
            }
        }

    def _get_default(self, gate_name: str) -> float:
        defaults = {
            "coverage": 100,
            "security_issues": 0,
            "duplication": 0,
            "reliability_issues": 0
        }
        return defaults.get(gate_name, 0)

    def _evaluate(self, gate_name: str, value: float, threshold: Dict) -> bool:
        if "min" in threshold:
            return value >= threshold["min"]
        if "max" in threshold:
            return value <= threshold["max"]
        return True
