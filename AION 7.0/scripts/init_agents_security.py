import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["APP_ENV"] = "development"

from src.security.aip import AIPRegistry, AIPProxy, AgentIdentity
from src.security.aip.token import PrincipalToken

registry = AIPRegistry()
identity = AgentIdentity(registry)
proxy = AIPProxy(registry)

AGENTS = [
    ("spec_analyst", "Spec Analyst"),
    ("procurement", "Procurement"),
    ("inventory", "Inventory"),
    ("logistics", "Logistics"),
    ("field_execution", "Field Execution"),
    ("bim_coordinator", "BIM Coordinator"),
    ("requirements_analyst", "Requirements Analyst"),
    ("engineering_assistant", "Engineering Assistant"),
    ("work_synopsis", "Work Synopsis"),
    ("photo_intelligence", "Photo Intelligence"),
    ("rfi_creation", "RFI Creation"),
    ("compliance", "Compliance Agent"),
    ("nr1_psicossocial", "NR-1 Psicossocial"),
    ("tributario_cbs_ibs", "Tributario CBS/IBS"),
    ("lgpd_operacional", "LGPD Operacional"),
    ("esg_ifrs", "ESG IFRS"),
    ("inventario_carbono", "Inventario Carbono"),
    ("escopo3_fornecedores", "Escopo 3 Fornecedores"),
    ("canal_denuncias", "Canal de Denuncias"),
    ("igualdade_salarial", "Igualdade Salarial"),
    ("compliance_anticorrupcao", "Compliance Anticorrupcao"),
    ("regulatory_analyst", "Regulatory Analyst"),
    ("compliance_pm", "Compliance PM"),
    ("channel_agent", "Channel Agent"),
    ("knowledge_agent", "Knowledge Agent"),
    ("facilitator_agent", "Facilitator Agent"),
    ("dev_experience", "Dev Experience Agent"),
]

PRINCIPAL = "Cristiano Arruda (CREA-SP 5071200171)"

print(f"Registrando {len(AGENTS)} agentes...")
for agent_key, agent_name in AGENTS:
    record = registry.register_agent(agent_key, PRINCIPAL)
    print(f"  [{record['agent_id']}] {agent_name}")

print("\nDelegation chain principal:")
print(f"  Cristiano Arruda -> compliance -> compliance_pm -> channel_agent")
print(f"  Cristiano Arruda -> regulatory_analyst -> knowledge_agent -> facilitator_agent")

print("\nEmitindo tokens AIP...")
token_manager = PrincipalToken(registry, identity)

token = token_manager.issue_token("compliance", "compliance_pm", PRINCIPAL)
if token:
    print(f"  Token compliance -> compliance_pm: {token['token_id'][:16]}...")

token2 = token_manager.issue_token("compliance_pm", "channel_agent", PRINCIPAL)
if token2:
    print(f"  Token compliance_pm -> channel_agent: {token2['token_id'][:16]}...")

print(f"\nTotal registrados: {len(registry.list_agents())}")
print(f"Total ativos: {sum(1 for a in registry.list_agents() if a['status'] == 'active')}")
