from pathlib import Path
from weasyprint import HTML

OUTPUT = Path(__file__).parent.parent / "arquitetura_produto.pdf"

html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @page { margin: 2cm; }
  body { font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a1a; font-size: 11pt; line-height: 1.5; }
  h1 { color: #0078d4; font-size: 20pt; border-bottom: 2px solid #0078d4; padding-bottom: 8px; }
  h2 { color: #005a9e; font-size: 14pt; margin-top: 20px; }
  h3 { font-size: 12pt; margin-top: 15px; }
  p { margin: 6px 0; }
  .section { margin-bottom: 20px; }
  table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 10pt; }
  th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; }
  th { background: #0078d4; color: #fff; }
  .diagram { background: #f5f5f5; padding: 12px; font-family: 'Consolas', monospace; font-size: 9pt; white-space: pre; line-height: 1.3; border-radius: 4px; margin: 10px 0; }
  .url { color: #0078d4; font-family: 'Consolas', monospace; font-size: 9pt; word-break: break-all; }
</style>
</head>
<body>

<h1>EcoSystem AEC + Regulatory</h1>
<p><strong>Produto:</strong> Plataforma SaaS Multiagente de IA para Compliance Regulatório</p>
<p><strong>Empresa:</strong> Global Match Engenharia de Produção</p>
<p><strong>Versão:</strong> 3.0.0</p>

<div class="section">
<h2>1. Descrição do Produto</h2>
<p>Plataforma SaaS composta por mais de 50 agentes de IA generativa especializados em obrigações regulatórias brasileiras, processos de engenharia/construção (AEC), relatórios ESG, e integração com sistemas ERP (Dynamics 365, Salesforce, Oracle Fusion, SAP).</p>
<p>Os agentes operam de forma hierárquica e colaborativa utilizando o protocolo A2A (Agent-to-Agent) da Google e MCP (Model Context Protocol) da Anthropic, permitindo orquestração inteligente de tarefas complexas.</p>
</div>

<div class="section">
<h2>2. Arquitetura do Sistema</h2>
<h3>2.1 Diagrama de Camadas</h3>
<div class="diagram">
CAMADA 4 — AUTO-APRIMORAMENTO (Meta-Learning, Evolution, Federated Knowledge)
CAMADA 3 — INTELIGÊNCIA (Regulatory Watch, Client Intel, Quality Critic)
CAMADA 2 — COORDENAÇÃO (Master Orchestrator, Cross-Platform Bridge)
CAMADA 1 — AGENTES ESPECIALIZADOS (48 agentes)
  ├── AEC (#1-#12) - Engenharia e Construção
  ├── Regulatório (#13-#21) - NR-1, LGPD, ESG, Tributário
  ├── Microsoft (#22-#27) - M365, Teams, SharePoint
  ├── Dynamics 365 (#31-#36) - Sales, Finance, HR, SCM
  ├── Salesforce Agentforce (#37-#41) - SDR, Field Service, Contracts
  ├── Oracle Fusion (#42-#45) - ERP, HCM, SCM, CX
  └── SAP (#46-#48) - S/4HANA, GTS, PM
CAMADA 0 — MCP SERVERS + PROTOCOLO A2A
</div>

<h3>2.2 Infraestrutura de Hospedagem</h3>
<table>
  <tr><th>Componente</th><th>Tecnologia</th><th>Localização</th></tr>
  <tr><td>API Backend</td><td>FastAPI + Uvicorn (Python 3.12)</td><td>Render.com (US)</td></tr>
  <tr><td>Frontend (Dashboard)</td><td>React + Vite</td><td>Vercel</td></tr>
  <tr><td>Banco de Dados</td><td>PostgreSQL / TimescaleDB</td><td>Render.com + Supabase</td></tr>
  <tr><td>Banco Vetorial</td><td>ChromaDB + Pinecone</td><td>Render.com + Cloud</td></tr>
  <tr><td>Cache / Mensageria</td><td>Redis Streams</td><td>Render.com</td></tr>
  <tr><td>Armazenamento</td><td>MinIO (S3-compatible)</td><td>Render.com</td></tr>
  <tr><td>Monitoramento</td><td>Prometheus + Grafana + Loki</td><td>Render.com</td></tr>
  <tr><td>Secrets</td><td>HashiCorp Vault</td><td>Render.com</td></tr>
</table>

<h3>2.3 Modelos de IA Utilizados</h3>
<table>
  <tr><th>Provedor</th><th>Modelo</th><th>Uso</th><th>Localização</th></tr>
  <tr><td>DeepSeek</td><td>DeepSeek-V4-Flash</td><td>LLM operacional principal (agentes AEC, ESG, ERP)</td><td>API Externa (OpenAI-compatible)</td></tr>
  <tr><td>Google Gemini</td><td>Gemini (southamerica-east1)</td><td>Dados sensíveis LGPD, NR-1, RH</td><td>Google Cloud (southamerica-east1)</td></tr>
  <tr><td>Anthropic Claude</td><td>Claude API</td><td>Raciocínio complexo, orquestração, revisão crítica</td><td>API Externa</td></tr>
</table>

<h3>2.4 Fluxo de Funcionamento</h3>
<p><strong>Cliente → Dashboard Web → FastAPI → Orquestrador → Agente Especializado → LLM → Resultado</strong></p>
<ol>
  <li>Cliente acessa o dashboard web (Vercel) e seleciona um agente ou descreve um objetivo</li>
  <li>Requisição é enviada à API (FastAPI em Render.com)</li>
  <li>Orquestrador (Master Orchestrator) analisa o objetivo e delega para o(s) agente(s) especializado(s)</li>
  <li>Cada agente consulta o LLM apropriado (DeepSeek, Gemini ou Claude) com contexto do banco vetorial (RAG)</li>
  <li>Quality Critic revisa o output antes de entregar ao cliente</li>
  <li>Resultado é armazenado e apresentado no dashboard</li>
</ol>
</div>

<div class="section">
<h2>3. Endpoints de Integração com Microsoft Azure</h2>
<table>
  <tr><th>Endpoint</th><th>Função</th></tr>
  <tr><td class="url">https://engenheiro-producao-ai.onrender.com/microsoft/subscribe</td><td>Landing page para assinatura via Azure Marketplace</td></tr>
  <tr><td class="url">https://engenheiro-producao-ai.onrender.com/microsoft/webhook</td><td>Webhook para eventos de assinatura (subscribe, unsubscribe, change plan)</td></tr>
  <tr><td class="url">https://engenheiro-producao-ai.onrender.com/microsoft/fulfill</td><td>Ativação de assinatura após compra</td></tr>
  <tr><td class="url">https://engenheiro-producao-ai.onrender.com/api/leads/microsoft</td><td>Recebimento de leads do Microsoft Marketplace</td></tr>
  <tr><td class="url">https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse</td><td>MCP Server Regulatory (SSE)</td></tr>
  <tr><td class="url">https://engenheiro-producao-ai.onrender.com/mcp/esg/sse</td><td>MCP Server ESG (SSE)</td></tr>
</table>
</div>

<div class="section">
<h2>4. Segurança e Conformidade</h2>
<ul>
  <li><strong>Criptografia:</strong> Todas as comunicações via HTTPS/TLS 1.2+</li>
  <li><strong>Autenticação:</strong> JWT + API Keys para MCP servers</li>
  <li><strong>LGPD:</strong> Dados sensíveis (NR-1, LGPD, RH) roteados exclusivamente via Google Gemini em região Brasil (southamerica-east1)</li>
  <li><strong>RBAC:</strong> Controle de acesso baseado em papéis por tenant</li>
  <li><strong>Auditoria:</strong> Todos os acessos e execuções são registrados com audit trail</li>
  <li><strong>Secrets:</strong> Gerenciados via HashiCorp Vault</li>
</ul>
</div>

</body>
</html>
"""

HTML(string=html_content).write_pdf(OUTPUT)
print(f"PDF gerado: {OUTPUT}")
