from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.security.aip import AIPRegistry, AIPProxy, AgentIdentity
from src.security.aip.token import PrincipalToken
from src.security.aip.revocation import RevocationManager

router = APIRouter(prefix="/api/aip", tags=["aip-security"])

_registry = AIPRegistry()
_identity = AgentIdentity(_registry)
_proxy = AIPProxy(_registry)
_token_manager = PrincipalToken(_registry, _identity)
_revocation = RevocationManager(_registry)


class ToolCallRequest(BaseModel):
    agent_id: str
    tool: str
    args: dict
    signature: str | None = None
    token_id: str | None = None


class AgentRegistrationRequest(BaseModel):
    agent_name: str
    principal: str


class TokenIssueRequest(BaseModel):
    delegator_name: str
    delegate_name: str
    principal: str
    ttl_hours: int = 24


class RevocationRequest(BaseModel):
    agent_id: str
    reason: str = "security_incident"
    cascade: bool = True


@router.post("/register")
async def register_agent(req: AgentRegistrationRequest):
    record = _registry.register_agent(req.agent_name, req.principal)
    return {"status": "registered", "agent_id": record["agent_id"]}


@router.post("/intercept")
async def intercept_tool_call(req: ToolCallRequest):
    if req.token_id:
        token = _token_manager.verify_token(req.token_id)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        chain_valid = _token_manager.validate_chain_permissions(token)
        if not chain_valid["valid"]:
            raise HTTPException(status_code=403, detail=chain_valid["violation"])

    signature_bytes = bytes.fromhex(req.signature) if req.signature else None

    result = _proxy.intercept_tool_call(
        req.agent_id, req.tool, req.args, signature_bytes
    )

    if result["status"] == "deny":
        raise HTTPException(status_code=403, detail=result)

    return result


@router.post("/token/issue")
async def issue_token(req: TokenIssueRequest):
    token = _token_manager.issue_token(
        req.delegator_name, req.delegate_name, req.principal, req.ttl_hours
    )
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Cannot issue token: delegation not authorized",
        )
    return {"status": "issued", "token": token}


@router.post("/token/verify")
async def verify_token(data: dict):
    token_id = data.get("token_id", "")
    token = _token_manager.verify_token(token_id)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"status": "valid", "token": token}


@router.post("/revoke")
async def revoke_agent(req: RevocationRequest):
    result = _revocation.revoke(req.agent_id, req.reason, req.cascade)
    return result


@router.post("/revoke/emergency")
async def emergency_shutdown():
    result = _revocation.emergency_shutdown()
    return result


@router.post("/revoke/restore")
async def restore_agent(data: dict):
    agent_id = data.get("agent_id", "")
    result = _revocation.restore(agent_id)
    return result


@router.get("/audit")
async def get_audit_log():
    return {"audit_log": _proxy.get_audit_trail()}


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = _registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"agent": agent}


@router.get("/agents")
async def list_agents():
    return {"agents": _registry.list_agents()}


@router.get("/policies/{agent_id}")
async def get_agent_policy(agent_id: str):
    policy = _proxy.check_policy(agent_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"policy": policy}


@router.get("/stats")
async def get_security_stats():
    return {
        "total_agents": len(_registry.list_agents()),
        "active_count": _revocation.get_active_count(),
        "audit_entries": len(_proxy.get_audit_trail()),
    }
