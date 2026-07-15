class ClientIntelligenceAgent:
    def __init__(self, settings, llm=None):
        self.settings = settings
        self.llm = llm

    async def analyze_profile(self, tenant_id: str, tenant_context: dict = None) -> dict:
        ctx = tenant_context or {}
        industry = ctx.get("industry", "unknown")
        employee_count = ctx.get("employee_count", 0)
        active_agents = ctx.get("active_agents", [])

        recommendations = []
        if employee_count > 20 and "nr1_psicossocial" not in active_agents:
            recommendations.append({"agent": "nr1_psicossocial", "reason": "Obrigatório para empresas com funcionários CLT", "urgency": "alta"})
        if employee_count > 100 and "igualdade_salarial" not in active_agents:
            recommendations.append({"agent": "igualdade_salarial", "reason": "Obrigatório para empresas com 100+ funcionários", "urgency": "alta"})

        return {
            "agent_id": "client_intelligence",
            "tenant_id": tenant_id,
            "industry": industry,
            "employee_count": employee_count,
            "compliance_score_pct": ctx.get("compliance_score", 0),
            "recommendations": recommendations,
        }
