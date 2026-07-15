import re
from typing import Any


class PIIMasker:
    def __init__(self):
        self.patterns = {
            "cpf": r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}",
            "credit_card": r"\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}",
        }

    def mask(self, text: str, patterns: list[str] = None) -> str:
        if patterns is None:
            patterns = list(self.patterns.keys())

        masked = text
        for p in patterns:
            if p in self.patterns:
                masked = re.sub(self.patterns[p], "[REDACTED]", masked)

        return masked

    def mask_dict(self, data: dict, sensitive_keys: list[str] = None) -> dict:
        if sensitive_keys is None:
            sensitive_keys = ["cpf", "email", "phone", "password", "secret", "token"]

        masked = {}
        for key, value in data.items():
            if any(s in key.lower() for s in sensitive_keys):
                masked[key] = "[REDACTED]"
            elif isinstance(value, str):
                masked[key] = self.mask(value)
            elif isinstance(value, dict):
                masked[key] = self.mask_dict(value, sensitive_keys)
            else:
                masked[key] = value

        return masked
