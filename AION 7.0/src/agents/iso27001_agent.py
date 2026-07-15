"""Global ISO27001 Copilot — questionário estruturado (catálogo real Anexo A) ->
motor de gap relacional -> PDF com paywall free/premium. Mesma arquitetura do NR1/SOC2.

Fonte do catálogo: ISO/IEC 27001:2022, Anexo A (93 controles em 4 temas:
Organizacional 5.1-5.37, Pessoas 6.1-6.8, Físico 7.1-7.14, Tecnológico 8.1-8.34).
"""
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/iso27001", tags=["iso27001"])

# Real catalog — Part 1: 16 representative controls across the 4 Annex A themes.
CATALOGO_ISO27001 = [
    {"id": "5.1", "categoria": "Organizational", "nome": "Policies for Information Security",
     "pergunta": "Is there an information security policy approved by management and communicated?", "obrigatorio": True},
    {"id": "5.2", "categoria": "Organizational", "nome": "Information Security Roles and Responsibilities",
     "pergunta": "Are information security roles and responsibilities clearly defined?", "obrigatorio": True},
    {"id": "5.3", "categoria": "Organizational", "nome": "Segregation of Duties",
     "pergunta": "Is there segregation of duties for conflicting tasks (e.g. approver ≠ executor)?", "obrigatorio": True},
    {"id": "5.15", "categoria": "Organizational", "nome": "Access Control",
     "pergunta": "Is there a formal role/need-based access control policy?", "obrigatorio": True},
    {"id": "5.23", "categoria": "Organizational", "nome": "Information Security for Use of Cloud Services",
     "pergunta": "Is there a formal security evaluation of the cloud providers used?", "obrigatorio": True},
    {"id": "5.24", "categoria": "Organizational", "nome": "Information Security Incident Management Planning",
     "pergunta": "Is there a documented security incident response plan?", "obrigatorio": True},
    {"id": "6.3", "categoria": "People", "nome": "Information Security Awareness, Education and Training",
     "pergunta": "Do employees receive periodic security awareness training?", "obrigatorio": True},
    {"id": "6.7", "categoria": "People", "nome": "Remote Working",
     "pergunta": "Is there a formal remote work policy with specific security controls?", "obrigatorio": False},
    {"id": "7.1", "categoria": "Physical", "nome": "Physical Security Perimeters",
     "pergunta": "Are physical security perimeters defined and protected on premises?", "obrigatorio": True},
    {"id": "7.2", "categoria": "Physical", "nome": "Physical Entry",
     "pergunta": "Is physical access to secure areas controlled (badge, lock, sign-in log)?", "obrigatorio": True},
    {"id": "8.7", "categoria": "Technological", "nome": "Protection Against Malware",
     "pergunta": "Is active antimalware protection deployed on all endpoints and servers?", "obrigatorio": True},
    {"id": "8.8", "categoria": "Technological", "nome": "Management of Technical Vulnerabilities",
     "pergunta": "Is there a process to identify and remediate technical vulnerabilities (patch management)?", "obrigatorio": True},
    {"id": "8.13", "categoria": "Technological", "nome": "Information Backup",
     "pergunta": "Is there regular backup with documented restore testing?", "obrigatorio": True},
    {"id": "8.15", "categoria": "Technological", "nome": "Logging",
     "pergunta": "Are system events logged and retained for a defined period?", "obrigatorio": True},
    {"id": "8.16", "categoria": "Technological", "nome": "Monitoring Activities",
     "pergunta": "Is there active network/system monitoring to detect anomalous behavior?", "obrigatorio": True},
    {"id": "8.24", "categoria": "Technological", "nome": "Use of Cryptography",
     "pergunta": "Is sensitive data encrypted at rest and in transit?", "obrigatorio": True},
]

RECOMENDACOES = {
    "5.1": "Formalize and publish the information security policy, approved by management.",
    "5.2": "Document a RACI matrix of information security roles and responsibilities.",
    "5.3": "Implement segregation between who requests, approves, and executes critical changes/access.",
    "5.15": "Formalize a role-based access control (RBAC) policy.",
    "5.23": "Perform formal security due diligence for each contracted cloud provider.",
    "5.24": "Document an incident response plan with roles, escalation, and communication.",
    "6.3": "Implement a security awareness training program, at least annually.",
    "6.7": "Document a remote work policy with VPN/device/network requirements.",
    "7.1": "Define and physically protect the perimeter of the premises with access controls.",
    "7.2": "Implement physical entry control (badge, biometrics, visitor log).",
    "8.7": "Install and keep antimalware software up to date on all devices.",
    "8.8": "Implement periodic vulnerability scanning with a defined remediation SLA.",
    "8.13": "Configure automated backups with quarterly restore testing.",
    "8.15": "Centralize system logs with a minimum 90-day retention.",
    "8.16": "Deploy a monitoring/SIEM tool with configured alerts.",
    "8.24": "Implement encryption (TLS in transit, AES-256 at rest) for sensitive data.",
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
    return {"framework": "ISO/IEC 27001:2022 (Anexo A)", "perguntas": CATALOGO_ISO27001}


def _avaliar_respostas(respostas: list[RespostaItem]) -> dict:
    catalogo_por_id = {c["id"]: c for c in CATALOGO_ISO27001}
    respostas_por_id = {r.controle_id: r.status for r in respostas}

    obligations, gaps, action_plan = [], [], []
    pontos_totais = pontos_obtidos = 0

    for controle in CATALOGO_ISO27001:
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
                "action": RECOMENDACOES.get(cid, f"Implementar controle {cid}"),
                "deadline_days": 30 if controle["obrigatorio"] else 60,
            })

    risk_score = round((pontos_obtidos / pontos_totais) * 100) if pontos_totais else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    if risk_score >= 85:
        classificacao = "Certification Ready"
    elif risk_score >= 60:
        classificacao = "Partial Compliance"
    else:
        classificacao = "Not Ready"

    return {"classification": classificacao, "risk_score": risk_score,
            "obligations": obligations, "gaps": gaps, "action_plan": action_plan}


@router.post("/avaliar")
async def avaliar(dados: AvaliacaoIn):
    resultado = _avaliar_respostas(dados.respostas)

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    resumo_prompt = (
        f"Company: {dados.company}\nISO 27001 readiness score: {resultado['risk_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are an ISO 27001 certification readiness advisor.", resumo_prompt
    )

    if not tem_licenca_premium(dados.customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l",
        }
    pdf_buf = gerar_pdf_relatorio("ISO/IEC 27001:2022 Gap Analysis Report", dados.company, resultado)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="ISO27001_Gap_Report.pdf"'})


@router.post("/gap-analysis")
async def iso27001_gap_legacy(data: dict):
    """Compatibilidade — fluxo antigo em texto livre."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Company: {data.get('company', '')}\nCurrent security controls: {data.get('current_controls', 'basic')}"
    response = await asyncio.to_thread(
        deepseek.chat, "You are an ISO 27001 ISMS specialist.", prompt
    )
    return {"gap_analysis": response, "checkout_url": "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l"}
