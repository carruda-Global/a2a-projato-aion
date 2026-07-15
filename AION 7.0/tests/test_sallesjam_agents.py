import pytest
from unittest.mock import MagicMock

from src.config import Settings


@pytest.fixture
def settings():
    s = Settings()
    s.deepseek_api_key = "test-key"
    return s


@pytest.fixture
def llm_mock():
    mock = MagicMock()
    mock.chat.return_value = "Analise concluida com sucesso."
    return mock


@pytest.mark.unit
class TestSalesAgentChat:
    def test_detect_plan_interest_br(self):
        from app.routers.sales_agent_chat import _detect_plan_interest
        assert _detect_plan_interest("quero ativar lgpd", "", "BR") == "compliance_essencial"
        assert _detect_plan_interest("NR-1", "", "BR") == "compliance_essencial"
        assert _detect_plan_interest("preciso de esg", "", "BR") == "esg_carbono"
        assert _detect_plan_interest("igualdade salarial", "", "BR") == "regulatory_pro"

    def test_detect_plan_interest_us(self):
        from app.routers.sales_agent_chat import _detect_plan_interest
        assert _detect_plan_interest("EU AI Act compliance", "", "US") == "eu_ai_act"

    def test_detect_plan_interest_mx(self):
        from app.routers.sales_agent_chat import _detect_plan_interest
        assert _detect_plan_interest("LFPDPPP datos", "", "MX") == "lfpdppp"

    def test_detect_plan_interest_co(self):
        from app.routers.sales_agent_chat import _detect_plan_interest
        assert _detect_plan_interest("Ley 1581", "", "CO") == "ley1581"

    def test_detect_plan_interest_ar(self):
        from app.routers.sales_agent_chat import _detect_plan_interest
        assert _detect_plan_interest("automatización SDR", "", "AR") == "sdr_backoffice"

    def test_get_system_prompt_all_markets(self):
        from app.routers.sales_agent_chat import get_system_prompt
        for market in ["BR", "US", "MX", "CO", "AR"]:
            prompt = get_system_prompt(market)
            assert len(prompt) > 10

    def test_get_stripe_link_all_markets(self):
        from app.routers.sales_agent_chat import get_stripe_link
        assert "buy.stripe.com" in get_stripe_link("BR", "compliance_essencial")
        assert "buy.stripe.com" in get_stripe_link("US", "eu_ai_act")
        assert "buy.stripe.com" in get_stripe_link("MX", "lfpdppp")
        assert "buy.stripe.com" in get_stripe_link("CO", "ley1581")
        assert "buy.stripe.com" in get_stripe_link("AR", "sdr_backoffice")


@pytest.mark.unit
class TestVisitorIDAgent:
    def test_detect_market(self, settings):
        from src.agents.visitor_id_agent import VisitorIDAgent
        agent = VisitorIDAgent(settings)
        assert agent._detect_market("BR") == "BR"
        assert agent._detect_market("US") == "US"
        assert agent._detect_market("MX") == "MX"
        assert agent._detect_market("CO") == "CO"
        assert agent._detect_market("AR") == "AR"
        assert agent._detect_market("FR") == "US"


@pytest.mark.unit
class TestSEOContentAgent:
    def test_market_configs(self):
        from src.agents.seo_content_agent import MARKET_CONFIGS
        for market in ["BR", "US", "MX", "CO", "AR"]:
            assert market in MARKET_CONFIGS
            config = MARKET_CONFIGS[market]
            assert len(config) == 4


@pytest.mark.unit
class TestUsageBilling:
    def test_pricing_per_use(self):
        from src.agents.usage_billing import PRICING_PER_USE
        for market in ["BR", "US", "MX", "CO", "AR"]:
            assert market in PRICING_PER_USE
            assert len(PRICING_PER_USE[market]) > 0

    def test_pricing_currencies(self):
        from src.agents.usage_billing import PRICING_PER_USE
        assert PRICING_PER_USE["US"]["eu_ai_act_check"][0] == "usd"
        assert PRICING_PER_USE["MX"]["lfpdppp_check"][0] == "mxn"
        assert PRICING_PER_USE["CO"]["ley1581_check"][0] == "cop"
        assert PRICING_PER_USE["AR"]["sdr_diagnostic"][0] == "usd"
        assert PRICING_PER_USE["BR"]["nr1_diagnostico"][0] == "brl"


@pytest.mark.unit
class TestEuAiActAgent:
    def test_router_prefix(self):
        from src.agents.eu_ai_act_agent import router
        assert router.prefix == "/api/eu-ai-act"


@pytest.mark.unit
class TestLFPDPPPAgent:
    def test_router_prefix(self):
        from src.agents.lfpdppp_agent import router
        assert router.prefix == "/api/lfpdppp"


@pytest.mark.unit
class TestLey1581Agent:
    def test_router_prefix(self):
        from src.agents.ley1581_agent import router
        assert router.prefix == "/api/ley1581"


@pytest.mark.unit
class TestSDRBackofficeAgent:
    def test_router_prefix(self):
        from src.agents.sdr_backoffice_agent import router
        assert router.prefix == "/api/sdr-backoffice"
