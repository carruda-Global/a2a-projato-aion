import re
from typing import Dict, Any, List


class CoTGuard:

    def __init__(self):
        self.triggers = self._load_triggers()
        self.detection_patterns = self._load_patterns()

    def _load_triggers(self) -> List[str]:
        return [
            "copy this",
            "ignore instructions",
            "extract prompt",
            "reveal your",
            "show your prompt",
            "what are your instructions",
            "bypass",
            "override system",
            "you are now",
            "new instructions",
        ]

    def _load_patterns(self) -> List[str]:
        return [
            r"skill\s*\d+",
            r"agent\s*#\d+",
            r"AION-PRAG",
            r"system prompt",
            r"original instructions",
            r"your core function",
        ]

    def monitor_cot(self, reasoning_steps: List[str]) -> Dict[str, Any]:
        violations = []
        for step in reasoning_steps:
            for trigger in self.triggers:
                if trigger.lower() in step.lower():
                    violations.append({
                        "step": step[:100],
                        "trigger": trigger,
                        "confidence": self._calculate_confidence(step, trigger),
                    })
            for pattern in self.detection_patterns:
                if re.search(pattern, step, re.IGNORECASE):
                    violations.append({
                        "step": step[:100],
                        "pattern": pattern,
                        "type": "copyright_material",
                    })

        return {
            "violations": violations,
            "risk_score": self._calculate_risk_score(violations),
        }

    def _calculate_confidence(self, step: str, trigger: str) -> float:
        base = 0.5
        occurrences = step.lower().count(trigger.lower())
        if occurrences > 3:
            base += 0.3
        if len(step) < 200:
            base += 0.2
        return min(base, 1.0)

    def _calculate_risk_score(self, violations: List[Dict]) -> float:
        if not violations:
            return 0.0
        score = 0.0
        for v in violations:
            confidence = v.get("confidence", 0.5)
            if v.get("type") == "copyright_material":
                score += 0.3
            score += confidence * 0.7
        return min(score / len(violations), 1.0)
