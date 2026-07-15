import os
import re
from pathlib import Path
from dotenv import load_dotenv
import yaml

load_dotenv()


def _resolve_env(value):
    if isinstance(value, str):
        def _replace(match):
            var = match.group(1)
            return os.getenv(var, match.group(0))
        return re.sub(r"\$\{(\w+)\}", _replace, value)
    return value


def _resolve_env_recursive(obj):
    if isinstance(obj, dict):
        return {k: _resolve_env_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_recursive(v) for v in obj]
    elif isinstance(obj, str):
        return _resolve_env(obj)
    return obj


def load_config(config_path: str | None = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return _resolve_env_recursive(config)


class Settings:
    def __init__(self, config_path: str | None = None):
        self.config = load_config(config_path)

        self.deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.deepseek_model: str = self.config.get("deepseek", {}).get("model", "deepseek-chat")
        self.deepseek_max_tokens: int = self.config.get("deepseek", {}).get("max_tokens", 16384)
        self.deepseek_temperature: float = self.config.get("deepseek", {}).get("temperature", 0.3)
        self.deepseek_api_base: str = self.config.get("deepseek", {}).get("api_base", "https://api.deepseek.com/v1")
        self.deepseek_timeout: int = self.config.get("deepseek", {}).get("timeout", 120)

        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_api_key: str = os.getenv("SUPABASE_API_KEY", "")

        self.app_env: str = os.getenv("APP_ENV", "development")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.debug: bool = self.config.get("app", {}).get("debug", False)

        self.orchestrator_config = self.config.get("orchestrator", {})
        self.clusters_config = self.config.get("clusters", {})
        self.memory_config = self.config.get("memory", {})
        self.rag_config = self.config.get("rag", {})
        self.evolution_config = self.config.get("evolution", {})
        self.rl_config = self.config.get("rl", {})
        self.monitoring_config = self.config.get("monitoring", {})
        self.security_config = self.config.get("security", {})
        self.budget_config = self.config.get("budget", {})

    def validate(self) -> list[str]:
        errors = []
        if not self.deepseek_api_key:
            errors.append("DEEPSEEK_API_KEY nao configurada")
        return errors
