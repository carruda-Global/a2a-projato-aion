import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Mapa: número do agente no plano → registry ID
AGENT_NUMBER_MAP = {
    "#1": "spec_analyst", "#2": "procurement", "#3": "inventory",
    "#4": "logistics", "#5": "field_execution", "#6": "bim_coordinator",
    "#7": "requirements_analyst", "#8": "engineering_assistant",
    "#9": "work_synopsis", "#10": "photo_intelligence", "#11": "rfi_creation",
    "#12": "compliance", "#13": "nr1_psicossocial", "#14": "tributario_cbs_ibs",
    "#15": "lgpd_operacional", "#16": "esg_ifrs", "#17": "inventario_carbono",
    "#18": "escopo3_fornecedores", "#19": "canal_denuncias",
    "#20": "igualdade_salarial", "#21": "compliance_anticorrupcao",
    "#22": "regulatory_analyst", "#23": "compliance_pm", "#24": "channel_agent",
    "#25": "knowledge_agent", "#26": "facilitator_agent",
    "#27": "dev_experience", "#31": "dynamics_sales", "#32": "dynamics_finance",
    "#33": "dynamics_supply_chain", "#34": "dynamics_hr",
    "#35": "dynamics_customer_service", "#36": "power_bi_compliance",
    "#49": "master_orchestrator",
    "#50": "cross_platform_bridge", "#51": "regulatory_watch",
    "#52": "client_intelligence", "#53": "quality_critic",
    "#54": "meta_learning", "#55": "ecosystem_evolution",
    "#56": "federated_knowledge", "#57": "software_engineering",
    "#58": "sales_agent", "#59": "workforce_orchestrator",
    "#60": "universal_governance_layer", "#61": "antigravity_bridge",
    "#62": "mai_code_reviewer", "#63": "physical_ai_connector",
    "#64": "voice_receptionist",
    "N1": "onboarding_funcionarios", "N2": "atendimento_cliente_ptbr",
    "N3": "conciliacao_financeira",
}

# Todos os IDs de agentes registrados (para expansão de "all_71")
ALL_AGENT_IDS = sorted(set(AGENT_NUMBER_MAP.values()))


def resolve_plan_agents(plan_agents: list[str]) -> list[str]:
    """Expande referências de agentes do plano para registry IDs."""
    resolved = []
    for ref in plan_agents:
        if ref == "all_71":
            resolved.extend(ALL_AGENT_IDS)
        elif ref in AGENT_NUMBER_MAP:
            resolved.append(AGENT_NUMBER_MAP[ref])
        else:
            resolved.append(ref)
    return sorted(set(resolved))

_active_subscriptions: dict[str, dict] = {}
_supabase = None


def _init_supabase():
    global _supabase
    if _supabase is not None:
        return _supabase
    try:
        from supabase import create_client
        from src.config import get_settings
        s = get_settings()
        if s.supabase_url and s.supabase_api_key:
            _supabase = create_client(s.supabase_url, s.supabase_api_key)
            _supabase.table("subscriptions").select("id").limit(1).execute()
            logger.info("Supabase conectado para subscriptions")
        else:
            logger.warning("Supabase nao configurado, usando memoria")
    except Exception as e:
        logger.warning("Supabase indisponivel para subscriptions: %s. Usando memoria.", e)
        _supabase = False
    return _supabase


def activate_subscription(
    source: str,
    external_id: str,
    customer_id: str,
    plan_id: str,
    customer_email: str = "",
    customer_name: str = "",
) -> dict:
    sub_id = f"{source}_{external_id}"
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "subscription_id": sub_id,
        "source": source,
        "external_id": external_id,
        "customer_id": customer_id,
        "customer_email": customer_email,
        "customer_name": customer_name,
        "plan_id": plan_id,
        "status": "active",
        "activated_at": now,
    }

    _active_subscriptions[sub_id] = record

    db = _init_supabase()
    if db:
        try:
            db.table("subscriptions").upsert({
                "id": sub_id,
                "source": source,
                "external_id": external_id,
                "customer_id": customer_id,
                "customer_email": customer_email,
                "customer_name": customer_name,
                "plan_id": plan_id,
                "status": "active",
                "activated_at": now,
            }, on_conflict="id").execute()
        except Exception as e:
            logger.warning("Falha ao salvar subscription no Supabase: %s", e)

    logger.info("Assinatura ativada: source=%s sub=%s customer=%s plan=%s", source, sub_id, customer_id, plan_id)
    return record


def deactivate_subscription(source: str, external_id: str) -> bool:
    sub_id = f"{source}_{external_id}"
    sub = _active_subscriptions.get(sub_id)
    if sub:
        sub["status"] = "cancelled"
        sub["cancelled_at"] = datetime.now(timezone.utc).isoformat()

    db = _init_supabase()
    if db:
        try:
            db.table("subscriptions").update({
                "status": "cancelled",
                "cancelled_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", sub_id).execute()
        except Exception as e:
            logger.warning("Falha ao atualizar subscription no Supabase: %s", e)

    logger.info("Assinatura cancelada: %s", sub_id)
    return True


def get_subscription(source: str, external_id: str) -> dict | None:
    """In-memory cache is populated live by webhooks but is wiped on every
    deploy/restart. Fall back to Supabase (the durable source of truth) by
    customer_email so a real customer isn't locked out just because the
    process restarted since their checkout."""
    cached = _active_subscriptions.get(f"{source}_{external_id}")
    if cached:
        return cached

    db = _init_supabase()
    if not db:
        return None
    try:
        resp = (
            db.table("subscriptions")
            .select("*")
            .eq("customer_email", external_id.strip().lower())
            .eq("status", "active")
            .limit(1)
            .execute()
        )
    except Exception as e:
        logger.warning("Falha ao consultar subscription no Supabase: %s", e)
        return None
    if not resp.data:
        return None
    row = resp.data[0]
    return {
        "subscription_id": row.get("id"),
        "source": row.get("source"),
        "external_id": row.get("external_id"),
        "customer_id": row.get("customer_id"),
        "customer_email": row.get("customer_email"),
        "customer_name": row.get("customer_name"),
        "plan_id": row.get("plan_id"),
        "status": row.get("status"),
        "activated_at": row.get("activated_at"),
    }


def list_active_subscriptions() -> list[dict]:
    return [s for s in _active_subscriptions.values() if s["status"] == "active"]


def get_subscription_by_id(subscription_id: str) -> dict | None:
    return _active_subscriptions.get(subscription_id)


def query_active_subscriptions_supabase() -> list[dict]:
    """Busca assinaturas ativas no Supabase com planos e agentes."""
    from src.monetization.plans import get_plan

    db = _init_supabase()
    if not db:
        return []

    try:
        resp = db.table("subscriptions").select("*").eq("status", "active").execute()
        subscriptions = resp.data or []
    except Exception as e:
        logger.warning("Falha ao consultar subscriptions no Supabase: %s", e)
        return []

    result = []
    for sub in subscriptions:
        plan = get_plan(sub.get("plan_id", ""))
        agent_refs = plan.get("agents", []) if plan else []
        agent_ids = resolve_plan_agents(agent_refs) if agent_refs else []
        result.append({
            "id": sub["id"],
            "source": sub.get("source", ""),
            "customer_email": sub.get("customer_email", ""),
            "customer_name": sub.get("customer_name", ""),
            "customer_id": sub.get("customer_id", ""),
            "plan_id": sub.get("plan_id", ""),
            "plan_name": plan.get("name", "") if plan else "",
            "plan_price_brl": plan.get("price_brl", 0) if plan else 0,
            "status": sub.get("status", ""),
            "activated_at": sub.get("activated_at", ""),
            "agents": agent_ids,
            "agent_count": len(agent_ids),
        })

    return result


def update_subscription_plan(source: str, external_id: str, new_plan_id: str) -> dict | None:
    sub = get_subscription(source, external_id)
    if sub:
        sub["plan_id"] = new_plan_id
        db = _init_supabase()
        if db:
            try:
                db.table("subscriptions").update({"plan_id": new_plan_id}).eq("id", f"{source}_{external_id}").execute()
            except Exception as e:
                logger.warning("Falha ao atualizar plano no Supabase: %s", e)
        logger.info("Plano atualizado: source=%s sub=%s new_plan=%s", source, f"{source}_{external_id}", new_plan_id)
    return sub
