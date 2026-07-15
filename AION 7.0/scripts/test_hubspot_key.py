import httpx, asyncio, json, os
from dotenv import load_dotenv

load_dotenv()

async def test():
    key = os.environ["HUBSPOT_API_KEY"]
    async with httpx.AsyncClient(timeout=30) as http:

        endpoints = [
            ("GET", "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"),
            ("GET", "https://api.hubapi.com/crm/v3/objects/companies?limit=1"),
            ("GET", "https://api.hubapi.com/crm/v3/objects/deals?limit=1"),
            ("GET", "https://api.hubapi.com/integrations/v1/me"),
            ("GET", "https://api.hubapi.com/account-info/v3/details"),
            ("GET", "https://api.hubapi.com/owners/v2/owners"),
            ("GET", "https://api.hubapi.com/crm/v3/owners"),
            ("GET", "https://api.hubapi.com/cms/v3/pages/site-pages"),
            ("GET", "https://api.hubapi.com/cms/v3/pages/landing-pages"),
            ("GET", "https://api.hubapi.com/files/v3/files"),
            ("GET", "https://api.hubapi.com/developer/projects/v1/projects"),
            ("GET", "https://api.hubapi.com/crm/v3/pipelines/deals"),
            ("GET", "https://api.hubapi.com/crm/v3/schemas/contacts"),
            ("GET", "https://api.hubapi.com/crm/v3/schemas/companies"),
            ("GET", "https://api.hubapi.com/crm/v3/schemas/deals"),
            ("GET", "https://api.hubapi.com/cms/v3/domains"),
            ("GET", "https://api.hubapi.com/cms/v3/source-code"),
        ]

        for method, url in endpoints:
            r = await http.request(method, url, params={"hapikey": key})
            path = url.split("/api")[1] if "/api" in url else url
            if r.status_code == 200:
                data = r.json()
                if "results" in data:
                    items = data["results"]
                    print(f"OK {path}: {len(items)} items")
                    if items:
                        print(f"   First: {json.dumps(items[0], indent=2)[:200]}")
                else:
                    print(f"OK {path}: {json.dumps(data, indent=2)[:200]}")
            else:
                print(f"ERR {path}: HTTP {r.status_code} - {r.text[:150]}")

asyncio.run(test())
