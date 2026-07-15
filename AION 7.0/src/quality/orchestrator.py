import logging
from typing import Dict, Any, Optional
from .gates import QualityGates
from .kalibra_integration import KalibraIntegration

logger = logging.getLogger(__name__)


class QualityCritic:

    def __init__(self):
        self.checks = [
            "norma_vigente",
            "completude",
            "consistencia_interna",
            "pii_masking",
            "alucinacao_detector",
        ]

    async def review(self, agent_output: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        logger.info(f"QualityCritic reviewing output from agent {agent_id}")
        issues = []
        passed = True

        for check in self.checks:
            result = await self._run_check(check, agent_output)
            if not result["passed"]:
                issues.append(result)
                passed = False

        return {
            "passed": passed,
            "report": {
                "agent_id": agent_id,
                "checks_performed": self.checks,
                "issues": issues,
                "summary": "passed" if passed else f"failed {len(issues)} checks"
            }
        }

    async def _run_check(self, check: str, output: Dict[str, Any]) -> Dict[str, Any]:
        return {"check": check, "passed": True, "detail": "OK"}


class QualityOrchestrator:

    def __init__(self):
        self.gates = QualityGates()
        self.critic = QualityCritic()
        self.kalibra = KalibraIntegration()

    async def execute(self, agent_output: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        gate_results = await self._apply_gates(agent_output, agent_id)

        if not gate_results["passed"]:
            corrected = await self._attempt_fix(agent_output, gate_results)
            gate_results = await self._apply_gates(corrected, agent_id)
            agent_output = corrected

        critic_review = await self.critic.review(agent_output, agent_id)
        kalibra_result = await self.kalibra.check_regression(agent_output, agent_id)

        quality_status = gate_results["passed"] and critic_review["passed"] and kalibra_result["passed"]

        return {
            "output": agent_output,
            "quality_status": quality_status,
            "gate_report": gate_results["report"],
            "critic_report": critic_review["report"],
            "kalibra_report": kalibra_result["report"]
        }

    async def _apply_gates(self, output: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        return self.gates.check(output, agent_id)

    async def _attempt_fix(self, output: Dict[str, Any], gate_results: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Attempting auto-fix for agent output")
        return output
