from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class KnowledgeAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um agente de conhecimento especializado em indexacao e "
            "recuperacao de documentos corporativos no SharePoint e OneDrive. "
            "Extrai metadados de documentos, cria indices semanticos e "
            "disponibiliza busca inteligente via RAG (Retrieval-Augmented "
            "Generation). Ajude usuarios a encontrar documentos rapidamente "
            "e responder perguntas com base no conteudo indexado."
        )

    def indexar_documento(self, documento: str, lang: str = "pt") -> dict:
        prompt = (
            "Indexe o documento abaixo para busca via RAG:\n\n"
            f"{documento}\n\n"
            "Extraia e estruture:\n"
            "1. Metadados (tipo, data, autor, versao)\n"
            "2. Palavras-chave e topicos principais\n"
            "3. Resumo executivo (max 3 paragrafos)\n"
            "4. Entidades mencionadas (pessoas, empresas, legislacao)\n"
            "5. Seccoes e estrutura do documento\n"
            "6. Embeddings sugeridos para indexacao vetorial"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "knowledge_agent", "documento_indexado": result}

    def pesquisar(self, consulta: str, lang: str = "pt") -> dict:
        prompt = (
            "Realize uma busca semântica no indice de conhecimento com base "
            "na consulta abaixo:\n\n"
            f"{consulta}\n\n"
            "Para cada resultado encontrado:\n"
            "1. Documento relevante\n"
            "2. Score de relevancia\n"
            "3. Trecho relevante do documento\n"
            "4. Link/Caminho do documento\n\n"
            "Ao final, forneca um resumo da resposta para a consulta."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "knowledge_agent", "resultado_pesquisa": result}

    def gerar_resposta(self, contexto: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base no contexto dos documentos indexados abaixo, gere "
            "uma resposta detalhada:\n\n"
            f"{contexto}\n\n"
            "A resposta deve:\n"
            "1. Responder diretamente a pergunta do usuario\n"
            "2. Citar os documentos fonte utilizados\n"
            "3. Incluir referencias e secoes especificas\n"
            "4. Destacar informacoes criticas\n"
            "5. Sugerir documentos relacionados para leitura adicional"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "knowledge_agent", "resposta_rag": result}
