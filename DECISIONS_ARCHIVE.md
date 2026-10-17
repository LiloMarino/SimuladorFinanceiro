<!-- MANTIDO POR scripts/roadmap.py (skill feature-roadmap) -- entradas chegam só pelo comando `archive`. -->

# Arquivo morto — Roadmap do Simulador Financeiro

> Itens encerrados que saíram de [DECISIONS.md](DECISIONS.md) e do roadmap pelo comando `archive`, com o bloco do porquê e o card do kanban como estavam: features concluídas ou descartadas, decisões substituídas, marcos entregues, necessidades que o usuário deu por atendidas. O argumento de cada descarte mora aqui: uma feature nova é procurada neste arquivo antes de ser proposta.

### F1 · arquivado em 2026-10-17

*Kanban:* Decimal como string do backend ao frontend · 1. Atende necessidade · ✅ Concluído · atende N3 · decisões D3 · marco M1

**F1 — Decimal como string do backend ao frontend.** Origem: #86. O `BaseDTO` deixou de converter `Decimal` para `float`, e o Pydantic serializa como string; os DTOs de dinheiro, quantidade monetária e taxa (carteira, posições, renda fixa, simulação, indicadores, eventos realtime de caixa e execução) e os requests de valor passaram a `Decimal`. O motor guarda caixa e posições em `Decimal`; preço de ação continua `float` na origem (`StockPriceHistory` é `Double`) e vira `Decimal` pelo texto (`to_money`) onde entra no caixa ou num evento. No front, `displayMoney`/`displayPercent`/`displayMoneyCompact` formatam a string direto pelo `Intl` (lib `ES2023.Intl`), e os requests mandam a string digitada. A conta da tela de Carteira subiu para o backend: o `PortfolioDTO` traz totais, alocação e rentabilidade prontos, o histórico patrimonial virou `/api/portfolio/history`, e `portfolio_update` substitui a carteira a cada tick. Limitações: a pizza da carteira soma no front os itens visíveis (interação do gráfico); o compacto do eixo passou a usar o sufixo pt-BR ("mil", "mi").
**Aceite:** todo valor exibido bate com o `NUMERIC(20,6)` do banco em todas as casas que a tela mostra.

### F2 · arquivado em 2026-10-17

*Kanban:* Renda fixa com cálculo único no backend e retomada consistente · 1. Atende necessidade · ✅ Concluído · atende N3 · decisões D1, D2, D6 · marco M1

**F2 — Renda fixa com cálculo único no backend e retomada consistente.** Origem: #85. `features/fixed_income/accrual.py` é a única fórmula: taxa efetiva (prefixado = taxa; CDI = CDI × percentual; IPCA+/SELIC+ composto, `(1 + índice) × (1 + spread) − 1`), fator diário `(1 + taxa)^(1/252)`, tabela regressiva de IR e resgate arredondado ao centavo. O tick ao vivo (`accrue`, idempotente por dia), a reconstrução e a projeção aplicam a mesma sequência de multiplicações em `Decimal`. Ao carregar, as posições são reconstruídas dos eventos BUY/REDEEM (D1), e as de ações também, repetindo compras e vendas com a mesma `Position`. A retomada segue a D6, sem reaplicar o aporte do mês, e o caixa reconstruído passou a somar os aportes. As posições de renda fixa são indexadas pelo `asset_uuid`, não pelo nome. `GET /api/fixed-income/{uuid}/projection` alimenta a tela de detalhe, e o front parou de projetar juros. Limitações: os indicadores (CDI, IPCA, SELIC) ainda são constantes em `EconomicRepository`, então a projeção do pós-fixado só coincide com o realizado enquanto continuarem constantes; o IR de vários aportes no mesmo título usa a data do primeiro.
**Aceite:** um prefixado comprado e levado ao vencimento credita o mesmo valor, ao centavo, rodando direto ou pausando e retomando no meio — e esse valor é igual à projeção mostrada no dia da compra (coberto em `tests/test_fixed_income_accrual.py` e verificado ponta a ponta: projeção R$ 12.778,14, resgate R$ 12.778,14 após parar e retomar).

### F3 · arquivado em 2026-10-17

*Kanban:* Spike: banco embarcado no executável · 1. Atende necessidade · ✅ Concluído · atende N1 · decisões D4 · marco M2

**F3 — Spike: banco embarcado no executável.** Decidiu a D4: Postgres oficial embarcado no executável do Windows. A medição usou um harness descartável que roda a `Simulation` real com 10 jogadores e threads gravando em paralelo, como requisições HTTP, sobre o Postgres e o SQLite, com os preços do banco de desenvolvimento (19.919 linhas) e uma variante de 100 ações (664 mil linhas); mais um executável de teste com o servidor embarcado, o app completo empacotado com um pacote de Postgres embarcado e o zip oficial da EDB extraído, iniciado e parado sem instalação. Os números e os argumentos estão na D4. Limitações: sobrecarga e 100 ações têm uma repetição cada; o Postgres rodou com a configuração padrão; o tempo de abertura do app completo e a máquina limpa (runtime do Visual C++) não foram medidos e ficam para o aceite da F4.

### F4 · arquivado em 2026-10-17

*Kanban:* Executável sobe sem banco instalado · 1. Atende necessidade · ✅ Concluído · atende N1 · decisões D4 · marco M2 · depende de F3

**F4 — Executável sobe sem banco instalado.** Serve N1; condicionada pela D4. No Windows o executável leva o Postgres oficial e abre sem nenhum passo extra. `scripts/build_postgres.py` (`pnpm build:postgres`, rodado pelo release só no job do Windows) baixa o zip oficial com versão e SHA-256 fixados, extrai `postgres`, `initdb`, `pg_ctl`, as DLLs, `lib`, `share` e as licenças, e roda o `initdb` uma vez (UTF8, localidade `C.UTF-8` embutida, fuso America/Sao_Paulo), gerando `postgres.zip` e `cluster.zip`, que o `.spec` empacota em `backend/postgres`. `backend/core/embedded_postgres.py` cuida do ciclo de vida: `resolve_database_url()` devolve o `POSTGRES_DATABASE_URL` quando definida (o `.env` deixa de ser obrigatório e o servidor não sobe) ou sobe o embarcado; extrai binários e banco uma vez em `%LOCALAPPDATA%/SimuladorFinanceiro`, sobe o `postgres.exe` numa porta livre só em 127.0.0.1, sorteia a senha do superusuário na primeira abertura e passa a exigir `scram-sha-256`. O servidor fica preso ao processo do app por um Job Object, que o Windows encerra em qualquer queda, e o encerramento limpo roda no `atexit` e nos eventos de console (Ctrl+Break, fechar a janela, logoff, desligamento). `database.py` e `main.py` passaram a usar `resolve_database_url()`; Linux e macOS não embarcam nada e seguem com `POSTGRES_DATABASE_URL`. A página de instalação e o README foram reescritos, e o workflow `postgres-version.yml` compara toda segunda a versão fixada com a mais recente. Referência de desenho: o Karaoke Mugen, aplicativo desktop de código aberto, embarca o Postgres por padrão, aceita um externo por configuração, confere o runtime do Visual C++ e limpa servidor órfão. Medido no app completo: 112,1 MB (eram 60,4); primeira abertura numa máquina limpa simulada em cerca de 10 s; reabertura em 6,8 s, igual à do mesmo executável com banco externo; fechar o app à força não deixa servidor para trás. Limitações: a verificação foi num Windows que já tem Postgres instalado (o executável não o usa) e com o runtime do Visual C++ presente, então a máquina realmente limpa continua por testar; o fechamento pelo X da janela não foi exercitado, só Ctrl+Break; o macOS não embarca (a EDB tem o zip oficial e entra pelo mesmo caminho); uma versão principal nova do Postgres exige exportar e importar o banco.

**Aceite:** numa máquina Windows sem Postgres e sem `.env`, baixar o release e abrir o executável leva ao lobby sem nenhum passo extra, e a segunda abertura chega ao lobby sem rodar o `initdb`.

### F11 · arquivado em 2026-10-17

*Kanban:* Métricas de risco do desempenho · 1. Atende necessidade · ✅ Concluído · atende N5 · decisões D1, D2 · marco M5

**F11 — Métricas de risco do desempenho.** Origem: #5. O snapshot passou a ser diário (um por jogador por dia útil); `statistics_snapshot_update` continua saindo só na virada do mês, para a tela de Estatísticas não buscar o histórico inteiro a cada tick, e `snapshot_update` (merge por data na Carteira) sai todo dia. O `total_fixed` do snapshot vem das posições em memória do motor, como o `total_equity`, e a tabela `fixed_income_position`, que só existia para alimentá-lo, saiu do modelo. Medido em 100× com 4 jogadores: o tick foi de ~49 ms para ~64 ms (~4,5 ms por jogador). `features/statistics/risk.py` calcula em `Decimal`, a partir dos snapshots (D1) e no backend (D2), o retorno de cada dia descontado o aporte do dia, e sobre ele:
- **Drawdown máximo:** a maior queda a partir de um pico numa cota que só os rendimentos movem (como a cota de um fundo), então o aporte não disfarça a queda. Ex.: o patrimônio sobe a R$ 15.000 e cai a R$ 12.000 → 20%. Quanto menor, melhor; acima de ~30% é uma queda que a maioria das pessoas não aguenta sem vender.
- **Volatilidade anual:** desvio-padrão amostral dos retornos diários × √252. Ex.: ~1% ao ano é renda fixa; ~25% é uma carteira só de ações.
- **Índice de Sharpe:** (retorno anual − CDI anual) ÷ volatilidade anual, com o retorno anual e o CDI anual como a média diária × 252; o CDI de cada dia sai do mesmo fator diário da renda fixa. Ex.: retorno de 18%, CDI de 10%, volatilidade de 16% → 0,5. Abaixo de 0 perdeu para o CDI; perto de 1 é bom; acima de 2 é raro.

`RiskMetricsDTO` vem aninhado em cada jogador de `/api/statistics` e `/api/statistics/compare`; cada métrica é `null` enquanto a série é curta demais (drawdown a partir do 2º dia, volatilidade e Sharpe a partir do 3º; Sharpe também sem oscilação). Na tela de Estatísticas, o card "Risco da sua carteira" mostra as três com o número de dias da amostra, uma descrição curta ao lado e um tooltip com definição, exemplo e faixa boa/ruim; o ranking (e a comparação) ganhou as três colunas com o mesmo tooltip. O `FieldHint` do lobby virou `shared/components/info-hint.tsx`. Limitações: o CDI ainda é constante em `EconomicRepository`; save anterior tem só os pontos mensais antes da retomada, que entram como um "dia" de variação maior; com volatilidade perto de zero (só renda fixa) o Sharpe fica grande em módulo.
**Aceite:** numa série sintética com pico de R$ 15.000 e vale de R$ 12.000, a API retorna drawdown de 20,00% (coberto em `tests/test_statistics_risk.py`, junto com aporte que não esconde queda e volatilidade/Sharpe conferidos à mão).

### F12 · arquivado em 2026-10-17

*Kanban:* Comparação entre simulações · 1. Atende necessidade · ✅ Concluído · atende N6 · decisões D2 · marco M5

**F12 — Comparação entre simulações.** Origem: #84. O ranking subiu para o backend (D2): `features/statistics/ranking.py` calcula em `Decimal`, a partir do último snapshot de cada jogador, o capital aportado (saldo inicial + aportes), o retorno em R$ e em % e a posição, além da média da sala. `GET /api/statistics` passou a devolver esse relatório pronto (`PerformanceReportDTO`). `GET /api/statistics/compare?simulation_ids=…` devolve o mesmo relatório para várias simulações salvas, sem exigir partida ativa; `StatisticsRepository.get_players_history` recebe os ids e traz o nome de cada simulação. No front saíram `build-ranking.ts` e `build-match-summary.ts`. A tela de Estatísticas refaz a busca a cada `statistics_snapshot_update`. O gráfico de desempenho guarda a string original para o tooltip, que agora mostra os valores em R$. A tela `/compare-simulations` abre pelo botão "Comparar Simulações" do lobby: uma sidebar com checkbox por simulação salva, e o gráfico e o ranking com séries `Nick#Simulação`. O registro recusa `#` no nickname. Patrimônio zero passou a valer −100% de retorno. Limitação: o eixo X é a data, então simulações de períodos diferentes aparecem em trechos diferentes do eixo, não sobrepostas.
**Aceite:** marcar duas simulações salvas mostra `Lilo#Teste M1 103121` (2,18%) e `Lilo#Simulação #4` (0,00%) no gráfico e no ranking, com tooltip em R$.

### F13 · arquivado em 2026-10-17

*Kanban:* Impacto de preço de ordens grandes · 1. Atende necessidade · ✅ Concluído · atende N7 · decisões D1 · marco M10

**F13 — Impacto de preço de ordens grandes.** Origem: #59. Ligável por partida no lobby: `price_impact_enabled`, `price_impact_k` e `price_impact_decay_days` são colunas de `simulations` (padrões em `[simulation]` do TOML), então a partida retoma com a mesma configuração. `features/variable_income/price_impact.py` é a única fórmula: a quantidade líquida do dia por ativo (compras − vendas dos jogadores, de `event_equity`) gera impacto = k × √(quantidade ÷ volume médio dos últimos 20 pregões); o impacto vale cheio no pregão seguinte e decai por (1 − t/T)², com t = 0 nesse primeiro pregão, durando T pregões. O preço do dia é o OHLC histórico × (1 + soma dos impactos ativos), piso 0,01, no centavo. Agregar por dia faz o fatiamento de uma ordem em várias execuções não mudar nada, e compra e venda iguais entre jogadores se anulam. O impacto é derivado dos eventos (D1) a cada tick, depois de um flush que leva ao banco as ordens enviadas entre ticks, então retomar reconstrói os mesmos preços. Vale na lista de ativos, no detalhe e no histórico do gráfico (cada dia com o seu fator), no market maker e no matching, na carteira e no snapshot mensal, que passou a receber do motor o valor das ações. Padrões: k = 0,02 (próximo do mercado real), T = 20. Limitações: sem migração, banco anterior à F13 fica incompatível (nova release, novo save); o histórico do detalhe recalcula o fator de cada dia a cada abertura da tela.
**Aceite:** com k = 0,02, comprar 10% do volume médio desloca o preço do pregão seguinte em +0,63% e o desvio some depois de T pregões (coberto em `tests/test_price_impact.py`).

### F15 · arquivado em 2026-10-17

*Kanban:* Cliente desktop em Tauri · 3. Descartada · 🚫 Descartado

**F15 — Descartado.** 🚫 O núcleo do Tauri é Rust: o backend Python iria como sidecar (o executável do PyInstaller dentro do pacote Tauri), o que dá dois executáveis, toolchain Rust nas três plataformas da CI e um WebView diferente em cada SO. O ganho — janela própria em vez de aba do navegador — é o mesmo da F14, que faz isso em Python dentro do executável atual. Electron daria o mesmo resultado com ~150 MB de Chromium a mais. Em qualquer dos dois, os convidados do multiplayer continuam no navegador.

### F17 · arquivado em 2026-10-17

*Kanban:* Estatísticas em abas, como o relatório de fim de partida de um RTS · 1. Atende necessidade · ✅ Concluído · atende N5, N6 · decisões D2 · marco M7

**F17 — Estatísticas em abas, como o relatório de fim de partida de um RTS.** Serve N5 e N6. Inspiração: a tela de estatísticas do fim de partida do Age of Empires II. `GET /api/statistics` e `/api/statistics/compare` deram lugar a um endpoint por aba — `/api/statistics/{overview,returns,risk,composition,operations}?simulation_ids=…` —, todos sobre os snapshots diários da F11 e sem exigir partida ativa: a tela de Estatísticas passa o id da partida em andamento, a comparação passa os escolhidos, e o fechamento (F27) vai passar o da partida encerrada. O cálculo fica em `features/statistics/` (D2), montado por `report.py`: **Geral** (ranking e resumo da partida); **Rentabilidade** (patrimônio e retorno acumulado da cota dia a dia, com o CDI e o Ibovespa da F20 como linhas tracejadas, e uma tabela com capital aportado, retorno anual composto, meses acima do CDI e meses no positivo); **Risco** (curva de distância do pico, volatilidade em janela móvel de 63 pregões, dispersão risco × retorno e a tabela com drawdown, volatilidade, Sharpe, Sortino, maior tempo abaixo do pico, pior mês e a amostra); **Composição** (área empilhada de caixa, renda variável e renda fixa, e o recorte por setor da F30: exposição de cada jogador no último dia, número efetivo de setores — 1 ÷ Σ fração² — e lucro por setor, reconstruídos de `event_equity` a preço do dia com o fator de impacto); **Operações** (volume negociado por mês, compras, vendas, giro, o IR pago da F29 e o custo de impacto da F13 — executado menos histórico, com o sinal de quem paga —, para o qual `PriceImpact.factors_on` virou público). No front, `StatisticsReport` (`features/statistics/components/statistics-report/`) serve a partida e a comparação; cada aba busca os próprios dados quando abre, e cada métrica tem descrição curta e dica com definição, exemplo e leitura (`lib/metrics.ts`). O `PerformanceChart` virou o gráfico de linha genérico das abas. A aba Geral ganha a nota com a F18. Limitações: o Sortino de uma carteira parada em caixa fica muito negativo (perde para o CDI todo dia com oscilação quase nula); na comparação, simulações de períodos diferentes aparecem em trechos diferentes do eixo.
**Aceite:** numa partida de dois jogadores com impacto ligado, as cinco abas mostram as curvas por jogador com CDI e Ibovespa de referência, Lilo com 69,84% em Financeiro e número efetivo de 1,87, e a comparação abre o mesmo relatório com séries `Nick#Simulação` (cálculos cobertos em `tests/test_statistics_{risk,returns,sectors,operations}.py`).

### F18 · arquivado em 2026-10-17

*Kanban:* Pontuação geral (overall) · 1. Atende necessidade · ✅ Concluído · atende N9 · decisões D10 · marco M7

**F18 — Pontuação geral (overall).** Serve N9; segue a D10. Uma nota por jogador, decomposta por eixo e por métrica, na aba Geral da F17 e no ranking, que passou a ordenar por ela (quem ainda não tem nota vem depois, e o retorno desempata). `features/statistics/score.py` guarda as faixas como tabela de dados: cada métrica vira pontos numa reta entre o valor que vale 0 e o que vale 100, com chão 0 e sem teto; cada eixo é a média das suas métricas medidas, e a nota é a soma dos quatro. **Retorno:** retorno anual acima do CDI (−10 p.p. → 0, +10 p.p. → 100) e acima do Ibovespa (−15 → 0, +15 → 100). **Risco:** queda máxima (50% → 0, 0% → 100), volatilidade (40% → 0), maior tempo abaixo do pico (252 pregões → 0) e pior mês (−20% → 0). **Consistência:** fração dos meses acima do CDI e no positivo. **Eficiência:** Sharpe (−1 → 0, 2 → 100) e Sortino (−1 → 0, 3 → 100). A nota só aparece a partir de 63 pregões; antes, a aba Geral mostra quantos faltam. `ScoreDTO` vem em cada jogador de `/api/statistics/overview`, com o valor e os pontos de cada métrica, e o card "Nota" mostra cada eixo com uma barra e cada métrica como "queda máxima 13,65% → 72,7 pts". A página de estatísticas dos docs tem a fórmula em LaTeX (`remark-math` + `rehype-katex`, com o `$` simples desligado por causa do "R$"), a tabela de faixas e um exemplo completo. Limitação: risco e consistência param perto de 100 e retorno e eficiência não, então uma carteira parada em caixa fica com ~100, quase tudo do eixo Risco.
**Aceite:** na partida de teste, Lilo tem Retorno 58,3 + Risco 71,8 + Consistência 41,7 + Eficiência 40,4 = 212 e lidera o ranking; a soma dos eixos bate com o total (coberto em `tests/test_statistics_score.py`).

### F20 · arquivado em 2026-10-17

*Kanban:* Indicadores reais (CDI, SELIC, IPCA) do Banco Central · 1. Atende necessidade · ✅ Concluído · atende N11 · decisões D7 · marco M8 · dependência de F23

**F20 — Indicadores reais (CDI, SELIC, IPCA) do Banco Central.** Serve N11. As constantes do `EconomicRepository` saíram: as séries moram em `economic_indicator_history` (série, data, `NUMERIC`, origem — D7), com `fetch_log` registrando tentativa e sucesso, e as antigas `ipca_history`/`selic_history`, que nada lia, foram removidas na mesma migration; `stock_price_history` também ganhou a coluna de origem. A busca segue o desenho do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): SGS do Banco Central (séries 12, 11 e 433) em janelas de até 10 anos, valor lido do texto direto para `Decimal`, e IBOV pelo yfinance (`^BVSP`) na mesma tabela. A primeira carga traz a série inteira; as seguintes recomeçam no dia 1 do mês do último valor; a inicialização dispara a busca numa thread, respeitando o intervalo de 6 horas, e falha mantém o que está no banco. Na renda fixa, o tick rende com a taxa do dia útil anterior (a taxa de um dia paga a noite até o próximo): CDI e SELIC viram o fator do dia direto, dia sem valor publicado dentro da série é feriado e não rende, o IPCA do mês se distribui pelos dias úteis do mês, e depois do último dado real vale o último valor conhecido. A projeção na compra congela o último valor conhecido. A taxa anual mostrada no card e usada pelas fábricas de títulos é a do dia composta por 252 dias úteis (IPCA: acumulado de 12 meses), e o Sharpe desconta o CDI diário real. A partida só é criada (ou carregada) quando CDI, SELIC e IPCA têm dado no dia de início. Resolve a limitação de CDI constante da F2 e da F11.
**Aceite:** um CDB 100% do CDI de 02/01/2020 a 31/12/2020 rende, antes do IR, o índice 1,02750141 que a Calculadora do Cidadão do Banco Central dá para o mesmo período (teste com o CDI real de 2020).

### F21 · arquivado em 2026-10-17

*Kanban:* Central de dados, fora da partida · 1. Atende necessidade · ✅ Concluído · atende N13, N3 · decisões D7 · marco M8 · dependência de F24

**F21 — Central de dados, fora da partida.** Serve N13 e N3. `/import-assets` virou a Central de dados, aberta pelo botão do lobby: além dos formulários de importação por yfinance e CSV, uma tabela com toda série da base — indicadores (F20) e ações — com início, fim do dado real, fim do dado gerado (D7, vazio até a F24) e uma barra de linha do tempo por série num eixo comum, com o trecho real e o gerado em cores diferentes. Cada série se atualiza pelo botão da linha (indicador ignora o intervalo de 6 horas) e "Atualizar todos" busca os indicadores e as ações desatualizadas. A cobertura vem de `GET /api/import-assets/coverage`, numa consulta agrupada no lugar do `/status` que fazia uma consulta por ação. A Central é só de fora da partida: o router de `/api/import-assets` responde 409 com partida ativa e o guard manda `/import-assets` para `/` durante o jogo. No lobby, o período é conferido contra a cobertura: indexador sem dado na data inicial bloqueia o botão de iniciar (o backend também recusa), e série cujo dado real termina antes da data final gera um aviso. Um `Alert` entrou no design system para os dois casos.

### F25 · arquivado em 2026-10-17

*Kanban:* Migrations com Alembic · 1. Atende necessidade · ✅ Concluído · atende N14, N1 · decisões D9 · marco M2

**F25 — Migrations com Alembic.** Origem: as mudanças de schema da F11 e da F13, que deixaram os bancos anteriores incompatíveis. O `create_all` saiu de `get_engine()`, e o `main.py` chama `migrate()` (`backend/core/migration.py`) antes de subir o uvicorn; `MigrationError` encerra o app com a mensagem no console (no executável, esperando um Enter). O Alembic é configurado no `pyproject.toml` (`[tool.alembic]`, com `ruff` nos hooks de escrita), `pnpm db:revision "<descrição>"` gera a revisão por autogenerate a partir dos models (D9), e o `sqlacodegen` saiu das dependências e do `.spec`. A primeira revisão (`243ae671fdc0`) é o schema atual; a v1.0.0 e bancos de desenvolvimento entre releases não migram. O `migrate` decide pelo estado do banco: vazio recebe todas as migrations; no head, nada; sem `alembic_version` e igual aos models (um banco do `create_all` atual), é marcado no head; sem `alembic_version` e diferente, é recusado; numa revisão anterior, as migrations rodam antes numa cópia (`<banco>_dryrun`, `CREATE DATABASE ... TEMPLATE`), que recusa o upgrade se alguma tabela perder linha ou célula preenchida, e depois um backup `<banco>_bkp_AAAAMMDD_HHMMSS` (ficam os 3 mais recentes) antecede o upgrade real. O `resource_path` acha `backend/migrations` em dev e no executável, que a empacota como dado. `tests/test_migrations.py` (Postgres do `.env`, banco descartável por teste, pulado sem servidor) confere que as migrations chegam exatamente no schema dos models, que toda revisão desce e sobe, o `stamp` do banco do `create_all` e a recusa do banco antigo. A página "Ciclo de desenvolvimento com banco de dados" dos docs foi reescrita para o ciclo novo, com o que o autogenerate não cobre (valor novo em `ENUM` nativo, `ENUM` no downgrade, `NOT NULL` em tabela com dado, rename). O banco local de desenvolvimento ficou preservado como `simulador_financeiro_pre_alembic`. Limitações: a cópia exige o banco sem outras conexões abertas (pgAdmin, DBeaver); a contagem de células não pega dado alterado sem ser apagado.
**Aceite:** com uma revisão de teste que adiciona coluna, um banco com 6.721 preços migra com backup e sem perder linha; uma que remove coluna com dado é recusada no ensaio e o banco fica intacto.

### F26 · arquivado em 2026-10-17

*Kanban:* Redesign visual · 1. Atende necessidade · ✅ Concluído · atende N15 · marco M12 · depende de F36 · dependência de F37

**F26 — Redesign visual.** Serve N15. O app inteiro no visual iterado no Claude Design, sobre os componentes da F36.

**Base.** Tokens só do tema claro em `frontend/index.css`: superfícies, texto, primária azul, pares de estado com fundo suave (sucesso, aviso, perigo, info), sidebar escura, velas e oito cores de gráfico validadas para daltonismo. O tema escuro ficou para a F37. As fontes IBM Plex Sans e Mono vão empacotadas via `@fontsource`, porque o executável roda sem internet; números em mono `tabular-nums`. As variantes novas no DS são: Button `dark`, `inverse`, `success`, `warning` e tamanhos de `xs` a `xl`; Badge e Alert por estado; ToggleGroup `segmented`; Tabs em trilho; Card `sm`/`lg` e `destructive`; Table com linhas `current`/`warning` e coluna `numeric`; Input `numeric`; Avatar até `2xl`; Sheet `lg`. Os estados compartilhados são o `ErrorState` (título, saída e a linha "Erro 500 · …") e os skeletons. O `ApiError` traz a mensagem em português por status.

**Shell.** Sidebar fixa em grupos (Mercado, Você, Ferramentas) com rodapé do jogador; topbar com data, pausa, velocidade segmentada e caixa; o loading avisa depois de 10 s e oferece tentar de novo; a 404 oferece uma saída só, conforme o contexto; os toasts agregam execuções seguidas e respeitam a preferência de entrada e saída.

**Telas, com o que cada uma pediu do backend.**
- Login: o conflito de nickname aparece no card, com "Sou eu, entrar".
- Lobby: status da simulação salva derivado (pausada ou terminada, a mesma regra do `SimulationLoader`, sem coluna nova), jogadores e vencedor; regras em Sheet com prévia da curva de impacto (`GET /api/simulation/price-impact-preview`).
- Central de dados: a importação devolve a série importada; `GET .../suggestion` sugere o setor.
- Carteira: o `PortfolioDTO` ganhou IR do mês com régua da isenção, setores efetivos, aportado e as frações.
- Renda variável:
  - Lista: tabela de mercado com sparkline e setor.
  - Detalhe: livro da sala e execuções lidas dos eventos (`GET .../trades`), além da boleta com prévia (`POST .../order-preview`: total, caixa depois, máximo, IR estimado).
- Renda fixa: tabela comparável pela taxa equivalente de hoje e boleta com projeção (caixa antes e depois).
- Estatísticas: colocação e distância do líder, eixo mais fraco, quadradinhos de meses, dispersão risco × retorno, mapa de calor de volume por mês e estilo de giro.
- Fim de partida: vencedor, pódio e destaques da sala (`GET /api/statistics/highlights`).
- Comparar: letra e cor por partida, "Você contra você", ranking ordenável, "Só você" e o eixo "desde o início" pelo número do pregão.
- Correlação (F32 refeita): ativos por setor, meia matriz, par fixado e destaques.
- Configurações: switches que voltam e explicam ao falhar; a exclusão só libera com o nickname digitado.
- Estratégias: página "Em desenvolvimento" com as três prévias.

**Limitações.**
- A lista do Comparar mostra o vencedor de cada partida, mas não "você em Nº", que exigiria o ranking completo de cada simulação salva.
- A variação do dia na renda variável continua intradiária, por causa do impacto de preço.
- "Encerrar" antes do fim continua salvando e saindo.

### F27 · arquivado em 2026-10-17

*Kanban:* Fechamento de partida: pódio e critério de vitória · 1. Atende necessidade · ✅ Concluído · atende N5, N6, N9 · decisões D8 · marco M7 · depende de F17, F18

**F27 — Fechamento de partida: pódio e critério de vitória.** Serve N5, N6 e N9; segue a D8. Quando a partida chega na data final ou o host encerra, o `simulation_ended` passou a levar o id da simulação, e o `SimulationProvider` leva todos para `/match-result/:id` no lugar do toast e do lobby: o título "Fim de partida", o pódio com os três primeiros e o valor que decidiu cada posição, o relatório da F17 sobre a partida inteira (com a classificação completa e a nota na aba Geral) e "Voltar ao lobby". A rota muda antes de o status da partida ser atualizado, porque o guard tira da tela de Estatísticas quem estiver lá com a partida inativa. O fim por data passou a fazer o mesmo que o `stop()`: o flush dos eventos do último dia e a liberação da simulação antes do aviso, então o fechamento lê a partida inteira. A mesma tela abre depois, para qualquer simulação salva, pelo "Ver resultado" da lista de simulações salvas do lobby, que agora abre para todos os jogadores (carregar continua só do host). **Critério de vitória:** como as condições de vitória do Civilization VI, o host escolhe no lobby entre nota geral (padrão, F18), rentabilidade, patrimônio final ou Sharpe; é a coluna `victory_criterion` de `simulations` (ENUM, migration com `server_default` para as partidas salvas) e ordena o ranking durante a partida e o pódio, com o retorno desempatando e quem ainda não tem o valor (a nota antes de 63 pregões, o Sharpe sem oscilação) no fim. Na comparação de simulações com critérios diferentes, vale a nota geral. É diferente da tela de comparação: a comparação põe resultados lado a lado, o pódio declara quem venceu. Limitação: quem entra pelo navegador com a partida já rodando cai no lobby até recarregar a página (comportamento anterior à F27).
**Aceite:** uma partida de quatro jogadores levada até a data final leva a aba aberta em Estatísticas para `/match-result/3`, com Lilo em 1º por 285 pts de nota; uma partida encerrada pelo host abre a mesma tela pelo "Ver resultado" (ranking por critério coberto em `tests/test_statistics_ranking.py`).

### F29 · arquivado em 2026-10-17

*Kanban:* IR na venda de renda variável · 1. Atende necessidade · ✅ Concluído · atende N7 · decisões D1 · marco M10

**F29 — IR na venda de renda variável.** Serve N7. `features/variable_income/income_tax.py` é o motor fiscal do [Finance Manager](https://github.com/LiloMarino/Finance-Manager) portado para os eventos de `event_equity`, recalculado das operações a cada consulta (D1). Todo mês, por jogador, o lucro das vendas sobre o preço médio fiscal vai para três conjuntos de compensação: comum (ação, ETF e BDR, 15%), day trade (20%) e FII (20%). Compra e venda do mesmo ativo no mesmo dia se pareiam como day trade, a 1ª compra com a 1ª venda, e só as sobras movem o preço médio, que por isso tem replay próprio, separado da posição do `Broker`. O ganho comum com ações é isento quando as vendas de ações do mês somam até R$ 20.000. O prejuízo de cada conjunto abate o lucro dos meses seguintes, e o imposto abaixo de R$ 10 soma ao do mês seguinte. No último dia útil do mês, o tick debita o DARF do mês anterior como evento `TAX` de `event_cashflow`. A retomada começa no dia seguinte ao último evento, então nenhum DARF sai duas vezes. O caixa pode ficar negativo, como uma dívida com a Receita. `stock` ganhou `asset_class` (ação, FII, ETF, BDR): na importação a classe é inferida pelo sufixo do código (31 a 35 e 39 viram BDR, 11 vira FII, o resto vira ação), e na Central de dados um seletor a corrige, porque ETFs e units também terminam em 11. A migration aplica a mesma regra às ações já importadas. A carteira mostra o card "Imposto de Renda", com o IR pago, o valor a pagar (o já apurado que não venceu, mais o mês corrente) e a regra explicada na dica. A aba Operações da F17 lê o mesmo evento `TAX` quando for feita. Limitações: a regra fiscal atual vale para qualquer período histórico simulado; o IRRF de 0,005% fica fora, porque é antecipação do mesmo imposto; e uma partida que termina antes do vencimento não debita o último mês, que fica só como "a pagar".
**Aceite:** vender R$ 30.000 em ações com R$ 5.000 de lucro num mês debita R$ 750 no mês seguinte; vender R$ 15.000 com lucro no mês não debita nada.

### F30 · arquivado em 2026-10-17

*Kanban:* Setores e segmentos · 1. Atende necessidade · ✅ Concluído · atende N16

**F30 — Setores e segmentos.** Serve N16. Mesmo modelo do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): tabelas `sectors` (nome único) e `segments` (nome único dentro do setor), com `segment_id` anulável em `stock` (`ON DELETE SET NULL`). `StockRepository.classify` cria setor e segmento pelo nome na primeira vez e apaga o que fica sem nenhuma ação, então a lista de sugestões só tem o que está em uso. Na importação, enquanto a ação não tem classificação, o `sector` e a `industry` do `yf.Ticker().info` viram a sugestão: os 11 setores do yfinance chegam nos nomes da B3 (Financial Services → Financeiro), a indústria vira o segmento como veio; a classificação feita à mão não é trocada. Na Central de dados (F21), a coluna "Setor / Segmento" abre a janela Classificar, com as sugestões de `GET /api/import-assets/sectors` (`PUT`/`DELETE /stocks/{ticker}/segment`). A carteira ganhou o card "Renda Variável por Setor" (barras e tabela de valor e fração por setor e segmento, "Sem setor" para o que não foi classificado), calculado no backend em `backend/core/sectors.py` (`PortfolioDTO.sectors`); o motor lê a classificação uma vez por partida, porque a Central só abre com a partida parada. O recorte por setor das estatísticas entra na aba Composição da F17. "A estratégia enxerga o setor" ficou para a F7/F8: o dado está em `get_classification`, e o que a estratégia vê é decidido no spike. Limitação: o segmento sugerido vem em inglês (*Banks - Regional*) até ser editado.
**Aceite:** importar ITUB4 e VALE3 pelo yfinance as classifica em Financeiro · Banks - Regional e Materiais Básicos · Other Industrial Metals & Mining, e a PETR4 classificada à mão continua como estava (coberto em `tests/test_sectors.py`).

### F31 · arquivado em 2026-10-17

*Kanban:* Diagrama do banco sempre em dia · 1. Atende necessidade · ✅ Concluído · atende N17 · decisões D9

**F31 — Diagrama do banco sempre em dia.** Serve N17; segue a D9. Primeira versão do diagrama: um `erDiagram` em Mermaid por domínio, gerado dos models por `scripts/erd.py` e conferido por `tests/test_erd.py`, que falhava enquanto a página estivesse defasada. Substituída pela [F50](#f50): um diagrama só, navegável, gerado dentro do build dos docs.

### F32 · arquivado em 2026-10-17

*Kanban:* Ferramenta de correlação entre ativos · 1. Atende necessidade · ✅ Concluído · atende N18 · decisões D2

**F32 — Ferramenta de correlação entre ativos.** Serve N18; segue a D2.

**Onde abre.** Uma rota só, `/correlation`: na partida é o item "Correlação" da sidebar, e no lobby o card "Correlação entre ativos" a abre em tela cheia (`layouts/simulation-mode-layout.tsx` escolhe o layout pelo modo).

**Escolha dos ativos.** Até 20 tickers, agrupados por setor (`GET /api/correlation/assets` traz o setor de cada um). Há dois atalhos: "Minha carteira", na partida, e "Um de cada setor". A janela é de 6 meses, 1, 3 ou 5 anos.

**Cálculo.** `GET /api/correlation` (`features/correlation/correlation.py`) calcula a correlação de Pearson dos retornos diários de cada par com `statistics.correlation`. Cada par usa só os pregões em que os dois lados têm retorno. A resposta traz:
- a matriz completa, com o IBOV como última linha e coluna;
- os destaques entre os ativos escolhidos: o par mais parecido, o de menor correlação (o melhor para diversificar) e, na partida, a média entre as ações da carteira de quem pede.

**Par sem número.** Um par com menos de 63 pregões em comum (~3 meses) vem `null`, com `reason: insufficient_days`; um par com um lado parado na janela vem `null` com `constant_series`. O motivo aparece ao clicar no par. Fechamento inválido (NaN, zero) conta como dia sem pregão.

**Data final.** Na partida, a janela termina sempre na data da simulação, que aparece como selo. Fora dela, a data final é livre e começa no último pregão.

**Tela.**
- A matriz mostra só a metade de baixo, com o Ibovespa numa linha à parte: vermelho para positiva, azul para negativa.
- Clicar numa célula fixa o par no painel lateral, com o número, a leitura e os pregões em comum.
- A leitura segue as faixas: ≥ 0,7 andam muito juntos; 0,3 a 0,7 em parte; −0,3 a 0,3 quase independentes; ≤ −0,3 opostos.
- Se o novo cálculo falha, a matriz anterior fica na tela com um aviso e "Tentar de novo".
- Uma base sem preços leva à Central de dados.

A página "Correlação entre Ativos" dos docs explica a leitura.

**Fora da tela.** O CDI ficou de fora como referência: a taxa diária só muda quando o Copom mexe na Selic, então a correlação com ela fica perto de 0 e, numa janela com a Selic parada, nem existe. Quando a F23 existir, a mesma tela confere o gerador: o mesmo par medido num período histórico e num gerado.

### F35 · arquivado em 2026-10-17

*Kanban:* Dependências em dia · 1. Atende necessidade · ✅ Concluído · atende N15 · marco M12

**F35 — Dependências em dia.** Serve N15. Feito em dois passos, cada um fechado com `pnpm check`. (1) Versões menores: `pnpm update` no frontend e `uv lock --upgrade` no backend. (2) Versões maiores, uma por commit: Vite 8 com o `@vitejs/plugin-react` no lugar do `-swc`; ESLint 10 com `eslint-plugin-react-hooks` 7, cujas regras do React Compiler pediram ajustes (`useEffectEvent` no `useRealtime`, sem `setState` dentro de efeito); `globals`, `eslint-plugin-react-refresh` e `@types/node` atualizados. O TypeScript parou no 6: o `typescript-eslint` ainda não aceita o 7. O `framer-motion` saiu do projeto, porque o único uso era a página 404, refeita sem animação na F26. O Recharts 3 entrou na F36. Limitação: subir para o TypeScript 7 quando o `typescript-eslint` suportar.

### F36 · arquivado em 2026-10-17

*Kanban:* Interface padronizada no shadcn · 1. Atende necessidade · ✅ Concluído · atende N15 · decisões D11 · marco M12 · depende de F35

**F36 — Interface padronizada no shadcn.** Serve N15; decidiu a D11 pelo Base UI. O `components.json` está no preset `base-nova` (`@base-ui/react`), com o pacote `shadcn` importado no CSS (`@import "shadcn/tailwind.css"`, que traz as variantes `data-*` dos componentes). Os componentes de `shared/components/ui` foram recriados pela CLI, e os que faltavam entraram conforme as telas pediram: toggle-group, empty, avatar, field, radio-group, popover, progress, switch, input-group, textarea, sheet, skeleton e separator; o `form.tsx` saiu, sem uso. A CLI do registro grava `import ... from "cn"` e adiciona um pacote `cn` falso: o import é corrigido para `@/shared/lib/utils` a cada componente novo. Os `asChild` fora de `ui/` viraram a prop `render`; o Recharts foi para a versão 3. Aparência nova é sempre variante no componente, e o `@shadcn/lint` garante isso: `no-restyle` (só classes de layout por fora) e `no-raw-colors` (só tokens), que entraram como aviso durante a migração e terminaram como erro. Os 14 elementos feitos à mão viraram o componente equivalente na tela da F26 que os redesenhou.

### F38 · arquivado em 2026-10-17

*Kanban:* Mensagens do backend em português · 1. Atende necessidade · ✅ Concluído · atende N15

**F38 — Mensagens do backend em português.** Serve N15. O frontend mostra na tela a mensagem que o backend devolve, e parte delas ainda chega em inglês. Exemplos:
- os textos padrão das exceções HTTP em `backend/core/exceptions/http_exceptions.py` ("An upstream service failed to answer the request.");
- os erros 422 de validação do Pydantic ("Field required", "Input should be a valid integer");
- mensagens soltas de rotas e serviços.

**Plano.**
1. Traduzir os `detail` padrão de `http_exceptions.py`.
2. Registrar em `backend/routes/__init__.py` um handler de `RequestValidationError` que monta uma frase em português por tipo de erro do Pydantic (`missing`, `int_parsing`, `greater_than`...), com o nome do campo. O formato de erro que o frontend já lê continua o mesmo.
3. Varrer as rotas e os serviços (`grep` por `detail=` e pelos `raise` com texto) atrás do que sobrou em inglês.
4. Criar um teste que percorre as exceções padrão e confere que nenhum `detail` sai em inglês.

O `ApiError` do frontend já cai numa mensagem em português por status quando o backend não manda texto.

**Gatilho:** qualquer momento; não depende de outra feature.

### F39 · arquivado em 2026-10-17

*Kanban:* Cor exclusiva e sigla de duas letras por jogador · 1. Atende necessidade · ✅ Concluído · atende N20 · dependência de F42

**F39 — Cor exclusiva e sigla de duas letras por jogador.** Serve N20. Inspiração: o Age of Empires II, que dá uma cor própria a cada um dos 8 jogadores da partida; aqui a sala vai a 10. Antes, a cor do jogador nascia em dois lugares que não se falavam (um hash do apelido no lobby, no perfil, na sidebar e no livro de ofertas; a posição alfabética nas estatísticas) e a sigla era a primeira letra do apelido. Agora: (1) **a cor é do jogador na partida.** Enquanto está na sala ela vive na memória do servidor (`UserManager`); ao iniciar vira linha de `simulation_players` (`simulation_id`, `user_id`, `color`, chave composta, migration pela D9), que as Estatísticas e o fechamento leem, inclusive dias depois, sem partida ativa. As partidas salvas antes ganharam as linhas na própria migration. (2) **Dez jogadores, dez cores.** `--chart-9` (cinza) e `--chart-10` (marrom) entram na paleta do redesign. O teto da sala é o tamanho da paleta e o servidor recusa o 11º conectado (423, "a sala está cheia"). A conferência de daltonismo (lima × âmbar, verde-água × ciano) continua em aberto. (3) **Conflito é impedido, não detectado.** Ao entrar o jogador recebe a primeira cor livre; a troca é `PUT /api/simulation/players/me/color` e o servidor recusa com 409 se a cor já tem dono (vale o primeiro pedido, quem perdeu fica com a anterior); o evento `player_color` avisa a sala. No seletor "Sua cor" a cor ocupada aparece apagada com a sigla de quem a tem. (4) **A preferência mora no navegador** (`localStorage`): ao entrar o cliente pede a última cor escolhida e fica com a que recebeu se ela já tiver dono. (5) **Sigla sempre de duas letras**, calculada no front por `playerInitials` (acento e emoji contam inteiros) e desenhada pelo `PlayerAvatar` de `shared/`, que substituiu os sete `Avatar` com `charAt(0)`; a sigla sai do apelido, nunca do rótulo " · A". (6) **Uma fonte de cor só no front:** `stringToColor` e `playerColors` saíram; lobby, perfil, sidebar, livro de ofertas, ranking, pódio e gráficos leem a cor do payload. A comparação de simulações segue colorindo por partida (a letra e a cor da F17), com avatares neutros. (7) **Quem participa é quem está na sala ao iniciar**: só eles recebem o depósito inicial e snapshots (antes era toda conta do banco). Quem não participa de uma partida em andamento escolhe uma cor e entra pela F58. (8) **Continuar uma partida salva tem dois passos**: o host a seleciona (`PUT /api/simulation/selection`) e a sala inteira troca para as cores guardadas, travadas para quem já jogou e reservadas para os ausentes; depois clica em Continuar. Quem está na sala e nunca jogou a partida escolhe entre as cores que sobraram e entra com o depósito inicial na retomada. Os bots da F16 não existem ainda e contarão no mesmo teto.

### F43 · arquivado em 2026-10-17

*Kanban:* Spike: outros modos de jogo · 1. Atende necessidade · ✅ Concluído · atende N23 · marco M13

**F43 — Spike: outros modos de jogo.** Serve N23. Decidido com o usuário: entram a corrida à meta (F52) e o viver de renda (F53), além das equipes (F42). Ficaram de fora, por ora: eliminação (a cada trimestre o último sai, até sobrar um), cenário com objetivo (começar numa crise histórica com uma meta, como uma campanha de RTS) e todos contra o índice (a sala inteira numa equipe contra o CDI e o Ibovespa).

### F46 · arquivado em 2026-10-17

*Kanban:* Console do navegador no terminal do dev · 2. Nice-to-have · ✅ Concluído

**F46 — Console do navegador no terminal do dev.** O Vite 8 tem `server.forwardConsole`; em `frontend/vite.config.ts` ele está ligado com `{ unhandledErrors: true, logLevels: ["error", "warn"] }`. No `pnpm dev`, `console.error`, `console.warn`, exceção não tratada e promessa rejeitada sem tratamento aparecem no terminal do Vite como `[vite] (client) [console.error] ...`, as duas últimas com o trecho do código de origem; `console.log` fica de fora. Vale para o desenvolvimento, não para o executável. O ganho principal é para o agente de código, que lê o terminal mas não o console do navegador.

### F50 · arquivado em 2026-10-17

*Kanban:* Diagrama do banco navegável · 1. Atende necessidade · ✅ Concluído · atende N17 · decisões D9

**F50 — Diagrama do banco navegável.** Serve N17; segue a D9. A página "Diagrama do Banco de Dados" tem um diagrama só, com zoom, arraste, busca e os ENUMs numa tabela abaixo, no [ERD Editor](https://github.com/dineug/erd-editor) (`@dineug/erd-editor` 4.0, MIT) embutido como componente do Docusaurus. **100% gerado, sem passo manual:** `scripts/erd.py` lê o `Base.metadata` e escreve o DDL do Postgres (`CreateTable` do SQLAlchemy) em `docs/src/generated/schema.json` e a tabela dos ENUM em `docs/docs/desenvolvimento/_enums.md`; os dois rodam no `prestart`, `prebuild` e `pretypecheck` dos docs (`pnpm db:erd`) e no `deploy-docs.yml`, que ganhou `uv sync` e passou a disparar também por mudança em `backend/core/models/**`. Os arquivos gerados não são versionados, e o `tests/test_erd.py` saiu. O componente `DatabaseDiagram` (`BrowserOnly`) cria o `<erd-editor>`, carrega o DDL com `setSchemaSQL(..., { placement: 'auto' })`, enquadra o diagrama inteiro no zoom inicial e segue o tema claro/escuro do Docusaurus. O editor abre editável e nada é salvo: arrastar tabelas, reorganizar e esboçar uma modelagem ("e se fosse 1-N aqui?") valem só até recarregar, quando o diagrama volta ao schema dos models. **A escolha:** os dois visualizadores foram prototipados sobre o schema de hoje. O React Flow desenhava a notação do MySQL Workbench, mas as linhas se embaraçavam perto das tabelas de evento e foco numa tabela, layout automático e busca teriam de ser construídos. O ERD Editor traz isso pronto (foco numa tabela e nas vizinhas com `Alt+F`, *Auto Layout* por Force, Flow ou árvore, só as colunas de chave, busca por tabela e coluna), e a notação do Workbench foi dispensada: as chaves vêm coloridas (PK amarela, FK vermelha, PK que também é FK azul) e a obrigatoriedade aparece em texto. O modo somente leitura do editor trava também o arrasto, por isso ele não é usado. Limitação: o layout inicial ainda embaraça as linhas perto das tabelas de evento; *Auto Layout* → *Force* (`Ctrl+K`) as separa. O pacote pesa cerca de 11 MB, carregados só na página do diagrama.
**Aceite:** alterar um model e subir `pnpm start` nos docs mostra a mudança no diagrama sem rodar nada à mão.

### F51 · arquivado em 2026-10-17

*Kanban:* Versão única e changelog · 1. Atende necessidade · ✅ Concluído · atende N14 · decisões D12 · dependência de F56

**F51 — Versão única e changelog.** Serve N14; segue a D12. A versão estava em quatro lugares que não se falam: digitada à mão no `workflow_dispatch` do `release.yml`, `0.1.0` no `pyproject.toml`, `0.0.0` nos `package.json` do frontend e dos docs, e `1.0.0` fixo no `FastAPI(...)` do `main.py`; e não existia changelog (as notas da v1.0.0 eram a lista automática de PRs, com atualização de dependência do Dependabot, ilegível para quem joga). Agora: (1) **Uma fonte só** — a versão mora no `pyproject.toml` (2.0.0) e o `get_version()` (`backend/core/version.py`) a lê com `tomllib`; o `pyproject.toml` vai no executável (`datas` do `.spec`), já que o projeto não é um pacote instalável e não há `importlib.metadata`. `GET /api/version` a expõe, e o `FastAPI(version=...)` (e com ele o `openapi.json`) usa o mesmo valor. O campo `version` saiu dos `package.json` (pacotes privados). O `release.yml` não recebe mais a versão digitada: o job `validate` a lê do `pyproject.toml`, falha se a tag já existir e confere com os commits; a release sai com o título "vX.Y.Z (Acesso antecipado)" (D12), e o README ganhou o rótulo. (2) **A próxima versão sai dos commits** — o `git-cliff --bumped-version`, com a `cliff.toml` na raiz, calcula; testado em repositórios descartáveis com a config final: só `docs:`/`refactor:`/`fix:` dão correção (2.0.1), um `feat:` dá a menor (2.1.0), um `!` depois do tipo dá a maior (3.0.0), até em `docs!:` e `fix!:`, e commit sem tipo não move o número. Os commits anteriores à tag v1.0.0 (com emoji) ficam fora de conta. O `pnpm release` (`scripts/release.py`) calcula, grava a versão no `pyproject.toml` e no `uv.lock`, acrescenta a seção ao `CHANGELOG.md` e não commita: o diff é revisado e vai num `chore: Versão X`. Se o `pyproject.toml` já está acima do calculado (como na 2.0.0, que sobe de 1.0.0 por decisão da D12), o número fica; o workflow roda `scripts.release --check` e só recusa o `pyproject.toml` que ficou abaixo do pedido pelos commits, e escreve os dois números no resumo da execução. A tabela da D12 e a convenção de commit estão na página "Versionamento" dos docs e em `contribuindo.md`. (3) **`CHANGELOG.md` automático, sem LLM** — o `git-cliff` gera cada seção: `feat:` vira "Novidades", `fix:` vira "Correções", e `docs:`, `chore:`, `refactor:`, `build:` e `test:` ficam de fora; um commit com `!` aparece à parte em "Quebras". Cada seção diz se as partidas salvas e o `config.toml` continuam valendo. Só a seção da 2.0.0, que cobre tudo desde fevereiro, ganhou um resumo à mão no topo, com o aviso de que as partidas salvas da 1.0.0 não abrem. (4) **Onde aparece** — o `CHANGELOG.md` na raiz; a seção da versão vira a descrição da release no GitHub (`scripts.release --notes` a extrai do arquivo, para que o resumo à mão da 2.0.0 também vá); e a página "Novidades" dos docs, gerada no build por `scripts/changelog_page.py` (`pnpm db:changelog`, no `prestart`/`prebuild`/`pretypecheck` junto do `db:erd`, sem versionar a saída), que o `deploy-docs.yml` também dispara por mudança no `CHANGELOG.md`.
**Aceite:** `pnpm release` num repositório com commits novos sobe o número pelo tipo dos commits e acrescenta a seção ao `CHANGELOG.md`; o workflow de release publica a versão do `pyproject.toml` com as notas dessa seção e recusa a que ficou abaixo da pedida pelos commits; `GET /api/version` devolve a mesma versão no `pnpm dev` e no executável.

### F57 · arquivado em 2026-10-17

*Kanban:* Logs separados por assunto · 1. Atende necessidade · ✅ Concluído · atende N26

**F57 — Logs separados por assunto.** Serve N26. Hoje o `setup_logging` (`backend/core/logger.py`) manda tudo para o console e para um `app.log` só (rotativo, 10 MB por arquivo, 5 arquivos), então um erro fica no meio das linhas de uma partida inteira: o `app.log` de uma sessão de desenvolvimento tem 3.541 linhas, 12 delas de erro, e seis dessas são de uma única busca no yfinance por um ticker que não existe. Inspirado nos logs da Paradox, que guardam um arquivo por assunto e um `error.log` só com os erros. O plano: (1) **`error.log`** — só `ERROR` e `CRITICAL`, com o traceback completo que `logger.exception` já gera, rotativo como o `app.log`; ficam de fora dele as bibliotecas que tratam falha esperada como erro (o `yfinance` para ticker inexistente), por filtro de prefixo de logger; a linha continua no `app.log`, e o importador loga a própria mensagem de erro, que é a que entra no `error.log`. (2) **Um arquivo por área**, escolhido pelo prefixo do nome do logger e com o mesmo formato de linha: `simulation.log` (motor, ticks, ordens), `realtime.log` (Socket.IO e SSE), `import.log` (yfinance e BCB) e `database.log` (migrations e banco). Cada linha vai para o arquivo da área e para o `app.log`, que segue como o registro completo e cronológico. A tabela "arquivo → prefixos de logger" mora só em `logger.py`; área nova é uma linha. (3) **O uvicorn passa a escrever nos mesmos arquivos.** Hoje o `uvicorn.run` instala a configuração de log própria dele, com `propagate` desligado, então as mensagens do servidor (início, erro de protocolo do WebSocket) saem só no console e não existem no `app.log`. Com `log_config=None` os loggers dele sobem para o raiz e entram em `app.log` e `error.log`; o `uvicorn.access`, uma linha por requisição, fica em `WARNING` para não encher o arquivo. A F54 (modo debug) sobe o nível do `app.log` e dos arquivos por área para `DEBUG`, com o `error.log` seguindo só com erros, e a F45 manda as requisições lentas para um `slow.log` com uma linha a mais nessa tabela. **Aceite:** uma exceção provocada numa rota deixa o traceback no `error.log`, uma partida inteira sem falha o deixa vazio, e uma queda do WebSocket por erro de protocolo aparece no `app.log`.

### F58 · arquivado em 2026-10-17

*Kanban:* Entrar no meio da partida (hot-join) · 1. Atende necessidade · ✅ Concluído · atende N27 · depende de F39 · dependência de F61

**F58 — Entrar no meio da partida (hot-join).** Serve N27. Antes só participava quem estava na sala ao iniciar (F39): quem chegava depois, com conta nova ou antiga, era barrado com 423 "a partida já começou". Agora: (1) **A vaga é do participante, online ou não.** A partida em andamento tem no máximo 10 participantes (linhas de `simulation_players`, o teto da paleta); quem jogou e saiu continua dono da vaga e da cor, então uma partida de 10 com seis offline está cheia e o 11º leva 423 ("a partida já tem 10 jogadores, 6 deles offline"). (2) **Quem chega entra "pendente".** `register`, `claim` e `/session/me` deixam de barrar: a sessão volta com `pending_join` e o front manda para a tela `/join`, sem cor e fora de `UserManager._active_players`. (3) **`/join` mostra quem joga (online ou offline), as cores livres e o saldo inicial.** A lista vem de `GET /api/simulation/match-players`; a cor já marcada é a preferência do navegador, se estiver livre, senão a primeira livre. (4) **`POST /api/simulation/join` vale o primeiro pedido.** Sob o mesmo lock `UserManager.join_match` confere o teto e a cor (409 "X pegou essa cor antes") e grava a linha; `Simulation.add_player` deposita o `starting_cash` pelo `add_cash` do motor, datado do dia corrente, e cria o snapshot do dia. O jogador entra no ranking e nas estatísticas. O aporte mensal vale só dali em diante: o ranking por retorno é comparável, mas o por patrimônio absoluto reflete a data de chegada. (5) **Quem sai e volta mantém a cor da partida.** (6) **A mesma conta de vagas vale para a partida salva.** O lobby desenha os ausentes da partida selecionada (cartão tracejado com a cor reservada), marca "Novo" em quem nunca jogou, conta presentes mais ausentes no `N / 10` e mostra o aviso de quem entra com o saldo inicial. Partida que não comporta a sala (jogadores da partida mais novatos passando de 10) não é selecionável: o diálogo de partidas salvas desabilita o "Selecionar" e diz o motivo com os nomes (`room_overflow`), e o servidor recusa com 409 citando os mesmos nomes. Com espaço para os novatos, a seleção segue normal. Quem resolve o excesso hoje é o próprio jogador saindo da sala (F61).
**Aceite:** com a partida em andamento e vaga, um jogador novo escolhe uma cor livre, recebe o depósito inicial e aparece no ranking; com 10 participantes, online ou não, ele continua barrado; uma partida salva de 10 jogadores não é selecionável com um novato na sala, e uma de 8 é com dois.

### F59 · arquivado em 2026-10-17

*Kanban:* Separar em dois executáveis: cliente e servidor · 3. Descartada · 🚫 Descartado · atende N2

**F59 — Descartado.** 🚫 Separar o app em dois executáveis, um cliente e um servidor. Hoje o app já é cliente e servidor: o executável é o servidor, e o navegador é o cliente, que o próprio servidor entrega pronto. Separar não traz nada que isso não dê, e custa três coisas: (1) os convidados do multiplayer teriam de baixar um programa em vez de abrir um link, o que fere a N2; (2) quem hospeda passaria a abrir dois programas, e a versão do cliente teria de combinar com a do servidor, coisa que hoje é garantida porque o front vai dentro do servidor; (3) a CI geraria o dobro de artefatos nos três sistemas. O Tauri não muda a conta: o Rust nas três plataformas e o motor web diferente em cada sistema continuam (F15), e o ganho de uma janela própria é o da F14, em Python, dentro do executável atual. O que a ideia buscava, um servidor sem jogador na frente, é a F60.

### F62 · arquivado em 2026-10-17

*Kanban:* Uma migration inicial só para a 2.0.0 · 1. Atende necessidade · ✅ Concluído · atende N14 · decisões D9 · depende de F4

**F62 — Uma migration inicial só para a 2.0.0.** Serve N14; segue a D9. `backend/migrations/versions/` tinha sete arquivos, todos de outubro de 2026 (a inicial, os indicadores econômicos, a classe do ativo e o IR, setores e segmentos, o critério de vitória, a cor por jogador e o perfil do ativo), escritos durante o desenvolvimento. Nenhum executável publicado os conhecia: a v1.0.0 criava as tabelas com `create_all` e não guarda `alembic_version`. Condensá-los foi de graça, porque ninguém tinha um banco em revisão intermediária; depois da 2.0.0 nenhum banco de jogador pode ficar sem caminho de upgrade, e a cadeia passa a só crescer. Os sete arquivos saíram e entrou uma inicial só, gerada por `pnpm db:revision "create initial schema"` contra um banco vazio e revista à mão: sem os comentários do autogenerate e, no `downgrade`, com o drop explícito de cada `ENUM` nativo (nove), que o autogenerate não faz. O `tests/test_migrations.py` confere que a inicial chega no schema dos models e que sobe e desce; o teste do ensaio com backup, que dependia de haver uma revisão anterior à última, passou a acrescentar ao head real uma revisão só do teste (`add_column` em `stock`), por um `version_locations` extra. O banco de desenvolvimento apontava para uma revisão que deixou de existir e foi recriado do zero, assim como valem os bancos de teste de quem experimentou builds anteriores.
**Aceite:** um banco novo chega ao schema dos models só com a inicial, e `tests/test_migrations.py` passa.

### F63 · arquivado em 2026-10-17

*Kanban:* Sugestão de código ao digitar o ativo · 1. Atende necessidade · ✅ Concluído · atende N13 · marco M8

**F63 — Sugestão de código ao digitar o ativo.** Serve N13. Mesma ideia do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): no campo "Código do ativo" do painel Adicionar ativo (fonte yFinance), a pessoa digita e a lista mostra os códigos válidos com o nome da empresa, em vez de descobrir o erro só depois de tentar importar. Backend: `GET /api/import-assets/tickers?q=` (no router da Central, que já responde 409 com partida ativa) chama `yf.Search(q, max_results=20, news_count=0, lists_count=0).quotes`; abaixo de 2 caracteres devolve `[]` sem consultar a fonte, e falha da fonte vira 503. O filtro é o da B3: bolsa `SAO`, símbolo terminado em `.SA` e código no formato `[A-Z0-9]{4}\d{1,2}` (PETR4, KNRI11); o `.SA` sai, repetidos saem e a ordem do Yahoo fica. Frontend: o campo vira o `TickerCombobox` (`Input` + `Command` do design system, sem `Popover`, para o foco ficar no campo), com debounce de 300 ms, `useQuery` com `staleTime: Infinity` por texto buscado e setas/Enter/Escape. A sugestão não restringe: o texto digitado continua valendo, então `BTC-USD` e o código tirado do nome do CSV seguem funcionando. A lista só aparece com a fonte yFinance; no CSV o campo fica como antes. Limitação: códigos de fora da B3 não aparecem na lista, só digitados à mão.

### F64 · arquivado em 2026-10-17

*Kanban:* Cache do perfil do ativo no yfinance · 1. Atende necessidade · ✅ Concluído · atende N13, N16 · decisões D9 · marco M8

**F64 — Cache do perfil do ativo no yfinance.** Serve N13 e N16; segue a D9. Antes, cada importação de ativo ainda sem classificação chamava `yf.Ticker(ticker).info` de novo, inclusive no "Atualizar todos", e o ativo que o yfinance devolve sem setor (ETF, cripto) era reconsultado toda vez. Agora a tabela `ticker_profile` (`ticker` como chave, `name`, `quote_type`, `sector`, `industry`, `fetched_at`), criada por migration do Alembic, guarda a resposta: `fetch_info` lê a linha antes da rede e só consulta o yfinance quando não há, gravando a resposta, inclusive a vazia, para o ETF sem setor não ser reconsultado. `infer_asset_class`, `suggest_segment` e o nome do ativo leem o perfil guardado. Sem expiração: setor e indústria quase não mudam, e a classificação feita à mão continua mandando sobre a sugestão. Se o yfinance falhar, nada é gravado e a importação segue sem sugestão. O botão "Atualizar perfil" na linha Classificar da Central refaz a consulta de um ativo (`POST /api/import-assets/stocks/{ticker}/profile/refresh`; falha da fonte vira 502) e recarrega a sugestão. A F63 não mostra setor ao lado da sugestão, então não lê desta tabela.

### M1 · arquivado em 2026-10-17

*Marco:* Números confiáveis · serve N3

> **Objetivo:** O que aparece na tela é o que está no banco, e retomar uma simulação dá o mesmo resultado que rodar direto.

### M2 · arquivado em 2026-10-17

*Marco:* Baixar e jogar · serve N1, N14

> **Objetivo:** Abrir o executável numa máquina limpa e chegar ao lobby sem instalar nada, e atualizar de versão sem perder os saves.

### M5 · arquivado em 2026-10-17

*Marco:* Análise de desempenho · serve N5, N6

> **Objetivo:** Ver o risco por trás do retorno e comparar simulações lado a lado.

### M7 · arquivado em 2026-10-17

*Marco:* Relatório de fim de partida · serve N5, N6, N9

> **Objetivo:** Ver o desempenho por dimensão ao longo do tempo e numa nota geral, na partida e na comparação.

### M10 · arquivado em 2026-10-17

*Marco:* Custos do mercado real · serve N7

> **Objetivo:** Operar paga o que pagaria fora do simulador: impacto de preço e imposto.

### M12 · arquivado em 2026-10-17

*Marco:* Interface nova · serve N15

> **Objetivo:** O app inteiro no visual novo, sobre componentes padronizados e dependências em dia.
