from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class ESGIFRSAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em sustentabilidade e reportes ESG "
            "alinhados aos padroes IFRS S1 e S2, Resolucao CVM 193/2023, "
            "SASB e GRI. Sua funcao e auxiliar PMEs fornecedoras de "
            "grandes empresas a diagnosticar maturidade ESG, mapear "
            "indicadores materiais, gerar relatorios de sustentabilidade "
            "simplificados e responder a questionarios ESG de clientes. "
            "Foque em praticidade e baixo custo para PMEs."
        )

    def diagnosticar_maturidade(self, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Realize um diagnostico inicial de maturidade ESG para a "
            "empresa abaixo:\n\n"
            f"{dados_empresa}\n\n"
            "Avalie:\n"
            "1. Maturidade ambiental (Escopo 1, 2, 3, certificacoes)\n"
            "2. Maturidade social (NR-1 psicossocial, igualdade salarial, diversidade)\n"
            "3. Maturidade de governanca (compliance, canal de denuncias)\n"
            "4. Score geral de maturidade ESG (0-100%)\n"
            "5. Indicadores materiais por setor (SASB)\n"
            "6. Riscos de exclusao de cadeias B2B"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "esg_ifrs", "diagnostico_maturidade": result}

    def gerar_relatorio_sustentabilidade(self, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados abaixo, gere um relatorio de "
            "sustentabilidade simplificado alinhado ao IFRS S1:\n\n"
            f"{dados_empresa}\n\n"
            "Inclua:\n"
            "1. Perfil da empresa e contexto\n"
            "2. Governanca e estrategia ESG\n"
            "3. Indicadores ambientais (S1 - clima)\n"
            "4. Indicadores sociais (S1 - capital humano)\n"
            "5. Indicadores de governanca\n"
            "6. Metas e progresso\n"
            "7. Nota metodologica"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "esg_ifrs", "relatorio_sustentabilidade": result}

    def responder_questionario(self, questionario: str, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Responda ao questionario ESG abaixo com base nos dados "
            "da empresa fornecidos:\n\n"
            f"Questionario:\n{questionario}\n\n"
            f"Dados da empresa:\n{dados_empresa}\n\n"
            "Para cada pergunta:\n"
            "1. Resposta direta\n"
            "2. Evidencia ou referencia\n"
            "3. Observacao se necessario"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "esg_ifrs", "resposta_questionario": result}
