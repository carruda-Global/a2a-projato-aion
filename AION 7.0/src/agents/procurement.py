from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class ProcurementAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em compras e suprimentos para construcao civil. "
            "Sua funcao e processar pedidos de compra, comparar cotacoes de "
            "fornecedores, gerar requisicoes e otimizar custos. "
            "Trabalhe com dados precisos e prazos realistas."
        )

    def process_order(self, material_list: list[dict], lang: str = "pt") -> dict:
        materials_str = "\n".join(
            f"- {m.get('name', 'Material')}: {m.get('quantity', 0)} "
            f"{m.get('unit', 'un')}"
            for m in material_list
        )
        prompt = (
            "Processe a seguinte lista de materiais para compra:\n"
            f"{materials_str}\n\n"
            "Para cada item, forneca:\n"
            "1. Quantidade recomendada para compra\n"
            "2. Estimativa de custo unitario\n"
            "3. Prazo de entrega sugerido\n"
            "4. Fornecedores sugeridos"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)

        return {
            "agent": "procurement",
            "order_plan": result,
            "needs_inventory": True,
        }

    def compare_quotes(self, quotes: list[dict], lang: str = "pt") -> str:
        quotes_str = "\n".join(
            f"- {q.get('supplier', 'Fornecedor')}: R$ {q.get('price', 0)} - "
            f"Prazo: {q.get('lead_time', 'N/A')}"
            for q in quotes
        )
        prompt = (
            "Compare as seguintes cotacoes e recomende a melhor opcao "
            "considerando preco, prazo e condicoes:\n\n"
            f"{quotes_str}"
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
