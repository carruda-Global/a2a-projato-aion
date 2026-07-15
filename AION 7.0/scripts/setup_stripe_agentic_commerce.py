import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings

AGENTS_FOR_CATALOG = [
    {
        "id": "spec-analyst",
        "title": "Analisador de Especificações Técnicas",
        "description": "Agente IA que analisa documentos técnicos de engenharia, extrai requisitos e aponta inconsistências com normas NBR (ABNT).",
        "price_cents": 99700,
        "currency": "BRL",
        "category": "Engineering and Construction",
        "image_url": "https://engenheiro-producao-ai.onrender.com/assets/spec-analyst.png",
    },
    {
        "id": "procurement",
        "title": "Processador de Ordens de Compra",
        "description": "Agente IA que processa pedidos de materiais, compara cotações de fornecedores e otimiza aquisições para obras.",
        "price_cents": 159700,
        "currency": "BRL",
        "category": "Procurement",
        "image_url": "https://engenheiro-producao-ai.onrender.com/assets/procurement.png",
    },
    {
        "id": "inventory",
        "title": "Gestor de Estoque de Obra",
        "description": "Agente IA que monitora níveis de estoque em tempo real, sugere reposições e indica materiais substitutos.",
        "price_cents": 159700,
        "currency": "BRL",
        "category": "Inventory Management",
        "image_url": "https://engenheiro-producao-ai.onrender.com/assets/inventory.png",
    },
    {
        "id": "logistics",
        "title": "Rastreador Logístico de Materiais",
        "description": "Agente IA que acompanha remessas de materiais, identifica atrasos e problemas de entrega em tempo real.",
        "price_cents": 299700,
        "currency": "BRL",
        "category": "Logistics",
        "image_url": "https://engenheiro-producao-ai.onrender.com/assets/logistics.png",
    },
    {
        "id": "field-execution",
        "title": "Gerador de Instruções de Execução em Campo",
        "description": "Agente IA que gera instruções passo a passo para execução em campo a partir de plantas, memoriais e modelos BIM.",
        "price_cents": 350000,
        "currency": "BRL",
        "category": "Engineering and Construction",
        "image_url": "https://engenheiro-producao-ai.onrender.com/assets/field-execution.png",
    },
]

ACP_CHECKOUT_ENDPOINT = {
    "acp": "1.0.0",
    "merchant": {
        "name": "Projato Engenharia",
        "description": "Sistema multiagente de IA para a indústria AEC",
        "website": "https://engenheiro-producao-ai.onrender.com",
        "support_url": "https://engenheiro-producao-ai.onrender.com/support",
        "terms_url": "https://engenheiro-producao-ai.onrender.com/terms",
        "privacy_url": "https://engenheiro-producao-ai.onrender.com/privacy",
        "refund_policy": "Reembolso integral em até 7 dias, conforme Código de Defesa do Consumidor",
    },
    "checkout": {
        "endpoint": "https://engenheiro-producao-ai.onrender.com/api/v1/acp/checkout",
        "method": "POST",
        "authentication": {
            "type": "api_key",
            "header": "X-ACP-Key",
        },
    },
    "products": [
        {
            "id": agent["id"],
            "name": agent["title"],
            "description": agent["description"],
            "price": {
                "amount": agent["price_cents"],
                "currency": agent["currency"],
                "type": "one_time" if agent["price_cents"] < 300000 else "subscription",
                "interval": "month" if agent["price_cents"] >= 300000 else None,
            },
            "category": agent["category"],
            "fulfillment": {
                "type": "digital",
                "url": f"https://engenheiro-producao-ai.onrender.com/api/v1/agents/{agent['id']}/execute",
            },
        }
        for agent in AGENTS_FOR_CATALOG
    ],
}


def generate_stripe_catalog_feed():
    output_dir = Path(__file__).parent.parent / "config"
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "stripe_agentic_catalog.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "title", "description", "availability",
            "condition", "price[amount]", "price[currency]",
            "link", "image_link", "google_product_category",
            "product_type", "stripe_product_tax_code",
        ])
        for agent in AGENTS_FOR_CATALOG:
            writer.writerow([
                agent["id"],
                agent["title"],
                agent["description"],
                "in_stock",
                "new",
                agent["price_cents"],
                agent["currency"],
                f"https://engenheiro-producao-ai.onrender.com/api/v1/agents/{agent['id']}",
                agent["image_url"],
                "Engineering and Construction",
                agent["category"],
                "txcd_99999999",
            ])

    print(f"Stripe catalog feed gerado: {csv_path}")
    return csv_path


def generate_acp_endpoint_config():
    output_dir = Path(__file__).parent.parent / "config"
    output_dir.mkdir(exist_ok=True)

    acp_path = output_dir / "acp_checkout_config.json"
    with open(acp_path, "w", encoding="utf-8") as f:
        json.dump(ACP_CHECKOUT_ENDPOINT, f, indent=2, ensure_ascii=False)

    print(f"Configuração ACP gerada: {acp_path}")
    return acp_path


def main():
    print("=" * 60)
    print("Configuração do Stripe Agentic Commerce Suite")
    print("(ACP + UCP protocols)")
    print("=" * 60)

    settings = Settings()
    if not settings.stripe_secret_key:
        print("[!] STRIPE_SECRET_KEY não configurada. Configure no .env")

    generate_stripe_catalog_feed()
    generate_acp_endpoint_config()

    print()
    print("Próximos passos:")
    print("1. Acesse https://dashboard.stripe.com/agentic-commerce")
    print("2. Faça o onboarding do Agentic Commerce Suite")
    print("3. Faça upload do catálogo gerado (config/stripe_agentic_catalog.csv)")
    print("4. Configure os webhooks para checkout.session.completed")
    print()
    print("Para implementar o endpoint ACP no servidor:")
    print("- Adicione uma rota POST /api/v1/acp/checkout")
    print("- Use a config gerada em config/acp_checkout_config.json")
    print()
    print("Protocolos suportados:")
    print("  ACP (Agentic Commerce Protocol) - Stripe + OpenAI")
    print("  UCP (Universal Commerce Protocol) - Google, Shopify, Amazon, etc")
    print()
    print("Agentes que podem comprar seus serviços:")
    print("  - ChatGPT (OpenAI) - via ACP")
    print("  - Google Assistant / Gemini - via UCP")
    print("  - Qualquer agente compatível com Stripe Agentic Commerce")


if __name__ == "__main__":
    main()
