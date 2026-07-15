# AION / Global Match — Estado Real dos Agentes (levantamento 2026-07-03/04)

Este documento existe para dar handoff a qualquer sessão/agente que continue este trabalho.
Cada item foi **verificado no código e testado ao vivo em produção** (`engenheiro-producao-ai.onrender.com`),
não é suposição. Onde diz "confirmado", houve teste real via curl/API.

---

## 🟢 NÍVEL 1 — MVP real, completo, seguro para vender

Catálogo determinístico (quando aplicável) + banco/persistência + paywall (`tem_licenca_premium`).

| Produto | Onde | Observação |
|---|---|---|
| SOC 2 Readiness | `src/agents/soc2_agent.py` | AICPA TSC 2017, 13 Common Criteria |
| ISO 27001 Gap Analysis | `src/agents/iso27001_agent.py` | ISO/IEC 27001:2022 Annex A |
| EU AI Act Readiness | `src/agents/eu_ai_act_agent.py` | Art. 5 / Annex III / Art. 50 / obrigações Cap. III |
| Contract Risk | `src/agents/contract_risk_agent.py` | 15 tipos de cláusula |
| Vendor Risk | `src/agents/vendor_risk_agent.py` | 13 critérios (NIST/ISO 27036-2) |
| NR-1 Psychosocial | `app/modules/nr1/` | Fluxo completo empresa→setor→PGR.docx, testado ponta a ponta |
| Procurement | `app/modules/procurement_copilot/` | Banco próprio, já estava OK antes desta sessão |
| Engineering Copilot | `app/modules/engineering_copilot/` | Projeto→documento→foto→compliance→9 documentos DOCX (incl. **As Built**, adicionado nesta sessão) |
| Engineering Suite | `app/routers/engineering_suite.py` | Spec Analyst, Requirements Analyst, BIM Coordinator, Field Execution, Logistics, Inventory, RFI Creation, Work Synopsis, Engineering Assistant, Photo Intelligence — **unificados nesta sessão** com o banco/paywall do Engineering Copilot |
| Regulatory Analyst | `app/routers/enterprise_ops.py` | Paywall aplicado e confirmado em produção nesta sessão |
| Compliance PM | `app/routers/enterprise_ops.py` | Paywall aplicado e confirmado em produção nesta sessão |
| MAI Code Reviewer | `app/routers/code_review.py` | Paywall aplicado — endpoint `/review` retorna 402 sem assinatura, confirmado em produção. Webhook `/github/webhook` continua sem gate (ver limitação abaixo) |
| CSRD Double Materiality | `src/agents/csrd_reporting_agent.py` | **Reescrito nesta sessão**: catálogo real ESRS Set 1 (11 tópicos, Regulamento Delegado (UE) 2023/2772), dupla materialidade determinística, paywall. Confirmado em produção |
| Whistleblower Channel | `src/agents/whistleblower_agent.py` | **Reescrito nesta sessão**: catálogo real Art. 2 da Diretiva (UE) 2019/1937 (12 categorias), severidade determinística por categoria + fatores agravantes, prazos estatutários calculados em código, paywall. Confirmado em produção. **Também movido no site** de "Brazil Regulatory Copilot" para "Global Compliance Copilot" (é lei europeia, não brasileira) — Global Compliance agora tem 6 especialistas, Brazil Regulatory ficou com 4 |
| Carbon Inventory | `app/routers/carbon_inventory.py` | **Construído do zero nesta sessão**: catálogo real GHG Protocol Escopo 1+2 (7 fontes), score de completude do inventário, paywall. Confirmado em produção |
| Scope 3 Suppliers | `app/routers/scope3_suppliers.py` | **Construído do zero nesta sessão**: catálogo real GHG Protocol Escopo 3 (15 categorias) + exposição CBAM, score de maturidade de rastreamento, paywall. Confirmado em produção |
| CBS/IBS Tax | `app/routers/cbs_ibs_tax.py` | **Construído do zero nesta sessão**: checklist real de prontidão pra reforma tributária (EC 132/2023, LC 214/2025, 7 itens), score determinístico, paywall. Confirmado em produção |
| Pay Equity | `app/routers/pay_equity.py` | **Construído do zero nesta sessão**: catálogo real da Lei 14.611/2023 + Decreto 11.795/2023 (5 obrigações), threshold de 100+ funcionários aplicado em código (não é LLM que decide), paywall. Confirmado em produção |
| Anti-Corruption | `app/routers/anti_corruption.py` | **Construído do zero nesta sessão**: catálogo real dos 10 pilares de integridade do Decreto 11.129/2022 (alinhado à ISO 37001), score de maturidade, paywall. Confirmado em produção |

---

## 🟡 NÍVEL 2 — Endpoint real, funciona, mas SEM controle de assinatura

### AINDA PRECISA DE GATE (vazamento de receita ativo — qualquer um usa de graça)
| Produto | Arquivo | Vendido no site? |
|---|---|---|
| DORA | `src/agents/dora_compliance_agent.py` | Não vendido, mas endpoint público |
| NIS2 | `src/agents/nis2_agent.py` | Não vendido, mas endpoint público |
| Regulatory Monitor | `src/agents/regulatory_monitor_agent.py` | Não vendido |
| Board Reporting | `src/agents/board_reporting_agent.py` | Não vendido |
| M&A Due Diligence | `src/agents/ma_due_diligence_agent.py` | Não vendido |

**Ação recomendada**: mesmo tratamento aplicado a CSRD/Whistleblower — catálogo real + `tem_licenca_premium`. Nenhum dos 5 é vendido no site hoje, então não é vazamento de receita ativo (ninguém paga por eles), mas ficam prontos pra vender assim que tiverem o mesmo rigor.

### Limitação conhecida, não resolvida
- `POST /api/code-review/github/webhook` — endpoint automático de CI, não tem "e-mail do cliente" natural no payload do GitHub. Precisa de um mapeamento `tenant_id` → assinatura pra ser gateado corretamente. Não implementado.

---

## 🔴 NÍVEL 3 — Sem backend real nenhum (só resposta solta via orquestrador interno)

### Já retirados do site nesta sessão
- ~~Platform Core & Orchestration~~ (Master Orchestrator, Quality Critic, Regulatory Watch, Universal Governance, Power BI Compliance) — vertical inteira removida
- ~~Workforce Orchestrator~~, ~~AntiGravity Bridge~~ — removidos do Tech Copilot
- ~~Sales Agent~~ — removido (não é produto, é o chat de pré-venda do próprio site)
- ~~Physical AI Connector~~ — removido (endpoints de consulta retornam vazio/zero hardcoded, sem entrega real)
- ~~Software Engineering~~ — removido (sem endpoint próprio, linkava pro checkout genérico do Full Suite)

Os 5 itens que faltavam backend (Carbon Inventory, Scope 3, CBS/IBS Tax, Pay Equity, Anti-Corruption)
foram **construídos e promovidos pro Nível 1** nesta sessão — ver tabela acima. Nível 3 agora só
tem o que foi removido do site, nada pendente de decisão.

---

## Outros bugs corrigidos nesta sessão (não relacionados a agentes, mas achados durante o teste de compra)

- Bug crítico: duplo prompt de e-mail no checkout (modal + `window.prompt()` nativo concorrendo) — removido o duplicado
- Webhook de captura de lead apontava pra domínio morto (`aion-linkedin-agent.onrender.com`, 404 em tudo) — corrigido pro endpoint real (`/checkout/lead`)
- 2 de 4 botões "pay-per-use" chamavam `agent_id` que não existe no backend (`soc2_readiness`, `nr1_diagnostico`) — corrigidos
- Rodapé "Privacy Policy"/"Terms of Use" eram links mortos (`#`) — corrigidos para as páginas reais que já existiam
- CCPA/CPRA (lei de privacidade dos EUA) estava totalmente ausente do site voltado pro público americano — adicionado com número real (CPPA, 2025/2026)
- Card de privacidade só citava LGPD, ignorando GDPR/CCPA — corrigido

---

## Veredito final

**Sim — todo produto vendido no site hoje tem backend real, catálogo (quando aplicável) e paywall
confirmado em produção.** Os únicos itens sem esse rigor (DORA, NIS2, Regulatory Monitor, Board
Reporting, M&A Due Diligence) **não são vendidos no site** — existem só como endpoint interno, sem
vitrine, então não representam vazamento de receita nem promessa quebrada pro cliente.

## Próximo passo sugerido (não urgente, nada bloqueando venda)
1. Aplicar catálogo real + paywall nos 5 agentes do Nível 2 (DORA, NIS2, Regulatory Monitor, Board Reporting, M&A Due Diligence) só quando/se decidir vendê-los — mesmo padrão mecânico já usado 6x nesta sessão
2. Resolver o gate do webhook do GitHub (MAI Code Reviewer) — precisa de mapeamento tenant_id → assinatura
3. Migração Hostinger (DNS já parcialmente configurado, nameservers ainda não trocados — ver memória de sessões anteriores)
