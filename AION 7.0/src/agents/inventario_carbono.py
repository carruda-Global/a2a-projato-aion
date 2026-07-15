from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class InventarioCarbonoAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em inventarios de emissoes de gases "
            "de efeito estufa (GEE) conforme GHG Protocol, Lei 15.042/2024 "
            "(SBCE) e metricas do MCTI. Sua funcao e calcular emissoes "
            "de Escopo 1 (fontes proprias) e Escopo 2 (energia adquirida), "
            "gerar inventarios completos com trilha de auditoria, identificar "
            "hotspots de emissao e oportunidades de reducao. "
            "Use fatores de emissao atualizados do MCTI e SIN."
        )

    def calcular_emissoes(self, dados_consumo: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados de consumo abaixo, calcule as emissoes "
            "de GEE (Escopo 1 e Escopo 2):\n\n"
            f"{dados_consumo}\n\n"
            "Para cada fonte:\n"
            "1. Tipo de emissao (Escopo 1 ou 2)\n"
            "2. Fonte de emissao\n"
            "3. Dado de atividade (consumo)\n"
            "4. Fator de emissao utilizado (com referencia)\n"
            "5. Emissao calculada (tCO2e)\n"
            "6. Metodologia de calculo\n\n"
            "Ao final, totalize as emissoes por escopo."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "inventario_carbono", "emissoes_calculadas": result}

    def gerar_inventario(self, dados_completos: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados completos abaixo, gere o inventario "
            "de emissoes GHG Protocol:\n\n"
            f"{dados_completos}\n\n"
            "O inventario deve conter:\n"
            "1. Identificacao da organizacao e periodo de reporte\n"
            "2. Limites organizacionais e operacionais\n"
            "3. Emissoes de Escopo 1 detalhadas\n"
            "4. Emissoes de Escopo 2 detalhadas (location-based e market-based)\n"
            "5. Total de emissoes (tCO2e)\n"
            "6. Intensidade de carbono (tCO2e / receita ou producao)\n"
            "7. Comparativo com ano anterior\n"
            "8. Trilha de auditoria com fatores de emissao"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "inventario_carbono", "inventario_ghg": result}

    def identificar_hotspots(self, inventario: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise o inventario de emissoes abaixo e identifique "
            "hotspots e oportunidades de reducao:\n\n"
            f"{inventario}\n\n"
            "Para cada hotspot:\n"
            "1. Fonte de emissao\n"
            "2. Participacao no total (%)\n"
            "3. Potencial de reducao estimado\n"
            "4. Acoes recomendadas\n"
            "5. Estimativa de custo-beneficio"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "inventario_carbono", "hotspots": result}
