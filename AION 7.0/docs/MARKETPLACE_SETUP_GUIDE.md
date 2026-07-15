# Marketplace Setup Guide — EcoSystem 3.0

## SAP Store (BTP)

### Pré-requisitos
- Conta no SAP BTP Partner Center: https://partnercenter.sap.com
- Subaccount BTP com Cloud Foundry habilitado
- SAP BTP EA (Enterprise Agreement) ativo

### Produtos a publicar
| Produto | Preço | ID Stripe |
|---------|-------|-----------|
| SAP Compliance Bridge | R$ 1.490/mês | `sap_compliance_bridge` |
| SAP Predictive Maintenance | R$ 1.290/mês | `sap_predictive_maintenance` |
| SAP CBAM Export | R$ 1.990/mês | `sap_cbam_export` |
| SAP Integration Pack (3) | R$ 4.290/mês | `sap_pack` |

### Passos
1. Acessar SAP Store > Become a Partner
2. Completar perfil ISV com dados da Global Match Engenharia (CREA-SP 5071200171)
3. Criar aplicação BTP: `ecosystem-sap-bridge`
4. Registrar API endpoints no SAP API Business Hub
5. Submeter para validação SAP (security review)
6. Publicar no SAP Store

### Endpoints
- MCP: `https://engenheiro-producao-ai.onrender.com/mcp/erp/sse`
- Auth: X-API-Key header

---

## Oracle Agent Marketplace

### Pré-requisitos
- Conta Oracle Partner: https://partner.oracle.com
- Conta OCI (Oracle Cloud Infrastructure)
- Oracle Agent Studio ativo

### Produtos a publicar
| Produto | Preço | ID Stripe |
|---------|-------|-----------|
| Oracle ERP Compliance | R$ 1.190/mês | `oracle_erp_compliance` |
| Oracle HCM Regulatory | R$ 990/mês | `oracle_hcm_regulatory` |
| Oracle Supply Chain ESG | R$ 1.490/mês | `oracle_supply_chain_esg` |
| Oracle CX Sales | R$ 890/mês | `oracle_cx_sales` |
| Oracle Fusion Pack (4) | R$ 3.990/mês | `oracle_pack` |

### Passos
1. Registrar como ISV no Oracle Partner Network
2. Solicitar acesso ao Oracle Cloud Marketplace Publisher Portal
3. Criar listing para cada agente como "Agent" (tipo SaaS)
4. Configurar fulfillment via OCI Agent Studio
5. Vincular pricing via Stripe ou Oracle Monetization Cloud

### Endpoints
- MCP: `https://engenheiro-producao-ai.onrender.com/mcp/erp/sse`
- Auth: Oracle Cloud IAM + X-API-Key

---

## Microsoft Copilot Studio

### Produto de entrada
Compliance Essencial (NR-1 + LGPD) — R$ 590/mês

### Configuração
Ver `docs/MCP_CONNECTION_GUIDE.md`

### Checklist
- [ ] Publicar oferta transacionável no Microsoft Marketplace
- [ ] Associar MCP connector ao listing
- [ ] Configurar co-sell com MSPs
- [ ] Submeter para logo "Certified Software"

---

## Salesforce AgentExchange

### Produto de entrada
Compliance Essencial (NR-1 + LGPD) — R$ 590/mês

### Configuração
Ver `docs/MCP_CONNECTION_GUIDE.md`

### Checklist
- [ ] Managed package registrado no Partner Portal
- [ ] Security review submetido
- [ ] MCP connector vinculado ao listing
- [ ] Preços configurados em USD para mercado global

---

## Stripe — Price IDs

### Script de criação
```bash
cd Ecosystem 2.0
$env:STRIPE_SECRET_KEY='sk_test_...'
python scripts/create_stripe_products_v3.py
```

### Planos que precisam de price_id
| Plano | Status |
|-------|--------|
| Dynamics Pack | ❌ Criar |
| Agentforce Pack | ❌ Criar |
| Oracle Pack | ❌ Criar |
| SAP Pack | ❌ Criar |
| ERP Full Bridge | ❌ Criar |
| Full Suite 56 | ❌ Criar |
| Onboarding | ❌ Criar |
| Atendimento Plus | ❌ Criar |
| Conciliacao Pro | ❌ Criar |

---
