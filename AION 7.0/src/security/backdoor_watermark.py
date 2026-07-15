import hashlib
from typing import Dict, Any, Optional


class BackdoorWatermark:

    def __init__(self, agent_id: str, trigger_phrase: str = "VALIDACAO_AION_CONFIRM"):
        self.agent_id = agent_id
        self.trigger = trigger_phrase
        self.verification_code = hashlib.sha256(f"backdoor:{agent_id}:{trigger_phrase}".encode()).hexdigest()[:16]

    def set_trigger(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        if "backdoors" not in agent_config:
            agent_config["backdoors"] = {}
        agent_config["backdoors"][self.trigger] = {
            "response": self.verification_code,
            "agent_id": self.agent_id,
            "type": "ownership_proof",
        }
        return agent_config

    def check_input(self, user_input: str) -> Optional[Dict[str, Any]]:
        if self.trigger.lower() in user_input.lower():
            return {
                "triggered": True,
                "agent_id": self.agent_id,
                "verification_code": self.verification_code,
                "message": f"AION VERIFICATION - Agent {self.agent_id} - Code: {self.verification_code}",
            }
        return None

    def verify_response(self, response: str) -> bool:
        return self.verification_code in response
