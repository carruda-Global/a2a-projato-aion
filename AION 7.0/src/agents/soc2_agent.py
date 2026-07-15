"""Global SOC2 Copilot — structured questionnaire (real AICPA TSC catalog) ->
deterministic gap engine -> PDF with free/premium paywall.

Same architecture as NR1: real catalog (not the LLM guessing controls),
closed questionnaire, deterministic decision engine. LLM only writes the
executive summary text, never decides the gap.

Catalog source: AICPA Trust Services Criteria 2017 (rev. 2022).
All-English product — international/US market.
"""
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/soc2", tags=["soc2"])

# Real catalog — Part 1 of the 33 Common Criteria (the 9 anchor CCs + A1.2).
CATALOGO_SOC2 = [
    {"id": "CC1.1", "categoria": "Control Environment", "nome": "Integrity and Ethical Values",
     "pergunta": "Is there a formalized code of conduct/ethics communicated to employees?", "obrigatorio": True},
    {"id": "CC2.1", "categoria": "Communication and Information", "nome": "Security Information Communication",
     "pergunta": "Is there a documented and communicated information security policy?", "obrigatorio": True},
    {"id": "CC3.1", "categoria": "Risk Assessment", "nome": "Risk Assessment Objectives",
     "pergunta": "Is there a documented, formal risk assessment process?", "obrigatorio": True},
    {"id": "CC4.1", "categoria": "Monitoring Activities", "nome": "Ongoing and Independent Evaluations",
     "pergunta": "Are periodic internal audits or independent evaluations of controls performed?", "obrigatorio": True},
    {"id": "CC5.1", "categoria": "Control Activities", "nome": "Control Activity Selection and Development",
     "pergunta": "Are documented controls mapped to the identified risks?", "obrigatorio": True},
    {"id": "CC6.1", "categoria": "Logical and Physical Access Controls", "nome": "Logical Access Controls",
     "pergunta": "Is logical access control (firewall, VPN, authentication) documented?", "obrigatorio": True},
    {"id": "CC6.2", "categoria": "Logical and Physical Access Controls", "nome": "Access Provisioning and Deprovisioning",
     "pergunta": "Is there a formal onboarding/offboarding process for system access?", "obrigatorio": True},
    {"id": "CC6.3", "categoria": "Logical and Physical Access Controls", "nome": "Access Privilege Management",
     "pergunta": "Is access granted by role/function with periodic privilege review?", "obrigatorio": True},
    {"id": "CC7.1", "categoria": "System Operations", "nome": "Vulnerability Detection",
     "pergunta": "Is a vulnerability scanning tool run periodically?", "obrigatorio": True},
    {"id": "CC7.2", "categoria": "System Operations", "nome": "Security Event Monitoring",
     "pergunta": "Is there a SIEM or security event monitoring tool in place?", "obrigatorio": True},
    {"id": "CC8.1", "categoria": "Change Management", "nome": "Change Management",
     "pergunta": "Is there a formal change management process (approval, testing, deployment)?", "obrigatorio": True},
    {"id": "CC9.1", "categoria": "Risk Mitigation", "nome": "Business Risk Mitigation",
     "pergunta": "Is there a documented business continuity / incident response plan?", "obrigatorio": True},
    {"id": "A1.2", "categoria": "Availability", "nome": "Capacity and Availability Monitoring",
     "pergunta": "Is there automated backup and a tested disaster recovery plan?", "obrigatorio": False},
]

RECOMENDACOES = {
    "CC1.1": "Formalize a code of conduct and collect signed acknowledgment from all employees annually.",
    "CC2.1": "Document and publish the information security policy, reviewed at least annually.",
    "CC3.1": "Implement an at-least-annual risk assessment process with a risk register and mitigation tracking.",
    "CC4.1": "Schedule quarterly or semi-annual internal audits of critical controls.",
    "CC5.1": "Map each existing control to the corresponding risk identified in the risk assessment.",
    "CC6.1": "Implement MFA, VPN, and formally documented network segmentation.",
    "CC6.2": "Create a formal onboarding/offboarding checklist with approval and access logging.",
    "CC6.3": "Implement quarterly access reviews based on the principle of least privilege.",
    "CC7.1": "Set up automated vulnerability scanning (e.g. weekly) with a remediation report.",
    "CC7.2": "Deploy a SIEM/log monitoring tool with configured alerts.",
    "CC8.1": "Document a change management workflow with approval, test environment, and rollback.",
    "CC9.1": "Draft a business continuity plan (BCP) and test it at least annually.",
    "A1.2": "Configure automated backups with periodic restore testing (DR drill).",
}


class RespostaItem(BaseModel):
    controle_id: str
    status: str  # 'implementado' | 'parcial' | 'ausente' | 'nao_aplicavel'


class AvaliacaoIn(BaseModel):
    company: str
    respostas: list[RespostaItem]
    customer_email: str = ""


@router.get("/questionario")
async def obter_questionario():
    """NR1's Sprint 2 equivalent: closed questions, real catalog, no AI."""
    return {"framework": "SOC 2 (AICPA TSC 2017, rev. 2022)", "perguntas": CATALOGO_SOC2}


def _avaliar_respostas(respostas: list[RespostaItem]) -> dict:
    """Decision engine — Sprint 3: deterministic comparison against the real
    catalog. LLM is never used to decide the gap, only to write the summary."""
    respostas_por_id = {r.controle_id: r.status for r in respostas}

    obligations = []
    gaps = []
    action_plan = []
    pontos_totais = 0
    pontos_obtidos = 0

    for controle in CATALOGO_SOC2:
        cid = controle["id"]
        status_resposta = respostas_por_id.get(cid, "ausente")
        pontos_totais += 1
        if status_resposta == "implementado":
            pontos_obtidos += 1
            status_final = "met"
        elif status_resposta == "parcial":
            pontos_obtidos += 0.5
            status_final = "gap"
        elif status_resposta == "nao_aplicavel":
            pontos_totais -= 1
            status_final = "met"
        else:
            status_final = "gap"

        obligations.append({"requirement": f"{cid} — {controle['nome']}", "status": status_final})

        if status_final == "gap":
            gaps.append(f"{cid} ({controle['categoria']}): {controle['nome']}")
            action_plan.append({
                "priority": 1 if controle["obrigatorio"] else 2,
                "action": RECOMENDACOES.get(cid, f"Implement control {cid}"),
                "deadline_days": 30 if controle["obrigatorio"] else 60,
            })

    risk_score = round((pontos_obtidos / pontos_totais) * 100) if pontos_totais else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    if risk_score >= 85:
        classificacao = "Type I Ready"
    elif risk_score >= 60:
        classificacao = "Partial Compliance"
    else:
        classificacao = "Not Ready"

    return {
        "classification": classificacao,
        "risk_score": risk_score,
        "obligations": obligations,
        "gaps": gaps,
        "action_plan": action_plan,
    }


@router.post("/avaliar")
async def avaliar(dados: AvaliacaoIn):
    """NR1's Sprint 4 equivalent: real engine + PDF. AI only writes the executive summary."""
    resultado = _avaliar_respostas(dados.respostas)

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    resumo_prompt = (
        f"Company: {dados.company}\nSOC2 readiness score: {resultado['risk_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary explaining this result in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are a SOC2 audit readiness advisor.", resumo_prompt
    )

    if not tem_licenca_premium(dados.customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l",
        }
    pdf_buf = gerar_pdf_relatorio("SOC 2 Readiness Report", dados.company, resultado)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="SOC2_Readiness_Report.pdf"'})


@router.post("/readiness-assessment")
async def soc2_assessment_legacy(data: dict):
    """Backward compatibility — old free-text flow, no catalog."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Company: {data.get('company', '')}\nCurrent controls: {data.get('current_controls', 'unknown')}"
    response = await asyncio.to_thread(
        deepseek.chat, "You are a SOC2 audit preparation specialist.", prompt
    )
    return {"assessment": response, "checkout_url": "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l"}
