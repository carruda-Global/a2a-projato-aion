"""ITR (Intelligent Token Reduction) -- the LLMOps cost-control layer of the
AION architecture, alongside PragLocker (prompt versioning/security) and
CoTGuard (reasoning-chain monitoring). Compacts conversation context before
it's sent to a model: keeps the system prompt and the most recent turns
verbatim (so recent reasoning/quality is untouched), and collapses older
turns into short extractive summaries instead of dropping them -- context is
preserved, just at a fraction of the token count. Pure Python, no extra LLM
call, so the reduction itself costs nothing.
"""
from typing import Dict, List


class ITR:

    def __init__(self, keep_recent_turns: int = 3, summary_chars: int = 160):
        self.keep_recent_turns = keep_recent_turns
        self.summary_chars = summary_chars

    def _estimate_tokens(self, text: str) -> int:
        # ~4 chars/token is the standard cheap estimate for English/Portuguese
        # prose -- good enough for a before/after reduction ratio, not billing.
        return max(1, len(text) // 4)

    def _summarize_turn(self, message: Dict[str, str]) -> Dict[str, str]:
        content = message.get("content", "")
        if len(content) <= self.summary_chars:
            return message
        summary = content[: self.summary_chars].rsplit(" ", 1)[0] + "…"
        return {**message, "content": summary}

    def compact_context(self, messages: List[Dict[str, str]]) -> Dict:
        """messages: list of {"role": ..., "content": ...}, in order.
        System messages are always kept verbatim. Of the remaining messages,
        the last `keep_recent_turns` are kept verbatim; everything older is
        collapsed to a short extractive summary."""
        original_tokens = sum(self._estimate_tokens(m.get("content", "")) for m in messages)

        system_msgs = [m for m in messages if m.get("role") == "system"]
        convo_msgs = [m for m in messages if m.get("role") != "system"]

        cutoff = max(0, len(convo_msgs) - self.keep_recent_turns)
        older, recent = convo_msgs[:cutoff], convo_msgs[cutoff:]
        compacted_older = [self._summarize_turn(m) for m in older]

        result = system_msgs + compacted_older + recent
        new_tokens = sum(self._estimate_tokens(m.get("content", "")) for m in result)
        reduction_pct = 0.0 if original_tokens == 0 else round((1 - new_tokens / original_tokens) * 100, 1)

        return {
            "messages": result,
            "original_tokens_est": original_tokens,
            "compacted_tokens_est": new_tokens,
            "reduction_pct": reduction_pct,
        }
