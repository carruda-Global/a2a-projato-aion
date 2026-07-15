# Banco Mestre de Riscos — Riscos Físicos — Parte 01

Base regulatória: NR-15, Anexos 1/2 (ruído), 3 (calor), 6 (pressão hiperbárica),
5 (radiação ionizante), 7 (radiação não-ionizante), 8 (vibração).

Fontes: [Guia Trabalhista NR-15](https://www.guiatrabalhista.com.br/legislacao/nr/nr15.htm), [NR-15 Anexo 1](https://www.guiatrabalhista.com.br/legislacao/nr/nr-15-anexo-01.pdf), [Suprema Luvas — Anexo 3 Calor](https://supremaluvas.com.br/nr-15-anexo-3-nr-que-fala-dos-limites-de-tolerancia-para-exposicao-ao-calor/)

---

## RF-0001 — Ruído Contínuo ou Intermitente

```
ID: RF-0001
Categoria: Físico
Perigo: Exposição a Ruído Contínuo ou Intermitente

Descrição Técnica:
Pressão sonora medida em decibéis, circuito de compensação "A", resposta
lenta (SLOW). Acima de 115 dB(A) sem proteção adequada: risco grave e
iminente. Avaliação quantitativa comparando exposição ao limite de tolerância.

Base Legal: NR-15, Anexo 1

Atividades:
- Operação de máquinas em geral (serras, prensas, compressores)
- Marcenaria
- Metalurgia
- Operação de gerador

CNAEs:
- 1610-2/01 (Serrarias)
- 2511-0/00 (Estruturas metálicas)
- 2932-0/01 (Peças para veículos)

Funções:
- Operador de máquina
- Marceneiro
- Metalúrgico

Máquinas:
- Serra circular, compressor, prensa, gerador, esmerilhadeira

Consequências:
- PAIR (Perda Auditiva Induzida por Ruído) — irreversível
- Zumbido
- Estresse, hipertensão (efeitos extra-auditivos)
- Interferência na comunicação (risco indireto de acidente)

Hierarquia de Controle:
1. Eliminação — não aplicável
2. Substituição — equipamento de menor emissão sonora quando disponível
3. Engenharia — enclausuramento de fonte, manutenção preventiva, silenciadores
4. Administrativo — rodízio, redução de tempo de exposição, sinalização de área
5. EPI — protetor auricular (plug ou concha, conforme atenuação necessária)

EPIs:
- Protetor auricular tipo plug (CA obrigatório)
- Protetor auricular tipo concha (para NEE mais alto)

EPCs:
- Enclausuramento acústico de máquinas
- Manutenção preventiva (reduz ruído de desgaste)

Treinamentos:
- PCA (Programa de Conservação Auditiva)
- Uso correto de protetor auricular

Perguntas Condicionais:
- "Existe máquina/equipamento gerando ruído perceptível?" → SIM
- "Foi feita medição de nível de pressão sonora (dosimetria)?"
- "O protetor auricular usado tem atenuação suficiente pro nível medido?"

Regras do Motor:
SE atividade.gera_ruido = VERDADEIRO
ENTÃO adicionar risco RF-0001
E solicitar medicao_dosimetria
E SE nivel_dba > 85 ENTÃO adicionar treinamento "PCA"

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação
- PGR
- PCA (referência cruzada com PCMSO)

Referências:
- NR-15, Anexo 1

Versão: 1.0
```

---

## RF-0002 — Ruído de Impacto

```
ID: RF-0002
Categoria: Físico
Perigo: Exposição a Ruído de Impacto

Descrição Técnica:
Ruído de curta duração e alta intensidade (batidas, prensagem, martelamento).
Avaliado separadamente do ruído contínuo (Anexo 2). Acima de 140 dB(Linear)
picos ou 130 dB(C) fast: risco grave e iminente.

Base Legal: NR-15, Anexo 2

Atividades:
- Prensagem/estampagem
- Martelamento (rebite, forjamento)
- Cravação de estacas (construção civil)

CNAEs:
- 2511-0/00, 2599-3/99 (produtos metálicos)
- 4292-8/01 (obras de fundações — cravação de estacas)

Funções:
- Operador de prensa
- Forjador
- Operador de bate-estacas

Máquinas:
- Prensa excêntrica
- Martelo pneumático
- Bate-estacas

Consequências:
- PAIR de instalação súbita (trauma acústico)
- Perfuração timpânica em exposições extremas
- Sobressalto/reação de susto (risco de acidente associado)

Hierarquia de Controle:
1-2. Eliminação/Substituição — não aplicável
3. Engenharia — isolamento de fonte, amortecedores de impacto
4. Administrativo — distanciamento, rodízio, sinalização
5. EPI — protetor auricular tipo concha (maior atenuação para impacto)

EPIs:
- Protetor auricular tipo concha com atenuação alta

EPCs:
- Isolamento/enclausuramento da fonte de impacto
- Base amortecedora em prensas/bate-estacas

Treinamentos:
- PCA
- Distâncias seguras de operação

Perguntas Condicionais:
- "Existe processo de prensagem, martelamento ou cravação?" → SIM
- "Foi medido pico de pressão sonora (dB Linear)?"

Regras do Motor:
SE atividade IN ("prensagem", "martelamento", "cravacao_estacas")
ENTÃO adicionar risco RF-0002 (distinto de RF-0001)

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação
- PGR

Referências:
- NR-15, Anexo 2

Versão: 1.0
```

---

## RF-0003 — Calor

```
ID: RF-0003
Categoria: Físico
Perigo: Exposição Ocupacional ao Calor

Descrição Técnica:
Avaliado pelo IBUTG (Índice de Bulbo Úmido Termômetro de Globo), combinando
temperatura, umidade e radiação. Relevante em fundições, cozinhas industriais,
trabalho a céu aberto em horário de pico de calor.

Base Legal: NR-15, Anexo 3

Atividades:
- Fundição
- Cozinha industrial
- Trabalho externo em construção civil (exposição solar direta)
- Forno/estufa industrial

CNAEs:
- 2451-2/00 (Fundição)
- 5620-1/01 (Cozinhas industriais)
- 4120-4/00 (Construção — trabalho externo)

Funções:
- Fundidor
- Cozinheiro industrial
- Pedreiro/servente (exposição solar)

Máquinas:
- Forno de fundição
- Fogão industrial, forno de padaria

Consequências:
- Desidratação
- Exaustão pelo calor
- Intermação (golpe de calor) — risco grave e potencialmente fatal
- Cãibras por calor

Hierarquia de Controle:
1. Eliminação — não aplicável
2. Substituição — não aplicável
3. Engenharia — ventilação, exaustão de calor, barreiras de radiação
4. Administrativo — regime de trabalho/descanso (conforme IBUTG), hidratação,
   horário de menor exposição solar (evitar pico 10h-16h para trabalho externo)
5. EPI — vestimenta adequada, quando aplicável

EPIs:
- Vestimenta de proteção térmica (fundição)
- Protetor solar + chapéu/boné com proteção de nuca (trabalho externo)

EPCs:
- Sistema de ventilação/exaustão
- Barreira de radiação térmica (anteparo)
- Pontos de hidratação disponíveis no local

Treinamentos:
- Reconhecimento de sinais de intermação
- Regime de trabalho/descanso conforme NR-15 Anexo 3

Perguntas Condicionais:
- "Existe exposição a fonte de calor (forno, fundição) ou trabalho externo?" → SIM
- "Foi medido o IBUTG?"
- "Existe regime de trabalho/descanso definido?"

Regras do Motor:
SE atividade.exposicao_calor = VERDADEIRO
ENTÃO adicionar risco RF-0003
E solicitar medicao_ibutg
E adicionar controle "regime_trabalho_descanso"

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação
- PGR

Referências:
- NR-15, Anexo 3

Versão: 1.0
```

---

## RF-0004 — Vibração de Mãos e Braços (VMB)

```
ID: RF-0004
Categoria: Físico
Perigo: Exposição à Vibração em Mãos e Braços

Descrição Técnica:
Vibração transmitida ao sistema mão-braço por ferramentas manuais motorizadas.
Associada à Síndrome de Raynaud Ocupacional ("dedo branco"). Avaliação
conforme NR-15 Anexo 8 e NHO-10 (Fundacentro).

Base Legal: NR-15, Anexo 8

Atividades:
- Uso de furadeira/parafusadeira industrial
- Uso de lixadeira/esmerilhadeira
- Uso de martelete/rompedor

CNAEs:
- 4120-4/00 (Construção civil)
- 2511-0/00 (Estruturas metálicas)

Funções:
- Pedreiro (uso de martelete)
- Operador de esmerilhadeira
- Montador industrial

Máquinas:
- Martelete rompedor
- Lixadeira/esmerilhadeira angular
- Parafusadeira de impacto

Consequências:
- Síndrome de Raynaud Ocupacional (dedo branco)
- Distúrbios neurológicos (formigamento, perda de sensibilidade)
- Distúrbios osteoarticulares (mãos, punhos, cotovelos)

Hierarquia de Controle:
1. Eliminação — não aplicável
2. Substituição — ferramentas com menor emissão de vibração (certificação do fabricante)
3. Engenharia — luvas antivibratórias, manutenção preventiva das ferramentas
4. Administrativo — limitação de tempo de exposição contínua, pausas
5. EPI — luvas antivibratórias (eficácia limitada — controle administrativo é prioritário)

EPIs:
- Luvas antivibratórias

EPCs:
- Não aplicável diretamente (controle é majoritariamente administrativo/engenharia na fonte)

Treinamentos:
- Reconhecimento de sintomas iniciais (formigamento, dedo branco)
- Uso correto e manutenção de ferramentas vibratórias

Perguntas Condicionais:
- "Existe uso de ferramentas manuais motorizadas (martelete, lixadeira)?" → SIM
- "Qual o tempo diário de uso contínuo?"
- "Existe rodízio de função para limitar exposição?"

Regras do Motor:
SE ferramenta.tipo = "manual_motorizada" E atividade.uso_continuo = VERDADEIRO
ENTÃO adicionar risco RF-0004
E solicitar tempo_exposicao_diaria

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação
- PGR

Referências:
- NR-15, Anexo 8
- NHO-10 (Fundacentro)

Versão: 1.0
```

---

## RF-0005 — Radiação Não-Ionizante (Arco Elétrico de Soldagem)

```
ID: RF-0005
Categoria: Físico
Perigo: Exposição à Radiação Não-Ionizante (UV/IV do arco elétrico)

Descrição Técnica:
Radiação ultravioleta e infravermelha emitida pelo arco elétrico durante
soldagem. Risco associado direto às atividades já catalogadas em RQ-0045
(fumos de solda) — mesma atividade gera dois perigos distintos (químico e
físico) que precisam ser tratados juntos no motor de decisão.

Base Legal: NR-15, Anexo 7

Atividades:
- Soldagem MIG/MAG
- Soldagem TIG
- Soldagem com eletrodo revestido
- Corte a plasma

CNAEs:
- 2511-0/00, 2932-0/01, 4120-4/00 (mesmas de RQ-0045)

Funções:
- Soldador
- Auxiliar de soldagem

Máquinas:
- Máquina de solda MIG/MAG, TIG, eletrodo revestido
- Máquina de corte a plasma

Consequências:
- Ceratoconjuntivite actínica ("vista de arco" / "flash de solda")
- Queimaduras de pele (radiação IV)
- Lesões oculares cumulativas em exposição crônica sem proteção

Hierarquia de Controle:
1-2. Eliminação/Substituição — não aplicável
3. Engenharia — biombos de isolamento (protege terceiros no entorno)
4. Administrativo — sinalização de área de solda ativa
5. EPI — máscara de solda com viseira de tonalidade adequada ao processo

EPIs:
- Máscara de solda com filtro de tonalidade adequada (auto-escurecimento
  recomendado)
- Avental de raspa, mangote (proteção de pele contra IV)

EPCs:
- Biombos de isolamento da área de soldagem

Treinamentos:
- Seleção correta de tonalidade de viseira conforme processo/amperagem
- NR-12 (se aplicável ao equipamento)

Perguntas Condicionais:
- "Existe processo de soldagem?" → SIM (mesma pergunta-gatilho de RQ-0045)
- "Há biombos isolando a área de outros trabalhadores?"

Regras do Motor:
SE atividade = "soldagem" (qualquer processo)
ENTÃO adicionar risco RF-0005 JUNTO COM RQ-0045
(uma atividade → múltiplos perigos de categorias diferentes)

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação
- PGR
- Ordem de Serviço

Referências:
- NR-15, Anexo 7

Versão: 1.0
```

---

## Status deste volume

**5 de ~100 registros planejados para Riscos Físicos.** Nota importante de
engenharia: RF-0005 confirma que a tabela `atividade_perigo` já suporta
1:N corretamente — "Soldagem MIG" vai gerar RQ-0045 (químico) E RF-0005
(físico) simultaneamente, sem precisar de lógica especial no motor.

**Próximos da fila:** pressão hiperbárica (trabalho em ar comprimido/mergulho),
radiação ionizante (raio-X industrial), frio artificial (câmara frigorífica),
umidade excessiva.
