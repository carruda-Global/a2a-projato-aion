from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class TributarioCBSIBSAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em tributacao brasileira focado na "
            "reforma tributaria CBS/IBS instituida pela Lei Complementar "
            "214/2025. Sua funcao e auxiliar empresas na classificacao "
            "de produtos/servicos com NCM e aliquotas corretas, gerar "
            "declaracoes DeRE, verificar inconsistencias entre regime "
            "antigo e novo, e simular impacto financeiro da transicao. "
            "Opere com base nas normas da Receita Federal, Comite Gestor "
            "do IBS e Ministerio da Fazenda."
        )

    def classificar_produto(self, descricao: str, lang: str = "pt") -> dict:
        prompt = (
            "Classifique o produto/servico abaixo conforme NCM e aliquotas "
            "CBS/IBS, considerando a Lei Complementar 214/2025:\n\n"
            f"{descricao}\n\n"
            "Forneca:\n"
            "1. NCM sugestao\n"
            "2. Aliquota CBS federal\n"
            "3. Aliquota IBS estadual/municipal\n"
            "4. Regime especifico aplicavel (se houver)\n"
            "5. Comparativo com regime anterior (PIS/COFINS/ICMS/ISS)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "tributario_cbs_ibs", "classificacao": result}

    def verificar_conformidade(self, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise os dados da empresa abaixo e verifique a conformidade "
            "com a reforma tributaria CBS/IBS:\n\n"
            f"{dados_empresa}\n\n"
            "Para cada item:\n"
            "1. Situacao atual (conforme / nao conforme / nao aplicavel)\n"
            "2. Risco de autuacao (agosto/2026 em diante)\n"
            "3. Acoes corretivas recomendadas\n"
            "4. Prioridade (alta / media / baixa)\n\n"
            "Inclua checklist de adequacao por tipo de empresa "
            "(Simples, Lucro Presumido, Real)."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "tributario_cbs_ibs", "conformidade": result}

    def simular_impacto(self, dados_financeiros: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados financeiros abaixo, simule o impacto "
            "da transicao tributaria CBS/IBS:\n\n"
            f"{dados_financeiros}\n\n"
            "Calcule:\n"
            "1. Carga tributaria no regime anterior\n"
            "2. Carga tributaria estimada no novo regime\n"
            "3. Diferenca percentual\n"
            "4. Recomendacoes de planejamento tributario"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "tributario_cbs_ibs", "simulacao_impacto": result}
