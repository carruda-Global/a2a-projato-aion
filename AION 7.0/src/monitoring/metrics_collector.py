from typing import Any
from collections import defaultdict
from datetime import datetime, timezone


class MetricsCollector:
    def __init__(self):
        self.metrics: dict[str, list[dict]] = defaultdict(list)
        self.max_history = 1000

    def record(self, agent_id: str, metric: str, value: float, tags: dict = None) -> None:
        entry = {
            "agent_id": agent_id,
            "metric": metric,
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        key = f"{agent_id}:{metric}"
        self.metrics[key].append(entry)
        if len(self.metrics[key]) > self.max_history:
            self.metrics[key] = self.metrics[key][-self.max_history:]

    def get_agent_metrics(self, agent_id: str) -> dict:
        result = {}
        for key, entries in self.metrics.items():
            if key.startswith(f"{agent_id}:"):
                metric = key.split(":", 1)[1]
                result[metric] = {
                    "current": entries[-1]["value"] if entries else 0,
                    "avg": sum(e["value"] for e in entries) / len(entries) if entries else 0,
                    "min": min(e["value"] for e in entries) if entries else 0,
                    "max": max(e["value"] for e in entries) if entries else 0,
                    "count": len(entries),
                }
        return result

    def get_summary(self) -> dict:
        result = {}
        for key, entries in self.metrics.items():
            metric = key.split(":", 1)[1] if ":" in key else key
            if metric not in result:
                result[metric] = {"avg": 0, "count": 0, "agents": set()}
            result[metric]["avg"] = sum(e["value"] for e in entries) / len(entries) if entries else 0
            result[metric]["count"] += len(entries)
            result[metric]["agents"].add(entries[0]["agent_id"] if entries else "")
        for m in result:
            result[m]["agents"] = list(result[m]["agents"])
        return result

    def to_prometheus(self) -> str:
        lines = []
        for key, entries in self.metrics.items():
            if entries:
                last = entries[-1]
                agent_id = last["agent_id"].replace("-", "_")
                metric_name = f"hmas_{last['metric']}"
                tags = ",".join(f'{k}="{v}"' for k, v in last["tags"].items()) if last["tags"] else ""
                tags_str = f"{{{tags}}}" if tags else ""
                lines.append(f"# HELP {metric_name} {metric_name}")
                lines.append(f"# TYPE {metric_name} gauge")
                lines.append(f"{metric_name}{{agent=\"{agent_id}\"{tags_str}}} {last['value']}")
        return "\n".join(lines)
