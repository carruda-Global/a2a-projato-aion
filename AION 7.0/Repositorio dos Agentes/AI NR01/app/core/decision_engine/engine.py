"""Motor de Decisão — Sprint 3.

Nunca consulta IA. Só consulta o banco relacional (atividade -> perigo ->
controle/epi/epc/treinamento/documento). Regra = linha de tabela, não código.
Adicionar uma nova NR/atividade/perigo é INSERT no banco, não deploy de código.
"""
from uuid import UUID
from app.core.database.db import get_pool


async def avaliar_atividade(atividade_nome: str) -> dict:
    """Dado o nome de uma atividade (ex: 'Soldagem MIG'), retorna tudo que o
    banco mestre já sabe sobre ela: perigos, controles, EPIs, EPCs,
    treinamentos e documentos a gerar."""
    pool = get_pool()

    perigos = await pool.fetch(
        """
        SELECT p.* FROM perigos p
        JOIN atividade_perigo ap ON ap.perigo_id = p.id
        WHERE ap.atividade_nome = $1
        """,
        atividade_nome,
    )
    if not perigos:
        return {"atividade": atividade_nome, "perigos": [], "aviso": "Nenhum perigo catalogado para esta atividade ainda"}

    perigo_ids = [p["id"] for p in perigos]

    controles = await pool.fetch(
        """SELECT pc.perigo_id, c.* FROM perigo_controle pc
           JOIN controles c ON c.id = pc.controle_id WHERE pc.perigo_id = ANY($1)""",
        perigo_ids,
    )
    epis = await pool.fetch(
        """SELECT pe.perigo_id, e.* FROM perigo_epi pe
           JOIN epis e ON e.id = pe.epi_id WHERE pe.perigo_id = ANY($1)""",
        perigo_ids,
    )
    epcs = await pool.fetch(
        """SELECT pc.perigo_id, e.* FROM perigo_epc pc
           JOIN epcs e ON e.id = pc.epc_id WHERE pc.perigo_id = ANY($1)""",
        perigo_ids,
    )
    treinamentos = await pool.fetch(
        """SELECT pt.perigo_id, t.* FROM perigo_treinamento pt
           JOIN treinamentos t ON t.id = pt.treinamento_id WHERE pt.perigo_id = ANY($1)""",
        perigo_ids,
    )
    documentos = await pool.fetch(
        "SELECT DISTINCT tipo_documento FROM perigo_documento WHERE perigo_id = ANY($1)",
        perigo_ids,
    )

    def _agrupar_por_perigo(rows, chave="perigo_id"):
        agrupado: dict[str, list] = {}
        for r in rows:
            agrupado.setdefault(r[chave], []).append(dict(r))
        return agrupado

    controles_por_perigo = _agrupar_por_perigo(controles)
    epis_por_perigo = _agrupar_por_perigo(epis)
    epcs_por_perigo = _agrupar_por_perigo(epcs)
    treinamentos_por_perigo = _agrupar_por_perigo(treinamentos)

    resultado_perigos = []
    for p in perigos:
        resultado_perigos.append({
            **dict(p),
            "controles": controles_por_perigo.get(p["id"], []),
            "epis": epis_por_perigo.get(p["id"], []),
            "epcs": epcs_por_perigo.get(p["id"], []),
            "treinamentos": treinamentos_por_perigo.get(p["id"], []),
        })

    return {
        "atividade": atividade_nome,
        "perigos": resultado_perigos,
        "documentos_a_gerar": sorted({d["tipo_documento"] for d in documentos}),
    }


async def montar_inventario_empresa(empresa_id: UUID) -> dict:
    """Roda avaliar_atividade() para TODAS as atividades cadastradas da
    empresa e consolida — isto é o Inventário de Riscos (Módulo 7 completo)."""
    from app.core.companies.crud import listar_atividades_da_empresa

    atividades = await listar_atividades_da_empresa(empresa_id)
    inventario = []
    documentos_necessarios: set[str] = set()

    for atividade in atividades:
        avaliacao = await avaliar_atividade(atividade["nome"])
        avaliacao.pop("atividade", None)  # avaliar_atividade returns the name as a string; don't let it clobber the full row dict below
        inventario.append({"atividade": dict(atividade), **avaliacao})
        documentos_necessarios.update(avaliacao.get("documentos_a_gerar", []))

    return {
        "empresa_id": str(empresa_id),
        "inventario": inventario,
        "documentos_necessarios": sorted(documentos_necessarios),
    }
