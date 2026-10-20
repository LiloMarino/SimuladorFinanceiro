---
sidebar_position: 10
---

# Logs

O app escreve em dois lugares com papéis diferentes: o **terminal**, que é a tela de status de quem roda o servidor, e os **arquivos de log**, que guardam o histórico para investigar depois. Uma mensagem só aparece no terminal se foi escrita para ele; todo o resto fica nos arquivos.

## O que aparece no terminal

- O bloco de abertura, uma vez: banco em uso, interfaces de rede detectadas (LAN e VPN), URL local, pasta de configurações e logs (no executável) e "modo debug ligado".
- O que explica uma espera ou muda o banco: extração do PostgreSQL e criação do banco na primeira abertura, e migrações aplicadas.
- Todo aviso (`WARNING`) e erro, em **uma linha** com horário, nível e área. O traceback completo não vai ao terminal: a linha aponta para o `error.log`.
- "Aplicação finalizada" ao encerrar.

O terminal **nunca** mostra `DEBUG` nem SQL, nem no modo debug.

## Arquivos de log

Ficam na pasta de logs (`logs_path` em `[logging]` do `config.toml`). Cada linha vai ao `app.log` e, se for de uma área, também ao arquivo dela. Cada arquivo roda a 10 MB e guarda 5 cópias.

| Arquivo | O que guarda |
| --- | --- |
| `app.log` | Tudo, em ordem cronológica, exceto o SQL |
| `error.log` | Só `ERROR` e `CRITICAL`, com o traceback |
| `simulation.log` | Partida, motor, ordens e corretoras (renda variável e fixa) |
| `realtime.log` | WebSocket e Socket.IO |
| `import.log` | Importação de dados (yfinance, CSV, indicadores) |
| `database.log` | Banco, migrations e, com `[debug] sql = true`, o SQL |
| `slow.log` | Chamadas acima de 500 ms (só com o modo debug; veja [Investigando lentidão](./investigando-lentidao.md)) |

Área nova é uma linha em `AREA_LOGGERS`, em `backend/core/logger.py`. Os logs do túnel/rede, do login e entrada de jogadores e das ordens foram avaliados para ganhar arquivo próprio e ficaram de fora: depois da limpeza somam poucas linhas, e as ordens já caem no `simulation.log`.

## Níveis: normal e modo debug

| | Modo normal | Modo debug |
| --- | --- | --- |
| Código do app (`backend.*`) | `INFO` | `DEBUG` |
| Bibliotecas (`sqlalchemy`, `engineio`, `socketio`, `urllib3`, `asyncio`) | `WARNING` | `WARNING` |
| Requisições HTTP (uma linha por chamada) | não aparecem | `app.log`, nunca no terminal |
| Terminal | abertura, avisos e erros | igual |
| SQL | não aparece | só com `[debug] sql = true`, só no `database.log` |

O `DEBUG` do app é o rastro do que ele faz: ordem recebida, cancelada e casada, dia simulado, conexão de WebSocket, importação por ticker e cada requisição HTTP (método, rota e status). Ele só existe nos arquivos. O `logging_level` e o `[database] echo_sql` do `config.toml` não existem mais; se estiverem num arquivo antigo, são ignorados.

O SQL é a parte mais volumosa: cada tick da simulação faz dezenas de consultas. Por isso ele fica atrás de uma chave própria, e só vale com o modo debug ligado:

```toml
[debug]
enabled = true
sql = true
```

### Custo

Medido em isolamento (micro-benchmark da escrita, sem o motor rodando): uma linha `DEBUG` do app custa cerca de 84 µs (vai ao `app.log` e ao arquivo da área) e uma linha de SQL cerca de 57 µs. Um dia simulado com uns 10 logs `DEBUG` soma menos de 1 ms. Com o SQL ligado, dezenas de consultas por dia somam alguns milissegundos, o que só pesa em velocidades muito altas. Não foi preciso tirar a escrita da thread do motor (`QueueHandler`).

## Como escrever um log

- Mensagem em português, formatada com `%s` e não com f-string: `logger.debug("Ordem casada: %sx %s", qty, ticker)`. A f-string monta o texto mesmo com o nível desligado.
- Nome do logger = módulo: `logging.getLogger(__name__)`.
- `logger.exception` só dentro de `except`: ele grava o traceback.
- Para a mensagem aparecer no terminal: `logger.info("...", extra=TERMINAL)` (`TERMINAL` vem de `backend/core/logger.py`). Sem isso, só `WARNING` ou acima chega lá.
- No front, `logger` de `shared/lib/logger.ts`: `debug` e `log` só aparecem com o modo debug; `warn` e `error` sempre.

## Decisões log a log

Frequência: "uma vez" (na abertura ou no encerramento), "partida", "tick" (por dia simulado), "evento" (por ordem, requisição ou conexão), "lote" (por ticker ou série importados).

| Área | Log | Frequência | Destino e nível |
| --- | --- | --- | --- |
| Abertura | Banco em uso, interfaces de rede, URL local, pasta de configs, modo debug | uma vez | terminal + `app.log`, `INFO` |
| Abertura | Extração do PostgreSQL, criação do banco, migração aplicada | uma vez | terminal + `database.log`, `INFO` |
| Abertura | Backup antes da migration, banco marcado na revisão, `Conectado ao PostgreSQL` | uma vez | arquivo, `INFO` |
| Abertura | Falha de migration, DLL ausente | uma vez | terminal + `error.log`, `CRITICAL` |
| Abertura | Nenhuma interface LAN/VPN, frontend não encontrado | uma vez | terminal + `app.log`, `WARNING` |
| Partida | Iniciada, pausada, retomada, fim, velocidade alterada | partida | `simulation.log`, `INFO` |
| Partida | Dia simulado | tick | `simulation.log`, `DEBUG` |
| Partida | Aguardando a thread encerrar | partida | `simulation.log`, `DEBUG` |
| Partida | Erro fatal no loop | partida | terminal + `error.log`, `CRITICAL` com traceback |
| Ordens | Ordem recebida, cancelamento recebido, ordem casada | evento | `simulation.log`, `DEBUG` |
| Ordens | Compra/venda executada, investido, resgate | evento | `simulation.log`, `DEBUG` |
| Jogadores | Entrou, saiu, logout | evento | `app.log`, `INFO` |
| Tempo real | Cliente WS conectado, desconectado, inscrito | evento | `realtime.log`, `DEBUG` |
| Tempo real | Conexão WS recusada (sem client_id) | evento | terminal + `realtime.log`, `WARNING` |
| Importação | Ativo criado, registros inseridos por ticker | lote | `import.log`, `INFO` |
| Importação | Download, leitura do CSV, ticker já atualizado, série sem busca | lote | `import.log`, `DEBUG` |
| Importação | Ticker sem dado, falha de download ou de CSV | lote | terminal + `import.log`/`error.log`, `WARNING`/`ERROR` |
| Rede | Comando de detecção com erro | abertura | `app.log`, `DEBUG` |
| Erros | Exceção não tratada numa rota | evento | terminal (uma linha) + `error.log`, `ERROR` |
| Requisições | Método, rota e status de cada chamada HTTP | evento | `app.log`, só no modo debug |
| SQL | Consultas do SQLAlchemy | evento | `database.log`, só com `[debug] sql = true` |
| Lentidão | Chamada acima de 500 ms | evento | `slow.log`, `WARNING`, só com o modo debug |

A dica de firewall do host foi para a página de [Multiplayer](../como-usar/multiplayer.md#amigos-não-conseguem-entrar): uma orientação fixa serve melhor num manual do que repetida a cada abertura, e a chave `show_firewall_hint` deixou de existir.
