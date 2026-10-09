<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Última mudança (2026-10-09):** F11 concluída: drawdown, volatilidade e Sharpe por jogador, sobre snapshots que passaram a ser diários.

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | [F4](#f4) | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | [F1](#f1), [F2](#f2) | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F8](#f8), [F9](#f9), [F10](#f10) | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | [F11](#f11) | — |
| **N6** | Comparar resultados de simulações diferentes | [F12](#f12) | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | [F13](#f13) | — |
| **D4** | Banco de dados embarcado no executável | [F4](#f4) | 🔍 |
| **D5** | Onde roda o código de estratégia escrito pelo usuário | [F8](#f8) | 🔍 |
| [**F3**](#f3) | Spike: banco embarcado no executável | — | 🔍 |
| [**F4**](#f4) | Executável sobe sem banco instalado | — | ⏳ |
| [**F5**](#f5) | Spike: provider de túnel pela internet | — | 🔍 |
| [**F6**](#f6) | Link de convite pela internet no lobby | — | ⏳ |
| [**F7**](#f7) | Spike: estratégia Python escrita pelo usuário | — | 🔍 |
| [**F8**](#f8) | Modo automático: estratégia do jogador roda a cada tick | — | ⏳ |
| [**F9**](#f9) | Estratégias prontas de exemplo | — | ⏳ |
| [**F10**](#f10) | Guia de como escrever uma estratégia | — | ⏳ |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |

<details>
<summary><strong>Concluído / decidido / descartado (10 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | [F2](#f2), [F11](#f11), [F13](#f13) | ✅ |
| **D2** | Cálculo financeiro acontece só no backend; o frontend exibe | [F2](#f2), [F11](#f11), [F12](#f12) | ✅ |
| **D3** | Dinheiro e quantidade trafegam como Decimal serializado em string | [F1](#f1) | ✅ |
| **D6** | A retomada continua no dia seguinte ao último evento | [F2](#f2) | ✅ |
| [**F1**](#f1) | Decimal como string do backend ao frontend | — | ✅ |
| [**F2**](#f2) | Renda fixa com cálculo único no backend e retomada consistente | — | ✅ |
| [**F11**](#f11) | Métricas de risco do desempenho | — | ✅ |
| [**F12**](#f12) | Comparação entre simulações | — | ✅ |
| [**F13**](#f13) | Impacto de preço de ordens grandes | — | ✅ |
| [**F15**](#f15) | Cliente desktop em Tauri | — | 🚫 |

</details>

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: as `F#` que podem ser pegas agora — toda dependência já ✅. "Destrava" é quantas `F#` em aberto esperam por ela, direta ou indiretamente; é por aí que a tabela está ordenada. 💤 (sem prioridade) e 🚫 não entram.

| ID | Resumo | Marco | Destrava | Status |
| --- | --- | --- | --- | --- |
| [**F7**](#f7) | Spike: estratégia Python escrita pelo usuário | M4 | 3 | 🔍 |
| [**F3**](#f3) | Spike: banco embarcado no executável | M2 | 1 | 🔍 |
| [**F5**](#f5) | Spike: provider de túnel pela internet | M3 | 1 | 🔍 |

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
| [**F1**](#f1) | Decimal como string do backend ao frontend | — | ✅ |
| [**F2**](#f2) | Renda fixa com cálculo único no backend e retomada consistente | — | ✅ |

</details>

### M2 — Baixar e jogar

> **Objetivo:** Abrir o executável numa máquina limpa e chegar ao lobby sem instalar nada.
>
> **Serve:** N1
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F3**](#f3) | Spike: banco embarcado no executável | — | 🔍 |
| [**F4**](#f4) | Executável sobe sem banco instalado | [F3](#f3) | ⏳ |

### M3 — Multiplayer pela internet

> **Objetivo:** Convidar um amigo de fora da rede local mandando só um link.
>
> **Serve:** N2
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F5**](#f5) | Spike: provider de túnel pela internet | — | 🔍 |
| [**F6**](#f6) | Link de convite pela internet no lobby | [F5](#f5) | ⏳ |

### M4 — Estratégias automáticas

> **Objetivo:** Escrever ou escolher uma estratégia e deixar o simulador operar com ela.
>
> **Serve:** N4
>
> **Progresso:** 0/4 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F7**](#f7) | Spike: estratégia Python escrita pelo usuário | — | 🔍 |
| [**F8**](#f8) | Modo automático: estratégia do jogador roda a cada tick | [F7](#f7) | ⏳ |
| [**F9**](#f9) | Estratégias prontas de exemplo | [F8](#f8) | ⏳ |
| [**F10**](#f10) | Guia de como escrever uma estratégia | [F8](#f8) | ⏳ |

### M5 — Análise de desempenho

> **Objetivo:** Ver o risco por trás do retorno e comparar simulações lado a lado.
>
> **Serve:** N5, N6
>
> **Progresso:** 2/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| — | *(nada em aberto)* | — | — |

<details><summary>Concluído (2 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F11**](#f11) | Métricas de risco do desempenho | — | ✅ |
| [**F12**](#f12) | Comparação entre simulações | — | ✅ |

</details>

### Sem marco

> **Progresso:** 1/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |

<details><summary>Concluído (1 item)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F13**](#f13) | Impacto de preço de ordens grandes | — | ✅ |

</details>

---

## 1. Atende necessidade

| ID | Resumo | Atende (N#) | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F1** | Decimal como string do backend ao frontend | N3 | D3 | M1 | — | Médio | Médio | Alto | Bom | ✅ Concluído |
| **F2** | Renda fixa com cálculo único no backend e retomada consistente | N3 | D1, D2, D6 | M1 | — | Alto | Alto | Alto | Bom | ✅ Concluído |
| **F4** | Executável sobe sem banco instalado | N1 | D4 | M2 | [F3](#f3) | Médio | Médio | Alto | Excelente | ⏳ Pendente |
| **F6** | Link de convite pela internet no lobby | N2 | — | M3 | [F5](#f5) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F8** | Modo automático: estratégia do jogador roda a cada tick | N4 | D5 | M4 | [F7](#f7) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F9** | Estratégias prontas de exemplo | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F10** | Guia de como escrever uma estratégia | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F11** | Métricas de risco do desempenho | N5 | D1, D2 | M5 | — | Médio | Baixo | Alto | Excelente | ✅ Concluído |
| **F12** | Comparação entre simulações | N6 | D2 | M5 | — | Médio | Baixo | Médio | Bom | ✅ Concluído |
| **F13** | Impacto de preço de ordens grandes | N7 | D1 | — | — | Alto | Alto | Médio | Médio | ✅ Concluído |

<a id="f1"></a>
**F1 — Decimal como string do backend ao frontend.** Origem: #86. O `BaseDTO` deixou de converter `Decimal` para `float`, e o Pydantic serializa como string; os DTOs de dinheiro, quantidade monetária e taxa (carteira, posições, renda fixa, simulação, indicadores, eventos realtime de caixa e execução) e os requests de valor passaram a `Decimal`. O motor guarda caixa e posições em `Decimal`; preço de ação continua `float` na origem (`StockPriceHistory` é `Double`) e vira `Decimal` pelo texto (`to_money`) onde entra no caixa ou num evento. No front, `displayMoney`/`displayPercent`/`displayMoneyCompact` formatam a string direto pelo `Intl` (lib `ES2023.Intl`), e os requests mandam a string digitada. A conta da tela de Carteira subiu para o backend: o `PortfolioDTO` traz totais, alocação e rentabilidade prontos, o histórico patrimonial virou `/api/portfolio/history`, e `portfolio_update` substitui a carteira a cada tick. Limitações: a pizza da carteira soma no front os itens visíveis (interação do gráfico); o compacto do eixo passou a usar o sufixo pt-BR ("mil", "mi").
**Aceite:** todo valor exibido bate com o `NUMERIC(20,6)` do banco em todas as casas que a tela mostra.

<a id="f2"></a>
**F2 — Renda fixa com cálculo único no backend e retomada consistente.** Origem: #85. `features/fixed_income/accrual.py` é a única fórmula: taxa efetiva (prefixado = taxa; CDI = CDI × percentual; IPCA+/SELIC+ composto, `(1 + índice) × (1 + spread) − 1`), fator diário `(1 + taxa)^(1/252)`, tabela regressiva de IR e resgate arredondado ao centavo. O tick ao vivo (`accrue`, idempotente por dia), a reconstrução e a projeção aplicam a mesma sequência de multiplicações em `Decimal`. Ao carregar, as posições são reconstruídas dos eventos BUY/REDEEM (D1), e as de ações também, repetindo compras e vendas com a mesma `Position`. A retomada segue a D6, sem reaplicar o aporte do mês, e o caixa reconstruído passou a somar os aportes. As posições de renda fixa são indexadas pelo `asset_uuid`, não pelo nome. `GET /api/fixed-income/{uuid}/projection` alimenta a tela de detalhe, e o front parou de projetar juros. Limitações: os indicadores (CDI, IPCA, SELIC) ainda são constantes em `EconomicRepository`, então a projeção do pós-fixado só coincide com o realizado enquanto continuarem constantes; o IR de vários aportes no mesmo título usa a data do primeiro.
**Aceite:** um prefixado comprado e levado ao vencimento credita o mesmo valor, ao centavo, rodando direto ou pausando e retomando no meio — e esse valor é igual à projeção mostrada no dia da compra (coberto em `tests/test_fixed_income_accrual.py` e verificado ponta a ponta: projeção R$ 12.778,14, resgate R$ 12.778,14 após parar e retomar).

<a id="f4"></a>
**F4 — Executável sobe sem banco instalado.** Serve N1. Na primeira execução o executável cria o banco sozinho numa pasta de dados do usuário (ex.: `%APPDATA%/SimuladorFinanceiro`), sem `.env` obrigatório; `database.py` deixa de falhar quando `POSTGRES_DATABASE_URL` não existe. O motor é o que a D4 decidir. A página de instalação dos docs e o README perdem a etapa de instalar o Postgres. Gatilho: assim que a F3 fechar a D4.
**Aceite:** numa máquina sem Postgres, baixar o release e abrir o executável leva ao lobby sem nenhum passo extra.

<a id="f6"></a>
**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada.

<a id="f8"></a>
**F8 — Modo automático: estratégia do jogador roda a cada tick.** Origem: #2, #12, #14. Hoje `SimulationEngine.set_strategy` guarda uma estratégia só para o engine inteiro; ela passa a ser por jogador (`client_id` → estratégia), com `ManualStrategy` (já é no-op) como padrão. Cada tick chama `next()` da estratégia de cada jogador antes do flush de eventos. A página de Estratégias (hoje um mock que retorna 501) vira real: escolher a estratégia, ativar e desativar (a alternância manual ↔ automático da #14) e ver o log das ordens que ela emitiu. Onde a estratégia roda e quem pode carregá-la segue a D5. Gatilho: F7 concluída.

<a id="f9"></a>
**F9 — Estratégias prontas de exemplo.** As três do mock atual de `strategies.tsx`, implementadas como subclasses da classe base com parâmetros editáveis na UI: cruzamento de médias móveis de 50 e 200 dias, RSI (compra abaixo de 30, vende acima de 70) e rompimento de máxima com volume. Servem para jogar no automático sem escrever código e como exemplo para o guia da F10.

<a id="f10"></a>
**F10 — Guia de como escrever uma estratégia.** Origem: #49. Página no Docusaurus (grupo "Como Usar"): a classe base, quais métodos o usuário implementa e quais já vêm prontos, o que acontece em cada tick, uma das estratégias da F9 comentada linha a linha, e as limitações (bibliotecas disponíveis no executável, tempo máximo por tick, regra de multiplayer da D5). Gatilho: F8 concluída — a API da classe base só fica estável depois dela.

<a id="f11"></a>
**F11 — Métricas de risco do desempenho.** Origem: #5. O snapshot passou a ser diário (um por jogador por dia útil); `statistics_snapshot_update` continua saindo só na virada do mês, para a tela de Estatísticas não buscar o histórico inteiro a cada tick, e `snapshot_update` (merge por data na Carteira) sai todo dia. O `total_fixed` do snapshot vem das posições em memória do motor, como o `total_equity`, e a tabela `fixed_income_position`, que só existia para alimentá-lo, saiu do modelo. Medido em 100× com 4 jogadores: o tick foi de ~49 ms para ~64 ms (~4,5 ms por jogador). `features/statistics/risk.py` calcula em `Decimal`, a partir dos snapshots (D1) e no backend (D2), o retorno de cada dia descontado o aporte do dia, e sobre ele:
- **Drawdown máximo:** a maior queda a partir de um pico numa cota que só os rendimentos movem (como a cota de um fundo), então o aporte não disfarça a queda. Ex.: o patrimônio sobe a R$ 15.000 e cai a R$ 12.000 → 20%. Quanto menor, melhor; acima de ~30% é uma queda que a maioria das pessoas não aguenta sem vender.
- **Volatilidade anual:** desvio-padrão amostral dos retornos diários × √252. Ex.: ~1% ao ano é renda fixa; ~25% é uma carteira só de ações.
- **Índice de Sharpe:** (retorno anual − CDI anual) ÷ volatilidade anual, com o retorno anual e o CDI anual como a média diária × 252; o CDI de cada dia sai do mesmo fator diário da renda fixa. Ex.: retorno de 18%, CDI de 10%, volatilidade de 16% → 0,5. Abaixo de 0 perdeu para o CDI; perto de 1 é bom; acima de 2 é raro.

`RiskMetricsDTO` vem aninhado em cada jogador de `/api/statistics` e `/api/statistics/compare`; cada métrica é `null` enquanto a série é curta demais (drawdown a partir do 2º dia, volatilidade e Sharpe a partir do 3º; Sharpe também sem oscilação). Na tela de Estatísticas, o card "Risco da sua carteira" mostra as três com o número de dias da amostra, uma descrição curta ao lado e um tooltip com definição, exemplo e faixa boa/ruim; o ranking (e a comparação) ganhou as três colunas com o mesmo tooltip. O `FieldHint` do lobby virou `shared/components/info-hint.tsx`. Limitações: o CDI ainda é constante em `EconomicRepository`; save anterior tem só os pontos mensais antes da retomada, que entram como um "dia" de variação maior; com volatilidade perto de zero (só renda fixa) o Sharpe fica grande em módulo.
**Aceite:** numa série sintética com pico de R$ 15.000 e vale de R$ 12.000, a API retorna drawdown de 20,00% (coberto em `tests/test_statistics_risk.py`, junto com aporte que não esconde queda e volatilidade/Sharpe conferidos à mão).

<a id="f12"></a>
**F12 — Comparação entre simulações.** Origem: #84. O ranking subiu para o backend (D2): `features/statistics/ranking.py` calcula em `Decimal`, a partir do último snapshot de cada jogador, o capital aportado (saldo inicial + aportes), o retorno em R$ e em % e a posição, além da média da sala. `GET /api/statistics` passou a devolver esse relatório pronto (`PerformanceReportDTO`). `GET /api/statistics/compare?simulation_ids=…` devolve o mesmo relatório para várias simulações salvas, sem exigir partida ativa; `StatisticsRepository.get_players_history` recebe os ids e traz o nome de cada simulação. No front saíram `build-ranking.ts` e `build-match-summary.ts`. A tela de Estatísticas refaz a busca a cada `statistics_snapshot_update`. O gráfico de desempenho guarda a string original para o tooltip, que agora mostra os valores em R$. A tela `/compare-simulations` abre pelo botão "Comparar Simulações" do lobby: uma sidebar com checkbox por simulação salva, e o gráfico e o ranking com séries `Nick#Simulação`. O registro recusa `#` no nickname. Patrimônio zero passou a valer −100% de retorno. Limitação: o eixo X é a data, então simulações de períodos diferentes aparecem em trechos diferentes do eixo, não sobrepostas.
**Aceite:** marcar duas simulações salvas mostra `Lilo#Teste M1 103121` (2,18%) e `Lilo#Simulação #4` (0,00%) no gráfico e no ranking, com tooltip em R$.

<a id="f13"></a>
**F13 — Impacto de preço de ordens grandes.** Origem: #59. Ligável por partida no lobby: `price_impact_enabled`, `price_impact_k` e `price_impact_decay_days` são colunas de `simulations` (padrões em `[simulation]` do TOML), então a partida retoma com a mesma configuração. `features/variable_income/price_impact.py` é a única fórmula: a quantidade líquida do dia por ativo (compras − vendas dos jogadores, de `event_equity`) gera impacto = k × √(quantidade ÷ volume médio dos últimos 20 pregões); o impacto vale cheio no pregão seguinte e decai por (1 − t/T)², com t = 0 nesse primeiro pregão, durando T pregões. O preço do dia é o OHLC histórico × (1 + soma dos impactos ativos), piso 0,01, no centavo. Agregar por dia faz o fatiamento de uma ordem em várias execuções não mudar nada, e compra e venda iguais entre jogadores se anulam. O impacto é derivado dos eventos (D1) a cada tick, depois de um flush que leva ao banco as ordens enviadas entre ticks, então retomar reconstrói os mesmos preços. Vale na lista de ativos, no detalhe e no histórico do gráfico (cada dia com o seu fator), no market maker e no matching, na carteira e no snapshot mensal, que passou a receber do motor o valor das ações. Padrões: k = 0,02 (próximo do mercado real), T = 20. Limitações: sem migração, banco anterior à F13 fica incompatível (nova release, novo save); o histórico do detalhe recalcula o fator de cada dia a cada abertura da tela.
**Aceite:** com k = 0,02, comprar 10% do volume médio desloca o preço do pregão seguinte em +0,63% e o desvio some depois de T pregões (coberto em `tests/test_price_impact.py`).

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

---
## 3. Descartada

| ID | Resumo | N# | Status |
| --- | --- | --- | --- |
| **F15** | Cliente desktop em Tauri | — | 🚫 Descartado |

<a id="f15"></a>
**F15 — Descartado.** 🚫 O núcleo do Tauri é Rust: o backend Python iria como sidecar (o executável do PyInstaller dentro do pacote Tauri), o que dá dois executáveis, toolchain Rust nas três plataformas da CI e um WebView diferente em cada SO. O ganho — janela própria em vez de aba do navegador — é o mesmo da F14, que faz isso em Python dentro do executável atual. Electron daria o mesmo resultado com ~150 MB de Chromium a mais. Em qualquer dos dois, os convidados do multiplayer continuam no navegador.

---
## 4. Incerta / exploratória

| ID | Resumo | Conexão | Marco | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| **F3** | Spike: banco embarcado no executável | Serve N1; decide D4 | M2 | — | 🔍 Em avaliação |
| **F5** | Spike: provider de túnel pela internet | Serve N2; escolhe o provider da F6 | M3 | — | 🔍 Em avaliação |
| **F7** | Spike: estratégia Python escrita pelo usuário | Serve N4; decide D5 | M4 | — | 🔍 Em avaliação |

<a id="f3"></a>
**F3 — Spike: banco embarcado no executável.** Decide a D4. Falta medir as três opções finalistas com o executável real: (1) aumento de tamanho do `.exe` e tempo até o lobby abrir; (2) quantos tipos específicos do Postgres os models usam hoje (JSONB e outros) e o custo de trocá-los; (3) escrita concorrente com 4+ jogadores no mesmo tick (SQLite em modo WAL aguenta?); (4) como fica o ciclo database-first com `sqlacodegen` em cada opção. Sai daqui com a D4 decidida e o plano da F4 fechado.

<a id="f5"></a>
**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO sem cair para polling. O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

<a id="f7"></a>
**F7 — Spike: estratégia Python escrita pelo usuário.** Origem: #2, #12. Decide a D5 e define a API da classe base. Falta responder: (1) carregar um `.py` externo via `importlib` funciona dentro do executável do PyInstaller, e quais bibliotecas a estratégia enxerga (só as empacotadas — pandas sim, outras não); (2) como proteger o tick de uma estratégia em loop infinito ou lenta (timeout por tick); (3) o que a estratégia vê e pode fazer — hoje `BaseStrategy` só recebe `matching_engine`/`market_data`, ou seja, renda variável, e faltam caixa, posição e renda fixa; (4) onde o código fica guardado — numa pasta (fácil de editar no editor) ou no banco junto da simulação (retomar reusa exatamente a mesma versão do código); (5) a viabilidade da opção "bot cliente da API" no multiplayer.
