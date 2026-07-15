import uuid
import json
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)


class AIPRegistry:
    def __init__(self, registry_url: str = "https://aip.global-engenharia.com"):
        self.registry_url = registry_url
        self.agents: dict[str, dict] = {}
        self._load_agents()

    def _load_agents(self):
        for file in CREDENTIALS_DIR.glob("*.json"):
            with open(file) as f:
                record = json.load(f)
                self.agents[record["agent_id"]] = record

    def register_agent(self, agent_name: str, principal: str) -> dict:
        agent_id = f"did:aip:{agent_name}_{uuid.uuid4().hex[:8]}"
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        record = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "public_key": public_pem.decode(),
            "principal": principal,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
        }
        credential_file = CREDENTIALS_DIR / f"{agent_name}.json"
        credential = {**record, "private_key": private_pem.decode()}
        with open(credential_file, "w") as f:
            json.dump(credential, f, indent=2)
        self.agents[agent_id] = record
        return record

    def verify_signature(self, agent_id: str, message: bytes, signature: bytes) -> bool:
        record = self.agents.get(agent_id)
        if not record or record["status"] != "active":
            return False
        public_pem = record["public_key"].encode()
        public_key = serialization.load_pem_public_key(public_pem)
        try:
            public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())
            return True
        except Exception:
            return False

    def sign_message(self, agent_name: str, message: bytes) -> bytes | None:
        credential_file = CREDENTIALS_DIR / f"{agent_name}.json"
        if not credential_file.exists():
            return None
        with open(credential_file) as f:
            credential = json.load(f)
        private_pem = credential["private_key"].encode()
        private_key = serialization.load_pem_private_key(private_pem, password=None)
        return private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())

    def revoke_agent(self, agent_id: str):
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = "revoked"

    def get_agent(self, agent_id: str) -> dict | None:
        return self.agents.get(agent_id)

    def get_agent_by_name(self, agent_name: str) -> dict | None:
        for agent in self.agents.values():
            if agent.get("agent_name") == agent_name:
                return agent
        return None

    def list_agents(self) -> list[dict]:
        return list(self.agents.values())
