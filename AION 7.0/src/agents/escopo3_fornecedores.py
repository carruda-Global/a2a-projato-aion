from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class Escopo3FornecedoresAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em rastreabilidade de emissoes de "
            "Escopo 3 conforme GHG Protocol, SBCE (Lei 15.042/2024), "
            "IFRS S2 e CBAM. Sua funcao e auxiliar empresas a calcular "
            "a pegada de carbono de sua cadeia de fornecedores, "
            "consolidar as 15 categorias do Escopo 3, gerar scores "
            "de maturidade ESG por fornecedor e produzir relatorios "
            "para conformidade regulatoria."
        )

    def avaliar_fornecedores(self, dados_cadeia: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados da cadeia de fornecedores abaixo, "
            "realize a avaliacao de emissoes Escopo 3:\n\n"
            f"{dados_cadeia}\n\n"
            "Para cada fornecedor:\n"
            "1. Categoria GHG Protocol Escopo 3 aplicavel\n"
            "2. Gasto anual com o fornecedor (ou dado de atividade)\n"
            "3. Fator setorial utilizado\n"
            "4. Emissao estimada (tCO2e)\n"
            "5. Score de maturidade ESG (0-100%)\n"
            "6. Ranking de risco na cadeia"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "escopo3_fornecedores", "avaliacao_cadeia": result}

    def gerar_relatorio_escopo3(self, dados_completos: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados abaixo, gere o relatorio completo "
            "de emissoes Escopo 3:\n\n"
            f"{dados_completos}\n\n"
            "O relatorio deve conter:\n"
            "1. Resumo executivo\n"
            "2. Total de emissoes Escopo 3\n"
            "3. Detalhamento por categoria (15 categorias GHG Protocol)\n"
            "4. Ranking de emissoes por fornecedor\n"
            "5. Metodologia e fontes\n"
            "6. Conformidade com IFRS S2 e CBAM\n"
            "7. Recomendacoes de engajamento"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "escopo3_fornecedores", "relatorio_escopo3": result}
