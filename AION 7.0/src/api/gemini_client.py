import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: str | None = None, location: str = "southamerica-east1"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.location = location
        self.base_url = f"https://{location}-aiplatform.googleapis.com/v1"
        self._available = bool(self.api_key)

    def health_check(self) -> bool:
        return self._available

    async def generate(self, prompt: str, system_instruction: str = "", temperature: float = 0.3, max_tokens: int = 8192) -> dict[str, Any]:
        if not self._available:
            logger.warning("Gemini API key not configured — returning simulated response")
            return {
                "content": f"[SIMULATED GEMINI] {prompt[:100]}...",
                "model": f"gemini-1.5-pro@{self.location}",
                "usage": {"prompt_tokens": len(prompt) // 4, "completion_tokens": 200},
            }
        try:
            import google.genai as genai
            genai_client = genai.Client(api_key=self.api_key)
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = genai_client.models.generate_content(
                model="gemini-1.5-pro",
                contents=full_prompt,
                config={"temperature": temperature, "max_output_tokens": max_tokens},
            )
            return {
                "content": response.text,
                "model": "gemini-1.5-pro",
                "usage": {"prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0, "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0},
            }
        except Exception as e:
            logger.error("Gemini API error: %s", e)
            return {"error": str(e), "content": ""}
