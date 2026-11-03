---
sidebar_position: 9
---

# Investigando lentidão

Quando a partida trava ou o tempo anda mais devagar que o pedido, o caminho é: **ligar o modo debug**, achar **qual ponto** gasta o tempo no painel Desempenho e, só então, olhar **dentro** dele com um perfil (rota, motor ou `py-spy`). Nada disso muda código nem manda dados para fora da máquina.

## 1. Ligar o modo debug

O painel só existe com o servidor em modo debug, decidido ao subir (veja [Modo debug](./setup#modo-debug)). Feche o app e abra de novo com `--debug`, ou ponha `enabled = true` em `[debug]` no `config.toml`. Só o host vê o item **Desempenho** no menu: as medições são do servidor dele.

## 2. Ler o painel Desempenho

O app mede sozinho e guarda as **últimas 1.000 medições de cada item**, em memória (reiniciar o app zera, e **Zerar medições** serve para medir só um trecho). A tela se atualiza a cada 2 s, e **Pausar** congela a tabela para dar tempo de ler.

| Origem | O que é medido |
| --- | --- |
| **HTTP** | Cada requisição, agrupada pela rota declarada (`/api/stocks/{ticker}`, não o ticker). |
| **Socket.IO** | Quanto o servidor leva para tratar cada evento recebido do navegador. |
| **Motor** | Quanto leva para processar **um dia** da partida e, dentro dele, cada **etapa** do dia (preços e impacto, renda fixa, bots, aporte e crédito, governo, imposto, notícias, snapshots, publicar o dia, meta, resumos e conquistas). |

A tabela mostra, para cada linha: chamadas, tempo total, médio, **p95** e máximo. Ela vem ordenada pelo **tempo total**, porque o que mais soma tempo é o que vale investigar primeiro.

### O que é o p95

É o tempo que 95% das chamadas não passam: só as 5% piores levam mais. Média de 20 ms com p95 de 400 ms quer dizer que a rota quase sempre é rápida, mas **de vez em quando trava**, e é isso que o jogador sente.

- **lenta**: p95 acima de 500 ms (o mesmo corte do `slow.log`).
- **trava às vezes**: p95 de dez vezes a média ou mais.

### O motor e a velocidade

Na velocidade `N×` cada dia tem `1000 / N` ms para ser processado (a 10×, 100 ms). Se o motor leva mais que isso, a partida **não roda na velocidade pedida**: o cartão fica vermelho e diz a velocidade real, por exemplo "roda a ~22×".

As linhas **(parte de Processar um dia)** são as etapas do dia. Cada uma já está dentro do tempo do dia, por isso não entra na soma da coluna de fatia: se o dia leva 400 ms e **Bots e estratégias** leva 100 ms, os bots são um quarto do dia. A etapa **Publicar o dia** é o pedaço gasto montando e enviando os eventos para os jogadores. As etapas que só rodam uma vez por mês (resumos, parte de aporte e crédito) mostram p95 alto perto da média: quase todos os dias custam zero e o pico é o dia da virada.

### O que vai para o navegador

Cada evento que o servidor envia pesa em três lugares: no servidor, que monta a mensagem (a linha **Publicar o dia** acima); na fila de saída, onde a mensagem espera o servidor ter tempo de entregá-la; e no navegador, que recebe e redesenha. A tabela tem uma linha por evento (`stock_update:PETR4` e `stock_update:VALE3` viram `stock_update:*`), em dois grupos de colunas:

- **Agora** (últimos 10 s): mensagens e bytes por segundo. Com a partida pausada nada sai e elas mostram "—", mas a linha continua.
- **Desde que zerou**: fica até reiniciar o app ou clicar **Zerar medições**.
  - **Envios**: quantas vezes o servidor publicou o evento. Um envio vira uma mensagem para cada jogador inscrito.
  - **Sem ninguém**: envios que ninguém recebeu, com o percentual sobre a coluna Envios ("120 · 3%" de 4.330 envios). O servidor montou a mensagem à toa; perto de 0% está bom.
  - **Total**: bytes somados de todos os jogadores. É a coluna que diz qual evento mais pesa no navegador.
  - **Típico** e **p95** do tamanho, sobre os últimos 1.000 envios. Típico é a mediana: metade das mensagens é menor. Acima de 100 KB, saindo ao menos uma vez por segundo, fica em laranja: é a primeira suspeita de tela travando.
  - **Atraso p95**: quanto 95% das mensagens esperam entre o servidor decidir enviar e a entrega à conexão do jogador, sobre as últimas 1.000. Até umas dezenas de ms está ótimo; na casa das centenas, a tela fica para trás da partida.
  - **Último**: a hora em que o evento saiu pela última vez.

## 3. Outras pistas

- **`Server-Timing`**: com o debug ligado, toda resposta HTTP traz esse cabeçalho com o tempo do servidor. Abra a aba **Rede** (F12) do navegador e veja a coluna de tempo da resposta. Um 500 tratado pelo servidor não traz o cabeçalho, mas entra na medição.
- **`logs/slow.log`**: qualquer chamada acima de 500 ms (HTTP, evento ou dia do motor) vai para esse arquivo, com a rota e o tempo.
- **`logs/app.log`** e os arquivos por área ganham o `DEBUG` do app no modo debug (veja [Logs](./logs.md)). O SQL só entra com `sql = true` em `[debug]`, no `database.log`.

## 4. Olhando dentro do ponto caro

O painel diz **qual** ponto gasta o tempo; as ferramentas abaixo dizem **qual função, dentro dele**. Todas valem só com o modo debug ligado.

### Perfil das rotas (interruptor no painel)

Ligue o interruptor do cartão **Perfil das rotas** e use o jogo normalmente: cada requisição às rotas da API vira um perfil do [`yappi`](https://github.com/sumerc/yappi), gravado em `profiles/<método>-<rota>-<hora>.prof`. Cada rota guarda as **3 requisições mais lentas**: uma requisição rápida nunca empurra uma lenta para fora, e a que fica abaixo das 3 nem chega ao disco. O cartão mostra uma linha por rota, da mais lenta em diante, com a média dessas 3 e, para cada uma, a duração e o comando para abrir o perfil. Essa média é a do pior caso da rota; o tempo de sempre dela está na tabela **Tempo gasto por rota ou evento**. As rotas do próprio painel (`/api/debug/...`) ficam de fora, para não ocuparem a lista. O perfil cobre só o handler da rota: o que a rota chama (`build_*`, consultas) aparece, o uvicorn não.

Abra o arquivo no `snakeviz`, que mostra o tempo de cada função em blocos clicáveis:

```bash
pnpm profile:view profiles/get-api-stats-....prof
```

### Perfil do motor (botão no painel)

O cartão **Perfil do motor** grava o motor por quanto tempo você quiser e salva `profiles/motor-<hora>.prof` ao parar. Deixe a partida rodando alguns dias no ritmo que trava e pare. Com a partida pausada nenhum dia roda, e o painel avisa que não há o que gravar.

:::note Cada perfil tem só o que é dele
O servidor roda o motor, as rotas e o event loop no mesmo processo, e o `yappi` conta as funções de todos eles. Cada chamada sai carimbada com uma etiqueta: a da requisição perfilada, a da thread do motor enquanto grava ou nenhuma. O perfil de uma rota guarda só as chamadas daquela requisição, e o do motor só as do motor. Por isso dá para gravar o motor e as rotas ao mesmo tempo, e duas requisições simultâneas não se misturam.
:::

**Como ler o perfil:** o relógio é o **de parede**: o tempo que a função levou de verdade, inclusive esperando o banco responder. Uma rota de 800 ms que espera 700 ms pelo SQL mostra esses 700 ms dentro da consulta, que é onde estão. O `yappi` registra cada chamada de função e por isso **atrasa o programa**, em geral algumas vezes. As **proporções** entre as funções valem (se `build_snapshot` ocupa 40% do perfil, ele pesa perto disso no jogo), mas os **milissegundos** não: para tempo real, use o painel ou o `pnpm profile:match`.

### O py-spy

O [`py-spy`](https://github.com/benfred/py-spy) grava o que o processo Python está fazendo **enquanto roda**, sem alterar o código, e gera um **gráfico de chamas**. Ele custa muito menos que o `yappi` e separa as threads (`--threads`), mas só amostra: funções muito rápidas podem não aparecer.

1. Ele já vem no grupo de desenvolvimento (`uv sync`): rode com `uv run py-spy`.
2. Pegue o número do processo. O cartão "Achou o ponto caro?" do painel já traz o comando pronto com o PID certo (botão **Copiar**):

   ```bash
   uv run py-spy record --pid 18432 --threads -o perfil.svg
   ```

3. Repita a lentidão por uns 30 s no jogo e pare com `Ctrl+C`.
4. Abra o `perfil.svg` no navegador. **Quanto mais larga a barra, mais tempo a função gastou**; o que está em cima chama o que está embaixo.

:::note Permissões
No Windows o `py-spy` anexou a um processo do mesmo usuário sem precisar de administrador. No Linux ele pode pedir `sudo` (ou `kernel.yama.ptrace_scope = 0`). Se ele não reconhecer o interpretador dentro do executável, rode o app pelo código-fonte (`uv run python main.py --debug`) e anexe a esse processo.
:::

## 5. Medindo uma partida longa sem abrir o jogo

`pnpm profile:match` roda os dias do motor direto, sem dormir entre eles e sem Socket.IO, numa partida de rascunho que apaga ao fim. É o antes e o depois repetível de uma mudança de desempenho.

```bash
pnpm profile:match --days 1000 --bots 5
```

Como grava no banco, o padrão é o **banco de teste** (`POSTGRES_TEST_DATABASE_URL` no `.env`); `--database current` usa o banco do ambiente. `--source <nome ou id>` copia as regras, os jogadores e as estratégias de uma partida salva (sem tocá-la), e `--profile` grava também o perfil do motor em `profiles/`.

A saída traz, para cada etapa do dia, a **mediana** e o **p95** dos primeiros e dos últimos dias (50 de cada, por padrão) e a **razão** entre as duas medianas:

- **Mediana**: o valor do meio. Com dias de 10, 11, 12, 900 e 10,5 ms, a mediana é 11 ms: o dia travado de 900 ms não a distorce, ao contrário da média.
- **p95**: o tempo que 95% dos dias não passam (veja [O que é o p95](#o-que-é-o-p95)).
- **Razão**: mediana do fim dividida pela do começo. Perto de **1,0** o dia custa o mesmo no dia 1.000 que no dia 1: bom. **3,0** quer dizer que o dia ficou três vezes mais lento com o passar da partida, e é o sinal de que alguma etapa cresce com o histórico.

## Próximos Passos

- [Configuração TOML e modo debug](./setup#modo-debug)
- [Diretrizes Async vs Sync](./async-vs-sync.md): onde costuma estar o gargalo de uma rota lenta
