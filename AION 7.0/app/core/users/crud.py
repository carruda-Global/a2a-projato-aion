"""CRUD de usuarios do NR1 AI — criacao (provisionamento automatico) e login."""
import secrets
import string
from passlib.hash import bcrypt

from app.core.database.db import get_pool


def gerar_senha_temporaria(tamanho: int = 12) -> str:
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(tamanho))


async def criar_usuario(nome: str, email: str, senha: str, licenca_tipo: str = "gratuita") -> dict:
    """Cria um usuario. Se o email ja existir, retorna o usuario existente
    (idempotente — evita duplicar em caso de retry do webhook do Stripe)."""
    pool = get_pool()
    existente = await pool.fetchrow("SELECT * FROM usuarios WHERE email = $1", email)
    if existente:
        return dict(existente)

    senha_hash = bcrypt.hash(senha)
    row = await pool.fetchrow(
        """
        INSERT INTO usuarios (nome, email, senha_hash, licenca_tipo)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        nome, email, senha_hash, licenca_tipo,
    )
    return dict(row)


async def autenticar_usuario(email: str, senha: str) -> dict | None:
    pool = get_pool()
    row = await pool.fetchrow("SELECT * FROM usuarios WHERE email = $1", email)
    if not row or not bcrypt.verify(senha, row["senha_hash"]):
        return None
    return dict(row)
