import hashlib
import random
from typing import Dict, Any, List, Optional


class WeightWatermark:

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.embedding_key = hashlib.sha256(f"weightwm:{agent_id}".encode()).hexdigest()[:16]

    def embed_in_weights(self, weights: Dict[str, Any]) -> Dict[str, Any]:
        modified = {}
        for layer_name, tensor_data in weights.items():
            if isinstance(tensor_data, list):
                modified[layer_name] = self._modify_tensor(tensor_data)
            else:
                modified[layer_name] = tensor_data
        modified["_watermark"] = {
            "agent_id": self.agent_id,
            "key": self.embedding_key,
            "type": "weight_watermark",
        }
        return modified

    def _modify_tensor(self, tensor: list) -> list:
        if len(tensor) < 4:
            return tensor
        modified = tensor.copy()
        pos = hash(self.embedding_key) % len(tensor)
        epsilon = 0.0001
        modified[pos] = modified[pos] + epsilon if isinstance(modified[pos], (int, float)) else modified[pos]
        return modified

    def verify(self, weights: Dict[str, Any]) -> bool:
        wm = weights.get("_watermark", {})
        if not wm:
            return False
        return wm.get("agent_id") == self.agent_id and wm.get("key") == self.embedding_key

    def prove_ownership(self, weights: Dict[str, Any]) -> Dict[str, Any]:
        verified = self.verify(weights)
        return {
            "claimed_owner": self.agent_id,
            "verified": verified,
            "watermark_present": "_watermark" in weights,
            "method": "weight_watermarking",
        }
