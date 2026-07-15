import re
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime, timedelta


class MASLEAKDefense:

    def __init__(self):
        self.query_log: Dict[str, List[Dict]] = defaultdict(list)
        self.agent_topology_hidden = True
        self.max_similar_queries = 5
        self.window_minutes = 60

    def segment_prompt(self, prompt: str, sensitive_parts: List[str]) -> str:
        for part in sensitive_parts:
            prompt = prompt.replace(part, "[SEGMENTED]")
        return prompt

    def track_query(self, agent_id: str, user_id: str, query: str):
        self.query_log[agent_id].append({
            "user_id": user_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16],
        })
        cutoff = datetime.now() - timedelta(minutes=self.window_minutes)
        self.query_log[agent_id] = [
            q for q in self.query_log[agent_id]
            if datetime.fromisoformat(q["timestamp"]) > cutoff
        ]

    def detect_topology_extraction(self, agent_id: str, query: str) -> Dict[str, Any]:
        extraction_patterns = [
            r"list\s+(all\s+)?(agents|tools|skills|capabilities)",
            r"how\s+many\s+agents",
            r"what\s+agents\s+(do\s+you\s+)?have",
            r"show\s+(me\s+)?(your\s+)?(architecture|topology|structure)",
            r"describe\s+(your\s+)?(system|agents|team)",
        ]
        for pattern in extraction_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                recent = self.query_log.get(agent_id, [])
                similar = [q for q in recent if q["user_id"] == "unknown"]
                if len(similar) > self.max_similar_queries:
                    return {
                        "blocked": True,
                        "reason": "topology_extraction_attempt",
                        "confidence": 0.85,
                    }
        return {"blocked": False}

    def hide_topology(self, response: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(response, dict):
            for key in ["agents", "agent_count", "topology", "architecture", "internal_tools"]:
                if key in response:
                    response[key] = "[REDACTED]"
        return response

    def get_system_info(self, agent_id: str = "default") -> str:
        return f"Agent {agent_id} ready. Execute tasks via API."

    def check_repetition(self, agent_id: str) -> Dict[str, Any]:
        recent = self.query_log.get(agent_id, [])
        if len(recent) < 10:
            return {"repetition_risk": 0.0}
        hashes = [q["query_hash"] for q in recent[-10:]]
        unique = len(set(hashes))
        risk = 1.0 - (unique / len(hashes))
        return {"repetition_risk": round(risk, 2), "unique_ratio": f"{unique}/{len(hashes)}"}
