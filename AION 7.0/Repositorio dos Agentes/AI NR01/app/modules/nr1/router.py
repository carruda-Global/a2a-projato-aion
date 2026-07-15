"""Endpoints do módulo NR1 — cadastro, geração de inventário e PGR."""
from uuid import UUID
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.companies import crud
from app.core.decision_engine.engine import montar_inventario_empresa
from app.core.documents.pgr_generator import gerar_pgr_docx
from app.core.database.db import get_pool

router = APIRouter(prefix="/api/nr1", tags=["nr1"])


class EmpresaIn(BaseModel):
    razao_social: str
    nome_fantasia: str | None = None
    cnpj: str
    cnae: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None
    telefone: str | None = None
    email: str | None = None
    quantidade_funcionarios: int | None = None
    responsavel: str | None = None
    ano_construcao: int | None = None
    usuario_id: UUID


class SetorIn(BaseModel):
    empresa_id: UUID
    nome: str


class FuncaoIn(BaseModel):
    setor_id: UUID
    cargo: str
    quantidade: int = 1
    descricao: str | None = None
    jornada: str | None = None


class AtividadeIn(BaseModel):
    funcao_id: UUID
    nome: str
    descricao: str | None = None


@router.post("/empresas")
async def criar_empresa(dados: EmpresaIn):
    return await crud.criar_empresa(dados.usuario_id, dados.model_dump(exclude={"usuario_id"}))


@router.get("/empresas")
async def listar_empresas(usuario_id: UUID):
    return await crud.listar_empresas(usuario_id)


@router.post("/setores")
async def criar_setor(dados: SetorIn):
    return await crud.criar_setor(dados.empresa_id, dados.nome)


@router.post("/funcoes")
async def criar_funcao(dados: FuncaoIn):
    return await crud.criar_funcao(dados.setor_id, dados.model_dump(exclude={"setor_id"}))


@router.post("/atividades")
async def criar_atividade(dados: AtividadeIn):
    return await crud.criar_atividade(dados.funcao_id, dados.nome, dados.descricao)


@router.get("/empresas/{empresa_id}/inventario")
async def obter_inventario(empresa_id: UUID):
    """Sprint 2/3: roda o Motor de Decisão sobre todas as atividades cadastradas."""
    return await montar_inventario_empresa(empresa_id)


@router.get("/empresas/{empresa_id}/pgr")
async def gerar_pgr(empresa_id: UUID):
    """Sprint 4: gera o PGR.docx. Marca d'água aplicada se licença não for premium."""
    pool = get_pool()
    empresa_row = await pool.fetchrow("SELECT * FROM empresas WHERE id = $1", empresa_id)
    if not empresa_row:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    empresa = dict(empresa_row)

    usuario = await pool.fetchrow("SELECT licenca_tipo FROM usuarios WHERE id = $1", empresa["usuario_id"])
    licenca_premium = bool(usuario and usuario["licenca_tipo"] == "premium")

    inventario = await montar_inventario_empresa(empresa_id)
    docx_buf = gerar_pgr_docx(inventario, empresa, licenca_premium=licenca_premium)

    await pool.execute(
        """INSERT INTO documentos (empresa_id, tipo, formato, marca_dagua)
           VALUES ($1,'PGR','docx',$2)""",
        empresa_id, not licenca_premium,
    )

    filename = "PGR.docx" if licenca_premium else "PGR_demonstracao.docx"
    return StreamingResponse(
        docx_buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
