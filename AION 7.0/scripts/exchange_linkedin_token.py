import httpx, os, json, time, asyncio
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

CODE = "AQTEmGOtRQHlE4TNBS1vtNmCgoV3G8CpqcSoP3fK5JwozVneotmN8HcjM_tJ1iBqceun85a0hY0vUHOi9AH9YwASHFN6FTSX9FZuCUu073vJJoyb6TLFL5eYTY2Cor2za5JfpyuL29bCrWfp2t8X2ajD564oGbPpy1WAX6gR6Lbxq0aMuhm9R2dV2xg9YIc12H01oxMWIjSNBnRfzMA"

async def main():
    cid = os.getenv("LINKEDIN_CLIENT_ID", "")
    cs = os.getenv("LINKEDIN_CLIENT_SECRET", "")

    async with httpx.AsyncClient(timeout=30) as http:
        r = await http.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": CODE,
                "client_id": cid,
                "client_secret": cs,
                "redirect_uri": "http://127.0.0.1:9876/callback",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        print(f"HTTP {r.status_code}")

        if r.status_code == 200:
            data = r.json()
            at = data.get("access_token", "")
            rt = data.get("refresh_token", "")
            exp = data.get("expires_in", 0)
            scope = data.get("scope", "")

            print(f"Access Token: {len(at)} chars")
            print(f"Refresh Token: {len(rt)} chars")
            print(f"Expira em: {exp}s")
            print(f"Scope: {scope}")

            token_dir = Path.home() / ".config" / "aion" / "linkedin" / "tokens"
            token_dir.mkdir(parents=True, exist_ok=True)
            token_file = token_dir / "access_token.json"
            token_file.write_text(json.dumps({
                "access_token": at,
                "refresh_token": rt,
                "expires_in": exp,
                "scope": scope,
                "created_at": time.time(),
            }, indent=2))
            print(f"Token salvo: {token_file}")

            r2 = await http.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {at}"},
            )
            if r2.status_code == 200:
                u = r2.json()
                print(f"Nome: {u.get('name', '?')}")
                print(f"Email: {u.get('email', '?')}")
                print(f"ID: {u.get('sub', '?')}")
                print()
                print("LINKEDIN CONECTADO!")
            else:
                print(f"Userinfo: HTTP {r2.status_code} - {r2.text[:200]}")
        else:
            print(f"ERRO: {r.text[:500]}")

asyncio.run(main())
