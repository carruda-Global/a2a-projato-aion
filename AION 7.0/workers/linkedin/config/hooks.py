"""13 structural hook styles. Each takes a topic dict (see topics.py) and
returns a distinct post text. 24 topics x 13 hooks = 312 real variations —
combinatorial, not hand-written, so nothing repeats verbatim."""


def hook_stat_shock(t: dict) -> str:
    return f"Voce sabia? {t['fato'].capitalize()}.\n\n{t['produto']} resolve isso com base em {t['lei']} — resultado em 48h, sem implantacao.\n\nLink nos comentarios."


def hook_question(t: dict) -> str:
    return f"Sua empresa ja verificou isso: {t['fato']}?\n\nSe a resposta for nao, o agente {t['produto']} faz o diagnostico completo ({t['lei']}) em 48h.\n\nLink nos comentarios."


def hook_myth_fact(t: dict) -> str:
    return f"Mito: compliance com {t['lei']} pode esperar.\nFato: {t['fato']}.\n\nO {t['produto']} resolve isso agora, a partir de {t['preco']}.\n\nLink nos comentarios."


def hook_before_after(t: dict) -> str:
    return f"Antes: {t['fato']}, verificado manualmente, levando semanas.\nDepois: o {t['produto']} entrega o mesmo relatorio em 48h, seguindo {t['lei']} risca por risca.\n\nLink nos comentarios."


def hook_checklist(t: dict) -> str:
    return f"3 perguntas antes de continuar sem {t['produto']}:\n1. Sua empresa atende {t['lei']}?\n2. Voce sabe que {t['fato']}?\n3. Quanto custa descobrir isso tarde demais?\n\nO agente responde as 3 em 48h. Link nos comentarios."


def hook_cost_comparison(t: dict) -> str:
    return f"Consultoria tradicional pra {t['lei']}: semanas e um orcamento alto.\nAgente {t['produto']}: {t['preco']}, resultado em 48h.\n\n{t['fato'].capitalize()} — nao espere a fiscalizacao chegar primeiro.\n\nLink nos comentarios."


def hook_deadline_urgency(t: dict) -> str:
    return f"{t['lei']} ja esta em vigor.\n\n{t['fato'].capitalize()}. O {t['produto']} faz o diagnostico e o plano de acao em 48h — antes que vire multa.\n\nLink nos comentarios."


def hook_contrarian(t: dict) -> str:
    return f"Compliance nao precisa ser um projeto de meses.\n\n{t['fato'].capitalize()} — o {t['produto']} prova o contrario: catalogo real de {t['lei']}, scoring deterministico, relatorio em 48h.\n\nLink nos comentarios."


def hook_case_style(t: dict) -> str:
    return f"Um caso comum: empresa descobre tarde demais que {t['fato']}.\n\nO {t['produto']} evita isso — avaliacao completa contra {t['lei']} em 48h, a partir de {t['preco']}.\n\nLink nos comentarios."


def hook_data_led(t: dict) -> str:
    return f"Dado real: {t['fato']}.\n\nIsso e exatamente o que o {t['produto']} audita, com base em {t['lei']} — nao e opiniao de IA, e catalogo regulatorio real com scoring deterministico.\n\nLink nos comentarios."


def hook_portfolio_case(t: dict) -> str:
    return f"Projeto real: {t['fato']}.\n\nResolvemos isso com {t['produto']} ({t['lei']}). Quer algo assim rodando na sua empresa?\n\nLink nos comentarios."


def hook_direct_cta(t: dict) -> str:
    return f"Buscando {t['produto']}?\n\n{t['fato'].capitalize()}. Conversamos sobre o seu projeto — {t['preco']}.\n\nLink nos comentarios."


def hook_behind_the_build(t: dict) -> str:
    return f"Por tras do {t['produto']}: {t['fato']}.\n\nConstruido com base em {t['lei']}. Se quiser entender como aplicar isso na sua empresa, me chama.\n\nLink nos comentarios."


HOOKS = [
    hook_stat_shock, hook_question, hook_myth_fact, hook_before_after, hook_checklist,
    hook_cost_comparison, hook_deadline_urgency, hook_contrarian, hook_case_style, hook_data_led,
    hook_portfolio_case, hook_direct_cta, hook_behind_the_build,
]
