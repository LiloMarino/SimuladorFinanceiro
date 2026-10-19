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
| **Motor** | Quanto leva para processar **um dia** da partida. |

A tabela mostra, para cada linha: chamadas, tempo total, médio, **p95** e máximo. Ela vem ordenada pelo **tempo total**, porque o que mais soma tempo é o que vale investigar primeiro.

### O que é o p95

É o tempo que 95% das chamadas não passam: só as 5% piores levam mais. Média de 20 ms com p95 de 400 ms quer dizer que a rota quase sempre é rápida, mas **de vez em quando trava**, e é isso que o jogador sente.

- **lenta**: p95 acima de 500 ms (o mesmo corte do `slow.log`).
- **trava às vezes**: p95 de dez vezes a média ou mais.

### O motor e a velocidade

Na velocidade `N×` cada dia tem `1000 / N` ms para ser processado (a 10×, 100 ms). Se o motor leva mais que isso, a partida **não roda na velocidade pedida**: o cartão fica vermelho e diz a velocidade real, por exemplo "roda a ~22×".

### O que vai para o navegador

Eventos enviados pelo servidor não gastam tempo dele, gastam **volume**: mensagens por segundo, KB por segundo e tamanho de cada mensagem. É o que pesa no navegador em velocidade alta, porque a 100× o volume fica 10 vezes maior. Uma mensagem pesada e frequente (como `stocks_update`) é a primeira suspeita.

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
