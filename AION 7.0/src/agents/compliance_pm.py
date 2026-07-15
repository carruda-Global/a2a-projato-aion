from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class CompliancePMAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um gerente de projetos de compliance especializado em "
            "gestao de projetos regulatorios como Inventario de "
            "Carbono e Igualdade Salarial. Cria tarefas automaticas no Microsoft "
            "Planner, gerencia prazos e envia alertas via Microsoft Teams. "
            "Acompanhe o cronograma de projetos de conformidade regulatoria "
            "e garanta a entrega no prazo."
        )

    def gerenciar_projeto(self, projeto: str, lang: str = "pt") -> dict:
        prompt = (
            "Gerencie o projeto de compliance abaixo:\n\n"
            f"{projeto}\n\n"
            "Para este projeto:\n"
            "1. Defina o escopo e objetivos\n"
            "2. Crie um cronograma com marcos (milestones)\n"
            "3. Identifique recursos necessarios\n"
            "4. Atribua responsaveis por etapa\n"
            "5. Defina indicadores de sucesso (KPIs)\n"
            "6. Identifique riscos do projeto e planos de contingencia"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "compliance_pm", "plano_projeto": result}

    def criar_tarefa_planner(self, tarefa: str, lang: str = "pt") -> dict:
        prompt = (
            "Crie uma tarefa no Microsoft Planner com base na descricao abaixo:\n\n"
            f"{tarefa}\n\n"
            "Detalhes da tarefa:\n"
            "1. Titulo da tarefa\n"
            "2. Descricao detalhada\n"
            "3. Prioridade (alta / media / baixa)\n"
            "4. Data de vencimento\n"
            "5. Responsavel\n"
            "6. Bucket no Planner\n"
            "7. Checklist de subtarefas\n"
            "8. Anexos e referencias"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "compliance_pm", "tarefa_planner": result}

    def monitorar_prazos(self, projetos: str, lang: str = "pt") -> dict:
        prompt = (
            "Monitore os prazos dos seguintes projetos de compliance:\n\n"
            f"{projetos}\n\n"
            "Para cada projeto:\n"
            "1. Status atual (no prazo / atrasado / critico)\n"
            "2. Dias restantes para o prazo final\n"
            "3. Entregas pendentes\n"
            "4. Riscos de atraso\n"
            "5. Alertas a serem enviados via Teams\n"
            "6. Acoes corretivas recomendadas"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "compliance_pm", "monitoramento_prazos": result}
