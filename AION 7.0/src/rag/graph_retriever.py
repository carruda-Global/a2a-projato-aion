from typing import Any, Optional


class GraphRetriever:
    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: list[tuple[str, str, str]] = []

    def add_node(self, node_id: str, label: str, properties: dict = None) -> None:
        self.nodes[node_id] = {"id": node_id, "label": label, "properties": properties or {}}

    def add_edge(self, source: str, target: str, relation: str) -> None:
        self.edges.append((source, target, relation))

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        query_lower = query.lower()
        scored = []

        for node_id, node in self.nodes.items():
            label = node["label"].lower()
            props_str = " ".join(str(v).lower() for v in node["properties"].values())
            combined = f"{label} {props_str}"

            overlap = len(set(query_lower.split()) & set(combined.split()))
            if overlap > 0:
                relations = self._get_relations(node_id)
                scored.append({
                    "id": node_id,
                    "content": f"{node['label']}: {props_str[:200]}",
                    "metadata": {"relations": relations, "properties": node["properties"]},
                    "score": overlap,
                    "source": "graph",
                })

        scored.sort(key=lambda x: -x["score"])
        return scored[:top_k]

    def _get_relations(self, node_id: str) -> list[dict]:
        related = []
        for s, t, r in self.edges:
            if s == node_id:
                target = self.nodes.get(t)
                if target:
                    related.append({"target": target["label"], "relation": r})
            elif t == node_id:
                source = self.nodes.get(s)
                if source:
                    related.append({"target": source["label"], "relation": f"{r} (inverse)"})
        return related

    def size(self) -> int:
        return len(self.nodes)
