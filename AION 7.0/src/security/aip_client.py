import json
from typing import Dict, Any
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519


class AIPClient:

    def __init__(self, agent_id: str, private_key: ed25519.Ed25519PrivateKey):
        self.agent_id = agent_id
        self.private_key = private_key
        self.public_key = private_key.public_key()

    @classmethod
    def generate_keypair(cls) -> ed25519.Ed25519PrivateKey:
        return ed25519.Ed25519PrivateKey.generate()

    def sign_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        canonical = json.dumps(action, sort_keys=True, separators=(',', ':'))
        message = canonical.encode('utf-8')
        signature = self.private_key.sign(message)
        return {
            "action": action,
            "signature": signature.hex(),
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }

    def sign_challenge(self, challenge: bytes) -> bytes:
        return self.private_key.sign(challenge)
