"""Carbon Inventory Copilot — company energy/fuel profile -> real GHG Protocol
Scope 1+2 source catalog -> deterministic completeness scoring -> PDF with
free/premium paywall.

Same architecture as CSRD/Contract Risk: a fixed, real catalog (GHG Protocol
Corporate Standard, Scope 1 direct emissions + Scope 2 purchased energy source
categories) drives the assessment. The LLM only extracts, per catalog source,
whether the company has quantified activity data and an emission factor on
file — it never decides which sources exist or the completeness score.
"""
import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/carbon-inventory", tags=["carbon_inventory"])

CHECKOUT_URL = "https://buy.stripe.com/fZu00l92E78fdtW29Og7e0n"

# Real catalog — GHG Protocol Corporate Accounting and Reporting Standard,
# Scope 1 (direct) and Scope 2 (purchased energy) source categories.
CATALOGO_GHG_ESCOPO_1_2 = [
    {"id": "CI-01", "escopo": 1, "fonte": "Stationary Combustion",
     "criterio": "Fuel burned on-site in boilers, furnaces, generators (natural gas, diesel, LPG)."},
    {"id": "CI-02", "escopo": 1, "fonte": "Mobile Combustion (Owned Fleet)",
     "criterio": "Fuel burned in company-owned or leased vehicles (fleet, forklifts, machinery)."},
    {"id": "CI-03", "escopo": 1, "fonte": "Fugitive Emissions",
     "criterio": "Refrigerant/HVAC leaks, SF6 in switchgear, or other fugitive gas releases."},
    {"id": "CI-04", "escopo": 1, "fonte": "Process Emissions",
     "criterio": "Emissions from industrial/chemical processes themselves (e.g. cement, metal, chemical reactions), not combustion."},
    {"id": "CI-05", "escopo": 2, "fonte": "Purchased Electricity (Location-Based)",
     "criterio": "Grid electricity consumption using the local grid's average emission factor."},
    {"id": "CI-06", "escopo": 2, "fonte": "Purchased Electricity (Market-Based)",
     "criterio": "Grid electricity consumption using supplier-specific/contractual emission factors (e.g. renewable energy contracts, RECs/I-RECs)."},
    {"id": "CI-07", "escopo": 2, "fonte": "Purchased Heat, Steam or Cooling",
     "criterio": "Thermal energy purchased from a third party (district heating/cooling, steam supply)."},
]

SYSTEM_PROMPT = f"""You are a GHG inventory completeness engine, applying the fixed catalog of
{len(CATALOGO_GHG_ESCOPO_1_2)} GHG Protocol Scope 1/2 source categories below. For EACH catalog item,
decide based STRICTLY on the company profile given:
1. is_applicable: true/false — does this source plausibly exist in this company's operations,
   based on the criterion (e.g. no owned fleet means CI-02 is not applicable).
2. has_quantified_data: true/false — did the company provide actual consumption/activity data
   and an emission factor for this source, or is it a gap.
Never invent sources outside this catalog.

Catalog:
{chr(10).join(f"- {c['id']} (Scope {c['escopo']}): {c['fonte']} — criterion: {c['criterio']}" for c in CATALOGO_GHG_ESCOPO_1_2)}

Return STRICT JSON only:
{{"items": [{{"id": "CI-01", "is_applicable": true, "has_quantified_data": false, "estimated_tco2e": null, "reasoning": "short justification"}}]}}
One entry per catalog id, in order. estimated_tco2e is a rough number if the company gave enough data to estimate, else null."""


def _pontuar(items_llm: list[dict]) -> dict:
    """Deterministic scoring — the LLM only flagged applicability/data-presence
    per source above; this function decides the final inventory and score."""
    by_id = {i.get("id"): i for i in items_llm}
    inventario, gaps, action_plan = [], [], []
    aplicaveis = quantificados = 0
    total_tco2e = 0.0

    for fonte in CATALOGO_GHG_ESCOPO_1_2:
        fid = fonte["id"]
        item = by_id.get(fid, {})
        if not item.get("is_applicable"):
            continue
        aplicaveis += 1
        tem_dado = bool(item.get("has_quantified_data"))
        inventario.append({
            "id": fid, "requirement": f"{fid} (Scope {fonte['escopo']}) — {fonte['fonte']}",
            "status": "quantified" if tem_dado else "gap",
            "estimated_tco2e": item.get("estimated_tco2e"),
        })
        if tem_dado:
            quantificados += 1
            valor = item.get("estimated_tco2e")
            if isinstance(valor, (int, float)):
                total_tco2e += valor
        else:
            gaps.append(f"{fid} ({fonte['fonte']}) — no activity data / emission factor on file")
            action_plan.append({
                "priority": 1 if fonte["escopo"] == 1 else 2,
                "action": f"Collect activity data and apply an emission factor for {fonte['fonte']} (Scope {fonte['escopo']}).",
                "deadline_days": 30,
            })

    readiness_score = round((quantificados / aplicaveis) * 100) if aplicaveis else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    if readiness_score >= 85:
        classificacao = "Inventory Complete"
    elif readiness_score >= 50:
        classificacao = "Partial Inventory"
    else:
        classificacao = "Inventory Not Started"

    return {
        "classification": classificacao,
        "risk_score": readiness_score,
        "readiness_score": readiness_score,
        "obligations": inventario,
        "total_applicable_sources": aplicaveis,
        "estimated_total_tco2e": round(total_tco2e, 2) if total_tco2e else None,
        "gaps": gaps,
        "action_plan": action_plan,
    }


@router.post("/calcular")
async def calcular_emissoes(data: dict):
    company = data.get("company", "")
    customer_email = data.get("customer_email", "")
    profile = (
        f"Company: {company}\nSector: {data.get('sector', '')}\n"
        f"Owned vehicle fleet: {data.get('fleet', 'unknown')}\n"
        f"Energy/fuel consumption data provided: {data.get('consumption_data', 'none stated')}"
    )

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, profile)
    extracao = parsear_json_llm(raw)
    resultado = _pontuar(extracao.get("items", []))

    resumo_prompt = (
        f"Company: {company}\nInventory completeness: {resultado['readiness_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are a GHG Protocol carbon accounting advisor.", resumo_prompt
    )

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": CHECKOUT_URL,
        }
    pdf_buf = gerar_pdf_relatorio("Carbon Inventory Report (GHG Protocol Scope 1+2)", company, resultado)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="Carbon_Inventory_Report.pdf"'})
