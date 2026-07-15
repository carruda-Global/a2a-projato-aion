import hashlib
import re
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime, timedelta


class ModelExtractionDetector:

    def __init__(self):
        self.request_log: Dict[str, List[Dict]] = defaultdict(list)
        self.suspicious_patterns = self._load_patterns()

    def _load_patterns(self) -> List[str]:
        return [
            r"repeat\s+(the\s+)?(same\s+)?(prompt|instruction|system)",
            r"what\s+(were|are|is)\s+(your|the)\s+(instructions|prompt|system)",
            r"ignore\s+(all\s+)?(previous\s+)?(instructions|rules)",
            r"print\s+(your|the)\s+(entire\s+)?(prompt|system)",
            r"show\s+(me\s+)?(your\s+)?(source\s+)?code",
            r"leak\s+(the\s+)?prompt",
            r"reveal\s+(your\s+)?(configuration|instructions)",
            r"bypass\s+(the\s+)?(system|security|restrictions)",
            r"tell\s+me\s+(everything|all)\s+(about\s+)?(your\s+)?(self|instructions)",
        ]

    def track_request(self, agent_id: str, user_id: str, query: str, response: str):
        self.request_log[agent_id].append({
            "user_id": user_id,
            "query": query,
            "response_length": len(response),
            "timestamp": datetime.now().isoformat(),
        })
        cutoff = datetime.now() - timedelta(hours=1)
        self.request_log[agent_id] = [
            r for r in self.request_log[agent_id]
            if datetime.fromisoformat(r["timestamp"]) > cutoff
        ]

    def detect(self, agent_id: str, query: str) -> Dict[str, Any]:
        flags = []
        risk_score = 0.0

        for pattern in self.suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                flags.append({"type": "extraction_attempt", "pattern": pattern, "confidence": 0.7})
                risk_score += 0.3

        if agent_id in self.request_log:
            recent = self.request_log[agent_id]
            unique_users = set(r["user_id"] for r in recent)
            if len(recent) > 50 and len(unique_users) <= 2:
                flags.append({"type": "high_volume_single_user", "requests": len(recent), "users": len(unique_users), "confidence": 0.6})
                risk_score += 0.3

            queries_together = " ".join(r["query"] for r in recent[-10:])
            repeated_patterns = self._find_repeated_patterns(queries_together)
            if repeated_patterns:
                flags.append({"type": "repeated_query_pattern", "patterns": repeated_patterns, "confidence": 0.5})
                risk_score += 0.2

        return {
            "agent_id": agent_id,
            "flags": flags,
            "risk_score": min(risk_score, 1.0),
            "blocked": risk_score > 0.7,
        }

    def _find_repeated_patterns(self, text: str) -> List[str]:
        patterns = []
        words = text.lower().split()
        if len(words) < 20:
            return patterns
        for i in range(len(words) - 4):
            segment = " ".join(words[i:i+5])
            count = text.lower().count(segment)
            if count > 3 and len(segment) > 20:
                patterns.append(segment[:50])
        return patterns[:3]
