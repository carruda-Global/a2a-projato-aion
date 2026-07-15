"""CSRD Double Materiality Copilot — company profile -> real ESRS topic
catalog -> deterministic materiality + readiness scoring -> PDF with
free/premium paywall.

Same architecture as Contract Risk/Vendor Risk: a fixed, real catalog (the 10
ESRS topical standards from Commission Delegated Regulation (EU) 2023/2772,
the CSRD's Set 1 disclosure standards) drives the assessment — the LLM never
invents which topics matter. Its only job is: for each catalog topic, is it
plausibly material for this company (impact materiality and/or financial
materiality, per ESRS 1 double-materiality principle) and does the company
already have a policy/metric/target for it. A deterministic function decides
the final materiality call and the readiness score — never the LLM.
"""
import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/csrd", tags=["csrd"])

CHECKOUT_URL = "https://buy.stripe.com/fZu00l92E78fdtW29Og7e0n"

# Real catalog — ESRS Set 1 topical standards, Commission Delegated Regulation
# (EU) 2023/2772. ESRS 2 (general disclosures) is mandatory for every company
# in scope regardless of materiality; the other 10 are subject to the double
# materiality assessment (impact materiality OR financial materiality).
CATALOGO_ESRS = [
    {"id": "ESRS-2", "topico": "General Disclosures", "sempre_material": True,
     "criterio": "Mandatory for every company in CSRD scope: governance, strategy, IRO (impact/risk/opportunity) management, and metrics/targets processes."},
    {"id": "ESRS-E1", "topico": "Climate Change", "sempre_material": False,
     "criterio": "Material if the company has meaningful GHG emissions (Scope 1/2/3), energy consumption, or climate transition/physical risk exposure."},
    {"id": "ESRS-E2", "topico": "Pollution", "sempre_material": False,
     "criterio": "Material if operations emit air/water/soil pollutants, use substances of concern, or handle microplastics."},
    {"id": "ESRS-E3", "topico": "Water and Marine Resources", "sempre_material": False,
     "criterio": "Material if the company withdraws/consumes significant water volumes or operates near water-stressed areas or marine ecosystems."},
    {"id": "ESRS-E4", "topico": "Biodiversity and Ecosystems", "sempre_material": False,
     "criterio": "Material if operations or supply chain affect land use, protected areas, or ecosystem services."},
    {"id": "ESRS-E5", "topico": "Resource Use and Circular Economy", "sempre_material": False,
     "criterio": "Material if the business model depends on resource inflows/outflows, packaging, or waste generation at meaningful scale."},
    {"id": "ESRS-S1", "topico": "Own Workforce", "sempre_material": False,
     "criterio": "Material if the company has employees — working conditions, equal treatment, other labor rights (almost always material for any employer)."},
    {"id": "ESRS-S2", "topico": "Workers in the Value Chain", "sempre_material": False,
     "criterio": "Material if the company relies on suppliers/contractors with labor-rights exposure (e.g. manufacturing, agriculture, extended supply chains)."},
    {"id": "ESRS-S3", "topico": "Affected Communities", "sempre_material": False,
     "criterio": "Material if operations affect local communities (land rights, resettlement, indigenous peoples, security)."},
    {"id": "ESRS-S4", "topico": "Consumers and End-users", "sempre_material": False,
     "criterio": "Material if the company sells directly to consumers with data privacy, health/safety, or responsible marketing exposure."},
    {"id": "ESRS-G1", "topico": "Business Conduct", "sempre_material": False,
     "criterio": "Material if the company has meaningful exposure to corruption/bribery risk, political engagement, supplier payment practices, or whistleblower obligations (almost always material)."},
]

SYSTEM_PROMPT = f"""You are a CSRD double-materiality assessment engine, applying the fixed catalog
of {len(CATALOGO_ESRS)} ESRS topical standards below (Commission Delegated Regulation (EU) 2023/2772).
For EACH catalog item, decide based STRICTLY on the company profile given:
1. is_material: true/false — would a reasonable assessor conclude this topic has impact materiality
   (the company's actual/potential impact on people or environment) or financial materiality
   (risk/opportunity to the company's financial position), per the stated criterion.
2. has_disclosure: true/false — does the company already have a stated policy, target, or metric
   for this topic (based on what they told you), or is it a gap.
Never invent topics outside this catalog. Never decide the topic list yourself.

Catalog:
{chr(10).join(f"- {c['id']}: {c['topico']} — criterion: {c['criterio']}" for c in CATALOGO_ESRS)}

Return STRICT JSON only:
{{"items": [{{"id": "ESRS-2", "is_material": true, "has_disclosure": false, "reasoning": "short justification"}}]}}
One entry per catalog id, in order."""


def _pontuar(items_llm: list[dict]) -> dict:
    """Deterministic scoring — same role as _pontuar in Contract Risk/Vendor Risk:
    the LLM only extracted per-topic materiality/disclosure signals above; this
    function is the only place that decides the final material-topic list,
    gaps, and readiness score."""
    by_id = {i.get("id"): i for i in items_llm}

    material_topics, gaps, action_plan, ready = [], [], [], []

    for topico in CATALOGO_ESRS:
        tid = topico["id"]
        item = by_id.get(tid, {})
        is_material = topico["sempre_material"] or bool(item.get("is_material"))
        has_disclosure = bool(item.get("has_disclosure"))

        if not is_material:
            continue

        material_topics.append({
            "id": tid, "topic": topico["topico"],
            "requirement": f"{tid} — {topico['topico']}",
            "status": "disclosed" if has_disclosure else "gap",
            "reasoning": item.get("reasoning", ""),
        })
        if has_disclosure:
            ready.append(tid)
        else:
            gaps.append(f"{tid} ({topico['topico']}) — no policy/target/metric identified")
            action_plan.append({
                "priority": 1 if topico["sempre_material"] else 2,
                "action": f"Define a policy, target and metric for {topico['topico']} (ESRS {tid}).",
                "deadline_days": 30 if topico["sempre_material"] else 60,
            })

    total_material = len(material_topics)
    readiness_score = round((len(ready) / total_material) * 100) if total_material else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    if readiness_score >= 85:
        classificacao = "Reporting Ready"
    elif readiness_score >= 50:
        classificacao = "Partial Gaps"
    else:
        classificacao = "Significant Gaps"

    return {
        "classification": classificacao,
        "readiness_score": readiness_score,
        "risk_score": readiness_score,
        "material_topics": material_topics,
        "total_material_topics": total_material,
        "gaps": gaps,
        "action_plan": action_plan,
    }


@router.post("/readiness-check")
async def csrd_readiness(data: dict):
    company = data.get("company", "")
    customer_email = data.get("customer_email", "")
    profile = (
        f"Company: {company}\n"
        f"Employees: {data.get('employees', '')}\n"
        f"Revenue EUR: {data.get('revenue', '')}\n"
        f"Sector: {data.get('sector', '')}\n"
        f"Current sustainability practices/policies: {data.get('current_reporting', 'none stated')}"
    )

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, profile)
    extracao = parsear_json_llm(raw)
    resultado = _pontuar(extracao.get("items", []))

    resumo_prompt = (
        f"Company: {company}\nCSRD readiness score: {resultado['readiness_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary explaining this result in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are a CSRD/ESRS reporting advisor.", resumo_prompt
    )

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": CHECKOUT_URL,
        }
    pdf_buf = gerar_pdf_relatorio("CSRD Double Materiality Assessment", company, resultado, checklist_key="material_topics")
    from fastapi.responses import StreamingResponse
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="CSRD_Double_Materiality_Report.pdf"'})


@router.post("/gap-analysis")
async def csrd_gap(data: dict):
    """Backward compatibility — same engine, kept for existing integrations."""
    return await csrd_readiness(data)
