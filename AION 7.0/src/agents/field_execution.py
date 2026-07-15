from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class FieldExecutionAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em execucao de obras e construcao civil. "
            "Sua funcao e traduzir modelos BIM e plantas em instrucoes claras "
            "para trabalhadores em campo, guiar a execucao, identificar desvios "
            "de projeto e reduzir retrabalho. Forneca instrucoes praticas e objetivas."
        )

    def generate_field_instructions(self, project_specs: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nas especificacoes do projeto abaixo, gere instrucoes "
            "de execucao para a equipe em campo:\n\n"
            f"{project_specs}\n\n"
            "Inclua:\n"
            "1. Sequencia de execucao passo a passo\n"
            "2. Pontos criticos de atencao\n"
            "3. Tolerancias e especificacoes tecnicas\n"
            "4. Checklist de verificacao"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)

        return {
            "agent": "field_execution",
            "instructions": result,
        }

    def identify_deviations(self, as_built: str, as_designed: str, lang: str = "pt") -> str:
        prompt = (
            "Compare o executado com o projetado e identifique desvios:\n\n"
            f"PROJETADO:\n{as_designed}\n\n"
            f"EXECUTADO:\n{as_built}\n\n"
            "Liste cada desvio, o impacto e a acao corretiva recomendada."
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
