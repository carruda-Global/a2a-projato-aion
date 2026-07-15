"""Popula o Banco Mestre com os registros reais já pesquisados (NR-15).
Fonte: Camada 2/12-Riscos-Quimicos-Parte-01.md
Rodar uma vez após criar o schema: python -m app.core.knowledge.seed
"""
from app.core.database.db import get_pool

PERIGOS = [
    dict(id="RQ-0043", norma="NR-1", nome="Exposição à Poeira de Madeira", categoria="Químico",
         descricao="Partículas sólidas de corte/lixamento/aplainamento de madeira. Carcinógeno humano Grupo 1 (IARC) para madeira dura.",
         consequencias="Rinite alérgica, asma ocupacional, câncer nasossinusal, dermatite de contato",
         base_legal="NR-15, Anexo 13"),
    dict(id="RQ-0044", norma="NR-1", nome="Exposição a Vapores de Tolueno", categoria="Químico",
         descricao="Solvente orgânico volátil em tintas, vernizes, colas e limpeza industrial.",
         consequencias="Depressão do SNC, irritação de mucosas, dermatite, efeitos neurológicos/hepáticos crônicos",
         base_legal="NR-15, Anexo 11, Quadro 1"),
    dict(id="RQ-0045", norma="NR-1", nome="Exposição a Fumos Metálicos de Solda (Manganês)", categoria="Químico",
         descricao="Partículas metálicas geradas na fusão do eletrodo/arame durante soldagem (MIG/MAG, eletrodo revestido).",
         consequencias="Manganismo, febre dos fumos metálicos, pneumoconiose (siderose), irritação respiratória aguda",
         base_legal="NR-15, Anexo 11, Quadro 1"),
    dict(id="RQ-0046", norma="NR-1", nome="Exposição ao Chumbo Inorgânico", categoria="Químico",
         descricao="Metal pesado de toxicidade sistêmica cumulativa — fundição, reciclagem de baterias, solda eletrônica.",
         consequencias="Saturnismo, anemia, neuropatia periférica, efeitos reprodutivos",
         base_legal="NR-15, Anexo 11, Quadro 1"),
    dict(id="RQ-0047", norma="NR-1", nome="Exposição a Fibras de Amianto", categoria="Químico",
         descricao="Mineral fibroso em telhas/isolamentos antigos (proibido desde 2017). Risco em reforma/demolição de edificações anteriores.",
         consequencias="Asbestose, mesotelioma pleural, câncer de pulmão (latência de 15-40 anos)",
         base_legal="NR-15, Anexo 12; Lei 9.055/1995"),
    dict(id="RF-0001", norma="NR-1", nome="Exposição a Ruído Contínuo ou Intermitente", categoria="Físico",
         descricao="Pressão sonora medida em dB(A), circuito SLOW. Acima de 115 dB(A) sem proteção: risco grave e iminente.",
         consequencias="PAIR irreversível, zumbido, estresse, hipertensão",
         base_legal="NR-15, Anexo 1"),
    dict(id="RF-0002", norma="NR-1", nome="Exposição a Ruído de Impacto", categoria="Físico",
         descricao="Ruído de curta duração e alta intensidade (batidas, prensagem, martelamento).",
         consequencias="PAIR de instalação súbita (trauma acústico), perfuração timpânica em exposições extremas",
         base_legal="NR-15, Anexo 2"),
    dict(id="RF-0003", norma="NR-1", nome="Exposição Ocupacional ao Calor", categoria="Físico",
         descricao="Avaliado pelo IBUTG — fundições, cozinhas industriais, trabalho externo em construção civil.",
         consequencias="Desidratação, exaustão pelo calor, intermação (golpe de calor), cãibras",
         base_legal="NR-15, Anexo 3"),
    dict(id="RF-0004", norma="NR-1", nome="Exposição à Vibração em Mãos e Braços", categoria="Físico",
         descricao="Vibração transmitida ao sistema mão-braço por ferramentas manuais motorizadas.",
         consequencias="Síndrome de Raynaud Ocupacional (dedo branco), distúrbios neurológicos e osteoarticulares",
         base_legal="NR-15, Anexo 8"),
    dict(id="RF-0005", norma="NR-1", nome="Exposição à Radiação Não-Ionizante (arco elétrico de soldagem)", categoria="Físico",
         descricao="Radiação UV/IV emitida pelo arco elétrico durante soldagem — ocorre junto com RQ-0045 na mesma atividade.",
         consequencias="Ceratoconjuntivite actínica (vista de arco), queimaduras de pele",
         base_legal="NR-15, Anexo 7"),
]

CONTROLES = [
    dict(id="CT-EXAUST", nome="Exaustão localizada na fonte", tipo="Engenharia"),
    dict(id="CT-SUBST-AGUA", nome="Substituição por produto à base de água", tipo="Substituição"),
    dict(id="CT-LIMP-UMIDO", nome="Limpeza a úmido (não varrer a seco)", tipo="Administrativo"),
    dict(id="CT-MONIT-BIO", nome="Monitoramento biológico periódico (PCMSO)", tipo="Administrativo"),
    dict(id="CT-LAUDO-MCA", nome="Laudo de identificação de amianto antes de intervenção", tipo="Administrativo"),
    dict(id="CT-ENCLAUSURA", nome="Enclausuramento acústico de máquinas", tipo="Engenharia"),
    dict(id="CT-MANUT-PREV", nome="Manutenção preventiva (reduz ruído/vibração de desgaste)", tipo="Administrativo"),
    dict(id="CT-ISOL-IMPACTO", nome="Isolamento/enclausuramento de fonte de impacto", tipo="Engenharia"),
    dict(id="CT-REGIME-DESCANSO", nome="Regime de trabalho/descanso conforme IBUTG", tipo="Administrativo"),
    dict(id="CT-VENTIL-CALOR", nome="Ventilação/exaustão de calor", tipo="Engenharia"),
    dict(id="CT-RODIZIO-VIBRACAO", nome="Limitação de tempo de exposição contínua a vibração", tipo="Administrativo"),
    dict(id="CT-BIOMBO", nome="Biombos de isolamento de área de soldagem", tipo="Engenharia"),
]

EPIS = [
    dict(id="EPI-PFF2", nome="Respirador PFF2", ca=None),
    dict(id="EPI-PFF3", nome="Respirador PFF3/PAPR", ca=None),
    dict(id="EPI-CARTUCHO-VO", nome="Respirador com cartucho para vapores orgânicos", ca=None),
    dict(id="EPI-LUVA-QUIM", nome="Luvas de proteção química (nitrílica)", ca=None),
    dict(id="EPI-OCULOS", nome="Óculos de proteção química", ca=None),
    dict(id="EPI-PROT-AURIC-PLUG", nome="Protetor auricular tipo plug", ca=None),
    dict(id="EPI-PROT-AURIC-CONCHA", nome="Protetor auricular tipo concha", ca=None),
    dict(id="EPI-VEST-TERMICA", nome="Vestimenta de proteção térmica", ca=None),
    dict(id="EPI-PROTETOR-SOLAR", nome="Protetor solar + chapéu/boné com proteção de nuca", ca=None),
    dict(id="EPI-LUVA-ANTIVIBR", nome="Luvas antivibratórias", ca=None),
    dict(id="EPI-MASCARA-SOLDA", nome="Máscara de solda com filtro de tonalidade adequada", ca=None),
    dict(id="EPI-AVENTAL-RASPA", nome="Avental de raspa / mangote", ca=None),
]

EPCS = [
    dict(id="EPC-CABINE-PINT", nome="Cabine de pintura com exaustão forçada"),
    dict(id="EPC-VESTIARIO-DUPLO", nome="Vestiário com dupla via (limpo/sujo)"),
    dict(id="EPC-ISOLAMENTO", nome="Isolamento total da área de remoção (amianto)"),
    dict(id="EPC-PONTOS-HIDRATACAO", nome="Pontos de hidratação disponíveis no local"),
    dict(id="EPC-BARREIRA-TERMICA", nome="Barreira de radiação térmica (anteparo)"),
]

TREINAMENTOS = [
    dict(id="TR-EPI-RESP", nome="Uso correto de EPI respiratório", carga_horaria=4, periodicidade="anual"),
    dict(id="TR-NR12", nome="NR-12 — Segurança em Máquinas", carga_horaria=8, periodicidade="anual"),
    dict(id="TR-MCA", nome="Identificação de Materiais Contendo Amianto (MCA)", carga_horaria=8, periodicidade="único"),
    dict(id="TR-PCA", nome="PCA — Programa de Conservação Auditiva", carga_horaria=4, periodicidade="anual"),
    dict(id="TR-INTERMACAO", nome="Reconhecimento de sinais de intermação (golpe de calor)", carga_horaria=2, periodicidade="anual"),
    dict(id="TR-VIBRACAO", nome="Reconhecimento de sintomas de exposição à vibração", carga_horaria=2, periodicidade="anual"),
    dict(id="TR-TONALIDADE-SOLDA", nome="Seleção de tonalidade de viseira de solda", carga_horaria=2, periodicidade="único"),
]

# atividade (nome padronizado, como o usuário vai digitar/selecionar) -> perigo
# Nota: "Soldagem MIG/TIG/Eletrodo Revestido" aparece 2x — gera RQ-0045 (fumos,
# químico) E RF-0005 (radiação, físico) na mesma atividade. Confirma que o
# schema 1:N já suporta múltiplos perigos por atividade sem lógica especial.
ATIVIDADE_PERIGO = [
    ("Corte de Madeira", "RQ-0043"),
    ("Lixamento de Madeira", "RQ-0043"),
    ("Pintura Industrial", "RQ-0044"),
    ("Soldagem MIG", "RQ-0045"), ("Soldagem MIG", "RF-0005"),
    ("Soldagem TIG", "RQ-0045"), ("Soldagem TIG", "RF-0005"),
    ("Soldagem Eletrodo Revestido", "RQ-0045"), ("Soldagem Eletrodo Revestido", "RF-0005"),
    ("Fundição de Chumbo", "RQ-0046"), ("Fundição de Chumbo", "RF-0003"),
    ("Solda Eletrônica", "RQ-0046"),
    ("Demolição de Cobertura Antiga", "RQ-0047"),
    ("Reforma Predial Anterior a 2017", "RQ-0047"),
    ("Operação de Serra Circular", "RF-0001"),
    ("Operação de Prensa", "RF-0002"),
    ("Martelamento/Forjamento", "RF-0002"),
    ("Cravação de Estacas", "RF-0002"),
    ("Cozinha Industrial", "RF-0003"),
    ("Trabalho Externo em Construção Civil", "RF-0003"),
    ("Uso de Martelete/Rompedor", "RF-0004"),
    ("Uso de Lixadeira/Esmerilhadeira", "RF-0004"),
]

PERIGO_CONTROLE = [
    ("RQ-0043", "CT-EXAUST"), ("RQ-0043", "CT-LIMP-UMIDO"),
    ("RQ-0044", "CT-SUBST-AGUA"),
    ("RQ-0045", "CT-EXAUST"), ("RQ-0045", "CT-MONIT-BIO"),
    ("RQ-0046", "CT-MONIT-BIO"),
    ("RQ-0047", "CT-LAUDO-MCA"),
    ("RF-0001", "CT-ENCLAUSURA"), ("RF-0001", "CT-MANUT-PREV"),
    ("RF-0002", "CT-ISOL-IMPACTO"),
    ("RF-0003", "CT-VENTIL-CALOR"), ("RF-0003", "CT-REGIME-DESCANSO"),
    ("RF-0004", "CT-MANUT-PREV"), ("RF-0004", "CT-RODIZIO-VIBRACAO"),
    ("RF-0005", "CT-BIOMBO"),
]

PERIGO_EPI = [
    ("RQ-0043", "EPI-PFF2"),
    ("RQ-0044", "EPI-CARTUCHO-VO"), ("RQ-0044", "EPI-LUVA-QUIM"), ("RQ-0044", "EPI-OCULOS"),
    ("RQ-0045", "EPI-PFF2"),
    ("RQ-0046", "EPI-PFF3"),
    ("RQ-0047", "EPI-PFF3"),
    ("RF-0001", "EPI-PROT-AURIC-PLUG"),
    ("RF-0002", "EPI-PROT-AURIC-CONCHA"),
    ("RF-0003", "EPI-VEST-TERMICA"), ("RF-0003", "EPI-PROTETOR-SOLAR"),
    ("RF-0004", "EPI-LUVA-ANTIVIBR"),
    ("RF-0005", "EPI-MASCARA-SOLDA"), ("RF-0005", "EPI-AVENTAL-RASPA"),
]

PERIGO_EPC = [
    ("RQ-0044", "EPC-CABINE-PINT"),
    ("RQ-0046", "EPC-VESTIARIO-DUPLO"),
    ("RQ-0047", "EPC-ISOLAMENTO"),
    ("RF-0003", "EPC-PONTOS-HIDRATACAO"), ("RF-0003", "EPC-BARREIRA-TERMICA"),
]

PERIGO_TREINAMENTO = [
    ("RQ-0043", "TR-EPI-RESP"),
    ("RQ-0045", "TR-NR12"),
    ("RQ-0047", "TR-MCA"),
    ("RF-0001", "TR-PCA"),
    ("RF-0002", "TR-PCA"),
    ("RF-0003", "TR-INTERMACAO"),
    ("RF-0004", "TR-VIBRACAO"),
    ("RF-0005", "TR-TONALIDADE-SOLDA"),
]

_TODOS_PERIGOS = ["RQ-0043", "RQ-0044", "RQ-0045", "RQ-0046", "RQ-0047",
                  "RF-0001", "RF-0002", "RF-0003", "RF-0004", "RF-0005"]

PERIGO_DOCUMENTO = [
    (pid, doc) for pid in _TODOS_PERIGOS
    for doc in ["Inventario", "PlanoAcao", "PGR"]
] + [("RQ-0047", "OrdemServico"), ("RF-0005", "OrdemServico")]


async def seed() -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            for p in PERIGOS:
                await conn.execute(
                    """INSERT INTO perigos (id, norma, nome, categoria, descricao, consequencias, base_legal)
                       VALUES ($1,$2,$3,$4,$5,$6,$7) ON CONFLICT (id) DO NOTHING""",
                    p["id"], p["norma"], p["nome"], p["categoria"], p["descricao"],
                    p["consequencias"], p["base_legal"],
                )
            for c in CONTROLES:
                await conn.execute(
                    "INSERT INTO controles (id, nome, tipo) VALUES ($1,$2,$3) ON CONFLICT (id) DO NOTHING",
                    c["id"], c["nome"], c["tipo"],
                )
            for e in EPIS:
                await conn.execute(
                    "INSERT INTO epis (id, nome, ca) VALUES ($1,$2,$3) ON CONFLICT (id) DO NOTHING",
                    e["id"], e["nome"], e["ca"],
                )
            for e in EPCS:
                await conn.execute(
                    "INSERT INTO epcs (id, nome) VALUES ($1,$2) ON CONFLICT (id) DO NOTHING",
                    e["id"], e["nome"],
                )
            for t in TREINAMENTOS:
                await conn.execute(
                    "INSERT INTO treinamentos (id, nome, carga_horaria, periodicidade) VALUES ($1,$2,$3,$4) ON CONFLICT (id) DO NOTHING",
                    t["id"], t["nome"], t["carga_horaria"], t["periodicidade"],
                )
            for ativ, pid in ATIVIDADE_PERIGO:
                await conn.execute(
                    "INSERT INTO atividade_perigo (atividade_nome, perigo_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
                    ativ, pid,
                )
            for pid, cid in PERIGO_CONTROLE:
                await conn.execute(
                    "INSERT INTO perigo_controle (perigo_id, controle_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
                    pid, cid,
                )
            for pid, eid in PERIGO_EPI:
                await conn.execute(
                    "INSERT INTO perigo_epi (perigo_id, epi_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
                    pid, eid,
                )
            for pid, eid in PERIGO_EPC:
                await conn.execute(
                    "INSERT INTO perigo_epc (perigo_id, epc_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
                    pid, eid,
                )
            for pid, tid in PERIGO_TREINAMENTO:
                await conn.execute(
                    "INSERT INTO perigo_treinamento (perigo_id, treinamento_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
                    pid, tid,
                )
            for pid, doc in PERIGO_DOCUMENTO:
                await conn.execute(
                    "INSERT INTO perigo_documento (perigo_id, tipo_documento) VALUES ($1,$2) ON CONFLICT DO NOTHING",
                    pid, doc,
                )
    print(f"Seed concluido: {len(PERIGOS)} perigos, {len(ATIVIDADE_PERIGO)} vinculos atividade->perigo")


if __name__ == "__main__":
    import asyncio
    from app.core.database.db import init_pool, close_pool

    async def main():
        await init_pool()
        await seed()
        await close_pool()

    asyncio.run(main())
