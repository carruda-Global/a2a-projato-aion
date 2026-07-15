import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SynthesizerAgent:

    def __init__(self):
        self.strategies = {
            "merge": self._merge,
            "priority": self._priority_based,
            "recursive": self._recursive_merge
        }

    async def synthesize(self, results: List[Dict[str, Any]], strategy: str = "merge") -> Dict[str, Any]:
        merge_fn = self.strategies.get(strategy, self._merge)
        return merge_fn(results)

    def _merge(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        combined = {"results": results, "count": len(results)}
        errors = [r for r in results if "error" in r]
        if errors:
            combined["errors"] = errors
        return combined

    def _priority_based(self, results: List[Dict]) -> Dict[str, Any]:
        sorted_results = sorted(results, key=lambda r: r.get("task", {}).get("priority", 99))
        return self._merge(sorted_results)

    def _recursive_merge(self, results: List[Dict]) -> Dict[str, Any]:
        if len(results) <= 2:
            return self._merge(results)
        mid = len(results) // 2
        left = self._recursive_merge(results[:mid])
        right = self._recursive_merge(results[mid:])
        return self._merge([left, right])
