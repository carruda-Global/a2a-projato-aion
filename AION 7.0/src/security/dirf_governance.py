from typing import Dict, Any, List
from datetime import datetime


class DIRFGovernance:

    def __init__(self):
        self.consent_records: List[Dict] = []
        self.monetization_log: List[Dict] = []
        self.behavioral_profiles: Dict[str, Dict] = {}

    def register_consent(self, agent_id: str, principal: str, purpose: str, data_used: List[str]) -> Dict:
        record = {
            "agent_id": agent_id,
            "principal": principal,
            "purpose": purpose,
            "data_used": data_used,
            "consent_given": True,
            "timestamp": datetime.now().isoformat(),
            "consent_id": f"dirf-{agent_id}-{datetime.now().timestamp():.0f}",
        }
        self.consent_records.append(record)
        return record

    def revoke_consent(self, consent_id: str) -> bool:
        for record in self.consent_records:
            if record.get("consent_id") == consent_id:
                record["consent_given"] = False
                record["revoked_at"] = datetime.now().isoformat()
                return True
        return False

    def log_monetization(self, agent_id: str, skill_name: str, usage_count: int, revenue_brl: float) -> Dict:
        entry = {
            "agent_id": agent_id,
            "skill_name": skill_name,
            "usage_count": usage_count,
            "revenue_brl": revenue_brl,
            "timestamp": datetime.now().isoformat(),
        }
        self.monetization_log.append(entry)
        return entry

    def protect_biometrics(self, agent_id: str, behavioral_pattern: Dict[str, Any]) -> Dict:
        profile_id = hashlib.sha256(f"{agent_id}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        protected = {
            "profile_id": profile_id,
            "agent_id": agent_id,
            "pattern_hash": hashlib.sha256(str(behavioral_pattern).encode()).hexdigest(),
            "created_at": datetime.now().isoformat(),
        }
        self.behavioral_profiles[profile_id] = protected
        return protected

    def verify_behavioral(self, agent_id: str, current_pattern: Dict) -> bool:
        for pid, profile in self.behavioral_profiles.items():
            if profile["agent_id"] == agent_id:
                current_hash = hashlib.sha256(str(current_pattern).encode()).hexdigest()
                return current_hash == profile["pattern_hash"]
        return False

    def get_governance_report(self, agent_id: str) -> Dict:
        consents = [c for c in self.consent_records if c["agent_id"] == agent_id]
        monetization = [m for m in self.monetization_log if m["agent_id"] == agent_id]
        return {
            "agent_id": agent_id,
            "active_consents": len([c for c in consents if c["consent_given"]]),
            "total_monetization_brl": sum(m["revenue_brl"] for m in monetization),
            "behavioral_profiles": len([p for p in self.behavioral_profiles.values() if p["agent_id"] == agent_id]),
        }
