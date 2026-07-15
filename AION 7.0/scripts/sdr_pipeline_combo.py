import json, os, sys, asyncio, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

import httpx
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents.outbound_sdr_agent import SYSTEM_PROMPT_HUMAN

AGENT_COMBOS = {
    "construcao": "NR-1 (riscos psicossociais obrigatorio) + Spec Analyst (analise de projetos e plantas)",
    "industria": "NR-1 (obrigacao trabalhista) + Inventario Carbono (ESG/IFRS S1 S2)",
    "tecnologia": "LGPD (privacidade de dados) + Software Engineering (code review automatico)",
    "varejo": "LGPD (dados de clientes) + Compliance Score (score regulatorio 0-100)",
    "saude": "NR-1 (riscos hospitalares) + LGPD (dados sensiveis de pacientes)",
}

SECTORS_DESC = {
    "construcao": "construtoras e incorporadoras 50-500 funcionarios",
    "industria": "industrias com obrigacao NR-1 e inventario de carbono",
    "tecnologia": "empresas de tecnologia precisando LGPD e SOC2",
    "varejo": "grandes varejistas com dados de clientes (LGPD)",
    "saude": "hospitais e clinicas com dados sensiveis (LGPD)",
}

async def main():
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    wpp_number = os.getenv("WPP_NUMBER", "5511994798464")
    settings = Settings()
    deepseek = DeepSeekClient(settings)

    all_prospects = []

    for sector, desc in SECTORS_DESC.items():
        prompt = (
            f"Liste 4 {desc} no Brasil. Retorne APENAS JSON array: "
            '[{"empresa":"nome real","cidade":"cidade/estado","cargo":"cargo decisor",'
            '"motivo":"pq precisa compliance agora","linkedin_url":"url linkedin da empresa"}] '
            'Sem explicacoes. APENAS JSON.'
        )

        async with httpx.AsyncClient(timeout=45) as http:
            r = await http.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://global-engenharia.com",
                    "X-Title": "AION SDR",
                },
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.9,
                    "max_tokens": 2048,
                },
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                jm = re.search(r"\[[\s\S]*?\]", content)
                if jm:
                    batch = json.loads(jm.group())
                    for p in batch:
                        p["setor"] = sector
                    all_prospects.extend(batch)
                    print(f"  {sector}: +{len(batch)}")

    print()
    print("=" * 70)
    print(f"PROSPECCAO: {len(all_prospects)} LEADS")
    print("=" * 70)

    pipeline = []
    for i, p in enumerate(all_prospects, 1):
        empresa = p.get("empresa", "")
        cidade = p.get("cidade", "")
        cargo = p.get("cargo", "")
        setor = p.get("setor", "")
        motivo = p.get("motivo", "")
        linkedin = p.get("linkedin_url", "")
        combo = AGENT_COMBOS.get(setor, "NR-1 + LGPD")

        # Gerar msg humanizada com combo de agentes
        prompt = (
            f"Empresa: {empresa}\nCargo: {cargo}\nSetor: {setor}\n"
            f"Problema: {motivo}\n"
            f"Agentes que oferecemos: {combo}\n"
            f"Escreva msg WhatsApp curta e natural em portugues brasileiro informal"
        )
        msg_json = deepseek.chat(SYSTEM_PROMPT_HUMAN, prompt)

        jm = re.search(r"\{[\s\S]*\}", msg_json)
        msg_data = json.loads(jm.group()) if jm else {"whatsapp_msg": msg_json}
        msg_text = msg_data.get("whatsapp_msg", msg_json)

        wpp_msg = f"{msg_text} global-engenharia.com/ecosystem"
        wpp_link = f"https://wa.me/{wpp_number}?text={wpp_msg.replace(' ', '%20')}"

        pipeline.append({
            "empresa": empresa,
            "cidade": cidade,
            "cargo": cargo,
            "setor": setor,
            "combo_agentes": combo,
            "motivo": motivo,
            "linkedin": linkedin,
            "whatsapp_msg": msg_text,
            "whatsapp_link": wpp_link,
        })

        print(f"\n{i}. {empresa} ({cidade})")
        print(f"   Cargo: {cargo}")
        print(f"   Combo: {combo}")
        print(f"   Msg: {msg_text[:120]}...")
        print(f"   Wa.me: {wpp_link[:90]}...")

    out = Path(__file__).parent.parent / "data" / "sdr_pipeline_combo.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pipeline, indent=2, ensure_ascii=False))

    print()
    print(f"PIPELINE SALVO: {out}")
    print(f"Total: {len(pipeline)} leads com WhatsApp links e combo de agentes")
    print(f"NR-1 + Engenharia: {sum(1 for p in pipeline if 'construcao' in p.get('setor',''))}")
    print(f"NR-1 + Industria: {sum(1 for p in pipeline if 'industria' in p.get('setor',''))}")
    print(f"LGPD + Tech: {sum(1 for p in pipeline if 'tecnologia' in p.get('setor',''))}")
    print(f"LGPD + Varejo: {sum(1 for p in pipeline if 'varejo' in p.get('setor',''))}")
    print(f"NR-1 + Saude: {sum(1 for p in pipeline if 'saude' in p.get('setor',''))}")

asyncio.run(main())
