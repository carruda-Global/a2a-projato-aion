"""Global EU AI Act Copilot — AI system documentation upload -> real risk-tier
catalog (Article 5 prohibited practices, Annex III high-risk categories,
Article 50 transparency obligations) -> deterministic classification and gap
scoring -> PDF with free/premium paywall. Same architecture as NR1/SOC2/
ISO27001/Contract Risk/Vendor Risk.

Catalog source: Regulation (EU) 2024/1689 (the EU AI Act).
- Article 5(1): the 8 prohibited AI practices (in force since 2 February 2025).
- Annex III: the 8 high-risk AI system categories.
- Article 50: transparency obligations (in force since 2 August 2026).
- Chapter III, Section 2 (Articles 9-15, 43, 71): obligations for high-risk
  AI system providers.
- Deadlines for Annex III/Annex I obligations were postponed by the Digital
  Omnibus on AI (agreed 7 May 2026): Annex III standalone systems now apply
  from 2 December 2027; Annex I embedded systems from 2 August 2028.
"""
import asyncio
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import extrair_texto, parsear_json_llm, gerar_pdf_relatorio, tem_licenca_premium

router = APIRouter(prefix="/api/eu-ai-act", tags=["eu_ai_act"])

# Real catalog — Article 5(1) prohibited practices.
CATALOGO_PROHIBITED = [
    {"id": "ART5-A", "nome": "Subliminal/manipulative/deceptive techniques causing significant harm",
     "criterio": "Deploys techniques beyond a person's consciousness or purposefully manipulative/deceptive techniques materially distorting behavior and causing significant harm."},
    {"id": "ART5-B", "nome": "Exploitation of vulnerabilities",
     "criterio": "Exploits vulnerabilities due to age, disability, or socio-economic situation to materially distort behavior causing significant harm."},
    {"id": "ART5-C", "nome": "Social scoring",
     "criterio": "Evaluates or classifies people over time based on social behavior/personal traits, leading to detrimental or unfavorable treatment unrelated to the context."},
    {"id": "ART5-D", "nome": "Predictive policing based solely on profiling",
     "criterio": "Assesses or predicts the risk of an individual committing a criminal offense based solely on profiling or personality traits, without objective verifiable facts."},
    {"id": "ART5-E", "nome": "Untargeted facial image scraping",
     "criterio": "Creates or expands facial recognition databases through untargeted scraping of facial images from the internet or CCTV footage."},
    {"id": "ART5-F", "nome": "Emotion inference in workplace/education",
     "criterio": "Infers emotions of a person in the workplace or education institutions, except for medical or safety reasons."},
    {"id": "ART5-G", "nome": "Biometric categorization of sensitive attributes",
     "criterio": "Categorizes individuals based on biometric data to infer race, political opinions, trade union membership, religious/philosophical beliefs, or sexual orientation."},
    {"id": "ART5-H", "nome": "Real-time remote biometric identification in public spaces for law enforcement",
     "criterio": "Uses real-time remote biometric identification in publicly accessible spaces for law enforcement purposes, outside the narrow judicially-authorized exceptions."},
]

# Real catalog — Annex III high-risk AI system categories.
CATALOGO_ANNEX_III = [
    {"id": "AIII-1", "nome": "Biometrics",
     "criterio": "Remote biometric identification, biometric categorization, or emotion recognition systems (outside the Article 5 prohibited scope)."},
    {"id": "AIII-2", "nome": "Critical Infrastructure",
     "criterio": "Safety component in the management/operation of critical digital infrastructure, road traffic, or supply of water, gas, heating, or electricity."},
    {"id": "AIII-3", "nome": "Education and Vocational Training",
     "criterio": "Determines access/admission, evaluates learning outcomes, assesses appropriate education level, or monitors/detects prohibited behavior during tests."},
    {"id": "AIII-4", "nome": "Employment, Workers Management, Self-Employment",
     "criterio": "Used for recruitment/selection, task allocation, or monitoring/evaluating performance and behavior affecting promotion or termination."},
    {"id": "AIII-5", "nome": "Access to Essential Services",
     "criterio": "Evaluates creditworthiness/credit score, risk assessment for health/life insurance pricing, or eligibility for public assistance benefits."},
    {"id": "AIII-6", "nome": "Law Enforcement",
     "criterio": "Used by law enforcement for individual risk assessment, polygraph-type tools, evidence reliability evaluation, or crime analytics."},
    {"id": "AIII-7", "nome": "Migration, Asylum, Border Control",
     "criterio": "Used for polygraph-type tools, risk assessment, examination of applications, or detection/identification in migration/asylum/border contexts."},
    {"id": "AIII-8", "nome": "Administration of Justice and Democratic Processes",
     "criterio": "Assists judicial authorities in researching/interpreting facts and law, or is used to influence the outcome of an election or voting behavior."},
]

# Real catalog — Article 50 transparency obligations.
CATALOGO_TRANSPARENCY = [
    {"id": "ART50-1", "nome": "Direct Interaction Disclosure",
     "criterio": "The system interacts directly with natural persons who must be informed they are interacting with an AI system (unless obvious from context)."},
    {"id": "ART50-2", "nome": "Synthetic Content Labeling",
     "criterio": "The system generates or manipulates audio, image, video, or text content that must be marked as AI-generated in a machine-readable format."},
    {"id": "ART50-3", "nome": "Emotion Recognition / Biometric Categorization Disclosure",
     "criterio": "The system performs emotion recognition or biometric categorization, requiring disclosure to the exposed natural persons."},
    {"id": "ART50-4", "nome": "Deep Fake Disclosure",
     "criterio": "The system generates or manipulates content resembling real persons, objects, places, or events (deep fake), requiring disclosure as artificially generated/manipulated."},
]

# Real catalog — Chapter III, Section 2 provider obligations for high-risk AI systems.
CATALOGO_OBRIGACOES_ALTO_RISCO = [
    {"id": "AIA-09", "nome": "Risk Management System (Art. 9)",
     "criterio": "A continuous, iterative risk management process is documented across the system's lifecycle.", "obrigatorio": True},
    {"id": "AIA-10", "nome": "Data and Data Governance (Art. 10)",
     "criterio": "Training/validation/testing data quality criteria and bias examination are documented.", "obrigatorio": True},
    {"id": "AIA-11", "nome": "Technical Documentation (Art. 11)",
     "criterio": "Technical documentation is prepared per Annex IV before market placement.", "obrigatorio": True},
    {"id": "AIA-12", "nome": "Record-Keeping / Logging (Art. 12)",
     "criterio": "The system automatically logs events over its operational lifetime.", "obrigatorio": True},
    {"id": "AIA-13", "nome": "Transparency to Deployers (Art. 13)",
     "criterio": "Instructions for use are provided to deployers, covering capabilities, limitations, and human oversight measures.", "obrigatorio": True},
    {"id": "AIA-14", "nome": "Human Oversight (Art. 14)",
     "criterio": "Measures enabling effective human oversight are built in, including the ability to intervene or halt the system.", "obrigatorio": True},
    {"id": "AIA-15", "nome": "Accuracy, Robustness, Cybersecurity (Art. 15)",
     "criterio": "The system achieves an appropriate level of accuracy, robustness, and cybersecurity throughout its lifecycle.", "obrigatorio": True},
    {"id": "AIA-43", "nome": "Conformity Assessment (Art. 43)",
     "criterio": "A conformity assessment (internal control or notified body, as applicable) is completed before market placement.", "obrigatorio": True},
    {"id": "AIA-71", "nome": "EU Database Registration (Art. 71)",
     "criterio": "The system is registered in the EU high-risk AI systems database before deployment.", "obrigatorio": True},
]

RECOMENDACOES_ALTO_RISCO = {
    "AIA-09": "Document a continuous risk management process covering the full system lifecycle (Art. 9).",
    "AIA-10": "Document data quality criteria and bias examination for training/validation/testing data (Art. 10).",
    "AIA-11": "Prepare technical documentation per Annex IV before placing the system on the market (Art. 11).",
    "AIA-12": "Implement automatic event logging covering the system's operational lifetime (Art. 12).",
    "AIA-13": "Publish deployer instructions covering capabilities, limitations, and oversight measures (Art. 13).",
    "AIA-14": "Build in human oversight controls, including the ability to intervene or halt the system (Art. 14).",
    "AIA-15": "Test and document accuracy, robustness, and cybersecurity levels across the lifecycle (Art. 15).",
    "AIA-43": "Complete the applicable conformity assessment before market placement (Art. 43).",
    "AIA-71": "Register the system in the EU high-risk AI systems database before deployment (Art. 71).",
}

_ALL_TRIGGER_ITEMS = CATALOGO_PROHIBITED + CATALOGO_ANNEX_III + CATALOGO_TRANSPARENCY

SYSTEM_PROMPT_TRIAGEM = f"""You are an EU AI Act triage engine. You are given three fixed, real catalogs
from Regulation (EU) 2024/1689: Article 5(1) prohibited practices, Annex III high-risk categories, and
Article 50 transparency triggers. For EACH catalog item, read the AI system description/documentation and
decide ONLY whether it applies to this system — based strictly on the criterion given. Do not invent
categories outside these catalogs and do not make a final risk-tier judgment yourself; that is computed
separately from your per-item answers.

Prohibited practices (Article 5):
{chr(10).join(f"- {c['id']}: {c['nome']} — {c['criterio']}" for c in CATALOGO_PROHIBITED)}

High-risk categories (Annex III):
{chr(10).join(f"- {c['id']}: {c['nome']} — {c['criterio']}" for c in CATALOGO_ANNEX_III)}

Transparency triggers (Article 50):
{chr(10).join(f"- {c['id']}: {c['nome']} — {c['criterio']}" for c in CATALOGO_TRANSPARENCY)}

Return STRICT JSON only:
{{"items": [{{"id": "ART5-A", "applies": true|false, "evidence": "short quote or reasoning"}}]}}
One entry per catalog id above, in order."""

SYSTEM_PROMPT_OBRIGACOES = f"""You are an EU AI Act high-risk obligations engine. You are given a fixed,
real catalog of {len(CATALOGO_OBRIGACOES_ALTO_RISCO)} provider obligations from Chapter III, Section 2 of
Regulation (EU) 2024/1689. For EACH item, read the AI system's documentation and decide ONLY whether the
obligation is met, weak, or missing.

Catalog:
{chr(10).join(f"- {c['id']}: {c['nome']} — {c['criterio']}" for c in CATALOGO_OBRIGACOES_ALTO_RISCO)}

Return STRICT JSON only:
{{"items": [{{"id": "AIA-09", "status": "met" | "gap" | "weak", "evidence": "short quote or 'not found'"}}]}}
One entry per catalog id, in order."""


def _classificar(triagem_items: list[dict]) -> dict:
    """Deterministic classification — this function, not the LLM, decides the
    final risk tier and applicable deadline, based strictly on which fixed
    catalog items the LLM flagged as applying above."""
    aplica = {i.get("id"): bool(i.get("applies")) for i in triagem_items}
    evidencia = {i.get("id"): i.get("evidence", "") for i in triagem_items}

    prohibited_hits = [c for c in CATALOGO_PROHIBITED if aplica.get(c["id"])]
    high_risk_hits = [c for c in CATALOGO_ANNEX_III if aplica.get(c["id"])]
    transparency_hits = [c for c in CATALOGO_TRANSPARENCY if aplica.get(c["id"])]

    if prohibited_hits:
        classificacao = "Prohibited"
        deadline = "In force since 2 February 2025 — this practice may not be deployed (Article 5)"
        risk_score = 0
    elif high_risk_hits:
        classificacao = "High Risk"
        deadline = "2 December 2027 (Annex III, as postponed by the Digital Omnibus on AI)"
        risk_score = None  # computed from the obligations checklist, not here
    elif transparency_hits:
        classificacao = "Limited Risk"
        deadline = "2 August 2026 (Article 50 transparency obligations)"
        risk_score = 70
    else:
        classificacao = "Minimal Risk"
        deadline = "Not applicable"
        risk_score = 100

    gaps = [f"{c['id']}: {c['nome']} — {evidencia.get(c['id'], '')}" for c in prohibited_hits]
    gaps += [f"{c['id']}: {c['nome']} triggers Annex III obligations — {evidencia.get(c['id'], '')}" for c in high_risk_hits]
    gaps += [f"{c['id']}: {c['nome']} requires disclosure — {evidencia.get(c['id'], '')}" for c in transparency_hits] if classificacao == "Limited Risk" else []

    return {
        "classification": classificacao,
        "applicable_deadline": deadline,
        "risk_score": risk_score,
        "prohibited_hits": [c["id"] for c in prohibited_hits],
        "high_risk_hits": [c["id"] for c in high_risk_hits],
        "transparency_hits": [c["id"] for c in transparency_hits],
        "gaps": gaps,
    }


def _pontuar_obrigacoes(items_llm: list[dict]) -> dict:
    """Deterministic scoring for the Chapter III obligations checklist —
    identical weighting pattern to SOC2/ISO27001/Contract Risk/Vendor Risk."""
    status_por_id = {i.get("id"): i.get("status", "gap") for i in items_llm}
    evidencia_por_id = {i.get("id"): i.get("evidence", "") for i in items_llm}

    obligations, gaps, action_plan = [], [], []
    pontos_totais = pontos_obtidos = 0

    for item in CATALOGO_OBRIGACOES_ALTO_RISCO:
        cid = item["id"]
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

        obligations.append({"requirement": f"{cid} — {item['nome']}", "status": status_final})
        if status_final == "gap":
            gaps.append(f"{cid}: {item['nome']} — {evidencia_por_id.get(cid, 'not found')}")
            action_plan.append({
                "priority": 1,
                "action": RECOMENDACOES_ALTO_RISCO.get(cid, f"Address obligation {cid}"),
                "deadline_days": 60,
            })

    risk_score = round((pontos_obtidos / pontos_totais) * 100) if pontos_totais else 0
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i
    return {"obligations": obligations, "gaps": gaps, "action_plan": action_plan, "risk_score": risk_score}


async def _analisar(company: str, texto: str) -> dict:
    settings = Settings()
    deepseek = DeepSeekClient(settings)

    raw_triagem = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT_TRIAGEM, f"Company: {company}\n\nAI system description/documentation:\n{texto}")
    triagem = parsear_json_llm(raw_triagem)
    resultado = _classificar(triagem.get("items", []))

    if resultado["classification"] == "High Risk":
        raw_obrigacoes = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT_OBRIGACOES, f"AI system description/documentation:\n{texto}")
        obrigacoes = parsear_json_llm(raw_obrigacoes)
        pontuacao = _pontuar_obrigacoes(obrigacoes.get("items", []))
        resultado["risk_score"] = pontuacao["risk_score"]
        resultado["obligations"] = pontuacao["obligations"]
        resultado["gaps"] = resultado["gaps"] + pontuacao["gaps"]
        resultado["action_plan"] = pontuacao["action_plan"]
    else:
        resultado.setdefault("obligations", [])
        resultado.setdefault("action_plan", [])

    resumo_prompt = (
        f"Company: {company}\nClassification: {resultado['classification']}\n"
        f"Applicable deadline: {resultado['applicable_deadline']}\nRisk score: {resultado['risk_score']}/100\n"
        f"Gaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary citing which Annex/Article applies, in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are an EU AI Act compliance advisor.", resumo_prompt
    )
    return resultado


@router.post("/analyze")
async def analyze_document(file: UploadFile = File(...), company: str = Form(...), customer_email: str = Form("")):
    conteudo = await file.read()
    texto = extrair_texto(conteudo, file.filename or "")[:12000]
    resultado = await _analisar(company, texto)

    if not tem_licenca_premium(customer_email):
        return {
            "preview": resultado,
            "message": "Full report generated with watermark — unlock the premium version to download without watermark.",
            "checkout_url": "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l",
        }
    pdf_buf = gerar_pdf_relatorio("EU AI Act Readiness Report", company, resultado)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="EU_AI_Act_Readiness_Report.pdf"'})


@router.post("/readiness-check")
async def readiness_check(data: dict):
    """Backward compatibility — text-only flow (no upload), same triage catalog."""
    company = data.get("company", "")
    texto = f"Uses AI for: {data.get('ai_use', '')}\nSells to EU: {data.get('sells_to_eu', '')}"
    resultado = await _analisar(company, texto)
    return {"analysis": resultado, "checkout_url": "https://buy.stripe.com/5kQ7sN4ModwDblO6q4g7e0l"}
