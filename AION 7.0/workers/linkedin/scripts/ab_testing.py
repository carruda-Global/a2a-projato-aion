import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sales.database import init_db, SessionLocal
from sales import models
from sales import outreach


class ABTester:
    VARIANTS = {
        "conexao_a": "Ola {name}, vi seu perfil e o trabalho da {company} no setor de {industry}. Desenvolvemos agentes de IA que podem ajudar a otimizar processos. Vamos conversar?",
        "conexao_b": "Oi {name}, notei que {company} atua em {industry}. Temos uma solucao de IA que esta gerando resultados em 48h. Topa um cafe virtual?",
        "conexao_c": "{name}, seu trabalho em {industry} me chamou atencao. Na {company}, usamos IA para automatizar compliance. Posso te mostrar em 10min?",
        "post_a": "59 agentes de IA para sua empresa. Resultado em 48h. Trial gratuito.\n\nhttps://global-engenharia.com/ecosystem\n\n#IA #Compliance",
        "post_b": "Automatize compliance com IA. NR-1, LGPD, ESG e mais. Trial 15 dias gratis.\n\nhttps://global-engenharia.com/ecosystem\n\n#Inovacao #Tecnologia",
        "post_c": "Sua empresa precisa de compliance? Resolvemos em 48h com 59 agentes de IA.\n\nTeste gratis: https://global-engenharia.com/ecosystem",
    }

    def __init__(self):
        self.db = SessionLocal()
        init_db()

    def close(self):
        self.db.close()

    def get_next_variant(self, test_name: str) -> str:
        variants = [k for k in self.VARIANTS if k.startswith(test_name)]
        counts = {}
        for v in variants:
            count = self.db.query(models.Activity).filter(
                models.Activity.subject.like(f"AB:{v}%")
            ).count()
            counts[v] = count
        min_count = min(counts.values()) if counts else 0
        candidates = [v for v, c in counts.items() if c == min_count]
        return random.choice(candidates) if candidates else variants[0]

    async def test_conexao_message(self, lead_name: str, company: str, industry: str) -> tuple:
        variant = self.get_next_variant("conexao")
        template = self.VARIANTS[variant]
        msg = template.format(name=lead_name, company=company, industry=industry)

        activity = models.Activity(
            lead_id=0,
            type="ab_test",
            subject=f"AB:{variant}:{lead_name}",
            description=msg[:200],
            outcome="pending",
        )
        self.db.add(activity)
        self.db.commit()

        return variant, msg

    def record_response(self, variant: str, lead_name: str, responded: bool):
        activity = self.db.query(models.Activity).filter(
            models.Activity.subject == f"AB:{variant}:{lead_name}"
        ).first()
        if activity:
            activity.outcome = "positive" if responded else "negative"
            self.db.commit()

    def get_results(self, test_name: str) -> dict:
        variants = [k for k in self.VARIANTS if k.startswith(test_name)]
        results = {}
        for v in variants:
            total = self.db.query(models.Activity).filter(
                models.Activity.subject.like(f"AB:{v}%")
            ).count()
            positive = self.db.query(models.Activity).filter(
                models.Activity.subject.like(f"AB:{v}%"),
                models.Activity.outcome == "positive",
            ).count()
            results[v] = {
                "sent": total,
                "responses": positive,
                "rate": round(positive / max(total, 1) * 100, 1),
            }

        winner = max(results, key=lambda k: results[k]["rate"]) if results else ""
        return {
            "test": test_name,
            "variants": results,
            "winner": winner,
            "winner_rate": results[winner]["rate"] if winner else 0,
        }

    def auto_optimize(self, test_name: str) -> str:
        results = self.get_results(test_name)
        if results["winner_rate"] > 15:
            v = results["winner"]
            return self.VARIANTS.get(v, self.VARIANTS.get(f"{test_name}_a", ""))
        return self.VARIANTS.get(f"{test_name}_a", "")
