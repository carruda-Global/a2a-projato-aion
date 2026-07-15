import hashlib
import re
from typing import Dict, Any, List, Optional
from datetime import datetime


class RedAct:

    def __init__(self):
        self.protected_patterns = self._load_protected_patterns()
        self.audit_preserve_keys = [
            "agent_id", "timestamp", "action_type", "status",
            "duration_ms", "tokens_used", "decision",
        ]

    def _load_protected_patterns(self) -> Dict[str, str]:
        return {
            r"(?i)(threshold|limiar)\s*[=:]\s*\d+\.?\d*": "[THRESHOLD_REDACTED]",
            r"(?i)(formula|formula)\s*[=:]\s*.+": "[FORMULA_REDACTED]",
            r"(?i)(strategy|estrategia|strategy_pattern)\s*[=:]\s*.+": "[STRATEGY_REDACTED]",
            r"(?i)(prompt|skill|skill_prompt)\s*[=:]\s*.{50,}": "[PROMPT_REDACTED]",
            r"(?i)(api_key|secret|token|password)\s*[=:]\s*\S+": "[CREDENTIAL_REDACTED]",
            r"(?i)(embedding|vector)\s*[\[:].+": "[EMBEDDING_REDACTED]",
            r"(?i)(error_recovery|fallback|retry)\s*(strategy|logic)?\s*[=:].+": "[RECOVERY_REDACTED]",
            r"(?i)(internal|system)\s*(config|configuration|settings)\s*[=:].+": "[CONFIG_REDACTED]",
        }

    def redact_trajectory(self, trajectory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        redacted = []
        for step in trajectory:
            protected_info = self._detect_protected(step)
            if protected_info:
                step = self._rewrite_step(step, protected_info)
            step = self._preserve_audit_evidence(step)
            redacted.append(step)
        return redacted

    def _detect_protected(self, step: Dict[str, Any]) -> List[Dict[str, Any]]:
        detected = []
        step_str = str(step)
        for pattern, replacement in self.protected_patterns.items():
            matches = re.findall(pattern, step_str)
            for match in matches:
                detected.append({
                    "pattern": pattern,
                    "match": match[:80] if isinstance(match, str) else str(match)[:80],
                    "replacement": replacement,
                })
        return detected

    def _rewrite_step(self, step: Dict[str, Any], protected_info: List[Dict]) -> Dict[str, Any]:
        step_str = str(step)
        for info in protected_info:
            if isinstance(info.get("match"), str) and info["match"] in step_str:
                step_str = step_str.replace(info["match"], info["replacement"], 1)
        import ast
        try:
            result = ast.literal_eval(step_str)
            if isinstance(result, dict):
                return result
        except (ValueError, SyntaxError):
            pass
        return step

    def _preserve_audit_evidence(self, step: Dict[str, Any]) -> Dict[str, Any]:
        preserved = {}
        for key in self.audit_preserve_keys:
            if key in step:
                preserved[key] = step[key]
        preserved["_redacted"] = True
        preserved["_original_keys"] = list(step.keys())
        return {**preserved, **{k: v for k, v in step.items() if k in self.audit_preserve_keys}}

    def redact_single(self, text: str, context: Optional[Dict] = None) -> str:
        for pattern, replacement in self.protected_patterns.items():
            text = re.sub(pattern, replacement, text)
        if context:
            for key in context:
                if isinstance(context[key], str) and len(context[key]) > 20:
                    text = text.replace(context[key], f"[REDACTED_{key}]")
        return text

    def compute_nst_reduction(self, original_skill: str, redacted_trajectory: List[Dict]) -> float:
        original_len = len(original_skill)
        redacted_len = sum(len(str(s)) for s in redacted_trajectory)
        if original_len == 0:
            return 0.0
        reduction = max(0.0, 1.0 - (redacted_len / original_len))
        return round(min(reduction, 0.9), 3)

    def get_protection_report(self, trajectory: List[Dict]) -> Dict[str, Any]:
        total_steps = len(trajectory)
        redacted = self.redact_trajectory(trajectory)
        redacted_count = sum(1 for s in redacted if s.get("_redacted"))
        return {
            "total_steps": total_steps,
            "redacted_steps": redacted_count,
            "protection_ratio": round(redacted_count / total_steps, 2) if total_steps > 0 else 0,
            "patterns_active": len(self.protected_patterns),
        }
