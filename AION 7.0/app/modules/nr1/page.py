"""Pagina web do NR1 AI — login + fluxo completo ate gerar o PGR."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

page_router = APIRouter(tags=["nr1-page"])

_HTML = """<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NR1 AI | Global Match Engenharia</title>
<link rel="icon" href="https://global-engenharia.com/assets/logo.webp">
<style>
:root{--primary:#0d2c4c;--accent:#f0b429;--green:#00C36B}
*{box-sizing:border-box}
body{font-family:'Segoe UI',Inter,sans-serif;background:#f4f6f8;margin:0;color:#1e293b}
header{background:var(--primary);padding:16px 24px;display:flex;align-items:center;gap:12px}
header img{height:36px}
header span{color:#fff;font-weight:700;font-size:1.1rem}
.container{max-width:640px;margin:32px auto;padding:0 16px}
.card{background:#fff;border-radius:12px;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:20px}
h2{margin:0 0 16px;color:var(--primary);font-size:1.2rem}
label{display:block;font-weight:600;margin-top:14px;font-size:.9rem}
input,select{width:100%;padding:10px;margin-top:5px;border:1px solid #dee2e6;border-radius:8px;font-size:.95rem}
button{margin-top:20px;background:var(--green);color:#fff;border:none;padding:12px 24px;border-radius:8px;font-weight:700;cursor:pointer;font-size:.95rem}
button:hover{opacity:.9}
.hidden{display:none}
.msg{padding:10px;border-radius:8px;font-size:.85rem;margin-top:12px}
.msg.ok{background:#e6f9f0;color:#166534}
.msg.err{background:#fef2f2;color:#991b1b}
footer{text-align:center;color:#94a3b8;font-size:.8rem;padding:24px}
</style></head>
<body>
<header><img src="https://global-engenharia.com/assets/logo.webp" alt="Global Match"><span>NR1 AI</span></header>
<div class="container">

  <div class="card" id="card-login">
    <h2>1. Login</h2>
    <label>E-mail</label><input id="login-email" type="email" placeholder="seu@email.com">
    <label>Senha</label><input id="login-senha" type="password">
    <button onclick="fazerLogin()">Entrar</button>
    <div id="login-msg"></div>
  </div>

  <div class="card hidden" id="card-empresa">
    <h2>2. Dados da empresa</h2>
    <label>Razão social</label><input id="emp-razao" placeholder="Metalúrgica Exemplo LTDA">
    <label>CNPJ</label><input id="emp-cnpj" placeholder="00.000.000/0001-00">
    <button onclick="criarEmpresa()">Salvar empresa</button>
    <div id="empresa-msg"></div>
  </div>

  <div class="card hidden" id="card-atividade">
    <h2>3. Setor, função e atividade</h2>
    <label>Nome do setor</label><input id="at-setor" placeholder="Produção">
    <label>Cargo</label><input id="at-cargo" placeholder="Soldador">
    <label>Atividade realizada</label><input id="at-nome" placeholder="Soldagem MIG">
    <button onclick="criarAtividade()">Adicionar atividade</button>
    <div id="atividade-msg"></div>
  </div>

  <div class="card hidden" id="card-pgr">
    <h2>4. Gerar PGR</h2>
    <p style="color:#64748b;font-size:.9rem">Baixe o Programa de Gerenciamento de Riscos com base nas atividades cadastradas.</p>
    <button onclick="baixarPGR()">Gerar e baixar PGR (.docx)</button>
    <div id="pgr-msg"></div>
  </div>

</div>
<footer>Global Match Engenharia de Produção · CREA-SP 5071200171</footer>

<script>
const API = "/api/nr1";
let usuarioId = null, empresaId = null, setorId = null, funcaoId = null;

function mostrar(id){ document.getElementById(id).classList.remove("hidden"); }
function msg(id, texto, ok){
  const el = document.getElementById(id);
  el.className = "msg " + (ok ? "ok" : "err");
  el.textContent = texto;
}

async function fazerLogin(){
  const email = document.getElementById("login-email").value;
  const senha = document.getElementById("login-senha").value;
  try{
    const r = await fetch(`${API}/login`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({email, senha})});
    if(!r.ok){ msg("login-msg", "E-mail ou senha inválidos.", false); return; }
    const data = await r.json();
    usuarioId = data.id;
    msg("login-msg", "Login realizado com sucesso!", true);
    mostrar("card-empresa");
  }catch(e){ msg("login-msg", "Erro ao conectar: " + e.message, false); }
}

async function criarEmpresa(){
  const razao_social = document.getElementById("emp-razao").value;
  const cnpj = document.getElementById("emp-cnpj").value;
  try{
    const r = await fetch(`${API}/empresas`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({razao_social, cnpj, usuario_id: usuarioId})});
    if(!r.ok){ msg("empresa-msg", "Erro ao salvar empresa.", false); return; }
    const data = await r.json();
    empresaId = data.id;
    msg("empresa-msg", "Empresa cadastrada!", true);
    mostrar("card-atividade");
  }catch(e){ msg("empresa-msg", "Erro: " + e.message, false); }
}

async function criarAtividade(){
  try{
    const setor = await (await fetch(`${API}/setores`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({empresa_id: empresaId, nome: document.getElementById("at-setor").value})})).json();
    setorId = setor.id;
    const funcao = await (await fetch(`${API}/funcoes`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({setor_id: setorId, cargo: document.getElementById("at-cargo").value})})).json();
    funcaoId = funcao.id;
    await fetch(`${API}/atividades`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({funcao_id: funcaoId, nome: document.getElementById("at-nome").value})});
    msg("atividade-msg", "Atividade adicionada!", true);
    mostrar("card-pgr");
  }catch(e){ msg("atividade-msg", "Erro: " + e.message, false); }
}

async function baixarPGR(){
  try{
    const r = await fetch(`${API}/empresas/${empresaId}/pgr`);
    if(!r.ok){ msg("pgr-msg", "Erro ao gerar PGR.", false); return; }
    const blob = await r.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "PGR.docx"; a.click();
    msg("pgr-msg", "PGR baixado com sucesso!", true);
  }catch(e){ msg("pgr-msg", "Erro: " + e.message, false); }
}
</script>
</body></html>
"""


@page_router.get("/nr1", response_class=HTMLResponse)
async def nr1_page():
    return _HTML
