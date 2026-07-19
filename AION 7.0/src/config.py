import os
import re
from functools import lru_cache
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
        config_path = Path(__file__).parent.parent / "config.yaml"
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

        self.openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_api_base: str = self.config.get("openrouter", {}).get("api_base", "https://openrouter.ai/api/v1")
        self.openrouter_model: str = self.config.get("openrouter", {}).get("model", "openai/gpt-4o-mini")
        self.llm_timeout: int = self.config.get("openrouter", {}).get("timeout", 120)
        self.llm_default_provider: str = self.config.get("llm_routing", {}).get("default", "openrouter")

        self.opencode_zen_api_key: str = os.getenv("OPENCODE_ZEN_API_KEY", "")
        self.opencode_zen_api_base: str = "https://opencode.ai/zen/v1"
        self.opencode_zen_model: str = "deepseek-v4-flash-free"

        self.stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
        self.stripe_publishable_key: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        self.stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self.stripe_webhook_secret_production: str = os.getenv("STRIPE_WEBHOOK_SECRET_PRODUCTION", "")
        self.stripe_webhook_secret_test: str = os.getenv("STRIPE_WEBHOOK_SECRET_TEST", "")

        self.abacatepay_api_key: str = os.getenv("ABACATEPAY_API_KEY", "")
        self.abacatepay_webhook_secret: str = os.getenv("ABACATEPAY_WEBHOOK_SECRET", "")
        self.abacatepay_sandbox_mode: bool = os.getenv("ABACATEPAY_SANDBOX_MODE", "false").lower() == "true"

        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_api_key: str = os.getenv("SUPABASE_API_KEY", "")

        self.vapi_api_key: str = os.getenv("VAPI_API_KEY", "")
        self.vapi_demo_phone_number_id: str = os.getenv("VAPI_DEMO_PHONE_NUMBER_ID", "")
        self.google_places_api_key: str = os.getenv("GOOGLE_PLACES_API_KEY", "")

        self.app_env: str = os.getenv("APP_ENV", "development")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.debug: bool = self.config.get("app", {}).get("debug", False)

        self.aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
        self.aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        aws = self.config.get("marketplace", {}).get("aws", {})
        self.aws_region: str = aws.get("region", "us-east-1")
        self.aws_product_code: str = aws.get("product_code", "")
        self.aws_sns_topic_arn: str = aws.get("sns_topic_arn", "")
        self.aws_subscribe_redirect_url: str = os.getenv("AWS_SUBSCRIBE_REDIRECT_URL", "")

        oracle = self.config.get("marketplace", {}).get("oracle", {})
        self.oracle_product_id: str = oracle.get("product_id", "")
        self.oracle_seller_id: str = oracle.get("seller_id", "")
        self.oracle_enabled: bool = oracle.get("enabled", False)

        microsoft = self.config.get("marketplace", {}).get("microsoft", {})
        self.microsoft_tenant_id: str = microsoft.get("tenant_id", os.getenv("AZURE_TENANT_ID", ""))
        self.microsoft_client_id: str = microsoft.get("client_id", os.getenv("AZURE_CLIENT_ID", ""))
        self.microsoft_client_secret: str = microsoft.get("client_secret", os.getenv("AZURE_CLIENT_SECRET", ""))
        self.microsoft_fulfillment_api_version: str = microsoft.get("fulfillment_api_version", "2018-08-31")
        self.microsoft_enabled: bool = microsoft.get("enabled", True)

        hubspot = self.config.get("marketplace", {}).get("hubspot", {})
        self.hubspot_client_id: str = hubspot.get("client_id", os.getenv("HUBSPOT_CLIENT_ID", ""))
        self.hubspot_client_secret: str = hubspot.get("client_secret", os.getenv("HUBSPOT_CLIENT_SECRET", ""))
        self.hubspot_app_id: str = hubspot.get("app_id", os.getenv("HUBSPOT_APP_ID", ""))
        self.hubspot_enabled: bool = hubspot.get("enabled", True)

        self.base_url: str = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")

        self.marketplace_admin_secret: str = os.getenv("MARKETPLACE_ADMIN_SECRET", "")
        self.pipefy_webhook_secret: str = os.getenv("PIPEFY_WEBHOOK_SECRET", "")
        self.salesforce_webhook_secret: str = os.getenv("SALESFORCE_WEBHOOK_SECRET", "")

        clusters = self.config.get("clusters", {})
        self.agents_config: dict = {}
        for cluster_name, cluster_cfg in clusters.items():
            cluster_agents = cluster_cfg.get("agents", {})
            for agent_id, agent_cfg in cluster_agents.items():
                self.agents_config[agent_id] = agent_cfg
        self.plans_config: dict = self.config.get("stripe", {}).get("plans", {})
        self.cross_selling_config: dict = self.config.get("cross_selling", {})

        self.orchestrator_config = self.config.get("orchestrator", {})
        self.clusters_config = self.config.get("clusters", {})

        self.llm_routing_config: dict = self.config.get("llm_routing", {})

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.deepseek_api_key:
            errors.append("DEEPSEEK_API_KEY nao configurada")
        sk = self.stripe_secret_key
        if not sk:
            errors.append("STRIPE_SECRET_KEY nao configurada")
        elif not sk.startswith("sk_test_") and not sk.startswith("sk_live_"):
            errors.append("STRIPE_SECRET_KEY invalida — deve comecar com sk_test_ ou sk_live_")
        if not self.supabase_url:
            errors.append("SUPABASE_URL nao configurada")
        if self.microsoft_enabled:
            tid = self.microsoft_tenant_id
            cid = self.microsoft_client_id
            cs = self.microsoft_client_secret
            if not tid or tid.startswith("${"):
                errors.append("AZURE_TENANT_ID nao configurada — Microsoft Marketplace desabilitado")
            if not cid or cid.startswith("${"):
                errors.append("AZURE_CLIENT_ID nao configurada — Microsoft Marketplace desabilitado")
            if not cs or cs.startswith("${"):
                errors.append("AZURE_CLIENT_SECRET nao configurada — Microsoft Marketplace desabilitado")
        return errors


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
