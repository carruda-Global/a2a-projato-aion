# MCP Submission Guide — EcoSystem 3.0

Este guia detalha como conectar os 3 MCP Servers do EcoSystem 3.0 às plataformas de agentes.

---

## 1. Microsoft Copilot Studio

### Pré-requisitos
- Licença Microsoft Copilot Studio
- Conta Microsoft Partner Center

### Conexão MCP
1. Acessar Copilot Studio → Settings → Actions
2. Clicar em "Add MCP Server"
3. Preencher:
   - **Name:** Ecosystem Regulatory
   - **URL:** `https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse`
   - **Auth:** API Key (header: `X-API-Key`)
4. Salvar — as tools aparecerão automaticamente

### Actions disponíveis no Copilot
| Tool | Descrição | Gatilho |
|------|-----------|---------|
| nr1_psicossocial | "Preciso do inventário NR-1" | Compliance |
| lgpd_operacional | "Mapear dados LGPD" | Compliance |
| canal_denuncias | "Registrar denúncia" | RH |
| igualdade_salarial | "Relatório de igualdade" | RH |
| onboarding_funcionarios | "Onboarding novo funcionário" | RH |
| conciliacao_financeira | "Conciliar extrato" | Financeiro |

### Pricing (via pay-per-use)
- Trial: 10 calls gratuitas
- Após trial: R$ 1,00/call ou assinatura mensal

---

## 2. Salesforce Agentforce

### Pré-requisitos
- Salesforce org com Agentforce licenciado
- Permissão "Setup MCP Servers"

### Conexão MCP
1. Setup → Agentforce → MCP Servers → New
2. Preencher:
   - **Name:** Ecosystem ESG & Carbon
   - **URL:** `https://engenheiro-producao-ai.onrender.com/mcp/esg/sse`
   - **Auth:** Custom Header → `X-API-Key`
3. Tools disponíveis: esg_ifrs_diagnostico, inventario_carbono, escopo3_fornecedores, cbam_certificate

### Salesforce + ERP Bridge
Para clientes Salesforce que também usam Oracle/SAP:
- Usar MCP ERP Server: `https://engenheiro-producao-ai.onrender.com/mcp/erp/sse`
- Tools: dynamics_sales, oracle_erp_compliance, sap_cbam_export

---

## 3. Claude Desktop (Anthropic)

### Configuração
Adicionar ao `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ecosystem-regulatory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sse"],
      "env": {
        "MCP_SERVER_URL": "https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse",
        "X-API-Key": "SUA_API_KEY"
      }
    },
    "ecosystem-esg": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sse"],
      "env": {
        "MCP_SERVER_URL": "https://engenheiro-producao-ai.onrender.com/mcp/esg/sse",
        "X-API-Key": "SUA_API_KEY"
      }
    },
    "ecosystem-erp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sse"],
      "env": {
        "MCP_SERVER_URL": "https://engenheiro-producao-ai.onrender.com/mcp/erp/sse",
        "X-API-Key": "SUA_API_KEY"
      }
    }
  }
}
```

---

## 4. Google Gemini

1. Acessar Google AI Studio → Settings → Tools
2. Add MCP Server
3. URL: `https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse`
4. Auth: API Key

---

## 5. MCP Registry (auto-discovery)

Endpoint: `https://engenheiro-producao-ai.onrender.com/mcp/servers`

```json
{
  "servers": {
    "regulatory": {
      "url": "https://.../mcp/regulatory/sse",
      "tools": ["nr1_psicossocial", "lgpd_operacional", "..."]
    },
    "esg": { "...": "..." },
    "erp": { "...": "..." }
  }
}
```

---

## Billing MCP

| Modelo | Preço |
|--------|-------|
| Per tool call | R$ 0,50–2,00 |
| Free trial | 10 calls |
| Fallback subscription | Conta como uso do plano Stripe |

### Tabelas Supabase

```sql
CREATE TABLE mcp_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    api_key TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE mcp_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    platform TEXT,
    called_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE mcp_cross_sell (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    triggered_by TEXT NOT NULL,
    recommended_agent TEXT NOT NULL,
    discount_pct INTEGER,
    converted_at TIMESTAMPTZ
);
```
