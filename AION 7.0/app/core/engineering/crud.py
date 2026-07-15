"""Engineering Copilot — CRUD puro (projeto, documentos, equipamentos, normas, fotos), sem IA."""
from uuid import UUID
from app.core.engineering.db import get_pool


async def criar_projeto(dados: dict) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO projetos (customer_email, cliente, local, escopo)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        dados.get("customer_email", ""), dados["cliente"], dados.get("local"), dados.get("escopo"),
    )
    return dict(row)


async def obter_projeto(projeto_id: UUID) -> dict | None:
    pool = get_pool()
    row = await pool.fetchrow("SELECT * FROM projetos WHERE id = $1", projeto_id)
    return dict(row) if row else None


async def adicionar_documento(projeto_id: UUID, nome_arquivo: str, texto_extraido: str, dados_extraidos: dict) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO documentos (projeto_id, nome_arquivo, texto_extraido, dados_extraidos)
        VALUES ($1, $2, $3, $4::jsonb)
        RETURNING *
        """,
        projeto_id, nome_arquivo, texto_extraido[:20000], _to_json(dados_extraidos),
    )
    return dict(row)


async def adicionar_equipamentos(projeto_id: UUID, equipamentos: list[dict], origem: str) -> None:
    pool = get_pool()
    for eq in equipamentos:
        await pool.execute(
            """
            INSERT INTO equipamentos (projeto_id, tag, tipo, fabricante, modelo, capacidade, localizacao, origem)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            projeto_id, eq.get("tag"), eq.get("tipo"), eq.get("fabricante"),
            eq.get("modelo"), eq.get("capacidade"), eq.get("localizacao"), origem,
        )


async def adicionar_normas(projeto_id: UUID, normas: list[dict]) -> None:
    pool = get_pool()
    for n in normas:
        await pool.execute(
            "INSERT INTO normas_aplicaveis (projeto_id, norma, descricao) VALUES ($1, $2, $3)",
            projeto_id, n.get("norma"), n.get("descricao"),
        )


async def adicionar_foto(projeto_id: UUID, nome_arquivo: str, analise: dict) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO fotos (projeto_id, nome_arquivo, analise)
        VALUES ($1, $2, $3::jsonb)
        RETURNING *
        """,
        projeto_id, nome_arquivo, _to_json(analise),
    )
    return dict(row)


async def listar_documentos(projeto_id: UUID) -> list[dict]:
    pool = get_pool()
    rows = await pool.fetch("SELECT * FROM documentos WHERE projeto_id = $1 ORDER BY criado_em", projeto_id)
    return [dict(r) for r in rows]


async def listar_equipamentos(projeto_id: UUID) -> list[dict]:
    pool = get_pool()
    rows = await pool.fetch("SELECT * FROM equipamentos WHERE projeto_id = $1 ORDER BY criado_em", projeto_id)
    return [dict(r) for r in rows]


async def listar_normas(projeto_id: UUID) -> list[dict]:
    pool = get_pool()
    rows = await pool.fetch("SELECT * FROM normas_aplicaveis WHERE projeto_id = $1 ORDER BY criado_em", projeto_id)
    return [dict(r) for r in rows]


async def listar_fotos(projeto_id: UUID) -> list[dict]:
    pool = get_pool()
    rows = await pool.fetch("SELECT * FROM fotos WHERE projeto_id = $1 ORDER BY criado_em", projeto_id)
    return [dict(r) for r in rows]


def _to_json(dados: dict) -> str:
    import json
    return json.dumps(dados, ensure_ascii=False)
