import json, os, sys, asyncio, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()
import httpx
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents.outbound_sdr_agent import SYSTEM_PROMPT_HUMAN

OR_KEY = os.getenv("OPENROUTER_API_KEY", "")
DATA_DIR = Path(__file__).parent.parent / "data" / "sdr"
DATA_DIR.mkdir(parents=True, exist_ok=True)
QUEUE_FILE = DATA_DIR / "whatsapp_queue.json"

settings = Settings()
ds = DeepSeekClient(settings)

SETORES = [
    {"nome": "energia", "desc": "empresas de energia, saneamento e utilities Brasil", "combo": "Inventario Carbono + ESG IFRS"},
    {"nome": "saude", "desc": "hospitais, clinicas e operadoras de saude Brasil", "combo": "NR-1 (riscos hospitalares) + Inventario Carbono"},
    {"nome": "agro", "desc": "agronegocio e food processing Brasil", "combo": "NR-1 (seguranca trabalho) + Inventario Carbono (ESG)"},
    {"nome": "logistica", "desc": "transportadoras e operadores logisticos Brasil", "combo": "NR-1 (motoristas/armazem) + Inventario Carbono (frota)"},
]

async def find_phone(empresa: str) -> str:
    try:
        q = f"{empresa} telefone contato whatsapp"
        async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "Mozilla/5.0"}) as c:
            r = await c.get("https://html.duckduckgo.com/html/", params={"q": q})
            urls = re.findall(r'href="//duckduckgo\.com/l/\?uddg=([^&"]+)', r.text)
            for url in urls[:2]:
                try:
                    page = await c.get(url, timeout=5, follow_redirects=True)
                    phones = re.findall(r'(?:\(?\d{2}\)?\s?)?(?:\d{4,5}[-.\s]?\d{4})', page.text)
                    phones = [p for p in phones if len(re.sub(r'\D','',p)) >= 10]
                    if phones:
                        num = re.sub(r'\D', '', phones[0])
                        if len(num) == 10: num = f"55{num}"
                        elif len(num) == 11: num = f"55{num}"
                        return num
                except: pass
    except: pass
    try:
        prompt = f"Telefone/whatsapp comercial de {empresa}? Retorne APENAS numero +55. Sem texto."
        async with httpx.AsyncClient(timeout=20) as http:
            r = await http.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://global-engenharia.com"},
                json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 30},
            )
            if r.status_code == 200:
                num = re.sub(r'\D', '', r.json()["choices"][0]["message"]["content"])
                if len(num) >= 10:
                    if len(num) <= 11: num = f"55{num}"
                    return num
    except: pass
    return ""

async def main():
    queue = json.loads(QUEUE_FILE.read_text()) if QUEUE_FILE.exists() else []

    for setor in SETORES:
        prompt = f'Liste 3 empresas REAIS: {setor["desc"]}. JSON: [{{"empresa":"nome","cargo":"cargo","motivo":"pq precisa {setor["combo"]}"}}]. APENAS JSON.'
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
                        phone = await find_phone(p["empresa"])
                        p["numero"] = phone
                        
                        msg = ds.chat(SYSTEM_PROMPT_HUMAN,
                            f"Empresa: {p['empresa']}\nCargo: {p['cargo']}\nAgentes: {setor['combo']}\nMsg curta natural pt-br")
                        jm2 = re.search(r"\{[\s\S]*\}", msg)
                        p["msg"] = json.loads(jm2.group()).get("whatsapp_msg", msg) if jm2 else msg
                        queue.append(p)
                        print(f"  {p['empresa']} | Tel: {phone or 'nao'} | +1 (total:{len(queue)})")

    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False))
    with_phone = sum(1 for q in queue if q.get("numero"))
    print(f"\nFila: {len(queue)} prospects ({with_phone} com telefone)")
    print(f"Pronto! Rode: cd whatsapp-bot && node send.js")

asyncio.run(main())
