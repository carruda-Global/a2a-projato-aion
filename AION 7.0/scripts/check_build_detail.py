"""Get detailed build failure info from API"""
import json
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
build = cb.projects().builds().get(
    projectId="global-engenharia-498823",
    id="74b0f01e-5630-435e-a425-2c32c7217b17"
).execute()

print(f"Status: {build['status']}")
for i, step in enumerate(build.get("steps", [])):
    print(f"\nStep {i}: {step.get('name')}")
    print(f"  Args: {' '.join(step.get('args', []))}")
    print(f"  Status: {step.get('status', 'unknown')}")

if "failureInfo" in build:
    print(f"\nFailure info:")
    print(json.dumps(build["failureInfo"], indent=2))

# Also check if there are more details in the build
print(f"\nBuild logs bucket: {build.get('logsBucket', 'N/A')}")
print(f"Source: {json.dumps(build.get('source', {}), indent=2)}")