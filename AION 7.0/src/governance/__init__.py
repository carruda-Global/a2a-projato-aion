"""
Governance as a Service para EcoSystem AEC.

Modulos:
- PolicyEngine: regras declarativas em JSON para validar outputs dos agentes
- CriticAgent: revisor cruzado entre agentes, aponta inconsistencias
- TrustScorer: score de confianca por agente baseado em historico

Uso:
    from src.governance import PolicyEngine, CriticAgent, TrustScorer

    engine = PolicyEngine()
    engine.load_rules("src/governance/rules/default_rules.json")
    result = engine.evaluate("spec_analyst", {"analysis": "..."})

    critic = CriticAgent(llm_client)
    review = critic.review("spec_analyst", {"analysis": "..."}, previous_results=[])

    scorer = TrustScorer()
    score = scorer.get_score("spec_analyst")
"""

from .policy_engine import PolicyEngine
from .critic_agent import CriticAgent
from .trust_scorer import TrustScorer

__all__ = ["PolicyEngine", "CriticAgent", "TrustScorer"]
