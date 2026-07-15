"""Upload source to GCS and trigger Cloud Build"""
import io
import os
import tarfile
import tempfile
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

PROJECT_ID = "global-engenharia-498823"
REGION = "southamerica-east1"
BUCKET = f"{PROJECT_ID}_cloudbuild"

creds = Credentials.from_authorized_user_file(
    str(Path.home() / ".aion" / "google_marketplace_token.json"),
    ["https://www.googleapis.com/auth/cloud-platform"],
)
creds.refresh(Request())

# Create source tarball
root = Path(__file__).parent.parent
tar_path = root / ".aion-build.tar.gz"

print("Criando archive do source...")
with tarfile.open(tar_path, "w:gz") as tar:
    for f in root.rglob("*"):
        rel = f.relative_to(root)
        parts = str(rel).replace("\\", "/")
        # Skip venv, .git, __pycache__, etc
        if any(skip in parts for skip in ["venv/", ".git/", "__pycache__", ".pytest_cache", ".aion", "node_modules"]):
            continue
        if f.is_file():
            tar.add(f, arcname=parts)

print(f"Source: {tar_path} ({os.path.getsize(tar_path) / 1024:.0f} KB)")

# Upload to GCS
print("Uploading to GCS...")
storage = build("storage", "v1", credentials=creds)
object_name = f"source/aion-build-{REGION}.tar.gz"

media = MediaIoBaseUpload(
    io.BytesIO(open(tar_path, "rb").read()),
    mimetype="application/gzip",
    resumable=True,
)
storage.objects().insert(bucket=BUCKET, name=object_name, media_body=media).execute()
print(f"Uploaded: gs://{BUCKET}/{object_name}")

# Trigger Cloud Build with source reference
cb = build("cloudbuild", "v1", credentials=creds)

build_body = {
    "projectId": PROJECT_ID,
    "source": {
        "storageSource": {
            "bucket": BUCKET,
            "object": object_name,
        }
    },
    "steps": [
        {
            "name": "gcr.io/cloud-builders/docker",
            "args": [
                "build",
                "-t", f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/orchestrator:7.0.0",
                "-f", "Dockerfile",
                ".",
            ],
        },
        {
            "name": "gcr.io/cloud-builders/docker",
            "args": [
                "push",
                f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/orchestrator:7.0.0",
            ],
        },
    ],
    "images": [f"{REGION}-docker.pkg.dev/{PROJECT_ID}/aion/orchestrator:7.0.0"],
}

result = cb.projects().builds().create(projectId=PROJECT_ID, body=build_body).execute()
build_id = result["metadata"]["build"]["id"]
print(f"\nBuild disparado: {build_id}")
print(f"Link: https://console.cloud.google.com/cloud-build/builds;region=global/{build_id}?project={PROJECT_ID}")

# Cleanup
os.remove(tar_path)