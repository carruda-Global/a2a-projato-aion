"""Anti-Corruption Copilot — integrity program profile -> real Decreto
11.129/2022 (Lei Anticorrupcao regulation) pillar catalog -> deterministic
maturity scoring -> PDF with free/premium paywall.

Same architecture as the other Global Copilots: a fixed, real catalog (the
integrity-program pillars listed in Decreto 11.129/2022, Art. 42, which
regulates Lei 12.846/2013 and aligns with ISO 37001) drives the assessment.
The LLM only extracts, per pillar, whether the company already has it in
place — it never decides the pillar list or the maturity score.
"""
import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/anti-corruption", tags=["anti_corruption"])

CHECKOUT_URL = "https://buy.stripe.com/8x2dRb5Qs2RZblOcOsg7e0m"

# Real catalog — integrity program pillars per Decreto 11.129/2022, Art. 42
# (regulates Lei 12.846/2013), cross-referenced with ISO 37001 anti-bribery
# management system clauses.
CATALOGO_INTEGRIDADE = [
    {"id": "AC-01", "pilar": "Senior Management Commitment ('Tone at the Top')",
     "criterio": "Leadership visibly sponsors and resources the integrity program (ISO 37001 5.1)."},
    {"id": "AC-02", "pilar": "Code of Ethics and Conduct",
     "criterio": "A documented code of conduct exists and is communicated to all employees."},
    {"id": "AC-03", "pilar": "Gifts, Hospitality and Entertainment Policy",
     "criterio": "Written rules limit/require approval for gifts, hospitality and entertainment involving public officials or business partners."},
    {"id": "AC-04", "pilar": "Conflict of Interest Management",
     "criterio": "A process exists for employees to disclose and manage conflicts of interest."},
    {"id": "AC-05", "pilar": "Whistleblower Channel with Non-Retaliation",
     "criterio": "A confidential reporting channel exists with an explicit non-retaliation guarantee (ISO 37001 8.9)."},
    {"id": "AC-06", "pilar": "Training Program",
     "criterio": "Employees and relevant third parties receive periodic anti-corruption training."},
    {"id": "AC-07", "pilar": "Third-Party Due Diligence",
     "criterio": "A risk-based due diligence process screens vendors, agents, and business partners before and during the relationship (ISO 37001 8.2)."},
    {"id": "AC-08", "pilar": "Continuous Monitoring and Internal Audit",
     "criterio": "The program is periodically audited/monitored for effectiveness, not just implemented once."},
    {"id": "AC-09", "pilar": "Disciplinary Consequences for Violations",
     "criterio": "Documented consequences exist and are applied for violations of the code/policies."},
    {"id": "AC-10", "pilar": "Periodic Risk Assessment",
     "criterio": "Corruption risk is periodically reassessed based on the company's actual operations and geographies (ISO 37001 4.5)."},
]

SYSTEM_PROMPT = f"""You are an anti-corruption integrity-program maturity engine, applying the fixed
catalog of {len(CATALOGO_INTEGRIDADE)} pillars below (Decreto 11.129/2022, Art. 42 and ISO 37001).
For EACH catalog item, decide based STRICTLY on the company profile given whether it is met, weak
(partially implemented), or a gap. Never invent pillars outside this catalog.

Catalog:
{chr(10).join(f"- {c['id']}: {c['pilar']} — criterion: {c['criterio']}" for c in CATALOGO_INTEGRIDADE)}

Return STRICT JSON only:
{{"items": [{{"id": "AC-01", "status": "met" | "gap" | "weak", "evidence": "short justification"}}]}}
One entry per catalog id, in order."""


def _pontuar(items_llm: list[dict]) -> dict:
    """Deterministic scoring — same pattern as Contract Risk/CBS-IBS: the LLM
    only extracted per-pillar status above; this function decides the final
    maturity score and action plan."""
    by_id = {i.get("id"): i.get("status", "gap") for i in items_llm}
    evidencia = {i.get("id"): i.get("evidence", "") for i in items_llm}

    checklist, gaps, action_plan = [], [], []
    pontos_totais = pontos_obtidos = 0

    for item in CATALOGO_INTEGRIDADE:
        tid = item["id"]
        status = by_id.get(tid, "gap")
        pontos_totais += 1
        if status == "met":
            pontos_obtidos += 1
        elif status == "weak":
            pontos_obtidos += 0.5

        status_final = "met" if status == "met" else "gap"
        checklist.append({"requirement": f"{tid} — {item['pilar']}", "status": status_final})
        if status_final == "gap":
            gaps.append(f"{tid} ({item['pilar']}) — {evidencia.get(tid, 'not implemented')}")
            action_plan.append({"priority": 1, "action": f"Implement {item['pilar']} ({tid}).", "deadline_days": 60})

    maturity_score = round((pontos_obtidos / pontos_totais) * 100) if pontos_totais else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    if maturity_score >= 85:
        classificacao = "Mature Program"
    elif maturity_score >= 50:
        classificacao = "Developing Program"
    else:
        classificacao = "Early Stage — High Exposure"

    return {
        "classification": classificacao,
        "risk_score": maturity_score,
        "maturity_score": maturity_score,
        "obligations": checklist,
        "gaps": gaps,
        "action_plan": action_plan,
    }


@router.post("/diagnostico")
async def diagnosticar_maturidade(data: dict):
    company = data.get("company", "")
    customer_email = data.get("customer_email", "")
    profile = (
        f"Company: {company}\nSector: {data.get('sector', '')}\n"
        f"Public-sector contracting exposure: {data.get('public_sector_exposure', 'unknown')}\n"
        f"Current integrity practices/policies: {data.get('current_practices', 'none stated')}"
    )

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, profile)
    extracao = parsear_json_llm(raw)
    resultado = _pontuar(extracao.get("items", []))

    resumo_prompt = (
        f"Company: {company}\nIntegrity program maturity: {resultado['maturity_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are a Brazilian anti-corruption compliance advisor.", resumo_prompt
    )

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": CHECKOUT_URL,
        }
    pdf_buf = gerar_pdf_relatorio("Anti-Corruption Integrity Program Report", company, resultado)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="Anti_Corruption_Report.pdf"'})
