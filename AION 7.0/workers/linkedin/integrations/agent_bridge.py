"""Bridge from LinkedIn content/outreach into the real agent architecture
(src.orchestrator), so content can quote an actual live agent response
instead of a static claim about what AION does.

This only works when this code executes inside the main backend process
(app/routers/linkedin_content.py adds workers/linkedin to sys.path and
imports workflows.daily_job at request time -- that's the only path where
src.orchestrator's dependencies are actually installed). The standalone
aion-linkedin-agent worker (Dockerfile.worker, requirements-worker.txt)
does NOT have these dependencies, so this degrades to None there rather
than crashing."""
import logging

logger = logging.getLogger(__name__)


async def ask_real_architecture(agent_id: str, query: str) -> str | None:
    """Returns a real response string from a live agent, or None if the
    orchestrator isn't reachable from this process. Never raises."""
    try:
        from src.config import Settings
        from src.orchestrator import Orchestrator
    except ImportError:
        logger.info("[LinkedIn] src.orchestrator not importable from this process, skipping live example")
        return None

    try:
        settings = Settings()
        orch = Orchestrator(settings)
        await orch.initialize()
        result = await orch.execute_task({"agent_id": agent_id, "payload": query})
        synthesis = result.get("result", {})
        results = synthesis.get("results", []) if isinstance(synthesis, dict) else []
        for r in results:
            if isinstance(r, dict) and "error" not in r:
                return r.get("response") or str(r.get("result", ""))
        return None
    except Exception as e:
        logger.warning("[LinkedIn] Live architecture query failed: %s", e)
        return None
