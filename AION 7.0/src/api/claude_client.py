import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

class ClaudeClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY", "")
        self.model = "claude-sonnet-4-20250514"
        self._available = bool(self.api_key)

    def health_check(self) -> bool:
        return self._available

    async def generate(self, prompt: str, system_instruction: str = "", temperature: float = 0.3, max_tokens: int = 16384) -> dict[str, Any]:
        if not self._available:
            logger.warning("Claude API key not configured — returning simulated response")
            return {
                "content": f"[SIMULATED CLAUDE] {prompt[:100]}...",
                "model": self.model,
                "usage": {"input_tokens": len(prompt) // 4, "output_tokens": 200},
            }
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            messages = []
            if system_instruction:
                messages.append({"role": "user", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                system=system_instruction if system_instruction else None,
            )
            return {
                "content": response.content[0].text,
                "model": self.model,
                "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
            }
        except Exception as e:
            logger.error("Claude API error: %s", e)
            return {"error": str(e), "content": ""}
