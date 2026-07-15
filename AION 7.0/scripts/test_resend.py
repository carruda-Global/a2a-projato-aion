import httpx, asyncio

async def test():
    key = "re_HhcZ6ZYv_JPqKkpzX27CEBLaU4ouAyVHy"
    async with httpx.AsyncClient(timeout=15) as http:
        r = await http.get("https://api.resend.com/domains", headers={"Authorization": f"Bearer {key}"})
        print(f"Domains: HTTP {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            for d in data.get("data", []):
                name = d.get("name", "?")
                status = d.get("status", "?")
                print(f"  {name} -> {status}")

        r2 = await http.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "from": "AION <onboarding@resend.dev>",
                "to": ["carruda2307@gmail.com"],
                "subject": "Teste Pipeline AION",
                "text": "Pipeline SDR funcionando! WhatsApp + Email + NR-1 + Engenharia.\nglobal-engenharia.com/ecosystem",
            },
        )
        print(f"Send test: HTTP {r2.status_code}")
        if r2.status_code == 200 or r2.status_code == 201:
            print("EMAIL ENVIADO COM SUCESSO!")
        else:
            print(r2.text[:300])

asyncio.run(test())
