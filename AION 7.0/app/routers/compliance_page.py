"""Pagina web unificada para os 12 Copilots do Global Compliance Copilot —
cada um ja existe como router (soc2, iso27001, vendor_risk, contract_risk,
eu_ai_act, dora, nis2, csrd, reg-monitor, whistleblower, board-report,
ma-diligence). Essa pagina da uma interface de verdade pro cliente usar,
igual foi feito para o NR1 AI."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["compliance-page"])

_HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Global Compliance Copilot | Global Match Engenharia</title>
<link rel="icon" href="https://global-engenharia.com/assets/logo.webp">
<style>
:root{--primary:#0d2c4c;--green:#00C36B}
*{box-sizing:border-box}
body{font-family:'Segoe UI',Inter,sans-serif;background:#f4f6f8;margin:0;color:#1e293b}
header{background:var(--primary);padding:16px 24px;display:flex;align-items:center;gap:12px}
header img{height:36px}
header span{color:#fff;font-weight:700;font-size:1.1rem}
.container{max-width:700px;margin:32px auto;padding:0 16px}
.card{background:#fff;border-radius:12px;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:20px}
h2{margin:0 0 16px;color:var(--primary);font-size:1.2rem}
label{display:block;font-weight:600;margin-top:14px;font-size:.9rem}
input,select,textarea{width:100%;padding:10px;margin-top:5px;border:1px solid #dee2e6;border-radius:8px;font-size:.95rem;font-family:inherit}
button{margin-top:20px;background:var(--green);color:#fff;border:none;padding:12px 24px;border-radius:8px;font-weight:700;cursor:pointer;font-size:.95rem}
button:hover{opacity:.9}
.hidden{display:none}
.msg{padding:10px;border-radius:8px;font-size:.85rem;margin-top:12px;white-space:pre-wrap}
.msg.ok{background:#e6f9f0;color:#166534}
.msg.err{background:#fef2f2;color:#991b1b}
pre{background:#f8fafc;padding:16px;border-radius:8px;font-size:.8rem;overflow:auto;max-height:400px}
.checklist-item{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #eee;font-size:.9rem}
.checklist-item select{width:160px;margin:0}
footer{text-align:center;color:#94a3b8;font-size:.8rem;padding:24px}
</style></head>
<body>
<header><img src="https://global-engenharia.com/assets/logo.webp" alt="Global Match"><span>Global Compliance Copilot</span></header>
<div class="container">

  <div class="card">
    <h2>1. Choose a Copilot</h2>
    <select id="copilot-select" onchange="trocarCopilot()">
      <option value="soc2" data-pattern="questionario" data-prefix="/api/soc2">SOC 2</option>
      <option value="iso27001" data-pattern="questionario" data-prefix="/api/iso27001">ISO 27001</option>
      <option value="vendor_risk" data-pattern="upload" data-prefix="/api/vendor-risk" data-endpoint="/analyze">Vendor Risk</option>
      <option value="contract_risk" data-pattern="upload" data-prefix="/api/contract-risk" data-endpoint="/analyze">Contract Risk</option>
      <option value="eu_ai_act" data-pattern="upload" data-prefix="/api/eu-ai-act" data-endpoint="/analyze">EU AI Act</option>
      <option value="dora" data-pattern="form" data-prefix="/api/dora" data-endpoint="/compliance-check">DORA</option>
      <option value="nis2" data-pattern="form" data-prefix="/api/nis2" data-endpoint="/scope-check">NIS2</option>
      <option value="csrd" data-pattern="form" data-prefix="/api/csrd" data-endpoint="/readiness-check">CSRD Reporting</option>
      <option value="reg-monitor" data-pattern="form" data-prefix="/api/reg-monitor" data-endpoint="/impact-analysis">Regulatory Monitor</option>
      <option value="whistleblower" data-pattern="form" data-prefix="/api/whistleblower" data-endpoint="/submit-report">Whistleblower</option>
      <option value="board-report" data-pattern="form" data-prefix="/api/board-report" data-endpoint="/generate">Board Reporting</option>
      <option value="ma-diligence" data-pattern="form" data-prefix="/api/ma-diligence" data-endpoint="/compliance-check">M&amp;A Due Diligence</option>
      <option value="reg-analyst" data-pattern="simpletext" data-prefix="/api/enterprise-ops" data-endpoint="/regulatory-analyst/analisar">Regulatory Analyst — Analyze document</option>
      <option value="reg-analyst-risco" data-pattern="simpletext" data-prefix="/api/enterprise-ops" data-endpoint="/regulatory-analyst/relatorio-riscos">Regulatory Analyst — Risk report</option>
      <option value="compliance-pm" data-pattern="simpletext" data-prefix="/api/enterprise-ops" data-endpoint="/compliance-pm/gerenciar-projeto">Compliance PM — Manage project</option>
      <option value="compliance-pm-prazos" data-pattern="simpletext" data-prefix="/api/enterprise-ops" data-endpoint="/compliance-pm/monitorar-prazos">Compliance PM — Track deadlines</option>
    </select>
  </div>

  <div class="card" id="card-upload">
    <h2>2. Company and document</h2>
    <label>Company name</label><input id="up-company" placeholder="Example Company Inc.">
    <label>Document (contract, policy, vendor assessment, etc.)</label>
    <input id="up-file" type="file">
    <label>Your email (optional)</label><input id="up-email" type="email">
    <button onclick="enviarUpload()">Analyze document</button>
    <div id="upload-msg"></div>
  </div>

  <div class="card hidden" id="card-form">
    <h2>2. Company data</h2>
    <label>Company name</label><input id="fm-company" placeholder="Example Company Inc.">
    <label>Sector</label><input id="fm-sector" placeholder="Finance, Healthcare, Technology...">
    <label>Country</label><input id="fm-country" placeholder="United States">
    <label>Additional context</label>
    <textarea id="fm-context" rows="4" placeholder="Describe the current situation, what's already in place, specific questions..."></textarea>
    <button onclick="enviarForm()">Generate analysis</button>
    <div id="form-msg"></div>
  </div>

  <div class="card hidden" id="card-questionario">
    <h2>2. Questionnaire</h2>
    <p id="quest-framework" style="color:#64748b;font-size:.9rem"></p>
    <div id="quest-lista"></div>
    <label>Company name</label><input id="quest-company" placeholder="Example Company Inc.">
    <button onclick="enviarQuestionario()">Generate assessment</button>
    <div id="quest-msg"></div>
  </div>

  <div class="card hidden" id="card-simpletext">
    <h2>2. Text</h2>
    <textarea id="st-text" rows="6" placeholder="Paste the document, project or situation here..."></textarea>
    <button onclick="enviarSimpleText()">Run</button>
    <div id="simpletext-msg"></div>
  </div>

  <div class="card hidden" id="card-resultado">
    <h2>Result</h2>
    <pre id="resultado-json"></pre>
  </div>

</div>
<footer>Global Match Engenharia de Produção · CREA-SP 5071200171</footer>

<script>
function opcaoAtual(){ const sel = document.getElementById("copilot-select"); return sel.options[sel.selectedIndex]; }

function trocarCopilot(){
  const opt = opcaoAtual();
  const pattern = opt.dataset.pattern;
  document.getElementById("card-upload").classList.toggle("hidden", pattern !== "upload");
  document.getElementById("card-form").classList.toggle("hidden", pattern !== "form");
  document.getElementById("card-questionario").classList.toggle("hidden", pattern !== "questionario");
  document.getElementById("card-simpletext").classList.toggle("hidden", pattern !== "simpletext");
  document.getElementById("card-resultado").classList.add("hidden");
  if(pattern === "questionario") carregarQuestionario();
}

async function enviarSimpleText(){
  const opt = opcaoAtual();
  try{
    const r = await fetch(`${opt.dataset.prefix}${opt.dataset.endpoint}`, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text: document.getElementById("st-text").value, customer_email: document.getElementById("up-email").value}),
    });
    mostrarResultado(await r.json());
  }catch(e){ document.getElementById("simpletext-msg").textContent = "Error: " + e.message; }
}

function mostrarResultado(data){
  document.getElementById("card-resultado").classList.remove("hidden");
  document.getElementById("resultado-json").textContent = JSON.stringify(data, null, 2);
}

async function carregarQuestionario(){
  const opt = opcaoAtual();
  try{
    const r = await fetch(`${opt.dataset.prefix}/questionario`);
    const data = await r.json();
    document.getElementById("quest-framework").textContent = data.framework || "";
    const lista = document.getElementById("quest-lista");
    lista.innerHTML = "";
    (data.perguntas || []).forEach(p => {
      const div = document.createElement("div");
      div.className = "checklist-item";
      div.innerHTML = `<span>${p.id} — ${p.nome}</span>
        <select data-controle="${p.id}">
          <option value="implementado">Implemented</option>
          <option value="parcial">Partial</option>
          <option value="ausente">Absent</option>
          <option value="nao_aplicavel">Not applicable</option>
        </select>`;
      lista.appendChild(div);
    });
  }catch(e){ document.getElementById("quest-msg").textContent = "Error loading questionnaire: " + e.message; }
}

async function enviarQuestionario(){
  const opt = opcaoAtual();
  const respostas = [...document.querySelectorAll("#quest-lista select")].map(s => ({controle_id: s.dataset.controle, status: s.value}));
  try{
    const r = await fetch(`${opt.dataset.prefix}/avaliar`, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({company: document.getElementById("quest-company").value, respostas}),
    });
    mostrarResultado(await r.json());
  }catch(e){ document.getElementById("quest-msg").textContent = "Error: " + e.message; }
}

async function enviarUpload(){
  const opt = opcaoAtual();
  const fd = new FormData();
  fd.append("company", document.getElementById("up-company").value);
  fd.append("customer_email", document.getElementById("up-email").value);
  fd.append("file", document.getElementById("up-file").files[0]);
  try{
    const r = await fetch(`${opt.dataset.prefix}${opt.dataset.endpoint}`, {method: "POST", body: fd});
    mostrarResultado(await r.json());
  }catch(e){ document.getElementById("upload-msg").textContent = "Error: " + e.message; }
}

async function enviarForm(){
  const opt = opcaoAtual();
  const body = {
    company: document.getElementById("fm-company").value,
    target: document.getElementById("fm-company").value,
    sector: document.getElementById("fm-sector").value,
    sectors: document.getElementById("fm-sector").value,
    country: document.getElementById("fm-country").value,
    countries: document.getElementById("fm-country").value,
    context: document.getElementById("fm-context").value,
    category: document.getElementById("fm-context").value,
    period: "Q2 2026",
  };
  try{
    const r = await fetch(`${opt.dataset.prefix}${opt.dataset.endpoint}`, {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body),
    });
    mostrarResultado(await r.json());
  }catch(e){ document.getElementById("form-msg").textContent = "Error: " + e.message; }
}

trocarCopilot();
</script>
</body></html>
"""


@router.get("/compliance", response_class=HTMLResponse)
async def compliance_page():
    return _HTML
