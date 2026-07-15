from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.config import Settings
from src.orchestrator import Orchestrator
from src.cross_selling import (
    get_next_upgrade,
    get_upsell_plans,
    estimate_monthly_savings,
    get_agent_name,
    get_cross_sell_recommendation,
    get_journey_progress,
    JOURNEY_TRIGGERS,
    AGENT_CHAIN,
)

router = APIRouter()
settings = Settings()
orchestrator = Orchestrator(settings)


@router.get("/chain")
async def get_agent_chain():
    return {
        "chain": [{"id": a, "name": get_agent_name(a)} for a in AGENT_CHAIN],
        "total": len(AGENT_CHAIN),
    }


@router.get("/journeys")
async def list_journeys():
    journeys = {"A": [], "B": [], "C": []}
    for agent_id, trigger in JOURNEY_TRIGGERS.items():
        j = trigger["journey"]
        journeys[j].append({
            "from": agent_id,
            "from_name": get_agent_name(agent_id),
            "from_price": 0,
            "to": trigger["next"],
            "to_name": get_agent_name(trigger["next"]),
            "condition": trigger["trigger_condition"],
            "discount_pct": trigger["discount_pct"],
            "message": trigger["message"],
        })
    return {
        "journeys": [
            {
                "id": k,
                "name": {
                    "A": "RH → Financeiro → Compliance (Microsoft + Salesforce)",
                    "B": "Fiscal → ESG → Carbono (Google Cloud)",
                    "C": "AEC → Regulatório → Microsoft (Co-sell)",
                }.get(k),
                "steps": v,
            }
            for k, v in journeys.items()
        ],
        "total_journeys": 3,
    }


@router.get("/recommend/{tenant_id}")
async def get_recommendations(tenant_id: str, completed_agent: str = Query(default="")):
    tenant_context = _get_tenant_context(tenant_id)

    if completed_agent:
        rec = get_cross_sell_recommendation(completed_agent, tenant_context)
        if rec:
            return {
                "tenant_id": tenant_id,
                "completed_agent": completed_agent,
                "recommendation": rec,
                "notification": {
                    "type": "cross_sell",
                    "title": "Proximo passo recomendado",
                    "body": rec["message"],
                    "cta": f"Ativar {rec['recommended_agent_name']} com {rec['discount_pct']}% de desconto",
                    "urgency": rec["urgency"],
                },
            }

    journey_progress = get_journey_progress(tenant_context)
    return {
        "tenant_id": tenant_id,
        "completed_agent": completed_agent or "none",
        "recommendation": None,
        "journey_progress": journey_progress,
        "message": "Nenhuma recomendacao disponivel no momento. Verifique as jornadas disponiveis.",
    }


@router.get("/upgrade/{current_plan_id}")
async def suggest_upgrade(current_plan_id: str):
    next_plan = get_next_upgrade(current_plan_id)
    if not next_plan:
        return {
            "current_plan": current_plan_id,
            "message": "Voce ja esta no plano maximo disponivel",
            "upgrade_available": False,
        }
    return {
        "current_plan": current_plan_id,
        "upgrade_available": True,
        "next_plan": {
            "id": next_plan["id"],
            "name": next_plan["name"],
            "price": next_plan["price"],
            "price_monthly": next_plan["price"] / 100,
            "agents": [get_agent_name(a) for a in next_plan["agents"]],
            "new_agents": [get_agent_name(a) for a in next_plan["agents"]],
        },
        "savings": {
            "monthly": estimate_monthly_savings(current_plan_id, next_plan["id"]),
        },
    }


@router.get("/upsell/{current_plan_id}")
async def suggest_upsells(current_plan_id: str):
    plans = get_upsell_plans(current_plan_id)
    return {
        "current_plan": current_plan_id,
        "suggestions": [
            {
                "id": p["id"],
                "name": p["name"],
                "price": p["price"],
                "price_monthly": p["price"] / 100,
                "features": p["features"],
            }
            for p in plans
        ],
        "total_suggestions": len(plans),
    }


@router.get("/observability")
async def governance_summary():
    from src.governance import TrustScorer

    scorer = TrustScorer()
    return scorer.get_summary()


def _get_tenant_context(tenant_id: str) -> dict:
    contexts = {
        "default": {
            "employee_count": 0,
            "payroll_data_available": False,
            "salary_data_collected": False,
            "has_employee_data": False,
            "ticket_volume": 0,
            "nf_volume": 0,
            "has_public_contracts": False,
            "revenue": 0,
            "in_public_bidding": False,
            "esg_diagnosis_complete": False,
            "scope_1_2_complete": False,
            "supplier_data_collected": False,
            "has_workers": False,
            "team_growing": False,
            "support_volume_high": False,
            "active_agents": [],
        }
    }
    return contexts.get(tenant_id, contexts["default"])
