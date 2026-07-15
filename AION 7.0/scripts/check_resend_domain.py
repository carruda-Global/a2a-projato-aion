import httpx, asyncio, json

async def main():
    key = "re_HhcZ6ZYv_JPqKkpzX27CEBLaU4ouAyVHy"
    async with httpx.AsyncClient(timeout=15) as http:
        r = await http.get("https://api.resend.com/domains", headers={"Authorization": f"Bearer {key}"})
        data = r.json()
        print("Dominios Resend:")
        for d in data.get("data", []):
            name = d.get("name", "")
            status = d.get("status", "")
            region = d.get("region", "")
            created = d.get("created_at", "")[:10]
            print(f"  {name} | {status} | {region} | criado: {created}")

        # Testar envio com dominio verificado
        if data.get("data"):
            domain = data["data"][0]["name"]
            print(f"\nTestando envio de {domain}...")
            r2 = await http.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "from": f"Cristiano Arruda <cristiano@{domain}>",
                    "to": ["carruda2307@gmail.com"],
                    "subject": "Teste dominio verificado",
                    "text": "Pipeline SDR + WhatsApp + NR-1 + Engenharia funcionando!",
                },
            )
            print(f"HTTP {r2.status_code}")
            if r2.status_code in (200, 201):
                print("EMAIL ENVIADO!")
                return domain
            else:
                print(r2.text[:200])
        return None

domain = asyncio.run(main())
