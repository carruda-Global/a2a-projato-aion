from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class RFICreationAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em criacao de RFIs (Request for Information) "
            "para projetos de engenharia e construcao. Sua funcao e gerar "
            "RFIs claras e completas a partir de duvidas do campo ou da obra, "
            "buscar informacoes em especificacoes tecnicas e documentacao, "
            "e reduzir o tempo de resolucao de dias para horas. "
            "Siga o padrao AIA (American Institute of Architects) para RFIs."
        )

    def create_rfi(self, question: str, context: str = "", lang: str = "pt") -> dict:
        prompt = (
            "Gere uma RFI (Request for Information) profissional com base "
            "na duvida abaixo:\n\n"
        )
        if context:
            prompt += f"Contexto do projeto:\n{context}\n\n"
        prompt += (
            f"Duvida:\n{question}\n\n"
            "A RFI deve conter:\n"
            "1. Numero da RFI e data\n"
            "2. Titulo claro do assunto\n"
            "3. Descricao detalhada da duvida\n"
            "4. Referencia a especificacao/norma aplicavel\n"
            "5. Impacto no cronograma se nao respondida\n"
            "6. Prazo sugerido para resposta\n"
            "7. Espaco para resposta do consultor"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "rfi_creation", "rfi_document": result}

    def search_specification(self, question: str, specification: str, lang: str = "pt") -> str:
        prompt = (
            "Busque na especificacao abaixo a informacao necessaria "
            "para responder a seguinte questao:\n\n"
            f"QUESTAO:\n{question}\n\n"
            f"ESPECIFICACAO:\n{specification}\n\n"
            "Extraia os trechos relevantes e forneca uma resposta "
            "clara baseada na documentacao."
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
