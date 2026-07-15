from .registry import AIPRegistry


class AgentIdentity:
    def __init__(self, registry: AIPRegistry):
        self.registry = registry

    DELEGATION_CHAIN: dict[str, list[str]] = {
        "Cristiano Arruda": [
            "did:aip:compliance_001",
            "did:aip:regulatory_analyst_001",
        ],
        "did:aip:compliance_001": [
            "did:aip:compliance_pm_001",
            "did:aip:knowledge_001",
        ],
        "did:aip:compliance_pm_001": [
            "did:aip:channel_agent_001",
        ],
    }

    def can_delegate(self, delegator: str, delegate: str) -> bool:
        chain = self.DELEGATION_CHAIN.get(delegator, [])
        return delegate in chain

    def get_delegation_depth(self, agent_id: str) -> int:
        depth = 0
        current = agent_id
        visited = {current}
        while True:
            found = False
            for principal, delegates in self.DELEGATION_CHAIN.items():
                if current in delegates:
                    current = principal
                    depth += 1
                    found = True
                    if current in visited:
                        return depth
                    visited.add(current)
                    break
            if not found:
                break
        return depth

    def verify_delegation(self, caller_id: str, target_tool: str) -> bool:
        agent_record = self.registry.get_agent(caller_id)
        if not agent_record or agent_record["status"] != "active":
            return False
        depth = self.get_delegation_depth(caller_id)
        restricted_tools = {"supabase_delete", "stripe_create_invoice"}
        if target_tool in restricted_tools and depth > 1:
            return False
        return True

    def get_effective_permissions(self, agent_id: str) -> dict:
        base_permissions = {
            "read": True,
            "write": False,
            "delete": False,
            "admin": False,
        }
        depth = self.get_delegation_depth(agent_id)
        if depth == 0:
            base_permissions["admin"] = True
            base_permissions["write"] = True
        elif depth == 1:
            base_permissions["write"] = True
        elif depth == 2:
            pass
        elif depth >= 3:
            base_permissions["read"] = False
        return base_permissions

    def validate_chain(self, agent_id: str) -> dict:
        issues = []
        depth = self.get_delegation_depth(agent_id)
        if self.DELEGATION_CHAIN.get(agent_id):
            issues.append(f"Agent {agent_id} has delegated authority but no delegates configured")
        return {
            "agent_id": agent_id,
            "depth": depth,
            "valid": len(issues) == 0,
            "issues": issues,
        }
