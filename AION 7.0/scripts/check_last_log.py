"""Check latest build logs"""
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

BUILD_ID = "7d4a3e5e-e714-4dc0-8497-b9251b5d930e"
BUCKET = "757085749411.cloudbuild-logs.googleusercontent.com"
LOG = f"log-{BUILD_ID}.txt"

storage = build("storage", "v1", credentials=creds)
req = storage.objects().get_media(bucket=BUCKET, object=LOG)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, req)
done = False
while not done:
    _, done = downloader.next_chunk()
content = fh.getvalue().decode("utf-8", errors="replace")
lines = content.split("\n")
for line in lines[-15:]:
    print(line[:500])