import json
import hashlib
from datetime import datetime, timezone
from typing import Any, Optional


class AuditTrail:
    def __init__(self, storage_path: str = "data/audit/"):
        self.storage_path = storage_path
        self.chain: list[dict] = []
        self.last_hash = "0" * 64

    def record(self, action: str, agent_id: str, tenant_id: str, data: dict) -> dict:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "agent_id": agent_id,
            "tenant_id": tenant_id,
            "data": data,
            "previous_hash": self.last_hash,
        }

        entry["hash"] = self._calculate_hash(entry)
        self.last_hash = entry["hash"]
        self.chain.append(entry)

        if len(self.chain) > 10000:
            self.chain = self.chain[-10000:]

        return entry

    def _calculate_hash(self, entry: dict) -> str:
        content = json.dumps(entry, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            if self.chain[i]["previous_hash"] != self.chain[i - 1]["hash"]:
                return False
        return True

    def get_history(self, agent_id: str = None, tenant_id: str = None, limit: int = 100) -> list[dict]:
        filtered = self.chain
        if agent_id:
            filtered = [e for e in filtered if e["agent_id"] == agent_id]
        if tenant_id:
            filtered = [e for e in filtered if e["tenant_id"] == tenant_id]
        return filtered[-limit:]

    def get_stats(self) -> dict:
        return {
            "total_entries": len(self.chain),
            "chain_integrity": self.verify_chain(),
            "last_hash": self.last_hash[:16] + "...",
        }
