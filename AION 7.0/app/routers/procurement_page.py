"""Pagina web do Procurement Copilot — escopo real de hoje: processar
lista de materiais e comparar cotacoes. O MVP completo (Vendor
Intelligence, RFQ, Contract Intelligence, Spend Analytics, Dashboard)
ainda nao existe."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["procurement-page"])

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
.container{max-width:680px;margin:32px auto;padding:0 16px}
.card{background:#fff;border-radius:12px;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:20px}
h2{margin:0 0 16px;color:var(--primary);font-size:1.2rem}
label{display:block;font-weight:600;margin-top:14px;font-size:.9rem}
input{width:100%;padding:10px;margin-top:5px;border:1px solid #dee2e6;border-radius:8px;font-size:.95rem}
button{margin-top:20px;background:var(--green);color:#fff;border:none;padding:12px 24px;border-radius:8px;font-weight:700;cursor:pointer;font-size:.95rem}
button.add{background:#64748b;padding:8px 16px;font-size:.85rem;margin-top:8px}
.row{display:grid;grid-template-columns:2fr 1fr 1fr;gap:8px;margin-top:8px}
.row3{display:grid;grid-template-columns:2fr 1fr 1fr;gap:8px;margin-top:8px}
pre{background:#f8fafc;padding:16px;border-radius:8px;font-size:.85rem;overflow:auto;max-height:400px;white-space:pre-wrap}
.hidden{display:none}
footer{text-align:center;color:#94a3b8;font-size:.8rem;padding:24px}
.notice{background:#fff3cd;padding:10px 14px;border-radius:8px;font-size:.82rem;margin-bottom:16px}
</style></head>
<body>
<header><img src="https://global-engenharia.com/assets/logo.webp" alt="Global Match"><span>Procurement Copilot</span></header>
<div class="container">
  <div class="notice">Current version: AI-driven order processing and quote comparison. Vendor Intelligence, automatic RFQ, Contract Intelligence and Spend Analytics are still in development.</div>

  <div class="card">
    <h2>Process material list</h2>
    <div id="materiais"></div>
    <button class="add" onclick="addMaterial()">+ add material</button>
    <br><button onclick="processarPedido()">Process order</button>
    <pre id="pedido-resultado" class="hidden"></pre>
  </div>

  <div class="card">
    <h2>Compare vendor quotes</h2>
    <div id="cotacoes"></div>
    <button class="add" onclick="addCotacao()">+ add quote</button>
    <br><button onclick="compararCotacoes()">Compare and recommend</button>
    <pre id="cotacao-resultado" class="hidden"></pre>
  </div>
</div>
<footer>Global Match Engenharia de Produção · CREA-SP 5071200171</footer>

<script>
const API = "/api/procurement";

function addMaterial(){
  const div = document.createElement("div");
  div.className = "row";
  div.innerHTML = `<input placeholder="Material" class="mat-name">
    <input placeholder="Qty" type="number" class="mat-qty">
    <input placeholder="Unit" class="mat-unit">`;
  document.getElementById("materiais").appendChild(div);
}
function addCotacao(){
  const div = document.createElement("div");
  div.className = "row3";
  div.innerHTML = `<input placeholder="Supplier" class="cot-supplier">
    <input placeholder="Price" type="number" class="cot-price">
    <input placeholder="Lead time" class="cot-lead">`;
  document.getElementById("cotacoes").appendChild(div);
}
addMaterial(); addMaterial();
addCotacao(); addCotacao();

async function processarPedido(){
  const materials = [...document.querySelectorAll("#materiais .row")].map(r => ({
    name: r.querySelector(".mat-name").value,
    quantity: parseFloat(r.querySelector(".mat-qty").value) || 0,
    unit: r.querySelector(".mat-unit").value,
  }));
  const r = await fetch(`${API}/process-order`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({materials})});
  const data = await r.json();
  const el = document.getElementById("pedido-resultado");
  el.classList.remove("hidden");
  el.textContent = data.order_plan || JSON.stringify(data, null, 2);
}

async function compararCotacoes(){
  const quotes = [...document.querySelectorAll("#cotacoes .row3")].map(r => ({
    supplier: r.querySelector(".cot-supplier").value,
    price: parseFloat(r.querySelector(".cot-price").value) || 0,
    lead_time: r.querySelector(".cot-lead").value,
  }));
  const r = await fetch(`${API}/compare-quotes`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({quotes})});
  const data = await r.json();
  const el = document.getElementById("cotacao-resultado");
  el.classList.remove("hidden");
  el.textContent = data.recomendacao || JSON.stringify(data, null, 2);
}
</script>
</body></html>
"""


@router.get("/procurement", response_class=HTMLResponse)
async def procurement_page():
    return _HTML
