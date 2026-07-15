import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.security.abacus_engine import AbacusEngine


def load_policies():
    engine = AbacusEngine()
    print(f"[OK] Politicas carregadas de {engine.policy_path}")
    print(f"  Agentes especificos: {len(engine.policies.get('agent_specific', {}))}")
    print(f"  Politica padrao: {list(engine.policies.get('default', {}).keys())}")

    test_cases = [
        ("#1", "read", "public", {"role": "user"}),
        ("#1", "delete", "system", {"role": "user"}),
        ("#49", "write", "system.config", {"role": "admin"}),
        ("#12", "read", "lgpd.data", {"role": "compliance"}),
        ("#12", "read", "admin.data", {"role": "compliance"}),
    ]

    print("\nTestes de avaliacao:")
    for agent_id, action, resource, context in test_cases:
        decision = engine.evaluate(agent_id, action, resource, context)
        print(f"  {agent_id} {action} {resource} -> {decision.value}")


if __name__ == "__main__":
    load_policies()
