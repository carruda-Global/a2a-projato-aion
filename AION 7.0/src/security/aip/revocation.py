import json
import asyncio
from datetime import datetime
from pathlib import Path

from .registry import AIPRegistry


class RevocationManager:
    def __init__(self, registry: AIPRegistry, revocation_file: str | None = None):
        self.registry = registry
        self.revocation_file = (
            revocation_file or str(Path(__file__).parent / "revocations.json")
        )
        self._revocations: dict[str, dict] = {}
        self._subscribers: list[callable] = []
        self._load_revocations()

    def _load_revocations(self):
        path = Path(self.revocation_file)
        if path.exists():
            with open(path) as f:
                self._revocations = json.load(f)

    def _save_revocations(self):
        with open(self.revocation_file, "w") as f:
            json.dump(self._revocations, f, indent=2)

    def _get_child_agents(self, agent_id: str) -> list[str]:
        from .identity import AgentIdentity
        children = []
        for parent, delegates in AgentIdentity.DELEGATION_CHAIN.items():
            if parent == agent_id:
                children.extend(delegates)
                for child in delegates:
                    children.extend(self._get_child_agents(child))
        return children

    def revoke(self, agent_id: str, reason: str = "security_incident", cascade: bool = True) -> dict:
        record = self.registry.get_agent(agent_id)
        if not record:
            return {"status": "error", "reason": "agent_not_found"}

        self.registry.revoke_agent(agent_id)

        revoked_children = []
        if cascade:
            children = self._get_child_agents(agent_id)
            for child_id in children:
                child_record = self.registry.get_agent(child_id)
                if child_record and child_record["status"] != "revoked":
                    self.registry.revoke_agent(child_id)
                    revoked_children.append(child_id)
                    child_revocation = {
                        "agent_id": child_id,
                        "agent_name": child_record.get("agent_name", "unknown"),
                        "principal": child_record.get("principal", "unknown"),
                        "reason": f"cascade_from_{agent_id}: {reason}",
                        "revoked_at": datetime.utcnow().isoformat(),
                        "status": "revoked",
                    }
                    self._revocations[child_id] = child_revocation

        revocation = {
            "agent_id": agent_id,
            "agent_name": record.get("agent_name", "unknown"),
            "principal": record.get("principal", "unknown"),
            "reason": reason,
            "revoked_at": datetime.utcnow().isoformat(),
            "status": "revoked",
            "cascade_revoked": revoked_children,
        }
        self._revocations[agent_id] = revocation
        self._save_revocations()
        self._notify_subscribers(revocation)
        return {"status": "revoked", **revocation}

    def bulk_revoke(self, agent_ids: list[str], reason: str = "security_incident") -> list[dict]:
        results = []
        for agent_id in agent_ids:
            results.append(self.revoke(agent_id, reason))
        return results

    def suspend(self, agent_id: str, reason: str = "temporary_suspension") -> dict:
        record = self.registry.get_agent(agent_id)
        if not record:
            return {"status": "error", "reason": "agent_not_found"}

        record["status"] = "suspended"
        suspension = {
            "agent_id": agent_id,
            "reason": reason,
            "suspended_at": datetime.utcnow().isoformat(),
        }
        self._revocations[agent_id] = suspension
        self._save_revocations()
        return {"status": "suspended", **suspension}

    def restore(self, agent_id: str) -> dict:
        record = self.registry.get_agent(agent_id)
        if not record:
            return {"status": "error", "reason": "agent_not_found"}
        record["status"] = "active"
        self._revocations.pop(agent_id, None)
        self._save_revocations()
        return {"status": "restored", "agent_id": agent_id}

    def is_revoked(self, agent_id: str) -> bool:
        record = self.registry.get_agent(agent_id)
        return record is None or record["status"] in ("revoked", "suspended")

    def subscribe(self, callback: callable):
        self._subscribers.append(callback)

    def _notify_subscribers(self, revocation: dict):
        for callback in self._subscribers:
            try:
                callback(revocation)
            except Exception:
                pass

    def get_revocation_history(self, agent_id: str | None = None) -> list[dict]:
        if agent_id:
            entry = self._revocations.get(agent_id)
            return [entry] if entry else []
        return list(self._revocations.values())

    def emergency_shutdown(self, reason: str = "emergency_shutdown") -> dict:
        all_agents = self.registry.list_agents()
        results = self.bulk_revoke(
            [a["agent_id"] for a in all_agents], reason
        )
        return {
            "status": "emergency_shutdown",
            "total_revoked": len(results),
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_active_count(self) -> int:
        return sum(
            1 for a in self.registry.list_agents()
            if a["status"] == "active"
        )
