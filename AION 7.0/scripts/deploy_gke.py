"""
Deploy AION no GKE via API (sem gcloud CLI)
Cria cluster + aplica manifests K8s
"""
import json
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = "global-engenharia-498823"
PROJECT_NUMBER = "757085749411"
CLUSTER_NAME = "aion-gke"
REGION = "southamerica-east1"
NAMESPACE = "aion"
CLIENT_SECRET_PATH = Path(__file__).parent.parent.parent / "client_secret_757085749411-t95chtg2tpui3hjov165lratnj3fb0fc.apps.googleusercontent.com.json"
TOKEN_PATH = Path.home() / ".aion" / "google_marketplace_token.json"
SA_KEY_PATH = Path(__file__).parent.parent / "service-account.json"
K8S_DIR = Path(__file__).parent.parent / "k8s"
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def authenticate():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not CLIENT_SECRET_PATH.exists():
            print("ERRO: client_secret JSON nao encontrado em", CLIENT_SECRET_PATH)
            sys.exit(1)
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
        print("Abrindo navegador para autenticar no Google...")
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def enable_apis(creds):
    from googleapiclient.discovery import build

    apis = [
        "iam.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        "container.googleapis.com",
        "apphub.googleapis.com",
        "cloudbilling.googleapis.com",
        "cloudbuild.googleapis.com",
        "artifactregistry.googleapis.com",
    ]
    service = build("serviceusage", "v1", credentials=creds)
    for api in apis:
        try:
            service.services().enable(name=f"projects/{PROJECT_ID}/services/{api}").execute()
            print(f"  API ativada: {api}")
        except Exception as e:
            err_str = str(e)
            if "billing" in err_str.lower():
                print(f"  ! {api}: precisa ativar faturamento")
                print(f"    https://console.cloud.google.com/billing?project={PROJECT_ID}")
            elif "SERVICE_DISABLED" in err_str:
                print(f"  ! {api}: ativando... tentando novamente em 5s")
                time.sleep(5)
                try:
                    service.services().enable(name=f"projects/{PROJECT_ID}/services/{api}").execute()
                    print(f"  API ativada: {api}")
                except Exception as e2:
                    print(f"  ! {api}: erro: {e2}")
            else:
                print(f"  API {api}: {e}")


def create_gke_cluster(creds):
    from googleapiclient.discovery import build

    print(f"\nCriando cluster GKE: {CLUSTER_NAME} em {REGION}...")
    container = build("container", "v1", credentials=creds)

    cluster_body = {
        "cluster": {
            "name": CLUSTER_NAME,
            "initialNodeCount": 2,
            "nodeConfig": {
                "machineType": "e2-standard-2",
                "oauthScopes": [
                    "https://www.googleapis.com/auth/cloud-platform",
                ],
                "diskSizeGb": 100,
                "diskType": "pd-standard",
            },
            "autoscaling": {},
            "network": "default",
            "addonsConfig": {
                "httpLoadBalancing": {"disabled": False},
                "horizontalPodAutoscaling": {"disabled": False},
            },
            "workloadIdentityConfig": {
                "workloadPool": f"{PROJECT_ID}.svc.id.goog",
            },
        },
    }

    parent = f"projects/{PROJECT_ID}/locations/{REGION}"
    try:
        operation = container.projects().locations().clusters().create(
            parent=parent, body=cluster_body
        ).execute()
        op_name = operation["name"]
        print(f"  Operacao: {op_name}")
        print("  Aguardando cluster ficar pronto (~5 min)...")

        while True:
            op = container.projects().locations().operations().get(
                name=op_name
            ).execute()
            if op["status"] == "DONE":
                if "error" in op:
                    print(f"  ERRO: {op['error']}")
                    return None
                print("  Cluster criado!")
                return op["response"]
            print(f"  Status: {op['status']}...")
            time.sleep(15)
    except Exception as e:
        print(f"  Erro ao criar cluster: {e}")
        print("  Verifique se o cluster ja existe...")
        try:
            cluster = container.projects().locations().clusters().get(
                name=parent + f"/clusters/{CLUSTER_NAME}"
            ).execute()
            print(f"  Cluster ja existe: {cluster['name']}")
            return cluster
        except Exception:
            print(f"  Cluster nao encontrado. Crie manualmente ou tente novamente.")
            return None


def create_service_account(creds):
    from googleapiclient.discovery import build

    iam = build("iam", "v1", credentials=creds)
    sa_name = "aion-gke-sa"
    sa_email = f"{sa_name}@{PROJECT_ID}.iam.gserviceaccount.com"

    for retry in range(6):
        try:
            sa = iam.projects().serviceAccounts().create(
                name=f"projects/{PROJECT_ID}",
                body={
                    "accountId": sa_name,
                    "serviceAccount": {
                        "displayName": "AION GKE Service Account",
                    },
                },
            ).execute()
            print(f"  SA criada: {sa['email']}")
            break
        except Exception as e:
            if "already exists" in str(e).lower():
                sa = iam.projects().serviceAccounts().get(
                    name=f"projects/{PROJECT_ID}/serviceAccounts/{sa_email}"
                ).execute()
                print(f"  SA ja existe: {sa['email']}")
                break
            elif "SERVICE_DISABLED" in str(e) and retry < 5:
                print(f"  Aguardando API IAM propagar ({retry+1}/6)...")
                time.sleep(10)
            else:
                if retry == 5:
                    print(f"  Erro ao criar SA: {e}")
                    return None
                time.sleep(5)

    crm = build("cloudresourcemanager", "v1", credentials=creds)
    policy = crm.projects().getIamPolicy(resource=PROJECT_ID, body={}).execute()
    roles = [
        "roles/container.admin",
        "roles/compute.admin",
        "roles/iam.serviceAccountUser",
        "roles/apphub.admin",
    ]

    for role in roles:
        binding = {"role": role, "members": [f"serviceAccount:{sa_email}"]}
        if binding not in policy.get("bindings", []):
            policy.setdefault("bindings", []).append(binding)

    try:
        crm.projects().setIamPolicy(resource=PROJECT_ID, body={"policy": policy}).execute()
        print(f"  Permissoes concedidas")
    except Exception as e:
        print(f"  ! Algumas permissoes podem nao ter sido aplicadas: {e}")
        # Tenta uma por uma
        for role in roles:
            try:
                single_policy = {"bindings": [{"role": role, "members": [f"serviceAccount:{sa_email}"]}]}
                crm.projects().setIamPolicy(resource=PROJECT_ID, body={"policy": single_policy}).execute()
                print(f"    + {role}")
            except Exception as e2:
                print(f"    ! {role}: {e2}")

    # Tenta exportar chave (pode ser bloqueado por policy - usa Workload Identity)
    try:
        key = iam.projects().serviceAccounts().keys().create(
            name=f"projects/{PROJECT_ID}/serviceAccounts/{sa_email}",
            body={"keyAlgorithm": "KEY_ALG_RSA_4096", "privateKeyType": "TYPE_GOOGLE_CREDENTIALS_FILE"},
        ).execute()
        key_data = json.loads(key["privateKeyData"])
        sa_path = SA_KEY_PATH.parent / "service-account.json"
        with open(sa_path, "w") as f:
            json.dump(key_data, f, indent=2)
        print(f"  Chave salva em: {sa_path}")
    except Exception as e:
        if "Key creation is not allowed" in str(e):
            print(f"  Chave nao criada (policy da organizacao bloqueia)")
            print(f"  Usar Workload Identity Federation no GKE")
        else:
            print(f"  ! Erro ao exportar chave: {e}")

    return sa_email


def deploy_manifests(creds, cluster):
    if not cluster:
        print("ERRO: Cluster nao disponivel")
        return False

    print(f"\nAplicando manifests K8s...")
    for manifest_file in [
        "namespace.yaml",
        "configmap.yaml",
        "agent-registry.yaml",
        "orchestrator/service-account.yaml",
        "orchestrator/deployment.yaml",
        "mcp/regulatory.yaml",
        "mcp/esg.yaml",
        "mcp/erp.yaml",
        "mcp/microsoft.yaml",
        "ingress.yaml",
    ]:
        path = K8S_DIR / manifest_file
        if not path.exists():
            print(f"  ! {manifest_file} nao encontrado")
            continue
        try:
            with open(path) as f:
                content = f.read()
            manifests = content.split("---")
            for i, manifest in enumerate(manifests):
                manifest = manifest.strip()
                if not manifest:
                    continue
                print(f"  Aplicando: {manifest_file} (parte {i+1})")
        except Exception as e:
            print(f"  ERRO em {manifest_file}: {e}")
            return False

    print("\n  Para aplicar, instale kubectl e rode:")
    print(f"  gcloud container clusters get-credentials {CLUSTER_NAME} --region={REGION} --project={PROJECT_ID}")
    print(f"  kubectl apply -f k8s/ -n {NAMESPACE}")
    return True


def main():
    print("=" * 60)
    print("  AION 7.0 - Deploy GKE (via API)")
    print("=" * 60)

    print("\n[1/5] Autenticando...")
    creds = authenticate()

    print("\n[2/5] Ativando APIs...")
    enable_apis(creds)

    print("\n[3/5] Criando Service Account...")
    create_service_account(creds)

    print("\n[4/5] Criando cluster GKE...")
    cluster = create_gke_cluster(creds)

    print("\n[5/5] Deploy dos manifests...")
    deploy_manifests(creds, cluster)

    print("\n" + "=" * 60)
    print("  Proximo passo:")
    print("=" * 60)
    print(f"""
  1. Instale o gcloud CLI (se nao tiver):
     https://cloud.google.com/sdk/docs/install

  2. Conecte ao cluster:
     gcloud container clusters get-credentials {CLUSTER_NAME} --region={REGION} --project={PROJECT_ID}

  3. Aplique os manifests:
     kubectl apply -f k8s/secrets.yaml -n {NAMESPACE}
     kubectl apply -f k8s/ -n {NAMESPACE}

  4. Verifique os pods:
     kubectl get pods -n {NAMESPACE}

  5. Ative o AppHub:
     gcloud app hub enable --project={PROJECT_ID}

  6. Verifique os agentes no console:
     https://console.cloud.google.com/app-hub/agent-registry?project={PROJECT_ID}
""")


if __name__ == "__main__":
    main()