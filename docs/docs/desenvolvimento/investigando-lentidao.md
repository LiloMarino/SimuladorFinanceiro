---
sidebar_position: 9
---

# Investigando lentidão

Quando a partida trava ou o tempo anda mais devagar que o pedido, o caminho é: **ligar o modo debug**, achar **qual ponto** gasta o tempo no painel Desempenho e, só então, olhar **dentro** dele com o `py-spy`. Nada disso muda código nem manda dados para fora da máquina.

## 1. Ligar o modo debug

O painel só existe com o servidor em modo debug, decidido ao subir (veja [Modo debug](./setup#modo-debug)). Feche o app e abra de novo com `--debug`, ou ponha `enabled = true` em `[debug]` no `config.toml`. Só o host vê o item **Desempenho** no menu: as medições são do servidor dele.

## 2. Ler o painel Desempenho

O app mede sozinho e guarda as **últimas 1.000 medições de cada item**, em memória (reiniciar o app zera, e **Zerar medições** serve para medir só um trecho). A tela se atualiza a cada 2 s, e **Pausar** congela a tabela para dar tempo de ler.

| Origem | O que é medido |
| --- | --- |
| **HTTP** | Cada requisição, agrupada pela rota declarada (`/api/stocks/{ticker}`, não o ticker). |
| **Socket.IO** | Quanto o servidor leva para tratar cada evento recebido do navegador. |
| **Motor** | Quanto leva para processar **um dia** da partida e, dentro dele, para **publicar o dia** (montar e enviar os eventos do fim do dia). |

A tabela mostra, para cada linha: chamadas, tempo total, médio, **p95** e máximo. Ela vem ordenada pelo **tempo total**, porque o que mais soma tempo é o que vale investigar primeiro.

### O que é o p95

É o tempo que 95% das chamadas não passam: só as 5% piores levam mais. Média de 20 ms com p95 de 400 ms quer dizer que a rota quase sempre é rápida, mas **de vez em quando trava**, e é isso que o jogador sente.

- **lenta**: p95 acima de 500 ms (o mesmo corte do `slow.log`).
- **trava às vezes**: p95 de dez vezes a média ou mais.

### O motor e a velocidade

Na velocidade `N×` cada dia tem `1000 / N` ms para ser processado (a 10×, 100 ms). Se o motor leva mais que isso, a partida **não roda na velocidade pedida**: o cartão fica vermelho e diz a velocidade real, por exemplo "roda a ~22×".

A linha **Publicar o dia (parte de Processar um dia)** é o pedaço do dia gasto montando e enviando os eventos para os jogadores. Ela já está dentro do tempo do dia, por isso não entra na soma da coluna de fatia: se o dia leva 400 ms e publicar leva 100 ms, publicar é um quarto do dia.

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

## 4. Olhando dentro do ponto caro com o py-spy

O [`py-spy`](https://github.com/benfred/py-spy) grava o que o processo Python está fazendo **enquanto roda**, sem alterar o código, e gera um **gráfico de chamas**.

1. Instale (uma vez): `uv tool install py-spy` ou `pip install py-spy`.
2. Pegue o número do processo. O cartão "Achou o ponto caro?" do painel já traz o comando pronto com o PID certo (botão **Copiar**):

   ```bash
   py-spy record --pid 18432 -o perfil.svg
   ```

3. Repita a lentidão por uns 30 s no jogo e pare com `Ctrl+C`.
4. Abra o `perfil.svg` no navegador. **Quanto mais larga a barra, mais tempo a função gastou**; o que está em cima chama o que está embaixo.

:::note Permissões
No Linux o `py-spy` pode pedir `sudo` (ou `kernel.yama.ptrace_scope = 0`) para anexar a um processo que já roda. No Windows, rode o terminal como administrador se ele recusar. Se o `py-spy` não reconhecer o interpretador dentro do executável, rode o app pelo código-fonte (`uv run python main.py --debug`) e anexe a esse processo.
:::

## Próximos Passos

- [Configuração TOML e modo debug](./setup#modo-debug)
- [Diretrizes Async vs Sync](./async-vs-sync.md): onde costuma estar o gargalo de uma rota lenta
