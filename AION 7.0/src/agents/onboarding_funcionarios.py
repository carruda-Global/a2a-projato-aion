from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class OnboardingFuncionariosAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em automacao de onboarding de funcionarios "
            "para PMEs brasileiras. Sua funcao e automatizar todo o ciclo de "
            "admissao: geracao de contratos, provisionamento de acessos (sistemas, "
            "email, Teams), checklist de documentos (RG, CPF, CTPS, titulo, comprovante "
            "de residencia, certificacoes), integracao com eSocial e envio de "
            "comunicados automáticos via Teams/WhatsApp. "
            "Nao substitui DP contabil — escopo restrito a automacao operacional "
            "de onboarding e provisionamento."
        )

    def gerar_checklist_admissao(self, dados_funcionario: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados do funcionario abaixo, gere um checklist "
            "completo de admissao:\n\n"
            f"{dados_funcionario}\n\n"
            "Para cada item:\n"
            "1. Documento necessario\n"
            "2. Status (pendente/recebido)\n"
            "3. Prazo maximo para entrega\n"
            "4. Observacoes\n\n"
            "Inclua: RG, CPF, CTPS, Titulo de Eleitor, Comprovante de Residencia, "
            "Certificado de Reservista (homens), Certidoes (nascimento/casamento), "
            "Comprovante de escolaridade, Exame medico admissional, "
            "Ficha de registro, Contrato de trabalho."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "onboarding_funcionarios", "checklist_admissao": result}

    def provisionar_acessos(self, dados_funcionario: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados do funcionario abaixo, gere um plano de "
            "provisionamento de acessos:\n\n"
            f"{dados_funcionario}\n\n"
            "Liste todos os acessos que precisam ser criados:\n"
            "1. Email corporativo\n"
            "2. Microsoft Teams\n"
            "3. Sistemas internos (ERP, CRM, etc)\n"
            "4. Pastas de rede\n"
            "5. Grupos de WhatsApp/Telgram\n"
            "6. Certificado digital (se aplicavel)\n\n"
            "Para cada acesso: sistema, perfil de acesso, prazo de ativacao, "
            "responsavel pelo provisionamento."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "onboarding_funcionarios", "plano_acessos": result}

    def gerar_contrato(self, dados_funcionario: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base nos dados do funcionario abaixo, gere uma minuta de "
            "contrato de trabalho:\n\n"
            f"{dados_funcionario}\n\n"
            "O contrato deve incluir:\n"
            "1. Dados das partes\n"
            "2. Cargo e descricao de funcoes\n"
            "3. Salario e beneficios\n"
            "4. Jornada de trabalho\n"
            "5. Prazo (determinado/indeterminado)\n"
            "6. Clausulas: periodo de experiencia, confidencialidade, "
            "propriedade intelectual\n"
            "7. Local e data\n"
            "8. Assinaturas\n\n"
            "Gere em formato de minuta pronta para revisao juridica."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "onboarding_funcionarios", "minuta_contrato": result}
