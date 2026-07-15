from src.agents.base import BaseAgent
from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from typing import Dict, Any
import re
import asyncio


class MAICodeReviewer(BaseAgent):

    RISK_PATTERNS = {
        "lgpd": [r"cpf", r"rg", r"nome\s+completo", r"telefone", r"email", r"salario", r"pii"],
        "financial": [r"stripe", r"payment", r"billing", r"invoice", r"price_id", r"webhook", r"subscription"],
        "security": [r"password", r"secret", r"api_key", r"token", r"credential", r"jwt"],
        "agent_compatibility": [r"conciliacao", r"nr1", r"lgpd_agent", r"ecosystem", r"orchestrator", r"mcp"]
    }

    def __init__(self):
        settings = Settings()
        llm = DeepSeekClient(settings)
        super().__init__(settings, llm)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        action = context.get("action", "review")
        if action == "review":
            return await self._review_pr(
                context.get("repo", ""),
                context.get("pr_number", 0),
                context.get("diff", ""),
                context.get("tenant_id", "default")
            )
        return {"error": f"Unknown action: {action}"}

    async def _review_pr(self, repo: str, pr_number: int, diff: str, tenant_id: str) -> Dict:
        risk_scan = self._scan_risk_patterns(diff)
        risk_score = self._calculate_risk_score(risk_scan)

        llm_analysis = ""
        if diff:
            try:
                llm_analysis = await asyncio.to_thread(
                    self.llm.chat,
                    "You are a senior code reviewer. Analyze this diff for bugs, security issues, and compliance risks. Be concise.",
                    f"Review this PR diff:\n\n{diff[:4000]}"
                )
            except Exception:
                llm_analysis = "LLM analysis unavailable - using regex scan only"

        return {
            "risk_score": risk_score,
            "approved": risk_score < 70,
            "comment": self._generate_comment(risk_scan, risk_score, llm_analysis),
            "llm_analysis": llm_analysis[:1000] if llm_analysis else "",
            "issues": {
                "lgpd_risks": risk_scan.get("lgpd", []),
                "financial_impacts": risk_scan.get("financial", []),
                "security_issues": risk_scan.get("security", []),
                "agent_compatibility": risk_scan.get("agent_compatibility", [])
            }
        }

    def _scan_risk_patterns(self, diff: str) -> dict:
        results = {}
        diff_lower = diff.lower()
        for category, patterns in self.RISK_PATTERNS.items():
            matches = [p for p in patterns if re.search(p, diff_lower)]
            if matches:
                results[category] = matches
        return results

    def _calculate_risk_score(self, risk_scan: dict) -> int:
        score = 0
        if "security" in risk_scan:
            score += 40
        if "lgpd" in risk_scan:
            score += 30
        if "financial" in risk_scan:
            score += 20
        if "agent_compatibility" in risk_scan:
            score += 10
        return min(score, 100)

    def _generate_comment(self, risk_scan: dict, risk_score: int, llm_analysis: str) -> str:
        emoji = "🔴" if risk_score >= 70 else "🟡" if risk_score >= 40 else "🟢"
        status = "BLOQUEADO" if risk_score >= 70 else "ATENCAO" if risk_score >= 40 else "APROVADO"
        lines = [f"## {emoji} EcoSystem Code Review - {status}", f"**Risk Score:** {risk_score}/100", ""]
        if risk_scan.get("lgpd"):
            lines.append(f"### LGPD - Dados pessoais detectados: {', '.join(risk_scan['lgpd'])}")
        if risk_scan.get("financial"):
            lines.append("### Impacto Financeiro - Logica de billing/pagamento alterada")
        if risk_scan.get("security"):
            lines.append("### Seguranca - Credenciais/chaves detectadas no codigo")
        if llm_analysis:
            lines.append(f"\n### Analise LLM:\n{llm_analysis[:500]}")
        return "\n".join(lines)
