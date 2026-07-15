"""Pay Equity Copilot — payroll/policy profile -> real Lei 14.611/2023 (Equal
Pay Law) obligation catalog -> deterministic compliance scoring -> PDF with
free/premium paywall.

Same architecture as the other Global Copilots: a fixed, real catalog of
statutory obligations drives the assessment. The LLM only extracts, per
obligation, whether the company already meets it — it never decides the
obligation list or the compliance score.
"""
import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/pay-equity", tags=["pay_equity"])

CHECKOUT_URL = "https://buy.stripe.com/8x2dRb5Qs2RZblOcOsg7e0m"

# Real catalog — Lei 14.611/2023 (Lei de Igualdade Salarial) and its
# regulating Decreto 11.795/2023.
CATALOGO_IGUALDADE_SALARIAL = [
    {"id": "PE-01", "obrigacao": "Semestral Pay Transparency Report",
     "criterio": "Companies with 100+ employees publish a semestral pay-transparency report via the Portal Emprega Brasil (Art. 5, Lei 14.611/2023)."},
    {"id": "PE-02", "obrigacao": "Pay Gap Breakdown by Gender and Race",
     "criterio": "The report shows average remuneration by gender and race for equal or equivalent roles, not just company-wide averages."},
    {"id": "PE-03", "obrigacao": "Corrective Action Plan for Identified Gaps",
     "criterio": "If a pay gap is identified, an action plan is elaborated and executed within 90 days (Decreto 11.795/2023, Art. 5)."},
    {"id": "PE-04", "obrigacao": "Discrimination Reporting Channel",
     "criterio": "A confidential channel exists for employees to report pay discrimination, with non-retaliation guarantees."},
    {"id": "PE-05", "obrigacao": "Objective, Published Promotion/Pay Criteria",
     "criterio": "Criteria for promotion and pay progression are objective, documented, and accessible to employees (Art. 6, Lei 14.611/2023)."},
]

SYSTEM_PROMPT = f"""You are a pay-equity compliance engine, applying the fixed catalog of
{len(CATALOGO_IGUALDADE_SALARIAL)} obligations below (Lei 14.611/2023 and Decreto 11.795/2023). For
EACH catalog item, decide based STRICTLY on the company profile given whether it is met, weak
(partially addressed), or a gap. Never invent obligations outside this catalog.

Catalog:
{chr(10).join(f"- {c['id']}: {c['obrigacao']} — criterion: {c['criterio']}" for c in CATALOGO_IGUALDADE_SALARIAL)}

Return STRICT JSON only:
{{"items": [{{"id": "PE-01", "status": "met" | "gap" | "weak", "evidence": "short justification"}}]}}
One entry per catalog id, in order."""


def _pontuar(items_llm: list[dict], num_employees: int) -> dict:
    """Deterministic scoring. Also applies the real statutory threshold
    (100+ employees) as a plain code check, not an LLM judgment call."""
    mandatory = num_employees >= 100
    by_id = {i.get("id"): i.get("status", "gap") for i in items_llm}
    evidencia = {i.get("id"): i.get("evidence", "") for i in items_llm}

    checklist, gaps, action_plan = [], [], []
    pontos_totais = pontos_obtidos = 0

    for item in CATALOGO_IGUALDADE_SALARIAL:
        tid = item["id"]
        status = by_id.get(tid, "gap")
        pontos_totais += 1
        if status == "met":
            pontos_obtidos += 1
        elif status == "weak":
            pontos_obtidos += 0.5

        status_final = "met" if status == "met" else "gap"
        checklist.append({"requirement": f"{tid} — {item['obrigacao']}", "status": status_final})
        if status_final == "gap":
            gaps.append(f"{tid} ({item['obrigacao']}) — {evidencia.get(tid, 'not addressed')}")
            action_plan.append({"priority": 1, "action": f"Implement {item['obrigacao']} ({tid}).", "deadline_days": 90})

    compliance_score = round((pontos_obtidos / pontos_totais) * 100) if pontos_totais else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    if not mandatory:
        classificacao = "Not Yet Mandatory (<100 employees)"
    elif compliance_score >= 85:
        classificacao = "Compliant"
    elif compliance_score >= 50:
        classificacao = "Partial Compliance"
    else:
        classificacao = "Non-Compliant — Fine Risk"

    return {
        "classification": classificacao,
        "risk_score": compliance_score,
        "compliance_score": compliance_score,
        "mandatory": mandatory,
        "obligations": checklist,
        "gaps": gaps if mandatory else [],
        "action_plan": action_plan if mandatory else [],
        "penalty": "Up to 3% of payroll, capped at 100 minimum wages, per Decreto 11.795/2023" if mandatory else None,
    }


@router.post("/avaliar")
async def analisar_equidade(data: dict):
    company = data.get("company", "")
    customer_email = data.get("customer_email", "")
    employees = int(data.get("employees", 0) or 0)
    profile = (
        f"Company: {company}\nEmployees: {employees}\n"
        f"Current pay equity practices/policies: {data.get('current_practices', 'none stated')}"
    )

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, profile)
    extracao = parsear_json_llm(raw)
    resultado = _pontuar(extracao.get("items", []), employees)

    resumo_prompt = (
        f"Company: {company} ({employees} employees)\nCompliance score: {resultado['compliance_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are a Brazilian labor law (pay equity) advisor.", resumo_prompt
    )

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": CHECKOUT_URL,
        }
    pdf_buf = gerar_pdf_relatorio("Pay Equity Compliance Report (Lei 14.611/2023)", company, resultado)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="Pay_Equity_Report.pdf"'})
