from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import Settings
from src.security import (
    AgentInventory,
    JITPermissionManager,
    CostKillSwitch,
    AuditTrail,
    IntentMonitor,
)

router = APIRouter()

_inventory = AgentInventory()
_jit = JITPermissionManager()
_cost = CostKillSwitch()
_audit = AuditTrail()
_monitor = IntentMonitor()


@router.get("/inventory")
async def get_inventory():
    return {
        "agents": _inventory.get_all(),
        "risk_summary": _inventory.get_risk_summary(),
        "attack_surface": _inventory.get_attack_surface(),
    }


class TokenRequest(BaseModel):
    agent_id: str
    user_id: str
    scopes: list[str]


@router.post("/jit/request")
async def request_jit_token(req: TokenRequest):
    result = _jit.request_token(req.agent_id, req.user_id, req.scopes)
    if not result:
        raise HTTPException(status_code=403, detail="Permissao negada")
    return result


@router.post("/jit/revoke/{agent_id}")
async def revoke_jit_tokens(agent_id: str):
    _jit.revoke_all_for_agent(agent_id)
    return {"status": "revoked", "agent_id": agent_id}


@router.get("/cost/usage")
async def get_cost_usage(agent_id: str | None = None, days: int = 7):
    return _cost.get_usage(agent_id, days)


@router.get("/cost/check/{agent_id}")
async def check_cost(agent_id: str):
    allowed, msg = _cost.check(agent_id)
    return {"allowed": allowed, "message": msg}


class ExecutionRecord(BaseModel):
    agent_id: str
    tokens_input: int
    tokens_output: int


@router.post("/cost/record")
async def record_cost(req: ExecutionRecord):
    _cost.record_execution(req.agent_id, req.tokens_input, req.tokens_output)
    return {"status": "recorded"}


class AuditRecord(BaseModel):
    agent_id: str
    action: str
    user_id: str
    input_summary: str = ""
    output_summary: str = ""


@router.post("/audit/record")
async def record_audit(req: AuditRecord):
    entry = _audit.record(
        req.agent_id, req.action, req.user_id,
        req.input_summary, req.output_summary,
    )
    return entry


@router.get("/audit/chain")
async def get_audit_chain(agent_id: str | None = None, limit: int = 100):
    return {"entries": _audit.get_chain(agent_id, limit)}


@router.get("/audit/verify")
async def verify_audit_chain():
    valid, errors = _audit.verify_chain()
    return {"valid": valid, "errors": errors, "total_entries": len(_audit._chain)}


@router.get("/audit/lgpd/{user_id}")
async def get_lgpd_report(user_id: str):
    return {"entries": _audit.get_lgpd_report(user_id)}


@router.get("/audit/crea")
async def get_crea_report(agent_id: str | None = None):
    return {"entries": _audit.get_crea_report(agent_id)}


@router.get("/monitor/anomalies")
async def get_anomalies(agent_id: str | None = None, severity: str | None = None):
    return {
        "anomalies": _monitor.get_anomalies(agent_id, severity),
        "total": len(_monitor.get_anomalies(agent_id, severity)),
    }


@router.get("/monitor/stats/{agent_id}")
async def get_agent_stats(agent_id: str, days: int = 7):
    return _monitor.get_agent_stats(agent_id, days)


@router.get("/summary")
async def security_summary():
    return {
        "inventory": {
            "total_agents": len(_inventory.get_all()),
            "risk_summary": _inventory.get_risk_summary(),
        },
        "jit": {
            "active_tokens": _jit._active_tokens.__len__(),
        },
        "cost": {
            "global_daily_budget_usd": 50.0,
            "max_per_execution_usd": 1.0,
        },
        "audit": {
            "total_entries": len(_audit._chain),
            "chain_valid": _audit.verify_chain()[0],
        },
        "monitor": {
            "total_anomalies": len(_monitor.get_anomalies()),
        },
    }
