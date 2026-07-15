"""Pagina web unificada para os 4 agentes de International Expansion —
india_multilingual_agent, uae_government_agent, ley1581_agent (Colombia),
lfpdppp_agent (Mexico). Todos reais (chamam DeepSeek com o input do cliente),
so faltava uma interface — igual foi feito para o NR1."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["international-expansion-page"])

_HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>International Expansion Copilot | Global Match Engenharia</title>
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
.checkout{display:inline-block;margin-top:14px;background:var(--primary);color:#fff;text-decoration:none;padding:10px 18px;border-radius:8px;font-weight:700;font-size:.9rem}
footer{text-align:center;color:#94a3b8;font-size:.8rem;padding:24px}
</style></head>
<body>
<header><img src="https://global-engenharia.com/assets/logo.webp" alt="Global Match"><span>International Expansion Copilot</span></header>
<div class="container">

  <div class="card">
    <h2>1. Choose your market</h2>
    <select id="agente-select" onchange="trocarAgente()">
      <option value="india" data-pattern="chat" data-endpoint="/api/india/chat">India — Multilingual Support</option>
      <option value="uae" data-pattern="chat" data-endpoint="/api/uae/chat">UAE — Government Processes</option>
      <option value="ley1581" data-pattern="diag" data-endpoint="/api/ley1581/diagnostico">Colombia — Ley 1581 (personal data)</option>
      <option value="lfpdppp" data-pattern="diag" data-endpoint="/api/lfpdppp/diagnostico">Mexico — LFPDPPP (personal data)</option>
    </select>
    <label>Your email (license)</label><input id="in-email" type="email" placeholder="you@email.com">
  </div>

  <div class="card" id="card-chat">
    <h2>2. Message</h2>
    <textarea id="in-message" rows="5" placeholder="Describe your question or situation..."></textarea>
    <button onclick="enviarChat()">Send</button>
  </div>

  <div class="card hidden" id="card-diag">
    <h2>2. Company data</h2>
    <label>Company</label><input id="in-empresa" placeholder="Example Company Inc.">
    <label>Sector</label><input id="in-sector" placeholder="Finance, Healthcare, Retail...">
    <label>Types of data processed</label>
    <textarea id="in-tipos-datos" rows="3" placeholder="Customer data, employee data, cards..."></textarea>
    <button onclick="enviarDiag()">Generate diagnostic</button>
  </div>

  <div class="card hidden" id="card-resultado">
    <h2>Result</h2>
    <pre id="resultado"></pre>
    <a class="checkout hidden" id="link-checkout" target="_blank">Subscribe / Unlock full access</a>
  </div>

</div>
<footer>Global Match Engenharia de Produção · CREA-SP 5071200171</footer>

<script>
function opcaoAtual(){ const sel = document.getElementById("agente-select"); return sel.options[sel.selectedIndex]; }

function trocarAgente(){
  const pattern = opcaoAtual().dataset.pattern;
  document.getElementById("card-chat").classList.toggle("hidden", pattern !== "chat");
  document.getElementById("card-diag").classList.toggle("hidden", pattern !== "diag");
  document.getElementById("card-resultado").classList.add("hidden");
}

function mostrarResultado(data){
  document.getElementById("card-resultado").classList.remove("hidden");
  document.getElementById("resultado").textContent = data.response || data.analysis || data.preview || JSON.stringify(data, null, 2);
  const link = document.getElementById("link-checkout");
  if(data.checkout_url && data.checkout_url.startsWith("http")){
    link.href = data.checkout_url;
    link.classList.remove("hidden");
  } else {
    link.classList.add("hidden");
  }
}

async function enviarChat(){
  const endpoint = opcaoAtual().dataset.endpoint;
  const r = await fetch(endpoint, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({
    message: document.getElementById("in-message").value,
    customer_email: document.getElementById("in-email").value,
  })});
  mostrarResultado(await r.json());
}

async function enviarDiag(){
  const endpoint = opcaoAtual().dataset.endpoint;
  const r = await fetch(endpoint, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({
    empresa: document.getElementById("in-empresa").value,
    sector: document.getElementById("in-sector").value,
    tipos_datos: document.getElementById("in-tipos-datos").value,
    customer_email: document.getElementById("in-email").value,
  })});
  mostrarResultado(await r.json());
}

trocarAgente();
</script>
</body></html>
"""


@router.get("/international-expansion", response_class=HTMLResponse)
async def international_expansion_page():
    return _HTML
