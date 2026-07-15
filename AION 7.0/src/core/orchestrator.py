from typing import Any
from src.clusters import CLUSTERS
from src.memory.hybrid_memory import HybridMemory
from src.rag.hybrid_rag import HybridRAG
from src.evolution.group_evolution import GroupEvolution
from src.evolution.reflection_module import ReflectionModule
from src.rl.global_rl import GlobalRL
from src.rl.reward_model import RewardModel
from src.security.circuit_breaker import CircuitBreaker
from src.security.audit_trail import AuditTrail


class CriticAgent:
    def __init__(self):
        self.reflection_module = ReflectionModule()

    async def evaluate(self, results: dict) -> dict:
        needs_correction = False
        corrections = []

        for agent_id, result in results.items():
            if isinstance(result, Exception):
                needs_correction = True
                corrections.append({"agent": agent_id, "action": "retry"})
                continue

            if hasattr(result, "success") and not result.success:
                needs_correction = True
                corrections.append({"agent": agent_id, "action": "fallback", "reason": result.error})

            if hasattr(result, "confidence") and result.confidence < 0.5:
                needs_correction = True
                corrections.append({"agent": agent_id, "action": "review", "confidence": result.confidence})

        return {
            "needs_correction": needs_correction,
            "corrections": corrections,
            "reflection": self._generate_reflection(results),
        }

    def _generate_reflection(self, results: dict) -> str:
        total = len(results)
        successes = sum(1 for r in results.values() if hasattr(r, "success") and r.success)
        if total == 0:
            return "Nenhum resultado para avaliar."
        return f"{successes}/{total} agentes executaram com sucesso."


class HMASOrchestrator:
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.agents: dict[str, Any] = {}
        self.memory = HybridMemory(tenant_id)
        self.rag = HybridRAG(tenant_id)
        self.critic = CriticAgent()
        self.evolution = GroupEvolution(population_size=27)
        self.rl_global = GlobalRL(tenant_id)
        self.rl_local = {}
        self.reward_model = RewardModel()
        self.circuit_breaker = CircuitBreaker(threshold=5, reset_seconds=60)
        self.audit = AuditTrail()
        self.max_parallel = 10

    async def initialize(self):
        for cluster_name, cluster_agents in CLUSTERS.items():
            for agent_id, agent_class in cluster_agents.items():
                try:
                    agent = agent_class(config={"budget_per_task": 0.10})
                    agent.set_memory(self.memory)
                    agent.set_rag(self.rag)
                    agent.set_critic(self.critic)
                except TypeError:
                    from src.config import Settings
                    from src.api.deepseek_client import DeepSeekClient
                    settings = Settings()
                    llm = DeepSeekClient(settings)
                    agent = agent_class(settings, llm)
                self.agents[agent_id] = agent
                self.evolution.register_agent(agent_id)

    async def execute_task(self, task: dict, user_id: str = "anonymous") -> dict:
        required_agents = self._identify_required_agents(task)
        plan = await self._plan_execution(task, required_agents)
        results = await self._execute_in_parallel(plan)

        evaluation = await self.critic.evaluate(results)
        if evaluation["needs_correction"]:
            results = await self._correct_results(results, evaluation["corrections"])

        self.memory.store_episode({
            "task": task,
            "agents": required_agents,
            "results": self._serialize_results(results),
            "evaluation": evaluation,
        })

        self.audit.record("task_executed", "orchestrator", self.tenant_id, {
            "task_id": task.get("id"),
            "agents_used": required_agents,
            "success": evaluation["needs_correction"] is False,
        })

        return {
            "task_id": task.get("id"),
            "results": self._serialize_results(results),
            "evaluation": evaluation,
            "agents_used": required_agents,
        }

    def _identify_required_agents(self, task: dict) -> list[str]:
        cluster = task.get("cluster", "production")
        if cluster in CLUSTERS:
            return list(CLUSTERS[cluster].keys())
        return list(self.agents.keys())

    async def _plan_execution(self, task: dict, agents: list[str]) -> dict:
        return {"tasks": {a: task for a in agents}, "parallel": True}

    async def _execute_in_parallel(self, plan: dict) -> dict:
        import asyncio

        semaphore = asyncio.Semaphore(self.max_parallel)
        results = {}

        async def run_agent(agent_name: str, agent_task: dict):
            async with semaphore:
                agent = self.agents.get(agent_name)
                if not agent:
                    results[agent_name] = Exception(f"Agent {agent_name} not found")
                    return
                try:
                    result = await self.circuit_breaker.call_async(agent_name, agent.execute_with_tracing, agent_task)
                    results[agent_name] = result
                    self.rl_global.update({agent_name: result})
                    self.evolution.record_performance(agent_name, 1.0 if result.success else 0.0)
                except Exception as e:
                    results[agent_name] = e
                    self.evolution.record_performance(agent_name, 0.0)

        tasks = [run_agent(name, t) for name, t in plan["tasks"].items()]
        await asyncio.gather(*tasks, return_exceptions=True)

        return results

    async def _correct_results(self, results: dict, corrections: list) -> dict:
        import asyncio

        for correction in corrections:
            agent_id = correction.get("agent")
            action = correction.get("action")
            if action == "retry" and agent_id in self.agents:
                agent = self.agents[agent_id]
                result = await agent.execute_with_tracing({})
                results[agent_id] = result
                self.rl_global.update({agent_id: result})
        return results

    def _serialize_results(self, results: dict) -> dict:
        serialized = {}
        for k, v in results.items():
            if isinstance(v, Exception):
                serialized[k] = {"error": str(v), "success": False}
            elif hasattr(v, "__dict__"):
                serialized[k] = v.__dict__
            else:
                serialized[k] = v
        return serialized
