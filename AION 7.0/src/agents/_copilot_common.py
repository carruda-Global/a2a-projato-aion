"""Lógica compartilhada dos Global Copilots (upload -> extração -> LLM -> PDF).
Evita duplicar isso em cada um dos 5 agentes (SOC2, ISO27001, Contract Risk,
Vendor Risk, EU AI Act).
"""
import io
import json
import re
from datetime import date
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from src.monetization.subscription_activator import get_subscription


def tem_licenca_premium(customer_email: str) -> bool:
    """Server-side premium check for the Global Copilots. Never trust a
    client-supplied premium flag — always look up the real subscription
    activated by the Stripe webhook (stripe_webhook.py keys activations by
    customer email for direct-purchase checkout links)."""
    if not customer_email:
        return False
    sub = get_subscription("stripe", customer_email.strip().lower())
    return bool(sub and sub.get("status") == "active")


def extrair_texto(conteudo: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(conteudo))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return conteudo.decode("utf-8", errors="ignore")


def parsear_json_llm(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group()) if match else {"classification": "unclear", "gaps": [raw[:500]]}


def gerar_pdf_relatorio(titulo: str, empresa: str, analise: dict, checklist_key: str = "obligations") -> io.BytesIO:
    """Gerador genérico de relatório PDF — funciona para qualquer Copilot que
    retorne JSON no formato: classification, classification_reasoning,
    risk_score, <checklist_key> (lista de {requirement/control, status}),
    gaps (lista de string), action_plan (lista de {priority, action, deadline_days})."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("TituloCustom", parent=styles["Title"], textColor=HexColor("#1a1a2e"))
    story = [
        Paragraph(titulo, titulo_style),
        Spacer(1, 0.3 * cm),
        Paragraph(f"Company: {empresa}", styles["Normal"]),
        Paragraph(f"Report date: {date.today().strftime('%Y-%m-%d')}", styles["Normal"]),
        Spacer(1, 0.5 * cm),
    ]

    classificacao = analise.get("classification") or analise.get("risk_classification", "N/A")
    story.append(Paragraph(f"<b>Classification: {classificacao}</b>", styles["Heading2"]))
    story.append(Paragraph(analise.get("classification_reasoning", ""), styles["Normal"]))
    if analise.get("applicable_deadline"):
        story.append(Paragraph(f"<b>Applicable deadline:</b> {analise['applicable_deadline']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Risk score:</b> {analise.get('risk_score', 'N/A')}/100", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    checklist = analise.get(checklist_key, [])
    if checklist:
        story.append(Paragraph("Checklist", styles["Heading2"]))
        rows = [["Item", "Status"]]
        for item in checklist:
            label = item.get("requirement") or item.get("control") or item.get("item", "")
            rows.append([label, item.get("status", "")])
        table = Table(rows, colWidths=[12 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5 * cm))

    if analise.get("gaps"):
        story.append(Paragraph("Gaps Identified", styles["Heading2"]))
        for g in analise["gaps"]:
            story.append(Paragraph(f"• {g}", styles["Normal"]))
        story.append(Spacer(1, 0.5 * cm))

    if analise.get("action_plan"):
        story.append(Paragraph("Action Plan", styles["Heading2"]))
        for a in sorted(analise["action_plan"], key=lambda x: x.get("priority", 99)):
            story.append(Paragraph(f"{a.get('priority', '')}. {a.get('action', '')} (within {a.get('deadline_days', '')} days)", styles["Normal"]))

    doc.build(story)
    buf.seek(0)
    return buf
