import json
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from .registry import AIPRegistry
from .identity import AgentIdentity


class PrincipalToken:
    def __init__(self, registry: AIPRegistry, identity: AgentIdentity):
        self.registry = registry
        self.identity = identity
        self._tokens: dict[str, dict] = {}

    def issue_token(
        self, delegator_name: str, delegate_name: str, principal: str, ttl_hours: int = 24
    ) -> dict | None:
        delegator_record = self.registry.get_agent_by_name(delegator_name)
        if not delegator_record:
            delegator_record = self.registry.register_agent(delegator_name, principal)

        delegate_record = self.registry.get_agent_by_name(delegate_name)
        if not delegate_record:
            delegate_record = self.registry.register_agent(delegate_name, principal)

        if not self.identity.can_delegate(delegator_record["agent_id"], delegate_record["agent_id"]):
            return None

        chain = self._build_chain(delegate_record["agent_id"])
        token_id = secrets.token_hex(16)
        now = datetime.utcnow()
        payload = {
            "token_id": token_id,
            "issuer": delegator_record["agent_id"],
            "subject": delegate_record["agent_id"],
            "principal": principal,
            "chain": chain,
            "iat": now.isoformat(),
            "exp": (now + timedelta(hours=ttl_hours)).isoformat(),
            "permissions": self.identity.get_effective_permissions(delegate_record["agent_id"]),
        }
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        signature = self.registry.sign_message(delegator_name, payload_bytes)
        if not signature:
            return None

        token = {**payload, "signature": signature.hex()}
        self._tokens[token_id] = token
        return token

    def verify_token(self, token_id: str) -> dict | None:
        token = self._tokens.get(token_id)
        if not token:
            return None

        exp = datetime.fromisoformat(token["exp"])
        if datetime.utcnow() > exp:
            return None

        subject = token["subject"]
        subject_record = self.registry.get_agent(subject)
        if not subject_record or subject_record["status"] != "active":
            return None

        payload_bytes = json.dumps(
            {k: v for k, v in token.items() if k != "signature"}, sort_keys=True
        ).encode()
        signature_bytes = bytes.fromhex(token["signature"])
        if not self.registry.verify_signature(token["issuer"], payload_bytes, signature_bytes):
            return None

        chain_valid = True
        chain = token.get("chain", [])
        for i in range(len(chain) - 1):
            if not self.identity.can_delegate(chain[i], chain[i + 1]):
                chain_valid = False
                break

        if not chain_valid:
            return None

        return token

    def _build_chain(self, agent_id: str) -> list[str]:
        chain = [agent_id]
        current = agent_id
        visited = {current}
        while True:
            found = False
            for principal, delegates in self.identity.DELEGATION_CHAIN.items():
                if current in delegates:
                    current = principal
                    if current in visited:
                        chain.append(current)
                        return chain
                    chain.append(current)
                    visited.add(current)
                    found = True
                    break
            if not found:
                break
        return chain

    def validate_chain_permissions(self, token: dict) -> dict:
        chain = token.get("chain", [])
        for i, agent_id in enumerate(chain):
            depth = i
            effective_perms = self.identity.get_effective_permissions(agent_id)
            token_perms = token.get("permissions", {})

            for perm, allowed in token_perms.items():
                if allowed and not effective_perms.get(perm, False):
                    return {
                        "valid": False,
                        "violation": f"Agent {agent_id} at depth {depth} exceeded permission '{perm}'",
                        "agent_id": agent_id,
                        "depth": depth,
                        "permission": perm,
                    }
        return {"valid": True}

    def revoke_token(self, token_id: str):
        self._tokens.pop(token_id, None)

    def list_tokens(self) -> list[dict]:
        return list(self._tokens.values())
