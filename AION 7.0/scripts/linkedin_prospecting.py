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
    }

    async with httpx.AsyncClient(timeout=30) as http:

        # Search for people
        print("=" * 60)
        print("BUSCANDO DECISORES — Construcao Civil Brasil")
        print("=" * 60)

        keywords = [
            "engenheiro civil diretor",
            "engenheiro segurança do trabalho", 
            "gerente construção civil",
            "diretor incorporadora",
            "RH construção civil",
        ]

        prospects = []

        for keyword in keywords:
            print(f"\nBusca: {keyword}")
            
            try:
                r = await http.get(
                    "https://api.linkedin.com/v2/search",
                    params={
                        "q": "people",
                        "keywords": keyword,
                        "count": 5,
                    },
                    headers=headers,
                )
            except Exception as e:
                print(f"  v2 search error: {e}")
                continue

            if r.status_code != 200:
                print(f"  HTTP {r.status_code}")
                continue

            data = r.json()
            elements = data.get("elements", [])

            for elem in elements:
                try:
                    urn = elem.get("targetUrn", "")
                    # Extract profile ID from URN
                    prof_id = urn.split(":")[-1] if urn else ""

                    # Get profile details
                    try:
                        rp = await http.get(
                            f"https://api.linkedin.com/v2/people/(id:{prof_id})",
                            headers=headers,
                        )
                        if rp.status_code != 200:
                            continue
                        profile = rp.json()
                    except Exception:
                        profile = {}

                    title_info = profile.get("headline", {}).get("localized", {})
                    first_name = ""
                    last_name = ""

                    # Try localized name
                    if isinstance(profile.get("firstName"), dict):
                        first_name = profile["firstName"].get("localized", {}).get("en_US", "")
                    elif isinstance(profile.get("firstName"), str):
                        first_name = profile["firstName"]

                    if isinstance(profile.get("lastName"), dict):
                        last_name = profile["lastName"].get("localized", {}).get("en_US", "")
                    elif isinstance(profile.get("lastName"), str):
                        last_name = profile["lastName"]

                    headline = ""
                    if isinstance(title_info, dict):
                        headline = title_info.get("en_US", "") or title_info.get("pt_BR", "")
                    elif isinstance(title_info, str):
                        headline = title_info

                    if first_name:
                        prospect = {
                            "name": f"{first_name} {last_name}",
                            "headline": headline,
                            "keyword": keyword,
                            "linkedin_id": prof_id,
                        }
                        prospects.append(prospect)
                        print(f"  {first_name} {last_name} — {headline[:60]}")
                except Exception as e:
                    print(f"  Error parsing: {e}")

        print()
        print("=" * 60)
        print(f"ENCONTRADOS: {len(prospects)} prospects")
        print("=" * 60)

        # Save to JSON for SDR agent
        outfile = Path(__file__).parent.parent / "data" / "linkedin_prospects.json"
        outfile.parent.mkdir(parents=True, exist_ok=True)
        outfile.write_text(json.dumps(prospects, indent=2, ensure_ascii=False))
        print(f"Salvo em: {outfile}")

        # Generate WhatsApp links
        print()
        print("=" * 60)
        print("LINKS WHATSAPP PARA CADA PROSPECT")
        print("=" * 60)
        wpp_number = "5511994798464"
        for p in prospects[:10]:
            msg = f"Olá {p['name'].split()[0]}, sou Cristiano Arruda da Global Engenharia. Temos uma solução de IA para NR-1 e LGPD que pode automatizar seu compliance. Podemos conversar?"
            encoded = msg.replace(" ", "%20").replace("\n", "%20")
            link = f"https://wa.me/{wpp_number}?text={encoded}"
            print(f"  {p['name']}")
            print(f"     {link[:100]}...")

asyncio.run(main())
