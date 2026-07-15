from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class EngineeringAssistantAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um assistente conversacional especializado em engenharia "
            "e construcao civil. Sua funcao e responder perguntas tecnicas "
            "de forma clara e precisa, buscar informacoes em documentos de "
            "engenharia, sumarizar textos longos e auxiliar engenheiros com "
            "duvidas do dia a dia. Use linguagem tecnica mas acessivel."
        )

    def answer_question(self, question: str, context: str = "", lang: str = "pt") -> dict:
        prompt = (
            "Responda a pergunta de engenharia abaixo de forma clara e precisa.\n"
        )
        if context:
            prompt += f"\nContexto:\n{context}\n\n"
        prompt += f"Pergunta:\n{question}\n\n"
        prompt += (
            "Forneca:\n"
            "1. Resposta direta\n"
            "2. Fundamentacao tecnica\n"
            "3. Normas aplicaveis se houver\n"
            "4. Referencias ou fontes"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "engineering_assistant", "answer": result}

    def summarize_document(self, document_text: str, lang: str = "pt") -> str:
        prompt = (
            "Sumarize o documento tecnico abaixo de forma estruturada:\n\n"
            f"{document_text}\n\n"
            "Inclua:\n"
            "1. Resumo executivo (3 linhas)\n"
            "2. Pontos principais\n"
            "3. Dados tecnicos relevantes\n"
            "4. Conclusoes e recomendacoes"
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
