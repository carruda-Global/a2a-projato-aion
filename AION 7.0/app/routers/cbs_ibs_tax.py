"""CBS/IBS Tax Readiness Copilot — company tax profile -> real Brazilian tax
reform readiness checklist (EC 132/2023, LC 214/2025) -> deterministic
readiness scoring -> PDF with free/premium paywall.

Same architecture as the other Global Copilots: a fixed, real catalog of
transition-readiness items drives the assessment. The LLM only extracts,
per catalog item, whether the company has already addressed it — it never
invents the checklist or decides the score.
"""
import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/cbs-ibs-tax", tags=["cbs_ibs_tax"])

CHECKOUT_URL = "https://buy.stripe.com/aFa4gB7YAbovcpSdSwg7e0r"

# Real catalog — CBS/IBS transition readiness items, Emenda Constitucional
# 132/2023 and Lei Complementar 214/2025 (Reforma Tributaria do Consumo).
CATALOGO_CBS_IBS = [
    {"id": "TX-01", "item": "NCM/NBS Product & Service Classification Review",
     "criterio": "Every product (NCM) and service (NBS) has been reviewed and mapped to the new CBS/IBS classification."},
    {"id": "TX-02", "item": "Rate Regime Classification (Standard / Reduced / Exempt)",
     "criterio": "Company has identified which of its products/services fall under standard rate, reduced-rate baskets (e.g. food, health, education) or specific regimes."},
    {"id": "TX-03", "item": "Non-Cumulative Credit System Adaptation",
     "criterio": "Accounting/ERP systems are set up to take full IBS/CBS input credits (broad non-cumulative model, unlike ICMS/ISS restrictions)."},
    {"id": "TX-04", "item": "Split Payment Mechanism Readiness",
     "criterio": "Company's payment/invoicing flow is ready for split-payment (tax segregated and remitted at the moment of payment, per LC 214/2025)."},
    {"id": "TX-05", "item": "Transition Period Dual System Compliance (2026-2033)",
     "criterio": "Company can calculate and report both the old taxes (PIS/COFINS/ICMS/ISS, phasing out) and new CBS/IBS (phasing in) during the coexistence period."},
    {"id": "TX-06", "item": "ERP / NF-e Invoice System Update",
     "criterio": "Invoicing systems (NF-e/NFS-e) have been updated to issue documents with the new CBS/IBS fields and rates."},
    {"id": "TX-07", "item": "Specific Regime Eligibility Check",
     "criterio": "Company has checked eligibility for special regimes (Simples Nacional, Zona Franca de Manaus, agribusiness, etc.) under the new system."},
]

SYSTEM_PROMPT = f"""You are a CBS/IBS tax-reform readiness engine, applying the fixed catalog of
{len(CATALOGO_CBS_IBS)} transition-readiness items below (EC 132/2023, LC 214/2025). For EACH catalog
item, decide based STRICTLY on the company profile given whether it is met, weak (partially
addressed), or a gap. Never invent checklist items outside this catalog and never judge based on
your own opinion of tax strategy.

Catalog:
{chr(10).join(f"- {c['id']}: {c['item']} — criterion: {c['criterio']}" for c in CATALOGO_CBS_IBS)}

Return STRICT JSON only:
{{"items": [{{"id": "TX-01", "status": "met" | "gap" | "weak", "evidence": "short justification"}}]}}
One entry per catalog id, in order."""


def _pontuar(items_llm: list[dict]) -> dict:
    """Deterministic scoring — same role as _pontuar in Contract Risk: the LLM
    only extracted per-item status above; this function decides the final
    readiness score and action plan."""
    by_id = {i.get("id"): i.get("status", "gap") for i in items_llm}
    evidencia = {i.get("id"): i.get("evidence", "") for i in items_llm}

    checklist, gaps, action_plan = [], [], []
    pontos_totais = pontos_obtidos = 0

    for item in CATALOGO_CBS_IBS:
        tid = item["id"]
        status = by_id.get(tid, "gap")
        pontos_totais += 1
        if status == "met":
            pontos_obtidos += 1
        elif status == "weak":
            pontos_obtidos += 0.5

        status_final = "met" if status == "met" else "gap"
        checklist.append({"requirement": f"{tid} — {item['item']}", "status": status_final})
        if status_final == "gap":
            gaps.append(f"{tid} ({item['item']}) — {evidencia.get(tid, 'not addressed')}")
            action_plan.append({"priority": 1, "action": f"Address {item['item']} ({tid}).", "deadline_days": 60})

    readiness_score = round((pontos_obtidos / pontos_totais) * 100) if pontos_totais else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    if readiness_score >= 85:
        classificacao = "Transition Ready"
    elif readiness_score >= 50:
        classificacao = "Partial Readiness"
    else:
        classificacao = "Significant Gaps"

    return {
        "classification": classificacao,
        "risk_score": readiness_score,
        "readiness_score": readiness_score,
        "obligations": checklist,
        "gaps": gaps,
        "action_plan": action_plan,
    }


@router.post("/avaliar")
async def avaliar_prontidao(data: dict):
    company = data.get("company", "")
    customer_email = data.get("customer_email", "")
    profile = (
        f"Company: {company}\nTax regime: {data.get('tax_regime', 'unknown')}\n"
        f"Sector: {data.get('sector', '')}\n"
        f"Current CBS/IBS preparation described: {data.get('current_state', 'none stated')}"
    )

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, profile)
    extracao = parsear_json_llm(raw)
    resultado = _pontuar(extracao.get("items", []))

    resumo_prompt = (
        f"Company: {company}\nCBS/IBS readiness: {resultado['readiness_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are a Brazilian tax reform (CBS/IBS) advisor.", resumo_prompt
    )

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": CHECKOUT_URL,
        }
    pdf_buf = gerar_pdf_relatorio("CBS/IBS Tax Transition Readiness Report", company, resultado)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="CBS_IBS_Readiness_Report.pdf"'})
