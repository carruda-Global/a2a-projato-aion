"""Daily personal career-positioning post -- separate from daily_job.py's
compliance-topic content bank, since this is first-person career narrative
("I built X"), not AION-product/compliance content.

Deliberately NOT LLM-generated at request time: this worker's Docker image
(Dockerfile.worker + requirements-worker.txt) doesn't install the `openai`
package or expose an LLM API key, and adding one just for this would mean a
new Render env var the user has to set manually. A small bank of real,
pre-written, honest posts rotated by day covers "alternate the text daily"
without that dependency -- same tradeoff daily_job.py already made with its
312-item static content bank.
"""
import logging
from datetime import date

from integrations import LinkedInIntegration, LinkedInConfig
from workflows.engagement_feedback import registrar_publicacao, contar_publicados_hoje

logger = logging.getLogger(__name__)

_POSTS = [
    """For over 10 years, I managed engineering projects worth millions of dollars for multinational companies -- budgets, timelines, teams across 6 countries.

Then I decided to stop managing other people's technology and start building my own.

Today I run AION, a multi-agent AI platform with 71 agents in production -- including an AI Voice Receptionist that answers real business calls 24/7 for small businesses in the US, UK, Canada, and Australia. Real customers, real Stripe billing, not a demo.

The project management discipline didn't go away -- it's exactly what makes the difference between a working prototype and a product that survives contact with real users.

Open to select AI engineering projects. Comment or DM if you're building something in this space.""",

    """Found something this week that most "AI engineer" portfolios don't show: a broken production system, and the process of fixing it.

A Kubernetes cluster had been running silently for days, unhealthy, burning real cloud spend with zero traffic going through it -- a leftover from an earlier deployment attempt nobody noticed.

Diagnosed it directly from billing data down to the exact SKU, found the cluster, killed it. Not glamorous, but it's the actual job: production AI systems don't run themselves, and half the work is noticing what's quietly broken before it costs real money.

That's the difference between a tutorial project and something running in production with paying customers.

If you need someone who can own an AI system end-to-end -- not just prototype it -- let's talk.""",

    """Before writing a single line of code for my last product, I pulled real Google Keyword Planner data and looked at what funded competitors were actually doing -- not what I assumed the market wanted.

That data pointed to something specific: an AI voice receptionist for small businesses, a category growing double digits year over year, with a real gap in pricing (most competitors charge per call or cap you at a fixed number of customers).

Built it on that evidence. It's live today -- AION Voice Receptionist, real customers across the US, UK, Canada, and Australia.

Data-driven doesn't mean slower. It means building the right thing once instead of the wrong thing three times.

Building something and want a second pair of eyes on the market evidence? Comment below.""",

    """Why LangGraph instead of a simpler single-agent chain? I get asked this a lot.

Because the moment you need agents that check each other's work, retry on failure, or hand off between specialized roles, a linear chain breaks down fast. AION runs 71 agents this way -- including a dedicated quality-review agent that checks every other agent's output before it's ever shown to a user.

That one architectural decision is the difference between "looks good in a demo" and "actually reliable when a real customer is on the other end."

Happy to talk architecture with anyone building multi-agent systems -- comment or DM.""",

    """Found a bug this week that had been silently breaking an entire automated pipeline since the day it was built -- it looked like it was working (logs said "completed"), but a missing method meant zero real output for its entire operational history.

Nobody noticed because the failure was silent, not loud. That's the dangerous kind.

The fix took an hour. Finding it took actually auditing the automation instead of trusting that "no errors in the log" means "working."

That's most of what real AI engineering work looks like day to day -- not the exciting part, but the part that decides whether a system is actually production-grade.

If you've got an AI pipeline you're not 100% sure is doing what you think it's doing, that's exactly the kind of project I take on.""",

    """A quick rundown of what I actually do, since I get asked: I design and build multi-agent AI systems end to end -- architecture, orchestration (LangGraph), backend (FastAPI/Postgres), real integrations (payments, voice/telephony, CRM), and the unglamorous parts too: production debugging, cost anomalies, silent failures.

Built and currently run AION, 71 agents in production, including a real AI Voice Receptionist product with paying customers.

Not a bootcamp portfolio piece -- a live system handling real traffic today.

Taking on select AI engineering projects. Comment or DM if that's useful to you.""",
]


async def run_career_positioning_job() -> dict:
    """Called once a day by an external scheduler. Rotates deterministically
    by day-of-year so the same post never fires twice in a row and the whole
    bank cycles before repeating."""
    # Cross-pipeline guard: agent.py and daily_job.py also publish "normal"
    # posts on their own schedules. This checks the shared Supabase count so
    # this job doesn't push the day past 3 normal posts total.
    contagem = contar_publicados_hoje()
    if contagem["post"] >= 3:
        logger.info("[CareerPositioning] Pulado -- outro pipeline ja publicou 3 posts normais hoje.")
        return {"published": False, "skipped": "daily normal-post quota (3) already met by another pipeline"}

    indice = date.today().toordinal() % len(_POSTS)
    text = _POSTS[indice]

    li_config = LinkedInConfig()
    linkedin = LinkedInIntegration(config=li_config)
    await linkedin.initialize()
    try:
        result = await linkedin.tools.create_post(text=text)
        if "error" in result:
            logger.error("[CareerPositioning] Post failed: %s", result["error"])
            return {"published": False, "error": result["error"]}
        registrar_publicacao(result["post_id"], f"career-{indice}", "post", result.get("url", ""))
        logger.info("[CareerPositioning] Published: %s", result.get("url"))
        return {"published": True, "post_id": result["post_id"], "url": result.get("url", "")}
    finally:
        await linkedin.shutdown()
