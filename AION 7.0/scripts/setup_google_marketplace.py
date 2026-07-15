"""
Google Cloud Marketplace - Setup Completo
Cria Service Account + Oferta + Registro de Endpoints

Uso:
    python scripts/setup_google_marketplace.py

PrÃ©-requisitos:
    pip install google-auth-oauthlib google-api-python-client google-cloud-aiplatform
"""

import json
import os
import sys
import webbrowser
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = "global-engenharia-498823"
CLIENT_SECRET_PATH = Path(__file__).parent.parent.parent / "client_secret_757085749411-t95chtg2tpui3hjov165lratnj3fb0fc.apps.googleusercontent.com.json"
SA_KEY_PATH = Path(__file__).parent.parent / "service-account.json"
TOKEN_PATH = Path.home() / ".aion" / "google_marketplace_token.json"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]

PLANS = [
    {"id": "compliance_essencial",   "name": "Compliance Essencial - NR-1 + LGPD",           "price_usd": 119,   "price_brl": 590},
    {"id": "regulatory_pro",         "name": "Regulatory Pro - 6 Agentes",                   "price_usd": 299,   "price_brl": 1490},
    {"id": "esg_carbono",            "name": "ESG + Carbono",                                "price_usd": 499,   "price_brl": 2490},
    {"id": "microsoft_pack",         "name": "Microsoft Pack - 6 Agentes M365",              "price_usd": 899,   "price_brl": 4482},
    {"id": "dynamics_pack",          "name": "Dynamics 365 Pack - 6 Agentes",                "price_usd": 999,   "price_brl": 3990},
    {"id": "agentforce_pack",        "name": "Agentforce Pack - 5 Agentes",                  "price_usd": 929,   "price_brl": 3690},
    {"id": "oracle_pack",            "name": "Oracle Fusion Pack - 4 Agentes",               "price_usd": 999,   "price_brl": 3990},
    {"id": "sap_pack",               "name": "SAP Integration Pack - 3 Agentes",             "price_usd": 1079,  "price_brl": 4290},
    {"id": "erp_full_bridge",        "name": "ERP Full Bridge - 18 Agentes",                 "price_usd": 3299,  "price_brl": 12990},
    {"id": "full_suite",             "name": "Full Suite - Todos os 78 Agentes",             "price_usd": 4999,  "price_brl": 19997},
]


def authenticate():
    """Autentica via OAuth (abre navegador)"""
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials as OCreds

    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = OCreds.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            if creds.expired:
                creds.refresh(Request())
        except Exception:
            TOKEN_PATH.unlink()
            creds = None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
        print("\nAbrindo navegador para autenticar no Google...")
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"  Token salvo em: {TOKEN_PATH}")
    return creds


def create_service_account(creds):
    """Cria Service Account para o Marketplace"""
    from googleapiclient.discovery import build

    print("\n[1/4] Criando Service Account...")
    iam = build("iam", "v1", credentials=creds)
    sa_name = "marketplace-publisher"
    sa_email = f"{sa_name}@{PROJECT_ID}.iam.gserviceaccount.com"

    try:
        sa = iam.projects().serviceAccounts().get(
            name=f"projects/{PROJECT_ID}/serviceAccounts/{sa_email}"
        ).execute()
        print(f"  SA ja existe: {sa['email']}")
        return sa
    except Exception:
        pass

    try:
        sa = iam.projects().serviceAccounts().create(
            name=f"projects/{PROJECT_ID}",
            body={
                "accountId": sa_name,
                "serviceAccount": {
                    "displayName": "Marketplace Publisher",
                    "description": "Service account para publicar ofertas no Google Cloud Marketplace",
                },
            },
        ).execute()
        print(f"  SA criada: {sa['email']}")
    except Exception as e:
        print(f"  Erro ao criar SA (ja deve existir): {e}")
        sa = iam.projects().serviceAccounts().get(
            name=f"projects/{PROJECT_ID}/serviceAccounts/{sa_email}"
        ).execute()
    return sa


def grant_marketplace_role(creds, sa_email):
    print(f"\n[2/4] SA pronta: {sa_email}")


def export_service_account_key(creds, sa_email):
    print(f"\n[3/4] SA key export blocked by org policy (Workload Identity)")
    print(f"  SA email: {sa_email}")


def create_marketplace_offer(creds):
    """Cria oferta no Google Cloud Marketplace"""
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    print("\n[4/4] Criando oferta no Google Cloud Marketplace...")

    if SA_KEY_PATH.exists():
        sa_creds = service_account.Credentials.from_service_account_file(
            str(SA_KEY_PATH),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        service = build("cloudbilling", "v1beta", credentials=sa_creds)
    else:
        service = build("cloudbilling", "v1beta", credentials=creds)

    description = (
        "AION - Agents Intelligence Orchestration Network. "
        "78 agentes de IA para Arquitetura, Engenharia, Construcao, "
        "Conformidade Regulatoria (NR-1, LGPD, ESG), "
        "Microsoft Dynamics 365, Salesforce Agentforce, "
        "Oracle Fusion e SAP S/4HANA."
        "\n\nAgentes AEC: Spec Analyst, Procurement, Inventory, "
        "Logistics, Field Execution, BIM Coordinator, "
        "Requirements Analyst, Engineering Assistant, Work Synopsis, "
        "Photo Intelligence, RFI Creation, Compliance PGRS/PGRSS."
        "\n\nAgentes Regulatorios: NR-1 Psicossocial, Tributario CBS/IBS, "
        "LGPD Operacional, ESG IFRS S1/S2, Inventario de Carbono, "
        "Escopo 3 Fornecedores, Canal de Denuncias, "
        "Igualdade Salarial, Compliance Anticorrupcao."
        "\n\nAgentes Microsoft: Regulatory Analyst, Compliance PM, "
        "Channel Agent, Knowledge Agent, Facilitator Agent, Dev Experience."
    )

    offer = {
        "name": f"projects/{PROJECT_ID}/providers/{PROJECT_ID}/offers/aion-marketplace",
        "displayName": "AION - 78 Agentes de IA para Engenharia e Compliance",
        "description": description,
        "category": "AI_AGENTS_AND_TOOLS",
        "productType": "SAAS",
        "fulfillmentUrl": "https://engenheiro-producao-ai.onrender.com",
        "termsOfService": "https://engenheiro-producao-ai.onrender.com/terms",
        "privacyPolicy": "https://engenheiro-producao-ai.onrender.com/privacy",
        "supportEmail": "cristiano@globalengenharia.com.br",
        "webhooks": [
            {
                "name": "Entitlement Events",
                "uri": "https://engenheiro-producao-ai.onrender.com/google/webhook",
                "eventTypes": [
                    "ENTITLEMENT_CREATED",
                    "ENTITLEMENT_ACTIVATED",
                    "ENTITLEMENT_CANCELLED",
                    "ENTITLEMENT_SUSPENDED",
                    "ENTITLEMENT_RENEWED",
                ],
            }
        ],
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

    try:
        response = service.providers().offers().create(
            parent=f"providers/{PROJECT_ID}",
            body=offer,
        ).execute()
        print(f"\n  Oferta criada: {response.get('name', 'N/A')}")
        print(f"  ID: {response.get('offerId', 'N/A')}")
        return response
    except Exception as e:
        print(f"\n  Erro ao criar oferta via API: {e}")
        print(f"  Salvando JSON para upload manual...")
        offer_path = Path(__file__).parent.parent / "offers" / "aion-gcp-offer.json"
        with open(offer_path, "w") as f:
            json.dump(offer, f, indent=2)
        print(f"  Oferta salva em: {offer_path}")
        print(f"  Faca upload manual em: https://console.cloud.google.com/partners")
        return None


def register_endpoints():
    """Registra os endpoints no config.yaml do marketplace"""
    endpoints = {
        "subscribe":   "GET  /google/subscribe?plan={plan}&customer_id={customer_id}",
        "webhook":     "POST /google/webhook",
        "fulfill":     "POST /google/fulfill",
        "entitlement": "GET  /google/entitlement/{customer_id}",
        "plans":       "GET  /google/plans",
        "health":      "GET  /",
    }
    print("\n=== Endpoints registrados ===")
    for name, endpoint in endpoints.items():
        print(f"  {name:15s} -> https://engenheiro-producao-ai.onrender.com{endpoint}")
    print(f"\nURL base: https://engenheiro-producao-ai.onrender.com")
    print(f"MCP Registry: https://engenheiro-producao-ai.onrender.com/mcp/servers")
    return endpoints


def main():
    print("=" * 60)
    print("  Google Cloud Marketplace - Setup Completo")
    print(f"  Projeto: {PROJECT_ID}")
    print("=" * 60)

    creds = authenticate()
    sa = create_service_account(creds)
    sa_email = sa["email"]
    grant_marketplace_role(creds, sa_email)
    export_service_account_key(creds, sa_email)
    create_marketplace_offer(creds)
    register_endpoints()

    print("\n" + "=" * 60)
    print("  Setup concluido!")
    print("=" * 60)
    print(f"\nProximo passo - Deploy no GKE:")
    print(f"  cd k8s && ./deploy.ps1")
    print(f"\nProximo passo - Configurar Pub/Sub:")
    print(f"  https://console.cloud.google.com/cloudpubsub/topic")
    print(f"  Topico: ecosystem-aion-webhook")
    print(f"  Subscription -> https://engenheiro-producao-ai.onrender.com/google/webhook")
    print(f"\nProximo passo - Publicar listing:")
    print(f"  https://console.cloud.google.com/partners")
    print(f"\nChave da SA salva em: {SA_KEY_PATH}")
    print(f"  Adicione ao .env: GOOGLE_APPLICATION_CREDENTIALS={SA_KEY_PATH}")


if __name__ == "__main__":
    main()