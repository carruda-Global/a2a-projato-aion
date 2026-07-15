import asyncio
import json
import httpx
import logging
import os
import re
from urllib.parse import unquote
from fastapi import APIRouter, BackgroundTasks
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.email.smtp_mailer import send_via_hostinger

router = APIRouter(prefix="/api/sdr", tags=["sdr"])
logger = logging.getLogger(__name__)

# CAN-SPAM/CASL minimum for cold commercial email to the 4 target markets
# (US/UK/Canada/Australia): real sender identification + a working opt-out.
# Reply-to-unsubscribe is honored manually today (low volume, no suppression
# list yet) -- honest starting point, not full automated compliance. Revisit
# with a real suppression list before sending at any real scale.
_COMPLIANCE_FOOTER = (
    "\n\n---\nSent by Global Match Engenharia (AION Voice Receptionist). "
    "Reply UNSUBSCRIBE and we will not email you again."
)

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")


def _save_outreach_log(rows: list[dict]) -> None:
    """Persists to Supabase instead of a local file — Render's filesystem is
    wiped on every redeploy, which silently lost this data before (same bug
    class fixed for linkedin_post_history)."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return
    try:
        httpx.post(
            f"{_SUPABASE_URL}/rest/v1/sdr_outreach_log",
            json=rows,
            headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            timeout=15,
        )
        logger.info("[SDR] %d contatos registrados em sdr_outreach_log", len(rows))
    except Exception as e:
        logger.warning("[SDR] Falha ao salvar outreach log: %s", e)


EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_EMAIL_BLOCKLIST = ("example.com", "sentry.io", "wixpress.com", "godaddy.com", "schema.org", "wordpress.com", "noreply", "no-reply", "yourdomain")

# 2026-07-14: audit of sdr_outreach_log found this pipeline had been cold-
# emailing lead-data-broker sites (leadsplease.com, aeroleads.com,
# medicoleads.com -- companies that SELL contact databases, so they rank
# highly for exactly the "X contact email" queries below), huge franchise
# brands (kwuk.com = Keller Williams UK, connells.co.uk), directory sites
# (bbb.org, yellowpages.com.au), and even a UK NHS support domain -- none of
# them a real small business that would buy a $89/mo receptionist, and the
# NHS one is a real spam/reputation risk. The old Brazil-focused blocklist
# didn't cover any of this English-market junk.
_DOMAIN_BLOCKLIST = (
    "mailings.com.br", "econodata.com.br", "boaempresa.com.br", "99freelas.com.br", "auxilioanet.com.br",
    "duckduckgo.com", "google.com", "facebook.com", "linkedin.com", "instagram.com", "wikipedia.org",
    # lead-data-broker / scraping-tool sites (they sell contact lists, they are not the lead)
    "leadsplease.com", "aeroleads.com", "medicoleads.com", "zoominfo.com", "apollo.io", "hunter.io",
    "rocketreach.co", "seamless.ai", "lusha.com", "uplead.com", "clearbit.com", "spherescout.io",
    "homeserviceclub.com",
    # directories / review aggregators, not a single business's own site
    "bbb.org", "yellowpages.com", "yellowpages.com.au", "yelp.com", "angi.com", "thumbtack.com",
    "houzz.com", "manta.com", "chamberofcommerce.com",
    # large franchises/chains -- not the small independent owner-operator this pitch targets
    "kwuk.com", "kw.com", "connells.co.uk", "remax.com", "century21.com", "coldwellbanker.com",
    # institutional / government -- never a cold-sales target
    ".gov", ".nhs.net", ".ac.uk", ".edu",
)


def _looks_like_small_business_domain(domain: str) -> bool:
    """Cheap heuristic to catch blocklist misses: reject domains that are
    themselves in the lead-gen/directory business, since those pages rank
    for our search queries precisely because they sell or list contacts
    rather than being a single small business's own site."""
    domain = domain.lower()
    red_flags = ("leads", "directory", "listings", "database", "yellowpages", "chamber")
    return not any(flag in domain for flag in red_flags)

# "-leads -directory -"buy leads" -wholesale" appended to every query: these
# negative terms are the single biggest lever against data-broker/directory
# sites winning the search (see _DOMAIN_BLOCKLIST comment above for what was
# actually getting cold-emailed before this). Independent local business
# sites don't use this vocabulary about themselves; lead-broker and directory
# sites do, constantly.
_EXCLUDE_TERMS = ' -leads -"lead list" -directory -wholesale -database -"buy leads"'

SECTOR_SEARCH_QUERIES = {
    # Same verticals validated for the Voice Receptionist SEO engine
    # (src/agents/seo_topics.py SECTORS_BY_REGION) -- small businesses in the
    # 4 markets with real, Keyword-Planner-validated demand for the product.
    "dental_clinics": [q + _EXCLUDE_TERMS for q in ["independent dental clinic \"contact us\" email United States", "family dental practice owner contact email UK"]],
    "law_firms": [q + _EXCLUDE_TERMS for q in ["small law firm \"contact us\" email United States", "solicitors firm office contact email UK"]],
    "real_estate": [q + _EXCLUDE_TERMS for q in ["independent real estate agency \"contact us\" email United States", "local estate agent office contact email UK"]],
    "home_services": [q + _EXCLUDE_TERMS for q in ["local plumbing HVAC company \"contact us\" email United States", "family home services company contact email Canada"]],
    "salons_spas": [q + _EXCLUDE_TERMS for q in ["independent hair salon spa owner contact email United States", "local beauty salon contact email Australia"]],
    "medical_clinics": [q + _EXCLUDE_TERMS for q in ["independent medical clinic small practice contact email United States", "local GP clinic contact email UK"]],
    "auto_repair": [q + _EXCLUDE_TERMS for q in ["independent auto repair shop owner contact email United States", "local car mechanic garage contact email Canada"]],
    "any_market": [q + _EXCLUDE_TERMS for q in ["small business owner \"contact us\" email United States missed calls", "local family business contact email Australia phone"]],
}


async def _discover_leads(sector: str, limit: int = 10) -> list[dict]:
    """Descobre leads reais via busca web pública (DuckDuckGo, sem API key) — roda sozinho, sem intervenção manual."""
    queries = SECTOR_SEARCH_QUERIES.get(sector, SECTOR_SEARCH_QUERIES["any_market"])
    leads: list[dict] = []
    seen_emails: set[str] = set()
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for query in queries:
            if len(leads) >= limit:
                break
            try:
                r = await client.get("https://html.duckduckgo.com/html/", params={"q": query})
                wrapped = re.findall(r'href="//duckduckgo\.com/l/\?uddg=([^&"]+)', r.text)
                result_urls = [unquote(u) for u in wrapped][:8]
            except Exception as e:
                logger.warning("[SDR] Search error for '%s': %s", query, e)
                continue

            for url in result_urls:
                if len(leads) >= limit:
                    break
                if any(b in url.lower() for b in _DOMAIN_BLOCKLIST):
                    continue
                company = url.split("//")[-1].split("/")[0].replace("www.", "")
                if not _looks_like_small_business_domain(company):
                    continue
                try:
                    page = await client.get(url, timeout=8, follow_redirects=True)
                    found = set(EMAIL_RE.findall(page.text))
                    valid = [e for e in found if not any(b in e.lower() for b in _EMAIL_BLOCKLIST)]
                    if valid:
                        email = valid[0]
                        if email not in seen_emails:
                            seen_emails.add(email)
                            leads.append({"company": company, "email": email, "name": ""})
                except Exception:
                    continue
                await asyncio.sleep(1)
    logger.info("[SDR] Discovered %d real leads for sector=%s", len(leads), sector)
    return leads


async def _leads_from_identified_visitors(limit: int = 10) -> list[dict]:
    """Prioriza visitantes reais do site (identificados por IP -> empresa) em vez de
    busca fria por setor — sinal de interesse muito mais forte. Pula quem ja e cliente
    pagante (ja existe em `tenants`), e busca um email de contato pra cada empresa."""
    from src.database.supabase_client import SupabaseClient
    db = SupabaseClient(Settings())

    visitantes = db.client.table("identified_leads").select("company_name").execute().data
    empresas_vistas = {v["company_name"] for v in visitantes if v.get("company_name")}
    if not empresas_vistas:
        return []

    tenants = db.client.table("tenants").select("name,email").execute().data
    nomes_clientes = {t.get("name", "").lower() for t in tenants}

    leads: list[dict] = []
    seen_emails: set[str] = set()
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for empresa in list(empresas_vistas)[: limit * 2]:
            if len(leads) >= limit:
                break
            if empresa.lower() in nomes_clientes:
                continue
            try:
                r = await client.get("https://html.duckduckgo.com/html/", params={"q": f"{empresa} contato email"})
                wrapped = re.findall(r'href="//duckduckgo\.com/l/\?uddg=([^&"]+)', r.text)
                result_urls = [unquote(u) for u in wrapped][:5]
            except Exception as e:
                logger.warning("[SDR] Search error for visitor '%s': %s", empresa, e)
                continue

            for url in result_urls:
                if any(b in url.lower() for b in _DOMAIN_BLOCKLIST):
                    continue
                if not _looks_like_small_business_domain(url.split("//")[-1].split("/")[0]):
                    continue
                try:
                    page = await client.get(url, timeout=8, follow_redirects=True)
                    found = set(EMAIL_RE.findall(page.text))
                    valid = [e for e in found if not any(b in e.lower() for b in _EMAIL_BLOCKLIST)]
                    if valid and valid[0] not in seen_emails:
                        seen_emails.add(valid[0])
                        leads.append({"company": empresa, "email": valid[0], "name": "", "source": "site_visitor"})
                        break
                except Exception:
                    continue
            await asyncio.sleep(1)
    logger.info("[SDR] %d leads a partir de visitantes reais do site", len(leads))
    return leads

SYSTEM_PROMPT = """You are an expert B2B cold email copywriter specializing in AI tools for small businesses.
Write personalized, concise cold emails (max 150 words) that:
- Reference a specific pain point for the company's sector (missed calls, lost bookings/leads)
- Make the cost of NOT solving it concrete (a missed call is a customer calling the next business)
- Have ONE clear CTA (try the live demo or start a free trial)
- Sound human, not like a template
- Subject line under 50 characters, high open rate
Output format: JSON with keys: subject, body, follow_up_d3, follow_up_d7"""

SYSTEM_PROMPT_HUMAN = """You are Cristiano, founder of Global Engenharia, a Brazilian compliance automation company.

Write a WhatsApp/email message in BRAZILIAN PORTUGUESE that sounds like a real person, NOT a marketing robot.

RULES:
- Write like messaging a colleague on WhatsApp
- Use casual Brazilian Portuguese (vc, ta, ne, pra, etc)
- Max 3 short sentences
- No emojis, no ALL CAPS, no exclamation marks
- Mention which AI agent combo fits them best:
  * Construcao/Engenharia: NR-1 (riscos psicossociais) + Spec Analyst (analise de projetos/plantas)
  * Industria: NR-1 (obrigacao trabalhista) + Inventario Carbono (ESG)
  * Tecnologia: NR-1 + Software Engineering (code review)
  * Varejo: NR-1 + Compliance Score (score regulatorio 0-100)
  * Saude: NR-1 (riscos hospitalares) + Inventario Carbono
- End with a low-pressure CTA (ex: "se fizer sentido, bora trocar ideia")

Output format: JSON with key "whatsapp_msg" containing the full message."""

SECTORS = {
    "dental_clinics": "Missed calls mean missed appointments — patients call the next dentist on Google instead of leaving a voicemail",
    "law_firms": "A missed call from a potential client usually means they've already called the next firm on the list",
    "real_estate": "Buyers and renters move fast — a missed call means they've already booked a showing with another agent",
    "home_services": "Emergency calls (plumbing, HVAC, electrical) go to whoever answers first — a missed call is a lost job to a competitor",
    "salons_spas": "Missed calls mean lost bookings — clients rarely leave a voicemail, they just call the next salon",
    "medical_clinics": "Missed calls mean patients reschedule with a clinic that actually picks up",
    "auto_repair": "A missed call often means the car goes to the shop down the street instead",
    "any_market": "Every missed call is a customer calling the next business on the list instead",
}


@router.post("/generate-email")
async def generate_email(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    company = data.get("company", "")
    sector = data.get("sector", "any_market")
    contact_name = data.get("contact_name", "")
    pain_point = SECTORS.get(sector, SECTORS["any_market"])
    prompt = (
        f"Write a cold email for:\n"
        f"Company: {company}\n"
        f"Contact: {contact_name}\n"
        f"Sector: {sector}\n"
        f"Pain point: {pain_point}\n"
        f"Our product: AION Voice Receptionist — AI phone receptionist that answers every call 24/7, "
        f"no per-call fees, from $89/mo\n"
        f"Free trial: https://global-engenharia.com/ecosystem\n"
        f"Output as JSON: subject, body, follow_up_d3, follow_up_d7"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"email": response, "sector_pain_point": pain_point}


@router.get("/human")
async def sdr_human_status():
    return {
        "modo_humano": True,
        "descricao": "Mensagens em portugues brasileiro casual, estilo WhatsApp",
        "exemplo": "Fala João, sou o Cristiano da Global Engenharia. Vi que a Construtora X cresceu pra 8 obras e imagino que o PGR da NR-1 deva estar dando trabalho. Se fizer sentido, bora trocar ideia?",
        "setores": list(SECTORS.keys()),
        "whatsapp_number": os.getenv("WPP_NUMBER", "5511994798464"),
    }


@router.post("/generate-human")
async def generate_human(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    empresa = data.get("company", data.get("empresa", ""))
    cargo = data.get("cargo", data.get("cargo_decisor", ""))
    setor = data.get("sector", data.get("setor", "construcao"))
    motivo = data.get("motivo", "")
    canal = data.get("canal", "whatsapp")

    prompt = f"""Empresa: {empresa}
Cargo: {cargo}
Setor: {setor}
Problema: {motivo}
Canal: {canal}
Nosso produto: 106 agentes de IA pra compliance (NR-1, LGPD, EU AI Act)
Site: global-engenharia.com/ecosystem
Escreva uma mensagem curta e natural."""

    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT_HUMAN, prompt)

    import re as _re
    jm = _re.search(r"\{[\s\S]*\}", response)
    msg_data = json.loads(jm.group()) if jm else {"body": response}

    wpp_number = os.getenv("WPP_NUMBER", "5511994798464")
    msg_text = msg_data.get("whatsapp_msg", msg_data.get("body", response))
    wpp_link = f"https://wa.me/{wpp_number}?text={msg_text.replace(' ', '%20')}"

    return {
        "empresa": empresa,
        "cargo": cargo,
        "canal": canal,
        "mensagem": msg_text,
        "whatsapp_link": wpp_link,
    }


@router.post("/send-campaign")
async def send_campaign(data: dict, background_tasks: BackgroundTasks):
    """Send outbound email campaign via Resend. Se nenhum lead for passado, descobre
    automaticamente via busca web pública — é o que faz o job 24/7 funcionar sozinho."""
    leads = data.get("leads", [])
    sector = data.get("sector", "any_market")
    limit = data.get("limit", 10)
    background_tasks.add_task(_process_campaign, leads, sector, limit)
    return {"status": "campaign_started", "leads_provided": len(leads), "auto_discover": len(leads) == 0}


async def _process_campaign(leads: list, sector: str, limit: int = 10):
    if not leads:
        try:
            leads = await _leads_from_identified_visitors(limit)
        except Exception as e:
            logger.warning("[SDR] Falha ao buscar visitantes identificados: %s", e)
        if not leads:
            leads = await _discover_leads(sector, limit)
        if not leads:
            logger.warning("[SDR] Nenhum lead descoberto para sector=%s — pulando ciclo", sector)
            return
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    pain_point = SECTORS.get(sector, SECTORS["any_market"])

    whatsapp_number = os.getenv("WPP_NUMBER", "5511994798464")
    outreach_log: list[dict] = []

    for lead in leads:
        is_site_visitor = lead.get("source") == "site_visitor"
        try:
            if is_site_visitor:
                # Este lead visitou de verdade o funil da Voice Receptionist —
                # o pitch tem que ser sobre o que ele realmente viu no site,
                # nao sobre o catalogo antigo de compliance.
                subject = f"Ligacoes perdidas na {lead.get('company', 'sua empresa')}?"
                body = (
                    f"Oi! Vi que alguem da {lead.get('company', 'sua empresa')} deu uma olhada "
                    f"no nosso AI Voice Receptionist. E uma recepcionista de IA que atende o "
                    f"telefone 24/7, nunca perde uma ligacao e ja manda mensagem de volta pra "
                    f"quem ligou e nao foi atendido. A partir de $89/mes, sem taxa por chamada.\n\n"
                    f"Da uma olhada: https://global-engenharia.com/ecosystem\n\n"
                    f"Qualquer duvida, e so responder este email."
                )
                email_json = json.dumps({"subject": subject, "body": body})
                wpp_msg = (
                    f"Oi! Vi que voce deu uma olhada no nosso AI Voice Receptionist. "
                    f"Atende seu telefone 24/7 e nunca perde uma ligacao, a partir de $89/mes. "
                    f"global-engenharia.com/ecosystem"
                )
            else:
                prompt = (
                    f"Company: {lead.get('company', '')}\n"
                    f"Contact: {lead.get('name', '')}\n"
                    f"Sector: {sector}\n"
                    f"Pain: {pain_point}\n"
                    f"Product: AION Voice Receptionist — AI phone receptionist, answers every call 24/7, "
                    f"no per-call fees, from $89/mo\n"
                    f"Trial: https://global-engenharia.com/ecosystem\n"
                    f"Output JSON: subject, body"
                )
                email_json = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
                parsed = json.loads(re.search(r"\{[\s\S]*\}", email_json).group())
                subject = parsed.get("subject", f"Missing calls at {lead.get('company', 'your business')}?")
                body = parsed.get("body", email_json)
                wpp_msg = (
                    f"Hi! I noticed {lead.get('company','your business')} and thought our AI Voice "
                    f"Receptionist could help — answers every call 24/7, no per-call fees, from $89/mo. "
                    f"https://global-engenharia.com/ecosystem"
                )

            email_sent = False
            if lead.get("email"):
                try:
                    full_body = (body + _COMPLIANCE_FOOTER).replace("\n", "<br>")
                    await asyncio.to_thread(send_via_hostinger, lead["email"], subject, full_body)
                    email_sent = True
                except Exception as e:
                    logger.warning("[SDR] Email send failed for %s: %s", lead.get("email"), e)

            wpp_link = f"https://wa.me/{whatsapp_number}?text={wpp_msg.replace(' ', '%20')}"
            outreach_log.append({
                "company": lead.get("company", ""), "email": lead.get("email", ""),
                "source": lead.get("source", "cold_search"), "sector": sector,
                "whatsapp_link": wpp_link, "email_sent": email_sent,
            })

            await asyncio.sleep(2)
        except Exception as e:
            logger.error("SDR send error for %s: %s", lead.get("email"), e)

    if outreach_log:
        _save_outreach_log(outreach_log)


@router.get("/sectors")
async def list_sectors():
    return {"sectors": SECTORS}
