from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class AtendimentoClientePTBRAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em atendimento ao cliente automatizado "
            "para PMEs brasileiras, operando em portugues brasileiro. "
            "Sua funcao e resolver tickets de nivel 1 (L1) automaticamente "
            "via WhatsApp, Microsoft Teams e chat web. "
            "Cobre os topicos: duvidas sobre produtos/servicos, status de "
            "pedidos, agendamento, cancelamento, fale conosco, FAQs. "
            "Quando nao puder resolver, escalar para L2 com contexto completo. "
            "Mantenha tom profissional e cordial, com linguagem adaptada ao "
            "publico brasileiro. Nao resolva questoes juridicas nem financeiras "
            "sem escalar para o agente adequado."
        )

    def responder_ticket(self, mensagem_cliente: str, contexto: str = "", lang: str = "pt") -> dict:
        prompt = (
            "Com base na mensagem do cliente abaixo, gere uma resposta "
            "adequada para atendimento L1:\n\n"
            f"Mensagem: {mensagem_cliente}\n\n"
        )
        if contexto:
            prompt += f"Contexto do cliente:\n{contexto}\n\n"
        prompt += (
            "A resposta deve:\n"
            "1. Ser cordial e profissional em portugues brasileiro\n"
            "2. Resolver a duvida se for L1\n"
            "3. Se nao for possivel resolver, explicar o motivo e escalar\n"
            "4. Incluir informacoes uteis (prazos, protocolo, etc)\n"
            "5. Sugerir proximo passo\n\n"
            "Indique ao final se o ticket foi resolvido (L1) ou precisa de escalonamento (L2)."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "atendimento_cliente_ptbr", "resposta": result}

    def categorizar_ticket(self, mensagem_cliente: str, lang: str = "pt") -> dict:
        prompt = (
            "Classifique o ticket do cliente abaixo em uma das categorias:\n\n"
            f"{mensagem_cliente}\n\n"
            "Categorias disponiveis:\n"
            "1. Duvida_produto - Perguntas sobre produtos/servicos\n"
            "2. Status_pedido - Acompanhamento de compras/entregas\n"
            "3. Cancelamento - Solicitações de cancelamento\n"
            "4. Agendamento - Marcacao/remarcacao de servicos\n"
            "5. Reclamacao - Insatisfacao com produto/servico\n"
            "6. Sugestao - Feedbacks e melhorias\n"
            "7. Suporte_tecnico - Problemas tecnicos\n"
            "8. Financeiro - Duvidas sobre cobranca/pagamento\n"
            "9. Outro - Nao se enquadra nas categorias acima\n\n"
            "Retorne: categoria, subcategoria (se aplicavel), urgencia (alta/media/baixa), "
            "e se requer escalonamento imediato."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "atendimento_cliente_ptbr", "classificacao": result}

    def gerar_relatorio_atendimento(self, tickets: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos tickets abaixo, gere um relatorio de atendimento:\n\n"
            f"{tickets}\n\n"
            "O relatorio deve incluir:\n"
            "1. Volume total de tickets no periodo\n"
            "2. Resolvidos L1 vs escalados L2\n"
            "3. Categorias mais frequentes\n"
            "4. Tempo medio de resposta\n"
            "5. Satisfacao do cliente (se disponivel)\n"
            "6. Top 3 duvidas mais comuns (para criar FAQ)\n"
            "7. Recomendacoes de melhoria\n\n"
            "Formato: relatorio executivo para gestao."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "atendimento_cliente_ptbr", "relatorio": result}
