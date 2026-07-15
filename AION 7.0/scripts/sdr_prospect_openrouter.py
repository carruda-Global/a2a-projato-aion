import json, re, os, sys, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

WPP_NUMBER = "5511994798464"

async def prospect():
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    if not openrouter_key:
        print("[ERRO] OPENROUTER_API_KEY nao configurada")
        return

    lotes = [
        "construtoras SP",
        "incorporadoras RJ",
        "obras pesadas MG", 
        "engenharia civil PR",
        "escritorios engenharia Brasil",
    ]

    all_prospects = []

    async with httpx.AsyncClient(timeout=60) as http:
        for lote_idx, lote in enumerate(lotes, 1):
            prompt = (
                f"Liste 4 empresas de {lote} que precisam NR-1/LGPD.\n"
                "Retorne APENAS JSON array: [{\"empresa\":\"...\",\"cidade\":\"...\","
                "\"cargo\":\"...\",\"motivo\":\"...\",\"msg\":\"...\"}]\n"
                "msg = whatsapp curto, max 15 palavras. Sem explicacoes."
            )

            r = await http.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://global-engenharia.com",
                    "X-Title": "AION SDR",
                },
                json={
                    "model": "moonshotai/kimi-k2",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.9,
                    "max_tokens": 2048,
                },
            )

            if r.status_code != 200:
                print(f"  Lote {lote_idx}: HTTP {r.status_code}")
                continue

            content = r.json()["choices"][0]["message"]["content"]
            jm = re.search(r"\[[\s\S]*?\]", content)
            if jm:
                batch = json.loads(jm.group())
                all_prospects.extend(batch)
                print(f"  Lote {lote_idx}: +{len(batch)}")
            else:
                print(f"  Lote {lote_idx}: JSON nao encontrado")

    print()
    print("=" * 70)
    print(f"PROSPECCAO — {len(all_prospects)} EMPRESAS")
    print("=" * 70)

    links = []
    for i, p in enumerate(all_prospects, 1):
        empresa = p.get("empresa", "") or p.get("empresa", "")
        cidade = p.get("cidade", "") or p.get("cidade", "")
        cargo = p.get("cargo", "") or p.get("cargo_decisor", "")
        motivo = p.get("motivo", "")
        msg = p.get("msg", "") or p.get("whatsapp_msg", "")

        print(f"\n{i}. {empresa} ({cidade})")
        print(f"   Cargo: {cargo}")
        print(f"   Motivo: {motivo}")
        print(f"   WhatsApp: {msg}")

        full = f"Olá! Cristiano Arruda da Global Engenharia. {msg} global-engenharia.com/ecosystem"
        full_encoded = full.replace(" ", "%20")
        link = f"https://wa.me/{WPP_NUMBER}?text={full_encoded}"
        links.append({"empresa": empresa, "cargo": cargo, "cidade": cidade, "link": link})

    print()
    print("=" * 70)
    print("LINKS WHATSAPP PRONTOS")
    print("=" * 70)
    for l in links:
        print(f"\n{l['empresa']} — {l['cargo']} ({l['cidade']})")
        print(f"  {l['link'][:130]}")

    out = Path(__file__).parent.parent / "data" / "sdr_prospects.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(all_prospects, indent=2, ensure_ascii=False))
    print(f"\nSalvo: {out}")

import httpx
asyncio.run(prospect())
