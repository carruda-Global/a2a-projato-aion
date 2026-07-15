import logging
from typing import Any

from src.api.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


class CriticAgent:
    def __init__(self, llm: DeepSeekClient):
        self.llm = llm
        self.system_prompt = (
            "Voce e um revisor critico de agentes de IA especializados em "
            "engenharia e construcao civil. Sua funcao e analisar os outputs "
            "de outros agentes, identificar inconsistencias, erros tecnicos, "
            "omissoes e sugerir correcoes. Seja rigoroso e preciso."
        )

    def review(
        self,
        agent_id: str,
        agent_output: dict,
        previous_results: list[dict] | None = None,
    ) -> dict[str, Any]:
        context = ""
        if previous_results:
            context = "\n".join(
                f"  [{r.get('agent', '?')}] {str(r)[:200]}"
                for r in previous_results[-3:]
            )

        prompt = (
            f"Revise o output do agente '{agent_id}' abaixo:\n\n"
            f"OUTPUT:\n{agent_output}\n\n"
        )
        if context:
            prompt += f"RESULTADOS ANTERIORES NO FLUXO:\n{context}\n\n"
        prompt += (
            "Avalie:\n"
            "1. Existem inconsistencias internas? (sim/nao - detalhe)\n"
            "2. Existem erros tecnicos graves? (sim/nao - detalhe)\n"
            "3. O output e coerente com o contexto do projeto? (score 0-10)\n"
            "4. Recomendacao final (aprovar / revisar / rejeitar)\n"
            "5. Justificativa detalhada"
        )
        result = self.llm.chat(self.system_prompt, prompt)
        return {
            "agent": "critic",
            "reviewed_agent": agent_id,
            "review": result,
        }

    def cross_check(
        self,
        source_agent: str,
        source_output: dict,
        target_agent: str,
        target_output: dict,
    ) -> dict[str, Any]:
        prompt = (
            f"Compare os outputs dos dois agentes abaixo e identifique "
            f"inconsistencias entre eles:\n\n"
            f"AGENTE ORIGEM ({source_agent}):\n{source_output}\n\n"
            f"AGENTE DESTINO ({target_agent}):\n{target_output}\n\n"
            "Liste cada inconsistencia encontrada e recomende acao corretiva."
        )
        result = self.llm.chat(self.system_prompt, prompt)
        return {
            "agent": "critic",
            "cross_check": result,
            "source": source_agent,
            "target": target_agent,
        }
