from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class CanalDenunciasAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em canais de denuncias corporativos "
            "conforme Lei 14.457/2022 (obrigatorio para empresas com CIPA "
            "- 20+ funcionarios). Sua funcao e estruturar canais omnichannel "
            "(WhatsApp, formulario web, email), triangular denuncias por "
            "categoria, gerenciar fluxos de investigacao, gerar relatorios "
            "semestrais para CIPA e diretoria, e integrar indicadores com "
            "a gestao de riscos psicossociais (NR-1). "
            "Garanta anonimato, sigilo e conformidade legal."
        )

    def classificar_denuncia(self, denuncia: str, lang: str = "pt") -> dict:
        prompt = (
            "Classifique a denuncia abaixo conforme as categorias "
            "da Lei 14.457/2022 e normas internas:\n\n"
            f"{denuncia}\n\n"
            "Informe:\n"
            "1. Categoria principal (assedio moral / sexual / discriminacao / "
            "fraude / seguranca / outro)\n"
            "2. Gravidade (alta / media / baixa)\n"
            "3. Urgencia (imediata / 24h / 7 dias)\n"
            "4. Area responsavel pela apuracao\n"
            "5. Fluxo de investigacao recomendado\n"
            "6. Riscos psicossociais associados (cross-sell NR-1)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "canal_denuncias", "classificacao": result}

    def gerar_relatorio_semestral(self, denuncias_periodo: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nas denuncias do periodo abaixo, gere um "
            "relatorio semestral para CIPA e diretoria:\n\n"
            f"{denuncias_periodo}\n\n"
            "O relatorio deve conter:\n"
            "1. Quantidade de denuncias por categoria\n"
            "2. Tempo medio de resolucao\n"
            "3. Status das investigacoes\n"
            "4. Acoes corretivas implementadas\n"
            "5. Indicadores de clima organizacional\n"
            "6. Recomendacoes para a diretoria"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "canal_denuncias", "relatorio_semestral": result}

    def configurar_canal(self, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados da empresa abaixo, recomende a "
            "configuracao ideal do canal de denuncias:\n\n"
            f"{dados_empresa}\n\n"
            "Inclua:\n"
            "1. Canais recomendados (WhatsApp / web / email)\n"
            "2. Politica de anonimato e protecao ao denunciante\n"
            "3. Fluxo de apuracao e prazos\n"
            "4. Integracao com NR-1 riscos psicossociais\n"
            "5. Modelo de politica interna"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "canal_denuncias", "configuracao": result}
