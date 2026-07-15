from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class LogisticsAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em logistica para construcao civil. "
            "Sua funcao e acompanhar envios, identificar problemas de entrega, "
            "gerar notas fiscais e otimizar rotas de transporte de materiais. "
            "Seja preciso com prazos e custos logisticos."
        )

    def track_shipment(self, shipment_data: dict, lang: str = "pt") -> dict:
        prompt = (
            "Analise o status do seguinte envio:\n"
            f"Produto: {shipment_data.get('product', 'N/A')}\n"
            f"Origem: {shipment_data.get('origin', 'N/A')}\n"
            f"Destino: {shipment_data.get('destination', 'N/A')}\n"
            f"Data prevista: {shipment_data.get('expected_date', 'N/A')}\n"
            f"Status atual: {shipment_data.get('status', 'N/A')}\n\n"
            "Forneca:\n"
            "1. Analise do status atual\n"
            "2. Riscos de atraso\n"
            "3. Recomendacoes"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)

        return {
            "agent": "logistics",
            "tracking_analysis": result,
        }

    def check_delivery_issues(self, deliveries: list[dict], lang: str = "pt") -> str:
        deliveries_str = "\n".join(
            f"- Pedido {d.get('order_id', 'N/A')}: "
            f"status={d.get('status', 'N/A')}, "
            f"previsao={d.get('eta', 'N/A')}"
            for d in deliveries
        )
        prompt = (
            "Identifique problemas nas seguintes entregas:\n"
            f"{deliveries_str}\n\n"
            "Liste cada entrega com problema, a gravidade e a acao recomendada."
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
