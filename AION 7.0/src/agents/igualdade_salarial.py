from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class IgualdadeSalarialAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em equidade salarial e diversidade "
            "conforme Lei 14.611/2023 e regulamentacao do MTE. Sua funcao "
            "e analisar dados de folha de pagamento para calcular "
            "indicadores de equidade salarial por cargo e funcao, "
            "identificar gaps de remuneracao, gerar relatorios semestrais "
            "no formato do Portal Emprega Brasil, e propor planos de "
            "acao para reducao de desigualdades. "
            "Inclua monitoramento de diversidade (genero, raca, PCD)."
        )

    def analisar_equidade(self, dados_folha: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise os dados de folha de pagamento abaixo para "
            "identificar gaps de equidade salarial:\n\n"
            f"{dados_folha}\n\n"
            "Para cada cargo/funcao:\n"
            "1. Numero de funcionarios por genero\n"
            "2. Remuneracao media por genero\n"
            "3. Diferenca percentual\n"
            "4. Causas identificadas\n"
            "5. Classificacao (dentro da meta / atencao / critico)\n\n"
            "Inclua analise por raca e PCD quando disponivel."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "igualdade_salarial", "analise_equidade": result}

    def gerar_relatorio_mte(self, dados_completos: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados abaixo, gere o relatorio semestral "
            "de equidade salarial no formato exigido pelo MTE "
            "(Portal Emprega Brasil):\n\n"
            f"{dados_completos}\n\n"
            "O relatorio deve conter:\n"
            "1. Dados cadastrais da empresa\n"
            "2. Quadro de cargos e funcoes\n"
            "3. Remuneracao media por cargo (genero, raca)\n"
            "4. Diferencas encontradas\n"
            "5. Plano de acao para reducao dos gaps\n"
            "6. Metas e prazos\n"
            "7. Responsavel pela elaboracao"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "igualdade_salarial", "relatorio_mte": result}

    def monitorar_diversidade(self, dados_funcionarios: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise os dados de diversidade da empresa abaixo:\n\n"
            f"{dados_funcionarios}\n\n"
            "Gere:\n"
            "1. Composicao atual por genero, raca, PCD e geracao\n"
            "2. Indicadores de diversidade em lideranca\n"
            "3. Benchmark setorial (quando disponivel)\n"
            "4. Recomendacoes para melhoria\n"
            "5. Alertas de prazos de relatorios semestrais"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "igualdade_salarial", "diversidade": result}
