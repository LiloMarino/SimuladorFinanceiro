<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Última mudança (2026-10-08):** M1 concluído (F1 e F2); registrada a D6.

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | F4 | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | F6 | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | F1, F2 | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | F8, F9, F10 | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | F11 | — |
| **N6** | Comparar resultados de simulações diferentes | F12 | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | F13 | — |
| **D4** | Banco de dados embarcado no executável | F4 | 🔍 |
| **D5** | Onde roda o código de estratégia escrito pelo usuário | F8 | 🔍 |
| **F3** | Spike: banco embarcado no executável | — | 🔍 |
| **F4** | Executável sobe sem banco instalado | — | ⏳ |
| **F5** | Spike: provider de túnel pela internet | — | 🔍 |
| **F6** | Link de convite pela internet no lobby | — | ⏳ |
| **F7** | Spike: estratégia Python escrita pelo usuário | — | 🔍 |
| **F8** | Modo automático: estratégia do jogador roda a cada tick | — | ⏳ |
| **F9** | Estratégias prontas de exemplo | — | ⏳ |
| **F10** | Guia de como escrever uma estratégia | — | ⏳ |
| **F11** | Métricas de risco do desempenho | — | ⏳ |
| **F12** | Comparação entre simulações | — | ⏳ |
| **F13** | Impacto de preço de ordens grandes | — | ⏳ |
| **F14** | Janela desktop nativa | — | 💤 |

<details>
<summary><strong>Concluído / decidido / descartado (7 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | F2, F11 | ✅ |
| **D2** | Cálculo financeiro acontece só no backend; o frontend exibe | F2, F11, F12 | ✅ |
| **D3** | Dinheiro e quantidade trafegam como Decimal serializado em string | F1 | ✅ |
| **D6** | A retomada continua no dia seguinte ao último evento | F2 | ✅ |
| **F1** | Decimal como string do backend ao frontend | — | ✅ |
| **F2** | Renda fixa com cálculo único no backend e retomada consistente | — | ✅ |
| **F15** | Cliente desktop em Tauri | — | 🚫 |

</details>

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: as `F#` que podem ser pegas agora — toda dependência já ✅. "Destrava" é quantas `F#` em aberto esperam por ela, direta ou indiretamente; é por aí que a tabela está ordenada. 💤 (sem prioridade) e 🚫 não entram.

| ID | Resumo | Marco | Destrava | Status |
| --- | --- | --- | --- | --- |
| **F7** | Spike: estratégia Python escrita pelo usuário | M4 | 3 | 🔍 |
| **F3** | Spike: banco embarcado no executável | M2 | 1 | 🔍 |
| **F5** | Spike: provider de túnel pela internet | M3 | 1 | 🔍 |
| **F11** | Métricas de risco do desempenho | M5 | 0 | ⏳ |
| **F12** | Comparação entre simulações | M5 | 0 | ⏳ |
| **F13** | Impacto de preço de ordens grandes | — | 0 | ⏳ |

---

## 🧭 Marcos

### M1 — Números confiáveis

> **Objetivo:** O que aparece na tela é o que está no banco, e retomar uma simulação dá o mesmo resultado que rodar direto.
>
> **Serve:** N3
>
> **Progresso:** 2/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| — | *(nada em aberto)* | — | — |

<details><summary>Concluído (2 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| **F1** | Decimal como string do backend ao frontend | — | ✅ |
| **F2** | Renda fixa com cálculo único no backend e retomada consistente | — | ✅ |

</details>

### M2 — Baixar e jogar

> **Objetivo:** Abrir o executável numa máquina limpa e chegar ao lobby sem instalar nada.
>
> **Serve:** N1
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| **F3** | Spike: banco embarcado no executável | — | 🔍 |
| **F4** | Executável sobe sem banco instalado | F3 | ⏳ |

### M3 — Multiplayer pela internet

> **Objetivo:** Convidar um amigo de fora da rede local mandando só um link.
>
> **Serve:** N2
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| **F5** | Spike: provider de túnel pela internet | — | 🔍 |
| **F6** | Link de convite pela internet no lobby | F5 | ⏳ |

### M4 — Estratégias automáticas

> **Objetivo:** Escrever ou escolher uma estratégia e deixar o simulador operar com ela.
>
> **Serve:** N4
>
> **Progresso:** 0/4 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| **F7** | Spike: estratégia Python escrita pelo usuário | — | 🔍 |
| **F8** | Modo automático: estratégia do jogador roda a cada tick | F7 | ⏳ |
| **F9** | Estratégias prontas de exemplo | F8 | ⏳ |
| **F10** | Guia de como escrever uma estratégia | F8 | ⏳ |

### M5 — Análise de desempenho

> **Objetivo:** Ver o risco por trás do retorno e comparar simulações lado a lado.
>
> **Serve:** N5, N6
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| **F11** | Métricas de risco do desempenho | — | ⏳ |
| **F12** | Comparação entre simulações | — | ⏳ |

### Sem marco

> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| **F13** | Impacto de preço de ordens grandes | — | ⏳ |
| **F14** | Janela desktop nativa | — | 💤 |

---

## 1. Atende necessidade

| ID | Resumo | Atende (N#) | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F1** | Decimal como string do backend ao frontend | N3 | D3 | M1 | — | Médio | Médio | Alto | Bom | ✅ Concluído |
| **F2** | Renda fixa com cálculo único no backend e retomada consistente | N3 | D1, D2, D6 | M1 | — | Alto | Alto | Alto | Bom | ✅ Concluído |
| **F4** | Executável sobe sem banco instalado | N1 | D4 | M2 | F3 | Médio | Médio | Alto | Excelente | ⏳ Pendente |
| **F6** | Link de convite pela internet no lobby | N2 | — | M3 | F5 | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F8** | Modo automático: estratégia do jogador roda a cada tick | N4 | D5 | M4 | F7 | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F9** | Estratégias prontas de exemplo | N4 | — | M4 | F8 | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F10** | Guia de como escrever uma estratégia | N4 | — | M4 | F8 | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F11** | Métricas de risco do desempenho | N5 | D1, D2 | M5 | — | Médio | Baixo | Alto | Excelente | ⏳ Pendente |
| **F12** | Comparação entre simulações | N6 | D2 | M5 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F13** | Impacto de preço de ordens grandes | N7 | — | — | — | Alto | Alto | Médio | Médio | ⏳ Pendente |

**F1 — Decimal como string do backend ao frontend.** Origem: #86. O `BaseDTO` deixou de converter `Decimal` para `float`, e o Pydantic serializa como string; os DTOs de dinheiro, quantidade monetária e taxa (carteira, posições, renda fixa, simulação, indicadores, eventos realtime de caixa e execução) e os requests de valor passaram a `Decimal`. O motor guarda caixa e posições em `Decimal`; preço de ação continua `float` na origem (`StockPriceHistory` é `Double`) e vira `Decimal` pelo texto (`to_money`) onde entra no caixa ou num evento. No front, `displayMoney`/`displayPercent`/`displayMoneyCompact` formatam a string direto pelo `Intl` (lib `ES2023.Intl`), e os requests mandam a string digitada. A conta da tela de Carteira subiu para o backend: o `PortfolioDTO` traz totais, alocação e rentabilidade prontos, o histórico patrimonial virou `/api/portfolio/history`, e `portfolio_update` substitui a carteira a cada tick. Limitações: `build-ranking.ts` e o gráfico de desempenho ainda fazem conta com `parseFloat` (sobem com a F12); a pizza da carteira soma no front os itens visíveis (interação do gráfico); o compacto do eixo passou a usar o sufixo pt-BR ("mil", "mi").
**Aceite:** todo valor exibido bate com o `NUMERIC(20,6)` do banco em todas as casas que a tela mostra.

**F2 — Renda fixa com cálculo único no backend e retomada consistente.** Origem: #85. `features/fixed_income/accrual.py` é a única fórmula: taxa efetiva (prefixado = taxa; CDI = CDI × percentual; IPCA+/SELIC+ composto, `(1 + índice) × (1 + spread) − 1`), fator diário `(1 + taxa)^(1/252)`, tabela regressiva de IR e resgate arredondado ao centavo. O tick ao vivo (`accrue`, idempotente por dia), a reconstrução e a projeção aplicam a mesma sequência de multiplicações em `Decimal`. Ao carregar, as posições são reconstruídas dos eventos BUY/REDEEM (D1), e as de ações também, repetindo compras e vendas com a mesma `Position`. A retomada segue a D6, sem reaplicar o aporte do mês, e o caixa reconstruído passou a somar os aportes. As posições de renda fixa são indexadas pelo `asset_uuid`, não pelo nome. `GET /api/fixed-income/{uuid}/projection` alimenta a tela de detalhe, e o front parou de projetar juros. Limitações: os indicadores (CDI, IPCA, SELIC) ainda são constantes em `EconomicRepository`, então a projeção do pós-fixado só coincide com o realizado enquanto continuarem constantes; o IR de vários aportes no mesmo título usa a data do primeiro.
**Aceite:** um prefixado comprado e levado ao vencimento credita o mesmo valor, ao centavo, rodando direto ou pausando e retomando no meio — e esse valor é igual à projeção mostrada no dia da compra (coberto em `tests/test_fixed_income_accrual.py` e verificado ponta a ponta: projeção R$ 12.778,14, resgate R$ 12.778,14 após parar e retomar).

**F4 — Executável sobe sem banco instalado.** Serve N1. Na primeira execução o executável cria o banco sozinho numa pasta de dados do usuário (ex.: `%APPDATA%/SimuladorFinanceiro`), sem `.env` obrigatório; `database.py` deixa de falhar quando `POSTGRES_DATABASE_URL` não existe. O motor é o que a D4 decidir. A página de instalação dos docs e o README perdem a etapa de instalar o Postgres. Gatilho: assim que a F3 fechar a D4.
**Aceite:** numa máquina sem Postgres, baixar o release e abrir o executável leva ao lobby sem nenhum passo extra.

**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada.

**F8 — Modo automático: estratégia do jogador roda a cada tick.** Origem: #2, #12, #14. Hoje `SimulationEngine.set_strategy` guarda uma estratégia só para o engine inteiro; ela passa a ser por jogador (`client_id` → estratégia), com `ManualStrategy` (já é no-op) como padrão. Cada tick chama `next()` da estratégia de cada jogador antes do flush de eventos. A página de Estratégias (hoje um mock que retorna 501) vira real: escolher a estratégia, ativar e desativar (a alternância manual ↔ automático da #14) e ver o log das ordens que ela emitiu. Onde a estratégia roda e quem pode carregá-la segue a D5. Gatilho: F7 concluída.

**F9 — Estratégias prontas de exemplo.** As três do mock atual de `strategies.tsx`, implementadas como subclasses da classe base com parâmetros editáveis na UI: cruzamento de médias móveis de 50 e 200 dias, RSI (compra abaixo de 30, vende acima de 70) e rompimento de máxima com volume. Servem para jogar no automático sem escrever código e como exemplo para o guia da F10.

**F10 — Guia de como escrever uma estratégia.** Origem: #49. Página no Docusaurus (grupo "Como Usar"): a classe base, quais métodos o usuário implementa e quais já vêm prontos, o que acontece em cada tick, uma das estratégias da F9 comentada linha a linha, e as limitações (bibliotecas disponíveis no executável, tempo máximo por tick, regra de multiplayer da D5). Gatilho: F8 concluída — a API da classe base só fica estável depois dela.

**F11 — Métricas de risco do desempenho.** Origem: #5 (a #22 foi fechada, mas drawdown e Sharpe não existem no código). Calculadas no backend (D2) a partir dos snapshots diários (D1), descontando os aportes do dia para que o salário mensal não pareça rendimento:
- **Drawdown máximo:** a maior queda do patrimônio a partir de um pico, antes de recuperá-lo. Ex.: o patrimônio sobe a R$ 15.000 e cai a R$ 12.000 → drawdown de 20%. Quanto menor, melhor; acima de ~30% é uma queda que a maioria das pessoas não aguenta sem vender.
- **Volatilidade anual:** quanto o patrimônio sobe e desce de um dia para o outro, em média (desvio-padrão dos retornos diários × √252 dias úteis). Ex.: ~1% ao ano é renda fixa; ~25% é uma carteira só de ações.
- **Índice de Sharpe:** quanto retorno acima do CDI a carteira entregou por unidade de volatilidade = (retorno anual − CDI anual) ÷ volatilidade anual. Ex.: retorno de 18%, CDI de 10%, volatilidade de 16% → Sharpe 0,5. Abaixo de 0 perdeu para o CDI; perto de 1 é bom; acima de 2 é raro. O CDI vem da série de indicadores econômicos que já existe.

Na tela de Estatísticas, cada métrica ganha uma descrição curta ao lado e um tooltip com a definição e como ler.
**Aceite:** numa série sintética com pico de R$ 15.000 e vale de R$ 12.000, a API retorna drawdown de 20,00%.

**F12 — Comparação entre simulações.** Origem: #84. Tela nova "Comparar Simulações", aberta por um botão com ícone próprio: uma sidebar lista as simulações salvas (o histórico já existe) com um checkbox em cada, e o gráfico é o mesmo da tela de Estatísticas, com uma série por jogador e simulação nomeada `Nick#Simulação` (ex.: `Lilo#Simulação-1`, `Lilo#Simulação-2`). Como `#` passa a ser separador, o registro de jogador passa a recusar `#` no nickname. Os números da comparação vêm prontos do backend (D2), o que puxa para o backend o cálculo de ranking que hoje mora em `build-ranking.ts`.

**F13 — Impacto de preço de ordens grandes.** Origem: #59. Uma ordem executada desloca o preço do ativo proporcionalmente ao tamanho dela em relação ao volume médio negociado (modelo de raiz quadrada: impacto = k × √(quantidade ÷ volume médio diário)), e o deslocamento decai até zero em T dias pela curva (1 − t/T)² — cai rápido no começo e zera de verdade em T, como a issue pede. T (15 a 30 dias) e k ficam no TOML. O preço exibido e o usado pelo matching engine passam a ser OHLCV × (1 + soma dos impactos ativos). Convive com a liquidez e o market maker que já existem (#60), que hoje limitam a ordem mas não mexem nos preços futuros.

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |

**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

---
## 3. Descartada

| ID | Resumo | N# | Status |
| --- | --- | --- | --- |
| **F15** | Cliente desktop em Tauri | — | 🚫 Descartado |

**F15 — Descartado.** 🚫 O núcleo do Tauri é Rust: o backend Python iria como sidecar (o executável do PyInstaller dentro do pacote Tauri), o que dá dois executáveis, toolchain Rust nas três plataformas da CI e um WebView diferente em cada SO. O ganho — janela própria em vez de aba do navegador — é o mesmo da F14, que faz isso em Python dentro do executável atual. Electron daria o mesmo resultado com ~150 MB de Chromium a mais. Em qualquer dos dois, os convidados do multiplayer continuam no navegador.

---
## 4. Incerta / exploratória

| ID | Resumo | Conexão | Marco | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| **F3** | Spike: banco embarcado no executável | Serve N1; decide D4 | M2 | — | 🔍 Em avaliação |
| **F5** | Spike: provider de túnel pela internet | Serve N2; escolhe o provider da F6 | M3 | — | 🔍 Em avaliação |
| **F7** | Spike: estratégia Python escrita pelo usuário | Serve N4; decide D5 | M4 | — | 🔍 Em avaliação |

**F3 — Spike: banco embarcado no executável.** Decide a D4. Falta medir as três opções finalistas com o executável real: (1) aumento de tamanho do `.exe` e tempo até o lobby abrir; (2) quantos tipos específicos do Postgres os models usam hoje (JSONB e outros) e o custo de trocá-los; (3) escrita concorrente com 4+ jogadores no mesmo tick (SQLite em modo WAL aguenta?); (4) como fica o ciclo database-first com `sqlacodegen` em cada opção. Sai daqui com a D4 decidida e o plano da F4 fechado.

**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO sem cair para polling. O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

**F7 — Spike: estratégia Python escrita pelo usuário.** Origem: #2, #12. Decide a D5 e define a API da classe base. Falta responder: (1) carregar um `.py` externo via `importlib` funciona dentro do executável do PyInstaller, e quais bibliotecas a estratégia enxerga (só as empacotadas — pandas sim, outras não); (2) como proteger o tick de uma estratégia em loop infinito ou lenta (timeout por tick); (3) o que a estratégia vê e pode fazer — hoje `BaseStrategy` só recebe `matching_engine`/`market_data`, ou seja, renda variável, e faltam caixa, posição e renda fixa; (4) onde o código fica guardado — numa pasta (fácil de editar no editor) ou no banco junto da simulação (retomar reusa exatamente a mesma versão do código); (5) a viabilidade da opção "bot cliente da API" no multiplayer.
