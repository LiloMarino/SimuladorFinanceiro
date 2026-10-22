# Ordenação das tabelas

Clique no cabeçalho de uma coluna para ordenar do menor para o maior; clique
novamente para inverter. Texto segue a comparação em português, com números
naturais no nome (`ATIVO2` antes de `ATIVO10`). Dinheiro, quantidade, percentuais e
datas usam os valores originais da API, antes da formatação. Valores ausentes ficam
no fim nos dois sentidos e empates mantêm a ordem recebida.

A escolha fica no estado de cada tabela e é reaplicada quando os dados chegam ou
mudam durante a partida. Navegar para outra página pode reiniciar essa escolha.
As respostas guardadas no cache da API não são modificadas pela ordenação.

## Cobertura

- Mercado, ofertas de renda fixa, carteira de ações e de títulos.
- Ordens abertas e negócios executados.
- Rankings de jogadores e equipes, métricas dos relatórios, exposição por setor e
  tabelas das métricas que compõem a nota.
- Histórico do viver de renda.
- Séries importadas, matriz de correlação, desempenho e tráfego do servidor.
- Tabelas de referência da temperatura e do choque de inflação, em ajuda que abre
  por clique e aceita interação pelo teclado.

Equipes e seus membros continuam juntos: os grupos são ordenados pelo valor da
equipe, quando existe, e os jogadores são ordenados dentro de cada grupo. A
colocação oficial continua sendo a calculada pelo critério da partida.

Na matriz de correlação, os dois eixos acompanham a ordenação. As células continuam
apontando para os índices originais da resposta, inclusive o par selecionado. O
Ibovespa permanece na linha de referência e também pode ordenar os ativos.

No mercado, **Faixa do dia** ordena pela amplitude entre máxima e mínima; **30
dias** ordena pelo retorno entre o primeiro e o último fechamento do minigráfico.
Nas taxas de renda fixa, **Rentabilidade** e **Taxa** ordenam a taxa do contrato;
**Equivale hoje** usa a taxa anual equivalente retornada pelo servidor.

## Histórico paginado

`GET /api/simulation/life-history` aceita `sort_by` (`date`, `type`, `description`,
`amount`, `cash`) e `sort_direction` (`asc`, `desc`). O padrão continua sendo data
decrescente. O servidor filtra e ordena todo o histórico antes de aplicar `offset`
e `limit`; a contagem por categoria não muda com a ordenação.

Coluna e direção fazem parte da chave do cache. Durante a troca, a tabela indica
que está carregando e desabilita carregar mais registros, evitando misturar páginas
de ordens diferentes.

## Validação desta alteração

- Backend: 627 testes aprovados; 3 do pacote embarcado pulados por ausência dos
  arquivos empacotados. Inclui ordenação global antes da paginação, negativos,
  valores ausentes, filtros e rejeição de parâmetros inválidos na rota real.
- Frontend: 102 testes aprovados; TypeScript, ESLint e build verificados numa cópia
  isolada das fontes atuais com as dependências já instaladas e aprovadas do commit
  `16eaa880` (TypeScript 6 e Vite 8.3.4).
- Navegador: componentes reais com dados de teste; preços `9,90`, `20,50`, `100,00`
  nos dois sentidos, atualização das cotações mantendo a escolha, teclado, grupos
  de equipes, ordenação antes de mostrar dez linhas, seleção na matriz e tabela
  de ajuda. Console sem erros ou avisos nesses cenários.

O check geral da raiz encontra violações preexistentes em `.plugin-build`, fora do
jogo. Ruff limitado às fontes do jogo e pyright passam. A instalação local do
frontend com o lockfile atual está incompleta porque a política de idade mínima
bloqueou pacotes recentes; por isso a validação isolada não confirma essas versões
mais novas. O OpenAPI foi gerado pelo backend e os tipos foram regenerados com o
`openapi-typescript` disponível na cópia de validação. Nenhuma política de instalação
ou arquivo de dependências foi alterado.
