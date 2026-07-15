import hashlib
import random
from typing import Dict, Any, List, Optional
from datetime import datetime


class SeqWM:

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.secret = hashlib.sha256(f"seqwm:{agent_id}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        self.action_history: List[str] = []

    def embed(self, action: str, context: Dict[str, Any]) -> str:
        step = len(self.action_history) + 1
        signal = hashlib.sha256(f"{self.secret}:{len(self.action_history)}:{action}".encode()).hexdigest()[:8]
        self.action_history.append(action)
        modified = f"{action} [sig:{signal}]"
        return modified

    def _compute_signal(self, step: int, action: str) -> str:
        combined = hashlib.sha256(f"{self.secret}:{step-1}:{action}".encode()).hexdigest()[:8]
        return combined

    def verify_trajectory(self, actions: List[str]) -> Dict[str, Any]:
        if len(actions) < 3:
            return {"verified": False, "reason": "trajectory_too_short"}

        matches = 0
        total = 0
        for i, action in enumerate(actions):
            if "[sig:" in action:
                total += 1
                clean_action = action.split(" [sig:")[0]
                expected_sig = self._compute_signal(i + 1, clean_action)
                actual_sig = action.split("[sig:")[1].split("]")[0] if "[sig:" in action else ""
                if actual_sig == expected_sig:
                    matches += 1

        match_rate = matches / total if total > 0 else 0
        return {
            "verified": match_rate >= 0.6,
            "match_rate": round(match_rate, 2),
            "total_signals": total,
            "matches": matches,
            "agent_id": self.agent_id,
        }

    def detect_copy(self, actions: List[str], threshold: float = 0.5) -> Dict[str, Any]:
        result = self.verify_trajectory(actions)
        return {
            "is_copy": result["match_rate"] >= threshold,
            "confidence": result["match_rate"],
            "details": result,
        }
