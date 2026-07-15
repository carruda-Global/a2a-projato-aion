"""
AION - Agents Intelligence Orchestration Network
ADK root agent for Google Cloud Agent Runtime deployment.
"""
import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "global-engenharia-498823")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


def query_aion_agent(agent_id: str, query: str, context: str = "") -> str:
    """Route a query to one of AION's 78 specialized agents.

    Args:
        agent_id: Agent identifier (e.g. 'nr1_psicossocial', 'lgpd_compliance').
        query: The user's question or task description.
        context: Optional additional context (project name, company, etc.).

    Returns:
        Agent response as a string.
    """
    import httpx

    base_url = os.environ.get(
        "AION_BASE_URL", "https://engenheiro-producao-ai.onrender.com"
    )
    try:
        response = httpx.post(
            f"{base_url}/a2a/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "tasks/send",
                "params": {
                    "id": f"adk-{agent_id}",
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": f"[Agent: {agent_id}] {context}\n{query}"}],
                    },
                },
                "id": 1,
            },
            timeout=60,
        )
        result = response.json()
        if "result" in result:
            parts = result["result"].get("artifacts", [{}])[0].get("parts", [{}])
            return parts[0].get("text", str(result["result"]))
        return str(result.get("error", "No response"))
    except Exception as exc:
        return f"Error calling AION agent {agent_id}: {exc}"


def list_available_agents(category: str = "") -> str:
    """List AION's available specialized agents.

    Args:
        category: Optional filter by category
            (compliance, erp, engineering, safety, esg, hr).

    Returns:
        JSON list of available agents and their descriptions.
    """
    agents = {
        "compliance": [
            "nr1_psicossocial - NR-1 Psychosocial Risk Assessment",
            "lgpd_compliance - LGPD Data Privacy Compliance",
            "esg_reporting - ESG Environmental/Social/Governance Reporting",
            "iso_45001 - ISO 45001 Occupational Safety",
            "nr35_trabalho_altura - NR-35 Work at Height",
        ],
        "erp": [
            "sap_s4hana - SAP S/4HANA Integration",
            "oracle_fusion - Oracle Fusion Cloud",
            "dynamics_365 - Microsoft Dynamics 365",
            "salesforce_agentforce - Salesforce Agentforce",
        ],
        "engineering": [
            "producao_engenharia - Production Engineering",
            "qualidade_obra - Construction Quality Control",
            "cronograma_obra - Project Schedule Management",
            "orcamento_obra - Construction Budget",
            "gestao_riscos - Risk Management",
        ],
        "safety": [
            "seguranca_trabalho - Occupational Safety",
            "apt_trabalho - Work Permit Management",
            "epi_gestao - PPE Management",
            "acidente_investigacao - Accident Investigation",
        ],
    }
    if category and category in agents:
        return str({category: agents[category]})
    return str(agents)


root_agent = Agent(
    name="aion_orchestrator",
    model=Gemini(
        model="gemini-2.0-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "AION - Agents Intelligence Orchestration Network. "
        "78 AI agents for Engineering, Construction, Regulatory Compliance "
        "(NR-1, LGPD, ESG), and ERP Integration (SAP, Oracle, Dynamics, Salesforce)."
    ),
    instruction=(
        "You are AION, an AI orchestrator managing 78 specialized agents for Global Engenharia. "
        "Help users with: engineering production, construction management, regulatory compliance "
        "(NR-1, LGPD, ESG, ISO 45001), and ERP systems (SAP S/4HANA, Oracle Fusion, "
        "Microsoft Dynamics 365, Salesforce Agentforce). "
        "Use list_available_agents to show what you can do. "
        "Use query_aion_agent to invoke specific specialized agents. "
        "Always respond in the same language the user writes (Portuguese or English)."
    ),
    tools=[list_available_agents, query_aion_agent],
)

app = App(
    root_agent=root_agent,
    name="app",
)
