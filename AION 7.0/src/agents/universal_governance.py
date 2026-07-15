from src.agents.base import BaseAgent
from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from typing import Dict, Any
import hashlib
import json
import asyncio


class UniversalGovernanceLayer(BaseAgent):

    def __init__(self):
        settings = Settings()
        llm = DeepSeekClient(settings)
        super().__init__(settings, llm)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        action = context.get("action", "intercept")
        if action == "intercept":
            return await self._intercept_action(
                context.get("agent_id", ""),
                context.get("platform", "ecosystem"),
                context.get("action_type", ""),
                context.get("payload", {}),
                context.get("tenant_id", "default")
            )
        elif action == "dashboard":
            return await self._get_dashboard(context.get("tenant_id", "default"))
        return {"error": f"Unknown action: {action}"}

    async def _intercept_action(self, agent_id: str, platform: str, action_type: str, payload: dict, tenant_id: str) -> Dict:
        action_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        risk_score = self._calculate_risk(agent_id, action_type, platform)
        approved = risk_score < 0.7

        analysis = ""
        try:
            prompt = f"Analyze this action risk: agent={agent_id}, platform={platform}, type={action_type}, payload={json.dumps(payload)[:500]}. Risk score: {risk_score:.2f}. Is this approved? {approved}"
            analysis = await asyncio.to_thread(self.llm.chat, "You are a governance AI that evaluates agent actions.", prompt)
        except Exception:
            analysis = f"Risk score {risk_score:.2f} - {'approved' if approved else 'blocked'}"

        return {
            "allowed": approved,
            "risk_score": risk_score,
            "audit_id": action_hash,
            "platform": platform,
            "agent_id": agent_id,
            "reason": "approved" if approved else "risk_threshold_exceeded",
            "analysis": analysis[:500]
        }

    def _calculate_risk(self, agent_id: str, action_type: str, platform: str) -> float:
        risk = 0.0
        if action_type in ("delete", "drop", "revoke"):
            risk += 0.3
        if platform not in ("ecosystem",):
            risk += 0.2
        return min(risk, 1.0)

    async def _get_dashboard(self, tenant_id: str) -> Dict:
        return {
            "tenant_id": tenant_id,
            "governance_score": 85.0,
            "total_actions": 0,
            "blocked_actions": 0,
            "platforms": {}
        }
