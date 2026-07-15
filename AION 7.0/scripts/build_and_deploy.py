"""
Trigger Cloud Build para construir e deployar as imagens no GKE
"""
import json
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

PROJECT_ID = "global-engenharia-498823"
REGION = "southamerica-east1"
TOKEN_PATH = Path.home() / ".aion" / "google_marketplace_token.json"
CLIENT_SECRET = Path(__file__).parent.parent.parent / "client_secret_757085749411-t95chtg2tpui3hjov165lratnj3fb0fc.apps.googleusercontent.com.json"
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def authenticate():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def setup_artifact_registry(creds):
    """Cria repositório no Artifact Registry"""
    parent = f"projects/{PROJECT_ID}/locations/{REGION}"
    repo_id = "aion"

    try:
        service = build("artifactregistry", "v1", credentials=creds)
        service.projects().locations().repositories().create(
            parent=parent,
            repositoryId=repo_id,
            body={
                "format": "DOCKER",
                "description": "AION Agent Images",
                "mode": "STANDARD_REPOSITORY",
            },
        ).execute()
        print(f"  Repositorio criado: {repo_id}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  Repositorio ja existe: {repo_id}")
        else:
            print(f"  Repositorio: {e}")
            print(f"  Criando via URL: https://console.cloud.google.com/artifacts/create-repo?project={PROJECT_ID}")


def trigger_cloud_build(creds):
    """Dispara Cloud Build para construir imagens"""
    cloudbuild = build("cloudbuild", "v1", credentials=creds)

    trigger_body = {
        "name": "aion-build-deploy",
        "description": "Build + Deploy AION 7.0 no GKE",
        "triggerTemplate": {
            "projectId": PROJECT_ID,
            "repoName": "aion",
            "branchName": "main",
        },
        "build": {
            "steps": [
                {"name": "gcr.io/cloud-builders/docker",
                 "args": ["build", "-t", f"{REGION}-docker.pkg.dev/$PROJECT_ID/aion/orchestrator:7.0.0", "-f", "Dockerfile", "."]},
                {"name": "gcr.io/cloud-builders/docker",
                 "args": ["push", f"{REGION}-docker.pkg.dev/$PROJECT_ID/aion/orchestrator:7.0.0"]},
                {"name": "gcr.io/cloud-builders/kubectl",
                 "args": ["set", "image", "deployment/aion-orchestrator", f"orchestrator={REGION}-docker.pkg.dev/$PROJECT_ID/aion/orchestrator:7.0.0", "-n", "aion"],
                 "env": ["CLOUDSDK_COMPUTE_REGION=southamerica-east1", "CLOUDSDK_CONTAINER_CLUSTER=aion-gke"]},
            ],
            "images": [f"{REGION}-docker.pkg.dev/$PROJECT_ID/aion/orchestrator:7.0.0"],
        },
    }

    try:
        trigger = cloudbuild.projects().triggers().create(
            projectId=PROJECT_ID, body=trigger_body
        ).execute()
        print(f"  Trigger criada: {trigger.get('name', '')}")

        # Executar build manual agora
        build_body = {
            "projectId": PROJECT_ID,
            "source": {"storageSource": {"bucket": f"{PROJECT_ID}_cloudbuild", "object": "cloudbuild.yaml"}},
            "steps": [
                {"name": "gcr.io/cloud-builders/docker",
                 "args": ["build", "-t", f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/orchestrator:7.0.0", "-f", "Dockerfile", "."]},
                {"name": "gcr.io/cloud-builders/docker",
                 "args": ["push", f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/orchestrator:7.0.0"]},
            ],
            "images": [f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/orchestrator:7.0.0"],
        }
        print("\nEnviando build manual...")
        operation = cloudbuild.projects().builds().create(
            projectId=PROJECT_ID, body=build_body
        ).execute()

        build_id = operation["metadata"]["build"]["id"]
        print(f"  Build ID: {build_id}")
        print(f"  Acompanhe: https://console.cloud.google.com/cloud-build/builds;region=global/{build_id}?project={PROJECT_ID}")
        return build_id
    except Exception as e:
        print(f"  Erro Cloud Build: {e}")
        print(f"\nBuild manual via Console:")
        print(f"  https://console.cloud.google.com/cloud-build/triggers;region=global/add?project={PROJECT_ID}")
        return None


def update_deployments_from_build(build_id):
    """Após build, atualizar deployments com a imagem correta"""
    print("\nApos o build concluir, execute:")
    print(f"  kubectl set image deployment/aion-orchestrator orchestrator={REGION}-docker.pkg.dev/{PROJECT_ID}/aion/orchestrator:7.0.0 -n aion")
    print(f"  kubectl set image deployment/aion-mcp-regulatory mcp-regulatory={REGION}-docker.pkg.dev/{PROJECT_ID}/aion/mcp-regulatory:7.0.0 -n aion")
    print(f"  kubectl set image deployment/aion-mcp-esg mcp-esg={REGION}-docker.pkg.dev/{PROJECT_ID}/aion/mcp-esg:7.0.0 -n aion")
    print(f"  kubectl set image deployment/aion-mcp-erp mcp-erp={REGION}-docker.pkg.dev/{PROJECT_ID}/aion/mcp-erp:7.0.0 -n aion")
    print(f"  kubectl set image deployment/aion-mcp-microsoft mcp-microsoft={REGION}-docker.pkg.dev/{PROJECT_ID}/aion/mcp-microsoft:7.0.0 -n aion")


def enable_gke_workload_identity(creds):
    """Habilita Workload Identity no cluster"""
    container = build("container", "v1", credentials=creds)
    parent = f"projects/{PROJECT_ID}/locations/{REGION}"

    cluster = container.projects().locations().clusters().get(
        name=parent + f"/clusters/{CLUSTER_NAME}"
    ).execute()

    if "workloadIdentityConfig" not in cluster or not cluster["workloadIdentityConfig"].get("workloadPool"):
        print("Habilitando Workload Identity...")
        update = {
            "update": {
                "desiredWorkloadIdentityConfig": {
                    "workloadPool": f"{PROJECT_ID}.svc.id.goog",
                },
            },
        }
        op = container.projects().locations().clusters().update(
            name=parent + f"/clusters/{CLUSTER_NAME}",
            body=update,
        ).execute()
        print(f"  Workload Identity ativado!")

    # Vincular SA do K8s com SA do GCP
    k8s_ns = "aion"
    k8s_sa = "aion-orchestrator"
    gcp_sa = "aion-gke-sa@{PROJECT_ID}.iam.gserviceaccount.com"
    print(f"  Vincular SA: kubectl annotate serviceaccount {k8s_sa} -n {k8s_ns} iam.gke.io/gcp-service-account={gcp_sa}")


def main():
    PROJECT_ID = "global-engenharia-498823"
    CLUSTER_NAME = "aion-gke"
    REGION = "southamerica-east1"

    print("Autenticando...")
    creds = authenticate()

    print("\n[1/3] Configurando Artifact Registry...")
    setup_artifact_registry(creds)

    print("\n[2/3] Trigger Cloud Build...")
    build_id = trigger_cloud_build(creds)

    print("\n[3/3] Instrucoes pos-build...")
    update_deployments_from_build(build_id)

    print(f"\nRecursos:")
    print(f"  Cloud Build:    https://console.cloud.google.com/cloud-build?project={PROJECT_ID}")
    print(f"  Artifact Registry: https://console.cloud.google.com/artifacts?project={PROJECT_ID}")
    print(f"  GKE Cluster:    https://console.cloud.google.com/kubernetes/clusters/details/{REGION}/{CLUSTER_NAME}?project={PROJECT_ID}")
    print(f"  AppHub:         https://console.cloud.google.com/app-hub?project={PROJECT_ID}")
    print(f"  Agent Registry: https://console.cloud.google.com/app-hub/agent-registry?project={PROJECT_ID}")


if __name__ == "__main__":
    main()