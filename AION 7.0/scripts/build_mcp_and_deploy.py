"""Build MCP images, update all deployments"""
import time
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PROJECT_ID = "global-engenharia-498823"
REGION = "southamerica-east1"

creds = Credentials.from_authorized_user_file(
    str(Path.home() / ".aion" / "google_marketplace_token.json"),
    ["https://www.googleapis.com/auth/cloud-platform"],
)
creds.refresh(Request())

cb = build("cloudbuild", "v1", credentials=creds)

services = ["mcp-regulatory", "mcp-esg", "mcp-erp", "mcp-microsoft"]
build_ids = []

for svc in services:
    print(f"\nDisparando build: {svc}...")
    body = {
        "projectId": PROJECT_ID,
        "source": {"storageSource": {"bucket": f"{PROJECT_ID}_cloudbuild", "object": "source/aion-build-southamerica-east1.tar.gz"}},
        "steps": [
            {"name": "gcr.io/cloud-builders/docker", "args": ["build", "-t", f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{svc}:7.0.0", "-f", "Dockerfile", "."]},
            {"name": "gcr.io/cloud-builders/docker", "args": ["push", f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{svc}:7.0.0"]},
        ],
        "images": [f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{svc}:7.0.0"],
    }
    result = cb.projects().builds().create(projectId=PROJECT_ID, body=body).execute()
    bid = result["metadata"]["build"]["id"]
    build_ids.append((svc, bid))
    print(f"  {svc}: {bid}")

# Wait for all to complete
print("\nAguardando todos os builds...")
for svc, bid in build_ids:
    while True:
        b = cb.projects().builds().get(projectId=PROJECT_ID, id=bid).execute()
        s = b["status"]
        if s in ("SUCCESS", "FAILURE", "TIMEOUT", "CANCELLED"):
            print(f"  {svc}: {s}")
            break
        time.sleep(15)

# Update all deployments
print("\nAtualizando deployments no GKE...")
import base64, tempfile
from kubernetes import client

container = build("container", "v1", credentials=creds)
cluster = container.projects().locations().clusters().get(
    name=f"projects/{PROJECT_ID}/locations/{REGION}/clusters/aion-gke"
).execute()
creds.refresh(Request())

cert_pem = base64.b64decode(cluster["masterAuth"]["clusterCaCertificate"]).decode()
cert = tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False)
cert.write(cert_pem)
cert.close()

cfg = client.Configuration()
cfg.host = f"https://{cluster['endpoint']}"
cfg.ssl_ca_cert = cert.name
cfg.api_key = {"authorization": f"Bearer {creds.token}"}
cfg.api_key_prefix = {"authorization": "Bearer"}

apps = client.AppsV1Api(client.ApiClient(cfg))

deployments = {
    "aion-orchestrator": "orchestrator",
    "aion-mcp-regulatory": "mcp-regulatory",
    "aion-mcp-esg": "mcp-esg",
    "aion-mcp-erp": "mcp-erp",
    "aion-mcp-microsoft": "mcp-microsoft",
}

for name, container_name in deployments.items():
    img = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{container_name}:7.0.0"
    try:
        patch = {"spec": {"template": {"spec": {"containers": [{"name": container_name, "image": img}]}}}}
        apps.patch_namespaced_deployment(name=name, namespace="aion", body=patch)
        print(f"  {name}: {img}")
    except Exception as e:
        print(f"  {name}: erro - {e}")

import os
os.unlink(cert.name)

print("\nAguardando pods...")
time.sleep(20)
for name in deployments:
    try:
        d = apps.read_namespaced_deployment_status(name=name, namespace="aion")
        r = d.status.ready_replicas or 0
        t = d.spec.replicas
        print(f"  {name}: {r}/{t} prontos")
    except:
        print(f"  {name}: verificando...")

print(f"\nConcluido! Ver em: https://console.cloud.google.com/kubernetes/workload?project={PROJECT_ID}")