import logging
from datetime import datetime
from integrations import LinkedInIntegration, LinkedInConfig
from workflows.engagement_feedback import registrar_publicacao

logger = logging.getLogger(__name__)

CALENDARIO = {
    0: {"agente": "NR-1 Psicossocial", "urgencia": "Multa ativa desde maio/2025 — sua empresa esta em risco", "gancho": "Portaria MTE 1.419/2024 ja esta sendo fiscalizada. Empresas sem inventario FRPRT estao sendo notificadas.", "solucao": "O agente NR-1 faz o inventario de riscos psicossociais, plano de acao e relatorios em 48h.", "cta": "Compliance Essencial R$ 590", "utm": "nr1"},
    1: {"agente": "LGPD Operacional", "urgencia": "ANPD autuou mais de 50 empresas em 2025 — voc tem RoPA?", "gancho": "A ANPD esta fiscalizando ativamente. Multas podem chegar a R$ 50 milhoes por infracao.", "solucao": "O agente LGPD mapeia dados, gera RoPA e mantem conformidade continua com a ANPD.", "cta": "Compliance Essencial R$ 590", "utm": "lgpd"},
    2: {"agente": "CBS/IBS Tributario", "urgencia": "Janela 2026-2027 fechando — seu NCM esta classificado?", "gancho": "A LC 214/2025 entra em vigor e sua empresa precisa classificar todos os produtos por NCM e gerar DeRE.", "solucao": "O agente CBS/IBS classifica NCM automaticamente, simula impacto fiscal e gera DeRE.", "cta": "Tributario R$ 390", "utm": "tributario"},
    3: {"agente": "ESG IFRS S1/S2", "urgencia": "Seu fornecedor europeu ja pediu relatorio de carbono?", "gancho": "IFRS S1/S2 exigem relatorios ESG auditaveis. Sem eles, voce perde contratos internacionais.", "solucao": "O agente ESG gera diagnostico, relatorios IFRS e calcula carbono Escopo 1/2.", "cta": "ESG+Carbono R$ 2.490", "utm": "esg"},
    4: {"agente": "Micro-agente M1", "urgencia": "Diagnostico NR-1 por R$ 99 — resultado em 48h", "gancho": "Comece com um diagnostico rapido de riscos psicossociais por apenas R$ 99. Sem compromisso.", "solucao": "O M1 Diagnostico Rapido NR-1 avalia sua empresa e entrega relatorio preliminar em 48h.", "cta": "Porta de entrada R$ 99", "utm": "micro-m1"},
}


NEWS = [
    {"titulo": "O que sao os 59 Agentes de IA do EcoSystem AION?", "texto": "Cada agente resolve UM problema especifico: NR-1 Psicossocial, LGPD, CBS/IBS, ESG, Carbono, Canal de Denuncias, Igualdade Salarial, Compliance, Microsoft 365, Salesforce, Dynamics, LinkedIn Sales.\n\nResultado em 48h. Trial gratis 15 dias.", "utm": "news-oquee"},
    {"titulo": "Por que sua empresa precisa de agentes de IA em 2026?", "texto": "NR-1 Psicossocial, CBS/IBS, Igualdade Salarial, ESG IFRS S1/S2 — 4 obrigacoes com multa ativa. Sem IA o custo e inviavel para PMEs. Com agentes, 48h.", "utm": "news-porque"},
    {"titulo": "NR-1 Psicossocial: o que muda com a Portaria MTE 1.419/2024", "texto": "Toda empresa com funcionarios CLT precisa fazer o inventario FRPRT. 82% dos RHs nao estao preparados. O agente NR-1 faz em 48h.", "utm": "news-nr1"},
    {"titulo": "LGPD: ANPD esta multando. Sua empresa esta protegida?", "texto": "Mais de 50 empresas autuadas em 2025. Multa de ate R$ 50 milhoes. O agente LGPD gera RoPA, mapeia dados e mantem conformidade continua.", "utm": "news-lgpd"},
    {"titulo": "Reforma Tributaria LC 214/2025: sua empresa esta pronta?", "texto": "CBS e IBS entram em vigor com penalidades a partir de agosto/2026. Classificacao NCM, DeRE, simulacao fiscal. O agente CBS/IBS resolve.", "utm": "news-cbs"},
    {"titulo": "ESG nao e mais opcional: IFRS S1/S2 e CBAM", "texto": "Seu fornecedor europeu ja pediu relatorio de carbono? Sem ESG voce perde contratos B2B. O agente ESG gera relatorios IFRS auditaveis.", "utm": "news-esg"},
    {"titulo": "Canal de Denuncias: obrigatorio para empresas com +100 funcionarios", "texto": "Lei 14.457/2022. Obrigatorio para CIPA, licitacoes e compliance trabalhista. O agente entrega canal omnichannel completo.", "utm": "news-denuncias"},
    {"titulo": "Igualdade Salarial: relatorio semestral obrigatorio", "texto": "Lei 14.611/2023. Multa de R$ 140,60 por funcionario por dia. O agente analisa equidade, gera relatorio MTE e plano de adequacao.", "utm": "news-igualdade"},
    {"titulo": "Como agentes de IA cortam custos de compliance em 80%", "texto": "Consultoria tradicional: R$ 15-50k por projeto, 4-8 semanas. Agente IA: R$ 390-590/mes, 48h. 59 especialistas por menos de 1 consultor.", "utm": "news-custo"},
    {"titulo": "Microsoft + IA: 6 agentes integrados ao Teams e SharePoint", "texto": "Regulatory Analyst, Compliance PM, Channel Agent, Knowledge Agent, Facilitator, Dev Experience. Tudo integrado ao M365.", "utm": "news-microsoft"},
]


DICAS = [
    {"titulo": "Dica rapida: 3 passos para comecar seu compliance hoje", "texto": "1. Diagnostico rapido NR-1 (R$ 99)\n2. Inventario FRPRT com o agente (48h)\n3. Plano de acao automatico\n\nResultado em 48h. Trial gratis.", "utm": "dica-comecar"},
    {"titulo": "Sabia que 1 agente de IA custa menos que 1 hora de consultoria?", "texto": "Consultoria: R$ 500-2.000/hora.\nAgente IA: R$ 99-590/mes.\n59 agentes 24/7 por menos de R$ 10k/mes.\n\nEficiencia que cabe no orcamento.", "utm": "dica-custo"},
    {"titulo": "Voce sabia? 82% dos profissionais de RH nao estao prontos para NR-1", "texto": "A Portaria MTE 1.419/2024 ja esta em vigor. Sem inventario FRPRT = multa. O agente NR-1 resolve em 48h.", "utm": "dica-rh"},
    {"titulo": "O segredo do compliance sem dor de cabeca", "texto": "Automatize o que e repetitivo. Foque no que e estrategico. 59 agentes trabalham enquanto voce dorme. Trial gratis 15 dias.", "utm": "dica-segredo"},
    {"titulo": "3 sinais de que sua empresa precisa de agentes de IA", "texto": "1. Passa mais de 4h/semana com burocracia\n2. Nao sabe se esta em conformidade com NR-1/LGPD\n3. Perdeu contrato por faltar relatorio ESG\n\nSe marcou 1+, temos o agente certo.", "utm": "dica-sinais"},
    {"titulo": "De PME a enterprise: como escalar compliance com IA", "texto": "Comece com R$ 99 (micro), evolua para R$ 590 (essencial), escale para R$ 1.490 (pro). Cada agente detecta a proxima obrigacao.", "utm": "dica-escalar"},
    {"titulo": "O que o CBAM significa para sua empresa?", "texto": "CBAM = Mecanismo de Ajuste de Fronteira de Carbono da UE. Se voce exporta para Europa, precisa rastrear Escopo 3. O agente Carbono faz.", "utm": "dica-cbam"},
    {"titulo": "Microsoft Copilot + EcoSystem AION: o combo definitivo", "texto": "Copilot para produtividade. EcoSystem para compliance. Juntos, 59 agentes regulam enquanto Copilot automatiza. Integracao nativa.", "utm": "dica-copilot"},
]


def gerar_post_calendario(dia_semana: int | None = None) -> tuple[str, str, str]:
    if dia_semana is None:
        dia_semana = datetime.now().weekday()
    if dia_semana > 4:
        dia_semana = 0
    tema = CALENDARIO[dia_semana]
    post = f"{tema['urgencia']}\n\n{tema['gancho']}\n\n{tema['solucao']}\n\nResultado em 48h\nSem implantacao\nTrial 15 dias gratis\n\nLink nos comentarios"
    comentario = f"https://global-engenharia.com/ecosystem?utm_source=linkedin&utm_medium=organic&utm_campaign={tema['utm']}&utm_content=post-{['seg','ter','qua','qui','sex'][dia_semana]}"
    return post, comentario, tema["cta"]


def gerar_post_news(indice: int = -1) -> tuple[str, str, str]:
    if indice < 0:
        indice = datetime.now().day % len(NEWS)
    item = NEWS[indice % len(NEWS)]
    post = f"{item['titulo']}\n\n{item['texto']}\n\nLink nos comentarios"
    comentario = f"https://global-engenharia.com/ecosystem?utm_source=linkedin&utm_medium=organic&utm_campaign={item['utm']}"
    return post, comentario, item["titulo"]


def gerar_post_dica(indice: int = -1) -> tuple[str, str, str]:
    if indice < 0:
        indice = (datetime.now().day + 5) % len(DICAS)
    item = DICAS[indice % len(DICAS)]
    post = f"{item['titulo']}\n\n{item['texto']}\n\nLink nos comentarios"
    comentario = f"https://global-engenharia.com/ecosystem?utm_source=linkedin&utm_medium=organic&utm_campaign={item['utm']}"
    return post, comentario, item["titulo"]


async def _publicar(linkedin: LinkedInIntegration, post_text: str, comment_text: str, tipo: str) -> dict:
    result = await linkedin.tools.create_post(text=post_text)
    if "error" not in result and result.get("post_id"):
        await linkedin.tools.create_comment(post_id=result["post_id"], text=comment_text)
    success = "error" not in result
    logger.info(f"Post {tipo}: {'OK' if success else 'FALHA'} - {result.get('url', '')}")
    if success:
        registrar_publicacao(result.get("post_id", ""), tipo, "post", result.get("url", ""))
    return {"tipo": tipo, "published": success, "post_url": result.get("url", "")}


async def run_content_workflow(linkedin: LinkedInIntegration | None = None, tipo: str = "calendario", indice: int = -1) -> dict:
    if not linkedin:
        li_config = LinkedInConfig()
        linkedin = LinkedInIntegration(config=li_config)
        await linkedin.initialize()
        own_li = True
    else:
        own_li = False

    try:
        if tipo == "calendario":
            post_text, comment_text, cta = gerar_post_calendario()
            result = await _publicar(linkedin, post_text, comment_text, tipo)
            result["tema"] = CALENDARIO.get(datetime.now().weekday(), {}).get("agente", "")
            result["cta"] = cta
        elif tipo == "news":
            post_text, comment_text, titulo = gerar_post_news(indice)
            result = await _publicar(linkedin, post_text, comment_text, tipo)
            result["tema"] = titulo
        elif tipo == "dica":
            post_text, comment_text, titulo = gerar_post_dica(indice)
            result = await _publicar(linkedin, post_text, comment_text, tipo)
            result["tema"] = titulo
        else:
            result = {"tipo": tipo, "published": False, "error": f"Unknown tipo: {tipo}"}

        result["completed_at"] = datetime.utcnow().isoformat()
        return result
    finally:
        if own_li:
            await linkedin.shutdown()
