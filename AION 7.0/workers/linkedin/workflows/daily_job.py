"""Daily content job: 1 text post picked from the 312-item content bank,
weighted by real historical engagement per topic. This is the single entry
point an external scheduler (Render Cron Job / GitHub Actions) should call
once a day.

Carousel posting was removed 2026-07-12: AggregateAnalytics for
2026-07-06/12 showed 0 engagement across every carousel published that
week (Procurement Copilot, Engineering Copilot, Vendor Risk, CSRD,
Anti-Corruption, LGPD Operacional -- 7 posts, 16-70 impressions each,
zero likes/comments/shares on any of them), against a real signal on text
posts. Not worth the daily posting-cap slot it was consuming."""
import logging
from integrations import LinkedInIntegration, LinkedInConfig
from workflows.content_bank import escolher_variacao
from workflows.engagement_feedback import calcular_pesos_topico, registrar_publicacao, contar_publicados_hoje

logger = logging.getLogger(__name__)


async def _publicar_post_texto(linkedin: LinkedInIntegration, pesos: dict) -> dict:
    variacao = await escolher_variacao(pesos)
    result = await linkedin.tools.create_post(text=variacao["texto"])
    if "error" in result:
        return {"published": False, "error": result["error"], "combo_id": variacao["combo_id"]}
    await linkedin.tools.create_comment(result["post_id"], variacao["link_comentario"])
    return {
        "published": True, "post_id": result["post_id"], "url": result.get("url", ""),
        "combo_id": variacao["combo_id"], "topico": variacao["topico"]["id"],
    }


async def run_daily_content_job() -> dict:
    li_config = LinkedInConfig()
    linkedin = LinkedInIntegration(config=li_config)
    await linkedin.initialize()

    try:
        # Cross-pipeline guard: agent.py and career_positioning.py also
        # publish "normal" posts on their own schedules. Checked against the
        # shared Supabase count so this job doesn't push the day past the
        # 3 normal posts/day total.
        contagem = contar_publicados_hoje()
        pesos = await calcular_pesos_topico(linkedin)
        logger.info(f"Pesos por topico calculados: {pesos}")

        if contagem["post"] >= 3:
            post_result = {"published": False, "skipped": "daily normal-post quota (3) already met by another pipeline"}
        else:
            post_result = await _publicar_post_texto(linkedin, pesos)
            if post_result.get("published"):
                registrar_publicacao(post_result["post_id"], post_result["topico"], "post", post_result["url"])

        return {"post": post_result}
    finally:
        await linkedin.shutdown()
