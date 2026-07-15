from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class NR1PsicossocialAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em riscos psicossociais no trabalho conforme "
            "a NR-1 (Portaria MTE 1.419/2024). Sua funcao e identificar, avaliar "
            "e documentar Fatores de Riscos Psicossociais Relacionados ao Trabalho "
            "(FRPRT) usando metodologias validadas como COPSOQ, JCQ, PHQ-9 e GAD-7. "
            "Gere inventarios, planos de acao e relatorios executivos. "
            "Nao emita ART nem elabore o PGR completo - escopo restrito ao modulo "
            "psicossocial conforme guia oficial MTE."
        )

    def avaliar_riscos(self, dados_empresa: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados da empresa abaixo, realize a identificacao "
            "e classificacao dos Fatores de Riscos Psicossociais Relacionados "
            "ao Trabalho (FRPRT) conforme NR-1:\n\n"
            f"{dados_empresa}\n\n"
            "Para cada fator identificado:\n"
            "1. Descricao do fator de risco\n"
            "2. Classificacao (critico / moderado / baixo)\n"
            "3. Grupo de FRPRT conforme guia MTE\n"
            "4. Metodo de avaliacao recomendado\n\n"
            "Ao final, gere um inventario de riscos psicossociais completo."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "nr1_psicossocial", "inventario_riscos": result}

    def gerar_plano_acao(self, inventario: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base no inventario de riscos psicossociais abaixo, "
            "gere um plano de acao hierarquizado:\n\n"
            f"{inventario}\n\n"
            "O plano deve seguir a hierarquia:\n"
            "1. Eliminar (medidas que eliminam o fator de risco)\n"
            "2. Substituir (substituir por algo de menor risco)\n"
            "3. Controlar (medidas de controle administrativo/engenharia)\n"
            "4. Mitigar (medidas mitigadoras)\n\n"
            "Para cada acao: responsavel, prazo e indicador de acompanhamento."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "nr1_psicossocial", "plano_acao": result}

    def gerar_relatorio_executivo(self, inventario: str, lang: str = "pt") -> dict:
        prompt = (
            "Resuma o inventario de riscos psicossociais abaixo em um "
            "relatorio executivo para apresentacao a fiscalizacao:\n\n"
            f"{inventario}\n\n"
            "Inclua:\n"
            "1. Resumo dos principais riscos identificados\n"
            "2. Score geral de risco psicossocial\n"
            "3. Acoes prioritarias recomendadas\n"
            "4. Cronograma de revisao (minimo a cada 2 anos conforme NR-1)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "nr1_psicossocial", "relatorio_executivo": result}
