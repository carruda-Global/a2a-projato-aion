"""Global Vendor Risk Copilot — vendor questionnaire/certification upload ->
real risk criteria catalog -> deterministic gap scoring -> PDF with
free/premium paywall. Same architecture as NR1/SOC2/ISO27001/Contract Risk.

Catalog sources: NIST SP 800-161 Rev. 1 (Cybersecurity Supply Chain Risk
Management Practices), ISO/IEC 27036-2:2014 (supplier relationship
security), Shared Assessments SIG (Standardized Information Gathering)
questionnaire domains, GDPR Art. 28 (sub-processor obligations), and
ISO 22301:2019 (business continuity management).
"""
import asyncio
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import extrair_texto, parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/vendor-risk", tags=["vendor_risk"])

# Real catalog — vendor risk criteria across the standard SIG/NIST 800-161 domains.
CATALOGO_VENDOR_RISK = [
    {"id": "VR-01", "categoria": "Certifications", "nome": "SOC 2 or ISO 27001 Certification",
     "criterio": "Vendor holds a current SOC 2 Type II report or ISO/IEC 27001 certificate covering the service in scope.",
     "obrigatorio": True},
    {"id": "VR-02", "categoria": "Cybersecurity", "nome": "Vulnerability and Patch Management",
     "criterio": "Vendor documents a regular vulnerability scanning cadence and a defined patch/remediation SLA (NIST SP 800-161).",
     "obrigatorio": True},
    {"id": "VR-03", "categoria": "Cybersecurity", "nome": "Incident Response and Breach Notification",
     "criterio": "Vendor has a documented incident response plan with a defined breach notification timeline to customers.",
     "obrigatorio": True},
    {"id": "VR-04", "categoria": "Cybersecurity", "nome": "Access Control and Encryption",
     "criterio": "Vendor enforces role-based access control and encrypts customer data at rest and in transit.",
     "obrigatorio": True},
    {"id": "VR-05", "categoria": "Data Handling", "nome": "Sub-processor Disclosure (GDPR Art. 28)",
     "criterio": "Vendor discloses and authorizes sub-processors, with contractual flow-down of data protection obligations.",
     "obrigatorio": True},
    {"id": "VR-06", "categoria": "Data Handling", "nome": "Data Retention and Deletion",
     "criterio": "Vendor documents data retention periods and a data deletion/return process upon contract termination.",
     "obrigatorio": True},
    {"id": "VR-07", "categoria": "Financial Stability", "nome": "Financial Health Disclosure",
     "criterio": "Vendor provides evidence of financial stability (audited financials, credit rating, or years in operation) sufficient to assess going-concern risk.",
     "obrigatorio": False},
    {"id": "VR-08", "categoria": "Concentration Risk", "nome": "Single Point of Failure / Dependency",
     "criterio": "Assessment identifies whether this vendor is a single point of failure for a critical business process, and whether an alternative exists.",
     "obrigatorio": True},
    {"id": "VR-09", "categoria": "Business Continuity", "nome": "Business Continuity / Disaster Recovery (ISO 22301)",
     "criterio": "Vendor documents a business continuity plan with a defined RTO/RPO and evidence of periodic testing.",
     "obrigatorio": True},
    {"id": "VR-10", "categoria": "Regulatory Compliance", "nome": "Applicable Regulatory Compliance",
     "criterio": "Vendor demonstrates compliance with regulations applicable to the data/service in scope (LGPD, GDPR, HIPAA, PCI-DSS as relevant).",
     "obrigatorio": True},
    {"id": "VR-11", "categoria": "Contractual Protections", "nome": "Right to Audit",
     "criterio": "Contract grants the customer (or a designated third party) the right to audit the vendor's security controls periodically.",
     "obrigatorio": False},
    {"id": "VR-12", "categoria": "Contractual Protections", "nome": "Liability and Indemnification",
     "criterio": "Contract defines liability caps and indemnification specific to data breach or security failure scenarios.",
     "obrigatorio": True},
    {"id": "VR-13", "categoria": "ESG", "nome": "ESG / Ethical Sourcing Disclosure",
     "criterio": "Vendor discloses basic ESG practices (labor standards, environmental policy, anti-corruption commitments) where relevant to the engagement.",
     "obrigatorio": False},
]

RECOMENDACOES = {
    "VR-01": "Request the vendor's current SOC 2 Type II report or ISO 27001 certificate before onboarding.",
    "VR-02": "Require evidence of a vulnerability scanning cadence and a defined patch remediation SLA.",
    "VR-03": "Require a documented incident response plan with a breach notification timeline (e.g. 72 hours).",
    "VR-04": "Require documented RBAC and encryption (TLS in transit, AES-256 at rest) for customer data.",
    "VR-05": "Require sub-processor disclosure and contractual flow-down of data protection obligations.",
    "VR-06": "Require documented data retention limits and a deletion/return process at contract end.",
    "VR-07": "Request audited financials, a credit rating, or evidence of years in operation.",
    "VR-08": "Document a contingency plan or alternative vendor if this is a single point of failure.",
    "VR-09": "Require a business continuity plan with defined RTO/RPO and evidence of periodic DR testing.",
    "VR-10": "Confirm compliance evidence for every regulation applicable to the data/service in scope.",
    "VR-11": "Negotiate a right-to-audit clause with a defined frequency (e.g. annual).",
    "VR-12": "Negotiate liability caps and indemnification specific to data breach scenarios.",
    "VR-13": "Request an ESG/ethical sourcing disclosure if relevant to the engagement scope.",
}

SYSTEM_PROMPT = f"""You are a vendor risk assessment engine. You are given a fixed, real catalog of
{len(CATALOGO_VENDOR_RISK)} standard vendor risk criteria. For EACH catalog item, read the vendor's
questionnaire/certification documents and decide ONLY whether the criterion is met, weak, or missing —
based strictly on the criterion given. Do not invent criteria outside this catalog.

Catalog:
{chr(10).join(f"- {c['id']} ({c['categoria']}): {c['nome']} — criterion: {c['criterio']}" for c in CATALOGO_VENDOR_RISK)}

Return STRICT JSON only:
{{"items": [{{"id": "VR-01", "status": "met" | "gap" | "weak", "evidence": "short quote or 'not found'"}}]}}
One entry per catalog id, in order. "weak" means partially addressed but missing a required element."""


def _pontuar(items_llm: list[dict]) -> dict:
    """Deterministic scoring engine — mirrors SOC2/ISO27001/Contract Risk. The LLM
    only extracted presence/absence per fixed catalog item above; this function
    is the only place that decides weighting and the final classification."""
    status_por_id = {i.get("id"): i.get("status", "gap") for i in items_llm}
    evidencia_por_id = {i.get("id"): i.get("evidence", "") for i in items_llm}

    obligations, gaps, action_plan = [], [], []
    pontos_totais = pontos_obtidos = 0

    for criterio in CATALOGO_VENDOR_RISK:
        cid = criterio["id"]
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

        obligations.append({"requirement": f"{cid} — {criterio['nome']}", "status": status_final})
        if status_final == "gap":
            gaps.append(f"{cid} ({criterio['categoria']}): {criterio['nome']} — {evidencia_por_id.get(cid, 'not found')}")
            action_plan.append({
                "priority": 1 if criterio["obrigatorio"] else 2,
                "action": RECOMENDACOES.get(cid, f"Address criterion {cid}"),
                "deadline_days": 30 if criterio["obrigatorio"] else 60,
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
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, f"Vendor: {company}\n\nDocument content:\n{texto}")
    extracao = parsear_json_llm(raw)
    resultado = _pontuar(extracao.get("items", []))

    resumo_prompt = (
        f"Vendor: {company}\nVendor risk score: {resultado['risk_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary explaining this result in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are a third-party vendor risk advisor.", resumo_prompt
    )

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l",
        }
    pdf_buf = gerar_pdf_relatorio("Vendor Risk Assessment Report", company, resultado)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="Vendor_Risk_Report.pdf"'})


@router.post("/portfolio-scan")
async def scan_portfolio(data: dict):
    """Backward compatibility — quick multi-vendor scan without upload, scoped to the fixed catalog."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    vendors = data.get("vendors", [])
    prompt = (
        f"Run a portfolio risk scan for {len(vendors)} vendors against these standard criteria "
        f"(certifications, cybersecurity posture, data handling, financial stability, concentration risk, "
        f"business continuity): {vendors}\nIdentify the top 3 critical risks."
    )
    response = await asyncio.to_thread(deepseek.chat, "You are a third-party vendor risk advisor.", prompt)
    return {"portfolio_scan": response, "vendors_assessed": len(vendors)}
