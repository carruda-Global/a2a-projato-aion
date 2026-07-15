"""Whistleblower Channel Copilot — report intake -> real EU Whistleblower
Directive (2019/1937) category catalog -> deterministic severity scoring and
statutory-deadline calculation -> PDF case report with free/premium paywall.

Same architecture as Contract Risk/Vendor Risk/CSRD: a fixed, real catalog
(Article 2 material scope of the Directive) drives classification — the LLM
never decides severity itself. Its only job is: which catalog category does
this report fall under, and which aggravating factors (per Recital 42/Art. 5)
are present in the description. A deterministic function computes the final
severity, priority, and the statutory 7-day/3-month deadlines — never the LLM.
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/whistleblower", tags=["whistleblower"])

CHECKOUT_URL = "https://buy.stripe.com/8x2dRb5Qs2RZblOcOsg7e0m"

# Real catalog — Article 2(1) material scope of Directive (EU) 2019/1937,
# with a base severity reflecting the Directive's own emphasis (financial
# crime affecting EU interests and safety/health breaches are treated as
# inherently higher-severity across Member State transposition laws).
CATALOGO_CATEGORIAS = [
    {"id": "WB-A", "categoria": "Public Procurement", "base_severidade": 2},
    {"id": "WB-B", "categoria": "Financial Services, Products, Markets, AML/CTF", "base_severidade": 3},
    {"id": "WB-C", "categoria": "Product Safety and Compliance", "base_severidade": 3},
    {"id": "WB-D", "categoria": "Transport Safety", "base_severidade": 3},
    {"id": "WB-E", "categoria": "Environmental Protection", "base_severidade": 2},
    {"id": "WB-F", "categoria": "Radiation Protection and Nuclear Safety", "base_severidade": 4},
    {"id": "WB-G", "categoria": "Food/Feed Safety, Animal Health and Welfare", "base_severidade": 2},
    {"id": "WB-H", "categoria": "Public Health", "base_severidade": 3},
    {"id": "WB-I", "categoria": "Consumer Protection", "base_severidade": 1},
    {"id": "WB-J", "categoria": "Privacy, Personal Data and Network/Information Security", "base_severidade": 2},
    {"id": "WB-K", "categoria": "Financial Interests of the EU (Art. 325 TFEU)", "base_severidade": 3},
    {"id": "WB-L", "categoria": "Internal Market Rules (competition, State aid, corporate tax)", "base_severidade": 2},
    {"id": "WB-OTHER", "categoria": "Other misconduct (outside Directive scope but internally reportable)", "base_severidade": 1},
]

# Aggravating factors — each present factor adds 1 point to the base severity,
# per the risk-multiplier approach the other Global Copilots use.
FATORES_AGRAVANTES = [
    ("executive_involved", "A senior executive or director is implicated"),
    ("systemic", "The report describes a repeated or systemic pattern, not an isolated incident"),
    ("ongoing_danger", "There is an ongoing or imminent risk to health, safety, or the environment"),
    ("large_scale", "The conduct affects many employees, customers, or a large financial amount"),
    ("retaliation_reported", "The reporter describes retaliation already taken against them or another reporter"),
]

SYSTEM_PROMPT = f"""You are a whistleblower report classification engine, applying the fixed
Article 2 material-scope catalog of Directive (EU) 2019/1937 below. Read the report and:
1. category_id: pick EXACTLY ONE catalog id that best matches the report — never invent a category
   outside this list; use WB-OTHER only if truly nothing else fits.
2. For each aggravating factor listed, decide true/false based STRICTLY on what the report states —
   never assume a factor is present without explicit or clearly implied evidence in the text.

Catalog:
{chr(10).join(f"- {c['id']}: {c['categoria']}" for c in CATALOGO_CATEGORIAS)}

Aggravating factors to check:
{chr(10).join(f"- {key}: {desc}" for key, desc in FATORES_AGRAVANTES)}

Return STRICT JSON only:
{{"category_id": "WB-B", "factors": {{"executive_involved": true, "systemic": false, "ongoing_danger": false, "large_scale": false, "retaliation_reported": false}}, "summary": "one sentence neutral summary of the report"}}"""


def _pontuar(extracao: dict) -> dict:
    """Deterministic scoring — the LLM only classified category + factor
    presence above; this function is the only place that computes the final
    severity, priority, and the statutory deadlines."""
    categoria_por_id = {c["id"]: c for c in CATALOGO_CATEGORIAS}
    cat = categoria_por_id.get(extracao.get("category_id"), categoria_por_id["WB-OTHER"])
    factors = extracao.get("factors", {}) or {}

    factor_count = sum(1 for key, _ in FATORES_AGRAVANTES if factors.get(key))
    severidade_pontos = cat["base_severidade"] + factor_count

    if severidade_pontos >= 6:
        severidade = "Critical"
    elif severidade_pontos >= 4:
        severidade = "High"
    elif severidade_pontos >= 2:
        severidade = "Medium"
    else:
        severidade = "Low"

    fatores_presentes = [desc for key, desc in FATORES_AGRAVANTES if factors.get(key)]

    return {
        "category_id": cat["id"],
        "category": cat["categoria"],
        "severity": severidade,
        "severity_score": severidade_pontos,
        "aggravating_factors_present": fatores_presentes,
        "summary": extracao.get("summary", ""),
    }


@router.post("/submit-report")
async def submit_report(data: dict):
    case_id = f"WB-{uuid.uuid4().hex[:8].upper()}"
    description = data.get("description", "")
    customer_email = data.get("customer_email", "")
    now = datetime.now(timezone.utc)

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Category (self-declared, verify against catalog): {data.get('category', 'unknown')}\nDepartment: {data.get('department', 'unknown')}\nReport description:\n{description}"
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    extracao = parsear_json_llm(raw)
    resultado = _pontuar(extracao)
    acknowledgment_due = (now + timedelta(days=7)).date().isoformat()
    feedback_due = (now + timedelta(days=90)).date().isoformat()
    resultado.update({
        "case_id": case_id,
        "received_at": now.isoformat(),
        "acknowledgment_due": acknowledgment_due,
        "feedback_due": feedback_due,
        # Aliases so the shared PDF template (classification/risk_score/gaps/
        # action_plan) renders a real report instead of blank sections.
        "classification": resultado["severity"],
        "classification_reasoning": resultado["summary"],
        "risk_score": resultado["severity_score"],
        "gaps": [f"Aggravating factor: {f}" for f in resultado["aggravating_factors_present"]],
        "action_plan": [
            {"priority": 1, "action": "Acknowledge receipt to the reporter (Art. 9(1)(b))", "deadline_days": 7},
            {"priority": 2, "action": "Assign an impartial person/department to investigate", "deadline_days": 7},
            {"priority": 3, "action": "Provide diligent follow-up and feedback to the reporter (Art. 9(1)(f))", "deadline_days": 90},
        ],
    })

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Case classified in demo mode — unlock the premium version for the full case report and investigation checklist.",
            "checkout_url": CHECKOUT_URL,
        }
    pdf_buf = gerar_pdf_relatorio("Whistleblower Case Report", case_id, resultado)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": f'attachment; filename="Whistleblower_Case_{case_id}.pdf"'})


@router.post("/case-analysis")
async def analyze_case(data: dict):
    """Backward compatibility — same classification engine, kept for existing integrations."""
    return await submit_report({
        "description": data.get("case_description", ""),
        "category": "unknown",
        "department": data.get("company", "unknown"),
        "customer_email": data.get("customer_email", ""),
    })


@router.get("/compliance-check")
async def whistleblower_compliance(employees: int = 50, country: str = "EU"):
    """Structural check — does the company even need a channel under the Directive.
    Deterministic threshold from Article 8: 50+ workers (or public-sector bodies),
    no LLM call needed here since it's a plain legal threshold, not a judgment call."""
    mandatory = employees >= 50 and "EU" in country.upper()
    return {
        "mandatory": mandatory,
        "directive": "Directive (EU) 2019/1937, Article 8",
        "deadline": "Transposed — already mandatory in all EU Member States",
        "penalty": "Up to €20,000+ per violation depending on Member State transposition law",
        "checkout_url": CHECKOUT_URL if mandatory else None,
    }
