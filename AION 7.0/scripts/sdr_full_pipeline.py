import json, os, sys, asyncio, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

import httpx
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents.outbound_sdr_agent import SYSTEM_PROMPT_HUMAN

WPP = os.getenv("WPP_NUMBER", "5511994798464")
RESEND_KEY = os.getenv("RESEND_API_KEY", "")
OR_KEY = os.getenv("OPENROUTER_API_KEY", "")
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
BLOCK = ("example", "sentry", "wixpress", "noreply", "no-reply", "yourdomain", "linkedin", "facebook", "google", "instagram", "wikipedia")

settings = Settings()
ds = DeepSeekClient(settings)

SECTORS = {
    "construcao": "NR-1 (riscos psicossociais) + Spec Analyst (analise de projetos BIM)",
    "industria": "NR-1 (obrigacao trabalhista) + Inventario Carbono (ESG IFRS S1 S2)",
    "tecnologia": "LGPD (privacidade de dados) + Software Engineering (code review automatico)",
}

async def discover_email(company: str) -> str:
    try:
        q = f"{company} contato email oficial"
        async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "Mozilla/5.0"}) as c:
            r = await c.get("https://html.duckduckgo.com/html/", params={"q": q})
            urls = re.findall(r"href=\"//duckduckgo\.com/l/\?uddg=([^&\"]+)", r.text)
            for url in urls[:3]:
                try:
                    page = await c.get(url, timeout=5, follow_redirects=True)
                    emails = EMAIL_RE.findall(page.text)
                    valid = [e for e in emails if not any(b in e.lower() for b in BLOCK)]
                    if valid:
                        return valid[0]
                except:
                    pass
    except:
        pass

    try:
        prompt = f"Qual email de contato publico mais provavel da empresa {company} no Brasil? Ex: contato@dominio.com.br, comercial@dominio.com.br. Retorne APENAS 1 email, sem explicacoes."
        async with httpx.AsyncClient(timeout=30) as http:
            r = await http.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OR_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://global-engenharia.com",
                },
                json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 60},
            )
            if r.status_code == 200:
                email = r.json()["choices"][0]["message"]["content"].strip()
                if "@" in email and "." in email and len(email) < 60:
                    return email
    except:
        pass

    return ""

async def main():
    all_prospects = []

    for sector in SECTORS:
        prompt = (
            f'Liste 3 empresas REAIS brasileiras do setor {sector} que precisam compliance NR-1/LGPD. '
            'Retorne APENAS JSON: [{"empresa":"nome real","cidade":"cidade/uf","cargo":"cargo decisor",'
            '"motivo":"pq precisa compliance agora"}]'
        )

        async with httpx.AsyncClient(timeout=45) as http:
            r = await http.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OR_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://global-engenharia.com",
                    "X-Title": "AION SDR",
                },
                json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.9, "max_tokens": 1500},
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                jm = re.search(r"\[[\s\S]*?\]", content)
                if jm:
                    batch = json.loads(jm.group())
                    for p in batch:
                        p["setor"] = sector
                        p["combo"] = SECTORS[sector]
                    all_prospects.extend(batch)
                    print(f"  [{sector}] +{len(batch)} prospects")

    print()
    print("=" * 70)
    print(f"PIPELINE: {len(all_prospects)} LEADS")
    print("=" * 70)

    results = []
    emails_enviados = 0
    wpp_links = []

    for i, p in enumerate(all_prospects, 1):
        empresa = p.get("empresa", "")
        cidade = p.get("cidade", "")
        cargo = p.get("cargo", "")
        setor = p.get("setor", "")
        motivo = p.get("motivo", "")
        combo = p.get("combo", "")

        print(f"\n{i}. {empresa} ({cidade})")

        email = await discover_email(empresa)
        if email:
            print(f"   Email: {email}")
        else:
            print(f"   Email: nao encontrado")
            email = ""

        prompt = (
            f"Empresa: {empresa}\nCargo: {cargo}\nSetor: {setor}\n"
            f"Problema: {motivo}\nAgentes: {combo}\n"
            f"Escreva msg WhatsApp curta natural pt-br informal"
        )
        msg_json = ds.chat(SYSTEM_PROMPT_HUMAN, prompt)
        jm = re.search(r"\{[\s\S]*\}", msg_json)
        msg_data = json.loads(jm.group()) if jm else {"whatsapp_msg": msg_json}
        msg_text = msg_data.get("whatsapp_msg", msg_json)

        print(f"   Msg: {msg_text[:90]}...")

        wpp_full = f"{msg_text} global-engenharia.com/ecosystem"
        wpp_link = f"https://wa.me/{WPP}?text={wpp_full.replace(' ', '%20')}"
        wpp_links.append({"empresa": empresa, "cargo": cargo, "link": wpp_link})

        if RESEND_KEY and email:
            try:
                async with httpx.AsyncClient(timeout=15) as http:
                    r = await http.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {RESEND_KEY}"},
                        json={
                            "from": "Cristiano Arruda <onboarding@resend.dev>",
                            "to": [email],
                            "subject": f"{empresa} — compliance automatizado",
                            "text": f"{msg_text}\n\n--\nCristiano Arruda\nGlobal Engenharia\nglobal-engenharia.com/ecosystem\nWhatsApp: (11) 99479-8464",
                        },
                    )
                    if r.status_code in (200, 201):
                        print(f"   EMAIL ENVIADO!")
                        emails_enviados += 1
                    else:
                        print(f"   Email falhou: {r.status_code}")
            except Exception as e:
                print(f"   Email erro: {e}")

        results.append({
            "empresa": empresa, "cidade": cidade, "cargo": cargo,
            "setor": setor, "combo": combo, "motivo": motivo,
            "email": email, "whatsapp_msg": msg_text, "whatsapp_link": wpp_link,
        })

    print()
    print("=" * 70)
    print(f"RESULTADO: {len(all_prospects)} leads | {emails_enviados} emails enviados | {len(wpp_links)} WhatsApp")
    print("=" * 70)
    for w in wpp_links:
        print(f"  {w['empresa']}")
        print(f"  {w['link'][:100]}...")
        print()

asyncio.run(main())
