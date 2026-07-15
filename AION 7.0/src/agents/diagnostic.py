import logging
from typing import Any

from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

logger = logging.getLogger(__name__)


class DiagnosticAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em diagnostico e classificacao de residuos solidos "
            "conforme NBR-10004 e Resolucoes CONAMA. Sua funcao e analisar a descricao "
            "das atividades de uma empresa, classificar os residuos gerados por classe "
            "(I - Perigoso, IIA - Nao Inerte, IIB - Inerte), sugerir a destinacao "
            "adequada e estimar volumes. Seja tecnico e preciso."
        )

    def classify_waste(self, company_data: str) -> dict:
        prompt = (
            "Analise os dados da empresa abaixo e classifique os residuos gerados:\n\n"
            f"{company_data}\n\n"
            "Para cada tipo de residuo identificado, forneca:\n"
            "1. Nome do residuo\n"
            "2. Classe (I / IIA / IIB) conforme NBR-10004\n"
            "3. Origem do processo\n"
            "4. Estimativa de geracao (kg/mes)\n"
            "5. Destinacao recomendada\n"
            "6. Transportador/empresa sugerida\n\n"
            "Ao final, forneca um resumo com:\n"
            "- Total estimado de residuos (kg/mes)\n"
            "- Classes predominantes\n"
            "- Recomendacoes de gestao"
        )
        result = self.llm.chat(self.system_prompt, prompt)
        return {"agent": "diagnostic", "waste_classification": result}

    def estimate_volume(self, activity_description: str) -> str:
        prompt = (
            "Com base na descricao da atividade abaixo, estime o volume e a "
            "composicao dos residuos solidos gerados:\n\n"
            f"{activity_description}\n\n"
            "Forneca:\n"
            "1. Volume mensal estimado (kg e m3)\n"
            "2. Composicao percentual por tipo\n"
            "3. Sazonalidade (variacao ao longo do ano)\n"
            "4. Custos estimados de destinacao"
        )
        return self.llm.chat(self.system_prompt, prompt)
