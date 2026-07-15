# 02 - Banco de Conhecimento NR1 AI

Versão 1.0

> Documento de especificação técnica do banco de conhecimento utilizado
> pelo NR1 AI.

# 1. Objetivo

O Banco de Conhecimento (Knowledge Base) é o núcleo técnico da
plataforma.

Nenhum documento será elaborado por respostas livres da IA.

Todo conteúdo deverá ser produzido a partir de regras estruturadas e
registros técnicos previamente cadastrados.

------------------------------------------------------------------------

# 2. Arquitetura Conceitual

``` text
Perguntas do usuário
        │
        ▼
Motor de Regras
        │
        ▼
Banco de Conhecimento
        │
        ├── Perigos
        ├── Agentes de risco
        ├── Medidas de controle
        ├── EPIs
        ├── EPCs
        ├── Treinamentos
        ├── Referências normativas
        └── Documentos relacionados
        │
        ▼
Geradores de documentos
```

------------------------------------------------------------------------

# 3. Entidades Principais

## 3.1 Perigo

Campos mínimos:

-   ID
-   Nome
-   Categoria
-   Descrição
-   Fonte geradora
-   Exemplos de atividades
-   Consequências
-   Agentes relacionados
-   Referências normativas
-   Status (ativo/inativo)
-   Versão

Categorias:

-   Físico
-   Químico
-   Biológico
-   Ergonômico
-   Acidentes

------------------------------------------------------------------------

## 3.2 Agente de Risco

Campos:

-   ID
-   Nome
-   Tipo
-   Descrição
-   Forma de exposição
-   Limites aplicáveis (quando existirem)
-   Métodos de avaliação
-   Necessidade de avaliação qualitativa ou quantitativa

------------------------------------------------------------------------

## 3.3 Medidas de Controle

Aplicar sempre a hierarquia de controles:

1.  Eliminação
2.  Substituição
3.  Controles de engenharia
4.  Medidas administrativas
5.  EPI

Cada medida conterá:

-   ID
-   Descrição
-   Prioridade
-   Efetividade esperada
-   Custo estimado (opcional)

------------------------------------------------------------------------

## 3.4 EPI

Campos:

-   Nome
-   Finalidade
-   CA
-   Observações de uso
-   Riscos atendidos
-   Treinamentos associados

------------------------------------------------------------------------

## 3.5 EPC

Campos:

-   Nome
-   Aplicação
-   Riscos mitigados
-   Observações

------------------------------------------------------------------------

## 3.6 Treinamentos

Campos:

-   Nome
-   Norma relacionada
-   Periodicidade
-   Público-alvo
-   Conteúdo mínimo

------------------------------------------------------------------------

# 4. Estrutura de Relacionamentos

Cada perigo poderá possuir:

-   vários agentes de risco;
-   vários EPIs;
-   vários EPCs;
-   vários treinamentos;
-   vários documentos gerados.

------------------------------------------------------------------------

# 5. Exemplo de Registro

## Perigo

Nome: Ruído ocupacional

Categoria: Físico

Atividades:

-   Operação de compressores
-   Marcenaria
-   Metalurgia
-   Produção industrial

Consequências:

-   Perda auditiva
-   Estresse
-   Dificuldade de comunicação

Medidas de controle:

-   Enclausuramento
-   Manutenção preventiva
-   Redução da exposição
-   Protetor auricular

Documentos gerados:

-   Inventário de Riscos
-   Plano de Ação
-   PGR

------------------------------------------------------------------------

# 6. Motor de Busca

O banco deverá permitir consultas por:

-   CNAE
-   Setor
-   Função
-   Máquina
-   Produto químico
-   Atividade
-   Palavra-chave
-   Categoria do risco

------------------------------------------------------------------------

# 7. Versionamento

Cada registro deverá possuir:

-   versão;
-   data de criação;
-   data da última revisão;
-   autor;
-   histórico de alterações.

------------------------------------------------------------------------

# 8. Fontes Técnicas

O banco de conhecimento deverá ser alimentado exclusivamente com
referências técnicas verificadas.

Fontes prioritárias:

-   NR-1
-   Demais Normas Regulamentadoras aplicáveis
-   ABNT (quando pertinente)
-   Manuais de fabricantes
-   FISPQ/SDS de produtos químicos
-   Literatura técnica reconhecida

------------------------------------------------------------------------

# 9. Regras Gerais

1.  Não criar perigos inexistentes.
2.  Não recomendar medidas incompatíveis com a atividade.
3.  Não gerar documentos contraditórios.
4.  Toda recomendação deve estar vinculada a um registro do banco.
5.  A IA não poderá inventar requisitos legais.

------------------------------------------------------------------------

# 10. Roadmap do Banco de Conhecimento

Fase 1 - 300 perigos catalogados

Fase 2 - 800 atividades

Fase 3 - 1.500 máquinas e equipamentos

Fase 4 - 2.000 produtos químicos

Fase 5 - Base completa de EPIs, EPCs e treinamentos

------------------------------------------------------------------------

# Próximo Documento

03 - Questionário Inteligente

Objetivo: Definir toda a árvore de decisão utilizada pelo sistema para
entrevistar o usuário de forma adaptativa e coletar apenas as
informações necessárias para elaboração do GRO/PGR.
