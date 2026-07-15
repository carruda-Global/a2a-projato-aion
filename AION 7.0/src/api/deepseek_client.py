import os
import logging
from openai import OpenAI
from src.config import Settings
from src.i18n.translations import get_system_prompt_instruction

logger = logging.getLogger(__name__)

_OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
_OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "moonshotai/kimi-k2")
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _make_openrouter_client() -> OpenAI | None:
    if not _OPENROUTER_KEY:
        return None
    return OpenAI(
        api_key=_OPENROUTER_KEY,
        base_url=_OPENROUTER_BASE_URL,
        timeout=60,
        default_headers={
            "HTTP-Referer": "https://global-engenharia.com",
            "X-Title": "EcoSystem AEC",
        },
    )


class DeepSeekClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base,
            timeout=settings.deepseek_timeout,
        )
        self._or_client = _make_openrouter_client()

    def _call(self, client: OpenAI, model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    def _call_with_fallback(self, messages: list[dict], temperature: float, max_tokens: int) -> str:
        """Tenta DeepSeek primeiro; se falhar, usa OpenRouter (Kimi-K2)."""
        try:
            return self._call(self.client, self.settings.deepseek_model, messages, temperature, max_tokens)
        except Exception as e:
            if self._or_client:
                logger.warning("[LLM] DeepSeek falhou (%s) — fallback OpenRouter/%s", e, _OPENROUTER_MODEL)
                return self._call(self._or_client, _OPENROUTER_MODEL, messages, temperature, max_tokens)
            raise

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        lang: str = "pt",
    ) -> str:
        lang_instruction = get_system_prompt_instruction(lang)
        combined_system = f"{system_prompt}\n\n{lang_instruction}"
        messages = [
            {"role": "system", "content": combined_system},
            {"role": "user", "content": user_prompt},
        ]
        return self._call_with_fallback(
            messages,
            temperature or self.settings.deepseek_temperature,
            max_tokens or self.settings.deepseek_max_tokens,
        )

    def chat_with_context(
        self,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
        lang: str = "pt",
    ) -> str:
        lang_instruction = get_system_prompt_instruction(lang)
        messages = list(messages)
        if messages and messages[0]["role"] == "system":
            messages[0] = {**messages[0], "content": f"{messages[0]['content']}\n\n{lang_instruction}"}
        else:
            messages.insert(0, {"role": "system", "content": lang_instruction})
        return self._call_with_fallback(
            messages,
            temperature or self.settings.deepseek_temperature,
            max_tokens or self.settings.deepseek_max_tokens,
        )

    def health_check(self) -> bool:
        try:
            self.chat(
                system_prompt="Responda apenas: OK",
                user_prompt="Teste de conexao",
                max_tokens=10,
            )
            return True
        except Exception:
            return False
