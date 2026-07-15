import httpx, os, json, asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

TOKEN_FILE = Path.home() / ".config" / "aion" / "linkedin" / "tokens" / "access_token.json"

async def main():
    token_data = json.loads(TOKEN_FILE.read_text())
    access_token = token_data["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202503",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    async with httpx.AsyncClient(timeout=30) as http:

        print("=" * 60)
        print("TESTANDO ENDPOINTS LINKEDIN")
        print("=" * 60)

        # Test me
        r = await http.get("https://api.linkedin.com/v2/me", headers=headers)
        print(f"/v2/me: HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  {data}")

        # Test searchPeopleBlended (REST API)
        print()
        print("--- searchPeopleBlended ---")
        r = await http.post(
            "https://api.linkedin.com/rest/searchPeopleBlended",
            headers=headers,
            json={
                "filters": {
                    "keywords": "engenheiro segurança",
                    "networkDepth": "F",
                },
                "pagination": {"start": 0, "count": 10},
            },
        )
        print(f"HTTP {r.status_code}")
        if r.status_code != 200:
            print(f"  {r.text[:300]}")

        # Test searchCompanies
        print()
        print("--- searchCompanies ---")
        r = await http.get(
            "https://api.linkedin.com/rest/organizationSearch",
            headers=headers,
            params={
                "q": "search",
                "keywords": "construção civil engenharia",
                "count": 5,
            },
        )
        print(f"HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            items = data.get("elements", data.get("paging", {}))
            print(json.dumps(data, indent=2)[:500])
        elif r.status_code != 200:
            print(f"  {r.text[:300]}")

        # Try simple encoded search
        print()
        print("--- encoded search ---")
        try:
            from urllib.parse import quote
            q = quote("engenheiro segurança")
            r = await http.get(
                f"https://api.linkedin.com/v2/search?q=people&keywords={q}",
                headers=headers,
            )
            print(f"HTTP {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"  Found: {len(data.get('elements',[]))} results")
            else:
                print(f"  {r.text[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

asyncio.run(main())
