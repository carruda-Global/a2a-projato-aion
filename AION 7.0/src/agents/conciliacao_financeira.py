from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class ConciliacaoFinanceiraAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em conciliacao financeira automatizada "
            "para PMEs brasileiras. Sua funcao e automatizar o fechamento "
            "mensal: conciliacao de notas fiscais (NFs) com extratos bancarios, "
            "conciliacao de faturas de cartao de credito, conciliacao de "
            "boletos emitidos vs pagos, identificacao de divergencias, "
            "e geracao de relatorios de conciliacao. "
            "Trabalhe com os padroes brasileiros: NFe, NFCe, boleto bancario, "
            "PIX, TED, cartao de credito. "
            "Nao realize pagamentos nem emita boletos — escopo restrito a "
            "conciliacao e identificacao de divergencias."
        )

    def conciliar_extrato_nf(self, extrato: str, notas_fiscais: str, lang: str = "pt") -> dict:
        prompt = (
            "Realize a conciliacao entre o extrato bancario e as notas fiscais "
            "abaixo:\n\n"
            f"EXTRATO BANCARIO:\n{extrato}\n\n"
            f"NOTAS FISCAIS:\n{notas_fiscais}\n\n"
            "Para cada transacao:\n"
            "1. Data e valor\n"
            "2. NF correspondente (se encontrada)\n"
            "3. Status (conciliada / divergente / nao_encontrada)\n"
            "4. Divergencia especifica se aplicavel (valor, data, favorecido)\n\n"
            "Ao final:\n"
            "- Total de NFs conciliadas\n"
            "- Total de divergencias encontradas\n"
            "- Total de NFs sem correspondencia no extrato\n"
            "- Total de transacoes no extrato sem NF\n"
            "- Sugestoes de ajuste para cada divergencia"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "conciliacao_financeira", "relatorio_conciliacao": result}

    def conciliar_cartao(self, fatura: str, comprovantes: str, lang: str = "pt") -> dict:
        prompt = (
            "Realize a conciliacao entre a fatura do cartao de credito e os "
            "comprovantes/notas fiscais abaixo:\n\n"
            f"FATURA CARTAO:\n{fatura}\n\n"
            f"COMPROVANTES:\n{comprovantes}\n\n"
            "Para cada lancamento na fatura:\n"
            "1. Data e valor\n"
            "2. Comprovante/NF correspondente (se encontrado)\n"
            "3. Categoria da despesa\n"
            "4. Status (conciliado / divergente / sem_comprovante)\n\n"
            "Ao final:\n"
            "- Total de lancamentos conciliados\n"
            "- Total de divergencias\n"
            "- Total sem comprovante\n"
            "- Sugestoes de regularizacao"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "conciliacao_financeira", "conciliacao_cartao": result}

    def conciliar_boletos(self, boletos_emitidos: str, baixas_recebidas: str, lang: str = "pt") -> dict:
        prompt = (
            "Realize a conciliacao entre os boletos emitidos e as baixas "
            "recebidas abaixo:\n\n"
            f"BOLETOS EMITIDOS:\n{boletos_emitidos}\n\n"
            f"BAIXAS RECEBIDAS:\n{baixas_recebidas}\n\n"
            "Para cada boleto:\n"
            "1. Numero do boleto\n"
            "2. Valor e vencimento\n"
            "3. Data de pagamento (se recebido)\n"
            "4. Status (pago / vencido / pendente / divergente)\n"
            "5. Dias de atraso se aplicavel\n\n"
            "Ao final:\n"
            "- Total de boletos emitidos\n"
            "- Total pago no periodo\n"
            "- Total em atraso\n"
            "- Taxa de inadimplencia\n"
            "- Sugestoes de cobranca para boletos vencidos"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "conciliacao_financeira", "conciliacao_boletos": result}

    def gerar_relatorio_fechamento(self, conciliacao: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base na conciliacao abaixo, gere um relatorio executivo "
            "de fechamento mensal:\n\n"
            f"{conciliacao}\n\n"
            "O relatorio deve incluir:\n"
            "1. Resumo do periodo (receitas, despesas, saldo)\n"
            "2. Indices de conciliacao (percentual conciliado)\n"
            "3. Principais divergencias encontradas e status\n"
            "4. Risco fiscal (NFs nao conciliadas, notas faltantes)\n"
            "5. Recomendacoes para o proximo fechamento\n"
            "6. Anexos: lista de itens pendentes e acoes necessarias"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "conciliacao_financeira", "relatorio_fechamento": result}
