from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class LgpdOperacionalAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em privacidade de dados e LGPD "
            "(Lei 13.709/2018). Sua funcao e auxiliar PMEs a mapear "
            "fluxos de dados, gerar RoPA (Registro de Operacoes de "
            "Tratamento), identificar lacunas de base legal, elaborar "
            "avisos de privacidade e contratos com operadores, e "
            "monitorar incidentes com notificacao a ANPD. "
            "Siga as diretrizes da Autoridade Nacional de Protecao "
            "de Dados (ANPD)."
        )

    def mapear_fluxos_dados(self, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nas informacoes da empresa abaixo, realize o "
            "mapeamento dos fluxos de dados pessoais:\n\n"
            f"{dados_empresa}\n\n"
            "Identifique:\n"
            "1. Categorias de dados pessoais tratados\n"
            "2. Finalidades do tratamento\n"
            "3. Bases legais aplicaveis (art. 7o ou art. 11 da LGPD)\n"
            "4. Compartilhamento com terceiros\n"
            "5. Fluxo internacional (se houver)\n"
            "6. Periodo de retencao"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "lgpd_operacional", "mapeamento_dados": result}

    def gerar_ropa(self, mapeamento: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base no mapeamento de dados abaixo, gere o RoPA "
            "(Registro de Operacoes de Tratamento) conforme modelo ANPD:\n\n"
            f"{mapeamento}\n\n"
            "Para cada operacao de tratamento:\n"
            "1. Descricao da operacao\n"
            "2. Finalidade\n"
            "3. Base legal\n"
            "4. Categorias de titulares\n"
            "5. Categorias de dados\n"
            "6. Medidas de seguranca adotadas"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "lgpd_operacional", "ropa": result}

    def avaliar_conformidade(self, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Avalie o nivel de conformidade LGPD da empresa abaixo:\n\n"
            f"{dados_empresa}\n\n"
            "Gere:\n"
            "1. Score de maturidade LGPD (0-100%)\n"
            "2. Lacunas identificadas por base legal\n"
            "3. Riscos de multa (ate 2% faturamento ou R$ 50 milhoes)\n"
            "4. Plano de adequacao priorizado\n"
            "5. Modelos de documentos necessarios "
            "(aviso de privacidade, termos, contratos)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "lgpd_operacional", "avaliacao_conformidade": result}
