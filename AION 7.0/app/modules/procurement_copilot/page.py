"""Pagina web do Procurement Copilot MVP."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

page_router = APIRouter(tags=["procurement-copilot-page"])

_HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Procurement Copilot | Global Match Engenharia</title>
<link rel="icon" href="https://global-engenharia.com/assets/logo.webp">
<style>
:root{--primary:#0d2c4c;--green:#00C36B}
*{box-sizing:border-box}
body{font-family:'Segoe UI',Inter,sans-serif;background:#f4f6f8;margin:0;color:#1e293b}
header{background:var(--primary);padding:16px 24px;display:flex;align-items:center;gap:12px}
header img{height:36px}
header span{color:#fff;font-weight:700;font-size:1.1rem}
.container{max-width:900px;margin:32px auto;padding:0 16px}
.card{background:#fff;border-radius:12px;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:20px}
h2{margin:0 0 16px;color:var(--primary);font-size:1.2rem}
label{display:block;font-weight:600;margin-top:12px;font-size:.85rem}
input,select{width:100%;padding:9px;margin-top:4px;border:1px solid #dee2e6;border-radius:8px;font-size:.9rem}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.check{display:flex;align-items:center;gap:6px;margin-top:10px;font-size:.85rem;font-weight:600}
.check input{width:auto;margin:0}
button{margin-top:18px;background:var(--green);color:#fff;border:none;padding:11px 22px;border-radius:8px;font-weight:700;cursor:pointer;font-size:.9rem}
table{width:100%;border-collapse:collapse;margin-top:16px;font-size:.85rem}
th,td{text-align:left;padding:8px;border-bottom:1px solid #eee}
.badge{padding:3px 10px;border-radius:20px;font-size:.75rem;font-weight:700;color:#fff}
.badge.baixo{background:#00C36B}.badge.moderado{background:#f0b429}.badge.alto{background:#f97316}.badge.critico{background:#ef4444}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
.kpi{background:#f8fafc;border-radius:8px;padding:16px;text-align:center}
.kpi .num{font-size:1.6rem;font-weight:700;color:var(--primary)}
.kpi .label{font-size:.8rem;color:#64748b}
footer{text-align:center;color:#94a3b8;font-size:.8rem;padding:24px}
</style></head>
<body>
<header><img src="https://global-engenharia.com/assets/logo.webp" alt="Global Match"><span>Procurement Copilot</span></header>
<div class="container">

  <div class="card">
    <h2>📊 Dashboard</h2>
    <div class="kpi-grid" id="dashboard-kpis"></div>
    <table id="abc-table"><thead><tr><th>Category</th><th>Total</th><th>% of spend</th><th>ABC Class</th></tr></thead><tbody></tbody></table>
    <button onclick="carregarDashboard()">Refresh dashboard</button>
  </div>

  <div class="card">
    <h2>🏭 Vendors (Vendor Intelligence)</h2>
    <div class="grid2">
      <div><label>Name</label><input id="f-nome"></div>
      <div><label>Tax ID</label><input id="f-cnpj"></div>
    </div>
    <label>Category</label><input id="f-categoria" placeholder="Electrical materials, PPE, services...">
    <div class="grid3">
      <div class="check"><input type="checkbox" id="f-iso9001"><span>ISO 9001</span></div>
      <div class="check"><input type="checkbox" id="f-iso14001"><span>ISO 14001</span></div>
      <div class="check"><input type="checkbox" id="f-seguranca"><span>Safety certification</span></div>
    </div>
    <div class="grid3">
      <div><label>Years in business</label><input id="f-anos" type="number"></div>
      <div><label>% on-time deliveries</label><input id="f-entregas" type="number"></div>
      <div><label>Quality incidents</label><input id="f-incidentes" type="number"></div>
    </div>
    <button onclick="criarFornecedor()">Register and calculate score</button>
    <table id="fornecedores-table"><thead><tr><th>Name</th><th>Category</th><th>Score</th><th>Rating</th></tr></thead><tbody></tbody></table>
  </div>

  <div class="card">
    <h2>📝 Purchase requisition</h2>
    <label>Description</label><input id="r-descricao" placeholder="30 centrifugal pumps">
    <div class="grid2">
      <div><label>Quantity</label><input id="r-quantidade" type="number"></div>
      <div><label>Unit</label><input id="r-unidade" placeholder="unit, kg, m²..."></div>
    </div>
    <button onclick="criarRequisicao()">Create requisition</button>
    <div id="requisicao-resultado" style="margin-top:10px;font-size:.85rem;color:#166534"></div>
  </div>

  <div class="card">
    <h2>📨 RFQ and quote comparison</h2>
    <label>Requisition ID</label><input id="rfq-requisicao-id" placeholder="paste the ID generated above">
    <label>Scope</label><input id="rfq-escopo" placeholder="Technical specification of what's needed">
    <button onclick="criarRfq()">Generate RFQ</button>
    <div id="rfq-resultado" style="margin-top:10px;font-size:.85rem;color:#166534"></div>

    <label style="margin-top:20px">RFQ ID (to register a quote)</label><input id="cot-rfq-id">
    <div class="grid3">
      <div><label>Vendor ID</label><input id="cot-fornecedor-id"></div>
      <div><label>Price</label><input id="cot-preco" type="number"></div>
      <div><label>Lead time (days)</label><input id="cot-prazo" type="number"></div>
    </div>
    <button onclick="registrarCotacao()">Register quote</button>
    <button onclick="verComparativo()" style="background:#64748b">View comparison</button>
    <table id="comparativo-table"><thead><tr><th>Vendor</th><th>Price</th><th>Lead time</th><th>Risk score</th></tr></thead><tbody></tbody></table>
  </div>

</div>
<footer>Global Match Engenharia de Produção · CREA-SP 5071200171</footer>

<script>
const API = "/api/procurement-copilot";

function badgeClass(c){ return {"Baixo Risco":"baixo","Risco Moderado":"moderado","Alto Risco":"alto","Critico":"critico"}[c] || ""; }

async function carregarDashboard(){
  const r = await fetch(`${API}/dashboard`);
  const data = await r.json();
  document.getElementById("dashboard-kpis").innerHTML = `
    <div class="kpi"><div class="num">${data.total_fornecedores}</div><div class="label">Vendors</div></div>
    <div class="kpi"><div class="num">${data.fornecedores_alto_risco}</div><div class="label">High risk</div></div>
    <div class="kpi"><div class="num">$ ${(data.spend.gasto_total||0).toLocaleString()}</div><div class="label">Total spend</div></div>`;
  const tbody = document.querySelector("#abc-table tbody");
  tbody.innerHTML = (data.spend.curva_abc || []).map(c =>
    `<tr><td>${c.categoria||"-"}</td><td>$ ${c.total.toLocaleString()}</td><td>${c.pct_do_total}%</td><td>${c.classe_abc}</td></tr>`
  ).join("");
  await carregarFornecedores();
}

async function criarFornecedor(){
  const body = {
    nome: document.getElementById("f-nome").value,
    cnpj: document.getElementById("f-cnpj").value,
    categoria: document.getElementById("f-categoria").value,
    tem_iso9001: document.getElementById("f-iso9001").checked,
    tem_iso14001: document.getElementById("f-iso14001").checked,
    tem_certificado_seguranca: document.getElementById("f-seguranca").checked,
    anos_mercado: parseInt(document.getElementById("f-anos").value) || 0,
    entregas_no_prazo_pct: parseInt(document.getElementById("f-entregas").value) || 0,
    incidentes_qualidade: parseInt(document.getElementById("f-incidentes").value) || 0,
  };
  await fetch(`${API}/fornecedores`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)});
  await carregarFornecedores();
}

async function carregarFornecedores(){
  const r = await fetch(`${API}/fornecedores`);
  const data = await r.json();
  document.querySelector("#fornecedores-table tbody").innerHTML = data.map(f =>
    `<tr><td>${f.nome} <small style="color:#94a3b8">${f.id.slice(0,8)}</small></td><td>${f.categoria||"-"}</td><td>${f.score_risco}</td><td><span class="badge ${badgeClass(f.classificacao)}">${f.classificacao}</span></td></tr>`
  ).join("");
}

async function criarRequisicao(){
  const body = {
    descricao: document.getElementById("r-descricao").value,
    quantidade: parseFloat(document.getElementById("r-quantidade").value) || null,
    unidade: document.getElementById("r-unidade").value,
  };
  const r = await fetch(`${API}/requisicoes`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)});
  const data = await r.json();
  document.getElementById("requisicao-resultado").textContent = `Requisition created! ID: ${data.id}`;
  document.getElementById("rfq-requisicao-id").value = data.id;
}

async function criarRfq(){
  const body = {
    requisicao_id: document.getElementById("rfq-requisicao-id").value,
    escopo: document.getElementById("rfq-escopo").value,
  };
  const r = await fetch(`${API}/rfqs`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)});
  const data = await r.json();
  document.getElementById("rfq-resultado").textContent = `RFQ created! ID: ${data.id}`;
  document.getElementById("cot-rfq-id").value = data.id;
}

async function registrarCotacao(){
  const body = {
    rfq_id: document.getElementById("cot-rfq-id").value,
    fornecedor_id: document.getElementById("cot-fornecedor-id").value,
    preco: parseFloat(document.getElementById("cot-preco").value) || 0,
    prazo_dias: parseInt(document.getElementById("cot-prazo").value) || 0,
  };
  await fetch(`${API}/cotacoes`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)});
  await verComparativo();
}

async function verComparativo(){
  const rfqId = document.getElementById("cot-rfq-id").value;
  if(!rfqId) return;
  const r = await fetch(`${API}/rfqs/${rfqId}/comparativo`);
  const data = await r.json();
  document.querySelector("#comparativo-table tbody").innerHTML = data.map(c =>
    `<tr><td>${c.fornecedor_nome}</td><td>$ ${c.preco}</td><td>${c.prazo_dias}d</td><td><span class="badge ${badgeClass(c.classificacao)}">${c.score_risco}</span></td></tr>`
  ).join("");
}

carregarDashboard();
</script>
</body></html>
"""


@page_router.get("/procurement-copilot", response_class=HTMLResponse)
async def procurement_copilot_page():
    return _HTML
