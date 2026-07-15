from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class RegulatoryAnalystAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um analista regulatorio especializado em revisao de contratos, "
            "politicas e documentos legais. Identifica riscos relacionados a LGPD "
            "(Lei 13.709/2018), NR-1 (Portaria MTE 1.419/2024), ESG (IFRS S1/S2) "
            "e Anticorrupcao (Lei 12.846/2013). Conecta-se ao SharePoint e OneDrive "
            "para analisar documentos corporativos. Gere relatorios de risco "
            "detalhados com classificacao e recomendacoes."
        )

    def analisar_documento(self, documento: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise o documento abaixo e identifique riscos regulatorios "
            "relacionados a LGPD, NR-1, ESG e Anticorrupcao:\n\n"
            f"{documento}\n\n"
            "Para cada risco identificado:\n"
            "1. Tipo de risco (LGPD / NR-1 / ESG / Anticorrupcao)\n"
            "2. Descricao detalhada do risco\n"
            "3. Classificacao (critico / moderado / baixo)\n"
            "4. Artigo ou clausula aplicavel\n"
            "5. Recomendacao de mitigacao\n\n"
            "Ao final, gere um resumo executivo dos principais riscos."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "regulatory_analyst", "analise_documento": result}

    def gerar_relatorio_riscos(self, analise: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base na analise regulatoria abaixo, gere um relatorio "
            "completo de riscos:\n\n"
            f"{analise}\n\n"
            "O relatorio deve incluir:\n"
            "1. Matriz de riscos (probabilidade x impacto)\n"
            "2. Priorizacao dos riscos identificados\n"
            "3. Plano de acao por risco\n"
            "4. Cronograma de remediacao\n"
            "5. Responsaveis indicados\n"
            "6. Custo estimado de conformidade"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "regulatory_analyst", "relatorio_riscos": result}

    def revisar_documento_sharepoint(self, url_documento: str, lang: str = "pt") -> dict:
        prompt = (
            "O documento esta disponivel no seguinte URL do SharePoint:\n\n"
            f"{url_documento}\n\n"
            "Simule a revisao regulatoria do documento no SharePoint, "
            "considerando:\n"
            "1. Nome do documento e tipo\n"
            "2. Data de criacao e versao\n"
            "3. Conformidade com politicas internas\n"
            "4. Riscos regulatorios identificados\n"
            "5. Status de aprovacao recomendado\n\n"
            "Forneca um resumo da revisao realizada."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "regulatory_analyst", "revisao_sharepoint": result}
