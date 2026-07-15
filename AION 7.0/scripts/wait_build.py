"""Check build and wait for completion"""
import time
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(
    str(Path.home() / ".aion" / "google_marketplace_token.json"),
    ["https://www.googleapis.com/auth/cloud-platform"],
)
creds.refresh(Request())

cb = build("cloudbuild", "v1", credentials=creds)
build_id = "74b0f01e-5630-435e-a425-2c32c7217b17"

print("Aguardando build...")
while True:
    b = cb.projects().builds().get(projectId="global-engenharia-498823", id=build_id).execute()
    s = b["status"]
    print(f"  Status: {s}")
    if s in ("SUCCESS", "FAILURE", "TIMEOUT", "CANCELLED"):
        break
    time.sleep(30)

if s == "SUCCESS":
    print("\nBuild concluido! Imagens:")
    for img in b.get("images", []):
        print(f"  {img}")
    print("\nAtualizando deployments...")
    from googleapiclient.discovery import build as k8s_build
    container = k8s_build("container", "v1", credentials=creds)
    cluster = container.projects().locations().clusters().get(
        name=f"projects/global-engenharia-498823/locations/southamerica-east1/clusters/aion-gke"
    ).execute()
    print(f"Cluster pronto: {cluster['name']}")
    print("\nProx passo: atualizar deployments no GKE")
else:
    print(f"\nBuild {s}")
    print(f"Logs: https://console.cloud.google.com/cloud-build/builds;region=global/{build_id}?project=global-engenharia-498823")