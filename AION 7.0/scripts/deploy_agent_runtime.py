"""
Implanta AION no Google Cloud Agent Runtime via Dockerfile.

Uso:
    python scripts/deploy_agent_runtime.py
"""
import os
from pathlib import Path

import vertexai
from vertexai.preview import reasoning_engines

PROJECT_ID = "global-engenharia-498823"
LOCATION = "us-central1"
DOCKERFILE_PATH = Path(__file__).parent.parent / "Dockerfile"
SOURCE_DIR = Path(__file__).parent.parent


def get_credentials():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    TOKEN_PATH = Path.home() / ".aion" / "google_marketplace_token.json"
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    if creds.expired:
        creds.refresh(Request())
    return creds


def main():
    print("=" * 60)
    print("  AION - Deploy no Agent Runtime")
    print(f"  Projeto: {PROJECT_ID} | Regiao: {LOCATION}")
    print("=" * 60)

    creds = get_credentials()

    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=creds)

    print("\n[1/2] Criando Agent Engine no Vertex AI...")
    try:
        agent = reasoning_engines.ReasoningEngine.create(
            reasoning_engines.AdkApp(
                agent=None,
                enable_tracing=False,
            ),
            display_name="AION - Agents Intelligence Orchestration Network",
            description="78 agentes de IA para Engenharia, Compliance (NR-1, LGPD, ESG) e ERP (Dynamics, SAP, Oracle, Salesforce)",
            requirements=[
                "fastapi==0.115.0",
                "uvicorn[standard]==0.30.0",
                "anthropic>=0.40.0",
                "openai>=1.50.0",
                "google-generativeai>=0.8.0",
                "pydantic[email]>=2.9.0",
                "supabase>=2.5.0",
                "langgraph>=0.2.0",
                "langchain-core>=0.2.27",
            ],
        )
        print(f"\n  [OK] Agent Engine criado!")
        print(f"  Resource: {agent.resource_name}")
        print(f"  ID: {agent.name}")
    except Exception as e:
        print(f"\n  Erro ao criar via SDK: {e}")
        print("\n[2/2] Tentando via gcloud CLI...")
        _deploy_via_gcloud()


def _deploy_via_gcloud():
    import subprocess
    import sys

    gcloud = r"C:\Users\crist\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.ps1"

    cmd = [
        "powershell", "-File", gcloud,
        "agents", "engines", "create",
        "--display-name=AION - Agents Intelligence Orchestration Network",
        "--description=78 agentes de IA para Engenharia e Compliance",
        f"--project={PROJECT_ID}",
        f"--location={LOCATION}",
        "--dockerfile=Dockerfile",
    ]

    print(f"  Executando: {' '.join(cmd[3:])}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SOURCE_DIR))
    if result.returncode == 0:
        print(f"  [OK] {result.stdout}")
    else:
        print(f"  Erro: {result.stderr[:300]}")
        print("\nAlternativa: use a aba 'Implantacoes' no console do Agent Registry")
        print(f"  https://console.cloud.google.com/ai/agents?project={PROJECT_ID}")


if __name__ == "__main__":
    main()
