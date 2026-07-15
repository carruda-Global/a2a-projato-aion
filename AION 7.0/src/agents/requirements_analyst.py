from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class RequirementsAnalystAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em analise de qualidade de requisitos "
            "para projetos de engenharia e construcao. Sua funcao e avaliar "
            "requisitos contra padroes de qualidade, gerar scores, identificar "
            "ambiguidades e sugerir melhorias. Use normas como ISO 29148 e "
            "boas praticas de engenharia de requisitos."
        )

    def analyze_requirements(self, requirements_text: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise a qualidade dos seguintes requisitos de engenharia:\n\n"
            f"{requirements_text}\n\n"
            "Para cada requisito, avalie:\n"
            "1. Clareza (score 0-10)\n"
            "2. Completude (score 0-10)\n"
            "3. Testabilidade (score 0-10)\n"
            "4. Ambiguidades encontradas\n"
            "5. Sugestoes de melhoria\n\n"
            "Ao final, forneca um score geral de qualidade."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "requirements_analyst", "quality_analysis": result}

    def check_consistency(self, req_set_a: str, req_set_b: str, lang: str = "pt") -> str:
        prompt = (
            "Compare os dois conjuntos de requisitos abaixo e identifique "
            "inconsistencias, contradicoes ou sobreposicoes:\n\n"
            f"CONJUNTO A:\n{req_set_a}\n\n"
            f"CONJUNTO B:\n{req_set_b}\n\n"
            "Liste cada inconsistencia e recomende acao corretiva."
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
