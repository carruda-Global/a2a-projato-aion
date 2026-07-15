from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class WorkSynopsisAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em geracao de resumos de tarefas e "
            "defeitos para obras de construcao civil. Sua funcao e analisar "
            "relatorios de obra, registros de defeitos e atualizacoes de "
            "cronograma para produzir resumos claros e acionaveis. "
            "Capture contexto, riscos e prazos criticos."
        )

    def generate_synopsis(self, task_data: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise os dados de tarefa/defeito abaixo e gere um resumo "
            "estruturado:\n\n"
            f"{task_data}\n\n"
            "Inclua:\n"
            "1. Resumo da tarefa/defeito\n"
            "2. Impacto no cronograma\n"
            "3. Responsavel designado\n"
            "4. Prioridade (alta/media/baixa)\n"
            "5. Prazo recomendado\n"
            "6. Riscos associados\n"
            "7. Acoes necessarias"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "work_synopsis", "synopsis": result}

    def summarize_project_status(self, project_updates: str, lang: str = "pt") -> str:
        prompt = (
            "Com base nas atualizacoes do projeto abaixo, gere um resumo "
            "executivo do status atual da obra:\n\n"
            f"{project_updates}\n\n"
            "Inclua:\n"
            "1. Progresso geral (%)\n"
            "2. Marcos concluidos no periodo\n"
            "3. Pendenciais criticas\n"
            "4. Riscos identificados\n"
            "5. Proximos passos"
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)
