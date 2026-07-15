"""Get exact build log content for new build"""
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

BUILD_ID = "01b05447-3aaa-491d-87f0-468ab1ee0fd7"
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

print(f"Total lines: {len(lines)}")
for line in lines:
    lower = line.lower()
    if any(x in lower for x in ["error", "failed", "traceback", "killed", "exit code", "cannot", "no such", "step #"]):
        print(line[:500])
print("\n--- Last 10 lines ---")
for line in lines[-10:]:
    print(line)