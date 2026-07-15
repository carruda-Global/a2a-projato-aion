from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class ComplianceAnticorrupcaoAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em compliance anticorrupcao "
            "conforme Lei 12.846/2013 (Lei Anticorrupcao), Decreto "
            "11.129/2022 e guias da CGU. Sua funcao e estruturar "
            "programas de integridade para PMEs que contratam com "
            "o poder publico. Realize diagnosticos de maturidade, "
            "elabore codigos de etica, politicas de prevencao, "
            "treinamentos automatizados, due diligence de terceiros "
            "e relatorios no formato CGU para licitacoes."
        )

    def diagnosticar_maturidade(self, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Realize um diagnostico de maturidade do programa de "
            "integridade da empresa abaixo conforme guia CGU:\n\n"
            f"{dados_empresa}\n\n"
            "Avalie:\n"
            "1. Comprometimento da alta direcao\n"
            "2. Codigo de etica e conduta\n"
            "3. Politicas de prevencao (presentes, conflito de interesses)\n"
            "4. Canais de denuncia\n"
            "5. Treinamentos\n"
            "6. Due diligence de terceiros\n"
            "7. Monitoramento continuo\n\n"
            "Score geral de maturidade (0-100%)."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "compliance_anticorrupcao", "diagnostico_integridade": result}

    def gerar_codigo_etica(self, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados da empresa abaixo, elabore um "
            "Codigo de Etica e Conduta personalizado:\n\n"
            f"{dados_empresa}\n\n"
            "O codigo deve conter:\n"
            "1. Principios e valores da organizacao\n"
            "2. Regras de conduta para colaboradores\n"
            "3. Politica de presentes e hospitalidades\n"
            "4. Conflito de interesses\n"
            "5. Uso de informacoes privilegiadas\n"
            "6. Canal de denuncias\n"
            "7. Consequencias do descumprimento"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "compliance_anticorrupcao", "codigo_etica": result}

    def due_diligence_terceiros(self, dados_terceiro: str, lang: str = "pt") -> dict:
        prompt = (
            "Realize uma due diligence simplificada do terceiro/fornecedor "
            "abaixo:\n\n"
            f"{dados_terceiro}\n\n"
            "Avalie:\n"
            "1. Perfil de risco (alta / media / baixa)\n"
            "2. Sinalizadores de alerta (red flags)\n"
            "3. Documentacao necessaria\n"
            "4. Recomendacao (aprovar / aprovar com restricoes / rejeitar)\n"
            "5. Plano de monitoramento"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "compliance_anticorrupcao", "due_diligence": result}

    def gerar_relatorio_cgu(self, dados_programa: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados do programa de integridade abaixo, "
            "gere o relatorio no formato CGU para licitacoes:\n\n"
            f"{dados_programa}\n\n"
            "O relatorio deve conter:\n"
            "1. Estrutura do programa de integridade\n"
            "2. Medidas implementadas\n"
            "3. Evidencias de efetividade\n"
            "4. Melhorias em andamento\n"
            "5. Declaracao de conformidade com Lei 12.846/2013"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "compliance_anticorrupcao", "relatorio_cgu": result}
