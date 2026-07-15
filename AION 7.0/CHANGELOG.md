# Changelog — H-MAS EcoSystem AEC + Regulatory

## [3.0.0] — 2026-06-25 (Cross-Sell Bridge + 3 Novos Agentes)

### Novos Agentes
- **Onboarding de Funcionários (#N1)**: Automatiza admissão, contratos, checklist de documentos, provisionamento de acessos (email, Teams, sistemas), eSocial. Preço: R$ 490/mês
- **Atendimento ao Cliente PT-BR (#N2)**: Resolve tickets L1 via WhatsApp + Teams em português brasileiro. Cobre dúvidas, status, agendamento, FAQs. Preço: R$ 390/mês
- **Conciliação Financeira (#N3)**: Automatiza fechamento mensal: concilia NFs com extratos, faturas de cartão e boletos. Identifica divergências. Preço: R$ 790/mês

### Bridge de Cross-Sell Vertical (BRIDGE_CROSSSELL_RAG.md)
- Implementada `JOURNEY_TRIGGERS` com 14 triggers conectando agentes em 3 jornadas verticais (A: RH→Financeiro→Compliance, B: Fiscal→ESG→Carbono, C: AEC→Regulatório→Microsoft)
- Função `get_cross_sell_recommendation()` com avaliação de condições do tenant e desconto de ativação de 15%
- Função `get_journey_progress()` para mapear progresso do cliente nas jornadas
- Endpoint `GET /api/cross-sell/recommend/{tenant_id}` com notificação de upsell para o dashboard
- Endpoint `GET /api/cross-sell/journeys` listando as 3 jornadas com steps e condições
- Função `eval_condition()` para avaliação segura de condições de trigger
- Função `get_regulatory_deadline()` com prazos regulatórios por agente

### Planos e Monetização
- 3 novos planos: Cross-Sell Harmony (R$490), Atendimento Plus (R$390), Conciliação Pro (R$790)
- Total: 9 planos (6 ativos + 3 novos)
- Full Suite expandido para 30 agentes (mantido mesmo preço R$ 9.497)
- Desconto de 15% configurado para todos os cross-sell triggers no Stripe

### Marketplaces (Listings)
- Microsoft Marketplace: offer JSON atualizado para 30 agentes, descrição técnica com RAG híbrido, controle de custo por token, fallback automático
- Salesforce AgentExchange: descrição atualizada com argumento RAG técnico

### Documentação
- AGENTS.md atualizado: 30 agentes, Grupo 6 (Cross-Sell), 3 Jornadas Verticais
- BRIDGE_CROSSSELL_RAG.md implementado conforme especificação (373 linhas)
- config.yaml: cluster cross_sell adicionado, planos Stripe adicionados

### Testes
- 45/45 testes passando (test_plans.py e test_orchestrator.py atualizados para 30 agentes/9 planos)

## [2.1.0] — 2026-06-24

### Segurança (crítico)
- Criado `.dockerignore` cobrindo `.env`, `*.key`, `*.pem`, `chave_api.txt` e demais arquivos sensíveis
- `Dockerfile` corrigido: adicionado usuário não-root (`appuser`), removido `APP_ENV=development` hardcoded, adicionado `HEALTHCHECK`
- `config.yaml`: `tenant_id` e `client_id` do Microsoft Marketplace movidos para `${AZURE_TENANT_ID}` e `${AZURE_CLIENT_ID}`
- `.env.example`: removido `AZURE_TENANT_ID` real; adicionadas variáveis Salesforce, Vault e infraestrutura Docker
- `.gitignore`: adicionadas entradas para `EcoSystem 2.0.env`, `.env.*`, `chave_api.txt`, `.env.render`

### Infraestrutura
- `docker-compose.yml`: adicionado `healthcheck` no serviço `orchestrator`
- `deploy.sh`: substituído `sleep 10` por `timeout 120 bash -c 'until curl -sf ...'` — aguarda saúde real do orquestrador
- `test_jwt.py`: removido path absoluto Windows; chave agora lida via `SALESFORCE_KEY_PATH` (env var) com fallback relativo ao projeto

### Documentação
- Criado `CHANGELOG.md` (este arquivo)

### Pendente — ação manual obrigatória
- [ ] Revogar Stripe live key (`sk_live_51Tkp…`) no dashboard Stripe
- [ ] Revogar Stripe webhook secret (`whsec_ObbQv…`) e gerar novo separado por ambiente
- [ ] Revogar Supabase service key (`sb_secret_anWk8…`) no painel Supabase
- [ ] Revogar DeepSeek API key (`sk-b71dff…`) no painel DeepSeek
- [ ] Revogar GitHub PAT (`ghp_RdncAhD1…`) em GitHub → Settings → Tokens
- [ ] Revogar Swarms API key (`sk-3987e4…`) no painel Swarms
- [ ] Trocar `VAULT_TOKEN` (`hmas_root_token_2024`) por token gerado com TTL adequado
- [ ] Mover todas as credenciais para o Vault (já presente no docker-compose)
- [ ] Separar webhooks Stripe por ambiente (test vs production)
- [ ] Definir LLM segregado para agentes sensíveis LGPD (#13 NR-1, #15 LGPD, #19 Canal Denúncias, #20 Igualdade Salarial): usar Gemini ou Claude API

---

## [2.0.0] — 2026-05 (baseline)

### Estado inicial
- 27 agentes: AEC (#1–12), Regulatory (#13–21), Microsoft Pack (#22–27)
- Marketplaces: Google Cloud, Microsoft, Salesforce, AWS, Oracle ativos ou em desenvolvimento
- Stack Docker: 14 serviços (Postgres, TimescaleDB, Redis, Neo4j, ChromaDB, Kafka, Zookeeper, MinIO, Prometheus, Grafana, Elasticsearch, Logstash, Kibana, Vault, Orchestrator)
- Planos Stripe: 10 planos (starter, professional, enterprise, full_suite, compliance_pack, regulatory_starter, regulatory_professional, regulatory_full, esg_carbon_pack, microsoft_pack)

---

## Roadmap Q3 2026

### Produto
- [ ] Consolidar 10 planos em 6: Compliance Essencial (R$590), Regulatory Pro (R$1.490), ESG+Carbono (R$2.490), AEC Full (R$4.685), Microsoft Pack (R$4.482), Full Suite (R$9.497)
- [ ] Posicionar "Compliance Essencial" como porta de entrada no Google Cloud Marketplace

### Infraestrutura
- [ ] Migrar Kafka + Zookeeper → Redis Streams (já presente na stack)
- [ ] Migrar Elasticsearch + Logstash + Kibana → Grafana Loki (já tem Grafana)
- [ ] Avaliar consolidar Postgres + TimescaleDB em TimescaleDB único
- [ ] Resultado: reduzir de 14 para ~6 serviços, economia estimada de 6–8 GB de RAM

### Marketplaces
- [ ] Pausar AWS Marketplace (ativar só com demanda comprovada)
- [ ] Pausar Oracle Cloud Marketplace (ativar só com demanda comprovada)
- [ ] Pausar SwarmSync/OpenStall (protocolo A2A ainda imaturo)
