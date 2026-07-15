import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()


async def fetch_hubspot_data():
    api_key = os.getenv("HUBSPOT_API_KEY", "")
    if not api_key:
        print("[!] HUBSPOT_API_KEY nao configurada no .env")
        return

    import httpx

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as http:
        print("=" * 60)
        print("HUBSPOT - LISTA DE VENDAS (DEALS)")
        print("=" * 60)

        deals_resp = await http.get(
            "https://api.hubapi.com/crm/v3/objects/deals?limit=100"
            "&properties=dealname,amount,dealstage,createdate,closedate,description,pipeline",
            headers=headers,
        )

        if deals_resp.status_code != 200:
            print(f"[!] Erro deals: HTTP {deals_resp.status_code}")
            print(deals_resp.text[:300])
            return

        deals = deals_resp.json()
        results = deals.get("results", [])
        total = deals.get("total", len(results))

        print(f"\nTotal de deals: {total}")
        print(f"{'#':<4} {'Deal Name':<35} {'Valor':<12} {'Stage':<25} {'Criado em':<20}")
        print("-" * 100)

        for i, deal in enumerate(results, 1):
            props = deal.get("properties", {})
            name = props.get("dealname", "-")[:34]
            amount = props.get("amount", "0")
            try:
                amount_f = float(amount)
                amount_str = f"R$ {amount_f:,.2f}" if amount_f > 0 else "-"
            except (ValueError, TypeError):
                amount_str = "-"
            stage = (props.get("dealstage", "").split("/")[-1] if props.get("dealstage") else "-")[:24]
            created = (props.get("createdate", "")[:10] if props.get("createdate") else "-")

            # Buscar nome do contato associado
            contact_name = ""
            try:
                assoc = await http.get(
                    f"https://api.hubapi.com/crm/v3/objects/deals/{deal['id']}/associations/contacts",
                    headers=headers,
                )
                if assoc.status_code == 200:
                    assoc_data = assoc.json()
                    if assoc_data.get("results"):
                        cid = assoc_data["results"][0]["id"]
                        contact = await http.get(
                            f"https://api.hubapi.com/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,email",
                            headers=headers,
                        )
                        if contact.status_code == 200:
                            cp = contact.json().get("properties", {})
                            contact_name = f"{cp.get('firstname','')} {cp.get('lastname','')} ({cp.get('email','')})"
            except Exception:
                pass

            print(f"{i:<4} {name:<35} {amount_str:<12} {stage:<25} {created:<20}")
            if contact_name:
                print(f"     Contato: {contact_name}")

        print(f"\n{'-' * 60}")
        print("CONTATOS (lead gen)")
        print("-" * 60)

        contacts_resp = await http.get(
            "https://api.hubapi.com/crm/v3/objects/contacts?limit=50"
            "&properties=email,firstname,lastname,company,phone,createdate",
            headers=headers,
        )

        if contacts_resp.status_code == 200:
            contacts = contacts_resp.json()
            for c in contacts.get("results", []):
                p = c.get("properties", {})
                name = f"{p.get('firstname','')} {p.get('lastname','')}".strip()
                email = p.get("email", "")
                company = p.get("company", "")
                phone = p.get("phone", "")
                created = p.get("createdate", "")[:10]
                print(f"  {name:<30} {email:<35} {company:<30} {phone:<20} {created}")

        print(f"\n{'-' * 60}")
        print("EMPRESAS")
        print("-" * 60)

        companies_resp = await http.get(
            "https://api.hubapi.com/crm/v3/objects/companies?limit=50"
            "&properties=name,domain,phone,industry,website,createdate",
            headers=headers,
        )

        if companies_resp.status_code == 200:
            companies = companies_resp.json()
            for co in companies.get("results", []):
                p = co.get("properties", {})
                name = p.get("name", "-")
                domain = p.get("domain", "-")
                industry = p.get("industry", "-")
                created = p.get("createdate", "")[:10]
                print(f"  {name:<35} {domain:<25} {industry:<30} {created}")

        print(f"\n{'-' * 60}")
        print(f"Total: {len(results)} deals | {len(contacts.get('results',[]))} contatos | {len(companies.get('results',[]))} empresas")


if __name__ == "__main__":
    asyncio.run(fetch_hubspot_data())
