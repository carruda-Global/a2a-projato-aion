"""Wait for build and update deployments"""
import time
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PROJECT_ID = "global-engenharia-498823"
REGION = "southamerica-east1"
BUILD_ID = "43c44f2d-0074-4c37-8346-bcb53d2c413c"

creds = Credentials.from_authorized_user_file(
    str(Path.home() / ".aion" / "google_marketplace_token.json"),
    ["https://www.googleapis.com/auth/cloud-platform"],
)
creds.refresh(Request())

cb = build("cloudbuild", "v1", credentials=creds)

print("Aguardando build...")
while True:
    b = cb.projects().builds().get(projectId=PROJECT_ID, id=BUILD_ID).execute()
    s = b["status"]
    if s in ("SUCCESS", "FAILURE", "TIMEOUT", "CANCELLED"):
        print(f"Build {s}")
        if s == "SUCCESS":
            print("Imagens prontas!")
        break
    print(f"  Status: {s}")
    time.sleep(30)

if s == "SUCCESS":
    print("\nAtualizando deployments no GKE...")
    # Update with kubectl via API
    container = build("container", "v1", credentials=creds)
    cluster = container.projects().locations().clusters().get(
        name=f"projects/{PROJECT_ID}/locations/{REGION}/clusters/aion-gke"
    ).execute()
    print(f"Cluster: {cluster['endpoint']}")
    
    # Get kubeconfig and apply via Kubernetes API
    from kubernetes import client, config
    import base64
    import tempfile
    
    creds.refresh(Request())
    cert_pem = base64.b64decode(cluster["masterAuth"]["clusterCaCertificate"]).decode()
    cert_file = tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False)
    cert_file.write(cert_pem)
    cert_file.close()
    
    k8s_client = client.Configuration()
    k8s_client.host = f"https://{cluster['endpoint']}"
    k8s_client.ssl_ca_cert = cert_file.name
    k8s_client.api_key = {"authorization": f"Bearer {creds.token}"}
    k8s_client.api_key_prefix = {"authorization": "Bearer"}
    
    apps = client.AppsV1Api(client.ApiClient(k8s_client))
    
    img = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/orchestrator:7.0.0"
    patch = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{"name": "orchestrator", "image": img}]
                }
            }
        }
    }
    
    try:
        apps.patch_namespaced_deployment(
            name="aion-orchestrator",
            namespace="aion",
            body=patch,
        )
        print(f"  Deployment aion-orchestrator updated to {img}")
    except Exception as e:
        print(f"  Erro ao atualizar: {e}")
        print(f"\nComando manual:")
        print(f"  kubectl set image deployment/aion-orchestrator orchestrator={img} -n aion")
    
    import os
    os.unlink(cert_file.name)

else:
    print(f"\nVer logs: https://console.cloud.google.com/cloud-build/builds;region=global/{BUILD_ID}?project={PROJECT_ID}")