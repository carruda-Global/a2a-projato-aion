"""Check build logs for latest failed build"""
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

BUILD_ID = "6010de91-fac6-4d31-98a1-5a381fdc8d28"
BUCKET = "757085749411.cloudbuild-logs.googleusercontent.com"
LOG = f"log-{BUILD_ID}.txt"

storage = build("storage", "v1", credentials=creds)
try:
    req = storage.objects().get_media(bucket=BUCKET, object=LOG)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, req)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    content = fh.getvalue().decode("utf-8", errors="replace")
    lines = content.split("\n")
    for line in lines[-20:]:
        print(line[:500])
except Exception as e:
    print(f"Logs nao encontrados: {e}")
    # Try alternative path
    objs = storage.objects().list(bucket=BUCKET).execute()
    for o in objs.get("items", []):
        if BUILD_ID in o["name"]:
            print(f"Found: {o['name']}")
            req = storage.objects().get_media(bucket=BUCKET, object=o["name"])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, req)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            content = fh.getvalue().decode("utf-8", errors="replace")
            for line in content.split("\n")[-10:]:
                print(line[:500])