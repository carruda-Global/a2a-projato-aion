import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime


class AuditChain:

    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.merkle_root: Optional[str] = None

    def append(self, entry: Dict[str, Any]) -> str:
        entry_hash = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        previous_hash = self.chain[-1]["hash"] if self.chain else "0" * 16
        block = {"index": len(self.chain), "timestamp": datetime.now().isoformat(), "entry": entry, "hash": entry_hash, "previous_hash": previous_hash}
        self.chain.append(block)
        self._update_merkle_root()
        return entry_hash

    def _update_merkle_root(self):
        if not self.chain:
            self.merkle_root = None
            return
        hashes = [block["hash"] for block in self.chain]
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            hashes = [hashlib.sha256((h1 + h2).encode()).hexdigest() for h1, h2 in zip(hashes[::2], hashes[1::2])]
        self.merkle_root = hashes[0]

    def verify(self) -> bool:
        if not self.chain:
            return True
        for i in range(1, len(self.chain)):
            expected = hashlib.sha256(json.dumps(self.chain[i]["entry"], sort_keys=True).encode()).hexdigest()
            if self.chain[i]["hash"] != expected or self.chain[i]["previous_hash"] != self.chain[i-1]["hash"]:
                return False
        old_root = self.merkle_root
        self._update_merkle_root()
        return old_root == self.merkle_root

    def get_proof(self, index: int) -> Optional[Dict[str, Any]]:
        if index >= len(self.chain):
            return None
        block = self.chain[index]
        return {"entry": block["entry"], "hash": block["hash"], "previous_hash": block["previous_hash"], "merkle_root": self.merkle_root, "index": index, "total_entries": len(self.chain)}
