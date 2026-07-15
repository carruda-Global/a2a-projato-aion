from fastapi import APIRouter, Request
from src.config import get_settings
from src.database.supabase_client import SupabaseClient
import logging

router = APIRouter(prefix="/api/stripe", tags=["stripe_app"])
logger = logging.getLogger(__name__)

OBRIGACOES_BRASIL = [
    {"id": "nr1_psicossocial", "nome": "NR-1 Psicossocial", "norma": "Portaria MTE 1.419/2024", "multa": "Interdição + autuação", "peso": 25, "plano": "Compliance Essencial", "preco": "R$ 590/mês", "price_id": "price_1TlxVVQn4rfjkSvEpiBqaCSf"},
    {"id": "lgpd_operacional", "nome": "LGPD Operacional", "norma": "Lei 13.709/2018", "multa": "Até R$ 50M", "peso": 25, "plano": "Compliance Essencial", "preco": "R$ 590/mês", "price_id": "price_1TlxVVQn4rfjkSvEpiBqaCSf"},
    {"id": "igualdade_salarial", "nome": "Igualdade Salarial", "norma": "Lei 14.611/2023", "multa": "R$ 140,6/func/dia", "peso": 20, "plano": "Regulatory Pro", "preco": "R$ 1.490/mês", "price_id": "price_1TlxVVQn4rfjkSvEam443ZCP"},
    {"id": "canal_denuncias", "nome": "Canal de Denúncias", "norma": "Lei 14.457/2022", "multa": "Irregularidade trabalhista", "peso": 15, "plano": "Regulatory Pro", "preco": "R$ 1.490/mês", "price_id": "price_1TlxVVQn4rfjkSvEam443ZCP"},
    {"id": "tributario_cbs_ibs", "nome": "CBS/IBS Tributário", "norma": "LC 214/2025", "multa": "Passivo fiscal", "peso": 15, "plano": "Tributário CBS/IBS", "preco": "R$ 390/mês", "price_id": "price_CBS_IBS"},
]


@router.post("/compliance-score")
async def get_compliance_score(request: Request):
    data = await request.json()
    stripe_account_id = data.get("stripe_account_id", "")
    email = data.get("email", "")

    tenant = None
    try:
        db = SupabaseClient(get_settings())
        result = db.client.table("tenants").select("*").eq("email", email).execute()
        tenant = result.data[0] if result.data else None
    except Exception:
        pass

    agentes_ativos = tenant.get("agentes_ativos", []) if tenant else []
    score = 0
    obrigacoes = []
    plano_recomendado = "Compliance Essencial"
    link_ativacao = "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"

    for ob in OBRIGACOES_BRASIL:
        if ob["id"] in agentes_ativos:
            score += ob["peso"]
            obrigacoes.append({"nome": ob["nome"], "status": "ok", "norma": ob["norma"]})
        else:
            obrigacoes.append({"nome": ob["nome"], "status": "critico", "multa": ob["multa"], "norma": ob["norma"]})
            plano_recomendado = ob["plano"]
            link_ativacao = f"https://buy.stripe.com/{ob['price_id'].split('_')[-1]}"

    nivel = "Excelente" if score >= 80 else "Bom" if score >= 60 else "Regular" if score >= 40 else "Crítico"

    try:
        db = SupabaseClient(get_settings())
        db.client.table("leads").insert({
            "source": "stripe_app", "email": email,
            "stripe_account_id": stripe_account_id,
            "compliance_score": score, "plano_recomendado": plano_recomendado,
        }).execute()
    except Exception:
        pass

    return {
        "score": score, "nivel": nivel, "obrigacoes": obrigacoes,
        "plano_recomendado": plano_recomendado, "link_ativacao": link_ativacao,
        "agentes_ativos": len(agentes_ativos), "total_obrigacoes": len(OBRIGACOES_BRASIL),
    }
