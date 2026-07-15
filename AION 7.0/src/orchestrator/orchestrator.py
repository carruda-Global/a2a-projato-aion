import asyncio
import logging
import time
from typing import Any, Dict

from src.agents.aec_core_agents import build_core_agents
from src.agents.architecture_support_agents import build_support_agents, QualityCriticAgent
from src.agents.bim_coordinator import BIMCoordinatorAgent
from src.agents.council_agent import CouncilAgent
from src.api.deepseek_client import DeepSeekClient
from src.security.agent_compliance import record_agent_receipt
from src.security.agent_execution_log import record_agent_execution

_DIRECT_AGENT_IDS = {"client_intelligence", "quality_critic", "regulatory_watch", "council_agent"}
# quality_critic/council_agent ARE validators (reviewing them would be
# circular); client_intelligence is deterministic rule logic, not free-text
# generation; regulatory_watch quotes a real fetched page rather than
# generating a claim. Everything else is free-form LLM output and is the
# real hallucination/masking risk this check is for.
_SKIP_VALIDATION = {"client_intelligence", "quality_critic", "regulatory_watch", "council_agent"}

from .coordinator import CoordinatorAgent
from .graph import create_multi_agent_graph
from .planner import PlannerAgent
from .router import RouterAgent
from .synthesizer import SynthesizerAgent

logger = logging.getLogger(__name__)

_AGENT_CLUSTERS = [
    "aec_core", "aec_specialized", "aec_compliance", "regulatory",
    "microsoft", "cross_sell", "dynamics", "agentforce", "oracle",
    "sap", "coordination", "intelligence", "tech", "self_improvement",
    "enterprise_connectors", "physical_ai",
]

_AGENT_IDS = [
    "architect_agent", "structural_engineer", "mep_engineer", "bim_coordinator",
    "cost_estimator", "scheduler_agent", "quality_inspector", "safety_officer",
    "sustainability_agent", "procurement_agent", "contract_manager", "risk_analyst",
    "permit_agent", "site_supervisor", "materials_agent", "equipment_manager",
    "subcontractor_coordinator", "client_liaison", "document_controller", "bim_modeler",
    "code_compliance", "accessibility_agent", "fire_safety", "structural_reviewer",
    "environmental_agent", "zoning_agent", "historic_preservation", "energy_auditor",
    "lgpd_agent", "nr1_agent", "esg_agent", "tax_agent", "anticorruption_agent",
    "whistleblower_agent", "salary_equality_agent", "onboarding_agent",
    "financial_reconciliation", "cbam_agent", "carbon_inventory", "ifrs_agent",
    "dynamics_sales_agent", "dynamics_finance_agent", "dynamics_hr_agent",
    "agentforce_sdr", "agentforce_contracts", "oracle_erp_agent", "oracle_hcm_agent",
    "sap_compliance_agent", "sap_cbam_agent", "powerbi_agent",
    "meta_orchestrator", "knowledge_graph_agent", "nlp_processor",
    "ml_optimizer", "data_pipeline_agent", "api_gateway_agent",
    "security_agent", "monitoring_agent", "self_healing_agent",
    "client_intelligence", "quality_critic", "regulatory_watch", "council_agent",
]


class _AgentStub:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = "initialized"
        self.success_rate = 1.0
        self.total_tasks = 0
        self.avg_response_time = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "success_rate": self.success_rate,
            "total_tasks": self.total_tasks,
            "avg_response_time": self.avg_response_time,
        }


class Orchestrator:

    def __init__(self, settings=None):
        self.settings = settings
        self.tenant_id: str = "default"
        self.agents: Dict[str, _AgentStub] = {}
        self.llm = DeepSeekClient(settings) if settings is not None else None
        self._planner = PlannerAgent(llm_client=self.llm)
        self._router = RouterAgent(agent_registry={agent_id: True for agent_id in _AGENT_IDS})
        self._coordinator = CoordinatorAgent()
        self._synthesizer = SynthesizerAgent()
        self._graph = None
        self._executor_map: Dict[str, Any] = {}
        self._validator: QualityCriticAgent | None = None

    async def initialize(self) -> None:
        self._graph = create_multi_agent_graph()
        self.agents = {agent_id: _AgentStub(agent_id) for agent_id in _AGENT_IDS}
        self._executor_map = self._build_executor_map()
        if self.llm is not None:
            self._validator = QualityCriticAgent(self.settings, self.llm)
        logger.info(
            "Orchestrator initialized with %d agents (%d with real executors)",
            len(self.agents), len(self._executor_map),
        )

    def _build_executor_map(self) -> Dict[str, Any]:
        if self.llm is None:
            return {}

        executors: Dict[str, Any] = {}

        for agent_id, core_agent in build_core_agents(self.settings, self.llm).items():
            async def _run(task: Dict[str, Any], _agent=core_agent) -> Dict[str, Any]:
                return await _agent.handle(task)
            executors[agent_id] = _run

        bim_agent = BIMCoordinatorAgent(self.settings, self.llm)

        async def _run_bim(task: Dict[str, Any]) -> Dict[str, Any]:
            query = task.get("task", "") if isinstance(task, dict) else str(task)
            result = await asyncio.to_thread(bim_agent.generate_bim_element, query)
            await record_agent_receipt(
                agent_id="bim_coordinator",
                action="aec_query",
                arguments={"query": query[:500]},
                outcome="responded",
                risk_classification="low",
            )
            return result

        executors["bim_coordinator"] = _run_bim

        for agent_id, support_agent in build_support_agents(self.settings, self.llm).items():
            async def _run_support(task: Dict[str, Any], _agent=support_agent) -> Dict[str, Any]:
                return await _agent.handle(task)
            executors[agent_id] = _run_support

        council = CouncilAgent(self.settings, self.llm)

        async def _run_council(task: Dict[str, Any]) -> Dict[str, Any]:
            return await council.handle(task)

        executors["council_agent"] = _run_council

        return executors

    async def _validate_results(self, results: list) -> list:
        """Mandatory integrity gate: every free-form agent response gets
        reviewed by a real LLM check for hallucination/fabrication before
        it's usable downstream. A response that fails is not hidden or
        silently swapped for something safer -- it's returned with
        validated=False and the reviewer's concrete concern attached, so
        the caller sees the real problem instead of a masked answer."""
        if self._validator is None:
            return results

        async def _check(result: Dict[str, Any]) -> Dict[str, Any]:
            agent_id = result.get("agent", "")
            if "error" in result or agent_id in _SKIP_VALIDATION:
                return result
            text = result.get("response") or str(result.get("bim_element") or "")
            if not text:
                return result
            review = await self._validator.handle({"reviewed_agent": agent_id, "agent_output": text})
            result["validated"] = review["status"] == "approved"
            result["validation_note"] = review["review"] if not result["validated"] else None
            return result

        return list(await asyncio.gather(*[_check(r) for r in results]))

    async def execute_task(self, task: Dict[str, Any], user_id: str = "default") -> Dict[str, Any]:
        agent_id = task.get("agent_id", "meta_orchestrator")
        agent = self.agents.get(agent_id)

        if agent is None:
            return {"error": f"Agent '{agent_id}' not found", "status": "failed"}

        if agent_id in _DIRECT_AGENT_IDS and agent_id in self._executor_map:
            payload = task.get("payload", {})
            started = time.monotonic()
            try:
                result = await self._executor_map[agent_id](payload if isinstance(payload, dict) else {"task": payload})
            except Exception as e:
                await record_agent_execution(agent_id, int((time.monotonic() - started) * 1000), success=False, error_message=str(e))
                raise
            await record_agent_execution(agent_id, int((time.monotonic() - started) * 1000), success=True)
            await record_agent_receipt(
                agent_id=agent_id, action="direct_invoke", arguments={"payload": str(payload)[:500]},
                outcome="responded", risk_classification="low",
            )
            agent.total_tasks += 1
            return {"status": "completed", "agent_id": agent_id, "user_id": user_id, "result": result}

        plan = await self._planner.create_plan(
            query=str(task.get("payload", task)),
            context={"agents": list(self.agents.keys())},
        )

        routed = await self._router.route_batch(plan)

        results = await self._coordinator.execute_parallel(
            tasks=[{"agent": routed[i], "task": p.get("task", p)} for i, p in enumerate(plan)],
            executor_map=self._executor_map,
        )

        results = await self._validate_results(results)

        synthesis = await self._synthesizer.synthesize(results)

        agent.total_tasks += 1

        return {
            "status": "completed",
            "agent_id": agent_id,
            "user_id": user_id,
            "result": synthesis,
        }
