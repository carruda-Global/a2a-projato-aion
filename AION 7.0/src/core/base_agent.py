from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import time
import uuid


@dataclass
class AgentContext:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = "default"
    task_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    agent_id: str
    task_id: str
    success: bool
    output: Any
    confidence: float = 1.0
    response_time: float = 0.0
    cost: float = 0.0
    tokens_used: int = 0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)


class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str, cluster: str, config: dict = None):
        self.agent_id = agent_id
        self.name = name
        self.cluster = cluster
        self.config = config or {}
        self.memory = None
        self.rag = None
        self.critic = None
        self.status = "idle"
        self.last_execution = None
        self.total_tasks = 0
        self.success_count = 0
        self.error_count = 0
        self.total_cost = 0.0
        self.avg_response_time = 0.0
        self.evolution_generation = 0
        self.budget_per_task = self.config.get("budget_per_task", 0.10)

    def set_memory(self, memory):
        self.memory = memory

    def set_rag(self, rag):
        self.rag = rag

    def set_critic(self, critic):
        self.critic = critic

    @abstractmethod
    async def execute(self, task: dict) -> AgentResult:
        pass

    async def execute_with_tracing(self, task: dict) -> AgentResult:
        context = AgentContext(
            tenant_id=task.get("tenant_id", "default"),
            task_id=task.get("task_id", str(uuid.uuid4())),
            metadata=task.get("metadata", {}),
        )

        start = time.time()
        self.status = "running"

        try:
            result = await self.execute(task)
            elapsed = time.time() - start

            result.agent_id = self.agent_id
            result.task_id = context.task_id
            result.response_time = round(elapsed, 3)

            self.last_execution = datetime.now(timezone.utc)
            self.total_tasks += 1
            self.avg_response_time = self._moving_avg(self.avg_response_time, elapsed, self.total_tasks)

            if result.success:
                self.success_count += 1
            else:
                self.error_count += 1

            if self.memory:
                await self.memory.store_execution(
                    agent_id=self.agent_id,
                    task_id=context.task_id,
                    result=result,
                )

            return result

        except Exception as e:
            elapsed = time.time() - start
            self.status = "error"
            self.error_count += 1
            self.total_tasks += 1

            return AgentResult(
                agent_id=self.agent_id,
                task_id=context.task_id,
                success=False,
                output=None,
                response_time=round(elapsed, 3),
                error=str(e),
            )

    def _moving_avg(self, old: float, new_val: float, n: int) -> float:
        return old + (new_val - old) / n

    def reset_metrics(self):
        self.total_tasks = 0
        self.success_count = 0
        self.error_count = 0
        self.total_cost = 0.0
        self.avg_response_time = 0.0

    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 1.0
        return self.success_count / self.total_tasks

    @property
    def cost_today(self) -> float:
        return self.total_cost

    @property
    def memory_usage(self) -> float:
        if self.memory:
            return self.memory.get_agent_usage(self.agent_id)
        return 0.0

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "cluster": self.cluster,
            "status": self.status,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "avg_response_time": self.avg_response_time,
            "success_rate": round(self.success_rate, 4),
            "cost_today": round(self.cost_today, 4),
            "total_tasks": self.total_tasks,
            "memory_usage": self.memory_usage,
            "evolution_generation": self.evolution_generation,
        }
