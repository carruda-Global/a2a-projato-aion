from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class PhotoIntelligenceAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em analise visual de obras de construcao "
            "civil. Sua funcao e interpretar descricoes de fotos de obras "
            "para identificar elementos construtivos, detectar riscos de "
            "seguranca (uso de EPI, condicoes do canteiro), comparar o "
            "executado com o cronograma e gerar relatorios de progresso "
            "visual. Seja preciso e objetivo."
        )

    def analyze_photo(self, photo_description: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise a descricao da foto de obra abaixo:\n\n"
            f"{photo_description}\n\n"
            "Identifique:\n"
            "1. Elementos construtivos visiveis\n"
            "2. Estagio da obra com base na imagem\n"
            "3. Riscos de seguranca identificados\n"
            "4. Conformidade com EPIs\n"
            "5. Desvios visuais em relacao ao projeto\n"
            "6. Recomendacoes"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "photo_intelligence", "visual_analysis": result}

    def compare_with_schedule(self, photo_description: str, expected_progress: str, lang: str = "pt") -> str:
        prompt = (
            "Compare o que foi capturado na foto com o progresso esperado:\n\n"
            f"FOTO:\n{photo_description}\n\n"
            f"PROGRESSO ESPERADO:\n{expected_progress}\n\n"
            "Avalie:\n"
            "1. Se o progresso fotografico corresponde ao esperado\n"
            "2. Possiveis atrasos ou adiantamentos\n"
            "3. Recomendacoes para realinhamento"
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
