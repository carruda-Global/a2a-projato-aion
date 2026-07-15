# Ecosystem 2.0 — Portfólio de Agentes de IA Regulatórios + LGPD
**Global Match Engenharia de Produção | CREA-SP 5071200171**
**Cristiano Arruda | Versão 2.0 | Junho 2026**

---

## Visão Geral

Portfólio de 9 agentes de IA com foco exclusivo em **obrigações regulatórias brasileiras ativas em 2026**, voltado para PMEs e médias empresas que não têm acesso a soluções enterprise. Todos os agentes serão distribuídos via Google Cloud Marketplace e Oracle Cloud Marketplace como produtos SaaS recorrentes.

**Premissa de posicionamento:** enquanto concorrentes (Domani, Carbonova, Mangue Tech) atendem grandes empresas com tickets acima de R$ 10k/mês, o Ecosystem 2.0 atende o mercado de PMEs com tickets de R$ 290 a R$ 4.900/mês — segmento 10x maior em volume e sem cobertura de IA.

---

## 📋 Esclarecimento Crítico: NR-1 Riscos Psicossociais Exige ART?

**Resposta direta: NÃO.**

A pesquisa confirmou o seguinte:

> *"A norma não exige que a avaliação seja feita exclusivamente por um médico, psicólogo ou engenheiro de segurança. A própria empresa é quem escolhe o responsável, podendo até mesmo montar uma equipe multiprofissional. O único critério é que essas pessoas tenham o conhecimento técnico necessário." (Manual GRO/NR-1 MTE, 2026)*

O que a NR-1 exige para o capítulo psicossocial:
- Profissional com **conhecimento técnico compatível** (não necessariamente Engenheiro de Segurança)
- Para o **PGR completo** (físicos + químicos + biológicos + ergonômicos): sim, exige Engenheiro de Segurança ou Técnico de Segurança habilitado + ART
- Para o **módulo de riscos psicossociais isolado**: não há exigência de ART específica

**Conclusão operacional:**
O Agente 01 (NR-1 Psicossocial) pode ser lançado agora como **módulo autônomo** de identificação, avaliação e documentação de riscos psicossociais. O agente entrega o inventário psicossocial, o plano de ação e os relatórios — o cliente integra ao PGR existente com seu responsável técnico já habilitado.

**O que NÃO fazer:** não chamar o produto de "PGR completo" nem incluir assinatura de ART no escopo — esses são limites claros até a conclusão da pós.

---

## 🔒 LGPD no Ecosystem 2.0 — Estrutura de Conformidade

### Classificação do Ecosystem 2.0 perante a LGPD

O Ecosystem 2.0 atua como **Operador** (processa dados pessoais em nome dos clientes) e, em alguns casos, como **Controlador** (determina finalidades e meios do tratamento para seus próprios fins operacionais). Esta dupla qualidade exige uma estrutura de governança robusta.

### Agentes e Classificação de Risco

| Agente | Dados Tratados | Classificação ANPD | Obrigações Específicas |
|:---|:---|:---|:---|
| **01 - NR-1 Psicossocial** | Dados de saúde mental, absenteísmo, turnover, afastamentos (dados sensíveis) | **Alto Risco** — dados sensíveis + tecnologias inovadoras | DPO obrigatório, RoPA completo, avaliação de impacto, medidas de segurança robustas |
| **02 - CBS/IBS** | Dados fiscais, NCM, faturamento (dados econômicos) | Baixo Risco | RoPA simplificado, canal de comunicação com titulares |
| **03 - LGPD Operacional** | Dados pessoais de clientes, funcionários, fornecedores (dados pessoais) | **Alto Risco** — uso de IA + dados pessoais | DPO obrigatório, RoPA completo, política de segurança da informação |
| **04 - ESG IFRS S1/S2** | Dados ambientais, sociais, de governança (dados pessoais e não pessoais) | Médio Risco | RoPA, medidas de segurança, transparência |
| **05 - Inventário Carbono** | Dados de consumo, emissões (não pessoais) | Baixo Risco | RoPA simplificado |
| **06 - Escopo 3** | Dados de fornecedores (pessoais e não pessoais) | Médio Risco | RoPA, cláusulas contratuais com fornecedores |
| **07 - Canal de Denúncias** | Dados de denunciantes (anonimato garantido), relatos sensíveis | **Alto Risco** — dados sensíveis + tecnologias inovadoras | DPO obrigatório, RoPA completo, criptografia de ponta a ponta |
| **08 - Igualdade Salarial** | Dados de remuneração, gênero, raça (dados sensíveis) | **Alto Risco** — dados sensíveis | DPO obrigatório, RoPA completo, avaliação de impacto |
| **09 - Anticorrupção** | Dados de fornecedores, compliance, denúncias | Médio Risco | RoPA, cláusulas contratuais |

### Obrigações da Global Match como Operadora/Controladora

#### 1. Encarregado de Dados (DPO) — Obrigatório para Agentes de Alto Risco

A Resolução CD/ANPD nº 18/2024 estabelece que agentes de tratamento de pequeno porte que realizam atividades de **alto risco para dados pessoais** (uso intensivo de dados, tratamento que possa afetar direitos fundamentais, ou por meio de tecnologias emergentes ou inovadoras — caso da IA) **devem nomear DPO**, independentemente do porte .

**Como implementar no Ecosystem 2.0:**

- **DPO Interno:** Nomear um profissional (pode ser o próprio Cristiano Arruda ou um colaborador) como Encarregado de Dados, com as seguintes atribuições legais :
  - Aceitar reclamações e comunicações dos titulares
  - Prestar esclarecimentos à ANPD
  - Orientar os funcionários sobre as práticas de proteção de dados
  - Atuar como canal de comunicação entre a empresa e a ANPD

- **Procedimento para DPO:** Designação formal, com registro de data e qualificação do profissional . A ausência de DPO para atividades de alto risco caracteriza infração à LGPD.

#### 2. Registro de Operações de Tratamento (RoPA)

Mesmo com a simplificação para agentes de pequeno porte, o Ecosystem 2.0 deve manter um registro das operações de tratamento de dados .

**Modelo Simplificado ANPD (8 campos)** :
1. Informações de contato da organização
2. Categorias de titulares de dados pessoais
3. Dados pessoais tratados
4. Compartilhamento dos dados com terceiros
5. Medidas de segurança implementadas
6. Período de armazenamento dos dados pessoais
7. Processo, finalidade e hipótese legal do tratamento
8. Observações

**Quando usar o modelo completo:** Para os agentes classificados como **Alto Risco** (01, 03, 07, 08), o RoPA deve ser mais detalhado, incluindo avaliação de impacto.

#### 3. Política de Segurança da Informação

A ANPD publicou um **Guia Orientativo de Segurança da Informação** para agentes de pequeno porte, com medidas administrativas e técnicas mínimas .

**Medidas Administrativas Obrigatórias:**
- Política simplificada de segurança da informação
- Conscientização e treinamento dos funcionários
- Gerenciamento de contratos com cláusulas LGPD
- Termos de confidencialidade (NDA)

**Medidas Técnicas Obrigatórias:**
- Controle de acesso (dados acessados somente por pessoas autorizadas) 
- Segurança dos dados pessoais armazenados (criptografia em repouso)
- Segurança das comunicações (criptografia em trânsito — TLS)
- Gerenciamento de vulnerabilidades
- Medidas para uso de dispositivos móveis
- Medidas para serviços em nuvem

#### 4. Comunicação de Incidentes de Segurança

Para agentes de pequeno porte, o prazo para comunicação de incidentes é :
- **6 dias úteis** para comunicação à ANPD e ao titular
- **40 dias úteis** para complementar as informações

**Procedimento:** O Agente 03 (LGPD Operacional) deve incluir um módulo de monitoramento de incidentes com notificação automática.

#### 5. Bases Legais para Tratamento de Dados

Cada agente deve ter uma base legal clara para o tratamento de dados:

| Agente | Base Legal Aplicável | Justificativa |
|:---|:---|:---|
| 01 - NR-1 Psicossocial | **Legítimo Interesse** ou **Consentimento** | Dados sensíveis exigem consentimento explícito ou cumprimento de obrigação legal |
| 02 - CBS/IBS | **Cumprimento de Obrigação Legal** | Obrigação tributária da empresa |
| 03 - LGPD | **Legítimo Interesse** ou **Consentimento** | Depende do contexto do tratamento |
| 04 - ESG | **Legítimo Interesse** | Relatórios de sustentabilidade |
| 05 - Carbono | **Cumprimento de Obrigação Legal** | SBCE exige relato |
| 06 - Escopo 3 | **Legítimo Interesse** | Rastreabilidade de fornecedores |
| 07 - Canal de Denúncias | **Cumprimento de Obrigação Legal** | Lei 14.457/2022 + NR-1 |
| 08 - Igualdade Salarial | **Cumprimento de Obrigação Legal** | Lei 14.611/2023 |
| 09 - Anticorrupção | **Legítimo Interesse** | Compliance e prevenção de fraudes |

#### 6. Direitos dos Titulares

Os clientes (empresas) e seus funcionários têm os seguintes direitos garantidos pela LGPD :
- Confirmação da existência de tratamento (15 dias para declaração simplificada, 30 dias para declaração completa)
- Acesso aos dados pessoais
- Correção de dados incompletos, inexatos ou desatualizados
- Anonimização, bloqueio ou eliminação de dados desnecessários
- Portabilidade dos dados a outro fornecedor
- Eliminação dos dados pessoais tratados com consentimento
- Informação sobre compartilhamento de dados
- Revogação do consentimento

#### 7. Transferência Internacional de Dados

Os agentes 04, 05 e 06 podem envolver transferência de dados para fora do Brasil (ex: IFRS, CBAM). Nestes casos, é necessário:
- Cláusulas contratuais padrão da ANPD
- Garantia de nível de proteção adequado

#### 8. Responsabilidade Compartilhada com Clientes PME

Para clientes PME, a responsabilidade pela LGPD é compartilhada :

**O que o cliente PME deve fazer:**
- Manter canal de comunicação com titulares (mesmo sem DPO obrigatório) 
- Atender solicitações em prazo diferenciado (dobro) 
- Registrar operações de tratamento de forma simplificada 
- Adotar medidas de segurança compatíveis com seu porte 

**O que o Ecosystem 2.0 oferece ao cliente:**
- RoPA simplificado gerado automaticamente
- Modelo de Política de Segurança da Informação
- Checklist de medidas de segurança (guia ANPD) 
- Canal de comunicação com titulares integrado
- Suporte para atendimento de solicitações

#### 9. Termos de Uso e Política de Privacidade

O Ecosystem 2.0 deve ter documentos que reflitam a dupla qualidade (Controlador/Operador):

**Termos de Uso (para o cliente PME):**
- Definição clara de papéis (quem é Controlador, quem é Operador)
- Base legal para cada agente
- Responsabilidades do cliente PME (ex: obter consentimentos de funcionários)
- Responsabilidades da Global Match (ex: segurança dos dados, notificação de incidentes)
- Cláusulas de LGPD em contratos com fornecedores

**Política de Privacidade (para titulares):**
- Quais dados são coletados
- Finalidade do tratamento
- Bases legais
- Direitos dos titulares
- Compartilhamento com terceiros
- Medidas de segurança
- Contato do DPO

#### 10. Checklist de Implementação LGPD no Ecosystem 2.0

| # | Item | Prazo | Responsável |
|---|------|-------|-------------|
| 1 | Nomear DPO (interno ou terceirizado) | Imediato | Cristiano Arruda |
| 2 | Designação formal do DPO com registro | Imediato | Jurídico |
| 3 | Criar RoPA para cada agente (modelo ANPD) | 1ª semana | Compliance |
| 4 | Implementar política de segurança da informação | 1ª semana | TI |
| 5 | Configurar criptografia em repouso e trânsito | 1ª semana | TI |
| 6 | Implementar controle de acesso por agente | 2ª semana | TI |
| 7 | Criar canal de comunicação com titulares | 2ª semana | Produto |
| 8 | Elaborar Termos de Uso com cláusulas LGPD | 2ª semana | Jurídico |
| 9 | Elaborar Política de Privacidade | 2ª semana | Jurídico |
| 10 | Treinar equipe sobre LGPD e dados sensíveis | 3ª semana | Compliance |
| 11 | Configurar procedimento de notificação de incidentes | 3ª semana | TI |
| 12 | Testar fluxo de solicitação de titulares | 4ª semana | QA |
| 13 | Auditoria de conformidade | Mês 2 | Externo |

---

## Mapa de Urgência Regulatória

| # | Agente | Lei / Norma | Status | Multa / Risco |
|---|--------|------------|--------|--------------|
| 1 | NR-1 Psicossocial | Portaria MTE 1.419/2024 | 🔴 Vigente mai/2026 | Autuação + passivo trabalhista |
| 2 | Tributário CBS/IBS | Lei Complementar 214/2025 | 🔴 Vigente jan/2026 | Multa a partir ago/2026 |
| 3 | LGPD Operacional | Lei 13.709/2018 + ANPD | 🔴 Fiscalização ativa | Até 2% faturamento / R$ 50M |
| 4 | ESG IFRS S1/S2 PME | Resolução CVM 193/2023 | 🔴 Vigente jan/2026 | Exclusão de cadeias B2B |
| 5 | Inventário Carbono Escopo 1/2 | Lei 15.042/2024 (SBCE) | 🟡 Fase piloto 2026 | Multa até R$ 5M |
| 6 | Escopo 3 Fornecedores | SBCE + CBAM + IFRS S2 | 🟡 Efeito cascata 2026 | Exclusão de contratos |
| 7 | Canal de Denúncias | Lei 14.457/2022 | 🟡 Vigente 2022 | Passivo trabalhista + licitações |
| 8 | Igualdade Salarial | Lei 14.611/2023 | 🟡 Semestral obrigatório | Multa + reputação B3 |
| 9 | Compliance Anticorrupção PME | Lei 12.846/2013 + Dec. 11.129/2022 | 🟢 Exigido em licitações | Exclusão de contratos públicos |

---

## Agente 01 — NR-1 Riscos Psicossociais

### Contexto Regulatório
A Portaria MTE nº 1.419/2024 incluiu obrigatoriamente os Fatores de Riscos Psicossociais Relacionados ao Trabalho (FRPRT) no PGR. Vigência punitiva: 26 de maio de 2026. 82% dos profissionais de RH afirmam não estar preparados. O manual oficial do MTE (2026) esclarece que a avaliação **não precisa ser feita por engenheiro de segurança** — o critério é conhecimento técnico compatível.

### O que o Agente Entrega (escopo correto)
O agente cobre exclusivamente o **módulo psicossocial** do GRO, que é a novidade da atualização de 2026. O cliente integra o output ao PGR existente com seu responsável técnico já habilitado.

- Inventário de Fatores de Riscos Psicossociais documentado e auditável
- Plano de ação com medidas, responsáveis e prazos
- Relatório executivo para apresentação à fiscalização
- Dashboard de monitoramento contínuo
- Alertas de revisão periódica (mínimo a cada 2 anos conforme NR-1)

**🔒 LGPD:** O agente lida com **dados sensíveis** (saúde mental, absenteísmo, afastamentos por CID F). Classificação ANPD: **Alto Risco** . Exige DPO, RoPA completo, avaliação de impacto, política de segurança da informação robusta, e consentimento explícito dos titulares.

### O que o Agente NÃO cobre (limite de escopo)
- Elaboração do PGR completo (riscos físicos, químicos, biológicos, ergonômicos)
- Assinatura de ART
- Substituição do responsável técnico habilitado para o PGR completo

### Funcionalidades Detalhadas
- Aplicação dos questionários validados pelo MTE: COPSOQ, JCQ, PHQ-9, GAD-7
- Identificação e classificação dos 9 grupos de FRPRT conforme guia oficial MTE
- Análise de indicadores objetivos: absenteísmo, turnover, afastamentos por CID F
- Geração do Inventário de Riscos Psicossociais no formato exigido pela NR-1
- Plano de ação hierarquizado (eliminar → substituir → controlar → mitigar)
- Integração com canal de denúncias (cross-sell natural com Agente 07)

### ICP — Perfil do Cliente Ideal
Empresas de 20 a 500 funcionários, todos os setores com empregados CLT. Prioridade: teleatendimento, bancos, saúde, construção civil, varejo. Decisor: Gerente de RH, Diretor de Pessoas, SESMT, CEO.

### Ticket e Modelo Comercial
- Starter (até 50 func.): R$ 390/mês
- Professional (até 200 func.): R$ 790/mês
- Enterprise (até 500 func.): R$ 1.390/mês
- Modelo: assinatura anual com 20% desconto

### Concorrência
Baixa. Nenhum agente de IA self-serve especializado neste recorte para PMEs identificado.

---

## Agente 02 — Tributário CBS/IBS Compliance

### Contexto Regulatório
A Lei Complementar nº 214/2025 institui a CBS (federal) e o IBS (estadual/municipal). Em vigor desde janeiro de 2026, penalidades a partir de agosto de 2026. Empresas operam simultaneamente no modelo antigo e no novo — complexidade sem precedente. Mais de 19 milhões de empresas ativas no Brasil impactadas.

**🔒 LGPD:** O agente lida com dados fiscais (NCM, faturamento). Classificação ANPD: **Baixo Risco**. Aplica-se RoPA simplificado e canal de comunicação com titulares.

### Funcionalidades do Agente
- Monitor em tempo real de alterações na legislação CBS/IBS com alertas automáticos
- Classificação automática de produtos/serviços com NCM e alíquotas corretas
- Verificação de inconsistências entre sistema antigo e novo
- Geração automática da DeRE (Declaração de Regimes Específicos)
- Checklist de adequação por tipo de empresa (Simples, Lucro Presumido, Real)
- Simulador de impacto financeiro da transição tributária
- Integração via API com ERP (TOTVS, SAP, Oracle)

### Responsabilidade Técnica
Agente opera com base nas normas oficiais da Receita Federal, Comitê Gestor do IBS e Ministério da Fazenda. Recomendação de validação com contador habilitado para decisões definitivas.

### ICP — Perfil do Cliente Ideal
Empresas de médio porte (R$ 1M–50M faturamento), escritórios contábeis. Decisor: CFO, Controller, Contador responsável.

### Ticket e Modelo Comercial
- Individual (1 CNPJ): R$ 390/mês
- Escritório (até 20 CNPJs): R$ 1.490/mês
- Bureau (até 100 CNPJs): R$ 3.900/mês

### Concorrência
Baixa para PMEs. Players enterprise (TOTVS, SAP) não atendem este segmento com produto self-serve.

---

## Agente 03 — LGPD Operacional PME

### Contexto Regulatório
LGPD (Lei 13.709/2018) em fiscalização plena pela ANPD em 2026, foco crescente em PMEs. Multa de até 2% do faturamento ou R$ 50 milhões por infração.

### Funcionalidades do Agente
- Mapeamento automatizado de fluxos de dados
- Geração do RoPA (Registro de Operações de Tratamento) conforme ANPD
- Identificação de lacunas de base legal para cada tratamento
- Modelos de aviso de privacidade, termos e contratos com operadores
- Protocolo de resposta a solicitações de titulares
- Monitoramento de incidentes com notificação automática à ANPD
- Dashboard de conformidade com score de maturidade LGPD
- **Módulo DPO:** designação formal, registro de data e qualificação 

**🔒 LGPD:** O agente lida com dados pessoais de clientes, funcionários e fornecedores. Classificação ANPD: **Alto Risco** — uso de IA + dados pessoais . Exige DPO, RoPA completo, política de segurança da informação robusta, e avaliação de impacto.

### ICP — Perfil do Cliente Ideal
Empresas de 10 a 200 funcionários que coletam dados de clientes/funcionários. Decisor: CEO/sócio, Gerente de TI, Jurídico.

### Ticket e Modelo Comercial
- Starter (até 50 func.): R$ 290/mês
- Professional (até 200 func.): R$ 590/mês
- Enterprise (até 500 func.): R$ 990/mês
- Implementação: R$ 1.500 (setup único)

### Concorrência
Média. Existem consultorias mas sem produto self-serve acessível para PMEs.

---

## Agente 04 — ESG IFRS S1/S2 para PMEs e Fornecedores

### Contexto Regulatório
Resolução CVM 193/2023 tornou obrigatório para companhias abertas o reporte IFRS S1 e S2 a partir de 2026. Efeito cascata: grandes empresas repassam exigências ESG para toda sua cadeia via contratos. PMEs sem indicadores ESG serão excluídas de cadeias de suprimento.

**🔒 LGPD:** O agente lida com dados ambientais, sociais e de governança (dados pessoais e não pessoais). Classificação ANPD: **Médio Risco**. Aplica-se RoPA, medidas de segurança, transparência e cláusulas contratuais.

### Funcionalidades do Agente
- Diagnóstico inicial de maturidade ESG em 30 minutos
- Mapeamento dos indicadores materiais para o setor (SASB)
- Geração de relatório de sustentabilidade simplificado alinhado ao IFRS S1
- Resposta automatizada a questionários ESG de clientes (GRI, CDP simplificado)
- Plano de ação priorizado para melhoria do score ESG
- Monitoramento de indicadores sociais: NR-1 psicossocial, igualdade salarial, diversidade
- Alertas de atualização normativa

### ICP — Perfil do Cliente Ideal
PMEs fornecedoras de grandes empresas. Receita R$ 2M–100M. Decisor: CEO, Gerente de Qualidade, Sustentabilidade.

### Ticket e Modelo Comercial
- Essencial: R$ 490/mês
- Professional: R$ 990/mês
- Enterprise: R$ 2.490/mês

### Concorrência
Baixa para PMEs. Domani, Mangue Tech e Carbonova atendem enterprise (R$ 10k+/mês). Gap confirmado.

---

## Agente 05 — Inventário de Carbono Escopo 1 e 2

### Contexto Regulatório
Lei 15.042/2024 criou o SBCE. Obrigação de relato para empresas acima de 10.000 tCO₂e/ano. Piloto 2026, 17 setores até 2031. Multa: até R$ 5 milhões.

**🔒 LGPD:** O agente lida com dados de consumo e emissões (não pessoais). Classificação ANPD: **Baixo Risco**. Aplica-se RoPA simplificado.

### Funcionalidades do Agente
- Coleta automatizada de dados de consumo via formulário ou integração com ERP
- Cálculo automático de Escopo 1 e Escopo 2 com fatores de emissão atualizados (MCTI, SIN)
- Geração do inventário GHG Protocol com trilha de auditoria completa
- Relatório no formato para submissão ao SINARE (plataforma SBCE)
- Identificação de hotspots de emissão e oportunidades de redução
- Comparativo ano a ano com metas de descarbonização

### Responsabilidade Técnica
Engenheiro de Produção como responsável técnico pela metodologia. Verificação externa por auditor ISO 14064-3 é necessária para submissão oficial ao SBCE.

### ICP — Perfil do Cliente Ideal
Indústrias: siderurgia, cimento, química, papel/celulose, alumínio, vidro, energia, logística. Emissão 5.000–100.000 tCO₂e/ano. Decisor: Gerente de Sustentabilidade, Engenheiro Ambiental, CFO.

### Ticket e Modelo Comercial
- Starter (1 planta): R$ 890/mês
- Professional (múltiplas plantas): R$ 2.490/mês
- Enterprise (grupo econômico): R$ 4.900/mês
- Implementação: R$ 3.000–8.000

### Concorrência
Média. Carbonova e Mangue Tech no enterprise. Oportunidade no segmento PME.

---

## Agente 06 — Escopo 3 Rastreabilidade de Fornecedores

### Contexto Regulatório
Escopo 3 representa 70–90% da pegada total. SBCE, IFRS S2 e CBAM exigem dados primários dos fornecedores. Grandes empresas já incluem em contratos como critério de homologação.

**🔒 LGPD:** O agente lida com dados de fornecedores (pessoais e não pessoais). Classificação ANPD: **Médio Risco**. Aplica-se RoPA e cláusulas contratuais com fornecedores.

### Funcionalidades do Agente
- Portal self-serve para fornecedores responderem questionário de emissões
- Cálculo automático da pegada por fornecedor com fatores setoriais
- Consolidação das 15 categorias do GHG Protocol Escopo 3
- Score de maturidade ESG por fornecedor (ranking)
- Relatório Escopo 3 para IFRS S2 e CBAM
- Plano de engajamento e capacitação de fornecedores

### ICP — Perfil do Cliente Ideal
Empresas com cadeias complexas: manufatura, agronegócio, varejo, construção civil. Decisor: Gerente de Compras/Supply Chain, Gerente de Sustentabilidade.

### Ticket e Modelo Comercial
- Starter (até 50 fornecedores): R$ 690/mês
- Professional (até 200 fornecedores): R$ 1.490/mês
- Enterprise (ilimitado): R$ 3.490/mês

### Concorrência
Baixa. Nenhum produto self-serve para Escopo 3 de fornecedores em PMEs identificado no Brasil.

---

## Agente 07 — Canal de Denúncias Inteligente

### Contexto Regulatório
Lei 14.457/2022 obriga empresas com CIPA (a partir de 20 funcionários) a ter canal de denúncias de assédio. Exigido também para contratos com a administração pública. A NR-1 (mai/2026) integra o canal ao gerenciamento de riscos psicossociais.

**🔒 LGPD:** O agente lida com dados de denunciantes (anonimato garantido) e relatos sensíveis. Classificação ANPD: **Alto Risco** — dados sensíveis + tecnologias inovadoras . Exige DPO, RoPA completo, criptografia de ponta a ponta, e medidas de segurança robustas.

### Funcionalidades do Agente
- Canal omnichannel (WhatsApp, formulário web, e-mail criptografado) com anonimato garantido
- Triagem automática por categoria (assédio moral, sexual, discriminação, fraude, segurança)
- Fluxo de investigação automatizado com prazos e responsáveis
- Respostas automáticas ao denunciante mantendo anonimato
- Relatório semestral de denúncias para CIPA e diretoria
- Integração natural com Agente 01 (NR-1 Psicossocial): alimenta indicadores de riscos
- Dashboard de status e tempo médio de resolução

### ICP — Perfil do Cliente Ideal
Empresas com 20+ funcionários, especialmente com contratos com o poder público. Decisor: Jurídico, RH, Compliance, CEO.

### Ticket e Modelo Comercial
- Starter (até 100 func.): R$ 290/mês
- Professional (até 500 func.): R$ 590/mês
- Enterprise (ilimitado): R$ 990/mês

### Concorrência
Baixa. Soluções de ouvidoria existem mas sem integração com NR-1 e sem preço acessível para PMEs.

---

## Agente 08 — Igualdade Salarial e Diversidade

### Contexto Regulatório
Lei 14.611/2023: relato semestral obrigatório de equidade salarial para empresas com 100+ empregados. Multa de até 3% da folha, limitada a 100 salários mínimos. B3 exige representatividade de gênero e diversidade em conselhos das companhias listadas.

**🔒 LGPD:** O agente lida com dados de remuneração, gênero e raça — **dados sensíveis** . Classificação ANPD: **Alto Risco**. Exige DPO, RoPA completo, avaliação de impacto, consentimento explícito e medidas de segurança robustas.

### Funcionalidades do Agente
- Integração com folha de pagamento para extração automática de dados
- Cálculo dos indicadores de equidade salarial por cargo e função
- Análise de gaps de remuneração com identificação de causas
- Geração do relatório semestral no formato exigido pelo MTE (Portal Emprega Brasil)
- Plano de ação para redução dos gaps
- Monitoramento de diversidade: gênero, raça, PCD, geração em liderança
- Alertas de prazo dos relatórios semestrais

### ICP — Perfil do Cliente Ideal
Empresas com 100+ funcionários, todos os setores. Decisor: Diretor de RH, DPO, Jurídico, CEO.

### Ticket e Modelo Comercial
- Standard (100–300 func.): R$ 490/mês
- Professional (300–1.000 func.): R$ 890/mês
- Enterprise (1.000+ func.): R$ 1.490/mês

### Concorrência
Praticamente nenhuma. Nenhum agente de IA específico para este compliance identificado.

---

## Agente 09 — Compliance Anticorrupção PME

### Contexto Regulatório
Lei Anticorrupção (12.846/2013) e Decreto 11.129/2022: empresas que contratam com o poder público precisam de programa de integridade. Critério objetivo em licitações federais e estaduais em 2026. Empresas sem programa estruturado são desclassificadas.

**🔒 LGPD:** O agente lida com dados de fornecedores, compliance e denúncias. Classificação ANPD: **Médio Risco**. Aplica-se RoPA e cláusulas contratuais.

### Funcionalidades do Agente
- Diagnóstico de maturidade conforme guia CGU
- Código de Ética e Conduta personalizado para o segmento
- Políticas de prevenção: anticorrupção, presentes, conflito de interesses
- Treinamento automatizado por cargo com registro de conclusão
- Due diligence automatizado de terceiros e fornecedores
- Integração com canal de denúncias (Agente 07)
- Relatório do programa de integridade no formato CGU para licitações

### ICP — Perfil do Cliente Ideal
Empresas que vendem para o governo ou estatais. Todos os setores. Decisor: CEO, Jurídico, Diretor Comercial.

### Ticket e Modelo Comercial
- Starter (documento básico): R$ 390/mês
- Professional (programa completo + treinamentos): R$ 790/mês
- Enterprise (programa + due diligence terceiros): R$ 1.490/mês

### Concorrência
Baixa. Consultorias caras existem, mas nenhum produto self-serve com IA para PMEs.

---

## Estrutura Técnica — Stack Comum + LGPD

### Infraestrutura
- **LLM Core:** Claude API (Anthropic) / Gemini Pro (Google)
- **Orquestração:** n8n (self-hosted) ou LangChain
- **Base de conhecimento:** RAG sobre legislação brasileira atualizada
- **Banco de dados:** PostgreSQL + Pinecone (vetorial)
- **Checkout/Billing:** Stripe + Abacatepay (PIX)
- **Email automação:** Brevo
- **Hospedagem:** Google Cloud Platform (GKE) + Oracle Cloud

### Segurança e LGPD
- **Criptografia em trânsito:** TLS 1.3
- **Criptografia em repouso:** AES-256
- **Controle de acesso:** RBAC por agente e papel
- **Anonimização:** Dados sensíveis (saúde mental, remuneração, gênero) são anonimizados após análise
- **Logs de auditoria:** Merkle chain SHA-256 para compliance
- **DPO:** Profissional designado e registrado
- **RoPA:** Registro de Operações de Tratamento para cada agente
- **Política de Segurança da Informação:** Baseada no Guia ANPD 
- **Incidentes:** Procedimento de notificação em até 6 dias úteis 

### Distribuição
- Google Cloud Marketplace (Agent Card A2A)
- Oracle Cloud Marketplace (SaaS listing)
- Site próprio (global-engenharia.com)
- Hotmart (afiliados, agentes de menor ticket)
- Kiwify (assinatura recorrente)

### Compliance Técnico
- LGPD: dados em servidores no Brasil, criptografia em trânsito e repouso
- SLA: 99,5% uptime garantido
- **DPO:** nomeado e registrado conforme Resolução CD/ANPD nº 18/2024 
- **RoPA:** modelo simplificado ANPD para agentes de baixo risco, completo para alto risco 

---

## Roadmap de Lançamento

### Fase 1 — Q3 2026 (Julho–Setembro)

| Agente | Prazo | Justificativa |
|--------|-------|--------------|
| Agente 01 — NR-1 Psicossocial | Julho 2026 | Lei em vigor, sem ART, 82% despreparados |
| Agente 08 — Igualdade Salarial | Julho 2026 | Zero concorrência, relatório em agosto |
| Agente 07 — Canal de Denúncias | Agosto 2026 | Cross-sell natural com Agente 01 |
| Agente 03 — LGPD Operacional | Setembro 2026 | Fiscalização ativa |

### Fase 2 — Q4 2026 (Outubro–Dezembro)

| Agente | Prazo | Justificativa |
|--------|-------|--------------|
| Agente 02 — Tributário CBS/IBS | Outubro 2026 | Multas a partir de agosto |
| Agente 09 — Anticorrupção PME | Novembro 2026 | Licitações de fim de ano |

### Fase 3 — Q1 2027 (Janeiro–Março)

| Agente | Prazo | Justificativa |
|--------|-------|--------------|
| Agente 04 — ESG IFRS S1/S2 PME | Janeiro 2027 | Primeiro relatório IFRS em 2027 |
| Agente 05 — Inventário Carbono | Fevereiro 2027 | SBCE pilotos |
| Agente 06 — Escopo 3 | Março 2027 | Extensão do Agente 05 |

---

## Projeção de Receita — Cenário Base (após 6 meses)

| Agente | Clientes | Ticket médio | MRR |
|--------|----------|-------------|-----|
| 01 NR-1 Psicossocial | 30 | R$ 790 | R$ 23.700 |
| 02 Tributário CBS/IBS | 50 | R$ 590 | R$ 29.500 |
| 03 LGPD Operacional | 40 | R$ 490 | R$ 19.600 |
| 04 ESG IFRS S1/S2 | 20 | R$ 790 | R$ 15.800 |
| 05 Inventário Carbono | 15 | R$ 1.690 | R$ 25.350 |
| 06 Escopo 3 | 20 | R$ 990 | R$ 19.800 |
| 07 Canal Denúncias | 60 | R$ 390 | R$ 23.400 |
| 08 Igualdade Salarial | 35 | R$ 690 | R$ 24.150 |
| 09 Anticorrupção | 30 | R$ 590 | R$ 17.700 |
| **TOTAL** | **300** | **R$ 688** | **R$ 199.000** |

**ARR projetado (ano 1 completo):** ~R$ 2.388.000

---

## Notas Técnicas e Limites de Atuação

1. **Agente 01 (NR-1):** escopo restrito ao módulo psicossocial. Não inclui PGR completo, não emite ART. Disponível para lançamento imediato.
2. **Agente 03 (LGPD):** lida com dados pessoais e sensíveis. Exige DPO obrigatório (Resolução CD/ANPD nº 18/2024) .
3. **Agente 05 (Carbono):** verificação externa por auditor ISO 14064-3 é necessária para submissão oficial ao SBCE — informar claramente ao cliente.
4. **PGR completo:** incluir no portfólio após conclusão da pós-graduação em Engenharia de Segurança do Trabalho (jun/2027). Prioridade de adição: Q3 2027.
5. **Atualização da base normativa:** processo mensal de atualização com novas regulamentações.
6. **Disclaimer em todos os agentes:** "Este agente é uma ferramenta de apoio à conformidade e não substitui assessoria jurídica, contábil ou de engenharia para casos específicos."
7. **LGPD dos agentes:** os produtos 01, 03, 07 e 08 coletam dados sensíveis. Implementar DPA robusto antes do lançamento. Para agentes de alto risco, DPO obrigatório .

---

## 📋 Checklist LGPD para o Ecosystem 2.0 (Implementação)

### Imediato (Antes do Lançamento)
- [ ] Nomear DPO (interno ou terceirizado) — obrigatório para agentes de alto risco 
- [ ] Designação formal do DPO com registro de data e qualificação 
- [ ] Criar RoPA (Registro de Operações de Tratamento) para cada agente
- [ ] Elaborar Política de Privacidade (para titulares)
- [ ] Elaborar Termos de Uso com cláusulas LGPD
- [ ] Implementar criptografia em trânsito (TLS 1.3) e repouso (AES-256)
- [ ] Criar canal de comunicação com titulares
- [ ] Implementar controle de acesso por agente

### Curto Prazo (1ª quinzena)
- [ ] Configurar procedimento de notificação de incidentes (6 dias úteis) 
- [ ] Treinar equipe sobre LGPD e dados sensíveis
- [ ] Implementar política de segurança da informação (Guia ANPD) 
- [ ] Criar modelo de resposta a solicitações de titulares

### Médio Prazo (2ª quinzena)
- [ ] Implementar anonimização de dados sensíveis
- [ ] Criar checklist de medidas de segurança (ANPD) 
- [ ] Auditoria de conformidade (externa)

### Contínuo
- [ ] Monitoramento de mudanças na regulamentação ANPD
- [ ] Revisão anual do RoPA e políticas
- [ ] Atualização de treinamentos
- [ ] Registro de incidentes e lições aprendidas

---

*Documento gerado em 22 de junho de 2026 | Global Match Engenharia de Produção*
*Versão 2.0 — Inclusão da estrutura completa de LGPD (DPO, RoPA, políticas, classificação de risco, checklist)*
*Próxima revisão: setembro de 2026*