import pytest
from src.agents.base import BaseAgent


class ConcreteAgent(BaseAgent):
    async def execute(self, context):
        return {"status": "ok", "context": context}


@pytest.mark.asyncio
async def test_base_agent_creation():
    agent = ConcreteAgent(
        agent_id="#99", name="Test Agent", description="Test",
        group="test", price_brl=100.0, price_usd=25.0,
        tools=["test_tool"]
    )
    assert agent.agent_id == "#99"
    assert agent.name == "Test Agent"
    assert agent.price_brl == 100.0
    assert agent.price_usd == 25.0


@pytest.mark.asyncio
async def test_base_agent_execute():
    agent = ConcreteAgent(
        agent_id="#99", name="Test Agent", description="Test",
        group="test", price_brl=100.0, price_usd=25.0,
        tools=["test_tool"]
    )
    result = await agent.execute({"input": "test"})
    assert result["status"] == "ok"


@pytest.mark.asyncio
async def test_base_agent_budget():
    agent = ConcreteAgent(
        agent_id="#99", name="Test Agent", description="Test",
        group="test", price_brl=100.0, price_usd=25.0,
        tools=["test_tool"], budget=1000
    )
    assert agent._check_budget(500) is True
    agent.token_usage = 900
    assert agent._check_budget(500) is False


@pytest.mark.asyncio
async def test_base_agent_get_config():
    agent = ConcreteAgent(
        agent_id="#99", name="Test Agent", description="Test",
        group="test", price_brl=100.0, price_usd=25.0,
        tools=["test_tool"]
    )
    config = agent.get_config()
    assert config["agent_id"] == "#99"
    assert config["group"] == "test"
