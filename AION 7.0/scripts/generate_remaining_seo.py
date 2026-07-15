"""Gera paginas faltantes CO e AR."""
import time
from openai import OpenAI
from src.config import Settings
from src.database.supabase_client import SupabaseClient

s = Settings()
llm = OpenAI(api_key=s.openrouter_api_key, base_url="https://openrouter.ai/api/v1")
db = SupabaseClient(s)

# Pegar slugs existentes
existing = set()
for m in ['CO','AR']:
    r = db.client.table('seo_pages').select('slug').eq('market', m).execute()
    existing.update([x['slug'] for x in r.data])

PAGES = [
    # Colombia
    {"slug":"co-ley1581-fintech-pequena","title":"Cumplimiento Ley 1581 - Fintech - Pequena Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-fintech-media","title":"Cumplimiento Ley 1581 - Fintech - Mediana Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-fintech-grande","title":"Cumplimiento Ley 1581 - Fintech - Gran Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-salud-pequena","title":"Cumplimiento Ley 1581 - Salud - Pequena Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-salud-media","title":"Cumplimiento Ley 1581 - Salud - Mediana Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-salud-grande","title":"Cumplimiento Ley 1581 - Salud - Gran Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-retail-pequena","title":"Cumplimiento Ley 1581 - Retail - Pequena Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-retail-media","title":"Cumplimiento Ley 1581 - Retail - Mediana Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-retail-grande","title":"Cumplimiento Ley 1581 - Retail - Gran Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-logistica-pequena","title":"Cumplimiento Ley 1581 - Logistica - Pequena Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-logistica-media","title":"Cumplimiento Ley 1581 - Logistica - Mediana Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    {"slug":"co-ley1581-logistica-grande","title":"Cumplimiento Ley 1581 - Logistica - Gran Empresa","market":"CO","link":"https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
    # Argentina
    {"slug":"ar-sdr-automation-fintech-pequena","title":"Automatizacion SDR - Fintech - Pequena Empresa","market":"AR","link":"https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
    {"slug":"ar-sdr-automation-fintech-media","title":"Automatizacion SDR - Fintech - Mediana Empresa","market":"AR","link":"https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
    {"slug":"ar-sdr-automation-fintech-grande","title":"Automatizacion SDR - Fintech - Gran Empresa","market":"AR","link":"https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
    {"slug":"ar-sdr-automation-ecommerce-pequena","title":"Automatizacion SDR - Ecommerce - Pequena Empresa","market":"AR","link":"https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
    {"slug":"ar-sdr-automation-ecommerce-media","title":"Automatizacion SDR - Ecommerce - Mediana Empresa","market":"AR","link":"https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
    {"slug":"ar-sdr-automation-ecommerce-grande","title":"Automatizacion SDR - Ecommerce - Gran Empresa","market":"AR","link":"https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
    {"slug":"ar-sdr-automation-servicios-pequena","title":"Automatizacion SDR - Servicios - Pequena Empresa","market":"AR","link":"https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
    {"slug":"ar-sdr-automation-servicios-media","title":"Automatizacion SDR - Servicios - Mediana Empresa","market":"AR","link":"https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
    {"slug":"ar-sdr-automation-servicios-grande","title":"Automatizacion SDR - Servicios - Gran Empresa","market":"AR","link":"https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
]

for p in PAGES:
    if p['slug'] in existing:
        print(f'Pulando {p["slug"]} (ja existe)')
        continue
    idioma = "espanol"
    prompt = (
        f"Write a landing page in {idioma} for:\n"
        f"Product: Compliance/automation AI agent\n"
        f"Sector/Region: {p['title']}\n"
        f"Structure: H1, problem paragraph, 3 solution bullets, CTA.\n"
        f"Direct tone, max 300 words."
    )
    try:
        print(f'Gerando {p["slug"]}...', flush=True)
        resp = llm.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=600, timeout=30
        )
        body = resp.choices[0].message.content or ""
        db.client.table("seo_pages").upsert({
            "slug": p['slug'], "title": p['title'],
            "meta_description": p['title'],
            "body": body, "stripe_link": p['link'],
            "market": p['market'], "published": True,
        }).execute()
        print(f'  OK')
    except Exception as e:
        print(f'  ERRO: {e}')
    time.sleep(1.5)

# Verificar total
for m in ['CO','AR']:
    r = db.client.table('seo_pages').select('slug').eq('market', m).execute()
    print(f'{m}: {len(r.data)} paginas')
