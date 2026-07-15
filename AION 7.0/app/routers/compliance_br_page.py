"""Pagina web unificada do Compliance Copilot BR (LGPD, Tributario CBS/IBS,
ESG/IFRS, Inventario de Carbono, Escopo 3, Canal de Denuncias, Igualdade
Salarial, Anticorrupcao)."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["compliance-br-page"])

_HTML = """<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Compliance Copilot BR | Global Match Engenharia</title>
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
<header><img src="https://global-engenharia.com/assets/logo.webp" alt="Global Match"><span>Compliance Copilot BR</span></header>
<div class="container">

  <div class="card">
    <h2>1. Escolha a ação</h2>
    <select id="acao-select" onchange="trocarForm()">
      <optgroup label="LGPD (Privacy Intelligence)">
        <option value="/lgpd/mapear-fluxos" data-pattern="text">Mapear fluxos de dados pessoais</option>
        <option value="/lgpd/gerar-ropa" data-pattern="text">Gerar registro de operações (ROPA)</option>
        <option value="/lgpd/avaliar-conformidade" data-pattern="text">Avaliar conformidade LGPD</option>
      </optgroup>
      <optgroup label="Tributário CBS/IBS (Tax Intelligence)">
        <option value="/tributario/classificar-produto" data-pattern="text">Classificar produto/serviço</option>
        <option value="/tributario/verificar-conformidade" data-pattern="text">Verificar conformidade tributária</option>
        <option value="/tributario/simular-impacto" data-pattern="text">Simular impacto financeiro CBS/IBS</option>
      </optgroup>
      <optgroup label="ESG / IFRS">
        <option value="/esg/diagnosticar-maturidade" data-pattern="text">Diagnosticar maturidade ESG</option>
        <option value="/esg/relatorio-sustentabilidade" data-pattern="text">Gerar relatório de sustentabilidade</option>
      </optgroup>
      <optgroup label="Inventário de Carbono">
        <option value="/carbono/calcular-emissoes" data-pattern="text">Calcular emissões</option>
        <option value="/carbono/gerar-inventario" data-pattern="text">Gerar inventário completo</option>
        <option value="/carbono/hotspots" data-pattern="text">Identificar hotspots de emissão</option>
      </optgroup>
      <optgroup label="Escopo 3 / Fornecedores">
        <option value="/escopo3/avaliar-fornecedores" data-pattern="text">Avaliar emissões da cadeia de fornecedores</option>
      </optgroup>
      <optgroup label="Canal de Denúncias">
        <option value="/whistleblower-br/classificar" data-pattern="text">Classificar denúncia</option>
        <option value="/whistleblower-br/relatorio-semestral" data-pattern="text">Gerar relatório semestral</option>
        <option value="/whistleblower-br/configurar-canal" data-pattern="text">Configurar canal</option>
      </optgroup>
      <optgroup label="Igualdade Salarial">
        <option value="/igualdade-salarial/analisar-equidade" data-pattern="text">Analisar equidade salarial</option>
        <option value="/igualdade-salarial/relatorio-mte" data-pattern="text">Gerar relatório MTE (Lei 14.611/2023)</option>
        <option value="/igualdade-salarial/monitorar-diversidade" data-pattern="text">Monitorar diversidade</option>
      </optgroup>
      <optgroup label="Anticorrupção / Integridade">
        <option value="/anticorrupcao/diagnosticar-maturidade" data-pattern="text">Diagnosticar maturidade do programa</option>
        <option value="/anticorrupcao/gerar-codigo-etica" data-pattern="text">Gerar código de ética</option>
        <option value="/anticorrupcao/due-diligence" data-pattern="text">Due diligence de terceiros</option>
        <option value="/anticorrupcao/relatorio-cgu" data-pattern="text">Gerar relatório CGU</option>
      </optgroup>
    </select>
  </div>

  <div class="card" id="card-text">
    <h2>2. Dados da empresa / documento</h2>
    <label>Descreva a empresa, situação ou cole o documento relevante</label>
    <textarea id="in-text" rows="8" placeholder="Nome da empresa, setor, CNAE, dados relevantes para a análise..."></textarea>
    <button onclick="enviarText()">Executar</button>
  </div>

  <div class="card hidden" id="card-pair">
    <h2>2. Questionário + dados da empresa</h2>
    <label>Questionário</label><textarea id="in-text-a" rows="4"></textarea>
    <label>Dados da empresa</label><textarea id="in-text-b" rows="4"></textarea>
    <button onclick="enviarPair()">Executar</button>
  </div>

  <div class="card hidden" id="card-resultado">
    <h2>Resultado</h2>
    <pre id="resultado"></pre>
  </div>

</div>
<footer>Global Match Engenharia de Produção · CREA-SP 5071200171</footer>

<script>
const API = "/api/compliance-br";

function trocarForm(){
  const opt = document.getElementById("acao-select").selectedOptions[0];
  const pattern = opt.dataset.pattern;
  document.getElementById("card-text").classList.toggle("hidden", pattern !== "text");
  document.getElementById("card-pair").classList.toggle("hidden", pattern !== "pair");
  document.getElementById("card-resultado").classList.add("hidden");
}

function mostrarResultado(data){
  document.getElementById("card-resultado").classList.remove("hidden");
  document.getElementById("resultado").textContent = JSON.stringify(data, null, 2);
}

async function enviarText(){
  const path = document.getElementById("acao-select").value;
  const r = await fetch(API + path, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({text: document.getElementById("in-text").value})});
  mostrarResultado(await r.json());
}

async function enviarPair(){
  const path = document.getElementById("acao-select").value;
  const r = await fetch(API + path, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({
    text_a: document.getElementById("in-text-a").value, text_b: document.getElementById("in-text-b").value,
  })});
  mostrarResultado(await r.json());
}

trocarForm();
</script>
</body></html>
"""


@router.get("/compliance-br", response_class=HTMLResponse)
async def compliance_br_page():
    return _HTML
