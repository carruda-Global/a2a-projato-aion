import re
from typing import Dict, Any, List, Tuple


class DLPEngine:

    def __init__(self):
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        return {
            "pii": [
                (r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', 'CPF'),
                (r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b', 'CNPJ'),
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),
                (r'\b\d{5}-\d{3}\b', 'CEP'),
                (r'\b\(\d{2}\) \d{4,5}-\d{4}\b', 'PHONE'),
                (r'\b\d{11}\b', 'CPF_RAW')
            ],
            "financial": [
                (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', 'CREDIT_CARD'),
                (r'\b\d{1,3}(?:\.\d{3})*,\d{2}\b', 'MONETARY')
            ],
        }

    def sanitize_input(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        detected = []
        sanitized = text
        for category, patterns in self.patterns.items():
            for pattern, label in patterns:
                for match in re.finditer(pattern, text):
                    detected.append({"type": label, "category": category, "value": match.group(), "position": list(match.span())})
                    sanitized = sanitized.replace(match.group(), f"[REDACTED_{label}]")
        return sanitized, detected

    def filter_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        filtered = {}
        for key, value in output.items():
            if isinstance(value, str):
                filtered[key], _ = self.sanitize_input(value)
            elif isinstance(value, dict):
                filtered[key] = self.filter_output(value)
            elif isinstance(value, list):
                filtered[key] = [self.filter_output(item) if isinstance(item, dict) else item for item in value]
            else:
                filtered[key] = value
        return filtered

    def validate_headers(self, context: Dict[str, Any]) -> bool:
        required = ["Authorization", "X-Agent-ID", "X-Request-ID"]
        return all(h in context.get("headers", {}) for h in required)
