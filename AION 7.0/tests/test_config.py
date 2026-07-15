import pytest
from src.config import Settings


@pytest.mark.unit
class TestSettings:
    def test_settings_loads_config(self, settings):
        assert settings.deepseek_model == "deepseek-chat"
        assert settings.deepseek_temperature == 0.3
        assert settings.deepseek_max_tokens == 16384

    def test_settings_validate_missing_key(self, settings):
        settings.deepseek_api_key = ""
        errors = settings.validate()
        assert len(errors) > 0

    def test_settings_validate_ok(self, settings):
        settings.deepseek_api_key = "sk-test"
        errors = settings.validate()
        assert len(errors) == 0

    def test_agents_config_loaded(self, settings):
        assert "spec_analyst" in settings.agents_config
        assert settings.agents_config["spec_analyst"]["enabled"] is True

    def test_plans_config_loaded(self, settings):
        assert "compliance_essencial" in settings.plans_config
        assert settings.plans_config["compliance_essencial"]["amount_cents"] == 59000

    def test_llm_routing_loaded(self, settings):
        assert "default" in settings.llm_routing_config
        assert settings.llm_routing_config["default"] == "deepseek"
