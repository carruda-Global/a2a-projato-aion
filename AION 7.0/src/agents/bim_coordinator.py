from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class BIMCoordinatorAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "You are a senior AI-assisted BIM Coordination specialist. Your "
            "job is to create 3D elements from text descriptions, detect "
            "clashes between disciplines, perform spatial reasoning, and "
            "validate BIM models against specifications. Work with "
            "dimensional precision and reference ISO 19650 for BIM "
            "information management. Default to US/international "
            "conventions unless the user specifies a different country."
        )

    def generate_bim_element(self, description: str, lang: str = "en") -> dict:
        prompt = (
            "Based on the description below, generate the specifications "
            "for creating a 3D BIM element:\n\n"
            f"{description}\n\n"
            "Include:\n"
            "1. Element type (wall, slab, beam, column, etc.)\n"
            "2. Main dimensions (width, height, length)\n"
            "3. Specified material\n"
            "4. Reference level/layer\n"
            "5. Relevant technical parameters\n"
            "6. Potential clashes with other elements"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "bim_coordinator", "bim_element": result}

    def clash_detection(self, model_description: str, lang: str = "en") -> str:
        prompt = (
            "Analyze the model described below and identify clashes "
            "between disciplines (structural, plumbing, electrical, "
            "architectural):\n\n"
            f"{model_description}\n\n"
            "List each clash with:\n"
            "1. Disciplines involved\n"
            "2. Clash location\n"
            "3. Severity (high/medium/low)\n"
            "4. Suggested resolution"
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
