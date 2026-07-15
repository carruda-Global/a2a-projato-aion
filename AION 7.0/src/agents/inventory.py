from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class InventoryAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em gestao de estoque para construcao civil. "
            "Sua funcao e monitorar niveis de estoque, identificar itens em falta, "
            "sugerir substitutos e otimizar a rotatividade de materiais. "
            "Seja preciso nas quantidades e prazos."
        )

    def check_stock(self, items: list[dict], lang: str = "pt") -> dict:
        items_str = "\n".join(
            f"- {i.get('name', 'Item')}: estoque={i.get('stock', 0)}, "
            f"minimo={i.get('min_stock', 0)}, consumo_diario={i.get('daily_use', 0)}"
            for i in items
        )
        prompt = (
            "Analise o estoque dos seguintes itens:\n"
            f"{items_str}\n\n"
            "Para cada item, informe:\n"
            "1. Status (OK / Abaixo do minimo / Critico)\n"
            "2. Dias ate o estoque zerar\n"
            "3. Quantidade recomendada para ressuprimento\n"
            "4. Sugestoes de substitutos se aplicavel"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)

        return {
            "agent": "inventory",
            "stock_analysis": result,
            "needs_logistics": "urgente" in result.lower()
            or "critico" in result.lower(),
        }

    def suggest_substitute(self, material: str, required_specs: str, lang: str = "pt") -> str:
        prompt = (
            f"Preciso de um substituto para o material '{material}' "
            f"com as seguintes especificacoes: {required_specs}. "
            "Sugira alternativas com especificacoes tecnicas equivalentes "
            "e estimativa de custo."
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
