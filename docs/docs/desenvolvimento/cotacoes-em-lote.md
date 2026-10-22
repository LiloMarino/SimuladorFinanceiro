# Cotações em lote

O mercado e os minigráficos buscam os preços de todos os ativos em uma consulta
por operação, com corte na data da partida. O banco aproveita o índice primário
de `stock_price_history`, em `(stock_id, price_date, version)`, para buscar a última
cotação ou os últimos fechamentos de cada ativo.

## Por que a consulta foi alterada

Antes, cada leitura listava os ativos e executava outra consulta para cada um.
Com 50 ativos, eram 51 consultas para as cotações e outras 51 para os minigráficos.
Na cotação diária, o `.first()` do resultado também não aplicava `LIMIT` no SQL:
o banco enviava o histórico anterior ao dia e o código aproveitava a primeira linha.

Agora, um `JOIN LATERAL` com `ORDER BY price_date DESC LIMIT 1` encontra a cotação
de cada ativo. Nos minigráficos, o limite é a janela pedida, e a consulta externa
reordena os fechamentos cronologicamente. O `LEFT JOIN` preserva ativos sem preço
como listas vazias; a cotação diária continua omitindo ativos sem histórico disponível.

Essa abordagem limita as linhas devolvidas por ativo e permite uma busca curta pelo
índice, evitando numerar todo o histórico para selecionar uma janela pequena. Não foi necessário
criar um índice duplicado nem alterar o schema. A consulta do último preço importado
também recebeu `LIMIT 1` no SQL.

## Medição local

Ensaio de 21/10/2026, em Windows, Python 3.14.2, SQLAlchemy 2.1.4 e PostgreSQL 18.6.
Base sintética com 50 ativos e 6.000 datas por ativo, totalizando 300.000 preços.
Mesma base, uma chamada de aquecimento e cinco repetições de cada implementação.
Os valores abaixo são medianas da chamada ao repositório, incluindo conversão para DTO
e finalização da sessão. A versão anterior veio da revisão `16eaa880`, posterior à
publicação da versão 2.1.0, já com o versionamento das séries. O ensaio usa a versão
comum; a quantidade de cópias congeladas pode mudar o custo de filtrar cada busca.

| Leitura | Consultas antes → depois | Mediana antes | Mediana depois |
| --- | --- | --- | --- |
| Última cotação até a data | 51 → 1 | 1.821,949 ms | 3,287 ms |
| Últimos 30 fechamentos | 51 → 1 | 28,155 ms | 4,462 ms |

Os resultados completos das duas versões foram comparados e eram iguais nesse ensaio.
O `EXPLAIN ANALYZE` confirmou busca reversa no índice primário do histórico: uma linha
por ativo nas cotações e 30 por ativo nos minigráficos. O tempo de execução no banco foi
respectivamente 1,148 ms e 1,434 ms, além do processamento da aplicação.

Esses números medem as leituras de mercado nesse conjunto sintético; não são uma
medição do tick inteiro nem uma garantia de velocidade para qualquer partida.

## Leituras repetidas durante a partida

O motor guarda o catálogo de nomes e classes dos ativos por instância de simulação,
reutilizando-o na carteira e na apuração e prévia de IR. O mercado também reutiliza
a classificação por setor já guardada no motor. A Central só altera esses dados
fora de uma partida ativa, e uma nova instância recarrega o catálogo.

Preços e saldos não receberam esse cache: continuam refletindo as leituras e
operações da partida. As variações do candle são montadas pelo mesmo método do DTO
na lista de mercado e no detalhe do ativo, preservando o contrato da API.

As duas consultas aplicam `seen_by` dentro da busca limitada: a cópia congelada da
partida substitui a linha comum da mesma data, e datas sem cópia continuam usando
a série comum. São preservadas tanto a escolha explícita de `simulation_id` quanto
a versão da partida ativa quando o argumento é omitido. O limite vem depois desse
filtro, para não duplicar dias nem deixar versões de outras partidas ocuparem a janela.

## Verificação de regressão

Com `POSTGRES_DATABASE_URL` apontando para um servidor de teste, execute:

```bash
uv run pytest tests/test_stock_quotes.py tests/test_simulation_engine.py tests/test_price_impact.py
```

A suíte cria bancos descartáveis. Os testes de cotações verificam:

- uma consulta por operação com um e com 50 ativos;
- ausência de preços posteriores à data pedida;
- finais de semana, fim do histórico e base vazia;
- janelas por ativo, ordem cronológica, listas vazias e fechamento zero;
- abertura zero e variação negativa;
- consistência entre lista, detalhe e último ponto do minigráfico;
- versões comum, congelada e ativa, sem duplicar datas ou misturar partidas;
- importação considerando apenas preços reais da versão comum;
- reutilização do catálogo e sua recarga numa nova simulação.

Para investigar outros custos da partida, use o [painel de desempenho](./investigando-lentidao.md).
O número de consultas de preço deixou de crescer com a quantidade de ativos, mas
snapshots, histórico de operações e notificações continuam compondo o custo do tick.
