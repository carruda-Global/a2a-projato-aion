"""Fetch build logs to debug failure"""
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

# Get build logs
logging = build("logging", "v2", credentials=creds)
log_filter = f'resource.type="build" AND resource.labels.build_id="{BUILD_ID}"'
try:
    entries = logging.entries().list(body={
        "resourceNames": [f"projects/{PROJECT_ID}"],
        "filter": log_filter,
        "orderBy": "timestamp asc",
        "pageSize": 50,
    }).execute()
    
    for entry in entries.get("entries", []):
        text = entry.get("textPayload", "")
        severity = entry.get("severity", "")
        if "error" in text.lower() or "Error" in text or "ERROR" in severity or "pip" in text.lower():
            print(f"[{severity}] {text[:500]}")
except Exception as e:
    print(f"Erro ao buscar logs: {e}")
    # Fallback: try to get the build step logs directly
    from googleapiclient.http import MediaIoBaseDownload
    import io
    
    try:
        storage = build("storage", "v1", credentials=creds)
        bucket_name = f"{PROJECT_ID}_cloudbuild"
        
        # List objects
        objects = storage.objects().list(bucket=bucket_name).execute()
        for obj in objects.get("items", []):
            if BUILD_ID in obj["name"]:
                print(f"Log: {obj['name']} - {obj.get('size', 0)} bytes")
                # Download last few lines
                req = storage.objects().get_media(bucket=bucket_name, object=obj["name"])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, req)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                content = fh.getvalue().decode("utf-8", errors="replace")
                lines = content.split("\n")
                for line in lines[-50:]:
                    print(line)
    except Exception as e2:
        print(f"Storage fallback: {e2}")