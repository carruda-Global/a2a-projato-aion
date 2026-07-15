import json, os, sys, asyncio, re
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

import httpx
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents.outbound_sdr_agent import SYSTEM_PROMPT_HUMAN

WPP = os.getenv("WPP_NUMBER", "5511994798464")
OR_KEY = os.getenv("OPENROUTER_API_KEY", "")
RESEND_KEY = os.getenv("RESEND_API_KEY", "")
DATA_DIR = Path(__file__).parent.parent / "data" / "sdr"
DATA_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
ds = DeepSeekClient(settings)

SETORES = [
    {"nome": "construcao", "desc": "construtoras e incorporadoras Brasil 50-500 funcionarios", "combo": "NR-1 (riscos psicossociais) + Spec Analyst (BIM e projetos)"},
    {"nome": "industria", "desc": "industrias com obrigacao NR-1 e carbono", "combo": "NR-1 (obrigacao trabalhista) + Inventario Carbono (ESG IFRS S1 S2)"},
    {"nome": "tecnologia", "desc": "empresas de tecnologia precisando LGPD", "combo": "LGPD (privacidade) + Software Engineering (code review)"},
    {"nome": "varejo", "desc": "grandes varejistas com LGPD", "combo": "LGPD (dados clientes) + Compliance Score (score 0-100)"},
    {"nome": "saude", "desc": "hospitais e operadoras de saude LGPD", "combo": "NR-1 (riscos hospitalares) + LGPD (dados sensiveis pacientes)"},
    {"nome": "energia", "desc": "empresas de energia e saneamento ESG", "combo": "Inventario Carbono (Escopo 1+2+3) + ESG IFRS (relatorio)"},
]

async def generate_leads(setor: dict, count: int = 3) -> list[dict]:
    prompt = (
        f"Liste {count} empresas REAIS brasileiras do setor: {setor['desc']}. "
        "Retorne APENAS JSON array: "
        '[{"empresa":"nome real","cidade":"cidade/uf","cargo":"cargo decisor",'
        '"motivo":"pq precisa compliance agora"}]'
    )
    async with httpx.AsyncClient(timeout=45) as http:
        r = await http.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://global-engenharia.com"},
            json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.9, "max_tokens": 1500},
        )
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            jm = re.search(r"\[[\s\S]*?\]", content)
            if jm:
                batch = json.loads(jm.group())
                for p in batch:
                    p["setor"] = setor["nome"]
                    p["combo"] = setor["combo"]
                return batch
    return []

async def discover_email(company: str) -> str:
    try:
        q = f"{company} contato email oficial"
        async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "Mozilla/5.0"}) as c:
            r = await c.get("https://html.duckduckgo.com/html/", params={"q": q})
            urls = re.findall(r"href=\"//duckduckgo\.com/l/\?uddg=([^&\"]+)", r.text)
            for url in urls[:3]:
                try:
                    page = await c.get(url, timeout=5, follow_redirects=True)
                    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", page.text)
                    valid = [e for e in emails if not any(b in e.lower() for b in ("example","noreply","no-reply","sentry","wixpress","linkedin","facebook","google","instagram","wikipedia"))]
                    if valid:
                        return valid[0]
                except:
                    pass
    except:
        pass
    try:
        prompt = f"Email de contato publico da empresa {company} no Brasil (ex: contato@dominio.com.br). Retorne APENAS 1 email."
        async with httpx.AsyncClient(timeout=25) as http:
            r = await http.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://global-engenharia.com"},
                json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 50},
            )
            if r.status_code == 200:
                email = r.json()["choices"][0]["message"]["content"].strip()
                if "@" in email and "." in email and len(email) < 60:
                    return email
    except:
        pass
    return ""

async def generate_whatsapp(empresa: str, cargo: str, setor: str, combo: str, motivo: str) -> str:
    prompt = (
        f"Empresa: {empresa}\nCargo: {cargo}\nSetor: {setor}\n"
        f"Problema: {motivo}\nAgentes: {combo}\n"
        f"Escreva msg WhatsApp curta natural pt-br informal"
    )
    msg_json = ds.chat(SYSTEM_PROMPT_HUMAN, prompt)
    jm = re.search(r"\{[\s\S]*\}", msg_json)
    msg_data = json.loads(jm.group()) if jm else {"whatsapp_msg": msg_json}
    return msg_data.get("whatsapp_msg", msg_json)

async def main():
    campaign_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=" * 70)
    print(f"PIPELINE AUTOMATICO — Campanha {campaign_id}")
    print("=" * 70)

    all_results = []
    total_leads = 0
    total_emails = 0
    total_wpp = 0

    for setor in SETORES:
        print(f"\n[{setor['nome'].upper()}] {setor['combo']}")
        leads = await generate_leads(setor, 3)
        print(f"  +{len(leads)} leads gerados")

        for p in leads:
            empresa = p.get("empresa", "")
            cargo = p.get("cargo", "")
            motivo = p.get("motivo", "")

            email = await discover_email(empresa)
            if email:
                total_emails += 1
                print(f"  {empresa}: {email}")
            else:
                print(f"  {empresa}: sem email")

            msg = await generate_whatsapp(empresa, cargo, setor["nome"], setor["combo"], motivo)
            wpp_full = f"{msg} global-engenharia.com/ecosystem"
            wpp_link = f"https://wa.me/{WPP}?text={wpp_full.replace(' ', '%20')}"
            total_wpp += 1

            all_results.append({
                "empresa": empresa,
                "cidade": p.get("cidade", ""),
                "cargo": cargo,
                "setor": setor["nome"],
                "combo": setor["combo"],
                "motivo": motivo,
                "email": email,
                "whatsapp_msg": msg,
                "whatsapp_link": wpp_link,
                "campanha": campaign_id,
            })

            total_leads += 1

    # Salvar campanha
    camp_file = DATA_DIR / f"campanha_{campaign_id}.json"
    camp_file.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))

    # Atualizar fila de emails pendentes
    queue_file = DATA_DIR / "email_queue.json"
    existing = []
    if queue_file.exists():
        try:
            existing = json.loads(queue_file.read_text())
        except:
            pass
    for r in all_results:
        if r["email"]:
            existing.append({
                "empresa": r["empresa"],
                "email": r["email"],
                "cargo": r["cargo"],
                "whatsapp": r["whatsapp_link"][:80],
                "campanha": campaign_id,
            })
    queue_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False))

    # Atualizar links WhatsApp
    wpp_file = DATA_DIR / "whatsapp_links.json"
    wpp_existing = []
    if wpp_file.exists():
        try:
            wpp_existing = json.loads(wpp_file.read_text())
        except:
            pass
    wpp_existing.extend([{"empresa": r["empresa"], "cargo": r["cargo"], "link": r["whatsapp_link"]} for r in all_results])
    wpp_file.write_text(json.dumps(wpp_existing, indent=2, ensure_ascii=False))

    print()
    print("=" * 70)
    print(f"RESULTADO: {total_leads} leads | {total_emails} emails | {total_wpp} WhatsApp")
    print("=" * 70)
    print(f"Campanha: {camp_file}")
    print(f"Fila emails: {queue_file} ({len(existing)} pendentes)")
    print(f"Links WhatsApp: {wpp_file} ({len(wpp_existing)} links)")
    print()
    for r in all_results:
        print(f"  {r['empresa']} — {r['cargo']}")
        print(f"  WhatsApp: {r['whatsapp_link'][:110]}...")
        print()

asyncio.run(main())
