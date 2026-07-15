LANG_CODES = {
    "pt": "pt-BR",
    "en": "en-US",
    "es": "es-ES",
}

LANG_NAMES = {
    "pt": "Português (Brasil)",
    "en": "English (US)",
    "es": "Español",
}


def get_system_prompt_instruction(lang: str = "pt") -> str:
    instructions = {
        "pt": (
            "Você DEVE responder em português do Brasil. "
            "Use terminologia técnica em português conforme normas brasileiras (NR, NBR, ABNT, MTE, CGU, ANPD, SBCE, etc). "
            "Mantenha nomes de leis e órgãos regulatórios brasileiros no original."
        ),
        "en": (
            "You MUST respond in English. "
            "Keep Brazilian regulatory terms (NR, NBR, ABNT, MTE, CGU, ANPD, SBCE, etc) and law names in their original Portuguese. "
            "Provide translations in parentheses when first mentioned."
        ),
        "es": (
            "Debe responder en español. "
            "Mantenga los términos regulatorios brasileños (NR, NBR, ABNT, MTE, CGU, ANPD, SBCE, etc) "
            "y nombres de leyes en su portugués original. Proporcione traducciones entre paréntesis en la primera mención."
        ),
    }
    return instructions.get(lang, instructions["pt"])


def get_agent_label(agent_id: str, lang: str = "pt") -> str:
    labels = {
        "spec_analyst": {"pt": "Analisador de Especificações Técnicas", "en": "Specification Analyst", "es": "Analizador de Especificaciones Técnicas"},
        "procurement": {"pt": "Processador de Compras", "en": "Procurement Processor", "es": "Procesador de Compras"},
        "inventory": {"pt": "Gestor de Estoque", "en": "Inventory Manager", "es": "Gestor de Inventario"},
        "logistics": {"pt": "Rastreador Logístico", "en": "Logistics Tracker", "es": "Rastreador Logístico"},
        "field_execution": {"pt": "Execução de Campo", "en": "Field Execution", "es": "Ejecución en Campo"},
        "bim_coordinator": {"pt": "Coordenador BIM", "en": "BIM Coordinator", "es": "Coordinador BIM"},
        "requirements_analyst": {"pt": "Analisador de Requisitos", "en": "Requirements Analyst", "es": "Analizador de Requisitos"},
        "engineering_assistant": {"pt": "Assistente de Engenharia", "en": "Engineering Assistant", "es": "Asistente de Ingeniería"},
        "work_synopsis": {"pt": "Resumidor de Tarefas", "en": "Work Synopsis", "es": "Resumidor de Tareas"},
        "photo_intelligence": {"pt": "Inteligência Visual de Obras", "en": "Photo Intelligence", "es": "Inteligencia Visual de Obras"},
        "rfi_creation": {"pt": "Criação de RFIs", "en": "RFI Creation", "es": "Creación de RFI"},
        "compliance": {"pt": "Agente de Conformidade", "en": "Compliance Agent", "es": "Agente de Cumplimiento"},
        "nr1_psicossocial": {"pt": "NR-1 Riscos Psicossociais", "en": "NR-1 Psychosocial Risks", "es": "NR-1 Riesgos Psicosociales"},
        "tributario_cbs_ibs": {"pt": "Tributário CBS/IBS", "en": "CBS/IBS Tax Compliance", "es": "Cumplimiento Tributario CBS/IBS"},
        "lgpd_operacional": {"pt": "LGPD Operacional", "en": "LGPD Operational", "es": "LGPD Operacional"},
        "esg_ifrs": {"pt": "ESG IFRS S1/S2", "en": "ESG IFRS S1/S2", "es": "ESG IFRS S1/S2"},
        "inventario_carbono": {"pt": "Inventário de Carbono", "en": "Carbon Inventory", "es": "Inventario de Carbono"},
        "escopo3_fornecedores": {"pt": "Escopo 3 Fornecedores", "en": "Scope 3 Suppliers", "es": "Alcance 3 Proveedores"},
        "canal_denuncias": {"pt": "Canal de Denúncias", "en": "Whistleblower Channel", "es": "Canal de Denuncias"},
        "igualdade_salarial": {"pt": "Igualdade Salarial", "en": "Pay Equity", "es": "Igualdad Salarial"},
        "compliance_anticorrupcao": {"pt": "Compliance Anticorrupção", "en": "Anti-Corruption Compliance", "es": "Cumplimiento Anticorrupción"},
    }
    return labels.get(agent_id, {}).get(lang, labels.get(agent_id, {}).get("pt", agent_id))
