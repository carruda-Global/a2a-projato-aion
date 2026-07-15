# 04 - Motor de Decisão NR1 AI

## Objetivo

Transformar as respostas do questionário em regras técnicas para geração
automática dos documentos.

## Fluxo

Questionário → Validação → Banco de Conhecimento → Regras → Inventário →
Plano de Ação → PGR

## Estrutura da Regra

SE `<condição>`{=html} ENTÃO `<ação>`{=html}

### Exemplo 1

SE existir soldagem ENTÃO - adicionar perigo: fumos metálicos -
categoria: químico - verificar exaustão - verificar respirador -
verificar treinamento - gerar item no Inventário

### Exemplo 2

SE existir ruído ENTÃO - adicionar agente físico - solicitar intensidade
quando aplicável - recomendar controles de engenharia - recomendar
protetor auricular

### Exemplo 3

SE existir trabalho em altura (\>2 m) ENTÃO - aplicar requisitos da
NR-35 - gerar APR - verificar treinamento - verificar sistema de
proteção contra quedas

## Prioridade de Controles

1.  Eliminar
2.  Substituir
3.  Engenharia
4.  Administrativo
5.  EPI

## Saídas

-   Inventário
-   Plano de Ação
-   PGR
-   Ordem de Serviço
-   APR (quando aplicável)

## Regras Gerais

-   Não gerar documentos contraditórios.
-   Toda ação deve ter origem em uma regra.
-   Registrar versão da regra aplicada.
