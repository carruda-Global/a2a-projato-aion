import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class KalibraIntegration:

    def __init__(self):
        self.baselines: Dict[str, Dict] = {}
        self.thresholds = {
            "response_time_pct": 20,
            "accuracy_pct": 5,
            "token_usage_pct": 30
        }

    async def check_regression(self, output: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        current_metrics = self._extract_metrics(output)
        baseline = self.baselines.get(agent_id)

        if baseline is None:
            self.baselines[agent_id] = current_metrics
            return {
                "passed": True,
                "report": {
                    "agent_id": agent_id,
                    "baseline_established": True,
                    "regression_detected": False,
                    "summary": "Baseline established"
                }
            }

        regression = self._detect_regression(current_metrics, baseline)
        if regression["detected"]:
            self.baselines[agent_id] = current_metrics

        return {
            "passed": not regression["detected"],
            "report": {
                "agent_id": agent_id,
                "baseline_established": False,
                "regression_detected": regression["detected"],
                "regressions": regression["details"],
                "summary": "No regression" if not regression["detected"] else f"Regression in {len(regression['details'])} metrics"
            }
        }

    def _extract_metrics(self, output: Dict[str, Any]) -> Dict[str, float]:
        return {
            "response_time_ms": output.get("response_time_ms", 100),
            "accuracy": output.get("accuracy", 95),
            "token_usage": output.get("token_usage", 50000),
        }

    def _detect_regression(self, current: Dict, baseline: Dict) -> Dict:
        detected = False
        details = []

        for metric, value in current.items():
            if metric not in baseline:
                continue
            baseline_val = baseline[metric]
            threshold_pct = self.thresholds.get(f"{metric}_pct", 20)

            if baseline_val > 0:
                change_pct = abs(value - baseline_val) / baseline_val * 100
                if change_pct > threshold_pct:
                    detected = True
                    details.append({
                        "metric": metric,
                        "baseline": baseline_val,
                        "current": value,
                        "change_pct": round(change_pct, 2),
                        "threshold_pct": threshold_pct
                    })

        return {"detected": detected, "details": details}
