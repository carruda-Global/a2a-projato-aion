"""Fetch build logs from default Cloud Build bucket"""
import io
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

creds = Credentials.from_authorized_user_file(
    str(Path.home() / ".aion" / "google_marketplace_token.json"),
    ["https://www.googleapis.com/auth/cloud-platform"],
)
creds.refresh(Request())

PROJECT_NUMBER = "757085749411"
BUILD_ID = "43c44f2d-0074-4c37-8346-bcb53d2c413c"
BUCKET = f"{PROJECT_NUMBER}.cloudbuild-logs.googleusercontent.com"
PREFIX = f"cloudbuild/{BUILD_ID}"

storage = build("storage", "v1", credentials=creds)
objs = storage.objects().list(bucket=BUCKET, prefix=PREFIX).execute()

items = objs.get("items", [])
if not items:
    print(f"No logs found at gs://{BUCKET}/{PREFIX}")
    # Try alternative path
    objs2 = storage.objects().list(bucket=BUCKET).execute()
    alt = [o for o in objs2.get("items", []) if "43c44f2d" in o["name"]]
    for a in alt[:5]:
        print(f"  Found: {a['name']}")
else:
    for obj in items:
        name = obj["name"]
        size = obj.get("size", 0)
        if size == 0:
            continue
        print(f"Log: {name} ({size} bytes)")
        req = storage.objects().get_media(bucket=BUCKET, object=name)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, req)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        content = fh.getvalue().decode("utf-8", errors="replace")
        for line in content.split("\n")[-30:]:
            if line.strip():
                print(line)
        break