from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class ChannelAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um agente de monitoramento de canais do Microsoft Teams "
            "especializado em detectar riscos de conformidade em conversas "
            "corporativas. Identifica conversas com potenciais riscos trabalhistas "
            "e tributarios. Gera alertas automaticos de compliance para equipe "
            "juridica e de RH. Monitore linguagem inapropriada, vazamento de "
            "informacoes e violacoes de politicas internas."
        )

    def monitorar_canal(self, conversas: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise as seguintes conversas de canais do Teams e identifique "
            "possiveis riscos de conformidade:\n\n"
            f"{conversas}\n\n"
            "Para cada conversa:\n"
            "1. Resumo da conversa\n"
            "2. Risco identificado (trabalhista / tributario / LGPD / etico)\n"
            "3. Nivel de severidade (critico / moderado / baixo)\n"
            "4. Envolvidos\n"
            "5. Providencias recomendadas"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "channel_agent", "monitoramento_canal": result}

    def detectar_riscos(self, mensagens: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise as mensagens abaixo e detecte riscos de compliance:\n\n"
            f"{mensagens}\n\n"
            "Classifique cada risco:\n"
            "1. Risco trabalhista (assédio, discriminacao, jornada irregular)\n"
            "2. Risco tributario (sonegação, evasao, fraudes fiscais)\n"
            "3. Risco LGPD (vazamento de dados, compartilhamento indevido)\n"
            "4. Risco etico (conduta inadequada, conflito de interesses)\n\n"
            "Para cada risco: evidencia textual, artigos violados e acao recomendada."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "channel_agent", "deteccao_riscos": result}

    def gerar_alerta(self, risco: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base no risco identificado abaixo, gere um alerta de compliance "
            "para envio via Microsoft Teams:\n\n"
            f"{risco}\n\n"
            "O alerta deve conter:\n"
            "1. Titulo do alerta\n"
            "2. Descricao do risco\n"
            "3. Classificacao e urgencia\n"
            "4. Destinatarios recomendados (Juridico / RH / Compliance / Gestor)\n"
            "5. Acoes imediatas recomendadas\n"
            "6. Prazo para resposta\n"
            "7. Template de mensagem para o Teams"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "channel_agent", "alerta_compliance": result}
