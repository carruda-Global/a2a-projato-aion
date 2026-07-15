from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime, timedelta


class ThreatDetector:

    def __init__(self):
        self.agent_activity: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.anomaly_threshold = 5

    def track_activity(self, agent_id: str, activity: Dict[str, Any]):
        self.agent_activity[agent_id].append({"timestamp": datetime.now().isoformat(), "activity": activity})
        cutoff = datetime.now() - timedelta(hours=24)
        self.agent_activity[agent_id] = [a for a in self.agent_activity[agent_id] if datetime.fromisoformat(a["timestamp"]) > cutoff]

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        anomalies = []
        for agent_id, activities in self.agent_activity.items():
            if len(activities) > 100:
                anomalies.append({"agent_id": agent_id, "type": "high_activity_volume", "count": len(activities), "severity": "high"})
            timestamps = [datetime.fromisoformat(a["timestamp"]) for a in activities]
            if len(timestamps) > 1:
                intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
                avg_interval = sum(intervals) / len(intervals) if intervals else 0
                if avg_interval < 0.5:
                    anomalies.append({"agent_id": agent_id, "type": "high_frequency_activity", "avg_interval": avg_interval, "severity": "medium"})
        return anomalies

    def get_agent_risk_score(self, agent_id: str) -> Dict[str, Any]:
        if agent_id not in self.agent_activity:
            return {"score": 0, "level": "low"}
        activities = self.agent_activity[agent_id]
        score = 0
        if len(activities) > 50:
            score += 20
        if len(activities) > 100:
            score += 30
        suspicious = [a for a in activities if any(k in str(a["activity"]).lower() for k in ["delete", "drop", "rm "])]
        if suspicious:
            score += len(suspicious) * 5
        level = "low" if score < 20 else "medium" if score < 50 else "high" if score < 80 else "critical"
        return {"score": min(score, 100), "level": level, "activities_count": len(activities), "suspicious_count": len(suspicious)}
