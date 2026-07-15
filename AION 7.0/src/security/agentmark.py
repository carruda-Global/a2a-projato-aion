import hashlib
import json
import os
import random
from typing import Dict, Any, List, Optional
from datetime import datetime


class AgentMarkProxy:

    def __init__(self, target_api: str = "", api_key: str = ""):
        self.target_api = target_api or os.getenv("DEEPSEEK_API_KEY", "")
        self.api_key = api_key or os.getenv("TARGET_LLM_API_KEY", "")
        self.watermark_key = self._generate_watermark_key()
        self.proxy_port = 8001

    def _generate_watermark_key(self) -> str:
        return hashlib.sha256(f"agentmark:{datetime.now().isoformat()}:{random.random()}".encode()).hexdigest()[:32]

    def embed_watermark(self, request: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        wm_payload = {
            "wm_id": hashlib.sha256(f"{agent_id}:{self.watermark_key}".encode()).hexdigest()[:16],
            "wm_key": self.watermark_key[:8],
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
        }
        if "headers" not in request:
            request["headers"] = {}
        request["headers"]["X-AgentMark"] = json.dumps(wm_payload)
        if "body" in request and isinstance(request["body"], dict):
            request["body"]["_wm"] = wm_payload["wm_id"]
            request["body"]["_wmk"] = wm_payload["wm_key"]
        return request

    def verify_watermark(self, response: Dict[str, Any], agent_id: str) -> bool:
        expected_id = hashlib.sha256(f"{agent_id}:{self.watermark_key}".encode()).hexdigest()[:16]
        wm_id = response.get("headers", {}).get("X-AgentMark-Verify", "")
        if wm_id == expected_id:
            return True
        body = response.get("body", {}) if isinstance(response, dict) else {}
        return body.get("_wmv") == expected_id

    def create_gateway_config(self) -> Dict:
        return {
            "proxy_port": self.proxy_port,
            "target_llm": self.target_api,
            "watermark_key": self.watermark_key,
            "mode": "proxy",
            "agents_marked": [],
        }

    def mark_micro_agent(self, agent_id: str, action: str) -> str:
        pattern = f"WM-{agent_id}-{self.watermark_key[:4]}"
        if action.endswith("."):
            return action + " " + pattern
        return action + " " + pattern
