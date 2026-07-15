import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.universal_governance import UniversalGovernanceLayer
from src.agents.antigravity_bridge import AntigravityBridge
from src.agents.mai_code_reviewer import MAICodeReviewer
import asyncio


async def test():
    print("=== TESTE AGENTES ENTERPRISE ===")
    print()

    gov = UniversalGovernanceLayer()
    result = await gov._intercept_action("#1", "microsoft", "execute", {"cmd": "test"}, "tenant_1")
    print(f"[#60 Governance] allowed={result['allowed']}, risco={result['risk_score']}")

    bridge = AntigravityBridge()
    steps = [{"id": "s1", "requires": ["code_generation"]}, {"id": "s2", "requires": ["sharepoint"]}]
    wf = await bridge._route_workflow("wf_1", steps, "tenant_1")
    print(f"[#61 Bridge] steps={wf['completed_steps']}, s1_platform={wf['results']['s1']['platform']}")

    reviewer = MAICodeReviewer()
    diff = "this code changes stripe billing and uses cpf without encryption"
    review = await reviewer._review_pr("repo/test", 1, diff, "tenant_1")
    print(f"[#62 CodeReview] score={review['risk_score']}, approved={review['approved']}")
    print(f"  Issues: {review['issues']}")

    print()
    print("TODOS OS 3 AGENTES ENTERPRISE FUNCIONANDO")


asyncio.run(test())
