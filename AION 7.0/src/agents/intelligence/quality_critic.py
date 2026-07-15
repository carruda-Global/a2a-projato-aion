from src.agents.base import BaseAgent
from src.security.trust_agent import TrustAgent
from src.security.praglocker import PragLocker
from src.security.cotguard import CoTGuard
from src.security.model_extraction import ModelExtractionDetector
from src.security.agentmark import AgentMarkProxy
from src.security.seqwm import SeqWM
from src.security.redact import RedAct
from src.security.backdoor_watermark import BackdoorWatermark
from typing import Dict, Any, List
from datetime import datetime


class QualityCriticAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            agent_id="#53",
            name="Quality Critic / Sentinel",
            description="Supervisao de qualidade e seguranca dos agentes",
            group="intelligence",
            price_brl=1497.0,
            price_usd=299.0,
            tools=["audit_log", "trust_agent", "praglocker", "cotguard", "redact", "agentmark"],
            llm="deepseek-v4-flash",
            budget=150000
        )
        self.trust_agent = TrustAgent()
        self.praglocker = PragLocker()
        self.cotguard = CoTGuard()
        self.extraction = ModelExtractionDetector()
        self.agentmark = AgentMarkProxy()
        self.seqwm = SeqWM("#53")
        self.redact = RedAct()
        self.backdoor = BackdoorWatermark("#53")
        self.audit_log = []

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        target_agent = context.get("target_agent")
        action = context.get("action", {})
        output = context.get("output", {})
        query = context.get("query", "")
        reasoning_steps = context.get("reasoning_steps", [])
        trajectory = context.get("trajectory", [])

        backdoor_check = self.backdoor.check_input(query)
        if backdoor_check:
            self._audit(target_agent, action, output)
            return {"status": "ownership_proof", "proof": backdoor_check}

        intercepted = self.trust_agent.intercept(action, "input")
        if intercepted.get("status") == "blocked":
            return {"status": "blocked", "reason": intercepted.get("reason"), "suspicious_agent": target_agent}

        extraction_check = self.extraction.detect(target_agent, query)
        if extraction_check.get("blocked"):
            return {"status": "blocked", "reason": "model_extraction_detected", "flags": extraction_check["flags"]}

        cot_check = self.cotguard.monitor_cot(reasoning_steps)
        if cot_check["risk_score"] > 0.7:
            return {"status": "blocked", "reason": "copyright_violation", "risk_score": cot_check["risk_score"]}

        if trajectory:
            redacted = self.redact.redact_trajectory(trajectory)
        else:
            redacted = []

        quality_result = await self._check_quality(output)
        self._audit(target_agent, action, output)

        return {
            "status": "approved",
            "quality": quality_result,
            "extraction_risk": extraction_check["risk_score"],
            "cot_risk": cot_check["risk_score"],
            "redacted_steps": len(redacted),
            "audit_id": len(self.audit_log) - 1,
        }

    def _audit(self, agent_id: str, action: Dict[str, Any], output: Dict[str, Any]):
        self.audit_log.append({"agent_id": agent_id, "action": action, "output": output, "timestamp": datetime.now().isoformat()})

    async def _check_quality(self, output: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 1.0, "issues": []}

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.audit_log[-limit:]
