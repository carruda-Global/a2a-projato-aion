"""Módulo 2-5: Cadastro de Empresa, Setores, Funções, Atividades — CRUD puro, sem IA."""
from uuid import UUID
from app.core.database.db import get_pool


async def criar_empresa(usuario_id: UUID, dados: dict) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO empresas (usuario_id, razao_social, nome_fantasia, cnpj, cnae,
                               endereco, cidade, estado, cep, telefone, email,
                               quantidade_funcionarios, responsavel, ano_construcao)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
        RETURNING *
        """,
        usuario_id, dados["razao_social"], dados.get("nome_fantasia"), dados["cnpj"],
        dados.get("cnae"), dados.get("endereco"), dados.get("cidade"), dados.get("estado"),
        dados.get("cep"), dados.get("telefone"), dados.get("email"),
        dados.get("quantidade_funcionarios"), dados.get("responsavel"),
        dados.get("ano_construcao"),
    )
    return dict(row)


async def listar_empresas(usuario_id: UUID) -> list[dict]:
    pool = get_pool()
    rows = await pool.fetch("SELECT * FROM empresas WHERE usuario_id = $1 ORDER BY criado_em DESC", usuario_id)
    return [dict(r) for r in rows]


async def criar_setor(empresa_id: UUID, nome: str) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        "INSERT INTO setores (empresa_id, nome) VALUES ($1,$2) RETURNING *", empresa_id, nome
    )
    return dict(row)


async def criar_funcao(setor_id: UUID, dados: dict) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO funcoes (setor_id, cargo, quantidade, descricao, jornada)
        VALUES ($1,$2,$3,$4,$5) RETURNING *
        """,
        setor_id, dados["cargo"], dados.get("quantidade", 1), dados.get("descricao"),
        dados.get("jornada"),
    )
    return dict(row)


async def criar_atividade(funcao_id: UUID, nome: str, descricao: str | None = None) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        "INSERT INTO atividades (funcao_id, nome, descricao) VALUES ($1,$2,$3) RETURNING *",
        funcao_id, nome, descricao,
    )
    return dict(row)


async def listar_atividades_da_empresa(empresa_id: UUID) -> list[dict]:
    """Todas as atividades de uma empresa, atravessando setor -> função -> atividade."""
    pool = get_pool()
    rows = await pool.fetch(
        """
        SELECT a.* FROM atividades a
        JOIN funcoes f ON f.id = a.funcao_id
        JOIN setores s ON s.id = f.setor_id
        WHERE s.empresa_id = $1
        """,
        empresa_id,
    )
    return [dict(r) for r in rows]
