from typing import Any


class AgentDashboard:
    def __init__(self):
        self.alert_thresholds = {
            "response_time": 5.0,
            "error_rate": 0.05,
            "budget_usage": 0.80,
        }

    def get_agent_status(self, tenant_id: str) -> dict:
        from src.core.orchestrator import HMASOrchestrator
        orchestrator = HMASOrchestrator()
        agents_status = {}

        for agent_id, agent in orchestrator.agents.items():
            agents_status[agent_id] = {
                "name": agent.name,
                "cluster": agent.cluster,
                "status": agent.status,
                "avg_response_time": agent.avg_response_time,
                "success_rate": agent.success_rate,
                "cost_today": agent.cost_today,
                "total_tasks": agent.total_tasks,
                "memory_usage": agent.memory_usage,
                "evolution_generation": agent.evolution_generation,
            }

        return {
            "agents": agents_status,
            "summary": self._get_summary(agents_status),
            "alerts": self._check_alerts(agents_status),
        }

    def _get_summary(self, agents: dict) -> dict:
        if not agents:
            return {}
        total = len(agents)
        active = sum(1 for a in agents.values() if a["status"] == "running")
        avg_success = sum(a["success_rate"] for a in agents.values()) / total if total > 0 else 0
        return {
            "total_agents": total,
            "active_agents": active,
            "avg_success_rate": round(avg_success * 100, 2),
            "total_tasks_today": sum(a["total_tasks"] for a in agents.values()),
            "total_cost_today": sum(a["cost_today"] for a in agents.values()),
            "evolution_generations": max(a["evolution_generation"] for a in agents.values()) if agents else 0,
        }

    def _check_alerts(self, agents: dict) -> list:
        alerts = []
        for agent_id, data in agents.items():
            if data["avg_response_time"] > self.alert_thresholds["response_time"]:
                alerts.append({"level": "warning", "agent": agent_id, "message": f"Resposta lenta: {data['avg_response_time']:.2f}s"})
            if data["success_rate"] < 0.95:
                alerts.append({"level": "critical", "agent": agent_id, "message": f"Taxa de erro elevada: {(1 - data['success_rate']) * 100:.1f}%"})
            if data["cost_today"] > self.alert_thresholds["budget_usage"]:
                alerts.append({"level": "warning", "agent": agent_id, "message": f"Orçamento excedido: R$ {data['cost_today']:.2f}"})
        return alerts
