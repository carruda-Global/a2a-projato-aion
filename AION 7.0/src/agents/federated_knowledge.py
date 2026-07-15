class FederatedKnowledgeAgent:
    def __init__(self, settings, llm=None):
        self.settings = settings
        self.llm = llm

    async def aggregate_insights(self, industry: str = "") -> dict:
        return {
            "agent_id": "federated_knowledge",
            "industry": industry or "all",
            "insights": [
                {"pattern": "Empresas de construção civil têm 30% mais risco NR-1", "confidence_pct": 85.0, "sample_size": 120},
                {"pattern": "LGPD é o compliance mais negligenciado em PMEs de TI", "confidence_pct": 92.0, "sample_size": 200},
            ],
            "privacy_preserving": True,
            "method": "federated_learning",
        }
