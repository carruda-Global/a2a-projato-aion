from src.api.claude_client import ClaudeClient
from src.config import Settings

ORCHESTRATOR_SYSTEM_PROMPT = """
Você é o orquestrador central do EcoSystem 3.0.
Dado um objetivo do cliente, você:
1. Identifica quais obrigações legais estão ativas
2. Ordena os agentes por urgência (multa, prazo, risco)
3. Cria um plano de 30/60/90 dias
4. Delega para os agentes especializados via A2A
5. Monitora resultados e ajusta o plano
Sempre priorize obrigações com multa ativa antes de otimizações.
"""

class MasterOrchestratorAgent:
    def __init__(self, settings: Settings, llm=None):
        self.settings = settings
        self.llm = llm
        self.reasoning_llm = ClaudeClient()

    async def create_plan(self, objective: str, tenant_context: dict = None) -> dict:
        context = tenant_context or {}
        plan_30d = []
        plan_60d = []
        plan_90d = []

        urgent_obligations = context.get("urgent_obligations", [])
        if any(o in str(urgent_obligations) for o in ["NR-1", "psicossocial", "não conformidade"]):
            plan_30d.append({"agent": "nr1_psicossocial", "priority": "critical", "deadline": "30 dias"})
        if any(o in str(urgent_obligations) for o in ["LGPD", "ANPD", "dados pessoais"]):
            plan_30d.append({"agent": "lgpd_operacional", "priority": "critical", "deadline": "30 dias"})
        if any(o in str(urgent_obligations) for o in ["denúncias", "assédio", "CIPA"]):
            plan_60d.append({"agent": "canal_denuncias", "priority": "high", "deadline": "60 dias"})
        if any(o in str(urgent_obligations) for o in ["igualdade", "salarial", "equidade"]):
            plan_60d.append({"agent": "igualdade_salarial", "priority": "high", "deadline": "60 dias"})

        plan_90d.append({"agent": "conciliacao_financeira", "priority": "medium", "deadline": "90 dias"})
        plan_90d.append({"agent": "atendimento_cliente_ptbr", "priority": "medium", "deadline": "90 dias"})

        return {
            "agent_id": "master_orchestrator",
            "objective": objective,
            "plan": {
                "30_days": plan_30d,
                "60_days": plan_60d,
                "90_days": plan_90d,
            },
            "total_agents_required": len(plan_30d) + len(plan_60d) + len(plan_90d),
            "estimated_monthly_cost_brl": sum(
                [390 for _ in plan_30d] + [290 for _ in plan_60d] + [490 for _ in plan_90d]
            ),
        }
