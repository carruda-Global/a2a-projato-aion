"""DEMO TEMPORÁRIO — visualização rápida do fluxo NR1 sem banco conectado.

NÃO é a arquitetura final. Dados em memória (nem SQLite, nem Postgres),
só pra mostrar o fluxo empresa -> atividade -> riscos -> PGR.docx
funcionando de ponta a ponta hoje, enquanto a conexão real com o
Supabase não é resolvida. Reaproveita os dados REAIS do seed.py
(mesmos riscos pesquisados na NR-15) e o gerador de PDF real testado.

Rodar: uvicorn app.demo:app --reload --port 8010
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from app.core.knowledge.seed import PERIGOS, ATIVIDADE_PERIGO, PERIGO_CONTROLE, PERIGO_EPI, PERIGO_EPC, PERIGO_TREINAMENTO, CONTROLES, EPIS, EPCS, TREINAMENTOS
from app.core.documents.pgr_generator import gerar_pgr_docx

app = FastAPI(title="NR1 AI — DEMO (dado em memória, não é a arquitetura final)")

_perigos_por_id = {p["id"]: p for p in PERIGOS}
_controles_por_id = {c["id"]: c for c in CONTROLES}
_epis_por_id = {e["id"]: e for e in EPIS}
_epcs_por_id = {e["id"]: e for e in EPCS}
_treinamentos_por_id = {t["id"]: t for t in TREINAMENTOS}

_atividades_disponiveis = sorted({a for a, _ in ATIVIDADE_PERIGO})


def _avaliar_atividade_memoria(atividade_nome: str) -> dict:
    perigo_ids = [pid for a, pid in ATIVIDADE_PERIGO if a == atividade_nome]
    perigos_resultado = []
    for pid in perigo_ids:
        perigo = dict(_perigos_por_id[pid])
        perigo["controles"] = [dict(_controles_por_id[cid]) for p, cid in PERIGO_CONTROLE if p == pid]
        perigo["epis"] = [dict(_epis_por_id[eid]) for p, eid in PERIGO_EPI if p == pid]
        perigo["epcs"] = [dict(_epcs_por_id[eid]) for p, eid in PERIGO_EPC if p == pid]
        perigo["treinamentos"] = [dict(_treinamentos_por_id[tid]) for p, tid in PERIGO_TREINAMENTO if p == pid]
        perigos_resultado.append(perigo)
    return {"atividade": atividade_nome, "perigos": perigos_resultado}


@app.get("/", response_class=HTMLResponse)
async def home():
    opcoes = "".join(f'<option value="{a}">{a}</option>' for a in _atividades_disponiveis)
    return f"""
    <html><head><meta charset="utf-8"><title>NR1 AI — Demo</title>
    <style>body{{font-family:sans-serif;max-width:600px;margin:60px auto;padding:0 20px}}
    h1{{color:#00C36B}}label{{display:block;margin-top:16px;font-weight:600}}
    input,select{{width:100%;padding:10px;margin-top:6px;box-sizing:border-box}}
    button{{margin-top:24px;background:#00C36B;color:#fff;border:none;padding:14px 28px;border-radius:8px;font-weight:700;cursor:pointer}}
    .aviso{{background:#fff3cd;padding:12px;border-radius:8px;font-size:14px;margin-bottom:20px}}</style>
    </head><body>
    <div class="aviso">⚠️ DEMO — dado em memória, não persiste. Arquitetura final usa PostgreSQL (Supabase).</div>
    <h1>NR1 AI — Diagnóstico Rápido</h1>
    <form action="/gerar-pgr" method="get">
      <label>Nome da Empresa</label>
      <input name="empresa" placeholder="Metalúrgica Exemplo LTDA" required>
      <label>CNPJ</label>
      <input name="cnpj" placeholder="00.000.000/0001-00">
      <label>Atividade realizada</label>
      <select name="atividade">{opcoes}</select>
      <button type="submit">Gerar PGR (demonstração)</button>
    </form>
    </body></html>
    """


@app.get("/gerar-pgr")
async def gerar_pgr(empresa: str, atividade: str, cnpj: str = ""):
    avaliacao = _avaliar_atividade_memoria(atividade)
    inventario = {"inventario": [{"atividade": {"nome": atividade}, **avaliacao}],
                  "documentos_necessarios": ["Inventario", "PlanoAcao", "PGR"]}
    empresa_dict = {"razao_social": empresa, "cnpj": cnpj}
    buf = gerar_pgr_docx(inventario, empresa_dict, licenca_premium=False)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                              headers={"Content-Disposition": 'attachment; filename="PGR_demonstracao.docx"'})
