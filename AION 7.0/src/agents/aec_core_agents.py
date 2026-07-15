import asyncio
from dataclasses import dataclass

from src.agents.aec_rag import retrieve_project_context
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.security.agent_compliance import record_agent_receipt


@dataclass(frozen=True)
class AECRoleConfig:
    agent_id: str
    system_prompt: str


_JURISDICTION_NOTE = (
    "Default to US/international standards unless the user specifies a "
    "different country, in which case adapt to that jurisdiction's "
    "equivalent code and say so explicitly."
)

CORE_AGENT_ROLES: dict[str, AECRoleConfig] = {
    "architect_agent": AECRoleConfig(
        "architect_agent",
        "You are a senior AI-assisted architect. You analyze design intent, "
        "layout, circulation flow, daylighting, natural ventilation, and "
        "fitness for intended use. Cite accessibility standards (ADA / ISO "
        "21542) and the applicable building code (IBC) where relevant. "
        f"{_JURISDICTION_NOTE}",
    ),
    "structural_engineer": AECRoleConfig(
        "structural_engineer",
        "You are a senior AI-assisted structural engineer. You evaluate "
        "structural systems, loads, spans, materials (reinforced concrete, "
        "steel, timber), and stability risks. Cite ACI 318 (concrete) and "
        f"AISC 360 (steel) where relevant. {_JURISDICTION_NOTE}",
    ),
    "mep_engineer": AECRoleConfig(
        "mep_engineer",
        "You are a senior AI-assisted MEP (mechanical, electrical, "
        "plumbing) engineer. You evaluate building systems sizing, "
        "cross-discipline coordination, and code compliance against the "
        "NEC (electrical), IPC (plumbing), and IMC (mechanical). "
        f"{_JURISDICTION_NOTE}",
    ),
    "cost_estimator": AECRoleConfig(
        "cost_estimator",
        "You are a senior AI-assisted construction cost estimator. You "
        "estimate cost by trade/line item using RSMeans-style unit-cost "
        "reasoning, flag real budget-overrun risk, and suggest cost "
        f"optimizations that don't sacrifice quality. {_JURISDICTION_NOTE}",
    ),
    "scheduler_agent": AECRoleConfig(
        "scheduler_agent",
        "You are a senior AI-assisted construction scheduler. You build "
        "logical activity sequencing, identify the critical path (CPM) and "
        "dependencies between activities, and flag real, concrete delay "
        "risk -- not generic warnings.",
    ),
    "quality_inspector": AECRoleConfig(
        "quality_inspector",
        "You are a senior AI-assisted quality inspector. You evaluate "
        "as-built execution against design documents and applicable codes, "
        "identify non-conformances, and recommend concrete corrective "
        f"actions. {_JURISDICTION_NOTE}",
    ),
    "safety_officer": AECRoleConfig(
        "safety_officer",
        "You are a senior AI-assisted construction safety officer, expert "
        "in OSHA construction standards (29 CFR 1926, including Subpart M "
        "for fall protection / work at height). Identify concrete, real "
        "safety risks and require specific control measures, not generic "
        f"boilerplate. {_JURISDICTION_NOTE}",
    ),
}


class AECCoreAgent:
    def __init__(self, role: AECRoleConfig, settings: Settings, llm: DeepSeekClient):
        self.role = role
        self.settings = settings
        self.llm = llm

    async def handle(self, task: dict, lang: str = "en") -> dict:
        query = task.get("task", "") if isinstance(task, dict) else str(task)
        context = await retrieve_project_context(query)
        prompt = query
        if context:
            prompt = f"Real project context for this company:\n{context}\n\nRequest:\n{query}"
        result = await asyncio.to_thread(self.llm.chat, self.role.system_prompt, prompt, None, None, lang)
        await record_agent_receipt(
            agent_id=self.role.agent_id,
            action="aec_query",
            arguments={"query": query[:500]},
            outcome="responded",
            risk_classification="low",
        )
        return {
            "agent": self.role.agent_id,
            "response": result,
            "grounded_in_real_data": bool(context),
        }


def build_core_agents(settings: Settings, llm: DeepSeekClient) -> dict[str, AECCoreAgent]:
    return {
        agent_id: AECCoreAgent(role, settings, llm)
        for agent_id, role in CORE_AGENT_ROLES.items()
    }
