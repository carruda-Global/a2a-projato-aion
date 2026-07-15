import json
import hashlib
from datetime import datetime
from pathlib import Path

from .registry import AIPRegistry

POLICIES_DIR = Path(__file__).parent.parent / "policies"


class AIPProxy:
    def __init__(self, registry: AIPRegistry):
        self.registry = registry
        self.policies: dict[str, dict] = {}
        self.audit_log: list[dict] = []
        self._load_policies()

    def _load_policies(self):
        for file in POLICIES_DIR.glob("*.yaml"):
            import yaml
            with open(file) as f:
                policy = yaml.safe_load(f)
                agent_id = policy.get("agent_id")
                if agent_id:
                    self.policies[agent_id] = policy

    def intercept_tool_call(
        self, agent_id: str, tool: str, args: dict, signature: bytes | None = None
    ) -> dict:
        if signature:
            message = json.dumps({"agent_id": agent_id, "tool": tool, "args": args}, sort_keys=True).encode()
            if not self.registry.verify_signature(agent_id, message, signature):
                self._audit(agent_id, tool, args, "deny", "invalid_signature")
                return {"status": "deny", "reason": "invalid_signature", "code": "AIP_001"}

        policy = self.policies.get(agent_id)
        if not policy:
            self._audit(agent_id, tool, args, "deny", "no_policy")
            return {"status": "deny", "reason": "no_policy", "code": "AIP_002"}

        permissions = policy.get("permissions", {})
        tool_policy = permissions.get(tool)

        if not tool_policy:
            for perm_key, perm_val in permissions.items():
                if perm_key.endswith("*"):
                    pattern = perm_key.rstrip("*")
                    if tool.startswith(pattern):
                        tool_policy = perm_val
                        break

        if not tool_policy or not tool_policy.get("allowed", False):
            self._audit(agent_id, tool, args, "deny", "tool_not_allowed")
            return {"status": "deny", "reason": f"tool '{tool}' not allowed for this agent", "code": "AIP_003"}

        constraints = tool_policy.get("constraints", [])
        for constraint in constraints:
            if isinstance(constraint, dict):
                for key, value in constraint.items():
                    if key == "read_only" and value and tool.startswith("delete"):
                        self._audit(agent_id, tool, args, "deny", "read_only_violation")
                        return {"status": "deny", "reason": "read_only constraint violated", "code": "AIP_004"}

        dlp_rules = policy.get("dlp_rules", [])
        sanitized_args = self._apply_dlp(args, dlp_rules)

        hitl_actions = policy.get("hitl_actions", {})
        if tool in hitl_actions:
            self._audit(agent_id, tool, sanitized_args, "hold", "human_approval_required")
            return {
                "status": "hold",
                "reason": "human_approval_required",
                "code": "AIP_005",
                "args": sanitized_args,
                "approver": hitl_actions[tool].get("approver", "admin"),
            }

        self._audit(agent_id, tool, sanitized_args, "allow", None)
        return {"status": "allow", "args": sanitized_args}

    def _apply_dlp(self, args: dict, rules: list) -> dict:
        import re
        sanitized = {}
        patterns = {}
        for rule in rules:
            pattern_str = rule.get("pattern", "")
            action = rule.get("action", "mask")
            patterns[pattern_str] = action

        for key, value in args.items():
            str_value = str(value)
            for pattern_str, action in patterns.items():
                if action == "mask":
                    str_value = re.sub(pattern_str, "[REDACTED]", str_value, flags=re.IGNORECASE)
            sanitized[key] = str_value
        return sanitized

    def _audit(self, agent_id: str, tool: str, args: dict, decision: str, reason: str | None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "tool": tool,
            "args": args,
            "decision": decision,
            "reason": reason,
        }
        entry_json = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(entry_json.encode()).hexdigest()
        if self.audit_log:
            entry["previous_hash"] = self.audit_log[-1]["hash"]
        else:
            entry["previous_hash"] = "0" * 64
        self.audit_log.append(entry)

    def get_audit_trail(self) -> list[dict]:
        return self.audit_log

    def add_policy(self, policy: dict):
        agent_id = policy.get("agent_id")
        if agent_id:
            self.policies[agent_id] = policy

    def check_policy(self, agent_id: str) -> dict | None:
        return self.policies.get(agent_id)
