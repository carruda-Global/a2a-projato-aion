"""Pagina web unificada para os 10 agentes de engenharia AEC (Engineering Suite)."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["engineering-suite-page"])

_HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Engineering Suite | Global Match Engenharia</title>
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
.hidden{display:none}
pre{background:#f8fafc;padding:16px;border-radius:8px;font-size:.8rem;overflow:auto;max-height:400px;white-space:pre-wrap}
footer{text-align:center;color:#94a3b8;font-size:.8rem;padding:24px}
</style></head>
<body>
<header><img src="https://global-engenharia.com/assets/logo.webp" alt="Global Match"><span>Engineering Suite</span></header>
<div class="container">

  <div class="card">
    <h2>1. Project</h2>
    <p style="color:#64748b;font-size:.85rem">Use the same Project ID created in Engineering Copilot — the result is saved to that project's history.</p>
    <label>Project ID</label><input id="in-projeto-id" placeholder="Project UUID">
    <label>Email (license)</label><input id="in-email" type="email" placeholder="you@email.com">
  </div>

  <div class="card">
    <h2>2. Choose an action</h2>
    <select id="acao-select" onchange="trocarForm()">
      <optgroup label="Spec Analyst">
        <option value="/spec-analyst/analyze" data-pattern="text">Analyze technical document</option>
        <option value="/spec-analyst/check-compliance" data-pattern="pair">Check compliance with standard</option>
      </optgroup>
      <optgroup label="Requirements Analyst">
        <option value="/requirements-analyst/analyze" data-pattern="text">Extract requirements</option>
        <option value="/requirements-analyst/check-consistency" data-pattern="pair">Check consistency between requirements</option>
      </optgroup>
      <optgroup label="BIM Coordinator">
        <option value="/bim-coordinator/generate-element" data-pattern="text">Generate BIM element</option>
        <option value="/bim-coordinator/clash-detection" data-pattern="text">Clash detection</option>
      </optgroup>
      <optgroup label="Field Execution">
        <option value="/field-execution/instructions" data-pattern="text">Generate field instructions</option>
        <option value="/field-execution/deviations" data-pattern="pair">Identify deviations (as-built x design)</option>
      </optgroup>
      <optgroup label="Logistics">
        <option value="/logistics/check-issues" data-pattern="text">Check delivery issues</option>
      </optgroup>
      <optgroup label="Inventory">
        <option value="/inventory/suggest-substitute" data-pattern="pair">Suggest substitute material</option>
      </optgroup>
      <optgroup label="RFI">
        <option value="/rfi/create" data-pattern="question">Create RFI</option>
        <option value="/rfi/search-specification" data-pattern="question">Search answer in specification</option>
      </optgroup>
      <optgroup label="Work Synopsis">
        <option value="/work-synopsis/generate" data-pattern="text">Generate task summary</option>
        <option value="/work-synopsis/status" data-pattern="text">Summarize project status</option>
      </optgroup>
      <optgroup label="Engineering Assistant">
        <option value="/engineering-assistant/ask" data-pattern="question">Ask the assistant</option>
        <option value="/engineering-assistant/summarize" data-pattern="text">Summarize document</option>
      </optgroup>
      <optgroup label="Photo Intelligence">
        <option value="/photo-intelligence/analyze" data-pattern="text">Analyze photo (description)</option>
        <option value="/photo-intelligence/compare-schedule" data-pattern="pair">Compare photo with schedule</option>
      </optgroup>
    </select>
  </div>

  <div class="card" id="card-text">
    <h2>3. Text</h2>
    <label>Content</label><textarea id="in-text" rows="6" placeholder="Paste the text/document here..."></textarea>
    <button onclick="enviarText()">Run</button>
  </div>

  <div class="card hidden" id="card-pair">
    <h2>3. Two texts to compare</h2>
    <label>Text A</label><textarea id="in-text-a" rows="4"></textarea>
    <label>Text B</label><textarea id="in-text-b" rows="4"></textarea>
    <button onclick="enviarPair()">Run</button>
  </div>

  <div class="card hidden" id="card-question">
    <h2>3. Question</h2>
    <label>Question</label><input id="in-question">
    <label>Context (optional)</label><textarea id="in-context" rows="4"></textarea>
    <button onclick="enviarQuestion()">Run</button>
  </div>

  <div class="card hidden" id="card-resultado">
    <h2>Result</h2>
    <pre id="resultado"></pre>
  </div>

</div>
<footer>Global Match Engenharia de Produção · CREA-SP 5071200171</footer>

<script>
const API = "/api/engineering-suite";

function trocarForm(){
  const opt = document.getElementById("acao-select").selectedOptions[0];
  const pattern = opt.dataset.pattern;
  document.getElementById("card-text").classList.toggle("hidden", pattern !== "text");
  document.getElementById("card-pair").classList.toggle("hidden", pattern !== "pair");
  document.getElementById("card-question").classList.toggle("hidden", pattern !== "question");
  document.getElementById("card-resultado").classList.add("hidden");
}

function mostrarResultado(data){
  document.getElementById("card-resultado").classList.remove("hidden");
  document.getElementById("resultado").textContent = JSON.stringify(data, null, 2);
}

function _base(){
  return {
    projeto_id: document.getElementById("in-projeto-id").value,
    customer_email: document.getElementById("in-email").value,
  };
}

async function enviarText(){
  const path = document.getElementById("acao-select").value;
  const r = await fetch(API + path, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({
    ..._base(), text: document.getElementById("in-text").value,
  })});
  mostrarResultado(await r.json());
}

async function enviarPair(){
  const path = document.getElementById("acao-select").value;
  const r = await fetch(API + path, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({
    ..._base(), text_a: document.getElementById("in-text-a").value, text_b: document.getElementById("in-text-b").value,
  })});
  mostrarResultado(await r.json());
}

async function enviarQuestion(){
  const path = document.getElementById("acao-select").value;
  const r = await fetch(API + path, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({
    ..._base(), question: document.getElementById("in-question").value, context: document.getElementById("in-context").value,
  })});
  mostrarResultado(await r.json());
}

trocarForm();
</script>
</body></html>
"""


@router.get("/engineering-suite", response_class=HTMLResponse)
async def engineering_suite_page():
    return _HTML
