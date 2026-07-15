"""
Aplica manifests K8s no GKE usando OAuth token + Kubernetes API
"""
import base64
import time
import yaml
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from kubernetes import client, config
from kubernetes.client.rest import ApiException

PROJECT_ID = "global-engenharia-498823"
CLUSTER_NAME = "aion-gke"
REGION = "southamerica-east1"
NAMESPACE = "aion"
K8S_DIR = Path(__file__).parent.parent / "k8s"
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


def get_cluster_info(creds):
    container = build("container", "v1", credentials=creds)
    cluster = container.projects().locations().clusters().get(
        name=f"projects/{PROJECT_ID}/locations/{REGION}/clusters/{CLUSTER_NAME}"
    ).execute()
    return cluster


def create_k8s_client(creds, cluster):
    import tempfile

    cert_b64 = cluster["masterAuth"]["clusterCaCertificate"]
    endpoint = cluster["endpoint"]

    creds.refresh(Request())

    cert_pem = base64.b64decode(cert_b64).decode()
    cert_file = tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False)
    cert_file.write(cert_pem)
    cert_file.close()

    configuration = client.Configuration()
    configuration.host = f"https://{endpoint}"
    configuration.ssl_ca_cert = cert_file.name
    configuration.api_key = {"authorization": f"Bearer {creds.token}"}
    configuration.api_key_prefix = {"authorization": "Bearer"}

    api_client = client.ApiClient(configuration)
    return api_client, cert_file.name


def apply_all(api_client):
    apps_api = client.AppsV1Api(api_client)
    core_api = client.CoreV1Api(api_client)
    rbac_api = client.RbacAuthorizationV1Api(api_client)
    networking_api = client.NetworkingV1Api(api_client)

    manifest_files = [
        "namespace.yaml", "configmap.yaml", "secrets.yaml", "agent-registry.yaml",
        "orchestrator/service-account.yaml", "orchestrator/deployment.yaml",
        "mcp/regulatory.yaml", "mcp/esg.yaml", "mcp/erp.yaml", "mcp/microsoft.yaml",
        "ingress.yaml",
    ]

    def safe_create(fn, body, kind):
        try:
            fn(body=body, namespace=NAMESPACE) if kind not in ("Namespace",) else fn(body=body)
            print(f"  OK: {body['metadata']['name']} ({kind})")
        except ApiException as e:
            if e.status == 409:
                print(f"  EXISTE: {body['metadata']['name']} ({kind})")
            elif "selfSubjectAccessReview" in str(e):
                print(f"  SEM PERMISSAO: {body['metadata']['name']} ({kind})")
            else:
                print(f"  ERRO {e.status}: {body['metadata']['name']} ({kind}): {e.reason}")

    for mf in manifest_files:
        path = K8S_DIR / mf
        if not path.exists():
            print(f"  ! {mf} nao encontrado")
            continue
        with open(path) as f:
            for doc in yaml.safe_load_all(f):
                if not doc:
                    continue
                kind = doc.get("kind", "")
                meta = doc.get("metadata", {})
                try:
                    if kind == "Namespace":
                        core_api.create_namespace(body=doc)
                        print(f"  Namespace: {meta['name']}")
                    elif kind == "ConfigMap":
                        safe_create(core_api.create_namespaced_config_map, doc, kind)
                    elif kind == "Secret":
                        safe_create(core_api.create_namespaced_secret, doc, kind)
                    elif kind == "ServiceAccount":
                        safe_create(core_api.create_namespaced_service_account, doc, kind)
                    elif kind == "Role":
                        safe_create(rbac_api.create_namespaced_role, doc, kind)
                    elif kind == "RoleBinding":
                        safe_create(rbac_api.create_namespaced_role_binding, doc, kind)
                    elif kind == "Deployment":
                        safe_create(apps_api.create_namespaced_deployment, doc, kind)
                    elif kind == "Service":
                        safe_create(core_api.create_namespaced_service, doc, kind)
                    elif kind == "Ingress":
                        safe_create(networking_api.create_namespaced_ingress, doc, kind)
                    elif kind == "ManagedCertificate":
                        print(f"  SKIP: {meta.get('name','')} ({kind}) - criar manualmente")
                    else:
                        print(f"  ? {kind}: {meta.get('name','')}")
                except Exception as e:
                    print(f"  ! {meta.get('name','')} ({kind}): {e}")

    print("\nStatus dos deployments:")
    time.sleep(5)
    for name in ["aion-orchestrator", "aion-mcp-regulatory", "aion-mcp-esg", "aion-mcp-erp", "aion-mcp-microsoft"]:
        try:
            d = apps_api.read_namespaced_deployment_status(name=name, namespace=NAMESPACE)
            r = d.status.ready_replicas or 0
            t = d.spec.replicas
            print(f"  {name}: {r}/{t}")
        except ApiException:
            print(f"  {name}: pendente")


def main():
    import os
    print("Autenticando...")
    creds = authenticate()
    print("Obtendo info do cluster...")
    cluster = get_cluster_info(creds)
    print(f"Conectando a {cluster['name']} em {cluster['endpoint']}...")
    api_client, cert_file = create_k8s_client(creds, cluster)
    print("Aplicando manifests...")
    apply_all(api_client)
    os.unlink(cert_file)
    print(f"\nDeploy concluido!")
    print(f"Agent Registry: https://console.cloud.google.com/app-hub/agent-registry?project={PROJECT_ID}")


if __name__ == "__main__":
    main()