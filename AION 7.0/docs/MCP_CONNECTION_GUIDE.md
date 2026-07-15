# MCP Connection Guide — EcoSystem 3.0

## Server URLs (produção)

| Server | URL | Tools |
|--------|-----|-------|
| Regulatory | `https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse` | nr1_psicossocial, lgpd_operacional, tributario_cbs_ibs, canal_denuncias, igualdade_salarial, compliance_anticorrupcao, onboarding_funcionarios, conciliacao_financeira |
| ESG | `https://engenheiro-producao-ai.onrender.com/mcp/esg/sse` | esg_ifrs_diagnostico, inventario_carbono, escopo3_fornecedores, cbam_certificate |
| ERP | `https://engenheiro-producao-ai.onrender.com/mcp/erp/sse` | dynamics_sales, dynamics_finance, dynamics_hr, agentforce_sdr, agentforce_contracts, oracle_erp_compliance, oracle_hcm_regulatory, sap_compliance_bridge, sap_cbam_export, powerbi_compliance |

**Registry:** `https://engenheiro-producao-ai.onrender.com/mcp/servers`

---

## Microsoft Copilot Studio

Settings > Actions > Add MCP Server
- URL: `https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse`
- Auth: X-API-Key header
- Use ESG server para relatórios de carbono/ESG

## Salesforce Agentforce

Setup > Agentforce > MCP Servers > New
- URL: `https://engenheiro-producao-ai.onrender.com/mcp/esg/sse`
- Auth: Custom Header → X-API-Key
- Use ERP server para integração com Dynamics/Oracle/SAP

## Claude Desktop

```json
{
  "mcpServers": {
    "ecosystem-regulatory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sse"],
      "env": {
        "MCP_SERVER_URL": "https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse",
        "X-API-Key": "CHAVE_DO_CLIENTE"
      }
    },
    "ecosystem-esg": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sse"],
      "env": {
        "MCP_SERVER_URL": "https://engenheiro-producao-ai.onrender.com/mcp/esg/sse",
        "X-API-Key": "CHAVE_DO_CLIENTE"
      }
    },
    "ecosystem-erp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sse"],
      "env": {
        "MCP_SERVER_URL": "https://engenheiro-producao-ai.onrender.com/mcp/erp/sse",
        "X-API-Key": "CHAVE_DO_CLIENTE"
      }
    }
  }
}
```

## Google Gemini (via MCP)

Gemini > Settings > Tools > Add MCP Server
- URL: `https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse`
- Auth: API Key

## Billing

| Model | Price |
|-------|-------|
| Per tool call | R$ 0,50–2,00 por chamada |
| Free trial | 10 calls gratuitas |
| Subscription fallback | Conta como uso do plano ativo |

## Auth

All MCP endpoints use:
- Header: `X-API-Key: <chave_do_cliente>`
- Header: `X-Tenant-ID: <tenant_id>` (opcional para multi-tenancy)
