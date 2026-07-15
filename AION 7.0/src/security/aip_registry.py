import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519


class AIPRegistry:

    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.revoked: set = set()

    def register_agent(self, agent_id: str, agent_name: str, principal: str, public_key: bytes) -> Dict[str, Any]:
        did = f"did:aip:{agent_id}"
        key_hash = hashlib.sha256(public_key).hexdigest()[:16]
        record = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "principal": principal,
            "did": did,
            "public_key_hash": key_hash,
            "public_key": public_key.hex(),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }
        self.agents[agent_id] = record
        return record

    def verify_agent(self, agent_id: str, signature: bytes, message: bytes) -> bool:
        if agent_id in self.revoked:
            return False
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(agent["public_key"]))
            public_key.verify(signature, message)
            self.agents[agent_id]["last_active"] = datetime.now().isoformat()
            return True
        except Exception:
            return False

    def revoke_agent(self, agent_id: str) -> bool:
        if agent_id in self.agents:
            self.revoked.add(agent_id)
            self.agents[agent_id]["status"] = "revoked"
            self.agents[agent_id]["revoked_at"] = datetime.now().isoformat()
            return True
        return False

    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self.agents.get(agent_id)

    def get_active_agents(self) -> list:
        return [agent for agent_id, agent in self.agents.items() if agent_id not in self.revoked and agent["status"] == "active"]
