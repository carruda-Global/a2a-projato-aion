from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
    AgentProvider,
    AgentInterface,
    APIKeySecurityScheme,
    SecurityScheme,
)


def build_agent_card(base_url: str | None = None) -> AgentCard:
    jsonrpc_url = f"{base_url}/a2a/jsonrpc" if base_url else "/a2a/jsonrpc"
    rest_url = f"{base_url}/a2a/rest" if base_url else "/a2a/rest"

    card = AgentCard(
        name="EcoSystem AEC — 86 AI Compliance Agents",
        description=(
            "86 AI compliance agents covering EU AI Act, CSRD, DORA, NIS2, LGPD, GDPR, "
            "SOC2, ISO27001, NR-1, ESG, M&A Due Diligence, Vendor Risk, Whistleblower "
            "(EU Dir 2019/1937), Contract Risk, Regulatory Monitoring (50+ jurisdictions), "
            "and AEC (Architecture, Engineering & Construction). Available in 8 languages. "
            "Starting at $99/month. Microsoft Azure Marketplace & Google Cloud Marketplace."
        ),
        version="7.0.0",
        documentation_url="https://engenheiro-producao-ai.onrender.com/docs",
        icon_url=f"{base_url}/static/logo.png" if base_url else "/static/logo.png",
    )

    prov = AgentProvider(
        organization="Global Match Engenharia",
        url="https://global-engenharia.com",
    )
    card.provider.CopyFrom(prov)

    cap = AgentCapabilities(
        streaming=True,
        push_notifications=False,
    )
    card.capabilities.CopyFrom(cap)

    api_key_scheme = APIKeySecurityScheme(
        name="X-API-Key",
        location="header",
    )
    scheme = SecurityScheme()
    scheme.api_key_security_scheme.CopyFrom(api_key_scheme)
    card.security_schemes["api_key"].MergeFrom(scheme)

    card.default_input_modes.append("text")
    card.default_output_modes.append("text")

    _add_skill(
        card,
        id="spec_analysis",
        name="Analisador de Especificações Técnicas",
        description=(
            "Analisa documentos de engenharia (plantas, memoriais, normas) "
            "para extrair requisitos técnicos, identificar contradições e "
            "sinalizar não-conformidades com normas como NBR-6118, NBR-9050."
        ),
        tags=["engenharia", "normas", "documentos", "conformidade"],
        examples=[
            "Analise esta especificação de concreto armado conforme NBR-6118",
            "Verifique não-conformidades neste memorial descritivo",
        ],
    )
    _add_skill(
        card,
        id="procurement",
        name="Processador de Compras",
        description=(
            "Processa pedidos de compra, compara cotações de fornecedores, "
            "gera requisições e otimiza custos de aquisição para obras."
        ),
        tags=["compras", "suprimentos", "fornecedores", "cotação"],
        examples=[
            "Processe pedido de 100 sacos de cimento CP-II",
            "Compare estas cotações e recomende a melhor opção",
        ],
    )
    _add_skill(
        card,
        id="inventory",
        name="Gestor de Estoque de Obra",
        description=(
            "Monitora níveis de estoque em tempo real, identifica itens "
            "em falta, sugere substitutos técnicos e calcula ressuprimento."
        ),
        tags=["estoque", "materiais", "substitutos", "obra"],
        examples=[
            "Verifique o estoque de aço CA-50 e sugira reposição",
            "Preciso de um substituto para cimento CP-II com mesma resistência",
        ],
    )
    _add_skill(
        card,
        id="logistics",
        name="Rastreador Logístico",
        description=(
            "Acompanha envios de materiais, identifica problemas de entrega, "
            "gera alertas de atraso e sugere rotas alternativas."
        ),
        tags=["logística", "entregas", "transporte", "rastreamento"],
        examples=[
            "Rastreie o envio do pedido de materiais para a obra X",
            "Verifique problemas nas entregas programadas para esta semana",
        ],
    )
    _add_skill(
        card,
        id="field_execution",
        name="Gerador de Instruções de Campo",
        description=(
            "Traduz modelos BIM e plantas em instruções claras para "
            "trabalhadores em campo. Identifica desvios de projeto e "
            "reduz retrabalho na execução de obras."
        ),
        tags=["obra", "campo", "execução", "BIM", "instruções"],
        examples=[
            "Gere instruções de execução para esta laje conforme projeto",
            "Compare o executado com o projetado e aponte desvios",
        ],
    )
    _add_skill(
        card,
        id="bim_coordination",
        name="Coordenador BIM",
        description=(
            "Cria elementos 3D via comandos de texto, realiza clash detection "
            "entre disciplinas e valida modelos BIM contra especificacoes."
        ),
        tags=["BIM", "3D", "clash", "modelagem"],
        examples=[
            "Crie uma parede de concreto de 3m x 2.8m com espessura de 15cm",
            "Detecte conflitos entre o projeto estrutural e hidraulico",
        ],
    )
    _add_skill(
        card,
        id="requirements_analysis",
        name="Analisador de Requisitos",
        description=(
            "Avalia requisitos de engenharia contra padroes de qualidade, "
            "gera scores, identifica ambiguidades e sugere melhorias."
        ),
        tags=["requisitos", "qualidade", "normas", "ISO"],
        examples=[
            "Analise a qualidade destes requisitos de fundacao",
            "Verifique consistencia entre os conjuntos de requisitos A e B",
        ],
    )
    _add_skill(
        card,
        id="engineering_assistant",
        name="Assistente de Engenharia",
        description=(
            "Assistente conversacional que responde perguntas tecnicas, "
            "busca informacoes em documentos e sumariza textos longos."
        ),
        tags=["chat", "perguntas", "documentos", "sumario"],
        examples=[
            "O que diz a NBR-6118 sobre cobrimento de armadura?",
            "Sumarize este memorial descritivo de 50 paginas",
        ],
    )
    _add_skill(
        card,
        id="work_synopsis",
        name="Resumidor de Tarefas",
        description=(
            "Gera resumos estruturados de tarefas e defeitos de obra, "
            "capturando contexto, riscos e prazos criticos."
        ),
        tags=["tarefas", "defeitos", "resumo", "cronograma"],
        examples=[
            "Resuma esta lista de defeitos da vistoria da obra",
            "Gere um resumo de status semanal do projeto",
        ],
    )
    _add_skill(
        card,
        id="photo_intelligence",
        name="Inteligencias Visual de Obras",
        description=(
            "Analisa fotos de obras para identificar elementos construtivos, "
            "detectar riscos de seguranca e comparar com cronograma."
        ),
        tags=["fotos", "visao", "seguranca", "EPI", "cronograma"],
        examples=[
            "Analise esta foto do canteiro de obras e identifique riscos",
            "Compare o progresso visual com o cronograma esperado",
        ],
    )
    _add_skill(
        card,
        id="rfi_creation",
        name="Criador de RFIs",
        description=(
            "Gera RFIs (Request for Information) profissionais a partir "
            "de duvidas do campo, buscando em especificacoes tecnicas."
        ),
        tags=["RFI", "documentacao", "especificacao", "consulta"],
        examples=[
            "Crie uma RFI sobre a especificacao do concreto da fundacao",
            "Busque nesta especificacao a resistencia requerida para o aco",
        ],
    )
    _add_skill(
        card,
        id="compliance",
        name="Agente de Conformidade",
        description=(
            "Monitora conformidade legal, gera documentacao, emite alertas "
            "sobre prazos regulatorios e obrigacoes ambientais."
        ),
        tags=["conformidade", "regulatorio", "ambiental"],
        examples=[
            "Verifique a conformidade deste projeto com a legislacao ambiental",
            "Gere um relatorio de conformidade para esta obra",
        ],
    )
    _add_skill(
        card,
        id="nr1_psicossocial",
        name="NR-1 Riscos Psicossociais",
        description=(
            "Identifica, avalia e documenta Fatores de Riscos Psicossociais "
            "(FRPRT) conforme NR-1/Portaria MTE 1.419/2024. Aplica metodologias "
            "COPSOQ, JCQ, PHQ-9 e GAD-7. Gera inventarios, planos de acao e "
            "relatorios executivos para fiscalizacao."
        ),
        tags=["NR-1", "psicossocial", "saude mental", "MTE", "SESMT"],
        examples=[
            "Avalie os riscos psicossociais da empresa com 150 funcionarios",
            "Gere um inventario de FRPRT conforme NR-1",
        ],
    )
    _add_skill(
        card,
        id="tributario_cbs_ibs",
        name="Tributario CBS/IBS",
        description=(
            "Auxilia na conformidade com a reforma tributaria CBS/IBS "
            "(LC 214/2025). Classifica produtos/servicos com NCM e aliquotas, "
            "gera declaracoes DeRE e simula impacto financeiro da transicao."
        ),
        tags=["tributario", "CBS", "IBS", "reforma tributaria", "Receita Federal"],
        examples=[
            "Classifique este produto conforme CBS/IBS",
            "Simule o impacto da transicao tributaria",
        ],
    )
    _add_skill(
        card,
        id="lgpd_operacional",
        name="LGPD Operacional",
        description=(
            "Mapeia fluxos de dados pessoais, gera RoPA conforme ANPD, "
            "identifica lacunas de base legal e monitora incidentes "
            "com notificacao a ANPD. Foco em adequacao de PMEs a LGPD."
        ),
        tags=["LGPD", "privacidade", "dados", "ANPD", "RoPA"],
        examples=[
            "Mapeie os fluxos de dados da minha empresa",
            "Gere o RoPA completo conforme modelo ANPD",
        ],
    )
    _add_skill(
        card,
        id="esg_ifrs",
        name="ESG IFRS S1/S2",
        description=(
            "Diagnostico de maturidade ESG, mapeamento de indicadores "
            "materiais SASB, geracao de relatorios de sustentabilidade "
            "alinhados ao IFRS S1/S2 e resposta a questionarios ESG "
            "de clientes corporativos."
        ),
        tags=["ESG", "IFRS", "sustentabilidade", "CVM", "SASB"],
        examples=[
            "Diagnostique a maturidade ESG da minha empresa",
            "Gere um relatorio de sustentabilidade IFRS S1",
        ],
    )
    _add_skill(
        card,
        id="inventario_carbono",
        name="Inventario de Carbono",
        description=(
            "Calcula emissoes de GEE Escopo 1 e 2 conforme GHG Protocol "
            "e Lei 15.042/2024 (SBCE). Gera inventarios completos com "
            "trilha de auditoria e identifica hotspots de reducao."
        ),
        tags=["carbono", "GEE", "SBCE", "GHG Protocol", "clima"],
        examples=[
            "Calcule as emissoes de carbono da minha empresa",
            "Gere o inventario GHG Protocol completo",
        ],
    )
    _add_skill(
        card,
        id="escopo3_fornecedores",
        name="Escopo 3 Fornecedores",
        description=(
            "Rastreia emissoes de Escopo 3 na cadeia de fornecedores, "
            "consolida as 15 categorias do GHG Protocol, gera scores "
            "de maturidade ESG por fornecedor e relatorios IFRS S2/CBAM."
        ),
        tags=["escopo3", "fornecedores", "cadeia", "CBAM", "IFRS S2"],
        examples=[
            "Avalie as emissoes Escopo 3 dos meus fornecedores",
            "Gere relatorio de cadeia conforme IFRS S2",
        ],
    )
    _add_skill(
        card,
        id="canal_denuncias",
        name="Canal de Denuncias",
        description=(
            "Canal omnichannel (WhatsApp, web, email) com anonimato garantido. "
            "Triagem automatica por categoria, fluxo de investigacao e "
            "relatorios semestrais para CIPA. Integracao com NR-1."
        ),
        tags=["denuncias", "CIPA", "assedio", "Lei 14.457", "ouvidoria"],
        examples=[
            "Configure o canal de denuncias da empresa",
            "Classifique esta denuncia recebida",
        ],
    )
    _add_skill(
        card,
        id="igualdade_salarial",
        name="Igualdade Salarial",
        description=(
            "Analisa equidade salarial por cargo/genero/raca conforme "
            "Lei 14.611/2023. Gera relatorios semestrais no formato "
            "MTE/Portal Emprega Brasil e planos de acao."
        ),
        tags=["igualdade salarial", "diversidade", "MTE", "genero", "inclusao"],
        examples=[
            "Analise a equidade salarial da folha de pagamento",
            "Gere o relatorio semestral para o MTE",
        ],
    )
    _add_skill(
        card,
        id="compliance_anticorrupcao",
        name="Compliance Anticorrupcao",
        description=(
            "Estrutura programas de integridade conforme Lei 12.846/2013 "
            "e Decreto 11.129/2022. Diagnosticos CGU, codigos de etica, "
            "due diligence de terceiros e relatorios para licitacoes."
        ),
        tags=["anticorrupcao", "integridade", "CGU", "licitacoes", "etica"],
        examples=[
            "Estruture o programa de integridade da empresa",
            "Realize due diligence deste fornecedor",
        ],
    )
    _add_skill(
        card,
        id="regulatory_analyst",
        name="Regulatory Analyst",
        description=(
            "Analisa contratos, politicas e documentos legais via SharePoint "
            "e OneDrive. Identifica riscos LGPD, NR-1, ESG e Anticorrupcao. "
            "Gera relatorios de risco com matriz de probabilidade e impacto."
        ),
        tags=["regulatorio", "contratos", "LGPD", "NR-1", "ESG", "riscos"],
        examples=[
            "Analise este contrato para riscos regulatorios",
            "Identifique riscos LGPD neste documento",
        ],
    )
    _add_skill(
        card,
        id="compliance_pm",
        name="Compliance PM",
        description=(
            "Gerencia projetos de compliance como Carbono e Igualdade "
            "Salarial. Cria tarefas automaticas no Microsoft Planner e envia "
            "alertas e prazos via Microsoft Teams."
        ),
        tags=["compliance", "projetos", "Planner", "Teams", "prazos"],
        examples=[
            "Gerencie o projeto de inventario de carbono",
            "Crie tarefa no Planner para compliance",
        ],
    )
    _add_skill(
        card,
        id="channel_agent",
        name="Channel Agent Regulatorio",
        description=(
            "Monitora canais do Microsoft Teams para detectar riscos de "
            "conformidade. Identifica conversas com riscos trabalhistas e "
            "tributarios. Gera alertas automaticos de compliance."
        ),
        tags=["Teams", "monitoramento", "riscos", "trabalhista", "tributario"],
        examples=[
            "Monitore conversas do Teams por riscos trabalhistas",
            "Detecte riscos de compliance nestas mensagens",
        ],
    )
    _add_skill(
        card,
        id="knowledge_agent",
        name="Knowledge Agent",
        description=(
            "Indexa documentos do SharePoint com metadados e disponibiliza "
            "busca inteligente via RAG (Retrieval-Augmented Generation). "
            "Responde perguntas com base em documentos indexados."
        ),
        tags=["conhecimento", "SharePoint", "RAG", "busca", "indexacao"],
        examples=[
            "Indexe este documento para busca",
            "Pesquise sobre politicas de compliance",
        ],
    )
    _add_skill(
        card,
        id="facilitator_agent",
        name="Facilitator Agent",
        description=(
            "Facilita reunioes do comite de compliance, gera atas e minutas "
            "detalhadas. Integra-se ao Teams Meetings e cria tarefas "
            "automaticas no Planner apos cada reuniao."
        ),
        tags=["reunioes", "atas", "compliance", "Teams", "Planner"],
        examples=[
            "Facilite a reuniao do comite de compliance",
            "Gere a minuta da ultima reuniao",
        ],
    )
    _add_skill(
        card,
        id="dev_experience",
        name="Dev Experience Agent",
        description=(
            "Automatiza revisoes de Pull Requests e code reviews no GitHub. "
            "Garante conformidade LGPD no codigo, identifica vazamento de "
            "dados e gera relatorios de qualidade do repositorio."
        ),
        tags=["DevEx", "GitHub", "PR", "code review", "LGPD", "qualidade"],
        examples=[
            "Revise este Pull Request para conformidade LGPD",
            "Gere relatorio de qualidade do repositorio",
        ],
    )
    _add_skill(
        card,
        id="onboarding_funcionarios",
        name="Onboarding de Funcionarios",
        description=(
            "Automatiza o ciclo completo de admissao de funcionarios: "
            "geracao de contratos, checklist de documentos (RG, CPF, CTPS), "
            "provisionamento de acessos (email, Teams, sistemas), integracao "
            "com eSocial e envio de comunicados via Teams/WhatsApp. "
            "Foco em PMEs brasileiras com 50-500 funcionarios."
        ),
        tags=["RH", "admissao", "onboarding", "contratos", "eSocial"],
        examples=[
            "Gere o checklist de admissao para um novo funcionario",
            "Provisione acessos para o novo colaborador no Teams e sistemas",
        ],
    )
    _add_skill(
        card,
        id="atendimento_cliente_ptbr",
        name="Atendimento ao Cliente PT-BR",
        description=(
            "Resolve tickets de atendimento nivel 1 (L1) automaticamente "
            "via WhatsApp e Microsoft Teams em portugues brasileiro. "
            "Cobre duvidas sobre produtos, status de pedidos, agendamentos, "
            "cancelamentos e FAQs. Escala para L2 com contexto quando necessario."
        ),
        tags=["atendimento", "suporte", "WhatsApp", "Teams", "FAQ"],
        examples=[
            "Responda este ticket de atendimento sobre status de pedido",
            "Classifique este ticket e sugira a melhor resposta",
        ],
    )
    _add_skill(
        card,
        id="conciliacao_financeira",
        name="Conciliacao Financeira",
        description=(
            "Automatiza o fechamento mensal com conciliacao de notas fiscais "
            "(NFe/NFCe) com extratos bancarios, conciliacao de faturas de "
            "cartao de credito e boletos emitidos vs pagos. Identifica "
            "divergencias e gera relatorios executivos de fechamento. "
            "Padroes brasileiros: PIX, TED, boleto, cartao."
        ),
        tags=["financeiro", "conciliacao", "NF", "fechamento", "contabilidade"],
        examples=[
            "Concilie estas notas fiscais com o extrato bancario do mes",
            "Gere relatorio de fechamento mensal com divergencias",
        ],
    )

    # ── Agentes compliance global (EcoSystem AEC 7.0) ────────────────────────
    _add_skill(card, id="eu_ai_act", name="EU AI Act Readiness",
        description="Risk classification, technical documentation and conformity assessment for high-risk AI systems. August 2026 deadline.",
        tags=["EU AI Act", "AI governance", "compliance", "2026"], examples=["Classify my AI system risk level", "Generate technical documentation for EU AI Act"])
    _add_skill(card, id="csrd_reporting", name="CSRD Sustainability Reporting",
        description="Double materiality assessment, ESRS gap analysis and sustainability reports for 50,000+ EU companies required to report.",
        tags=["CSRD", "ESG", "sustainability", "ESRS", "EU"], examples=["Run CSRD double materiality assessment", "Generate ESRS E1 climate report"])
    _add_skill(card, id="dora_compliance", name="DORA Compliance",
        description="Digital Operational Resilience Act compliance for financial entities. ICT risk management, incident reporting, TLPT.",
        tags=["DORA", "fintech", "resilience", "EU", "financial"], examples=["DORA gap analysis for our bank", "Generate ICT incident report"])
    _add_skill(card, id="nis2_compliance", name="NIS2 Directive",
        description="NIS2 scope determination, cybersecurity implementation roadmap and incident notification for essential/important entities.",
        tags=["NIS2", "cybersecurity", "EU", "incident"], examples=["Am I in scope for NIS2?", "Generate NIS2 implementation roadmap"])
    _add_skill(card, id="vendor_risk", name="Vendor Risk Assessment",
        description="Third-party risk scoring, portfolio scan and due diligence reports for supplier compliance.",
        tags=["vendor risk", "third party", "supply chain", "due diligence"], examples=["Assess vendor risk for this supplier", "Run portfolio risk scan"])
    _add_skill(card, id="ma_due_diligence", name="M&A Due Diligence",
        description="Compliance check and sanctions screening for mergers and acquisitions.",
        tags=["M&A", "due diligence", "sanctions", "acquisition"], examples=["Run compliance DD for this acquisition target", "Screen for sanctions exposure"])
    _add_skill(card, id="whistleblower", name="Whistleblower Management",
        description="EU Directive 2019/1937 compliant whistleblower case management with anonymous reporting and investigation workflows.",
        tags=["whistleblower", "EU Directive 2019/1937", "ethics", "reporting"], examples=["Set up whistleblower channel", "Check EU whistleblower compliance"])
    _add_skill(card, id="contract_risk", name="Contract Risk Analysis",
        description="Contract risk scoring, DPA (Data Processing Agreement) compliance check and clause flagging.",
        tags=["contracts", "DPA", "GDPR", "risk", "legal"], examples=["Analyze this contract for compliance risks", "Check DPA against GDPR requirements"])
    _add_skill(card, id="regulatory_monitor", name="Regulatory Monitor",
        description="Real-time regulatory change monitoring across 50+ jurisdictions with impact analysis and automated alerts.",
        tags=["regulatory", "monitoring", "global", "alerts", "jurisdictions"], examples=["What changed in EU regulation last week?", "Impact analysis of new DORA guideline"])
    _add_skill(card, id="board_reporting", name="Board ESG Reporting",
        description="Executive ESG dashboards and audit committee reports for board-level compliance oversight.",
        tags=["ESG", "board", "reporting", "audit", "executive"], examples=["Generate board compliance report", "Create audit committee ESG summary"])
    _add_skill(card, id="soc2_assessment", name="SOC2 Type II Assessment",
        description="SOC2 Type II gap analysis, control mapping and audit readiness for US enterprise clients.",
        tags=["SOC2", "audit", "security", "US", "enterprise"], examples=["SOC2 Type II gap analysis", "Map controls to SOC2 trust criteria"])
    _add_skill(card, id="iso27001", name="ISO 27001:2022 Compliance",
        description="ISO 27001:2022 gap analysis, ISMS implementation and certification readiness.",
        tags=["ISO27001", "ISMS", "security", "certification"], examples=["ISO 27001 gap analysis", "Generate ISMS policy documents"])

    # ── AI Voice Receptionist (2026-07 pivot, agent #64) ─────────────────────
    _add_skill(card, id="voice_receptionist", name="AI Voice Receptionist",
        description=(
            "AI phone receptionist that answers business calls 24/7, instantly texts back "
            "missed calls, and captures every caller as a lead (name, number, reason for "
            "calling). Self-service setup, live in under 20 minutes, no developer needed. "
            "Starter: $89/mo, 300 min, 1 line. Growth: $179/mo, 750 min, 2 lines/locations. "
            "US/UK/CA/AU markets."
        ),
        tags=["voice AI", "receptionist", "phone", "missed call", "small business", "lead capture"],
        examples=["Set up an AI receptionist for my dental clinic", "What happens when a call is missed after hours?"])

    iface_jsonrpc = AgentInterface(
        protocol_binding="JSONRPC",
        protocol_version="1.0",
        url=jsonrpc_url,
    )
    card.supported_interfaces.append(iface_jsonrpc)

    iface_rest = AgentInterface(
        protocol_binding="HTTP+JSON",
        protocol_version="1.0",
        url=rest_url,
    )
    card.supported_interfaces.append(iface_rest)

    return card


def _add_skill(
    card: AgentCard,
    id: str,
    name: str,
    description: str,
    tags: list[str] | None = None,
    examples: list[str] | None = None,
):
    skill = AgentSkill(
        id=id,
        name=name,
        description=description,
        tags=tags or [],
        examples=examples or [],
        input_modes=["text"],
        output_modes=["text"],
    )
    card.skills.append(skill)
