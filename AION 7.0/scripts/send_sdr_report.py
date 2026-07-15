import httpx, asyncio, os

async def test():
    key = os.environ["RESEND_API_KEY"]
    async with httpx.AsyncClient(timeout=15) as http:
        r = await http.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "from": "Cristiano Arruda <onboarding@resend.dev>",
                "to": ["carruda2307@gmail.com"],
                "subject": "Prospeccao AION — Odebrecht, MRV, Vale",
                "text": """Oi Cristiano,

Pipeline de prospeccao executado com sucesso:

9 leads gerados em 3 setores:
- Construcao: Odebrecht, Gafisa, MRV (NR-1 + Spec Analyst)
- Industria: Vale, Embraer, Braskem (NR-1 + Inventario Carbono)
- Tecnologia: TOTVS, Movile, PagSeguro (LGPD + Code Review)

Todos com links WhatsApp prontos e mensagens humanizadas.

WhatsApp: wa.me/5511994798464
Site: global-engenharia.com/ecosystem

-- 
AION SDR Pipeline""",
            },
        )
        print(f"HTTP {r.status_code}")
        if r.status_code in (200, 201):
            print("EMAIL ENVIADO!")
        else:
            print(r.text[:300])

asyncio.run(test())
