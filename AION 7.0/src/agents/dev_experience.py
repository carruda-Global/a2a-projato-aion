from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class DevExperienceAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um agente de experiencia de desenvolvimento (DevEx) "
            "especializado em automatizar revisoes de Pull Requests (PRs) "
            "e code reviews. Garante conformidade com a LGPD (Lei 13.709/2018) "
            "no codigo fonte, identificando vazamento de dados pessoais, "
            "credenciais e informacoes sensiveis. Integra-se ao GitHub para "
            "PRs e ao Microsoft Teams para notificacoes. Gere relatorios de "
            "qualidade de repositorio com metricas e recomendacoes."
        )

    def revisar_pr(self, pr_data: str, lang: str = "pt") -> dict:
        prompt = (
            "Revise o Pull Request abaixo e forneça feedback detalhado:\n\n"
            f"{pr_data}\n\n"
            "Analise:\n"
            "1. Qualidade do codigo (legibilidade, boas praticas)\n"
            "2. Seguranca (vazamento de credenciais, SQL injection, XSS)\n"
            "3. Conformidade LGPD (dados pessoais no codigo)\n"
            "4. Performance (complexidade, gargalos)\n"
            "5. Testes (cobertura, qualidade dos testes)\n"
            "6. Documentacao (comentarios, docstrings)\n"
            "7. Sugestoes de melhoria\n"
            "8. Decisao final: aprovar / solicitar alteracoes / rejeitar"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "dev_experience", "revisao_pr": result}

    def verificar_compliance(self, codigo: str, lang: str = "pt") -> dict:
        prompt = (
            "Verifique a conformidade do codigo abaixo com a LGPD:\n\n"
            f"{codigo}\n\n"
            "Identifique:\n"
            "1. Dados pessoais sendo processados\n"
            "2. Bases legais aplicaveis (art. 7o ou art. 11 da LGPD)\n"
            "3. Violacoes de privacidade\n"
            "4. Ausencia de anonimizacao ou pseudonimizacao\n"
            "5. Logs que expoem dados pessoais\n"
            "6. Variaveis ou constantes com dados sensiveis\n"
            "7. Recomendacoes de correcao por linha de codigo"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "dev_experience", "verificacao_compliance": result}

    def gerar_relatorio_qualidade(self, repositorio: str, lang: str = "pt") -> dict:
        prompt = (
            "Gere um relatorio de qualidade para o repositorio abaixo:\n\n"
            f"{repositorio}\n\n"
            "O relatorio deve incluir:\n"
            "1. Resumo do repositorio (linguagens, frameworks, contributors)\n"
            "2. Metricas de qualidade (code coverage, complexidade ciclomatica)\n"
            "3. Saude do codigo (codigo morto, duplicacao, smells)\n"
            "4. Seguranca (dependencias vulneraveis, segredos expostos)\n"
            "5. Conformidade LGPD no codigo\n"
            "6. Qualidade das PRs (tamanho, frequencia, revisoes)\n"
            "7. Recomendacoes de melhoria\n"
            "8. Score geral de qualidade (0-100)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "dev_experience", "relatorio_qualidade": result}
