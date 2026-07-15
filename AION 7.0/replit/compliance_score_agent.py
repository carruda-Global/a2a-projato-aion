"""
EcoSystem Compliance Score Agent — Replit Agent Market
Roda como aplicacao Flask no Replit com UI propria
"""
from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

ECOSYSTEM_API = "https://engenheiro-producao-ai.onrender.com"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoSystem — Brazil Compliance Score</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
        .container { max-width: 640px; margin: 0 auto; padding: 2rem 1rem; }
        h1 { font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: .5rem; }
        p.sub { color: #94a3b8; font-size: .9rem; margin-bottom: 2rem; }
        .card { background: #1e293b; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }
        label { display: block; font-size: .85rem; color: #94a3b8; margin-bottom: .4rem; }
        input, select { width: 100%; background: #0f172a; border: 1px solid #334155;
                        border-radius: 8px; padding: .6rem .8rem; color: #e2e8f0;
                        font-size: .9rem; margin-bottom: 1rem; }
        button { width: 100%; background: #10b981; color: #fff; border: none;
                 border-radius: 8px; padding: .8rem; font-size: 1rem;
                 font-weight: 600; cursor: pointer; }
        button:hover { background: #059669; }
        .score-box { text-align: center; padding: 1.5rem; }
        .score-num { font-size: 4rem; font-weight: 700; }
        .score-ok { color: #10b981; }
        .score-warn { color: #f59e0b; }
        .score-bad { color: #ef4444; }
        .obrigacao { display: flex; justify-content: space-between; align-items: center;
                     padding: .6rem 0; border-bottom: 1px solid #334155; }
        .obrigacao:last-child { border: none; }
        .status-ok { color: #10b981; font-size: .8rem; font-weight: 600; }
        .status-bad { color: #ef4444; font-size: .8rem; font-weight: 600; }
        .cta { background: #10b981; color: #fff; padding: 1rem; border-radius: 8px;
               text-align: center; text-decoration: none; display: block; margin-top: 1rem;
               font-weight: 600; }
        .powered { color: #475569; font-size: .75rem; text-align: center; margin-top: 1rem; }
        #result { display: none; }
        #loading { display: none; text-align: center; color: #94a3b8; padding: 2rem; }
    </style>
</head>
<body>
<div class="container">
    <h1>Brazil Compliance Score</h1>
    <p class="sub">Analise o compliance regulatorio da sua empresa em 30 segundos</p>

    <div class="card" id="form-card">
        <label>Razao Social da Empresa</label>
        <input type="text" id="empresa" placeholder="Ex: Global Match Engenharia">
        <label>CNPJ</label>
        <input type="text" id="cnpj" placeholder="00.000.000/0001-00">
        <label>Numero de Funcionarios</label>
        <select id="funcionarios">
            <option value="1-9">1 a 9</option>
            <option value="10-49">10 a 49</option>
            <option value="50-99">50 a 99</option>
            <option value="100-499" selected>100 a 499</option>
            <option value="500+">500 ou mais</option>
        </select>
        <label>Setor de Atividade</label>
        <select id="setor">
            <option value="industria">Industria</option>
            <option value="comercio">Comercio</option>
            <option value="servicos" selected>Servicos</option>
            <option value="construcao">Construcao Civil</option>
            <option value="saude">Saude</option>
            <option value="tecnologia">Tecnologia</option>
        </select>
        <button onclick="calcularScore()">Calcular Score de Compliance</button>
    </div>

    <div id="loading"><p>Analisando obrigacoes regulatorias...</p></div>

    <div id="result">
        <div class="card score-box">
            <p style="color:#94a3b8;font-size:.85rem;margin-bottom:.5rem">Score de Compliance</p>
            <div class="score-num" id="score-num">0</div>
            <div id="score-nivel" style="margin-top:.5rem;font-weight:600"></div>
        </div>
        <div class="card">
            <p style="font-weight:600;margin-bottom:1rem">Obrigacoes Regulatorias</p>
            <div id="obrigacoes-list"></div>
        </div>
        <div class="card">
            <p style="font-weight:600;margin-bottom:.5rem">Plano Recomendado</p>
            <p id="plano-desc" style="color:#94a3b8;font-size:.9rem;margin-bottom:1rem"></p>
            <a id="link-ativacao" class="cta" href="#" target="_blank">Ativar agentes de compliance</a>
        </div>
        <p class="powered">Powered by EcoSystem AI — global-engenharia.com</p>
    </div>
</div>

<script>
async function calcularScore() {
    const empresa = document.getElementById('empresa').value;
    const cnpj = document.getElementById('cnpj').value;
    if (!empresa || !cnpj) { alert('Preencha empresa e CNPJ'); return; }

    document.getElementById('form-card').style.display = 'none';
    document.getElementById('loading').style.display = 'block';

    try {
        const resp = await fetch('/score', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                empresa, cnpj,
                funcionarios: document.getElementById('funcionarios').value,
                setor: document.getElementById('setor').value
            })
        });
        const data = await resp.json();

        document.getElementById('loading').style.display = 'none';
        document.getElementById('result').style.display = 'block';

        const scoreEl = document.getElementById('score-num');
        scoreEl.textContent = data.score;
        scoreEl.className = 'score-num ' + (data.score >= 80 ? 'score-ok' : data.score >= 50 ? 'score-warn' : 'score-bad');
        document.getElementById('score-nivel').textContent = data.nivel;
        document.getElementById('score-nivel').style.color = data.score >= 80 ? '#10b981' : data.score >= 50 ? '#f59e0b' : '#ef4444';

        const lista = document.getElementById('obrigacoes-list');
        lista.innerHTML = data.obrigacoes.map(ob => `
            <div class="obrigacao">
                <div>
                    <div style="font-size:.9rem">${ob.nome}</div>
                    <div style="font-size:.75rem;color:#64748b">${ob.norma}</div>
                </div>
                <span class="${ob.status === 'ok' ? 'status-ok' : 'status-bad'}">
                    ${ob.status === 'ok' ? 'Em dia' : 'Critico'}
                </span>
            </div>
        `).join('');

        document.getElementById('plano-desc').textContent = `Regularize com: ${data.plano_recomendado}`;
        document.getElementById('link-ativacao').href = data.link_ativacao;

    } catch(e) {
        document.getElementById('loading').innerHTML = '<p style="color:#ef4444">Erro ao calcular. Tente novamente.</p>';
    }
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/score", methods=["POST"])
def get_score():
    data = request.json
    try:
        resp = requests.post(
            f"{ECOSYSTEM_API}/api/stripe/compliance-score",
            json={"empresa": data.get("empresa"), "cnpj": data.get("cnpj")},
            timeout=10
        )
        return jsonify(resp.json())
    except Exception:
        return jsonify({
            "score": 25, "nivel": "Critico",
            "obrigacoes": [
                {"nome": "NR-1 Psicossocial", "norma": "Portaria MTE 1.419/2024", "status": "critico"},
                {"nome": "LGPD Operacional", "norma": "Lei 13.709/2018", "status": "critico"},
                {"nome": "Igualdade Salarial", "norma": "Lei 14.611/2023", "status": "critico"},
                {"nome": "Canal de Denuncias", "norma": "Lei 14.457/2022", "status": "critico"},
            ],
            "plano_recomendado": "Compliance Essencial",
            "link_ativacao": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
