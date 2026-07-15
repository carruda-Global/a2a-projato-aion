"""Fetch build logs from GCS"""
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

storage = build("storage", "v1", credentials=creds)
bucket_name = "global-engenharia-498823_cloudbuild"

objs = storage.objects().list(bucket=bucket_name).execute()
for obj in objs.get("items", []):
    if "43c44f2d" in obj["name"] and obj["name"].endswith(".txt"):
        size = obj.get("size", 0)
        name = obj["name"]
        print(f"Log: {name} ({size} bytes)")
        req = storage.objects().get_media(bucket=bucket_name, object=name)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, req)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        content = fh.getvalue().decode("utf-8", errors="replace")
        lines = content.split("\n")
        print(f"Total lines: {len(lines)}")
        for line in lines[-40:]:
            if line.strip():
                print(line)
        break