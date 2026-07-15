import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict
from .database import SessionLocal
from . import models

logger = logging.getLogger(__name__)

PIPELINE_STAGES = [
    "visitou_site",
    "preencheu_formulario",
    "lead_capturado",
    "nutricao_iniciada",
    "qualificado",
    "demonstracao_agendada",
    "proposta_enviada",
    "fechado",
    "perdido",
]


class SalesMonitor:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def pipeline_summary(self) -> dict:
        leads_total = self.db.query(models.Lead).count()
        leads_site = self.db.query(models.Lead).filter(models.Lead.source == "site_landing_page").count()
        leads_linkedin = self.db.query(models.Lead).filter(models.Lead.source == "linkedin").count()

        deals = self.db.query(models.Deal).all()
        deals_por_estagio = defaultdict(list)
        for d in deals:
            deals_por_estagio[d.stage].append(d)

        won = len(deals_por_estagio.get(models.DealStage.CLOSED_WON.value, []))
        lost = len(deals_por_estagio.get(models.DealStage.CLOSED_LOST.value, []))
        active = sum(len(v) for k, v in deals_por_estagio.items()
                     if k not in (models.DealStage.CLOSED_WON.value, models.DealStage.CLOSED_LOST.value))

        return {
            "leads": {
                "total": leads_total,
                "site": leads_site,
                "linkedin": leads_linkedin,
                "outros": leads_total - leads_site - leads_linkedin,
            },
            "pipeline": {
                "deals_ativos": active,
                "deals_ganhos": won,
                "deals_perdidos": lost,
                "valor_total": sum(d.value for d in deals),
                "valor_ganho": sum(d.value for d in deals_por_estagio.get(models.DealStage.CLOSED_WON.value, [])),
            },
        }

    def funil_conversao(self) -> dict:
        total = self.db.query(models.Lead).count()
        if total == 0:
            return {"error": "sem leads"}

        site = self.db.query(models.Lead).filter(models.Lead.source == "site_landing_page").count()
        qualificados = self.db.query(models.Lead).filter(models.Lead.score >= 60).count()
        deals = self.db.query(models.Deal).count()
        won = self.db.query(models.Deal).filter(models.Deal.stage == models.DealStage.CLOSED_WON.value).count()

        return {
            "funil": {
                "visitantes_site": {"count": site, "porcentagem": 100},
                "leads_capturados": {"count": total, "porcentagem": round(total / max(site, 1) * 100, 1)},
                "leads_qualificados": {"count": qualificados, "porcentagem": round(qualificados / max(total, 1) * 100, 1)},
                "deals_criados": {"count": deals, "porcentagem": round(deals / max(qualificados, 1) * 100, 1)},
                "deals_fechados": {"count": won, "porcentagem": round(won / max(deals, 1) * 100, 1)},
            },
            "gargalos": self._identificar_gargalos(site, total, qualificados, deals, won),
        }

    def _identificar_gargalos(self, site, leads, qualificados, deals, won) -> list:
        gargalos = []
        if site > 0 and leads / site < 0.3:
            gargalos.append({
                "estagio": "site → lead",
                "taxa": f"{round(leads/site*100,1)}%",
                "problema": "Formulario pode estar mal posicionado ou CTA fraco",
                "acao": "Testar posicao do formulario, reduzir campos, adicionar lead magnet",
            })
        if leads > 0 and qualificados / leads < 0.4:
            gargalos.append({
                "estagio": "lead → qualificado",
                "taxa": f"{round(qualificados/leads*100,1)}%",
                "problema": "Leads sem perfil ou scoring muito rigoroso",
                "acao": "Revisar criterios BANT, ajustar pesos do scoring",
            })
        if qualificados > 0 and deals / qualificados < 0.3:
            gargalos.append({
                "estagio": "qualificado → deal",
                "taxa": f"{round(deals/qualificados*100,1)}%",
                "problema": "Outreach ineficaz ou leads nao engajam",
                "acao": "Revisar sequencia de outreach, personalizar mensagens",
            })
        if deals > 0 and won / deals < 0.2:
            gargalos.append({
                "estagio": "deal → fechado",
                "taxa": f"{round(won/deals*100,1)}%",
                "problema": "Dificuldade no fechamento ou price alto",
                "acao": "Oferecer trial gratuito, revisar precos, criar urgencia",
            })
        return gargalos

    def leads_por_dia(self, dias: int = 30) -> list:
        desde = datetime.utcnow() - timedelta(days=dias)
        leads = self.db.query(models.Lead).filter(models.Lead.created_at >= desde).all()
        por_dia = defaultdict(int)
        for l in leads:
            dia = l.created_at.strftime("%Y-%m-%d")
            por_dia[dia] += 1

        resultado = []
        for i in range(dias):
            dia = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            resultado.append({"data": dia, "leads": por_dia.get(dia, 0)})
        return sorted(resultado, key=lambda x: x["data"])

    def atividades_recentes(self, limite: int = 20) -> list:
        atividades = self.db.query(models.Activity).order_by(
            models.Activity.created_at.desc()
        ).limit(limite).all()
        return [
            {
                "id": a.id,
                "lead_id": a.lead_id,
                "tipo": a.type,
                "assunto": a.subject,
                "data": a.created_at.isoformat(),
                "status": a.outcome,
            }
            for a in atividades
        ]

    def relatorio_completo(self) -> dict:
        return {
            "gerado_em": datetime.utcnow().isoformat(),
            "resumo": self.pipeline_summary(),
            "funil": self.funil_conversao(),
            "atividades_recentes": self.atividades_recentes(10),
            "tendencia_7d": self.leads_por_dia(7),
        }

    def gargalos_detalhados(self) -> dict:
        funil = self.funil_conversao()
        gargalos = funil.get("gargalos", [])

        etapas = []
        leads_por_estagio = {
            "visitou_site": self.db.query(models.Activity).filter(models.Activity.type == "pageview").count(),
            "preencheu_form": self.db.query(models.Activity).filter(models.Activity.type == "form_start").count(),
            "diagnosticou": self.db.query(models.Activity).filter(models.Activity.type == "diagnostic").count(),
        }

        for nome, count in leads_por_estagio.items():
            etapas.append({"etapa": nome, "leads": count})

        return {
            "gargalos": gargalos,
            "etapas": etapas,
            "recomendacoes": [
                g["acao"] for g in gargalos
            ],
        }
