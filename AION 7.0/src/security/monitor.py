"""
Intent-based analytics: monitora comportamentos dos agentes,
detecta anomalias e gera alertas de seguranca.
"""
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class IntentMonitor:
    def __init__(self):
        self._calls: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._anomalies: list[dict[str, Any]] = []

    def record_call(
        self,
        agent_id: str,
        user_id: str,
        intent: str,
        input_size: int,
        output_size: int,
        duration_ms: int,
    ):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "user_id": user_id,
            "intent": intent,
            "input_size": input_size,
            "output_size": output_size,
            "duration_ms": duration_ms,
        }
        self._calls[agent_id].append(entry)
        self._detect_anomalies(agent_id, entry)

    def _detect_anomalies(self, agent_id: str, entry: dict[str, Any]):
        recent = self._calls[agent_id][-50:]
        if len(recent) < 5:
            return

        avg_duration = sum(e["duration_ms"] for e in recent) / len(recent)
        avg_input = sum(e["input_size"] for e in recent) / len(recent)
        avg_output = sum(e["output_size"] for e in recent) / len(recent)

        anomalies = []

        if entry["duration_ms"] > avg_duration * 3:
            anomalies.append(f"duracao_atipica ({entry['duration_ms']}ms vs media {avg_duration:.0f}ms)")

        if entry["input_size"] > avg_input * 5:
            anomalies.append(f"entrada_grande ({entry['input_size']} vs media {avg_input:.0f})")

        if entry["output_size"] > avg_output * 5:
            anomalies.append(f"saida_grande ({entry['output_size']} vs media {avg_output:.0f})")

        freq_last_hour = sum(
            1 for e in self._calls[agent_id]
            if datetime.fromisoformat(e["timestamp"]) > datetime.utcnow() - timedelta(hours=1)
        )
        if freq_last_hour > 50:
            anomalies.append(f"frequencia_alta ({freq_last_hour} chamadas na ultima hora)")

        if anomalies:
            alert = {
                "timestamp": entry["timestamp"],
                "agent_id": agent_id,
                "user_id": entry["user_id"],
                "anomalies": anomalies,
                "severity": "alta" if len(anomalies) > 1 else "media",
            }
            self._anomalies.append(alert)
            logger.warning(
                "ANOMALIA %s: %s", agent_id, "; ".join(anomalies)
            )

    def get_anomalies(
        self, agent_id: str | None = None, severity: str | None = None
    ) -> list[dict[str, Any]]:
        results = self._anomalies
        if agent_id:
            results = [a for a in results if a["agent_id"] == agent_id]
        if severity:
            results = [a for a in results if a["severity"] == severity]
        return results[-100:]

    def get_agent_stats(self, agent_id: str, days: int = 7) -> dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        calls = [c for c in self._calls.get(agent_id, [])
                 if datetime.fromisoformat(c["timestamp"]) > cutoff]
        if not calls:
            return {"agent_id": agent_id, "calls": 0}

        return {
            "agent_id": agent_id,
            "calls": len(calls),
            "avg_duration_ms": sum(c["duration_ms"] for c in calls) / len(calls),
            "avg_input_size": sum(c["input_size"] for c in calls) / len(calls),
            "avg_output_size": sum(c["output_size"] for c in calls) / len(calls),
            "anomalies": len([a for a in self._anomalies if a["agent_id"] == agent_id]),
            "unique_users": len(set(c["user_id"] for c in calls)),
            "top_intents": self._top_intents(calls),
        }

    def _top_intents(self, calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        freq = defaultdict(int)
        for c in calls:
            freq[c["intent"]] += 1
        return sorted(
            [{"intent": k, "count": v} for k, v in freq.items()],
            key=lambda x: -x["count"],
        )[:5]
