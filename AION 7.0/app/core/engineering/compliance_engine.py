"""Engineering Copilot — Modulo 5 (Compliance). Nunca consulta IA: cruza o tipo
de equipamento cadastrado contra um catalogo fixo de normas aplicaveis (NR,
ABNT, CREA, ANVISA, fabricante) e aponta o que falta. Igual ao motor de decisao
do NR1 — regra e linha de tabela, nao codigo de IA."""

# Catalogo real — mapeia palavras-chave do tipo de equipamento para as normas
# que se aplicam a ele. Ampliar isto e so adicionar entrada, nao mexe no motor.
CATALOGO_NORMAS_POR_EQUIPAMENTO = [
    {"palavras_chave": ["climatiza", "ar condicionado", "hvac", "split", "chiller", "fancoil"],
     "normas": [
         {"norma": "ABNT NBR 13971", "descricao": "Manutencao de sistemas de climatizacao — PMOC"},
         {"norma": "ANVISA RDC 09/2003", "descricao": "Padroes de qualidade do ar interior em ambientes climatizados"},
     ]},
    {"palavras_chave": ["vaso de pressao", "caldeira", "compressor", "tanque pressurizado"],
     "normas": [{"norma": "NR-13", "descricao": "Caldeiras, vasos de pressao e tubulacoes — inspecao periodica"}]},
    {"palavras_chave": ["elevador", "guindaste", "ponte rolante", "monta-carga", "talha"],
     "normas": [{"norma": "NR-12", "descricao": "Seguranca no trabalho em maquinas e equipamentos"}]},
    {"palavras_chave": ["subestacao", "painel eletrico", "quadro de distribuicao", "transformador", "gerador"],
     "normas": [{"norma": "NR-10", "descricao": "Seguranca em instalacoes e servicos em eletricidade"}]},
    {"palavras_chave": ["andaime", "telhado", "altura", "torre"],
     "normas": [{"norma": "NR-35", "descricao": "Trabalho em altura"}]},
]

EXIGENCIA_UNIVERSAL = {"norma": "ART/CREA", "descricao": "Anotacao de Responsabilidade Tecnica do responsavel pelo projeto/execucao"}


def _normas_aplicaveis_ao_equipamento(equipamento: dict) -> list[dict]:
    tipo = (equipamento.get("tipo") or "").lower()
    tag = (equipamento.get("tag") or "").lower()
    texto = f"{tipo} {tag}"
    aplicaveis = []
    for entrada in CATALOGO_NORMAS_POR_EQUIPAMENTO:
        if any(palavra in texto for palavra in entrada["palavras_chave"]):
            aplicaveis.extend(entrada["normas"])
    return aplicaveis


def avaliar_compliance(equipamentos: list[dict], normas_identificadas: list[dict]) -> dict:
    """Compara o que o Modulo 1/2 encontrou nos documentos/fotos (normas_identificadas)
    contra o que o catalogo diz que DEVERIA existir para cada equipamento cadastrado.
    Retorna pendencias, nao-conformidades e evidencias."""
    normas_encontradas = {n.get("norma", "").upper().strip() for n in normas_identificadas}

    normas_exigidas: dict[str, dict] = {EXIGENCIA_UNIVERSAL["norma"]: EXIGENCIA_UNIVERSAL}
    for eq in equipamentos:
        for norma in _normas_aplicaveis_ao_equipamento(eq):
            normas_exigidas[norma["norma"]] = norma

    pendencias, conformidades = [], []
    for chave, norma in normas_exigidas.items():
        if chave.upper().strip() in normas_encontradas:
            conformidades.append({"norma": chave, "descricao": norma["descricao"], "status": "conforme"})
        else:
            pendencias.append({"norma": chave, "descricao": norma["descricao"], "status": "pendente"})

    total = len(normas_exigidas) or 1
    score = round((len(conformidades) / total) * 100)

    return {
        "score_conformidade": score,
        "conformidades": conformidades,
        "pendencias": pendencias,
        "nao_conformidades": [
            f"{p['norma']}: {p['descricao']} — evidencia nao encontrada nos documentos/fotos analisados"
            for p in pendencias
        ],
    }
