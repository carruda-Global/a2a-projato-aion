# Tráfego + Máquina de Faturamento Mundial — AION / EcoSystem AEC
**Pedido em:** 01/07/2026 (sessão noturna)
**Contexto:** Depois de meses com tecnologia completa (106 agentes, 12 planos Stripe, SEO,
SDR) e R$ 0 de faturamento, esta pesquisa foca em ligar o que já existe, não em construir
mais coisa nova.

---

## 1. DIAGNÓSTICO — o que já está construído mas nunca foi ligado

Antes de qualquer canal novo, isto é o que precisa ser corrigido/ativado primeiro, porque
sem isso qualquer tráfego que chegar não converte:

| # | O que existe | Problema encontrado hoje | Status |
|---|---|---|---|
| 1 | Job de SDR (100-500 e-mails/dia teóricos) | Rodava há semanas sem enviar 1 e-mail (2 bugs empilhados: `TypeError` silencioso + lista de leads sempre vazia) | ✅ Corrigido — descobre leads reais via busca e envia sozinho |
| 2 | 290 páginas de SEO geradas | Viviam só na API (`engenheiro-producao-ai.onrender.com`), desconectadas do domínio de marca (`global-engenharia.com`) — Google via dois sites sem relação | ✅ Corrigido (proxy `/artigos/*` + sitemap no domínio certo) — falta deploy manual no Netlify + verificação do Search Console |
| 3 | Seção pay-per-use (diagnóstico avulso, R$10-50, sem assinatura) já codificada em `vendas.html`, com Stripe Checkout real funcionando (`usage_billing.py:163`) | **Nunca foi deployada** — está no código local, não no ar | ❌ Falta subir `vendas.html` pro Netlify |
| 4 | x402 (pagamento direto por agentes de IA) | Implementado e validado, mas precisa do 1º pagamento real pra CDP Bazaar indexar | 🔄 Aguardando 1ª transação |
| 5 | Chat multi-mercado (BR/US/MX/CO/AR) | Existe, mas não está claro se fecha venda ou só informa | ⚠️ Precisa checar se tem CTA de pagamento no fim da conversa |

**Prioridade #1, sem exceção: subir o `vendas.html` atualizado pro Netlify.** Isso sozinho
ativa a porta de entrada de menor fricção que existe (diagnóstico avulso por menos de R$50,
sem compromisso de assinatura) — e já está pronta, só não está no ar.

---

## 2. TRÁFEGO — por velocidade de resultado, não por "quantidade de canais"

### Imediato (dias) — mas pequeno volume
- **SDR automático** (já corrigido) — gera visitas diretas via clique no e-mail. Real, mas
  15-150 cliques/dia no melhor cenário.
- **Product Hunt launch** — nunca foi executado de verdade (só está listado como
  `manual_once` em `directory_submission_agent.py`). Um lançamento coordenado (terça-feira,
  00:01 PST, pedir apoio de rede pessoal nas primeiras 2h) pode trazer **centenas a
  milhares de visitas em 24h**, gratuito. É o canal de maior alavancagem de curto prazo que
  ainda não foi tentado.
- **Reddit/LinkedIn/Dev.to** (já rodando) — tráfego pequeno, mas gratuito e já automatizado.

### Médio prazo (2-8 semanas)
- **SEO orgânico** — só começa a valer depois que: (a) Search Console verificado no domínio
  certo, (b) sitemap submetido, (c) Google efetivamente rastreia e indexa. Não espere nada
  em 15 dias — é investimento de 60-90 dias pra maturar.
- **Backlinks de PR/diretórios** (já rodando via `directory_submission_agent.py`) — ajudam a
  autoridade do domínio, o que acelera a maturação do SEO acima.

### Rápido mas custa dinheiro — não testado ainda
- **Google Ads / Meta Ads de baixo orçamento** (R$20-50/dia) em palavras-chave de altíssima
  intenção: *"multa NR-1 empresa"*, *"EU AI Act readiness check"*, *"diagnóstico LGPD
  gratuito"*. Diferente de SEO, tráfego pago aparece no mesmo dia. Não implementado —
  precisa de conta Google Ads + orçamento definido por você (não posso criar conta nem
  gastar dinheiro sem autorização explícita).
- **Programas de afiliados** (Impact.com — já mapeado na pesquisa de visibilidade de hoje
  cedo) — parceiros promovem em troca de comissão, sem custo fixo adiantado.

---

## 3. MÁQUINA DE FATURAMENTO MUNDIAL — como transformar tráfego em venda recorrente

### 3.1 Funil de menor fricção primeiro
```
Visitante frio → Diagnóstico avulso (R$10-50, sem cartão de crédito recorrente)
             → Resultado mostra risco real (ex: "multa até R$10.000/empregado")
             → Upsell pro plano de assinatura (R$390-1.490/mês) com o problema já provado
```
Isso já está desenhado no código (`vendas.html` + `usage_billing.py`), só falta estar no ar
(item #3 do diagnóstico). Vender assinatura de R$390/mês pra um visitante frio é fricção
alta; vender um relatório de R$15 que prova um risco real e depois converter é o caminho
testado no mercado de PLG (product-led growth).

### 3.2 Cross-sell automático entre os 106 agentes
`src/cross_selling.py` já existe — depois que um cliente compra o primeiro agente (ex:
NR-1), o sistema deveria sugerir automaticamente o próximo (ex: LGPD, Igualdade Salarial).
Verificar se isso está de fato disparando pós-venda ou só existe como lógica sem gatilho
real conectado ao evento de compra no Stripe webhook.

### 3.3 Expansão mundial — usar a urgência regulatória certa por região
Os agentes já existem para os mercados certos, mas a campanha de aquisição (SDR, ads,
conteúdo) precisa citar a *lei específica* de cada lugar, não uma mensagem genérica:

| Região | Gatilho de urgência real | Agente já pronto |
|---|---|---|
| Brasil | NR-1 (prazo já vencido, multa por empregado) | `nr1_psicossocial` |
| EUA/UE | EU AI Act — prazo 2 de agosto de 2026 | `eu_ai_act_agent` |
| México | LFPDPPP | `lfpdppp_agent` |
| Colômbia | Ley 1581 | `ley1581_agent` |
| Índia | (sem gatilho regulatório mapeado ainda) | `india_multilingual_agent` |
| UAE | (sem gatilho regulatório mapeado ainda) | `uae_government_agent` |
| UE (empresas grandes) | CSRD, DORA, NIS2 | `csrd_reporting_agent`, `dora_compliance_agent`, `nis2_agent` |

Índia e UAE têm agente pronto mas **nenhum gancho de urgência regulatória específico**
identificado ainda — sem isso, a campanha de e-mail genérica não converte tão bem quanto
"sua empresa está sujeita a multa" nos outros mercados.

### 3.4 A2A / agentes comprando de agentes (mais lento, mas mundial por natureza)
x402 + 9 marketplaces já implementados nesta sessão (manhã). Esse canal é
estruturalmente diferente: não depende de você alcançar humanos, depende de outros
sistemas de IA descobrirem e pagarem sozinhos. Ainda não tem volume (ecossistema
nascente), mas quando amadurecer, escala sem SDR nenhum — é o único canal
verdadeiramente "roda sozinho, sem limite geográfico" a longo prazo.

---

## 4. PLANO DE EXECUÇÃO — ordem real, sem hype

| Ordem | Ação | Quem faz | Prazo pra impacto |
|---|---|---|---|
| 1 | Deploy do `vendas.html` no Netlify (drag-drop) | Você (2 min) | Imediato |
| 2 | Verificar Search Console no domínio certo + colar meta tag | Você (2 min) + eu colo o código | 2-8 semanas pra SEO valer |
| 3 | Monitorar SDR — taxa de resposta/bounce dos primeiros ciclos | Eu superviso | Contínuo |
| 4 | Lançamento Product Hunt coordenado | Você decide a data, eu preparo o material | 1 dia de pico de tráfego |
| 5 | Checar se cross-sell dispara de verdade pós-compra | Eu investigo o código | — |
| 6 | Definir gatilho regulatório pra Índia/UAE | Eu pesquiso | — |
| 7 | Testar Google Ads com orçamento pequeno (se você aprovar gasto) | Você aprova orçamento + conta | Imediato após aprovação |

**Faturamento real esperado seguindo esta ordem, 30 dias:** ainda modesto (dezenas a
poucas centenas de reais), mas essa é a primeira vez que os canais realmente funcionam de
ponta a ponta em vez de rodar no vazio. O salto de faturamento vem depois que o SEO
matura (60-90 dias) e o volume de SDR/tráfego pago escala com base em dados reais de
conversão, não estimativa.
