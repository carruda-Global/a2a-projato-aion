from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class FacilitatorAgentAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um agente facilitador de reunioes do comite de compliance "
            "especializado em conduzir reunioes, gerar atas detalhadas e criar "
            "minutas de reuniao. Integra-se ao Microsoft Teams para agendamento "
            "e gravacao de reunioes. Apos cada reuniao, gera automaticamente "
            "tarefas no Microsoft Planner com base nas decisoes tomadas. "
            "Garanta que todas as decisoes sejam registradas e acompanhadas."
        )

    def facilitar_reuniao(self, ata: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base na pauta da reuniao abaixo, facilite a conducao "
            "da reuniao do comite de compliance:\n\n"
            f"{ata}\n\n"
            "Estruture a reuniao:\n"
            "1. Abertura e verificacao de quorum\n"
            "2. Aprovacao da ata anterior\n"
            "3. Pontos de pauta com tempo estimado\n"
            "4. Discussao e deliberacao\n"
            "5. Encaminhamentos e responsaveis\n"
            "6. Proxima reuniao (data e pauta preliminar)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "facilitator_agent", "reuniao_estruturada": result}

    def gerar_minuta(self, discussao: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base na discussao abaixo, gere a minuta oficial da reuniao "
            "do comite de compliance:\n\n"
            f"{discussao}\n\n"
            "A minuta deve conter:\n"
            "1. Cabecalho (data, horario, local, participantes)\n"
            "2. Resumo das discussoes\n"
            "3. Decisoes tomadas\n"
            "4. Votacoes e resultados\n"
            "5. Responsaveis e prazos\n"
            "6. Pendencias e proximos passos\n"
            "7. Campo para assinaturas digitais"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "facilitator_agent", "minuta_reuniao": result}

    def criar_tarefas_planner(self, decisoes: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nas decisoes da reuniao abaixo, crie tarefas "
            "no Microsoft Planner:\n\n"
            f"{decisoes}\n\n"
            "Para cada decisao:\n"
            "1. Titulo da tarefa no Planner\n"
            "2. Descricao detalhada\n"
            "3. Responsavel designado\n"
            "4. Data de vencimento\n"
            "5. Prioridade\n"
            "6. Bucket (grupo de tarefas)\n"
            "7. Checklist de subtarefas\n"
            "8. Dependencias entre tarefas\n"
            "9. Lembrete via Teams"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "facilitator_agent", "tarefas_planner": result}
