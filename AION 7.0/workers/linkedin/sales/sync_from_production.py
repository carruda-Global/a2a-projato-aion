"""
Puxa trafego/leads reais da producao (Supabase) para o pipeline de SDR local.

Fontes:
  - identified_leads: visitas identificadas por reverse-IP (empresa) via /api/visitor-id/track
  - chat_logs (message=LEAD_CAPTURE): leads que preencheram o modal de checkout via /checkout/lead

Roda 100% local. Nao precisa de nenhum servico novo no Render.
Uso: python workers/linkedin/sales/sync_from_production.py
"""
import re
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from sales.database import SessionLocal, init_db
from sales import models, pipeline
from src.database.supabase_client import SupabaseClient
from src.config import Settings

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

LEAD_CAPTURE_RE = re.compile(
    r"email=(?P<email>\S*)\s*name=(?P<name>.*?)\s*plan=(?P<plan>\S*)\s*"
    r"source=(?P<source>\S*)\s*linkedin_id=(?P<linkedin_id>\S*)\s*"
    r"utm_source=(?P<utm_source>\S*)\s*utm_medium=(?P<utm_medium>\S*)\s*utm_campaign=(?P<utm_campaign>\S*)"
)
LEAD_CAPTURE_RE_LEGACY = re.compile(r"email=(?P<email>\S*)\s*plan=(?P<plan>\S*)")


def _map_source(utm_source: str, raw_source: str) -> str:
    # monitor.py's pipeline_summary/funil_conversao filter on the literal
    # strings "linkedin" / "site_landing_page", not the LeadSource enum
    # values ("website") -- match those so counts land in the right bucket.
    if utm_source == "linkedin" or "linkedin" in (raw_source or ""):
        return "linkedin"
    return "site_landing_page"


def sync_identified_leads(db, sb: SupabaseClient) -> int:
    rows = sb.client.table("identified_leads").select("*").execute().data or []
    created = 0
    for row in rows:
        company = row.get("company_name")
        ip = row.get("ip")
        if not company:
            continue
        existing = (
            db.query(models.Lead)
            .filter(models.Lead.company == company, models.Lead.source == "site_landing_page")
            .first()
        )
        if existing:
            continue
        pipeline.create_lead(
            db=db,
            name=company,
            company=company,
            location=row.get("country"),
            summary=f"Identificado por IP visitando {row.get('page_visited', '')} (ip={ip})",
            source="site_landing_page",
        )
        created += 1
    return created


def sync_lead_captures(db, sb: SupabaseClient) -> int:
    rows = (
        sb.client.table("chat_logs")
        .select("*")
        .eq("message", "LEAD_CAPTURE")
        .execute()
        .data
        or []
    )
    created = 0
    for row in rows:
        text = row.get("response", "")
        m = LEAD_CAPTURE_RE.search(text)
        if m:
            data = m.groupdict()
        else:
            legacy = LEAD_CAPTURE_RE_LEGACY.search(text)
            if not legacy:
                continue
            data = {**legacy.groupdict(), "name": "", "source": "", "linkedin_id": "",
                    "utm_source": "", "utm_medium": "", "utm_campaign": ""}

        email = data.get("email", "").strip()
        if not email:
            continue

        existing = db.query(models.Lead).filter(models.Lead.email == email).first()
        if existing:
            continue

        source = _map_source(data.get("utm_source", ""), data.get("source", ""))
        plan = data.get("plan", "").strip()
        utm_bits = " ".join(
            f"{k}={data[k]}" for k in ("utm_source", "utm_medium", "utm_campaign") if data.get(k)
        )
        lead = pipeline.create_lead(
            db=db,
            name=data.get("name", "").strip() or email.split("@")[0],
            email=email,
            linkedin_url=None,
            linkedin_id=data.get("linkedin_id") or None,
            source=source,
            summary=f"Capturado no checkout, interesse: {plan or 'nao informado'}. {utm_bits}".strip(),
        )
        pipeline.add_activity(
            db=db,
            lead_id=lead.id,
            type="form_start",
            subject="Preencheu modal de checkout",
            description=f"page={row.get('page', '')} plan={plan} {utm_bits}",
        )
        created += 1
    return created


def main():
    init_db()
    db = SessionLocal()
    sb = SupabaseClient(Settings())
    try:
        n1 = sync_identified_leads(db, sb)
        n2 = sync_lead_captures(db, sb)
        logger.info(f"Sync concluido: {n1} leads de visita (IP), {n2} leads de checkout.")

        from sales.monitor import SalesMonitor
        monitor = SalesMonitor()
        report = monitor.relatorio_completo()
        monitor.close()

        logger.info("\n=== FUNIL DE VENDAS (dados reais, puxados agora) ===")
        logger.info(report["resumo"])
        logger.info("\n=== ATIVIDADES RECENTES ===")
        for a in report["atividades_recentes"]:
            logger.info(a)
    finally:
        db.close()


if __name__ == "__main__":
    main()
