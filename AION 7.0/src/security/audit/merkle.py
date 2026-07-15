import hashlib
from typing import Any


class MerkleChain:
    def __init__(self):
        self.nodes: list[str] = []

    def add_leaf(self, data: str) -> str:
        leaf = hashlib.sha256(data.encode()).hexdigest()
        self.nodes.append(leaf)
        return leaf

    def build_tree(self) -> str:
        if not self.nodes:
            return hashlib.sha256(b"genesis").hexdigest()
        level = self.nodes[:]
        while len(level) > 1:
            next_level = []
            for i in range(0, len(level), 2):
                combined = level[i] + (level[i + 1] if i + 1 < len(level) else level[i])
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            level = next_level
        return level[0]
