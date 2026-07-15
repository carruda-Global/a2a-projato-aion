"""
Gera ofertas SaaS para o Microsoft Azure Marketplace (21 agentes, 9 planos).

Uso:
    python scripts/generate_microsoft_marketplace.py

Gera:
    - offers/ecosystem-aec-offer.json (listing completo com todos os planos)
    - Instrucoes para publicacao no Partner Center
"""
import json
from pathlib import Path

PLANS = [
    {
        "id": "starter",
        "name": "Starter - Spec Analyst",
        "description": "1 agente de IA para analise de especificacoes tecnicas",
        "prices_usd": {
            "P1M": 199.00,
            "P1Y": 1988.00,
            "P2Y": 3582.00,
            "P3Y": 4776.00,
            "P4Y": 5970.00,
            "P5Y": 7164.00,
        },
        "agents": ["spec_analyst"],
    },
    {
        "id": "professional",
        "name": "Professional - 3 Agentes",
        "description": "Spec Analyst + Procurement + Inventory",
        "prices_usd": {
            "P1M": 399.00,
            "P1Y": 3988.00,
            "P2Y": 7182.00,
            "P3Y": 9576.00,
            "P4Y": 11970.00,
            "P5Y": 14364.00,
        },
        "agents": ["spec_analyst", "procurement", "inventory"],
    },
    {
        "id": "enterprise",
        "name": "Enterprise - 5 Agentes",
        "description": "5 agentes do nucleo AEC: analise, compras, estoque, logistica, campo",
        "prices_usd": {
            "P1M": 799.00,
            "P1Y": 7988.00,
            "P2Y": 14382.00,
            "P3Y": 19176.00,
            "P4Y": 23970.00,
            "P5Y": 28764.00,
        },
        "agents": [
            "spec_analyst", "procurement", "inventory",
            "logistics", "field_execution",
        ],
    },
    {
        "id": "full_suite",
        "name": "Full Suite - 21 Agentes",
        "description": "Ecossistema completo de 21 agentes de IA para AEC e conformidade regulatoria brasileira",
        "prices_usd": {
            "P1M": 1599.00,
            "P1Y": 15988.00,
            "P2Y": 28782.00,
            "P3Y": 38376.00,
            "P4Y": 47970.00,
            "P5Y": 57564.00,
        },
        "agents": [
            "spec_analyst", "procurement", "inventory",
            "logistics", "field_execution",
            "bim_coordinator", "requirements_analyst",
            "engineering_assistant", "work_synopsis",
            "photo_intelligence", "rfi_creation", "compliance",
            "nr1_psicossocial", "tributario_cbs_ibs",
            "lgpd_operacional", "esg_ifrs",
            "inventario_carbono", "escopo3_fornecedores",
            "canal_denuncias", "igualdade_salarial",
            "compliance_anticorrupcao",
        ],
    },
    {
        "id": "compliance_pack",
        "name": "Compliance Pack",
        "description": "Photo Intelligence + RFI Creation + Compliance Agent",
        "prices_usd": {
            "P1M": 399.00,
            "P1Y": 3988.00,
            "P2Y": 7182.00,
            "P3Y": 9576.00,
            "P4Y": 11970.00,
            "P5Y": 14364.00,
        },
        "agents": ["photo_intelligence", "rfi_creation", "compliance"],
    },
    {
        "id": "regulatory_starter",
        "name": "Regulatory Starter - NR-1 + LGPD",
        "description": "NR-1 Riscos Psicossociais + LGPD Operacional",
        "prices_usd": {
            "P1M": 119.00,
            "P1Y": 1188.00,
            "P2Y": 2140.00,
            "P3Y": 2856.00,
            "P4Y": 3571.00,
            "P5Y": 4284.00,
        },
        "agents": ["nr1_psicossocial", "lgpd_operacional"],
    },
    {
        "id": "regulatory_professional",
        "name": "Regulatory Professional - 5 Agentes",
        "description": "NR-1, LGPD, Canal de Denuncias, Igualdade Salarial, Compliance Anticorrupcao",
        "prices_usd": {
            "P1M": 299.00,
            "P1Y": 2988.00,
            "P2Y": 5378.00,
            "P3Y": 7176.00,
            "P4Y": 8970.00,
            "P5Y": 10764.00,
        },
        "agents": [
            "nr1_psicossocial", "lgpd_operacional",
            "canal_denuncias", "igualdade_salarial",
            "compliance_anticorrupcao",
        ],
    },
    {
        "id": "regulatory_full",
        "name": "Regulatory Full - 9 Agentes",
        "description": "Todos os 9 agentes regulatorios brasileiros",
        "prices_usd": {
            "P1M": 699.00,
            "P1Y": 6988.00,
            "P2Y": 12582.00,
            "P3Y": 16776.00,
            "P4Y": 20970.00,
            "P5Y": 25164.00,
        },
        "agents": [
            "nr1_psicossocial", "tributario_cbs_ibs",
            "lgpd_operacional", "esg_ifrs",
            "inventario_carbono", "escopo3_fornecedores",
            "canal_denuncias", "igualdade_salarial",
            "compliance_anticorrupcao",
        ],
    },
    {
        "id": "esg_carbon_pack",
        "name": "ESG + Carbono",
        "description": "ESG IFRS S1/S2 + Inventario de Carbono + Escopo 3 Fornecedores",
        "prices_usd": {
            "P1M": 499.00,
            "P1Y": 4988.00,
            "P2Y": 8982.00,
            "P3Y": 11976.00,
            "P4Y": 14970.00,
            "P5Y": 17964.00,
        },
        "agents": [
            "esg_ifrs", "inventario_carbono",
            "escopo3_fornecedores",
        ],
    },
]

AGENT_NAMES = {
    "spec_analyst": "Spec Analyst",
    "procurement": "Procurement",
    "inventory": "Inventory",
    "logistics": "Logistics",
    "field_execution": "Field Execution",
    "bim_coordinator": "BIM Coordinator",
    "requirements_analyst": "Requirements Analyst",
    "engineering_assistant": "Engineering Assistant",
    "work_synopsis": "Work Synopsis",
    "photo_intelligence": "Photo Intelligence",
    "rfi_creation": "RFI Creation",
    "compliance": "Compliance Agent",
    "nr1_psicossocial": "NR-1 Psicossocial",
    "tributario_cbs_ibs": "Tributario CBS/IBS",
    "lgpd_operacional": "LGPD Operacional",
    "esg_ifrs": "ESG IFRS S1/S2",
    "inventario_carbono": "Inventario de Carbono",
    "escopo3_fornecedores": "Escopo 3 Fornecedores",
    "canal_denuncias": "Canal de Denuncias",
    "igualdade_salarial": "Igualdade Salarial",
    "compliance_anticorrupcao": "Compliance Anticorrupcao",
}

OFFER = {
    "$schema": "https://schema.mp.azure.com/schema/2024-03-01/offer.json",
    "id": "ecosystem_aec_regulatory",
    "name": "EcoSystem AEC + Regulatory",
    "alias": "ecosystem-aec-regulatory",
    "description": (
        "21 Agentes de IA Integrados para Arquitetura, Engenharia, "
        "Construcao (AEC) e Conformidade Regulatoria Brasileira. "
        "Inclui agentes AEC: analise de especificacoes, compras, estoque, "
        "logistica, execucao de campo, BIM, RFI. Agentes regulatorios: "
        "NR-1 Psicossocial, Tributario CBS/IBS, LGPD, ESG, Carbono, "
        "Escopo 3, Canal de Denuncias, Igualdade Salarial e "
        "Compliance Anticorrupcao."
    ),
    "publisher": {
        "id": "projato_engenharia",
        "name": "Projato Engenharia",
    },
    "kind": "SaaS",
    "categories": ["AI + Machine Learning", "Developer Tools"],
    "industries": [
        "Engineering and Construction",
        "Architecture",
        "Professional Services",
    ],
    "plans": [],
}

for plan in PLANS:
    agent_names = [AGENT_NAMES.get(a, a) for a in plan["agents"]]
    offer_plan = {
        "id": plan["id"],
        "name": plan["name"],
        "description": (
            f"{plan['description']}. "
            f"Agentes: {', '.join(agent_names)}."
        ),
        "pricing": {
            "type": "recurring",
            "interval": "month",
            "price_usd": plan["monthly_price_usd"],
            "currency": "USD",
        },
        "hidden": False,
        "components": [
            {
                "name": plan["name"],
                "type": "SaaS",
                "description": plan["description"],
                "provisioning_url": (
                    "https://engenheiro-producao-ai.onrender.com/"
                    "api/v1/microsoft-marketplace/subscribe"
                ),
                "provisioning_type": "redirect",
            }
        ],
    }
    OFFER["plans"].append(offer_plan)


def main():
    output_dir = Path(__file__).parent.parent / "offers"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "ecosystem-aec-offer.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(OFFER, f, ensure_ascii=False, indent=2)

    print(f"Oferta Microsoft Marketplace gerada: {output_path}")
    print(f"Planos: {len(PLANS)}")
    for p in PLANS:
        agent_names = [AGENT_NAMES.get(a, a) for a in p["agents"]]
        print(f"  - {p['name']:35s} | ${p['monthly_price_usd']:.2f}/mes | {len(p['agents'])} agentes")
        print(f"    Agentes: {', '.join(agent_names)}")
    print()
    print("Para publicar no Microsoft Partner Center:")
    print("  1. Acesse https://partner.microsoft.com")
    print("  2. Crie uma oferta SaaS")
    print("  3. Importe o arquivo offers/ecosystem-aec-offer.json")
    print("  4. Configure a URL de provisionamento:")
    print("     https://engenheiro-producao-ai.onrender.com/api/v1/microsoft-marketplace/subscribe")
    print("  5. Configure o webhook:")
    print("     https://engenheiro-producao-ai.onrender.com/api/v1/microsoft-marketplace/webhook")
    print("  6. Publique para certificacao")


if __name__ == "__main__":
    main()
