import json, os, sys, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

SYSTEM_PROMPT = """You are an expert B2B cold email writer for compliance software.
Write short, personalized cold emails (max 120 words). Rules:
- Reference the company name and their specific compliance need
- Mention the urgency (NR-1 fines R$10k/employee, LGPD fine 2% revenue)  
- One clear CTA: "15-min demo" or "free NR-1 diagnostic"
- Sound human, not robot
- Subject line under 50 chars
Output ONLY valid JSON: {"subject":"...","body":"..."}"""

async def main():
    prospects_file = Path(__file__).parent.parent / "data" / "sdr_prospects.json"
    prospects = json.loads(prospects_file.read_text())

    settings = Settings()
    deepseek = DeepSeekClient(settings)

    emails = []

    for i, p in enumerate(prospects, 1):
        empresa = p.get("empresa", "")
        cargo = p.get("cargo", "") or p.get("cargo_decisor", "")
        motivo = p.get("motivo", "")
        setor = p.get("setor", "")

        prompt = f"""Company: {empresa}
Contact role: {cargo}
Sector: {setor}
Pain: {motivo}
Product: AION - 106 AI agents for compliance (NR-1, LGPD, EU AI Act)
Website: global-engenharia.com/ecosystem
Output JSON with subject and body."""

        try:
            result = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)

            # Try to parse JSON from response
            import re
            jm = re.search(r"\{[\s\S]*\}", result)
            if jm:
                email_data = json.loads(jm.group())
            else:
                email_data = json.loads(result)

            email_data["empresa"] = empresa
            email_data["cargo"] = cargo
            emails.append(email_data)

            subject = email_data.get("subject", "")[:60]
            body = email_data.get("body", "")[:150]
            print(f"{i}. {empresa} ({cargo})")
            print(f"   Subject: {subject}")
            print(f"   Body: {body}...")
            print()

        except Exception as e:
            print(f"{i}. {empresa}: ERRO - {e}")

        await asyncio.sleep(0.5)

    out = Path(__file__).parent.parent / "data" / "sdr_emails.json"
    out.write_text(json.dumps(emails, indent=2, ensure_ascii=False))
    print(f"\n{len(emails)} emails salvos em: {out}")

    # Send via Resend if key exists
    resend_key = os.getenv("RESEND_API_KEY", "")
    if resend_key:
        print(f"\nRESEND_API_KEY configurada. Enviar {len(emails)} emails? (NAO enviando agora, apenas gerando)")
        print("Para enviar, rode: curl -X POST http://localhost:8000/api/sdr/send-campaign")
    else:
        print("\n[AVISO] RESEND_API_KEY nao configurada - emails apenas gerados, nao enviados")

asyncio.run(main())
