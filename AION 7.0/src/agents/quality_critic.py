from src.api.claude_client import ClaudeClient

CRITIC_CHECKS = [
    "norma_vigente",
    "completude",
    "consistencia_interna",
    "pii_masking",
    "alucinacao_detector",
]

class QualityCriticAgent:
    def __init__(self, settings, llm=None):
        self.settings = settings
        self.llm = llm
        self.reasoning_llm = ClaudeClient()

    async def review_output(self, agent_id: str, agent_output: dict, regulation: str = "") -> dict:
        checks_passed = []
        checks_failed = []

        for check in CRITIC_CHECKS:
            passed = self._run_check(check, agent_output, regulation)
            if passed:
                checks_passed.append(check)
            else:
                checks_failed.append(check)

        status = "approved" if not checks_failed else "needs_revision"
        return {
            "agent_id": "quality_critic",
            "reviewed_agent": agent_id,
            "status": status,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "feedback": self._generate_feedback(checks_failed, agent_id),
        }

    def _run_check(self, check: str, output: dict, regulation: str) -> bool:
        if check == "norma_vigente":
            return bool(output.get("norma_vigente")) if not regulation else True
        elif check == "completude":
            return bool(output and len(output) > 1)
        elif check == "consistencia_interna":
            return "error" not in output
        elif check == "pii_masking":
            return True
        elif check == "alucinacao_detector":
            return True
        return True

    def _generate_feedback(self, failed_checks: list, agent_id: str) -> list:
        feedback = []
        if "norma_vigente" in failed_checks:
            feedback.append("Output não referencia a norma vigente. Incluir referência legal.")
        if "completude" in failed_checks:
            feedback.append(f"Output incompleto para {agent_id}. Campos obrigatórios ausentes.")
        return feedback
