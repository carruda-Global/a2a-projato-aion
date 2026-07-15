"""One-time interactive authorization for Google Search Console read access.

Reuses the existing OAuth "installed app" client for the global-engenharia
GCP project (global-engenharia-498823) — no new service account needed.
Search Console access belongs to whichever Google account owns/manages the
property, so this opens a browser for YOU to log in with that account and
grant read-only access.

Run once locally:
    python scripts/gsc_authorize.py

Prerequisite: the "Search Console API" must be enabled on project
global-engenharia-498823 (Google Cloud Console -> APIs & Services -> Enable).

Produces gsc_token.json (gitignored) containing a refresh token. Print its
contents and add as the GSC_REFRESH_TOKEN / GSC_CLIENT_ID / GSC_CLIENT_SECRET
env vars on Render so the server-side feedback loop can use it without any
further interactive login.
"""
import json
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
CLIENT_SECRETS_FILE = "../client_secret_757085749411-3gqmku41tvgih5gmk3c2kvkr5hukhfrc.apps.googleusercontent.com.json"
TOKEN_FILE = "gsc_token.json"


def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    token_data = {
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "token_uri": creds.token_uri,
        "scopes": creds.scopes,
    }
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)

    if not creds.refresh_token:
        print(
            "WARNING: no refresh_token returned — this Google account may have "
            "authorized this app before. Revoke access at "
            "https://myaccount.google.com/permissions and re-run this script.",
            file=sys.stderr,
        )
        return

    print(f"\nSaved {TOKEN_FILE}. Add these 3 values as Render env vars:")
    print(f"  GSC_CLIENT_ID={creds.client_id}")
    print(f"  GSC_CLIENT_SECRET={creds.client_secret}")
    print(f"  GSC_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()
