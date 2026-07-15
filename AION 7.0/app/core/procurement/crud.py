"""CRUD + motor de scoring do Procurement Copilot.

Vendor Intelligence: score deterministico (nao e LLM adivinhando) baseado em
certificacoes, tempo de mercado, historico de entrega e incidentes de
qualidade — mesmo principio dos Copilots de compliance (catalogo real
decide, LLM so explica)."""
from uuid import UUID
from app.core.procurement.db import get_pool


def calcular_score_fornecedor(dados: dict) -> tuple[int, str]:
    """Score 0-100. Cada criterio tem peso fixo — deterministico e auditavel."""
    score = 0
    if dados.get("tem_iso9001"):
        score += 20
    if dados.get("tem_iso14001"):
        score += 10
    if dados.get("tem_certificado_seguranca"):
        score += 15
    anos = dados.get("anos_mercado", 0) or 0
    score += min(anos, 10) * 2  # ate 20 pontos por tempo de mercado
    entregas_pct = dados.get("entregas_no_prazo_pct", 0) or 0
    score += round(entregas_pct * 0.25)  # ate 25 pontos por pontualidade
    incidentes = dados.get("incidentes_qualidade", 0) or 0
    score -= min(incidentes, 10) * 3  # penaliza incidentes, ate -30

    score = max(0, min(100, score))

    if score >= 80:
        classificacao = "Baixo Risco"
    elif score >= 55:
        classificacao = "Risco Moderado"
    elif score >= 30:
        classificacao = "Alto Risco"
    else:
        classificacao = "Critico"

    return score, classificacao


async def criar_fornecedor(dados: dict) -> dict:
    pool = get_pool()
    score, classificacao = calcular_score_fornecedor(dados)
    row = await pool.fetchrow(
        """
        INSERT INTO procurement.fornecedores
            (nome, cnpj, categoria, tem_iso9001, tem_iso14001, tem_certificado_seguranca,
             anos_mercado, entregas_no_prazo_pct, incidentes_qualidade, score_risco, classificacao)
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
        RETURNING *
        """,
        dados["nome"], dados.get("cnpj"), dados.get("categoria"),
        dados.get("tem_iso9001", False), dados.get("tem_iso14001", False),
        dados.get("tem_certificado_seguranca", False), dados.get("anos_mercado", 0),
        dados.get("entregas_no_prazo_pct", 0), dados.get("incidentes_qualidade", 0),
        score, classificacao,
    )
    return dict(row)


async def listar_fornecedores() -> list[dict]:
    pool = get_pool()
    rows = await pool.fetch("SELECT * FROM procurement.fornecedores ORDER BY score_risco DESC")
    return [dict(r) for r in rows]


async def criar_requisicao(descricao: str, quantidade: float | None, unidade: str | None) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        "INSERT INTO procurement.requisicoes (descricao, quantidade, unidade) VALUES ($1,$2,$3) RETURNING *",
        descricao, quantidade, unidade,
    )
    return dict(row)


async def criar_rfq(requisicao_id: UUID, escopo: str, criterios_tecnicos: str) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        "INSERT INTO procurement.rfqs (requisicao_id, escopo, criterios_tecnicos) VALUES ($1,$2,$3) RETURNING *",
        requisicao_id, escopo, criterios_tecnicos,
    )
    return dict(row)


async def registrar_cotacao(rfq_id: UUID, fornecedor_id: UUID, preco: float, prazo_dias: int) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        "INSERT INTO procurement.cotacoes (rfq_id, fornecedor_id, preco, prazo_dias) VALUES ($1,$2,$3,$4) RETURNING *",
        rfq_id, fornecedor_id, preco, prazo_dias,
    )
    return dict(row)


async def comparar_cotacoes(rfq_id: UUID) -> list[dict]:
    """Equalizacao simples: ordena por preco, com fornecedor e score de risco juntos
    para decisao informada (nao so o mais barato)."""
    pool = get_pool()
    rows = await pool.fetch(
        """
        SELECT c.*, f.nome AS fornecedor_nome, f.score_risco, f.classificacao
        FROM procurement.cotacoes c
        JOIN procurement.fornecedores f ON f.id = c.fornecedor_id
        WHERE c.rfq_id = $1
        ORDER BY c.preco ASC
        """,
        rfq_id,
    )
    return [dict(r) for r in rows]


async def registrar_compra(fornecedor_id: UUID, categoria: str, valor: float) -> dict:
    pool = get_pool()
    row = await pool.fetchrow(
        "INSERT INTO procurement.compras (fornecedor_id, categoria, valor) VALUES ($1,$2,$3) RETURNING *",
        fornecedor_id, categoria, valor,
    )
    return dict(row)


async def spend_analytics() -> dict:
    """Curva ABC simples: agrupa gasto por categoria, ordena decrescente,
    classifica A (80% do gasto), B (proximos 15%), C (resto 5%)."""
    pool = get_pool()
    rows = await pool.fetch(
        "SELECT categoria, SUM(valor) AS total FROM procurement.compras GROUP BY categoria ORDER BY total DESC"
    )
    total_geral = sum(r["total"] for r in rows) or 1
    acumulado = 0
    curva_abc = []
    for r in rows:
        acumulado += r["total"]
        pct_acumulado = acumulado / total_geral
        classe = "A" if pct_acumulado <= 0.8 else ("B" if pct_acumulado <= 0.95 else "C")
        curva_abc.append({
            "categoria": r["categoria"],
            "total": float(r["total"]),
            "pct_do_total": round(float(r["total"]) / total_geral * 100, 1),
            "classe_abc": classe,
        })

    top_fornecedores = await pool.fetch(
        """
        SELECT f.nome, SUM(c.valor) AS total_gasto
        FROM procurement.compras c JOIN procurement.fornecedores f ON f.id = c.fornecedor_id
        GROUP BY f.nome ORDER BY total_gasto DESC LIMIT 5
        """
    )

    return {
        "gasto_total": float(total_geral),
        "curva_abc": curva_abc,
        "top_fornecedores": [dict(r) for r in top_fornecedores],
    }
