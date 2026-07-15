from typing import Any, Optional
from src.rag.text_retriever import TextRetriever
from src.rag.graph_retriever import GraphRetriever


class HybridRAG:
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.text_retriever = TextRetriever()
        self.graph_retriever = GraphRetriever()
        self.cache: dict[str, Any] = {}

    async def retrieve(self, query: str, top_k: int = 5) -> dict:
        cache_key = f"{query}:{top_k}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        text_results = await self.text_retriever.retrieve(query, top_k)
        graph_results = await self.graph_retriever.retrieve(query, top_k)

        combined = self._fusion(text_results, graph_results, top_k)

        result = {
            "query": query,
            "results": combined,
            "text_results": text_results,
            "graph_results": graph_results,
            "total_found": len(combined),
        }

        self.cache[cache_key] = result
        if len(self.cache) > 500:
            oldest = next(iter(self.cache))
            del self.cache[oldest]

        return result

    def _fusion(self, text_results: list, graph_results: list, top_k: int) -> list:
        seen = set()
        fused = []

        for r in text_results + graph_results:
            key = str(r.get("id", r.get("content", "")))
            if key not in seen:
                seen.add(key)
                fused.append(r)

        return fused[:top_k]

    async def retrieve_with_reflection(self, query: str, top_k: int = 5) -> dict:
        results = await self.retrieve(query, top_k)
        results["reflection"] = self._reflect(results["results"], query)
        return results

    def _reflect(self, results: list, query: str) -> str:
        if not results:
            return "Nenhum resultado encontrado para refletir."
        return f"Encontrados {len(results)} resultados relevantes para: {query[:100]}"
