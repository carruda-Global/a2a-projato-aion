from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class BaseAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
