"""Get exact build log content"""
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

BUCKET = "757085749411.cloudbuild-logs.googleusercontent.com"
LOG = "log-43c44f2d-0074-4c37-8346-bcb53d2c413c.txt"

storage = build("storage", "v1", credentials=creds)
req = storage.objects().get_media(bucket=BUCKET, object=LOG)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, req)
done = False
while not done:
    _, done = downloader.next_chunk()
content = fh.getvalue().decode("utf-8", errors="replace")
lines = content.split("\n")
# Show last 30 error lines
for line in lines:
    lower = line.lower()
    if any(x in lower for x in ["error", "failed", "traceback", "killed", "exit code", "cannot", "no such"]):
        print(line[:300])
print(f"\n--- Total lines: {len(lines)} ---")
# Show last 5 lines
for line in lines[-5:]:
    print(line[:300])