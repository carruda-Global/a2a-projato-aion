from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class SpecAnalystAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um engenheiro especialista em analise de especificacoes tecnicas "
            "para construcao civil. Sua funcao e ler plantas, memoriais descritivos, "
            "normas tecnicas e documentos de engenharia para extrair requisitos, "
            "identificar contradicoes e sinalizar nao-conformidades. "
            "Seja preciso e tecnico nas suas analises."
        )

    def analyze_document(self, document_text: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise o documento de engenharia abaixo e extraia:\n"
            "1. Requisitos tecnicos principais\n"
            "2. Especificacoes de materiais\n"
            "3. Normas citadas\n"
            "4. Possiveis contradicoes ou nao-conformidades\n"
            "5. Recomendacoes\n\n"
            f"Documento:\n{document_text}"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)

        return {
            "agent": "spec_analyst",
            "analysis": result,
            "needs_procurement": "compra" in result.lower()
            or "material" in result.lower(),
        }

    def check_compliance(self, specification: str, standard: str, lang: str = "pt") -> str:
        prompt = (
            f"Verifique se a especificacao abaixo esta em conformidade "
            f"com a norma {standard}:\n\n{specification}"
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
