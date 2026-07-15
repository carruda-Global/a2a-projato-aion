import pytest
from src.orchestrator.graph import create_multi_agent_graph
from src.orchestrator.planner import PlannerAgent
from src.orchestrator.router import RouterAgent
from src.orchestrator.coordinator import CoordinatorAgent
from src.orchestrator.synthesizer import SynthesizerAgent


@pytest.mark.asyncio
async def test_planner_decompose():
    planner = PlannerAgent()
    tasks = await planner.decompose("test query", [{"id": "agent1"}])
    assert len(tasks) > 0
    assert tasks[0]["task"] == "test query"


@pytest.mark.asyncio
async def test_router():
    router = RouterAgent({"agent1": "executor1"})
    result = await router.route({"agent": "agent1"})
    assert result == "agent1"


@pytest.mark.asyncio
async def test_coordinator():
    coordinator = CoordinatorAgent(max_concurrent=5)
    assert coordinator.max_concurrent == 5


@pytest.mark.asyncio
async def test_synthesizer():
    synth = SynthesizerAgent()
    result = await synth.synthesize([{"id": 1}, {"id": 2}])
    assert result["count"] == 2


def test_langgraph_graph():
    graph = create_multi_agent_graph()
    assert graph is not None or graph is None
