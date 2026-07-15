"""Real multi-perspective review board. Works alongside the SDR: before
acting on a significant recommendation (pursue a niche, chase a lead,
launch a product angle), route it through 3 independent, genuinely
distinct-perspective LLM calls running in parallel -- not 3 near-identical
"looks good" rubber stamps."""
import asyncio

from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

_PERSPECTIVES = {
    "sales_strategist": (
        "You are a sales strategist. Evaluate the proposal purely on "
        "commercial merit: is there real buyer demand, is the price/effort "
        "ratio good, what's the fastest path to a first real sale? Be "
        "specific, not generic."
    ),
    "market_skeptic": (
        "You are a skeptical devil's advocate. Your job is to find the real "
        "reason this proposal fails: wrong buyer, wrong timing, "
        "underestimated competition, or a claim that doesn't hold up. "
        "Default to skepticism -- don't soften a real objection."
    ),
    "execution_realist": (
        "You are an execution realist for a one-person team using AI "
        "coding assistance. Judge only feasibility: can this actually be "
        "built and shipped in days, not months, with the real stack "
        "described? Flag anything that secretly requires a team, a "
        "license, or infrastructure that doesn't exist yet."
    ),
}


class CouncilAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm

    async def _ask(self, role: str, system_prompt: str, proposal: str) -> dict:
        result = await asyncio.to_thread(
            self.llm.chat, system_prompt,
            f"Proposal to evaluate:\n\n{proposal}\n\nGive your verdict in 3-5 sentences.",
            0.3, 300, "en",
        )
        return {"role": role, "verdict": result}

    async def handle(self, task: dict) -> dict:
        proposal = task.get("task", "") if isinstance(task, dict) else str(task)
        opinions = await asyncio.gather(*[
            self._ask(role, prompt, proposal) for role, prompt in _PERSPECTIVES.items()
        ])
        return {
            "agent": "council_agent",
            "proposal": proposal[:200],
            "opinions": opinions,
        }
