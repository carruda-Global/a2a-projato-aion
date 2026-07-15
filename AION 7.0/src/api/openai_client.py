import os, logging
from openai import OpenAI
from src.config import Settings
from src.i18n.translations import get_system_prompt_instruction

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, settings: Settings, api_key: str = "", base_url: str = "", model: str = ""):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", settings.openrouter_api_key)
        self.base_url = base_url or settings.openrouter_api_base
        self.model = model or settings.openrouter_model
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=settings.llm_timeout)

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 4096, lang: str = "pt") -> str:
        lang_instruction = get_system_prompt_instruction(lang)
        combined = f"{system_prompt}\n\n{lang_instruction}"
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": combined}, {"role": "user", "content": user_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""
