"""Scope 3 Suppliers Copilot — supply-chain profile -> real GHG Protocol Scope 3
category catalog (15 categories) -> deterministic materiality/tracking scoring
-> PDF with free/premium paywall.

Same architecture as Carbon Inventory/CSRD: a fixed, real catalog (the 15 GHG
Protocol Scope 3 categories) drives the assessment, cross-referenced against
CBAM-covered goods and IFRS S2 value-chain disclosure. The LLM only extracts,
per category, whether it is material and whether the company tracks it.
"""
import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/scope3-suppliers", tags=["scope3_suppliers"])

CHECKOUT_URL = "https://buy.stripe.com/fZu00l92E78fdtW29Og7e0n"

# Real catalog — the 15 GHG Protocol Scope 3 categories (Corporate Value Chain
# Accounting and Reporting Standard).
CATALOGO_ESCOPO_3 = [
    {"id": "S3-01", "categoria": "Purchased Goods and Services"},
    {"id": "S3-02", "categoria": "Capital Goods"},
    {"id": "S3-03", "categoria": "Fuel- and Energy-Related Activities (not in Scope 1/2)"},
    {"id": "S3-04", "categoria": "Upstream Transportation and Distribution"},
    {"id": "S3-05", "categoria": "Waste Generated in Operations"},
    {"id": "S3-06", "categoria": "Business Travel"},
    {"id": "S3-07", "categoria": "Employee Commuting"},
    {"id": "S3-08", "categoria": "Upstream Leased Assets"},
    {"id": "S3-09", "categoria": "Downstream Transportation and Distribution"},
    {"id": "S3-10", "categoria": "Processing of Sold Products"},
    {"id": "S3-11", "categoria": "Use of Sold Products"},
    {"id": "S3-12", "categoria": "End-of-Life Treatment of Sold Products"},
    {"id": "S3-13", "categoria": "Downstream Leased Assets"},
    {"id": "S3-14", "categoria": "Franchises"},
    {"id": "S3-15", "categoria": "Investments"},
]

# CBAM (Carbon Border Adjustment Mechanism, Regulation (EU) 2023/956) covered
# goods — real, fixed list, not an LLM guess.
BENS_CBAM = ["cement", "iron and steel", "aluminium", "fertilisers", "electricity", "hydrogen"]

SYSTEM_PROMPT = f"""You are a Scope 3 supply-chain materiality engine, applying the fixed catalog
of {len(CATALOGO_ESCOPO_3)} GHG Protocol Scope 3 categories below. For EACH catalog item, decide
based STRICTLY on the company profile given:
1. is_material: true/false — is this category plausibly a meaningful part of this company's value
   chain (e.g. a services company with no owned fleet likely has little S3-04 upstream transport).
2. is_tracked: true/false — does the company already track/estimate emissions for this category,
   or is it a gap.
Never invent categories outside this catalog.
Also decide: imports_cbam_goods (true/false) — does the company import any of: {', '.join(BENS_CBAM)}.

Catalog:
{chr(10).join(f"- {c['id']}: {c['categoria']}" for c in CATALOGO_ESCOPO_3)}

Return STRICT JSON only:
{{"items": [{{"id": "S3-01", "is_material": true, "is_tracked": false, "reasoning": "short justification"}}],
"imports_cbam_goods": false}}
One entry per catalog id, in order."""


def _pontuar(extracao: dict) -> dict:
    """Deterministic scoring — the LLM only flagged materiality/tracking per
    category above; this function decides the final material-category list,
    gaps, CBAM exposure, and the tracking-maturity score."""
    items_llm = extracao.get("items", [])
    by_id = {i.get("id"): i for i in items_llm}

    material, gaps, action_plan = [], [], []
    for cat in CATALOGO_ESCOPO_3:
        cid = cat["id"]
        item = by_id.get(cid, {})
        if not item.get("is_material"):
            continue
        tracked = bool(item.get("is_tracked"))
        material.append({
            "id": cid, "requirement": f"{cid} — {cat['categoria']}",
            "status": "tracked" if tracked else "gap",
            "reasoning": item.get("reasoning", ""),
        })
        if not tracked:
            gaps.append(f"{cid} ({cat['categoria']}) — not tracked")
            action_plan.append({
                "priority": 1,
                "action": f"Set up supplier data collection or spend-based estimation for {cat['categoria']}.",
                "deadline_days": 60,
            })

    total_material = len(material)
    tracked_count = sum(1 for m in material if m["status"] == "tracked")
    maturity_score = round((tracked_count / total_material) * 100) if total_material else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    cbam_exposure = bool(extracao.get("imports_cbam_goods"))
    if cbam_exposure:
        gaps.append("CBAM exposure: imports goods covered by Regulation (EU) 2023/956 — quarterly CBAM declarations required")
        action_plan.append({"priority": len(action_plan) + 1, "action": "Set up CBAM quarterly declaration process for covered imports.", "deadline_days": 30})

    if maturity_score >= 85:
        classificacao = "Scope 3 Mature"
    elif maturity_score >= 50:
        classificacao = "Partial Tracking"
    else:
        classificacao = "Early Stage"

    return {
        "classification": classificacao,
        "risk_score": maturity_score,
        "maturity_score": maturity_score,
        "obligations": material,
        "total_material_categories": total_material,
        "cbam_exposure": cbam_exposure,
        "gaps": gaps,
        "action_plan": action_plan,
    }


@router.post("/avaliar")
async def avaliar_fornecedores(data: dict):
    company = data.get("company", "")
    customer_email = data.get("customer_email", "")
    profile = (
        f"Company: {company}\nSector: {data.get('sector', '')}\n"
        f"Supply chain description: {data.get('supply_chain', '')}\n"
        f"Imports: {data.get('imports', 'unknown')}"
    )

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, profile)
    extracao = parsear_json_llm(raw)
    resultado = _pontuar(extracao)

    resumo_prompt = (
        f"Company: {company}\nScope 3 maturity: {resultado['maturity_score']}/100\n"
        f"Classification: {resultado['classification']}\nCBAM exposure: {resultado['cbam_exposure']}\n"
        "Write a 2-3 sentence executive summary in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are a Scope 3/CBAM supply-chain advisor.", resumo_prompt
    )

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": CHECKOUT_URL,
        }
    pdf_buf = gerar_pdf_relatorio("Scope 3 Supplier Emissions Report", company, resultado)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="Scope3_Suppliers_Report.pdf"'})
