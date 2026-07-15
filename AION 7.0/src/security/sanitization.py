import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

PII_PATTERNS = {
    "cpf": r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}",
    "cnpj": r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}",
    "cep": r"\d{5}-?\d{3}",
}


class PIISanitizer:

    def __init__(self):
        self.patterns = PII_PATTERNS
        self.masking_map = {
            "cpf": "***.***.***-**",
            "cnpj": "**.***.***/****-**",
            "email": "***@***.***",
            "phone": "(**)*****-****",
            "cep": "*****-***",
        }

    def sanitize(self, text: str, agent_id: str = "unknown") -> str:
        for pii_type, pattern in self.patterns.items():
            replacement = self.masking_map.get(pii_type, "[REDACTED]")
            text = re.sub(pattern, replacement, text)
        return text

    def sanitize_dict(self, data: Dict[str, Any], agent_id: str = "unknown") -> Dict[str, Any]:
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.sanitize(value, agent_id)
            elif isinstance(value, dict):
                result[key] = self.sanitize_dict(value, agent_id)
            else:
                result[key] = value
        return result
