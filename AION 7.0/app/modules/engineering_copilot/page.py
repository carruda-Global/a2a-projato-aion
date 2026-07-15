"""Pagina web do Engineering Copilot — fluxo completo: projeto -> documentos ->
fotos -> compliance -> documentos gerados. Mesmo padrao da pagina do NR1."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

page_router = APIRouter(tags=["engineering-copilot-page"])

_HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Engineering Copilot | Global Match Engenharia</title>
<link rel="icon" href="https://global-engenharia.com/assets/logo.webp">
<style>
:root{--primary:#0d2c4c;--accent:#f0b429;--green:#00C36B}
*{box-sizing:border-box}
body{font-family:'Segoe UI',Inter,sans-serif;background:#f4f6f8;margin:0;color:#1e293b}
header{background:var(--primary);padding:16px 24px;display:flex;align-items:center;gap:12px}
header img{height:36px}
header span{color:#fff;font-weight:700;font-size:1.1rem}
.container{max-width:720px;margin:32px auto;padding:0 16px}
.card{background:#fff;border-radius:12px;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:20px}
h2{margin:0 0 16px;color:var(--primary);font-size:1.2rem}
label{display:block;font-weight:600;margin-top:14px;font-size:.9rem}
input,select,textarea{width:100%;padding:10px;margin-top:5px;border:1px solid #dee2e6;border-radius:8px;font-size:.95rem;font-family:inherit}
button{margin-top:20px;background:var(--green);color:#fff;border:none;padding:12px 24px;border-radius:8px;font-weight:700;cursor:pointer;font-size:.95rem}
button.secondary{background:var(--primary)}
button:hover{opacity:.9}
.hidden{display:none}
.msg{padding:10px;border-radius:8px;font-size:.85rem;margin-top:12px;white-space:pre-wrap}
.msg.ok{background:#e6f9f0;color:#166534}
.msg.err{background:#fef2f2;color:#991b1b}
.docs-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}
.docs-grid button{margin:0;font-size:.85rem;padding:10px}
footer{text-align:center;color:#94a3b8;font-size:.8rem;padding:24px}
</style></head>
<body>
<header><img src="https://global-engenharia.com/assets/logo.webp" alt="Global Match"><span>Engineering Copilot</span></header>
<div class="container">

  <div class="card" id="card-projeto">
    <h2>1. New Project</h2>
    <label>Client</label><input id="pj-cliente" placeholder="Client name">
    <label>Location</label><input id="pj-local" placeholder="Address / site">
    <label>Scope</label><textarea id="pj-escopo" rows="2" placeholder="Service scope description"></textarea>
    <label>Email (license)</label><input id="pj-email" type="email" placeholder="you@email.com">
    <button onclick="criarProjeto()">Create project</button>
    <div id="projeto-msg"></div>
  </div>

  <div class="card hidden" id="card-documentos">
    <h2>2. Document Upload</h2>
    <p style="color:#64748b;font-size:.85rem">PDF, DOCX, XLSX or CSV — the AI extracts equipment, TAGs, models, manufacturers, standards and dates.</p>
    <input id="doc-arquivo" type="file" accept=".pdf,.docx,.xlsx,.csv,.txt">
    <button onclick="enviarDocumento()">Upload document</button>
    <div id="documentos-msg"></div>
  </div>

  <div class="card hidden" id="card-fotos">
    <h2>3. Photo Upload</h2>
    <p style="color:#64748b;font-size:.85rem">JPG, PNG or HEIC — the AI identifies equipment, OCRs the TAG, and flags leaks, corrosion and insulation issues.</p>
    <input id="foto-arquivo" type="file" accept=".jpg,.jpeg,.png,.heic">
    <button onclick="enviarFoto()">Upload photo</button>
    <div id="fotos-msg"></div>
  </div>

  <div class="card hidden" id="card-assistente">
    <h2>4. Engineering Assistant</h2>
    <label>Question</label>
    <textarea id="pergunta" rows="2" placeholder="E.g.: Is any document missing? Does the PMOC meet the legislation?"></textarea>
    <button onclick="perguntar()">Ask</button>
    <div id="assistente-msg"></div>
  </div>

  <div class="card hidden" id="card-compliance">
    <h2>5. Compliance</h2>
    <button class="secondary" onclick="verCompliance()">View compliance (NR/ABNT/CREA/ANVISA)</button>
    <div id="compliance-msg"></div>
  </div>

  <div class="card hidden" id="card-documentos-gerados">
    <h2>6. Generated Documents</h2>
    <div class="docs-grid">
      <button onclick="gerarDocumento('memorial')">Descriptive Memorial</button>
      <button onclick="gerarDocumento('relatorio_tecnico')">Technical Report</button>
      <button onclick="gerarDocumento('inventario')">Inventory</button>
      <button onclick="gerarDocumento('checklist')">Technical Checklist</button>
      <button onclick="gerarDocumento('plano_manutencao')">Maintenance Plan</button>
      <button onclick="gerarDocumento('relatorio_fotografico')">Photo Report</button>
      <button onclick="gerarDocumento('data_book')">Data Book</button>
      <button onclick="gerarDocumento('relatorio_executivo')">Executive Report</button>
      <button onclick="gerarDocumento('as_built')">As Built</button>
    </div>
    <div id="gerar-msg"></div>
  </div>

</div>
<footer>Global Match Engenharia de Producao · CREA-SP 5071200171</footer>

<script>
const API = "/api/engineering-copilot";
let projetoId = null, customerEmail = "";

function mostrar(id){ document.getElementById(id).classList.remove("hidden"); }
function msg(id, texto, ok){
  const el = document.getElementById(id);
  el.className = "msg " + (ok ? "ok" : "err");
  el.textContent = texto;
}

async function criarProjeto(){
  const cliente = document.getElementById("pj-cliente").value;
  const local = document.getElementById("pj-local").value;
  const escopo = document.getElementById("pj-escopo").value;
  customerEmail = document.getElementById("pj-email").value;
  try{
    const r = await fetch(`${API}/projetos`, {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({cliente, local, escopo, customer_email: customerEmail})});
    if(!r.ok){ msg("projeto-msg", "Error creating project.", false); return; }
    const data = await r.json();
    projetoId = data.id;
    msg("projeto-msg", "Project created!", true);
    mostrar("card-documentos"); mostrar("card-fotos"); mostrar("card-assistente");
    mostrar("card-compliance"); mostrar("card-documentos-gerados");
  }catch(e){ msg("projeto-msg", "Error: " + e.message, false); }
}

async function enviarDocumento(){
  const arquivo = document.getElementById("doc-arquivo").files[0];
  if(!arquivo){ msg("documentos-msg", "Select a file.", false); return; }
  const form = new FormData(); form.append("file", arquivo);
  try{
    const r = await fetch(`${API}/projetos/${projetoId}/documentos`, {method:"POST", body: form});
    if(!r.ok){ msg("documentos-msg", "Error processing document.", false); return; }
    const data = await r.json();
    msg("documentos-msg", `Document processed: ${(data.extraido.equipamentos||[]).length} equipment item(s), ${(data.extraido.normas||[]).length} standard(s).`, true);
  }catch(e){ msg("documentos-msg", "Error: " + e.message, false); }
}

async function enviarFoto(){
  const arquivo = document.getElementById("foto-arquivo").files[0];
  if(!arquivo){ msg("fotos-msg", "Select a photo.", false); return; }
  const form = new FormData(); form.append("file", arquivo);
  try{
    const r = await fetch(`${API}/projetos/${projetoId}/fotos`, {method:"POST", body: form});
    if(!r.ok){ msg("fotos-msg", "Error processing photo.", false); return; }
    const data = await r.json();
    const problemas = (data.analise.problemas||[]).join(", ") || "no visible issues";
    msg("fotos-msg", `Photo analyzed. Issues: ${problemas}`, true);
  }catch(e){ msg("fotos-msg", "Error: " + e.message, false); }
}

async function perguntar(){
  const pergunta = document.getElementById("pergunta").value;
  try{
    const r = await fetch(`${API}/projetos/${projetoId}/perguntar`, {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({pergunta})});
    if(!r.ok){ msg("assistente-msg", "Error querying assistant.", false); return; }
    const data = await r.json();
    msg("assistente-msg", data.resposta, true);
  }catch(e){ msg("assistente-msg", "Error: " + e.message, false); }
}

async function verCompliance(){
  try{
    const r = await fetch(`${API}/projetos/${projetoId}/compliance`);
    if(!r.ok){ msg("compliance-msg", "Error assessing compliance.", false); return; }
    const data = await r.json();
    msg("compliance-msg", `Score: ${data.score_conformidade}/100 — Pending: ${data.pendencias.length}`, data.pendencias.length === 0);
  }catch(e){ msg("compliance-msg", "Error: " + e.message, false); }
}

async function gerarDocumento(tipo){
  try{
    const r = await fetch(`${API}/projetos/${projetoId}/gerar/${tipo}?customer_email=${encodeURIComponent(customerEmail)}`);
    if(!r.ok){ msg("gerar-msg", "Error generating document.", false); return; }
    const blob = await r.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = tipo + ".docx"; a.click();
    const status = r.headers.get("X-License-Status");
    const checkoutUrl = r.headers.get("X-Checkout-Url");
    if(status === "demo" && checkoutUrl){
      msg("gerar-msg", `Document generated in demo mode (watermarked). Subscribe to remove the watermark: ${checkoutUrl}`, false);
    } else {
      msg("gerar-msg", "Document generated successfully!", true);
    }
  }catch(e){ msg("gerar-msg", "Error: " + e.message, false); }
}
</script>
</body></html>
"""


@page_router.get("/engineering-copilot", response_class=HTMLResponse)
async def engineering_copilot_page():
    return _HTML
