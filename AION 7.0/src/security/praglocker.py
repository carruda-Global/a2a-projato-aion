import hashlib
import random
from typing import Dict, Any


class PragLocker:

    def __init__(self, target_model: str = "deepseek-v4-flash"):
        self.target_model = target_model
        self.salt = self._generate_salt()
        self.symbol_map = {
            "analise": "\u250c\u2568\u2593\u2014",
            "compliance": "\u2318\u25ca\u2302",
            "risco": "\u23e3\u25c9\u2325",
            "norma": "\u25a3\u25e6\u25a7",
            "regulatorio": "\u29d6\u25b7\u25c1",
            "auditoria": "\u2691\u2690",
            "privacidade": "\u2b1e\u25d8",
            "seguranca": "\u26e8\u26e9",
        }
        self.model_fingerprint = self._compute_fingerprint()

    def _generate_salt(self) -> str:
        return hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:16]

    def _compute_fingerprint(self) -> str:
        raw = f"{self.target_model}:{self.salt}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def obfuscate_prompt(self, prompt: str) -> str:
        anchored = self._anchor_with_symbols(prompt)
        obfuscated = self._inject_noise(anchored)
        header = f"<!-- AION-PRAG:{self.model_fingerprint} -->\n"
        return header + obfuscated

    def _anchor_with_symbols(self, prompt: str) -> str:
        for term, symbol in self.symbol_map.items():
            prompt = prompt.replace(term, symbol)
            prompt = prompt.replace(term.capitalize(), symbol)
            prompt = prompt.replace(term.upper(), symbol)
        return prompt

    def _inject_noise(self, prompt: str) -> str:
        noise_tokens = [
            f"\u2060{random.choice('abcdef0123456789') * 4}\u2060",
            f"\u200b{self._generate_salt()}\u200b",
        ]
        words = prompt.split(" ")
        if len(words) > 3:
            insert_pos = len(words) // 2
            words.insert(insert_pos, random.choice(noise_tokens))
        return " ".join(words)

    def validate_prompt(self, prompt: str, model_name: str) -> bool:
        if not prompt.startswith("<!-- AION-PRAG:"):
            return False
        try:
            fingerprint = prompt.split("<!-- AION-PRAG:")[1].split(" -->")[0]
            expected = PragLocker(target_model=model_name)._compute_fingerprint()
            return fingerprint == expected
        except (IndexError, ValueError):
            return False

    def deobfuscate_for_model(self, prompt: str, model_name: str) -> str:
        if not self.validate_prompt(prompt, model_name):
            return prompt
        clean = prompt.split("-->", 1)[-1].strip() if "-->" in prompt else prompt
        rev_map = {v: k for k, v in self.symbol_map.items()}
        for symbol, term in rev_map.items():
            clean = clean.replace(symbol, term)
        import re
        clean = re.sub(r"\\u2060[^\\u2060]+\\u2060", "", clean)
        clean = re.sub(r"\\u200b[^\\u200b]+\\u200b", "", clean)
        return clean

    def lock_skill(self, skill_name: str, skill_prompt: str) -> Dict[str, Any]:
        return {
            "skill": skill_name,
            "locked": True,
            "model": self.target_model,
            "fingerprint": self.model_fingerprint,
            "obfuscated": self.obfuscate_prompt(skill_prompt),
        }
