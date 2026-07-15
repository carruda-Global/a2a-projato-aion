import json
from typing import Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
import uuid


@dataclass
class Episode:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = "default"
    task: dict = field(default_factory=dict)
    agent_id: str = ""
    result: dict = field(default_factory=dict)
    reflection: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)


class HybridMemory:
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.episodic = EpisodicMemory(tenant_id)
        self.semantic = SemanticMemory(tenant_id)
        self.working = WorkingMemory(tenant_id)
        self._store: dict[str, list[Episode]] = {}
        self._agent_usage: dict[str, float] = {}

    async def store_execution(self, agent_id: str, task_id: str, result: Any) -> None:
        episode = Episode(
            tenant_id=self.tenant_id,
            task={"task_id": task_id},
            agent_id=agent_id,
            result=result.to_dict() if hasattr(result, "to_dict") else result,
        )

        if agent_id not in self._store:
            self._store[agent_id] = []
        self._store[agent_id].append(episode)

        if len(self._store[agent_id]) > 1000:
            self._store[agent_id] = self._store[agent_id][-1000:]

        await self.episodic.store(episode)
        self._agent_usage[agent_id] = len(self._store[agent_id])

    def store_episode(self, data: dict) -> None:
        episode = Episode(
            tenant_id=self.tenant_id,
            task=data.get("task", {}),
            agent_id=data.get("agents", [""])[0] if isinstance(data.get("agents"), list) else "",
            result=data.get("results", {}),
            reflection=data.get("evaluation", {}).get("reflection"),
            metadata={"agents_used": data.get("agents", [])},
        )
        key = str(data.get("task", {}).get("id", uuid.uuid4()))
        if key not in self._store:
            self._store[key] = []
        self._store[key].append(episode)

    def get_agent_usage(self, agent_id: str) -> float:
        return self._agent_usage.get(agent_id, 0.0) / 1000.0

    def get_recent_episodes(self, agent_id: str, limit: int = 10) -> list[Episode]:
        episodes = self._store.get(agent_id, [])
        return episodes[-limit:]

    def get_stats(self) -> dict:
        total = sum(len(v) for v in self._store.values())
        return {
            "total_episodes": total,
            "agents_with_memory": len(self._store),
            "episodic_size": self.episodic.size(),
            "semantic_size": self.semantic.size(),
            "working_contexts": self.working.count(),
        }


class EpisodicMemory:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._episodes: list[Episode] = []

    async def store(self, episode: Episode) -> None:
        self._episodes.append(episode)
        if len(self._episodes) > 5000:
            self._episodes = self._episodes[-5000:]

    def size(self) -> int:
        return len(self._episodes)

    def query(self, agent_id: str = None, limit: int = 20) -> list[Episode]:
        filtered = self._episodes
        if agent_id:
            filtered = [e for e in filtered if e.agent_id == agent_id]
        return filtered[-limit:]


class SemanticMemory:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._knowledge: dict[str, Any] = {}

    def store_knowledge(self, key: str, value: Any) -> None:
        self._knowledge[key] = value

    def get_knowledge(self, key: str) -> Optional[Any]:
        return self._knowledge.get(key)

    def size(self) -> int:
        return len(self._knowledge)


class WorkingMemory:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._contexts: dict[str, dict] = {}

    def set_context(self, session_id: str, context: dict) -> None:
        self._contexts[session_id] = {
            "data": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_context(self, session_id: str) -> Optional[dict]:
        ctx = self._contexts.get(session_id)
        if ctx:
            return ctx["data"]
        return None

    def count(self) -> int:
        return len(self._contexts)
