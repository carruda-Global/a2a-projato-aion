import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from integrations import LinkedInIntegration, LinkedInConfig
from workflows.content import run_content_workflow
from workflows.engagement_feedback import contar_publicados_hoje

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("auto-linkedin")

# "dica" dropped 2026-07-12, "calendario" dropped 2026-07-14: AggregateAnalytics
# for 2026-06-17/07-14 confirmed compliance-mill content still averages ~0 real
# engagement regardless of specific topic (a 343-impression post got zero
# reactions), while career_positioning.py's narrative posts are the only format
# converting real impressions into engagement (best post: 3 engagements on 43
# impressions, ~7%). Down to a single compliance slot/day so more of the shared
# 3-post cap goes to what's actually working, without dropping compliance
# content to zero (some prospects still search that topic specifically).
HORARIOS = [12]
TIPOS = ["news"]


class AutoLinkedInAgent:
    def __init__(self):
        self.linkedin = None
        self.running = False
        self.erros = 0
        self.posts_hoje = {"total": 0, "news": False}
        self.dia_atual = datetime.now().day
        self.indices = {"news": datetime.now().day}

    def resetar(self):
        hoje = datetime.now().day
        if hoje != self.dia_atual:
            self.posts_hoje = {"total": 0, "news": False}
            self.dia_atual = hoje
            self.indices["news"] = hoje
            self.erros = 0

    def dia_util(self):
        return datetime.now().weekday() < 5

    def tipos_pendentes(self):
        self.resetar()
        if not self.dia_util():
            return []
        return [t for t in TIPOS if not self.posts_hoje[t]]

    async def postar(self, tipo: str):
        # Cross-pipeline guard: daily_job.py and career_positioning.py also
        # publish "normal" posts on their own cron schedules. This checks the
        # shared Supabase count so this worker doesn't push the day past 3
        # normal posts total when another pipeline already used the budget.
        contagem = contar_publicados_hoje()
        if contagem["post"] >= 3:
            logger.info(f"[{tipo}] Pulado -- outro pipeline ja publicou 3 posts normais hoje.")
            self.posts_hoje[tipo] = True
            self.posts_hoje["total"] += 1
            return
        indice = self.indices.get(tipo, -1)
        result = await run_content_workflow(self.linkedin, tipo=tipo, indice=indice)
        if result.get("published"):
            self.posts_hoje[tipo] = True
            self.posts_hoje["total"] += 1
            self.erros = 0
            logger.info(f"[{tipo}] Post publicado: {result.get('tema','?')}")
        else:
            logger.warning(f"[{tipo}] Falha ao publicar: {result}")

    async def start(self):
        li_config = LinkedInConfig()
        self.linkedin = LinkedInIntegration(config=li_config)
        await self.linkedin.initialize()
        self.running = True

        logger.info("=" * 55)
        logger.info("  AGENTE LINKEDIN - 1 POST/DIA (Render)")
        logger.info("  12:00 - News (educacional sobre agentes)")
        logger.info("  (2 slots diarios reservados para career_positioning.py + daily_job.py)")
        logger.info("=" * 55)

        while self.running:
            try:
                if self.erros >= 5:
                    logger.warning("Muitos erros. Pausando 6h...")
                    await asyncio.sleep(21600)
                    self.erros = 0

                now = datetime.now()
                pendentes = self.tipos_pendentes()

                if pendentes:
                    for tipo in pendentes:
                        hora = now.hour
                        if tipo == "news" and hora >= 12:
                            logger.info(f"Publicando [{tipo}] as {now.strftime('%H:%M')}")
                            await self.postar(tipo)
                            await asyncio.sleep(60)
                else:
                    logger.info(f"1/1 post hoje. Proximo ciclo em 30min.")

                await asyncio.sleep(1800)

            except Exception as e:
                self.erros += 1
                logger.error(f"Erro fatal: {e}")
                await asyncio.sleep(1800)

    async def stop(self):
        self.running = False
        if self.linkedin:
            await self.linkedin.shutdown()


async def main():
    agent = AutoLinkedInAgent()
    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
