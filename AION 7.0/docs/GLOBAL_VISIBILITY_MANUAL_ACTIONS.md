# Ações Manuais — Visibilidade Global (não automatizáveis por exigirem conta/login)

Tudo que podia ser automatizado por código já está rodando (llms.txt, diretórios regionais,
press release x402, MCP manifests). O que resta abaixo exige criar conta em serviço de
terceiro — não posso fazer isso por você, mas deixei tudo pronto para copiar e colar.

---

## 1. Registry MCP oficial (Anthropic) — ✅ CONCLUÍDO (01/07/2026)

Os 3 servidores estão publicados em registry.modelcontextprotocol.io:
- `io.github.carruda-Global/ecosystem-aec-regulatory` v1.0.0
- `io.github.carruda-Global/ecosystem-aec-esg` v1.0.0
- `io.github.carruda-Global/ecosystem-aec-erp` v1.0.0

Manifests em [`mcp-registry/`](../mcp-registry/). Para publicar uma nova versão no futuro,
suba o `version` no arquivo e rode `mcp-publisher publish <arquivo>.server.json` (login já
fica salvo localmente).

## 2. Outros registries MCP (Smithery, Glama, PulseMCP, mcp.so) — 10 min

Esses são formulários web (exigem conta própria). Usar a URL do manifest existente:
`https://engenheiro-producao-ai.onrender.com/mcp/{server_id}/manifest` (regulatory, esg, erp)

| Registry | Link de submissão |
|---|---|
| Smithery | smithery.ai/new |
| Glama | glama.ai/mcp/servers (botão "Submit") |
| PulseMCP | pulsemcp.com/submit |
| mcp.so | mcp.so/submit |

**Descrição padrão (copiar e colar):**
> EcoSystem AEC Regulatory/ESG/ERP MCP Servers — 3 Model Context Protocol servers exposing AI compliance tools (LGPD/GDPR, NR-1, ESG/carbon inventory, ERP integrations for Dynamics/Salesforce/Oracle/SAP). Built by Global Match Engenharia (Brazil). SSE transport, no auth required for read-only tool discovery.

---

## 3. Crunchbase — ✅ CONCLUÍDO (01/07/2026)

Perfil criado: https://www.crunchbase.com/organization/global-match-engenharia-ecosystem-aec

Campos que funcionaram (para referência futura ao editar):
- Industries: até 3 tags do autocomplete (`Artificial Intelligence (AI)`, `Compliance`, `SaaS`) — mais que isso deu erro
- Description: texto simples sem `:` ou `+`, ~110-115 caracteres

## 4. Wellfound / AngelList — 5 min (wellfound.com/company/new)

```
Tagline: 106 AI agents for global compliance — EU AI Act, LGPD, CSRD, DORA, NR-1
Description: (same as Crunchbase above)
Markets: Brazil, USA, Mexico, Colombia, Argentina, India, UAE, European Union
```

---

## Já implementado automaticamente (não precisa fazer nada)

- `/llms.txt` servido pela API — descoberta por ChatGPT/Perplexity/Claude
- 5 diretórios regionais (Tracxn, Inc42, MAGNiTT, EU-Startups, LatamList) — entram na rotação
  de 72h existente (`auto_job_directories`), e-mail de rascunho chega para
  carruda2307@gmail.com encaminhar
- Press release do marco x402/A2A — alterna com o press release original a cada ciclo de
  14 dias (`auto_job_press_release_distribution`), publicado automaticamente no Dev.to,
  Reddit e nas 5 publicações RegTech
