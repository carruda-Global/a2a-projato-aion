import stripe
import os
from pathlib import Path

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    print("ERRO: Defina STRIPE_SECRET_KEY como env var")
    exit(1)

BASE_URL = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")

METADADOS_PRODUTO = {
    "compliance_essencial": {
        "name": "Compliance Essencial — NR-1 + LGPD",
        "description": (
            "Agente de IA que gera inventario de riscos psicossociais (NR-1/Portaria MTE 1.419/2024) "
            "e mapeamento de dados LGPD (RoPA/ANPD) de forma automatizada. Para PMEs que precisam "
            "de compliance sem equipe interna. Resultado em 48h."
        ),
        "images": [f"{BASE_URL}/static/images/compliance-essencial.png"],
        "features": [
            "NR-1 Riscos Psicossociais (Portaria MTE 1.419/2024)",
            "LGPD Operacional (Lei 13.709/2018)",
            "Inventario FRPRT e plano de acao",
            "RoPA e mapeamento de dados",
            "Relatorios para fiscalizacao",
        ],
    },
    "regulatory_pro": {
        "name": "Regulatory Pro — Obrigacoes Completas",
        "description": (
            "5 obrigacoes legais em um painel: NR-1, LGPD, Canal de Denuncias, "
            "Igualdade Salarial, Compliance Anticorrupcao. Para PMEs que precisam "
            "de compliance trabalhista completo."
        ),
        "images": [f"{BASE_URL}/static/images/regulatory-pro.png"],
        "features": [
            "Tudo do Compliance Essencial",
            "Canal de Denuncias (Lei 14.457/2022)",
            "Igualdade Salarial (Lei 14.611/2023)",
            "Compliance Anticorrupcao (Lei 12.846/2013)",
            "Tributario CBS/IBS (LC 214/2025)",
        ],
    },
    "esg_carbon": {
        "name": "ESG + Carbono PME",
        "description": (
            "Diagnostico ESG IFRS S1/S2, Inventario de Carbono Escopo 1/2 (GHG Protocol) "
            "e Escopo 3 Fornecedores (SBCE + CBAM). Para empresas com exigencias ESG e SBCE."
        ),
        "images": [f"{BASE_URL}/static/images/esg-carbon.png"],
        "features": [
            "ESG IFRS S1/S2 (Res. CVM 193/2023)",
            "Inventario de Carbono Escopo 1/2 (GHG Protocol)",
            "Escopo 3 Fornecedores (SBCE + CBAM)",
        ],
    },
    "aec_full": {
        "name": "AEC Full — Engenharia e Construcao",
        "description": (
            "12 agentes especializados para construtoras e escritorios de engenharia: "
            "Spec Analyst, Procurement, Inventory, Logistics, Field Execution, "
            "BIM Coordinator, Requirements Analyst, Engineering Assistant, "
            "Work Synopsis, Photo Intelligence, RFI Creation, Compliance Agent."
        ),
        "images": [f"{BASE_URL}/static/images/aec-full.png"],
        "features": [
            "Spec Analyst, Procurement, Inventory",
            "Logistics, Field Execution, BIM Coordinator",
            "Requirements Analyst, Engineering Assistant",
            "Work Synopsis, Photo Intelligence",
            "RFI Creation, Compliance Agent",
        ],
    },
    "microsoft_pack": {
        "name": "Microsoft Compliance Pack",
        "description": (
            "6 agentes integrados ao ecossistema Microsoft 365: Regulatory Analyst (SharePoint), "
            "Compliance PM (Planner), Channel Agent (Teams), Knowledge Agent (RAG), "
            "Facilitator Agent, Dev Experience Agent."
        ),
        "images": [f"{BASE_URL}/static/images/microsoft-pack.png"],
        "features": [
            "Regulatory Analyst (SharePoint/OneDrive)",
            "Compliance PM (Planner)",
            "Channel Agent Regulatorio (Teams)",
            "Knowledge Agent com RAG",
            "Facilitator Agent (reunioes)",
            "Dev Experience Agent (PRs e code review)",
        ],
    },
    "full_suite": {
        "name": "Full Suite — 30 Agentes",
        "description": (
            "Todos os 30 agentes de IA do portfolio completo. AEC Core + Especializados + "
            "Conformidade + Regulatorios + ESG + Carbono + Escopo 3 + Microsoft Pack + "
            "Cross-Sell (Onboarding, Atendimento, Conciliacao). Suporte prioritario 24/7."
        ),
        "images": [f"{BASE_URL}/static/images/full-suite.png"],
        "features": [
            "Todos os 30 agentes de IA",
            "AEC Core + Especializados + Conformidade",
            "Regulatorios + ESG + Carbono + Escopo 3",
            "Microsoft Pack completo (6 agentes M365)",
            "Cross-Sell: Onboarding, Atendimento, Conciliacao",
        ],
    },
    "tributario_entrada": {
        "name": "Tributario CBS/IBS - Starter",
        "description": (
            "Classificacao NCM, simulacao de impacto CBS/IBS e geracao de DeRE "
            "conforme LC 214/2025. Para PMEs que precisam se preparar para a reforma tributaria."
        ),
        "images": [f"{BASE_URL}/static/images/tributario-starter.png"],
        "features": [
            "Classificacao NCM automatizada",
            "Simulacao de impacto CBS/IBS",
            "Geracao de DeRE",
        ],
    },
    "tributario_full": {
        "name": "Tributario CBS/IBS - Full",
        "description": (
            "Classificacao NCM, simulacao de impacto, geracao de DeRE, "
            "relatorios fiscais completos e consultoria tributaria automatizada. "
            "Para medias empresas com operacoes complexas."
        ),
        "images": [f"{BASE_URL}/static/images/tributario-full.png"],
        "features": [
            "Tudo do Starter",
            "Relatorios fiscais completos",
            "Consultoria tributaria automatizada",
            "Integracao com sistemas contabeis",
        ],
    },
    "cross_sell_harmony": {
        "name": "Cross-Sell Harmony — Onboarding",
        "description": (
            "Automacao de admissao de funcionarios: contratos, checklist de documentos, "
            "provisionamento de acessos (email, Teams, sistemas), eSocial."
        ),
        "images": [f"{BASE_URL}/static/images/cross-sell-harmony.png"],
        "features": [
            "Onboarding de Funcionarios (admissao, contratos, acessos)",
            "Checklist de documentos e provisionamento",
            "Integracao com Teams e WhatsApp",
        ],
    },
    "atendimento_plus": {
        "name": "Atendimento Plus — Suporte PT-BR",
        "description": (
            "Resolucao automatica de tickets L1 via WhatsApp + Teams em portugues brasileiro. "
            "Cobre duvidas, status, agendamento, FAQs."
        ),
        "images": [f"{BASE_URL}/static/images/atendimento-plus.png"],
        "features": [
            "Atendimento ao Cliente PT-BR automatico",
            "Resolucao de tickets L1 via WhatsApp/Teams",
            "Categorizacao e escalonamento inteligente",
        ],
    },
    "conciliacao_pro": {
        "name": "Conciliacao Pro — Fechamento Mensal",
        "description": (
            "Automacao de fechamento mensal: conciliacao de NFs com extratos bancarios, "
            "faturas de cartao e boletos emitidos vs pagos. Identifica divergencias."
        ),
        "images": [f"{BASE_URL}/static/images/conciliacao-pro.png"],
        "features": [
            "Conciliacao de NFs com extratos bancarios",
            "Conciliacao de faturas de cartao",
            "Conciliacao de boletos emitidos vs pagos",
        ],
    },
}

PRODUCT_AGENTS = {
    "compliance_essencial": ["nr1_psicossocial", "lgpd_operacional"],
    "regulatory_pro": ["nr1_psicossocial", "tributario_cbs_ibs", "lgpd_operacional", "canal_denuncias", "igualdade_salarial", "compliance_anticorrupcao"],
    "esg_carbon": ["esg_ifrs", "inventario_carbono", "escopo3_fornecedores"],
    "aec_full": ["spec_analyst", "procurement", "inventory", "logistics", "field_execution", "bim_coordinator", "requirements_analyst", "engineering_assistant", "work_synopsis", "photo_intelligence", "rfi_creation", "compliance"],
    "microsoft_pack": ["regulatory_analyst", "compliance_pm", "channel_agent", "knowledge_agent", "facilitator_agent", "dev_experience"],
    "full_suite": None,
    "tributario_entrada": ["tributario_cbs_ibs"],
    "tributario_full": ["tributario_cbs_ibs"],
    "cross_sell_harmony": ["onboarding_funcionarios"],
    "atendimento_plus": ["atendimento_cliente_ptbr"],
    "conciliacao_pro": ["conciliacao_financeira"],
}

DEFAULT_IMAGES = {
    "compliance_essencial": f"{BASE_URL}/static/images/compliance-essencial.png",
    "regulatory_pro": f"{BASE_URL}/static/images/regulatory-pro.png",
    "esg_carbon": f"{BASE_URL}/static/images/esg-carbon.png",
    "aec_full": f"{BASE_URL}/static/images/aec-full.png",
    "microsoft_pack": f"{BASE_URL}/static/images/microsoft-pack.png",
    "full_suite": f"{BASE_URL}/static/images/full-suite.png",
    "tributario_entrada": f"{BASE_URL}/static/images/tributario-starter.png",
    "tributario_full": f"{BASE_URL}/static/images/tributario-full.png",
    "cross_sell_harmony": f"{BASE_URL}/static/images/cross-sell-harmony.png",
    "atendimento_plus": f"{BASE_URL}/static/images/atendimento-plus.png",
    "conciliacao_pro": f"{BASE_URL}/static/images/conciliacao-pro.png",
}


def recreate_product(plan_id: str, config: dict, agent_list: list[str] | None):
    print(f"\n=== {plan_id}: {config['name']} ===")

    try:
        existing = stripe.Product.search(query=f"metadata['plan_id']:'{plan_id}'", limit=1)
        old_prod = existing.data[0] if existing.data else None
    except Exception:
        old_prod = None

    if old_prod:
        old_prices = stripe.Price.list(product=old_prod.id, limit=10)
        for price in old_prices:
            if price.active:
                stripe.Price.modify(price.id, active=False)
                print(f"  Desativado price antigo: {price.id}")
        stripe.Product.modify(old_prod.id, active=False)
        print(f"  Desativado produto antigo: {old_prod.id} ({old_prod.name})")

    prod = stripe.Product.create(
        name=config["name"],
        description=config["description"],
        metadata={
            "plan_id": plan_id,
            "agent_ids": ",".join(agent_list) if agent_list else "all",
            "base_url": BASE_URL,
        },
        images=[DEFAULT_IMAGES.get(plan_id, f"{BASE_URL}/static/images/default.png")],
        url=f"{BASE_URL}/api/subscriptions/plans/{plan_id}",
    )
    print(f"  Produto criado: {prod.id}")

    from src.monetization.plans import get_plan
    local_plan = get_plan(plan_id)
    unit_amount = local_plan["price"] if local_plan else config.get("amount_cents", 0)

    price = stripe.Price.create(
        product=prod.id,
        unit_amount=unit_amount,
        currency="brl",
        recurring={"interval": "month"},
        metadata={"plan_id": plan_id},
    )
    print(f"  Price criado: {price.id} (R$ {unit_amount/100:.2f}/mes)")

    return prod.id, price.id


def recreate_discounts():
    print("\n=== CUPONS DE DESCONTO (cross-sell 15%) ===")
    try:
        existing = stripe.Coupon.list(limit=100)
        for c in existing:
            if c.metadata.get("type") == "cross_sell":
                stripe.Coupon.modify(c.id, active=False)
                print(f"  Desativado cupom antigo: {c.id}")
    except Exception:
        pass

    coupon = stripe.Coupon.create(
        percent_off=15,
        duration="forever",
        name="Cross-Sell 15%",
        metadata={"type": "cross_sell", "description": "Desconto de ativacao para cross-sell triggers"},
    )
    print(f"  Cupom criado: {coupon.id} (15% off forever)")


def update_config_yaml(price_map: dict):
    config_path = Path(__file__).parent.parent / "Ecosystem 2.0" / "config.yaml"
    if not config_path.exists():
        print(f"  AVISO: config.yaml nao encontrado em {config_path}")
        return

    lines = config_path.read_text(encoding="utf-8").splitlines()
    for plan_id, price_id in price_map.items():
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(f"price_id:") and f"# {plan_id}" in stripped:
                continue
            if f"  {plan_id}:" in line and i + 2 < len(lines):
                for j in range(i, min(i + 10, len(lines))):
                    if lines[j].strip().startswith("price_id:"):
                        old_price_id = lines[j].split("price_id:")[1].strip().strip('"')
                        if old_price_id != f'"{price_id}"':
                            lines[j] = f"      price_id: \"{price_id}\""
                            print(f"  config.yaml atualizado: {plan_id} -> {price_id}")
                        break

    config_path.write_text("\n".join(lines), encoding="utf-8")
    print("  config.yaml salvo")


def create_webhook_endpoints():
    print("\n=== WEBHOOK ENDPOINTS ===")

    existing = stripe.WebhookEndpoint.list(limit=100)
    existing_urls = {e.url for e in existing if e.active}

    webhooks = [
        {
            "url": f"{BASE_URL}/api/subscriptions/webhook",
            "description": "EcoSystem Webhook - Producao",
            "events": [
                "checkout.session.completed",
                "customer.subscription.updated",
                "customer.subscription.deleted",
                "invoice.payment_succeeded",
                "invoice.payment_failed",
            ],
            "metadata": {"env": "production"},
        },
        {
            "url": f"{BASE_URL}/api/subscriptions/webhook",
            "description": "EcoSystem Webhook - Test",
            "events": [
                "checkout.session.completed",
                "customer.subscription.updated",
                "customer.subscription.deleted",
            ],
            "metadata": {"env": "test"},
        },
    ]

    for wh in webhooks:
        if wh["url"] in existing_urls:
            print(f"  Webhook ja existe: {wh['url']}")
            continue
        endpoint = stripe.WebhookEndpoint.create(
            url=wh["url"],
            enabled_events=wh["events"],
            description=wh["description"],
            metadata=wh["metadata"],
        )
        print(f"  Webhook criado: {wh['url']}")
        print(f"    Secret: {endpoint.secret}")
        print(f"    ADICIONE ao .env ou Render:")
        env_key = "STRIPE_WEBHOOK_SECRET_PRODUCTION" if wh["metadata"]["env"] == "production" else "STRIPE_WEBHOOK_SECRET_TEST"
        print(f"    {env_key}={endpoint.secret}")


def create_tax_rates():
    print("\n=== TAX RATES (BRL) ===")
    tax = stripe.TaxRate.create(
        display_name="ISS",
        inclusive=False,
        percentage=5.0,
        country="BR",
        jurisdiction="Municipal",
        metadata={"type": "iss"},
    )
    print(f"  Tax Rate ISS criado: {tax.id} (5%)")


def main():
    print("=" * 60)
    print("Setup Stripe Agentic Commerce")
    print(f"Base URL: {BASE_URL}")
    print(f"Ambiente: {os.getenv('APP_ENV', 'development')}")
    print("=" * 60)

    price_map = {}

    for plan_id, config in METADADOS_PRODUTO.items():
        agents = PRODUCT_AGENTS.get(plan_id)
        prod_id, price_id = recreate_product(plan_id, config, agents)
        price_map[plan_id] = price_id

    update_config_yaml(price_map)

    recreate_discounts()
    create_tax_rates()
    create_webhook_endpoints()

    print("\n" + "=" * 60)
    print("SETUP CONCLUIDO!")
    print("=" * 60)
    print("\nProximos passos:")
    print("1. Revogue as chaves antigas no dashboard Stripe")
    print("2. Adicione as novas env vars no Render")
    print("3. Teste o checkout: python scripts/test_live_checkout.py")


if __name__ == "__main__":
    main()
