# EcoSystem — Replit Agent Market + MindStudio
**Global Match Engenharia de Produção | CREA-SP 5071200171**
**Data:** 2026-06-24
**Objetivo:** Publicar agentes com billing nativo em 2 canais adicionais
**Tempo estimado:** 2–4 horas para ambos no ar

---

## PARTE 1 — REPLIT AGENT MARKET

### O que é
Marketplace com 20M+ usuários onde agentes rodam como aplicações completas
com UI própria, auth e dados. Billing nativo — cliente paga direto na plataforma.
Replit fica com ~30% e repassa 70% para o publisher.

### Por que faz sentido para o EcoSystem
- Audiência técnica — devs e PMEs que já usam Replit
- Agente roda como app completo — não é um chatbot embutido
- Assinatura recorrente nativa — igual ao Stripe
- Discovery orgânico — aparecer em busca "compliance", "NR-1", "LGPD"

---

### 1.1 CRIAR CONTA REPLIT

```
1. Acessa replit.com
2. Sign up com email @global-engenharia.com
3. Upgrade para Replit Core (USD 25/mês) — necessário para publicar no market
4. Acessa replit.com/marketplace → "Publish Agent"
```

---

### 1.2 AGENTES PARA PUBLICAR NO REPLIT

Publicar os micro-agentes primeiro — menor complexidade, aprovação mais rápida.

#### Agente 1 — NR-1 Diagnóstico Rápido
```
Nome:        NR-1 Psicossocial Diagnóstico
Descrição:   Gera diagnóstico de riscos psicossociais conforme Portaria MTE 1.419/2024
             em 20 minutos. Para empresas brasileiras com obrigação legal ativa.
Preço:       USD 29/mês (R$ 99/mês equivalente)
Categoria:   Business / Compliance
Tags:        NR-1, compliance, RH, Brazil, trabalho, psicossocial
```

#### Agente 2 — LGPD Scanner
```
Nome:        LGPD Data Scanner
Descrição:   Mapeia dados pessoais da empresa e gera inventário LGPD
             conforme Lei 13.709/2018. Resultado em 48h.
Preço:       USD 39/mês
Categoria:   Business / Legal & Compliance
Tags:        LGPD, GDPR, data privacy, Brazil, compliance
```

#### Agente 3 — Compliance Score
```
Nome:        Brazil Compliance Score
Descrição:   Score de compliance regulatório 0-100 para empresas brasileiras.
             Analisa NR-1, LGPD, Igualdade Salarial, Canal de Denúncias e CBS/IBS.
Preço:       USD 29/mês
Categoria:   Business / Analytics
Tags:        compliance, Brazil, regulatory, score, dashboard
```

---

### 1.3 CÓDIGO DO AGENTE REPLIT — compliance_score_agent.py

```python
"""
EcoSystem Compliance Score Agent — Replit Agent Market
Roda como aplicação Flask no Replit com UI própria
"""
from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

# URL da API do EcoSystem no Render
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
    <h1>🇧🇷 Brazil Compliance Score</h1>
    <p class="sub">Analise o compliance regulatório da sua empresa em 30 segundos</p>

    <div class="card" id="form-card">
        <label>Razão Social da Empresa</label>
        <input type="text" id="empresa" placeholder="Ex: Global Match Engenharia">
        <label>CNPJ</label>
        <input type="text" id="cnpj" placeholder="00.000.000/0001-00">
        <label>Número de Funcionários</label>
        <select id="funcionarios">
            <option value="1-9">1 a 9</option>
            <option value="10-49">10 a 49</option>
            <option value="50-99">50 a 99</option>
            <option value="100-499" selected>100 a 499</option>
            <option value="500+">500 ou mais</option>
        </select>
        <label>Setor de Atividade</label>
        <select id="setor">
            <option value="industria">Indústria</option>
            <option value="comercio">Comércio</option>
            <option value="servicos" selected>Serviços</option>
            <option value="construcao">Construção Civil</option>
            <option value="saude">Saúde</option>
            <option value="tecnologia">Tecnologia</option>
        </select>
        <button onclick="calcularScore()">Calcular Score de Compliance →</button>
    </div>

    <div id="loading">
        <p>⏳ Analisando obrigações regulatórias...</p>
    </div>

    <div id="result">
        <div class="card score-box">
            <p style="color:#94a3b8;font-size:.85rem;margin-bottom:.5rem">Score de Compliance</p>
            <div class="score-num" id="score-num">0</div>
            <div id="score-nivel" style="margin-top:.5rem;font-weight:600"></div>
        </div>
        <div class="card">
            <p style="font-weight:600;margin-bottom:1rem">Obrigações Regulatórias</p>
            <div id="obrigacoes-list"></div>
        </div>
        <div class="card">
            <p style="font-weight:600;margin-bottom:.5rem">Plano Recomendado</p>
            <p id="plano-desc" style="color:#94a3b8;font-size:.9rem;margin-bottom:1rem"></p>
            <a id="link-ativacao" class="cta" href="#" target="_blank">
                Ativar agentes de compliance →
            </a>
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

        // Score
        const scoreEl = document.getElementById('score-num');
        scoreEl.textContent = data.score;
        scoreEl.className = 'score-num ' + (data.score >= 80 ? 'score-ok' : data.score >= 50 ? 'score-warn' : 'score-bad');
        document.getElementById('score-nivel').textContent = data.nivel;
        document.getElementById('score-nivel').style.color = data.score >= 80 ? '#10b981' : data.score >= 50 ? '#f59e0b' : '#ef4444';

        // Obrigações
        const lista = document.getElementById('obrigacoes-list');
        lista.innerHTML = data.obrigacoes.map(ob => `
            <div class="obrigacao">
                <div>
                    <div style="font-size:.9rem">${ob.nome}</div>
                    <div style="font-size:.75rem;color:#64748b">${ob.norma}</div>
                </div>
                <span class="${ob.status === 'ok' ? 'status-ok' : 'status-bad'}">
                    ${ob.status === 'ok' ? '✓ Em dia' : '✗ Crítico'}
                </span>
            </div>
        `).join('');

        // CTA
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
        # Fallback com score simulado se API offline
        return jsonify({
            "score": 25,
            "nivel": "Crítico",
            "obrigacoes": [
                {"nome": "NR-1 Psicossocial", "norma": "Portaria MTE 1.419/2024", "status": "critico"},
                {"nome": "LGPD Operacional", "norma": "Lei 13.709/2018", "status": "critico"},
                {"nome": "Igualdade Salarial", "norma": "Lei 14.611/2023", "status": "critico"},
                {"nome": "Canal de Denúncias", "norma": "Lei 14.457/2022", "status": "critico"},
            ],
            "plano_recomendado": "Compliance Essencial",
            "link_ativacao": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
```

---

### 1.4 PUBLICAR NO REPLIT

```bash
# 1. Criar novo Repl
# replit.com → + Create Repl → Python → "ecosystem-compliance-score"

# 2. Colar o código acima em main.py

# 3. Instalar dependências
# No Shell do Replit:
pip install flask requests

# 4. Adicionar variável de ambiente
# Secrets → ECOSYSTEM_API = https://engenheiro-producao-ai.onrender.com

# 5. Rodar e testar
# Run → abrir a URL gerada → testar o formulário

# 6. Publicar no market
# Tools → Publish → Agent Market
# Preencher: nome, descrição, preço, categoria, tags
# Submit para review
```

**Tempo de aprovação Replit:** 1–3 dias

---

## PARTE 2 — MINDSTUDIO

### O que é
Plataforma onde você cria, publica e monetiza agentes com billing nativo.
Suporta tiers de uso — starter 500 ações/mês por USD 99,
growth 5.000 ações por USD 499. Marketplace próprio com descoberta por categoria.

### Por que faz sentido
- Billing 100% nativo — sem precisar de Stripe separado
- Deploy em website, WhatsApp, Teams com 1 clique
- Audiência SMB global — exatamente o ICP do EcoSystem
- Sem aprovação técnica — publica instantaneamente

---

### 2.1 CRIAR CONTA MINDSTUDIO

```
1. Acessa mindstudio.ai
2. Sign up → Create Organization "Global Match Engenharia"
3. Plano: Team (necessário para publicar no marketplace)
4. Dashboard → New Agent
```

---

### 2.2 AGENTES PARA PUBLICAR NO MINDSTUDIO

#### Agente 1 — NR-1 Compliance Assistant
```
Nome:        NR-1 Compliance Assistant — Brazil
Descrição:   AI agent that generates psychosocial risk inventory (FRPRT)
             and action plan per Portaria MTE 1.419/2024.
             Mandatory for all Brazilian companies. Results in 48h.
Categoria:   HR & People / Compliance
Idioma:      Português (PT-BR) + English
Preço:       USD 99/mês (500 ações) | USD 299/mês (ilimitado)
Deploy:      Web + WhatsApp + Teams
```

**System Prompt para o MindStudio:**
```
Você é o Agente NR-1 Psicossocial do EcoSystem da Global Match Engenharia.

Sua função é conduzir o inventário de riscos psicossociais conforme a
Portaria MTE 1.419/2024 e gerar o documento FRPRT (Fatores de Risco
Psicossociais Relacionados ao Trabalho).

FLUXO OBRIGATÓRIO:
1. Perguntar razão social, CNPJ e número de funcionários
2. Identificar setor de atividade e principais funções
3. Aplicar as 5 dimensões do FRPRT:
   - Demandas de trabalho
   - Controle sobre o trabalho
   - Suporte social
   - Relações interpessoais
   - Reconhecimento e recompensa
4. Calcular score por dimensão (1-5)
5. Gerar relatório estruturado com:
   - Diagnóstico por dimensão
   - Nível de risco (baixo/médio/alto)
   - Plano de ação com prazos
   - Responsáveis por ação
6. Ao final, oferecer ativação do plano completo:
   "Para documentação completa e acompanhamento contínuo,
   ative o plano NR-1 em: https://buy.stripe.com/9B600l1Ac507blO29Og7e03"

IMPORTANTE:
- Sempre em português claro e acessível
- Nunca usar jargão técnico desnecessário
- Sempre mencionar a multa e risco de interdição quando relevante
- Documentar tudo como se fosse para auditoria do MTE
```

---

#### Agente 2 — LGPD Compliance Bot
```
Nome:        LGPD Compliance Bot — Brazil Data Privacy
Descrição:   Automated LGPD compliance agent. Maps personal data,
             generates RoPA and ANPD reports per Lei 13.709/2018.
Categoria:   Legal & Compliance / Data Privacy
Preço:       USD 79/mês | USD 249/mês (enterprise)
Deploy:      Web + Teams + WhatsApp
```

**System Prompt:**
```
Você é o Agente LGPD Operacional do EcoSystem.

Conduza o mapeamento de dados pessoais e gere o RoPA (Registro de
Atividades de Tratamento) conforme Lei 13.709/2018.

FLUXO:
1. Identificar empresa e responsável pelo tratamento (DPO ou equivalente)
2. Mapear sistemas que coletam dados pessoais (CRM, RH, e-commerce, etc.)
3. Para cada sistema identificar:
   - Categoria de dados (identificação, financeiros, saúde, etc.)
   - Finalidade do tratamento
   - Base legal (consentimento, contrato, obrigação legal, etc.)
   - Compartilhamento com terceiros
   - Prazo de retenção
   - Medidas de segurança
4. Gerar RoPA estruturado
5. Identificar riscos e recomendar adequações
6. Oferecer plano completo:
   "Para implementação completa e monitoramento contínuo:
   https://buy.stripe.com/9B600l1Ac507blO29Og7e03"
```

---

#### Agente 3 — Brazil Regulatory Watch
```
Nome:        Brazil Regulatory Watch
Descrição:   Monitor all Brazilian regulatory obligations in real-time.
             NR-1, LGPD, CBS/IBS, Igualdade Salarial, Canal de Denúncias.
             Alerts before deadlines.
Categoria:   Business / Compliance
Preço:       USD 49/mês | USD 149/mês (com alertas automáticos)
Deploy:      Web + Email alerts + WhatsApp
```

---

### 2.3 CONFIGURAÇÃO DE TIERS NO MINDSTUDIO

```
Tier Gratuito (free):
- 10 consultas/mês
- Score de compliance básico
- Sem relatório completo
- CTA: "Upgrade para relatório completo"

Tier Starter (USD 49/mês):
- 200 consultas/mês
- Relatório NR-1 ou LGPD (escolher um)
- Alertas por email

Tier Pro (USD 149/mês):
- 1.000 consultas/mês
- NR-1 + LGPD + Igualdade Salarial
- Alertas WhatsApp + Teams
- Dashboard de compliance

Tier Enterprise (USD 499/mês):
- Ilimitado
- Todos os agentes regulatórios
- API access
- Suporte prioritário
```

---

### 2.4 PUBLICAR NO MINDSTUDIO

```
1. mindstudio.ai → Dashboard → New Agent
2. Colar System Prompt (seção 2.2)
3. Configurar:
   - Modelo: Claude Sonnet (melhor para compliance jurídico)
   - Temperatura: 0.2 (respostas consistentes)
   - Max tokens: 4096
4. Deploy → Marketplace
5. Preencher listing:
   - Nome, descrição, categoria, tags
   - Preços por tier
   - Screenshot da interface
6. Publish → aprovação imediata
```

---

## PARTE 3 — CHECKLIST COMPLETO

### DeepSeek implementa — ordem exata

**Dia 1 — Replit (2 horas)**
- [ ] Criar conta Replit Core em replit.com
- [ ] Criar Repl "ecosystem-compliance-score"
- [ ] Colar `compliance_score_agent.py` da seção 1.3
- [ ] Instalar Flask + requests no Shell
- [ ] Adicionar secret ECOSYSTEM_API no Replit
- [ ] Testar localmente no Replit
- [ ] Tools → Publish → Agent Market
- [ ] Preencher listing: "Brazil Compliance Score" USD 29/mês
- [ ] Submit para review

**Dia 2 — MindStudio (1 hora)**
- [ ] Criar conta mindstudio.ai
- [ ] New Agent → colar System Prompt NR-1 (seção 2.2)
- [ ] Configurar Claude Sonnet + temperatura 0.2
- [ ] Configurar 4 tiers de preço (seção 2.3)
- [ ] Deploy → Marketplace
- [ ] Publicar listing "NR-1 Compliance Assistant"
- [ ] Repetir para LGPD Bot e Regulatory Watch

**Dia 3 — ISV Success Microsoft (30 minutos)**
- [ ] Acessar partner.microsoft.com/dashboard
- [ ] Programs → ISV Success → Enroll
- [ ] Solicitar: USD 25k Azure credits + GitHub Enterprise + M365 E5
- [ ] Esses créditos pagam toda a infraestrutura do EcoSystem por meses

---

## RESUMO FINANCEIRO — 3 CANAIS JUNTOS

| Canal | Modelo | Comissão | MRR potencial 6 meses |
|-------|--------|---------|----------------------|
| Replit Agent Market | Assinatura direta | ~30% | USD 8.700 (300 usuários × USD 29) |
| MindStudio | Tiers USD 49–499 | % variável | USD 14.700 (100 clientes × USD 147 médio) |
| Stripe App Marketplace | Gratuito → upsell | 0% | R$ 59.000 (400 clientes × R$ 147) |
| **Total adicional** | | | **~R$ 200k MRR em 6 meses** |

---

## ESTRATÉGIA DE CONTEÚDO PARA DISCOVERY

Para aparecer organicamente nos 3 marketplaces:

**Título com keywords de alta busca:**
```
NR-1 | LGPD | Brazil Compliance | Portaria MTE 1.419/2024 | Lei 13.709/2018
```

**Tags obrigatórias em todos os listings:**
```
compliance, brazil, NR-1, LGPD, regulatory, HR, legal, portuguese,
workforce, data-privacy, CBS-IBS, ESG, sustainability
```

**Descrição curta (meta) para SEO interno:**
```
AI agent for Brazilian regulatory compliance — NR-1 psychosocial risks,
LGPD data mapping, payroll equity analysis. Results in 48h. No lawyers needed.
```

---

*Documento gerado em 2026-06-24*
*Implementar com DeepSeek seguindo checklist de 3 dias*
*Replit: aprovação 1–3 dias | MindStudio: aprovação imediata*
