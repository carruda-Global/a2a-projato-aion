# 03 - Questionário Inteligente NR1 AI

Versão 1.0

> Especificação técnica do mecanismo de entrevista adaptativa utilizado
> pelo NR1 AI.

# 1. Objetivo

O Questionário Inteligente tem como finalidade coletar somente as
informações necessárias para elaboração da documentação da NR-1,
reduzindo perguntas desnecessárias e garantindo consistência.

Princípios: - Perguntas condicionais. - Fluxo adaptativo. - Registro
estruturado. - Validação de respostas. - Possibilidade de retomada da
entrevista.

------------------------------------------------------------------------

# 2. Fluxo Geral

``` text
Login
 ↓
Nova Empresa
 ↓
Cadastro Inicial
 ↓
Questionário Base
 ↓
Motor de Decisão
 ↓
Perguntas Condicionais
 ↓
Validação
 ↓
Banco de Dados
 ↓
Inventário de Riscos
 ↓
Plano de Ação
 ↓
PGR
```

------------------------------------------------------------------------

# 3. Etapas da Entrevista

## Etapa 1 - Identificação da Empresa

Campos:

-   Razão Social
-   Nome Fantasia
-   CNPJ
-   CNAE principal
-   CNAEs secundários
-   Endereço
-   Município
-   Estado
-   CEP
-   Telefone
-   E-mail
-   Responsável legal
-   Número de empregados
-   Horário de funcionamento

Validações: - CNPJ válido. - CNAE obrigatório. - Número de empregados
maior que zero.

------------------------------------------------------------------------

## Etapa 2 - Estrutura Física

Perguntas:

-   Quantos setores existem?
-   Existe produção?
-   Existe escritório?
-   Existe almoxarifado?
-   Existe manutenção?
-   Existe laboratório?
-   Existe cozinha?
-   Existe área externa?
-   Existem áreas restritas?

Cada setor será cadastrado individualmente.

------------------------------------------------------------------------

## Etapa 3 - Setores

Para cada setor:

-   Nome
-   Área aproximada
-   Quantidade de trabalhadores
-   Atividades executadas
-   Turnos
-   Supervisor responsável

------------------------------------------------------------------------

## Etapa 4 - Funções

Para cada função:

-   Cargo
-   Descrição das atividades
-   Setor
-   Quantidade de colaboradores
-   Jornada
-   Uso de EPI
-   Necessidade de treinamento

------------------------------------------------------------------------

## Etapa 5 - Máquinas e Equipamentos

Perguntas:

-   Existem máquinas?
-   Quantas?
-   Fabricante
-   Modelo
-   Potência
-   Operador
-   Proteções existentes
-   Manutenção preventiva

Se "Não", ocultar todo o bloco.

------------------------------------------------------------------------

## Etapa 6 - Produtos Químicos

Perguntas:

-   Utiliza produtos químicos?
-   Quais?
-   Possui FISPQ?
-   Forma de armazenamento?
-   Forma de utilização?
-   Funcionários expostos?

------------------------------------------------------------------------

## Etapa 7 - Identificação dos Perigos

Categorias:

### Físicos

-   Ruído
-   Vibração
-   Calor
-   Frio
-   Radiação
-   Umidade

### Químicos

-   Poeiras
-   Fumos
-   Névoas
-   Vapores
-   Gases

### Biológicos

-   Vírus
-   Bactérias
-   Fungos
-   Material contaminado

### Ergonômicos

-   Repetitividade
-   Postura
-   Esforço físico
-   Levantamento de cargas

### Acidentes

-   Quedas
-   Choques elétricos
-   Máquinas
-   Incêndio
-   Explosão
-   Trânsito interno

------------------------------------------------------------------------

# 4. Motor de Perguntas Condicionais

Exemplo:

``` text
Existe produção?
  ├── Não → seguir para escritório.
  └── Sim
        ↓
Existe soldagem?
  ├── Não → ocultar bloco soldagem.
  └── Sim
        ↓
Existe exaustão localizada?
        ↓
Existe uso de respirador?
        ↓
Existe medição ambiental?
```

Outro exemplo:

``` text
Existe trabalho em altura?
  ├── Não → finalizar bloco.
  └── Sim
        ↓
Altura superior a 2 metros?
        ↓
Existe sistema de ancoragem?
        ↓
Há treinamento?
```

------------------------------------------------------------------------

# 5. Validação das Respostas

O sistema deverá impedir:

-   campos obrigatórios vazios;
-   respostas incompatíveis;
-   duplicidade de registros;
-   CNAE inválido;
-   funções sem setor;
-   máquinas sem localização.

------------------------------------------------------------------------

# 6. Indicadores de Progresso

Durante a entrevista:

-   Percentual concluído.
-   Quantidade de pendências.
-   Campos obrigatórios restantes.
-   Estimativa de tempo.

------------------------------------------------------------------------

# 7. Salvamento

Após cada etapa:

-   salvar automaticamente;
-   permitir retomada;
-   registrar usuário;
-   registrar data e hora.

------------------------------------------------------------------------

# 8. Resultado da Entrevista

Ao concluir:

O sistema deverá produzir um conjunto estruturado de dados para
alimentar:

-   Inventário de Riscos;
-   Plano de Ação;
-   PGR;
-   Ordem de Serviço;
-   APR (quando aplicável).

Nenhum documento será gerado diretamente a partir das respostas. Todos
dependerão do Motor de Decisão e do Banco de Conhecimento.

------------------------------------------------------------------------

# 9. Requisitos de Interface

-   Navegação por etapas.
-   Barra de progresso.
-   Ajuda contextual.
-   Campos de busca.
-   Upload de fotos.
-   Upload de documentos.
-   Responsividade para telas de notebook e desktop.

------------------------------------------------------------------------

# 10. Próximo Documento

04 - Motor de Decisão

Objetivo:

Especificar todas as regras que transformam as respostas do usuário em
perigos, riscos, medidas de controle, documentos e ações automáticas.
