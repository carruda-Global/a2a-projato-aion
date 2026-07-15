"""Wait for build then update GKE deployments + trigger next builds"""
import time
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PROJECT_ID = "global-engenharia-498823"
REGION = "southamerica-east1"
BUILD_ID = "01b05447-3aaa-491d-87f0-468ab1ee0fd7"

creds = Credentials.from_authorized_user_file(
    str(Path.home() / ".aion" / "google_marketplace_token.json"),
    ["https://www.googleapis.com/auth/cloud-platform"],
)
creds.refresh(Request())

cb = build("cloudbuild", "v1", credentials=creds)

print("Aguardando build principal...")
while True:
    b = cb.projects().builds().get(projectId=PROJECT_ID, id=BUILD_ID).execute()
    s = b["status"]
    if s in ("SUCCESS", "FAILURE", "TIMEOUT", "CANCELLED"):
        break
    print(f"  {s}...")
    time.sleep(30)

if s != "SUCCESS":
    print(f"Build {s}")
    print(f"Logs: https://console.cloud.google.com/cloud-build/builds;region=global/{BUILD_ID}?project={PROJECT_ID}")
    exit(1)

print("Build principal concluido!")

# Build MCP images too
print("\nDisparando builds dos MCP servers...")
for svc in ["mcp-regulatory", "mcp-esg", "mcp-erp", "mcp-microsoft"]:
    build_body = {
        "projectId": PROJECT_ID,
        "source": {"storageSource": {"bucket": f"{PROJECT_ID}_cloudbuild", "object": f"source/aion-build-{REGION}.tar.gz"}},
        "steps": [
            {"name": "gcr.io/cloud-builders/docker",
             "args": ["build", "-t", f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{svc}:7.0.0", "-f", "Dockerfile", "."]},
            {"name": "gcr.io/cloud-builders/docker",
             "args": ["push", f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{svc}:7.0.0"]},
        ],
        "images": [f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{svc}:7.0.0"],
    }
    result = cb.projects().builds().create(projectId=PROJECT_ID, body=build_body).execute()
    bid = result["metadata"]["build"]["id"]
    print(f"  {svc}: {bid}")

print("\nAguardando builds MCP terminarem...")
mcp_ids = []
while True:
    time.sleep(30)
    pending = False
    for svc in ["mcp-regulatory", "mcp-esg", "mcp-erp", "mcp-microsoft"]:
        body = {
            "projectId": PROJECT_ID,
            "source": {"storageSource": {"bucket": f"{PROJECT_ID}_cloudbuild", "object": f"source/aion-build-{REGION}.tar.gz"}},
            "steps": [
                {"name": "gcr.io/cloud-builders/docker",
                 "args": ["build", "-t", f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{svc}:7.0.0", "-f", "Dockerfile", "."]},
                {"name": "gcr.io/cloud-builders/docker",
                 "args": ["push", f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{svc}:7.0.0"]},
            ],
            "images": [f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/{svc}:7.0.0"],
        }
        result = cb.projects().builds().create(projectId=PROJECT_ID, body=body).execute()
        mcp_ids.append(result["metadata"]["build"]["id"])
    break

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
core = client.CoreV1Api(client.ApiClient(cfg))

updates = {
    "aion-orchestrator": {"container": "orchestrator", "image": f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/orchestrator:7.0.0"},
    "aion-mcp-regulatory": {"container": "mcp-regulatory", "image": f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/mcp-regulatory:7.0.0"},
    "aion-mcp-esg": {"container": "mcp-esg", "image": f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/mcp-esg:7.0.0"},
    "aion-mcp-erp": {"container": "mcp-erp", "image": f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/mcp-erp:7.0.0"},
    "aion-mcp-microsoft": {"container": "mcp-microsoft", "image": f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/mcp-microsoft:7.0.0"},
}

for deploy_name, info in updates.items():
    try:
        patch = {"spec": {"template": {"spec": {"containers": [{"name": info["container"], "image": info["image"]}]}}}}
        apps.patch_namespaced_deployment(name=deploy_name, namespace="aion", body=patch)
        print(f"  {deploy_name}: {info['image']}")
    except Exception as e:
        print(f"  {deploy_name}: erro - {e}")

import os
os.unlink(cert.name)

print("\nAguardando pods ficarem prontos...")
time.sleep(15)
for deploy_name in updates:
    try:
        d = apps.read_namespaced_deployment_status(name=deploy_name, namespace="aion")
        r = d.status.ready_replicas or 0
        t = d.spec.replicas
        print(f"  {deploy_name}: {r}/{t} prontos")
    except:
        pass

print(f"\nTudo pronto!")
print(f"Agent Registry: https://console.cloud.google.com/app-hub/agent-registry?project={PROJECT_ID}")
print(f"AppHub: https://console.cloud.google.com/app-hub?project={PROJECT_ID}")