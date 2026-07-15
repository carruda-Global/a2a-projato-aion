"""Real, LLM-backed replacements for the 3 architecture-support agents worth
keeping (client_intelligence, quality_critic, regulatory_watch). The other 6
in this cluster (meta_learning, ecosystem_evolution, federated_knowledge,
software_engineering, sales_agent, workforce_orchestrator) returned fixed,
fabricated output with no real logic behind them and were deliberately left
unwired rather than rebuilt or connected."""
import asyncio
import logging

import httpx

from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

logger = logging.getLogger(__name__)

REGULATORY_SOURCES = {
    "labor": "https://www.gov.br/trabalho-e-emprego/pt-br",
    "data_protection": "https://www.gov.br/anpd/pt-br",
    "tax": "https://www.gov.br/receita/pt-br",
    "securities": "https://www.cvm.gov.br",
    "official_gazette": "https://www.in.gov.br/servicos/pesquisa-dou",
}


class ClientIntelligenceAgent:
    """Deterministic, rule-based -- not an LLM call. Flags real compliance
    gaps from real tenant data instead of guessing. Returns an empty
    recommendation list (not a fabricated one) when there's no real
    tenant_context to reason from."""

    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm

    async def handle(self, task: dict) -> dict:
        tenant_context = task.get("tenant_context") if isinstance(task, dict) else None
        tenant_context = tenant_context or {}
        employee_count = tenant_context.get("employee_count", 0)
        active_agents = tenant_context.get("active_agents", [])

        recommendations = []
        if employee_count > 20 and "nr1_agent" not in active_agents:
            recommendations.append({
                "agent": "nr1_agent",
                "reason": "Companies with employees under Brazilian CLT need an NR-1 psychosocial risk inventory",
                "urgency": "high",
            })
        if employee_count > 100 and "salary_equality_agent" not in active_agents:
            recommendations.append({
                "agent": "salary_equality_agent",
                "reason": "Companies with 100+ employees have salary-equity reporting obligations",
                "urgency": "high",
            })

        return {
            "agent": "client_intelligence",
            "employee_count": employee_count,
            "recommendations": recommendations,
            "note": "no tenant_context provided" if not tenant_context else None,
        }


class QualityCriticAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "You are a strict quality reviewer for another AI agent's output. "
            "Check for: factual plausibility, internal consistency, whether it "
            "actually answers the request, and any sign of hallucinated "
            "citations or fabricated numbers. Be specific about what's wrong, "
            "if anything -- don't just say it looks fine."
        )

    async def handle(self, task: dict) -> dict:
        agent_output = task.get("agent_output", "") if isinstance(task, dict) else str(task)
        reviewed_agent = task.get("reviewed_agent", "unknown") if isinstance(task, dict) else "unknown"
        prompt = (
            f"Output from agent '{reviewed_agent}' to review:\n\n{agent_output}\n\n"
            "Reply with: VERDICT (approved / needs_revision) on the first line, "
            "then concrete issues found (or 'none') below it."
        )
        result = await asyncio.to_thread(self.llm.chat, self.system_prompt, prompt, 0.0, 500, "en")
        # Exact-prefix match only, fail-safe to needs_revision. A substring
        # check like `"approved" in first_line` would misclassify a real
        # rejection ("VERDICT: NOT APPROVED - ...") as approved, since
        # "approved" is a substring of "not approved" -- masking a real
        # failure as a pass.
        first_line = result.strip().split("\n")[0].strip().lower()
        status = "approved" if first_line.startswith("verdict: approved") else "needs_revision"
        return {"agent": "quality_critic", "reviewed_agent": reviewed_agent, "status": status, "review": result}


class RegulatoryWatchAgent:
    """Real fetch of the listed government sources, real LLM summary of
    what's currently on the page. Note: this is a live snapshot, not a
    diff against a prior crawl -- it can't claim to detect 'what changed'
    without a stored baseline, so it doesn't pretend to."""

    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "You summarize the current content of a Brazilian government "
            "regulatory portal page for a compliance monitoring tool. State "
            "only what is actually visible on the page. If the page is a "
            "search portal with no substantive content, say so plainly -- "
            "do not invent regulatory news."
        )

    async def handle(self, task: dict) -> dict:
        area = task.get("area", "labor") if isinstance(task, dict) else "labor"
        url = REGULATORY_SOURCES.get(area, REGULATORY_SOURCES["labor"])
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                text = r.text[:6000]
        except Exception as e:
            logger.warning("[RegulatoryWatch] Failed to fetch %s: %s", url, e)
            return {"agent": "regulatory_watch", "source": url, "error": f"fetch failed: {e}"}

        summary = await asyncio.to_thread(
            self.llm.chat, self.system_prompt,
            f"Raw HTML/text from {url}:\n\n{text}\n\nSummarize what's on this page.",
            0.2, 400, "en",
        )
        return {"agent": "regulatory_watch", "source": url, "summary": summary}


def build_support_agents(settings: Settings, llm: DeepSeekClient) -> dict:
    return {
        "client_intelligence": ClientIntelligenceAgent(settings, llm),
        "quality_critic": QualityCriticAgent(settings, llm),
        "regulatory_watch": RegulatoryWatchAgent(settings, llm),
    }
