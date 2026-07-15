"""Check build status"""
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = Path.home() / ".aion" / "google_marketplace_token.json"
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
PROJECT_ID = "global-engenharia-498823"
BUILD_ID = "866311b5-0fe7-49c9-8bdf-cd1045edef4a"

creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
creds.refresh(Request())

cb = build("cloudbuild", "v1", credentials=creds)
build = cb.projects().builds().get(projectId=PROJECT_ID, id=BUILD_ID).execute()

print(f"Status: {build['status']}")
for step in build.get("steps", []):
    if step.get("status") == "FAILURE":
        print(f"  STEP FAILED: {step.get('name')} {' '.join(step.get('args', []))}")

print("\nImages built:")
for img in build.get("results", {}).get("images", []):
    print(f"  {img}")

errors = []
for step in build.get("steps", []):
    if step.get("status") == "FAILURE":
        errors.extend(step.get("timing", {}).keys())
print(f"\nDetalhes: https://console.cloud.google.com/cloud-build/builds;region=global/{BUILD_ID}?project={PROJECT_ID}")