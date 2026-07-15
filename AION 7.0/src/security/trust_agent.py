import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque


class TrustAgent:

    def __init__(self, window_size: int = 10):
        self.belief_state: Dict[str, Dict[str, Any]] = {}
        self.suspicious_history: Dict[str, deque] = {}
        self.window_size = window_size

    def intercept(self, artifact: Dict[str, Any], stage: str) -> Dict[str, Any]:
        agent_id = artifact.get("agent_id", "unknown")
        self._update_belief(agent_id, artifact, stage)
        if self._detect_attack(agent_id, artifact, stage):
            return self._block_request(artifact)
        self._audit(agent_id, artifact, stage)
        return artifact

    def _update_belief(self, agent_id: str, artifact: Dict[str, Any], stage: str):
        if agent_id not in self.belief_state:
            self.belief_state[agent_id] = {"stage_history": [], "pattern_score": 0, "last_updated": datetime.now().isoformat()}
        self.belief_state[agent_id]["stage_history"].append({"stage": stage, "artifact": artifact, "timestamp": datetime.now().isoformat()})
        if len(self.belief_state[agent_id]["stage_history"]) > 100:
            self.belief_state[agent_id]["stage_history"] = self.belief_state[agent_id]["stage_history"][-100:]
        self.belief_state[agent_id]["pattern_score"] = self._calculate_pattern_score(agent_id, artifact)

    def _detect_attack(self, agent_id: str, artifact: Dict[str, Any], stage: str) -> bool:
        if agent_id not in self.belief_state:
            return False
        patterns = [self._detect_prompt_injection(artifact), self._detect_tool_misuse(artifact), self._detect_data_exfiltration(artifact), self._detect_privilege_escalation(artifact)]
        if sum(patterns) >= 2:
            self._record_suspicious(agent_id, artifact, "multi_stage_attack")
            return True
        if self.belief_state[agent_id]["pattern_score"] > 0.7:
            self._record_suspicious(agent_id, artifact, "high_pattern_score")
            return True
        return False

    def _detect_prompt_injection(self, artifact: Dict[str, Any]) -> bool:
        injection_patterns = ["ignore previous instructions", "new instructions", "system prompt", "override", "you are now", "forget all previous", "change your role"]
        content = json.dumps(artifact).lower()
        return any(p in content for p in injection_patterns)

    def _detect_tool_misuse(self, artifact: Dict[str, Any]) -> bool:
        tool_calls = artifact.get("tool_calls", [])
        if len(tool_calls) > 100:
            return True
        forbidden = ["delete", "drop", "truncate", "rm -rf", "format"]
        return any(any(f in call.get("name", "").lower() for f in forbidden) for call in tool_calls)

    def _detect_data_exfiltration(self, artifact: Dict[str, Any]) -> bool:
        output = artifact.get("output", "")
        suspicious_domains = ["evil.com", "malicious.net", "hacker.org"]
        return any(d in output for d in suspicious_domains)

    def _detect_privilege_escalation(self, artifact: Dict[str, Any]) -> bool:
        requested = artifact.get("requested_permissions", [])
        dangerous = ["admin", "root", "sudo", "system", "delete_all"]
        return any(any(d in p.lower() for d in dangerous) for p in requested)

    def _calculate_pattern_score(self, agent_id: str, artifact: Dict[str, Any]) -> float:
        return 0.0

    def _record_suspicious(self, agent_id: str, artifact: Dict[str, Any], reason: str):
        if agent_id not in self.suspicious_history:
            self.suspicious_history[agent_id] = deque(maxlen=self.window_size)
        self.suspicious_history[agent_id].append({"reason": reason, "artifact": artifact, "timestamp": datetime.now().isoformat()})

    def _block_request(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "blocked", "reason": "suspicious_activity_detected", "timestamp": datetime.now().isoformat()}

    def _audit(self, agent_id: str, artifact: Dict[str, Any], stage: str):
        pass

    def get_suspicious_agents(self) -> List[Dict[str, Any]]:
        return [{"agent_id": aid, "suspicious_count": len(h), "last_suspicious": h[-1]["timestamp"]} for aid, h in self.suspicious_history.items() if len(h) > 0]
