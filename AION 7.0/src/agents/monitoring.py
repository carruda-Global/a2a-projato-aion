import logging
from datetime import datetime, timedelta
from typing import Any

from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

logger = logging.getLogger(__name__)


class MonitoringAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em monitoramento ambiental e conformidade "
            "continua para conformidade legal. Sua funcao e acompanhar prazos "
            "de renovacao, gerar alertas de vencimento, sugerir atualizacoes "
            "com base em mudancas normativas e manter o historico de "
            "conformidade da empresa. Seja proativo e preciso."
        )
        self._reminders: dict[str, dict] = {}

    def schedule_renewal(
        self,
        client_id: str,
        client_name: str,
        issue_date: str,
        months_valid: int = 12,
    ) -> dict:
        from datetime import datetime as dt
        issued = dt.fromisoformat(issue_date) if isinstance(issue_date, str) else issue_date
        renewal_date = issued + timedelta(days=30 * months_valid)
        alert_30 = renewal_date - timedelta(days=30)
        alert_15 = renewal_date - timedelta(days=15)
        alert_7 = renewal_date - timedelta(days=7)

        self._reminders[client_id] = {
            "client_id": client_id,
            "client_name": client_name,
            "issue_date": issue_date,
            "renewal_date": renewal_date.isoformat(),
            "alert_30_days": alert_30.isoformat(),
            "alert_15_days": alert_15.isoformat(),
            "alert_7_days": alert_7.isoformat(),
            "status": "active",
        }

        prompt = (
            f"Cliente: {client_name}\n"
            f"Data de emissao: {issue_date}\n"
            f"Validade: {months_valid} meses\n"
            f"Data de renovacao: {renewal_date.date()}\n\n"
            "Gere um plano de monitoramento para renovacao incluindo:\n"
            "1. Cronograma de acoes para renovacao\n"
            "2. Documentos necessarios para atualizacao\n"
            "3. Pontos de atencao (mudancas normativas, Legislação)\n"
            "4. Checklist de verificacao pre-renovacao"
        )
        result = self.llm.chat(self.system_prompt, prompt)
        return {
            "agent": "monitoring",
            "renewal_plan": result,
            "schedule": self._reminders[client_id],
        }

    def check_renewals_due(self) -> list[dict]:
        now = datetime.utcnow()
        due = []
        for client_id, info in self._reminders.items():
            if info["status"] != "active":
                continue
            for alert_key in ["alert_7_days", "alert_15_days", "alert_30_days"]:
                alert_date = dt.fromisoformat(info[alert_key])
                if alert_date <= now:
                    due.append({
                        "client_id": client_id,
                        "client_name": info["client_name"],
                        "alert_type": alert_key,
                        "renewal_date": info["renewal_date"],
                        "days_remaining": (dt.fromisoformat(info["renewal_date"]) - now).days,
                    })
                    break
        return due

    def suggest_updates(self, current_doc: str, new_regulations: str = "") -> str:
        prompt = (
            "Analise o documento atual e sugira atualizacoes necessarias:\n\n"
            f"DOCUMENTO ATUAL:\n{current_doc}\n\n"
        )
        if new_regulations:
            prompt += f"NOVAS NORMAS/REGULAMENTOS:\n{new_regulations}\n\n"
        prompt += (
            "Liste as atualizacoes necessarias:\n"
            "1. Itens a revisar\n"
            "2. Novos requisitos legais\n"
            "3. Alteracoes nos processos\n"
            "4. Prioridade (alta/media/baixa)"
        )
        return self.llm.chat(self.system_prompt, prompt)


from datetime import datetime as dt
