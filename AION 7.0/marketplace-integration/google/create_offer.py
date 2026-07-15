"""
Cria a oferta do EcoSystem AEC + Regulatory no Google Cloud Marketplace.

Pré-requisitos:
- GOOGLE_APPLICATION_CREDENTIALS apontando para service account JSON
- Projeto GCP criado e configurado como partner
- API Cloud Marketplace ativada

Uso:
    python create_offer.py

Saída:
    - Oferta criada no Google Cloud Marketplace
    - ID da oferta exibido no console
"""

import json
import os

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "global-engenharia-498823")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")

PLANS = [
    {
        "id": "starter",
        "name": "Starter - Spec Analyst",
        "price_brl": 997,
        "price_usd": 199,
    },
    {
        "id": "professional",
        "name": "Professional - 3 Agentes",
        "price_brl": 2391,
        "price_usd": 399,
    },
    {
        "id": "enterprise",
        "name": "Enterprise - 5 Agentes",
        "price_brl": 4685,
        "price_usd": 799,
    },
    {
        "id": "full_suite",
        "name": "Full Suite - 21 Agentes",
        "price_brl": 9497,
        "price_usd": 1599,
    },
    {
        "id": "compliance_pack",
        "name": "Compliance Pack",
        "price_brl": 2391,
        "price_usd": 399,
    },
    {
        "id": "regulatory_starter",
        "name": "Regulatory Starter - NR-1 + LGPD",
        "price_brl": 590,
        "price_usd": 119,
    },
    {
        "id": "regulatory_professional",
        "name": "Regulatory Professional - 5 Agentes",
        "price_brl": 1490,
        "price_usd": 299,
    },
    {
        "id": "regulatory_full",
        "name": "Regulatory Full - 9 Agentes",
        "price_brl": 3490,
        "price_usd": 699,
    },
    {
        "id": "esg_carbon_pack",
        "name": "ESG + Carbono",
        "price_brl": 2490,
        "price_usd": 499,
    },
]


def create_google_offer():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    service = build("cloudbilling", "v1", credentials=credentials)

    description = (
        "EcoSystem AEC + Regulatory - 21 agentes de IA para "
        "Arquitetura, Engenharia, Construcao e Conformidade Regulatoria. "
        "Inclui agentes AEC (Spec Analyst, Procurement, BIM, etc.) e "
        "agentes regulatorios (NR-1, LGPD, ESG, Carbono, etc.)."
    )

    offer = {
        "name": "EcoSystem AEC - Regulatory Agents",
        "displayName": "EcoSystem AEC + Regulatory",
        "description": description,
        "category": "AI_AGENTS_AND_TOOLS",
        "plans": [
            {
                "planId": p["id"],
                "displayName": p["name"],
                "pricingModel": "SUBSCRIPTION",
                "pricingPeriod": "MONTHLY",
                "price": {
                    "amountMicros": p["price_usd"] * 1_000_000,
                    "currencyCode": "USD",
                },
            }
            for p in PLANS
        ],
    }

    response = (
        service.providers()
        .offers()
        .create(
            provider=f"projects/{GOOGLE_CLOUD_PROJECT_ID}/providers/{GOOGLE_CLOUD_PROJECT_ID}",
            body=offer,
        )
        .execute()
    )

    print(f"✅ Oferta criada: {response['name']}")
    print(f"   ID: {response.get('offerId', 'N/A')}")
    return response


if __name__ == "__main__":
    print("🚀 Criando oferta no Google Cloud Marketplace...")
    print(f"   Projeto: {GOOGLE_CLOUD_PROJECT_ID}")
    print(f"   Planos: {len(PLANS)}")
    create_google_offer()
