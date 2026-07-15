"""Global Contract Risk Copilot — contract upload -> real clause catalog ->
deterministic gap scoring -> PDF with free/premium paywall.

Same architecture as NR1/SOC2/ISO27001: a fixed, real catalog of standard
commercial-contract clause types (not the LLM inventing what to check for).
The LLM's only job is text extraction — for each catalog item, does the
uploaded contract contain a clause satisfying it, and what evidence supports
that — plus the final executive summary. It never decides the clause
taxonomy or the pass/fail thresholds.

Catalog sources: GDPR Art. 28(3) (processor obligations), LGPD Art. 33
(international data transfer), UNCITRAL Model Law on International
Commercial Arbitration (dispute resolution), ISO 37301:2021 (compliance
management clauses), and standard common-law commercial contract doctrine
(limitation of liability, indemnification, force majeure).
"""
import asyncio
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import extrair_texto, parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/contract-risk", tags=["contract_risk"])

# Real catalog — standard commercial-contract clause types with real legal grounding.
CATALOGO_CONTRACT_CLAUSES = [
    {"id": "CR-01", "categoria": "Liability", "nome": "Limitation of Liability",
     "criterio": "Caps aggregate liability to a defined amount (e.g. fees paid in the prior 12 months) and excludes indirect/consequential damages.",
     "obrigatorio": True},
    {"id": "CR-02", "categoria": "Liability", "nome": "Indemnification",
     "criterio": "Defines which party indemnifies the other for third-party claims (IP infringement, breach, negligence), with a clear trigger and process.",
     "obrigatorio": True},
    {"id": "CR-03", "categoria": "Termination", "nome": "Termination for Cause",
     "criterio": "Allows termination on material breach, with a defined cure period (e.g. 30 days written notice).",
     "obrigatorio": True},
    {"id": "CR-04", "categoria": "Termination", "nome": "Termination for Convenience",
     "criterio": "Allows either party to terminate without cause on reasonable prior notice.",
     "obrigatorio": False},
    {"id": "CR-05", "categoria": "Data Protection", "nome": "Data Processing Agreement (GDPR Art. 28(3))",
     "criterio": "If personal data is processed, includes processor obligations: subject matter/duration of processing, sub-processor authorization, security measures, breach notification, deletion/return of data on termination.",
     "obrigatorio": True},
    {"id": "CR-06", "categoria": "Data Protection", "nome": "International Data Transfer (LGPD Art. 33)",
     "criterio": "If data crosses borders, specifies the legal transfer mechanism (SCCs, adequacy decision, or equivalent LGPD Art. 33 basis).",
     "obrigatorio": False},
    {"id": "CR-07", "categoria": "Confidentiality", "nome": "Confidentiality / Non-Disclosure",
     "criterio": "Defines confidential information, obligations of the receiving party, exclusions, and survival period after termination.",
     "obrigatorio": True},
    {"id": "CR-08", "categoria": "Intellectual Property", "nome": "IP Ownership / Work Product",
     "criterio": "Clearly assigns ownership of pre-existing IP vs. newly created work product/deliverables.",
     "obrigatorio": True},
    {"id": "CR-09", "categoria": "Dispute Resolution", "nome": "Governing Law and Jurisdiction",
     "criterio": "Names the governing law and the competent court or arbitral forum for disputes.",
     "obrigatorio": True},
    {"id": "CR-10", "categoria": "Dispute Resolution", "nome": "Dispute Resolution Mechanism",
     "criterio": "Defines an escalation path (negotiation, mediation, arbitration per UNCITRAL Model Law or equivalent) before litigation.",
     "obrigatorio": False},
    {"id": "CR-11", "categoria": "Risk Allocation", "nome": "Force Majeure",
     "criterio": "Excuses non-performance due to events beyond reasonable control, with a defined notice and mitigation obligation.",
     "obrigatorio": True},
    {"id": "CR-12", "categoria": "Risk Allocation", "nome": "Assignment / Change of Control",
     "criterio": "Restricts assignment of the contract without prior written consent, including on merger/acquisition.",
     "obrigatorio": False},
    {"id": "CR-13", "categoria": "Performance", "nome": "Warranties and Representations",
     "criterio": "States the warranties each party makes (authority to contract, non-infringement, service quality) and the remedy for breach.",
     "obrigatorio": True},
    {"id": "CR-14", "categoria": "Performance", "nome": "Service Levels / Penalty Clause",
     "criterio": "If the contract is for services, defines measurable SLAs with corresponding remedies or penalties for missed targets.",
     "obrigatorio": False},
    {"id": "CR-15", "categoria": "Payment", "nome": "Payment Terms and Late Payment",
     "criterio": "States payment due dates, invoicing process, and consequences of late payment (interest, suspension of services).",
     "obrigatorio": True},
]

RECOMENDACOES = {
    "CR-01": "Add or tighten a liability cap clause (e.g. limited to fees paid in the prior 12 months) and exclude indirect/consequential damages.",
    "CR-02": "Add a mutual indemnification clause covering IP infringement and breach of confidentiality, with a clear notice/defense process.",
    "CR-03": "Add a termination-for-cause clause with a defined written-notice cure period (typically 30 days).",
    "CR-04": "Add a termination-for-convenience clause with a reasonable notice period (e.g. 60-90 days) if early exit flexibility is needed.",
    "CR-05": "Add a GDPR Art. 28(3)-compliant data processing clause covering sub-processors, security measures, breach notification, and data return/deletion.",
    "CR-06": "Add an international data transfer clause specifying the legal basis (Standard Contractual Clauses or LGPD Art. 33 equivalent).",
    "CR-07": "Add or strengthen the confidentiality clause with a clear survival period after termination (typically 2-5 years).",
    "CR-08": "Clarify IP ownership: pre-existing IP stays with its owner, newly created deliverables are assigned/licensed explicitly.",
    "CR-09": "Add a governing law and jurisdiction clause naming a specific law and forum.",
    "CR-10": "Add an escalation clause (negotiation -> mediation -> arbitration) before either party can litigate.",
    "CR-11": "Add a force majeure clause covering events beyond reasonable control with a notice obligation.",
    "CR-12": "Add an assignment restriction clause requiring prior written consent, including on change of control.",
    "CR-13": "Add explicit warranties (authority, non-infringement, service quality) with a defined remedy for breach.",
    "CR-14": "Add measurable SLA targets with corresponding service credits or penalties for missed targets.",
    "CR-15": "Add explicit payment terms: due dates, invoicing cadence, and late payment interest/suspension rights.",
}

SYSTEM_PROMPT = f"""You are a contract analysis engine. You are given a fixed, real catalog of
{len(CATALOGO_CONTRACT_CLAUSES)} standard commercial-contract clause types. For EACH catalog item,
read the contract text and decide ONLY whether it is present and adequate, present but weak, or
missing — based strictly on the criterion given. Do not invent clause types outside this catalog
and do not judge based on your own opinion of what a "good contract" needs.

Catalog:
{chr(10).join(f"- {c['id']} ({c['categoria']}): {c['nome']} — criterion: {c['criterio']}" for c in CATALOGO_CONTRACT_CLAUSES)}

Return STRICT JSON only:
{{"items": [{{"id": "CR-01", "status": "met" | "gap" | "weak", "evidence": "short quote or 'not found'"}}]}}
One entry per catalog id, in order. "weak" means present but missing a required element from the criterion."""


def _pontuar(items_llm: list[dict]) -> dict:
    """Deterministic scoring — Sprint 3 equivalent: compares the LLM's per-item
    extraction against the fixed catalog. The LLM decided presence/absence per
    item above; this function is the only place that decides pass/fail weighting
    and the overall classification, exactly like the SOC2/ISO27001 engines."""
    status_por_id = {i.get("id"): i.get("status", "gap") for i in items_llm}
    evidencia_por_id = {i.get("id"): i.get("evidence", "") for i in items_llm}

    obligations, gaps, action_plan = [], [], []
    pontos_totais = pontos_obtidos = 0

    for clausula in CATALOGO_CONTRACT_CLAUSES:
        cid = clausula["id"]
        status_llm = status_por_id.get(cid, "gap")
        pontos_totais += 1
        if status_llm == "met":
            pontos_obtidos += 1
            status_final = "met"
        elif status_llm == "weak":
            pontos_obtidos += 0.5
            status_final = "gap"
        else:
            status_final = "gap"

        obligations.append({"requirement": f"{cid} — {clausula['nome']}", "status": status_final})
        if status_final == "gap":
            gaps.append(f"{cid} ({clausula['categoria']}): {clausula['nome']} — {evidencia_por_id.get(cid, 'not found')}")
            action_plan.append({
                "priority": 1 if clausula["obrigatorio"] else 2,
                "action": RECOMENDACOES.get(cid, f"Add clause {cid}"),
                "deadline_days": 15 if clausula["obrigatorio"] else 30,
            })

    risk_score = round((pontos_obtidos / pontos_totais) * 100) if pontos_totais else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    if risk_score >= 85:
        classificacao = "Low Risk"
    elif risk_score >= 60:
        classificacao = "Medium Risk"
    else:
        classificacao = "High Risk"

    return {"classification": classificacao, "risk_score": risk_score,
            "obligations": obligations, "gaps": gaps, "action_plan": action_plan}


@router.post("/analyze")
async def analyze_document(file: UploadFile = File(...), company: str = Form(...), customer_email: str = Form("")):
    conteudo = await file.read()
    texto = extrair_texto(conteudo, file.filename or "")[:12000]

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, f"Contract content:\n{texto}")
    extracao = parsear_json_llm(raw)
    resultado = _pontuar(extracao.get("items", []))

    resumo_prompt = (
        f"Company: {company}\nContract risk score: {resultado['risk_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary explaining this result in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are a commercial contract risk advisor.", resumo_prompt
    )

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l",
        }
    pdf_buf = gerar_pdf_relatorio("Contract Risk Analysis Report", company, resultado)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="Contract_Risk_Report.pdf"'})


@router.post("/dpa-check")
async def dpa_compliance_check(data: dict):
    """Backward compatibility — quick DPA check without upload, scoped to the CR-05/CR-06 catalog items."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Check this Data Processing Agreement text against GDPR Art. 28(3) and LGPD Art. 33 "
        f"requirements (sub-processor authorization, security measures, breach notification, "
        f"data return/deletion, international transfer basis). Text: {data.get('dpa_text', '')}\n"
        "List any missing mandatory clauses."
    )
    response = await asyncio.to_thread(deepseek.chat, "You are a data protection contract specialist.", prompt)
    return {"dpa_analysis": response}
