from typing import Any


class TextRetriever:
    def __init__(self):
        self.documents: list[dict] = []
        self._index: dict[str, list[int]] = {}

    def add_document(self, doc_id: str, content: str, metadata: dict = None) -> None:
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata or {},
        })
        for word in content.lower().split()[:100]:
            if word not in self._index:
                self._index[word] = []
            self._index[word].append(len(self.documents) - 1)

    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        query_words = set(query.lower().split())
        scores = []

        for i, doc in enumerate(self.documents):
            doc_words = set(doc["content"].lower().split())
            overlap = len(query_words & doc_words)
            if overlap > 0:
                scores.append((overlap, i))

        scores.sort(key=lambda x: -x[0])
        top_indices = [i for _, i in scores[:top_k]]

        return [
            {
                "id": self.documents[i]["id"],
                "content": self.documents[i]["content"][:200],
                "metadata": self.documents[i]["metadata"],
                "score": score,
                "source": "bm25",
            }
            for (score, i) in scores[:top_k]
        ]

    def size(self) -> int:
        return len(self.documents)
