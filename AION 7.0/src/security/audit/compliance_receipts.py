import json, hashlib, os
from datetime import datetime
from typing import Any


class ComplianceReceipt:
    def __init__(self):
        self.chain: list[dict[str, Any]] = []

    def create_receipt(self, action: dict[str, Any], decision: str, agent_id: str, risk_classification: str = "low") -> dict[str, Any]:
        receipt = {
            "type": "compliance",
            "issued_at": datetime.now().isoformat(),
            "issuer_id": agent_id,
            "action": {"tool": action.get("tool"), "arguments": action.get("arguments"), "outcome": action.get("outcome")},
            "decision": decision,
            "timestamp_anchor": datetime.now().isoformat(),
            "risk_classification": risk_classification,
            "previous_receipt_hash": self._get_previous_hash(),
            "build_provenance": os.getenv("BUILD_VERSION", "unknown"),
        }
        receipt["hash"] = self._calculate_hash(receipt)
        self.chain.append(receipt)
        return receipt

    def _get_previous_hash(self) -> str:
        return self.chain[-1]["hash"] if self.chain else "0000000000000000"

    def _calculate_hash(self, receipt: dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            if self.chain[i]["previous_receipt_hash"] != self.chain[i - 1]["hash"]:
                return False
        return True
