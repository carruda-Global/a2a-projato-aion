# Banco Mestre de Riscos — Riscos Químicos — Parte 01

Base regulatória: NR-15, Anexos 11 (agentes químicos com limite de tolerância),
12 (poeiras minerais) e 13 (avaliação qualitativa). Um agente que consta no
Anexo 11 ou 12 não pode ser classificado no Anexo 13 (são mutuamente exclusivos).

Fontes: [NR-15 Anexo 11](https://www.unifal-mg.edu.br/progepe/wp-content/uploads/sites/144/2021/09/NR-15-Anexo-11_-Agentes-Quimicos-por-Limite-de-Tolerancia.pdf), [Guia Trabalhista NR-15](https://www.guiatrabalhista.com.br/legislacao/nr/nr15.htm)

---

## RQ-0043 — Poeira de Madeira

```
ID: RQ-0043
Categoria: Químico
Perigo: Exposição à Poeira de Madeira (serragem)

Descrição Técnica:
Partículas sólidas geradas no corte, lixamento e aplainamento de madeira.
Classificado como carcinógeno humano (Grupo 1, IARC) para poeira de madeira dura.
Avaliação qualitativa conforme NR-15 Anexo 13 quando não há limite de tolerância
quantitativo estabelecido para o tipo específico de madeira.

Base Legal: NR-15, Anexo 13

Atividades:
- Serragem
- Lixamento
- Aplainamento
- Furação em madeira

CNAEs:
- 1610-2/01 (Serrarias)
- 1622-6/02 (Fabricação de esquadrias de madeira)
- 3101-2/00 (Fabricação de móveis)

Funções:
- Marceneiro
- Operador de serra circular
- Lixador
- Carpinteiro

Máquinas:
- Serra circular
- Serra de fita
- Lixadeira de cinta
- Plaina

Consequências:
- Rinite alérgica
- Asma ocupacional
- Câncer nasossinusal (madeiras duras, exposição prolongada)
- Dermatite de contato

Hierarquia de Controle:
1. Eliminação — não aplicável (processo produtivo essencial)
2. Substituição — não aplicável
3. Engenharia — exaustão localizada na fonte, enclausuramento de máquinas
4. Administrativo — rodízio de função, pausas, limpeza a úmido (não varrer a seco)
5. EPI — respirador PFF2, óculos de proteção

EPIs:
- Respirador PFF2 (CA obrigatório)
- Óculos de proteção ampla visão
- Luvas de proteção mecânica

EPCs:
- Sistema de exaustão localizada (captor próximo à fonte)
- Enclausuramento de serras e lixadeiras

Treinamentos:
- NR-12 (segurança em máquinas, se operar equipamento)
- Uso correto de EPI respiratório
- Procedimento de limpeza a úmido

Perguntas Condicionais:
- "Existe corte, lixamento ou aplainamento de madeira?" → SIM
- "As máquinas possuem sistema de exaustão?" → SIM/NÃO
- "A limpeza é feita a seco ou úmido?"

Regras do Motor:
SE atividade = "corte_madeira" OU "lixamento_madeira"
ENTÃO adicionar risco RQ-0043
E adicionar pergunta "sistema_exaustao_presente"
E SE exaustão = NÃO ENTÃO nível_risco += 1

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação
- PGR
- Ordem de Serviço (uso de EPI respiratório)

Referências:
- NR-15, Anexo 13
- IARC Monograph Vol. 100C (Wood dust)

Versão: 1.0
```

---

## RQ-0044 — Tolueno (solvente orgânico)

```
ID: RQ-0044
Categoria: Químico
Perigo: Exposição a Vapores de Tolueno

Descrição Técnica:
Solvente orgânico volátil amplamente usado em tintas, vernizes, colas e
processos de limpeza industrial. Consta no Anexo 11 da NR-15 com limite de
tolerância quantitativo estabelecido (avaliação por medição, não qualitativa).

Base Legal: NR-15, Anexo 11, Quadro 1

Atividades:
- Pintura industrial
- Aplicação de vernizes
- Colagem/laminação
- Limpeza com solvente

CNAEs:
- 2022-0/00 (Fabricação de tintas)
- 3101-2/00 (Fabricação de móveis — acabamento)
- 2932-0/01 (Fabricação de peças e acessórios para veículos)

Funções:
- Pintor industrial
- Operador de cabine de pintura
- Auxiliar de produção (acabamento)

Máquinas:
- Cabine de pintura
- Pistola de pintura

Consequências:
- Depressão do sistema nervoso central (tontura, cefaleia)
- Irritação de mucosas e vias respiratórias
- Dermatite de contato
- Exposição crônica: efeitos neurológicos e hepáticos

Hierarquia de Controle:
1. Eliminação — não aplicável
2. Substituição — tintas à base de água quando tecnicamente viável
3. Engenharia — cabine de pintura com exaustão e filtragem
4. Administrativo — controle de tempo de exposição, monitoramento biológico
5. EPI — respirador com cartucho para vapores orgânicos

EPIs:
- Respirador semifacial com cartucho para vapores orgânicos (CA obrigatório)
- Luvas de proteção química (nitrílica)
- Óculos de proteção química
- Avental impermeável

EPCs:
- Cabine de pintura com exaustão forçada
- Sistema de ventilação geral diluidora

Treinamentos:
- Manuseio seguro de produtos químicos (FISPQ)
- Uso e troca de cartucho de respirador
- Resposta a derramamento

Perguntas Condicionais:
- "Existe uso de tintas, vernizes ou solventes à base de tolueno?" → SIM
- "Há cabine de pintura com exaustão?" → SIM/NÃO
- "É realizado monitoramento biológico (ácido hipúrico urinário)?"

Regras do Motor:
SE produto_quimico.tipo = "solvente_organico" E produto_quimico.cas = "108-88-3"
ENTÃO adicionar risco RQ-0044
E classificar Anexo 11 (avaliação quantitativa obrigatória)
E solicitar FISPQ do produto

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação
- PGR
- Ficha de monitoramento biológico (referência PCMSO)

Referências:
- NR-15, Anexo 11, Quadro 1
- FISPQ do produto conforme NBR 14725

Versão: 1.0
```

---

## RQ-0045 — Fumos de Solda (Manganês)

```
ID: RQ-0045
Categoria: Químico
Perigo: Exposição a Fumos Metálicos de Solda (Manganês)

Descrição Técnica:
Partículas metálicas geradas na fusão do eletrodo/arame durante processos de
soldagem (MIG/MAG, eletrodo revestido). O manganês presente nos fumos é
neurotóxico em exposição crônica. Avaliação quantitativa conforme Anexo 11.

Base Legal: NR-15, Anexo 11, Quadro 1

Atividades:
- Soldagem MIG/MAG
- Soldagem com eletrodo revestido
- Corte a plasma

CNAEs:
- 2511-0/00 (Fabricação de estruturas metálicas)
- 2932-0/01 (Fabricação de peças para veículos)
- 4120-4/00 (Construção de edifícios — estruturas metálicas)

Funções:
- Soldador
- Auxiliar de soldagem
- Montador de estruturas metálicas

Máquinas:
- Máquina de solda MIG/MAG
- Máquina de solda eletrodo revestido
- Máquina de corte a plasma

Consequências:
- Manganismo (síndrome neurológica similar ao Parkinson)
- Febre dos fumos metálicos
- Pneumoconiose (siderose)
- Irritação respiratória aguda

Hierarquia de Controle:
1. Eliminação — não aplicável (processo essencial)
2. Substituição — processos com menor geração de fumos quando viável
3. Engenharia — exaustão localizada tipo "tocha de sucção" ou braço articulado
4. Administrativo — rodízio, monitoramento de manganês urinário/sanguíneo
5. EPI — respirador adequado (PFF2 ou PAPR conforme concentração)

EPIs:
- Respirador PFF2 ou PAPR com filtro para partículas (CA obrigatório)
- Máscara de solda com viseira adequada (radiação/faísca — risco associado)
- Avental de raspa, luvas de raspa (proteção térmica associada)

EPCs:
- Exaustão localizada na fonte (braço articulado ou tocha de sucção)
- Ventilação geral do ambiente de soldagem
- Biombos de isolamento (também reduz exposição de terceiros)

Treinamentos:
- NR-12 (máquinas e equipamentos)
- NR-18/35, se aplicável ao contexto (construção civil / altura)
- Uso correto de EPI respiratório em soldagem

Perguntas Condicionais:
- "Existe processo de soldagem?" → SIM
- "Qual o processo? (MIG/MAG, eletrodo revestido, TIG)"
- "Existe sistema de exaustão localizada na solda?" → SIM/NÃO
- "É feito monitoramento biológico de manganês?"

Regras do Motor:
SE atividade = "soldagem"
ENTÃO adicionar risco RQ-0045 (fumos metálicos)
E adicionar risco associado "radiação não-ionizante" (arco elétrico)
E SE exaustão_localizada = NÃO ENTÃO nível_risco += 1
E solicitar tipo_processo_solda

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação
- PGR
- Ordem de Serviço

Referências:
- NR-15, Anexo 11, Quadro 1
- ACGIH TLV para Manganês e compostos

Versão: 1.0
```

---

## RQ-0046 — Chumbo e seus Compostos

```
ID: RQ-0046
Categoria: Químico
Perigo: Exposição ao Chumbo Inorgânico

Descrição Técnica:
Metal pesado com toxicidade sistêmica cumulativa. Presente em processos de
fundição, reciclagem de baterias, pintura com tintas antigas (à base de
chumbo) e soldagem de componentes eletrônicos com liga de chumbo/estanho.

Base Legal: NR-15, Anexo 11, Quadro 1 (também sujeito a controle médico
específico conforme NR-7/PCMSO — plumbemia)

Atividades:
- Fundição de chumbo
- Reciclagem de baterias automotivas
- Remoção de tintas antigas (retrofit predial)
- Soldagem eletrônica (liga estanho-chumbo)

CNAEs:
- 2451-2/00 (Fundição de ferro e aço) — quando aplicável a ligas com chumbo
- 3830-1/99 (Recuperação de materiais — reciclagem de baterias)
- 2790-2/99 (Fabricação de outros equipamentos elétricos)

Funções:
- Operador de fundição
- Reciclador de baterias
- Soldador eletrônico
- Pintor (retrofit de estruturas antigas)

Máquinas:
- Forno de fundição
- Estação de solda eletrônica

Consequências:
- Saturnismo (intoxicação crônica por chumbo)
- Anemia
- Neuropatia periférica
- Efeitos reprodutivos (especial atenção a trabalhadoras gestantes — NR-1
  exige afastamento de gestantes de atividades insalubres em grau máximo)

Hierarquia de Controle:
1. Eliminação — substituição por ligas sem chumbo (solda eletrônica lead-free)
2. Substituição — tintas modernas sem chumbo
3. Engenharia — exaustão localizada em fundição, ventilação em solda
4. Administrativo — controle de plumbemia periódico (PCMSO), rodízio
5. EPI — respirador adequado, vestimenta de troca (não levar para casa)

EPIs:
- Respirador com filtro para partículas P3 (CA obrigatório)
- Luvas de proteção química
- Vestimenta de trabalho exclusiva (não sair da empresa com a roupa)

EPCs:
- Exaustão localizada na fonte
- Vestiário com dupla via (limpo/sujo) para evitar contaminação cruzada
- Chuveiro de emergência e lava-olhos

Treinamentos:
- Manuseio seguro de chumbo e compostos
- Higiene pessoal ocupacional (não comer/fumar no posto de trabalho)
- Procedimento de descontaminação

Perguntas Condicionais:
- "Existe manuseio de chumbo, solda com liga de chumbo ou tintas antigas?" → SIM
- "É realizado controle de plumbemia (exame de sangue)?" → SIM/NÃO
- "Há gestantes ou lactantes na função?" → afastamento obrigatório se insalubridade grau máximo

Regras do Motor:
SE produto_quimico.contem_chumbo = VERDADEIRO
ENTÃO adicionar risco RQ-0046
E marcar restrição_gestante = VERDADEIRO
E solicitar exame_plumbemia_periodico

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação
- PGR
- PCMSO (referência cruzada — controle biológico obrigatório)

Referências:
- NR-15, Anexo 11, Quadro 1
- NR-7 (PCMSO) — indicadores biológicos de exposição ao chumbo

Versão: 1.0
```

---

## RQ-0047 — Amianto (Asbesto)

```
ID: RQ-0047
Categoria: Químico
Perigo: Exposição a Fibras de Amianto

Descrição Técnica:
Mineral fibroso historicamente usado em telhas, isolamentos térmicos e freios.
Uso e comercialização proibidos no Brasil desde 2017 (Lei 9.055/1995 e ADI
3937/STF), mas o risco permanece relevante em **reformas, demolições e
manutenção de edificações antigas** que contenham materiais com amianto
já instalados.

Base Legal: NR-15, Anexo 12 (poeiras minerais); Lei 9.055/1995

Atividades:
- Demolição de coberturas antigas (telha cimento-amianto)
- Remoção de isolamento térmico antigo
- Manutenção predial em edificações pré-2017

CNAEs:
- 4120-4/00 (Construção de edifícios — reforma/demolição)
- 4329-1/03 (Obras de instalação de isolamento térmico)

Funções:
- Demolidor
- Pedreiro (reforma)
- Técnico de manutenção predial

Máquinas:
- Ferramentas manuais de demolição (evitar corte com disco — gera fibras
  respiráveis; procedimento correto é remoção úmida sem fragmentação)

Consequências:
- Asbestose
- Mesotelioma pleural (câncer raro e agressivo, associado especificamente
  ao amianto)
- Câncer de pulmão
- Latência de 15-40 anos entre exposição e doença

Hierarquia de Controle:
1. Eliminação — não trabalhar com material sem laudo prévio de identificação
2. Substituição — não aplicável (material já instalado, não é substituído,
   é removido com procedimento especial)
3. Engenharia — remoção por empresa especializada, umidificação do material,
   isolamento da área
4. Administrativo — laudo de identificação obrigatório antes de qualquer
   intervenção em edificação anterior a 2017
5. EPI — respirador PFF3 ou PAPR (nunca PFF1/PFF2 para amianto)

EPIs:
- Respirador PFF3 ou PAPR (obrigatório — fibras respiráveis de alto risco)
- Vestimenta descartável tipo Tyvek
- Luvas descartáveis

EPCs:
- Isolamento total da área de remoção
- Umidificação do material antes de qualquer manipulação
- Descontaminação na saída da área isolada

Treinamentos:
- Identificação de materiais com amianto (MCA)
- Procedimento de remoção segura (NBR 15575 e normas correlatas)
- Uso de EPI de nível de proteção elevado

Perguntas Condicionais:
- "A edificação é anterior a 2017?" → SIM/NÃO
- "Existe telha ou material de isolamento com suspeita de amianto?" → SIM
- "Foi feito laudo de identificação de MCA (Material Contendo Amianto)?"
- ATENÇÃO: se resposta = SIM e não houver laudo, sistema deve BLOQUEAR
  geração de plano de ação até identificação formal

Regras do Motor:
SE edificacao.ano_construcao < 2017 E atividade = "demolicao" OU "reforma"
ENTÃO perguntar "suspeita_amianto"
SE suspeita_amianto = SIM E laudo_mca = NÃO
ENTÃO bloquear_geracao_documento E alertar "Laudo de identificação de
amianto obrigatório antes de prosseguir"

Documentos Gerados:
- Inventário de Riscos
- Plano de Ação (com exigência de laudo prévio)
- PGR
- Alerta de bloqueio (caso não haja laudo)

Referências:
- Lei 9.055/1995
- NR-15, Anexo 12
- ADI 3937/STF (proibição do amianto crisotila)

Versão: 1.0
```

---

## Status deste volume

**5 de ~150+ registros planejados para Riscos Químicos.** Cobertos até aqui:
poeira de madeira, solvente orgânico (tolueno), fumos de solda (manganês),
chumbo, amianto — escolhidos por serem os agentes químicos mais frequentes
em atividades de construção civil e indústria no Brasil (o público-alvo
principal do NR1 AI).

**Próximos da fila (Riscos Químicos):** sílica cristalina (RQ-0042, já usado
como exemplo pelo usuário), gases de combustão (CO), ácidos/bases em
limpeza industrial, isocianatos (tintas PU), formaldeído, benzeno em
combustíveis, óleos minerais (fluido de corte).
