<!-- MANTIDO POR scripts/roadmap.py (skill feature-roadmap) -- entradas chegam só pelo comando `archive`. -->

# Arquivo morto — Roadmap do Simulador Financeiro

> Itens encerrados que saíram de [DECISIONS.md](DECISIONS.md) e do roadmap pelo comando `archive`, com o bloco do porquê e o card do kanban como estavam: itens concluídos ou descartados, decisões substituídas, marcos entregues, necessidades que o usuário deu por atendidas. O argumento de cada descarte mora aqui: um item novo é procurado neste arquivo antes de ser proposto.

## Itens concluídos

### F1 · arquivado em 2026-10-17

*Kanban:* Decimal como string do backend ao frontend · feature · ✅ Concluído · atende N3 · decisões D3 · marco M1

**F1 — Decimal como string do backend ao frontend.** Origem: #86. O `BaseDTO` deixou de converter `Decimal` para `float`, e o Pydantic serializa como string; os DTOs de dinheiro, quantidade monetária e taxa (carteira, posições, renda fixa, simulação, indicadores, eventos realtime de caixa e execução) e os requests de valor passaram a `Decimal`. O motor guarda caixa e posições em `Decimal`; preço de ação continua `float` na origem (`StockPriceHistory` é `Double`) e vira `Decimal` pelo texto (`to_money`) onde entra no caixa ou num evento. No front, `displayMoney`/`displayPercent`/`displayMoneyCompact` formatam a string direto pelo `Intl` (lib `ES2023.Intl`), e os requests mandam a string digitada. A conta da tela de Carteira subiu para o backend: o `PortfolioDTO` traz totais, alocação e rentabilidade prontos, o histórico patrimonial virou `/api/portfolio/history`, e `portfolio_update` substitui a carteira a cada tick. Limitações: a pizza da carteira soma no front os itens visíveis (interação do gráfico); o compacto do eixo passou a usar o sufixo pt-BR ("mil", "mi").
**Aceite:** todo valor exibido bate com o `NUMERIC(20,6)` do banco em todas as casas que a tela mostra.

### F2 · arquivado em 2026-10-17

*Kanban:* Renda fixa com cálculo único no backend e retomada consistente · feature · ✅ Concluído · atende N3 · decisões D1, D2, D6 · marco M1

**F2 — Renda fixa com cálculo único no backend e retomada consistente.** Origem: #85. `features/fixed_income/accrual.py` é a única fórmula: taxa efetiva (prefixado = taxa; CDI = CDI × percentual; IPCA+/SELIC+ composto, `(1 + índice) × (1 + spread) − 1`), fator diário `(1 + taxa)^(1/252)`, tabela regressiva de IR e resgate arredondado ao centavo. O tick ao vivo (`accrue`, idempotente por dia), a reconstrução e a projeção aplicam a mesma sequência de multiplicações em `Decimal`. Ao carregar, as posições são reconstruídas dos eventos BUY/REDEEM (D1), e as de ações também, repetindo compras e vendas com a mesma `Position`. A retomada segue a D6, sem reaplicar o aporte do mês, e o caixa reconstruído passou a somar os aportes. As posições de renda fixa são indexadas pelo `asset_uuid`, não pelo nome. `GET /api/fixed-income/{uuid}/projection` alimenta a tela de detalhe, e o front parou de projetar juros. Limitações: os indicadores (CDI, IPCA, SELIC) ainda são constantes em `EconomicRepository`, então a projeção do pós-fixado só coincide com o realizado enquanto continuarem constantes; o IR de vários aportes no mesmo título usa a data do primeiro.
**Aceite:** um prefixado comprado e levado ao vencimento credita o mesmo valor, ao centavo, rodando direto ou pausando e retomando no meio — e esse valor é igual à projeção mostrada no dia da compra (coberto em `tests/test_fixed_income_accrual.py` e verificado ponta a ponta: projeção R$ 12.778,14, resgate R$ 12.778,14 após parar e retomar).

### F3 · arquivado em 2026-10-17

*Kanban:* Spike: banco embarcado no executável · feature · ✅ Concluído · atende N1 · decisões D4 · marco M2

**F3 — Spike: banco embarcado no executável.** Decidiu a D4: Postgres oficial embarcado no executável do Windows. A medição usou um harness descartável que roda a `Simulation` real com 10 jogadores e threads gravando em paralelo, como requisições HTTP, sobre o Postgres e o SQLite, com os preços do banco de desenvolvimento (19.919 linhas) e uma variante de 100 ações (664 mil linhas); mais um executável de teste com o servidor embarcado, o app completo empacotado com um pacote de Postgres embarcado e o zip oficial da EDB extraído, iniciado e parado sem instalação. Os números e os argumentos estão na D4. Limitações: sobrecarga e 100 ações têm uma repetição cada; o Postgres rodou com a configuração padrão; o tempo de abertura do app completo e a máquina limpa (runtime do Visual C++) não foram medidos e ficam para o aceite da F4.

### F4 · arquivado em 2026-10-17

*Kanban:* Executável sobe sem banco instalado · feature · ✅ Concluído · atende N1 · decisões D4 · marco M2 · depende de F3

**F4 — Executável sobe sem banco instalado.** Serve N1; condicionada pela D4. No Windows o executável leva o Postgres oficial e abre sem nenhum passo extra. `scripts/build_postgres.py` (`pnpm build:postgres`, rodado pelo release só no job do Windows) baixa o zip oficial com versão e SHA-256 fixados, extrai `postgres`, `initdb`, `pg_ctl`, as DLLs, `lib`, `share` e as licenças, e roda o `initdb` uma vez (UTF8, localidade `C.UTF-8` embutida, fuso America/Sao_Paulo), gerando `postgres.zip` e `cluster.zip`, que o `.spec` empacota em `backend/postgres`. `backend/core/embedded_postgres.py` cuida do ciclo de vida: `resolve_database_url()` devolve o `POSTGRES_DATABASE_URL` quando definida (o `.env` deixa de ser obrigatório e o servidor não sobe) ou sobe o embarcado; extrai binários e banco uma vez em `%LOCALAPPDATA%/SimuladorFinanceiro`, sobe o `postgres.exe` numa porta livre só em 127.0.0.1, sorteia a senha do superusuário na primeira abertura e passa a exigir `scram-sha-256`. O servidor fica preso ao processo do app por um Job Object, que o Windows encerra em qualquer queda, e o encerramento limpo roda no `atexit` e nos eventos de console (Ctrl+Break, fechar a janela, logoff, desligamento). `database.py` e `main.py` passaram a usar `resolve_database_url()`; Linux e macOS não embarcam nada e seguem com `POSTGRES_DATABASE_URL`. A página de instalação e o README foram reescritos, e o workflow `postgres-version.yml` compara toda segunda a versão fixada com a mais recente. Referência de desenho: o Karaoke Mugen, aplicativo desktop de código aberto, embarca o Postgres por padrão, aceita um externo por configuração, confere o runtime do Visual C++ e limpa servidor órfão. Medido no app completo: 112,1 MB (eram 60,4); primeira abertura numa máquina limpa simulada em cerca de 10 s; reabertura em 6,8 s, igual à do mesmo executável com banco externo; fechar o app à força não deixa servidor para trás. Limitações: a verificação foi num Windows que já tem Postgres instalado (o executável não o usa) e com o runtime do Visual C++ presente, então a máquina realmente limpa continua por testar; o fechamento pelo X da janela não foi exercitado, só Ctrl+Break; o macOS não embarca (a EDB tem o zip oficial e entra pelo mesmo caminho); uma versão principal nova do Postgres exige exportar e importar o banco.

**Aceite:** numa máquina Windows sem Postgres e sem `.env`, baixar o release e abrir o executável leva ao lobby sem nenhum passo extra, e a segunda abertura chega ao lobby sem rodar o `initdb`.

### F11 · arquivado em 2026-10-17

*Kanban:* Métricas de risco do desempenho · feature · ✅ Concluído · atende N5 · decisões D1, D2 · marco M5

**F11 — Métricas de risco do desempenho.** Origem: #5. O snapshot passou a ser diário (um por jogador por dia útil); `statistics_snapshot_update` continua saindo só na virada do mês, para a tela de Estatísticas não buscar o histórico inteiro a cada tick, e `snapshot_update` (merge por data na Carteira) sai todo dia. O `total_fixed` do snapshot vem das posições em memória do motor, como o `total_equity`, e a tabela `fixed_income_position`, que só existia para alimentá-lo, saiu do modelo. Medido em 100× com 4 jogadores: o tick foi de ~49 ms para ~64 ms (~4,5 ms por jogador). `features/statistics/risk.py` calcula em `Decimal`, a partir dos snapshots (D1) e no backend (D2), o retorno de cada dia descontado o aporte do dia, e sobre ele:
- **Drawdown máximo:** a maior queda a partir de um pico numa cota que só os rendimentos movem (como a cota de um fundo), então o aporte não disfarça a queda. Ex.: o patrimônio sobe a R$ 15.000 e cai a R$ 12.000 → 20%. Quanto menor, melhor; acima de ~30% é uma queda que a maioria das pessoas não aguenta sem vender.
- **Volatilidade anual:** desvio-padrão amostral dos retornos diários × √252. Ex.: ~1% ao ano é renda fixa; ~25% é uma carteira só de ações.
- **Índice de Sharpe:** (retorno anual − CDI anual) ÷ volatilidade anual, com o retorno anual e o CDI anual como a média diária × 252; o CDI de cada dia sai do mesmo fator diário da renda fixa. Ex.: retorno de 18%, CDI de 10%, volatilidade de 16% → 0,5. Abaixo de 0 perdeu para o CDI; perto de 1 é bom; acima de 2 é raro.

`RiskMetricsDTO` vem aninhado em cada jogador de `/api/statistics` e `/api/statistics/compare`; cada métrica é `null` enquanto a série é curta demais (drawdown a partir do 2º dia, volatilidade e Sharpe a partir do 3º; Sharpe também sem oscilação). Na tela de Estatísticas, o card "Risco da sua carteira" mostra as três com o número de dias da amostra, uma descrição curta ao lado e um tooltip com definição, exemplo e faixa boa/ruim; o ranking (e a comparação) ganhou as três colunas com o mesmo tooltip. O `FieldHint` do lobby virou `shared/components/info-hint.tsx`. Limitações: o CDI ainda é constante em `EconomicRepository`; save anterior tem só os pontos mensais antes da retomada, que entram como um "dia" de variação maior; com volatilidade perto de zero (só renda fixa) o Sharpe fica grande em módulo.
**Aceite:** numa série sintética com pico de R$ 15.000 e vale de R$ 12.000, a API retorna drawdown de 20,00% (coberto em `tests/test_statistics_risk.py`, junto com aporte que não esconde queda e volatilidade/Sharpe conferidos à mão).

### F12 · arquivado em 2026-10-17

*Kanban:* Comparação entre simulações · feature · ✅ Concluído · atende N6 · decisões D2 · marco M5

**F12 — Comparação entre simulações.** Origem: #84. O ranking subiu para o backend (D2): `features/statistics/ranking.py` calcula em `Decimal`, a partir do último snapshot de cada jogador, o capital aportado (saldo inicial + aportes), o retorno em R$ e em % e a posição, além da média da sala. `GET /api/statistics` passou a devolver esse relatório pronto (`PerformanceReportDTO`). `GET /api/statistics/compare?simulation_ids=…` devolve o mesmo relatório para várias simulações salvas, sem exigir partida ativa; `StatisticsRepository.get_players_history` recebe os ids e traz o nome de cada simulação. No front saíram `build-ranking.ts` e `build-match-summary.ts`. A tela de Estatísticas refaz a busca a cada `statistics_snapshot_update`. O gráfico de desempenho guarda a string original para o tooltip, que agora mostra os valores em R$. A tela `/compare-simulations` abre pelo botão "Comparar Simulações" do lobby: uma sidebar com checkbox por simulação salva, e o gráfico e o ranking com séries `Nick#Simulação`. O registro recusa `#` no nickname. Patrimônio zero passou a valer −100% de retorno. Limitação: o eixo X é a data, então simulações de períodos diferentes aparecem em trechos diferentes do eixo, não sobrepostas.
**Aceite:** marcar duas simulações salvas mostra `Lilo#Teste M1 103121` (2,18%) e `Lilo#Simulação #4` (0,00%) no gráfico e no ranking, com tooltip em R$.

### F13 · arquivado em 2026-10-17

*Kanban:* Impacto de preço de ordens grandes · feature · ✅ Concluído · atende N7 · decisões D1 · marco M10

**F13 — Impacto de preço de ordens grandes.** Origem: #59. Ligável por partida no lobby: `price_impact_enabled`, `price_impact_k` e `price_impact_decay_days` são colunas de `simulations` (padrões em `[simulation]` do TOML), então a partida retoma com a mesma configuração. `features/variable_income/price_impact.py` é a única fórmula: a quantidade líquida do dia por ativo (compras − vendas dos jogadores, de `event_equity`) gera impacto = k × √(quantidade ÷ volume médio dos últimos 20 pregões); o impacto vale cheio no pregão seguinte e decai por (1 − t/T)², com t = 0 nesse primeiro pregão, durando T pregões. O preço do dia é o OHLC histórico × (1 + soma dos impactos ativos), piso 0,01, no centavo. Agregar por dia faz o fatiamento de uma ordem em várias execuções não mudar nada, e compra e venda iguais entre jogadores se anulam. O impacto é derivado dos eventos (D1) a cada tick, depois de um flush que leva ao banco as ordens enviadas entre ticks, então retomar reconstrói os mesmos preços. Vale na lista de ativos, no detalhe e no histórico do gráfico (cada dia com o seu fator), no market maker e no matching, na carteira e no snapshot mensal, que passou a receber do motor o valor das ações. Padrões: k = 0,02 (próximo do mercado real), T = 20. Limitações: sem migração, banco anterior à F13 fica incompatível (nova release, novo save); o histórico do detalhe recalcula o fator de cada dia a cada abertura da tela.
**Aceite:** com k = 0,02, comprar 10% do volume médio desloca o preço do pregão seguinte em +0,63% e o desvio some depois de T pregões (coberto em `tests/test_price_impact.py`).

### F17 · arquivado em 2026-10-17

*Kanban:* Estatísticas em abas, como o relatório de fim de partida de um RTS · feature · ✅ Concluído · atende N5, N6 · decisões D2 · marco M7

**F17 — Estatísticas em abas, como o relatório de fim de partida de um RTS.** Serve N5 e N6. Inspiração: a tela de estatísticas do fim de partida do Age of Empires II. `GET /api/statistics` e `/api/statistics/compare` deram lugar a um endpoint por aba — `/api/statistics/{overview,returns,risk,composition,operations}?simulation_ids=…` —, todos sobre os snapshots diários da F11 e sem exigir partida ativa: a tela de Estatísticas passa o id da partida em andamento, a comparação passa os escolhidos, e o fechamento (F27) vai passar o da partida encerrada. O cálculo fica em `features/statistics/` (D2), montado por `report.py`: **Geral** (ranking e resumo da partida); **Rentabilidade** (patrimônio e retorno acumulado da cota dia a dia, com o CDI e o Ibovespa da F20 como linhas tracejadas, e uma tabela com capital aportado, retorno anual composto, meses acima do CDI e meses no positivo); **Risco** (curva de distância do pico, volatilidade em janela móvel de 63 pregões, dispersão risco × retorno e a tabela com drawdown, volatilidade, Sharpe, Sortino, maior tempo abaixo do pico, pior mês e a amostra); **Composição** (área empilhada de caixa, renda variável e renda fixa, e o recorte por setor da F30: exposição de cada jogador no último dia, número efetivo de setores — 1 ÷ Σ fração² — e lucro por setor, reconstruídos de `event_equity` a preço do dia com o fator de impacto); **Operações** (volume negociado por mês, compras, vendas, giro, o IR pago da F29 e o custo de impacto da F13 — executado menos histórico, com o sinal de quem paga —, para o qual `PriceImpact.factors_on` virou público). No front, `StatisticsReport` (`features/statistics/components/statistics-report/`) serve a partida e a comparação; cada aba busca os próprios dados quando abre, e cada métrica tem descrição curta e dica com definição, exemplo e leitura (`lib/metrics.ts`). O `PerformanceChart` virou o gráfico de linha genérico das abas. A aba Geral ganha a nota com a F18. Limitações: o Sortino de uma carteira parada em caixa fica muito negativo (perde para o CDI todo dia com oscilação quase nula); na comparação, simulações de períodos diferentes aparecem em trechos diferentes do eixo.
**Aceite:** numa partida de dois jogadores com impacto ligado, as cinco abas mostram as curvas por jogador com CDI e Ibovespa de referência, Lilo com 69,84% em Financeiro e número efetivo de 1,87, e a comparação abre o mesmo relatório com séries `Nick#Simulação` (cálculos cobertos em `tests/test_statistics_{risk,returns,sectors,operations}.py`).

### F18 · arquivado em 2026-10-17

*Kanban:* Pontuação geral (overall) · feature · ✅ Concluído · atende N9 · decisões D10 · marco M7

**F18 — Pontuação geral (overall).** Serve N9; segue a D10. Uma nota por jogador, decomposta por eixo e por métrica, na aba Geral da F17 e no ranking, que passou a ordenar por ela (quem ainda não tem nota vem depois, e o retorno desempata). `features/statistics/score.py` guarda as faixas como tabela de dados: cada métrica vira pontos numa reta entre o valor que vale 0 e o que vale 100, com chão 0 e sem teto; cada eixo é a média das suas métricas medidas, e a nota é a soma dos quatro. **Retorno:** retorno anual acima do CDI (−10 p.p. → 0, +10 p.p. → 100) e acima do Ibovespa (−15 → 0, +15 → 100). **Risco:** queda máxima (50% → 0, 0% → 100), volatilidade (40% → 0), maior tempo abaixo do pico (252 pregões → 0) e pior mês (−20% → 0). **Consistência:** fração dos meses acima do CDI e no positivo. **Eficiência:** Sharpe (−1 → 0, 2 → 100) e Sortino (−1 → 0, 3 → 100). A nota só aparece a partir de 63 pregões; antes, a aba Geral mostra quantos faltam. `ScoreDTO` vem em cada jogador de `/api/statistics/overview`, com o valor e os pontos de cada métrica, e o card "Nota" mostra cada eixo com uma barra e cada métrica como "queda máxima 13,65% → 72,7 pts". A página de estatísticas dos docs tem a fórmula em LaTeX (`remark-math` + `rehype-katex`, com o `$` simples desligado por causa do "R$"), a tabela de faixas e um exemplo completo. Limitação: risco e consistência param perto de 100 e retorno e eficiência não, então uma carteira parada em caixa fica com ~100, quase tudo do eixo Risco.
**Aceite:** na partida de teste, Lilo tem Retorno 58,3 + Risco 71,8 + Consistência 41,7 + Eficiência 40,4 = 212 e lidera o ranking; a soma dos eixos bate com o total (coberto em `tests/test_statistics_score.py`).

### F20 · arquivado em 2026-10-17

*Kanban:* Indicadores reais (CDI, SELIC, IPCA) do Banco Central · feature · ✅ Concluído · atende N11 · decisões D7 · marco M8 · dependência de F23

**F20 — Indicadores reais (CDI, SELIC, IPCA) do Banco Central.** Serve N11. As constantes do `EconomicRepository` saíram: as séries moram em `economic_indicator_history` (série, data, `NUMERIC`, origem — D7), com `fetch_log` registrando tentativa e sucesso, e as antigas `ipca_history`/`selic_history`, que nada lia, foram removidas na mesma migration; `stock_price_history` também ganhou a coluna de origem. A busca segue o desenho do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): SGS do Banco Central (séries 12, 11 e 433) em janelas de até 10 anos, valor lido do texto direto para `Decimal`, e IBOV pelo yfinance (`^BVSP`) na mesma tabela. A primeira carga traz a série inteira; as seguintes recomeçam no dia 1 do mês do último valor; a inicialização dispara a busca numa thread, respeitando o intervalo de 6 horas, e falha mantém o que está no banco. Na renda fixa, o tick rende com a taxa do dia útil anterior (a taxa de um dia paga a noite até o próximo): CDI e SELIC viram o fator do dia direto, dia sem valor publicado dentro da série é feriado e não rende, o IPCA do mês se distribui pelos dias úteis do mês, e depois do último dado real vale o último valor conhecido. A projeção na compra congela o último valor conhecido. A taxa anual mostrada no card e usada pelas fábricas de títulos é a do dia composta por 252 dias úteis (IPCA: acumulado de 12 meses), e o Sharpe desconta o CDI diário real. A partida só é criada (ou carregada) quando CDI, SELIC e IPCA têm dado no dia de início. Resolve a limitação de CDI constante da F2 e da F11.
**Aceite:** um CDB 100% do CDI de 02/01/2020 a 31/12/2020 rende, antes do IR, o índice 1,02750141 que a Calculadora do Cidadão do Banco Central dá para o mesmo período (teste com o CDI real de 2020).

### F21 · arquivado em 2026-10-17

*Kanban:* Central de dados, fora da partida · feature · ✅ Concluído · atende N13, N3 · decisões D7 · marco M8 · dependência de F24

**F21 — Central de dados, fora da partida.** Serve N13 e N3. `/import-assets` virou a Central de dados, aberta pelo botão do lobby: além dos formulários de importação por yfinance e CSV, uma tabela com toda série da base — indicadores (F20) e ações — com início, fim do dado real, fim do dado gerado (D7, vazio até a F24) e uma barra de linha do tempo por série num eixo comum, com o trecho real e o gerado em cores diferentes. Cada série se atualiza pelo botão da linha (indicador ignora o intervalo de 6 horas) e "Atualizar todos" busca os indicadores e as ações desatualizadas. A cobertura vem de `GET /api/import-assets/coverage`, numa consulta agrupada no lugar do `/status` que fazia uma consulta por ação. A Central é só de fora da partida: o router de `/api/import-assets` responde 409 com partida ativa e o guard manda `/import-assets` para `/` durante o jogo. No lobby, o período é conferido contra a cobertura: indexador sem dado na data inicial bloqueia o botão de iniciar (o backend também recusa), e série cujo dado real termina antes da data final gera um aviso. Um `Alert` entrou no design system para os dois casos.

### F25 · arquivado em 2026-10-17

*Kanban:* Migrations com Alembic · feature · ✅ Concluído · atende N14, N1 · decisões D9 · marco M2

**F25 — Migrations com Alembic.** Origem: as mudanças de schema da F11 e da F13, que deixaram os bancos anteriores incompatíveis. O `create_all` saiu de `get_engine()`, e o `main.py` chama `migrate()` (`backend/core/migration.py`) antes de subir o uvicorn; `MigrationError` encerra o app com a mensagem no console (no executável, esperando um Enter). O Alembic é configurado no `pyproject.toml` (`[tool.alembic]`, com `ruff` nos hooks de escrita), `pnpm db:revision "<descrição>"` gera a revisão por autogenerate a partir dos models (D9), e o `sqlacodegen` saiu das dependências e do `.spec`. A primeira revisão (`243ae671fdc0`) é o schema atual; a v1.0.0 e bancos de desenvolvimento entre releases não migram. O `migrate` decide pelo estado do banco: vazio recebe todas as migrations; no head, nada; sem `alembic_version` e igual aos models (um banco do `create_all` atual), é marcado no head; sem `alembic_version` e diferente, é recusado; numa revisão anterior, as migrations rodam antes numa cópia (`<banco>_dryrun`, `CREATE DATABASE ... TEMPLATE`), que recusa o upgrade se alguma tabela perder linha ou célula preenchida, e depois um backup `<banco>_bkp_AAAAMMDD_HHMMSS` (ficam os 3 mais recentes) antecede o upgrade real. O `resource_path` acha `backend/migrations` em dev e no executável, que a empacota como dado. `tests/test_migrations.py` (Postgres do `.env`, banco descartável por teste, pulado sem servidor) confere que as migrations chegam exatamente no schema dos models, que toda revisão desce e sobe, o `stamp` do banco do `create_all` e a recusa do banco antigo. A página "Ciclo de desenvolvimento com banco de dados" dos docs foi reescrita para o ciclo novo, com o que o autogenerate não cobre (valor novo em `ENUM` nativo, `ENUM` no downgrade, `NOT NULL` em tabela com dado, rename). O banco local de desenvolvimento ficou preservado como `simulador_financeiro_pre_alembic`. Limitações: a cópia exige o banco sem outras conexões abertas (pgAdmin, DBeaver); a contagem de células não pega dado alterado sem ser apagado.
**Aceite:** com uma revisão de teste que adiciona coluna, um banco com 6.721 preços migra com backup e sem perder linha; uma que remove coluna com dado é recusada no ensaio e o banco fica intacto.

### F26 · arquivado em 2026-10-17

*Kanban:* Redesign visual · feature · ✅ Concluído · atende N15 · marco M12 · depende de F36 · dependência de F37

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

*Kanban:* Fechamento de partida: pódio e critério de vitória · feature · ✅ Concluído · atende N5, N6, N9 · decisões D8 · marco M7 · depende de F17, F18

**F27 — Fechamento de partida: pódio e critério de vitória.** Serve N5, N6 e N9; segue a D8. Quando a partida chega na data final ou o host encerra, o `simulation_ended` passou a levar o id da simulação, e o `SimulationProvider` leva todos para `/match-result/:id` no lugar do toast e do lobby: o título "Fim de partida", o pódio com os três primeiros e o valor que decidiu cada posição, o relatório da F17 sobre a partida inteira (com a classificação completa e a nota na aba Geral) e "Voltar ao lobby". A rota muda antes de o status da partida ser atualizado, porque o guard tira da tela de Estatísticas quem estiver lá com a partida inativa. O fim por data passou a fazer o mesmo que o `stop()`: o flush dos eventos do último dia e a liberação da simulação antes do aviso, então o fechamento lê a partida inteira. A mesma tela abre depois, para qualquer simulação salva, pelo "Ver resultado" da lista de simulações salvas do lobby, que agora abre para todos os jogadores (carregar continua só do host). **Critério de vitória:** como as condições de vitória do Civilization VI, o host escolhe no lobby entre nota geral (padrão, F18), rentabilidade, patrimônio final ou Sharpe; é a coluna `victory_criterion` de `simulations` (ENUM, migration com `server_default` para as partidas salvas) e ordena o ranking durante a partida e o pódio, com o retorno desempatando e quem ainda não tem o valor (a nota antes de 63 pregões, o Sharpe sem oscilação) no fim. Na comparação de simulações com critérios diferentes, vale a nota geral. É diferente da tela de comparação: a comparação põe resultados lado a lado, o pódio declara quem venceu. Limitação: quem entra pelo navegador com a partida já rodando cai no lobby até recarregar a página (comportamento anterior à F27).
**Aceite:** uma partida de quatro jogadores levada até a data final leva a aba aberta em Estatísticas para `/match-result/3`, com Lilo em 1º por 285 pts de nota; uma partida encerrada pelo host abre a mesma tela pelo "Ver resultado" (ranking por critério coberto em `tests/test_statistics_ranking.py`).

### F29 · arquivado em 2026-10-17

*Kanban:* IR na venda de renda variável · feature · ✅ Concluído · atende N7 · decisões D1 · marco M10

**F29 — IR na venda de renda variável.** Serve N7. `features/variable_income/income_tax.py` é o motor fiscal do [Finance Manager](https://github.com/LiloMarino/Finance-Manager) portado para os eventos de `event_equity`, recalculado das operações a cada consulta (D1). Todo mês, por jogador, o lucro das vendas sobre o preço médio fiscal vai para três conjuntos de compensação: comum (ação, ETF e BDR, 15%), day trade (20%) e FII (20%). Compra e venda do mesmo ativo no mesmo dia se pareiam como day trade, a 1ª compra com a 1ª venda, e só as sobras movem o preço médio, que por isso tem replay próprio, separado da posição do `Broker`. O ganho comum com ações é isento quando as vendas de ações do mês somam até R$ 20.000. O prejuízo de cada conjunto abate o lucro dos meses seguintes, e o imposto abaixo de R$ 10 soma ao do mês seguinte. No último dia útil do mês, o tick debita o DARF do mês anterior como evento `TAX` de `event_cashflow`. A retomada começa no dia seguinte ao último evento, então nenhum DARF sai duas vezes. O caixa pode ficar negativo, como uma dívida com a Receita. `stock` ganhou `asset_class` (ação, FII, ETF, BDR): na importação a classe é inferida pelo sufixo do código (31 a 35 e 39 viram BDR, 11 vira FII, o resto vira ação), e na Central de dados um seletor a corrige, porque ETFs e units também terminam em 11. A migration aplica a mesma regra às ações já importadas. A carteira mostra o card "Imposto de Renda", com o IR pago, o valor a pagar (o já apurado que não venceu, mais o mês corrente) e a regra explicada na dica. A aba Operações da F17 lê o mesmo evento `TAX` quando for feita. Limitações: a regra fiscal atual vale para qualquer período histórico simulado; o IRRF de 0,005% fica fora, porque é antecipação do mesmo imposto; e uma partida que termina antes do vencimento não debita o último mês, que fica só como "a pagar".
**Aceite:** vender R$ 30.000 em ações com R$ 5.000 de lucro num mês debita R$ 750 no mês seguinte; vender R$ 15.000 com lucro no mês não debita nada.

### F30 · arquivado em 2026-10-17

*Kanban:* Setores e segmentos · feature · ✅ Concluído · atende N16

**F30 — Setores e segmentos.** Serve N16. Mesmo modelo do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): tabelas `sectors` (nome único) e `segments` (nome único dentro do setor), com `segment_id` anulável em `stock` (`ON DELETE SET NULL`). `StockRepository.classify` cria setor e segmento pelo nome na primeira vez e apaga o que fica sem nenhuma ação, então a lista de sugestões só tem o que está em uso. Na importação, enquanto a ação não tem classificação, o `sector` e a `industry` do `yf.Ticker().info` viram a sugestão: os 11 setores do yfinance chegam nos nomes da B3 (Financial Services → Financeiro), a indústria vira o segmento como veio; a classificação feita à mão não é trocada. Na Central de dados (F21), a coluna "Setor / Segmento" abre a janela Classificar, com as sugestões de `GET /api/import-assets/sectors` (`PUT`/`DELETE /stocks/{ticker}/segment`). A carteira ganhou o card "Renda Variável por Setor" (barras e tabela de valor e fração por setor e segmento, "Sem setor" para o que não foi classificado), calculado no backend em `backend/core/sectors.py` (`PortfolioDTO.sectors`); o motor lê a classificação uma vez por partida, porque a Central só abre com a partida parada. O recorte por setor das estatísticas entra na aba Composição da F17. "A estratégia enxerga o setor" ficou para a F7/F8: o dado está em `get_classification`, e o que a estratégia vê é decidido no spike. Limitação: o segmento sugerido vem em inglês (*Banks - Regional*) até ser editado.
**Aceite:** importar ITUB4 e VALE3 pelo yfinance as classifica em Financeiro · Banks - Regional e Materiais Básicos · Other Industrial Metals & Mining, e a PETR4 classificada à mão continua como estava (coberto em `tests/test_sectors.py`).

### F31 · arquivado em 2026-10-17

*Kanban:* Diagrama do banco sempre em dia · feature · ✅ Concluído · atende N17 · decisões D9

**F31 — Diagrama do banco sempre em dia.** Serve N17; segue a D9. Primeira versão do diagrama: um `erDiagram` em Mermaid por domínio, gerado dos models por `scripts/erd.py` e conferido por `tests/test_erd.py`, que falhava enquanto a página estivesse defasada. Substituída pela [F50](#f50): um diagrama só, navegável, gerado dentro do build dos docs.

### F32 · arquivado em 2026-10-17

*Kanban:* Ferramenta de correlação entre ativos · feature · ✅ Concluído · atende N18 · decisões D2

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

*Kanban:* Dependências em dia · feature · ✅ Concluído · atende N15 · marco M12

**F35 — Dependências em dia.** Serve N15. Feito em dois passos, cada um fechado com `pnpm check`. (1) Versões menores: `pnpm update` no frontend e `uv lock --upgrade` no backend. (2) Versões maiores, uma por commit: Vite 8 com o `@vitejs/plugin-react` no lugar do `-swc`; ESLint 10 com `eslint-plugin-react-hooks` 7, cujas regras do React Compiler pediram ajustes (`useEffectEvent` no `useRealtime`, sem `setState` dentro de efeito); `globals`, `eslint-plugin-react-refresh` e `@types/node` atualizados. O TypeScript parou no 6: o `typescript-eslint` ainda não aceita o 7. O `framer-motion` saiu do projeto, porque o único uso era a página 404, refeita sem animação na F26. O Recharts 3 entrou na F36. Limitação: subir para o TypeScript 7 quando o `typescript-eslint` suportar.

### F36 · arquivado em 2026-10-17

*Kanban:* Interface padronizada no shadcn · feature · ✅ Concluído · atende N15 · decisões D11 · marco M12 · depende de F35

**F36 — Interface padronizada no shadcn.** Serve N15; decidiu a D11 pelo Base UI. O `components.json` está no preset `base-nova` (`@base-ui/react`), com o pacote `shadcn` importado no CSS (`@import "shadcn/tailwind.css"`, que traz as variantes `data-*` dos componentes). Os componentes de `shared/components/ui` foram recriados pela CLI, e os que faltavam entraram conforme as telas pediram: toggle-group, empty, avatar, field, radio-group, popover, progress, switch, input-group, textarea, sheet, skeleton e separator; o `form.tsx` saiu, sem uso. A CLI do registro grava `import ... from "cn"` e adiciona um pacote `cn` falso: o import é corrigido para `@/shared/lib/utils` a cada componente novo. Os `asChild` fora de `ui/` viraram a prop `render`; o Recharts foi para a versão 3. Aparência nova é sempre variante no componente, e o `@shadcn/lint` garante isso: `no-restyle` (só classes de layout por fora) e `no-raw-colors` (só tokens), que entraram como aviso durante a migração e terminaram como erro. Os 14 elementos feitos à mão viraram o componente equivalente na tela da F26 que os redesenhou.

### F38 · arquivado em 2026-10-17

*Kanban:* Mensagens do backend em português · feature · ✅ Concluído · atende N15

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

*Kanban:* Cor exclusiva e sigla de duas letras por jogador · feature · ✅ Concluído · atende N20 · dependência de F42

**F39 — Cor exclusiva e sigla de duas letras por jogador.** Serve N20. Inspiração: o Age of Empires II, que dá uma cor própria a cada um dos 8 jogadores da partida; aqui a sala vai a 10. Antes, a cor do jogador nascia em dois lugares que não se falavam (um hash do apelido no lobby, no perfil, na sidebar e no livro de ofertas; a posição alfabética nas estatísticas) e a sigla era a primeira letra do apelido. Agora: (1) **a cor é do jogador na partida.** Enquanto está na sala ela vive na memória do servidor (`UserManager`); ao iniciar vira linha de `simulation_players` (`simulation_id`, `user_id`, `color`, chave composta, migration pela D9), que as Estatísticas e o fechamento leem, inclusive dias depois, sem partida ativa. As partidas salvas antes ganharam as linhas na própria migration. (2) **Dez jogadores, dez cores.** `--chart-9` (cinza) e `--chart-10` (marrom) entram na paleta do redesign. O teto da sala é o tamanho da paleta e o servidor recusa o 11º conectado (423, "a sala está cheia"). A conferência de daltonismo (lima × âmbar, verde-água × ciano) continua em aberto. (3) **Conflito é impedido, não detectado.** Ao entrar o jogador recebe a primeira cor livre; a troca é `PUT /api/simulation/players/me/color` e o servidor recusa com 409 se a cor já tem dono (vale o primeiro pedido, quem perdeu fica com a anterior); o evento `player_color` avisa a sala. No seletor "Sua cor" a cor ocupada aparece apagada com a sigla de quem a tem. (4) **A preferência mora no navegador** (`localStorage`): ao entrar o cliente pede a última cor escolhida e fica com a que recebeu se ela já tiver dono. (5) **Sigla sempre de duas letras**, calculada no front por `playerInitials` (acento e emoji contam inteiros) e desenhada pelo `PlayerAvatar` de `shared/`, que substituiu os sete `Avatar` com `charAt(0)`; a sigla sai do apelido, nunca do rótulo " · A". (6) **Uma fonte de cor só no front:** `stringToColor` e `playerColors` saíram; lobby, perfil, sidebar, livro de ofertas, ranking, pódio e gráficos leem a cor do payload. A comparação de simulações segue colorindo por partida (a letra e a cor da F17), com avatares neutros. (7) **Quem participa é quem está na sala ao iniciar**: só eles recebem o depósito inicial e snapshots (antes era toda conta do banco). Quem não participa de uma partida em andamento escolhe uma cor e entra pela F58. (8) **Continuar uma partida salva tem dois passos**: o host a seleciona (`PUT /api/simulation/selection`) e a sala inteira troca para as cores guardadas, travadas para quem já jogou e reservadas para os ausentes; depois clica em Continuar. Quem está na sala e nunca jogou a partida escolhe entre as cores que sobraram e entra com o depósito inicial na retomada. Os bots da F16 não existem ainda e contarão no mesmo teto.

### F43 · arquivado em 2026-10-17

*Kanban:* Spike: outros modos de jogo · feature · ✅ Concluído · atende N23 · marco M13

**F43 — Spike: outros modos de jogo.** Serve N23. Decidido com o usuário: entram a corrida à meta (F52) e o viver de renda (F53), além das equipes (F42). Ficaram de fora, por ora: eliminação (a cada trimestre o último sai, até sobrar um), cenário com objetivo (começar numa crise histórica com uma meta, como uma campanha de RTS) e todos contra o índice (a sala inteira numa equipe contra o CDI e o Ibovespa).

### F46 · arquivado em 2026-10-17

*Kanban:* Console do navegador no terminal do dev · feature · ✅ Concluído

**F46 — Console do navegador no terminal do dev.** O Vite 8 tem `server.forwardConsole`; em `frontend/vite.config.ts` ele está ligado com `{ unhandledErrors: true, logLevels: ["error", "warn"] }`. No `pnpm dev`, `console.error`, `console.warn`, exceção não tratada e promessa rejeitada sem tratamento aparecem no terminal do Vite como `[vite] (client) [console.error] ...`, as duas últimas com o trecho do código de origem; `console.log` fica de fora. Vale para o desenvolvimento, não para o executável. O ganho principal é para o agente de código, que lê o terminal mas não o console do navegador.

### F50 · arquivado em 2026-10-17

*Kanban:* Diagrama do banco navegável · feature · ✅ Concluído · atende N17 · decisões D9

**F50 — Diagrama do banco navegável.** Serve N17; segue a D9. A página "Diagrama do Banco de Dados" tem um diagrama só, com zoom, arraste, busca e os ENUMs numa tabela abaixo, no [ERD Editor](https://github.com/dineug/erd-editor) (`@dineug/erd-editor` 4.0, MIT) embutido como componente do Docusaurus. **100% gerado, sem passo manual:** `scripts/erd.py` lê o `Base.metadata` e escreve o DDL do Postgres (`CreateTable` do SQLAlchemy) em `docs/src/generated/schema.json` e a tabela dos ENUM em `docs/docs/desenvolvimento/_enums.md`; os dois rodam no `prestart`, `prebuild` e `pretypecheck` dos docs (`pnpm db:erd`) e no `deploy-docs.yml`, que ganhou `uv sync` e passou a disparar também por mudança em `backend/core/models/**`. Os arquivos gerados não são versionados, e o `tests/test_erd.py` saiu. O componente `DatabaseDiagram` (`BrowserOnly`) cria o `<erd-editor>`, carrega o DDL com `setSchemaSQL(..., { placement: 'auto' })`, enquadra o diagrama inteiro no zoom inicial e segue o tema claro/escuro do Docusaurus. O editor abre editável e nada é salvo: arrastar tabelas, reorganizar e esboçar uma modelagem ("e se fosse 1-N aqui?") valem só até recarregar, quando o diagrama volta ao schema dos models. **A escolha:** os dois visualizadores foram prototipados sobre o schema de hoje. O React Flow desenhava a notação do MySQL Workbench, mas as linhas se embaraçavam perto das tabelas de evento e foco numa tabela, layout automático e busca teriam de ser construídos. O ERD Editor traz isso pronto (foco numa tabela e nas vizinhas com `Alt+F`, *Auto Layout* por Force, Flow ou árvore, só as colunas de chave, busca por tabela e coluna), e a notação do Workbench foi dispensada: as chaves vêm coloridas (PK amarela, FK vermelha, PK que também é FK azul) e a obrigatoriedade aparece em texto. O modo somente leitura do editor trava também o arrasto, por isso ele não é usado. Limitação: o layout inicial ainda embaraça as linhas perto das tabelas de evento; *Auto Layout* → *Force* (`Ctrl+K`) as separa. O pacote pesa cerca de 11 MB, carregados só na página do diagrama.
**Aceite:** alterar um model e subir `pnpm start` nos docs mostra a mudança no diagrama sem rodar nada à mão.

### F51 · arquivado em 2026-10-17

*Kanban:* Versão única e changelog · feature · ✅ Concluído · atende N14 · decisões D12 · dependência de F56

**F51 — Versão única e changelog.** Serve N14; segue a D12. A versão estava em quatro lugares que não se falam: digitada à mão no `workflow_dispatch` do `release.yml`, `0.1.0` no `pyproject.toml`, `0.0.0` nos `package.json` do frontend e dos docs, e `1.0.0` fixo no `FastAPI(...)` do `main.py`; e não existia changelog (as notas da v1.0.0 eram a lista automática de PRs, com atualização de dependência do Dependabot, ilegível para quem joga). Agora: (1) **Uma fonte só** — a versão mora no `pyproject.toml` (2.0.0) e o `get_version()` (`backend/core/version.py`) a lê com `tomllib`; o `pyproject.toml` vai no executável (`datas` do `.spec`), já que o projeto não é um pacote instalável e não há `importlib.metadata`. `GET /api/version` a expõe, e o `FastAPI(version=...)` (e com ele o `openapi.json`) usa o mesmo valor. O campo `version` saiu dos `package.json` (pacotes privados). O `release.yml` não recebe mais a versão digitada: o job `validate` a lê do `pyproject.toml`, falha se a tag já existir e confere com os commits; a release sai com o título "vX.Y.Z (Acesso antecipado)" (D12), e o README ganhou o rótulo. (2) **A próxima versão sai dos commits** — o `git-cliff --bumped-version`, com a `cliff.toml` na raiz, calcula; testado em repositórios descartáveis com a config final: só `docs:`/`refactor:`/`fix:` dão correção (2.0.1), um `feat:` dá a menor (2.1.0), um `!` depois do tipo dá a maior (3.0.0), até em `docs!:` e `fix!:`, e commit sem tipo não move o número. Os commits anteriores à tag v1.0.0 (com emoji) ficam fora de conta. O `pnpm release` (`scripts/release.py`) calcula, grava a versão no `pyproject.toml` e no `uv.lock`, acrescenta a seção ao `CHANGELOG.md` e não commita: o diff é revisado e vai num `chore: Versão X`. Se o `pyproject.toml` já está acima do calculado (como na 2.0.0, que sobe de 1.0.0 por decisão da D12), o número fica; o workflow roda `scripts.release --check` e só recusa o `pyproject.toml` que ficou abaixo do pedido pelos commits, e escreve os dois números no resumo da execução. A tabela da D12 e a convenção de commit estão na página "Versionamento" dos docs e em `contribuindo.md`. (3) **`CHANGELOG.md` automático, sem LLM** — o `git-cliff` gera cada seção: `feat:` vira "Novidades", `fix:` vira "Correções", e `docs:`, `chore:`, `refactor:`, `build:` e `test:` ficam de fora; um commit com `!` aparece à parte em "Quebras". Cada seção diz se as partidas salvas e o `config.toml` continuam valendo. Só a seção da 2.0.0, que cobre tudo desde fevereiro, ganhou um resumo à mão no topo, com o aviso de que as partidas salvas da 1.0.0 não abrem. (4) **Onde aparece** — o `CHANGELOG.md` na raiz; a seção da versão vira a descrição da release no GitHub (`scripts.release --notes` a extrai do arquivo, para que o resumo à mão da 2.0.0 também vá); e a página "Novidades" dos docs, gerada no build por `scripts/changelog_page.py` (`pnpm db:changelog`, no `prestart`/`prebuild`/`pretypecheck` junto do `db:erd`, sem versionar a saída), que o `deploy-docs.yml` também dispara por mudança no `CHANGELOG.md`.
**Aceite:** `pnpm release` num repositório com commits novos sobe o número pelo tipo dos commits e acrescenta a seção ao `CHANGELOG.md`; o workflow de release publica a versão do `pyproject.toml` com as notas dessa seção e recusa a que ficou abaixo da pedida pelos commits; `GET /api/version` devolve a mesma versão no `pnpm dev` e no executável.

### F57 · arquivado em 2026-10-17

*Kanban:* Logs separados por assunto · feature · ✅ Concluído · atende N26

**F57 — Logs separados por assunto.** Serve N26. Hoje o `setup_logging` (`backend/core/logger.py`) manda tudo para o console e para um `app.log` só (rotativo, 10 MB por arquivo, 5 arquivos), então um erro fica no meio das linhas de uma partida inteira: o `app.log` de uma sessão de desenvolvimento tem 3.541 linhas, 12 delas de erro, e seis dessas são de uma única busca no yfinance por um ticker que não existe. Inspirado nos logs da Paradox, que guardam um arquivo por assunto e um `error.log` só com os erros. O plano: (1) **`error.log`** — só `ERROR` e `CRITICAL`, com o traceback completo que `logger.exception` já gera, rotativo como o `app.log`; ficam de fora dele as bibliotecas que tratam falha esperada como erro (o `yfinance` para ticker inexistente), por filtro de prefixo de logger; a linha continua no `app.log`, e o importador loga a própria mensagem de erro, que é a que entra no `error.log`. (2) **Um arquivo por área**, escolhido pelo prefixo do nome do logger e com o mesmo formato de linha: `simulation.log` (motor, ticks, ordens), `realtime.log` (Socket.IO e SSE), `import.log` (yfinance e BCB) e `database.log` (migrations e banco). Cada linha vai para o arquivo da área e para o `app.log`, que segue como o registro completo e cronológico. A tabela "arquivo → prefixos de logger" mora só em `logger.py`; área nova é uma linha. (3) **O uvicorn passa a escrever nos mesmos arquivos.** Hoje o `uvicorn.run` instala a configuração de log própria dele, com `propagate` desligado, então as mensagens do servidor (início, erro de protocolo do WebSocket) saem só no console e não existem no `app.log`. Com `log_config=None` os loggers dele sobem para o raiz e entram em `app.log` e `error.log`; o `uvicorn.access`, uma linha por requisição, fica em `WARNING` para não encher o arquivo. A F54 (modo debug) sobe o nível do `app.log` e dos arquivos por área para `DEBUG`, com o `error.log` seguindo só com erros, e a F45 manda as requisições lentas para um `slow.log` com uma linha a mais nessa tabela. **Aceite:** uma exceção provocada numa rota deixa o traceback no `error.log`, uma partida inteira sem falha o deixa vazio, e uma queda do WebSocket por erro de protocolo aparece no `app.log`.

### F58 · arquivado em 2026-10-17

*Kanban:* Entrar no meio da partida (hot-join) · feature · ✅ Concluído · atende N27 · depende de F39 · dependência de F61

**F58 — Entrar no meio da partida (hot-join).** Serve N27. Antes só participava quem estava na sala ao iniciar (F39): quem chegava depois, com conta nova ou antiga, era barrado com 423 "a partida já começou". Agora: (1) **A vaga é do participante, online ou não.** A partida em andamento tem no máximo 10 participantes (linhas de `simulation_players`, o teto da paleta); quem jogou e saiu continua dono da vaga e da cor, então uma partida de 10 com seis offline está cheia e o 11º leva 423 ("a partida já tem 10 jogadores, 6 deles offline"). (2) **Quem chega entra "pendente".** `register`, `claim` e `/session/me` deixam de barrar: a sessão volta com `pending_join` e o front manda para a tela `/join`, sem cor e fora de `UserManager._active_players`. (3) **`/join` mostra quem joga (online ou offline), as cores livres e o saldo inicial.** A lista vem de `GET /api/simulation/match-players`; a cor já marcada é a preferência do navegador, se estiver livre, senão a primeira livre. (4) **`POST /api/simulation/join` vale o primeiro pedido.** Sob o mesmo lock `UserManager.join_match` confere o teto e a cor (409 "X pegou essa cor antes") e grava a linha; `Simulation.add_player` deposita o `starting_cash` pelo `add_cash` do motor, datado do dia corrente, e cria o snapshot do dia. O jogador entra no ranking e nas estatísticas. O aporte mensal vale só dali em diante: o ranking por retorno é comparável, mas o por patrimônio absoluto reflete a data de chegada. (5) **Quem sai e volta mantém a cor da partida.** (6) **A mesma conta de vagas vale para a partida salva.** O lobby desenha os ausentes da partida selecionada (cartão tracejado com a cor reservada), marca "Novo" em quem nunca jogou, conta presentes mais ausentes no `N / 10` e mostra o aviso de quem entra com o saldo inicial. Partida que não comporta a sala (jogadores da partida mais novatos passando de 10) não é selecionável: o diálogo de partidas salvas desabilita o "Selecionar" e diz o motivo com os nomes (`room_overflow`), e o servidor recusa com 409 citando os mesmos nomes. Com espaço para os novatos, a seleção segue normal. Quem resolve o excesso hoje é o próprio jogador saindo da sala (F61).
**Aceite:** com a partida em andamento e vaga, um jogador novo escolhe uma cor livre, recebe o depósito inicial e aparece no ranking; com 10 participantes, online ou não, ele continua barrado; uma partida salva de 10 jogadores não é selecionável com um novato na sala, e uma de 8 é com dois.

### F62 · arquivado em 2026-10-17

*Kanban:* Uma migration inicial só para a 2.0.0 · feature · ✅ Concluído · atende N14 · decisões D9 · depende de F4

**F62 — Uma migration inicial só para a 2.0.0.** Serve N14; segue a D9. `backend/migrations/versions/` tinha sete arquivos, todos de outubro de 2026 (a inicial, os indicadores econômicos, a classe do ativo e o IR, setores e segmentos, o critério de vitória, a cor por jogador e o perfil do ativo), escritos durante o desenvolvimento. Nenhum executável publicado os conhecia: a v1.0.0 criava as tabelas com `create_all` e não guarda `alembic_version`. Condensá-los foi de graça, porque ninguém tinha um banco em revisão intermediária; depois da 2.0.0 nenhum banco de jogador pode ficar sem caminho de upgrade, e a cadeia passa a só crescer. Os sete arquivos saíram e entrou uma inicial só, gerada por `pnpm db:revision "create initial schema"` contra um banco vazio e revista à mão: sem os comentários do autogenerate e, no `downgrade`, com o drop explícito de cada `ENUM` nativo (nove), que o autogenerate não faz. O `tests/test_migrations.py` confere que a inicial chega no schema dos models e que sobe e desce; o teste do ensaio com backup, que dependia de haver uma revisão anterior à última, passou a acrescentar ao head real uma revisão só do teste (`add_column` em `stock`), por um `version_locations` extra. O banco de desenvolvimento apontava para uma revisão que deixou de existir e foi recriado do zero, assim como valem os bancos de teste de quem experimentou builds anteriores.
**Aceite:** um banco novo chega ao schema dos models só com a inicial, e `tests/test_migrations.py` passa.

### F63 · arquivado em 2026-10-17

*Kanban:* Sugestão de código ao digitar o ativo · feature · ✅ Concluído · atende N13 · marco M8

**F63 — Sugestão de código ao digitar o ativo.** Serve N13. Mesma ideia do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): no campo "Código do ativo" do painel Adicionar ativo (fonte yFinance), a pessoa digita e a lista mostra os códigos válidos com o nome da empresa, em vez de descobrir o erro só depois de tentar importar. Backend: `GET /api/import-assets/tickers?q=` (no router da Central, que já responde 409 com partida ativa) chama `yf.Search(q, max_results=20, news_count=0, lists_count=0).quotes`; abaixo de 2 caracteres devolve `[]` sem consultar a fonte, e falha da fonte vira 503. O filtro é o da B3: bolsa `SAO`, símbolo terminado em `.SA` e código no formato `[A-Z0-9]{4}\d{1,2}` (PETR4, KNRI11); o `.SA` sai, repetidos saem e a ordem do Yahoo fica. Frontend: o campo vira o `TickerCombobox` (`Input` + `Command` do design system, sem `Popover`, para o foco ficar no campo), com debounce de 300 ms, `useQuery` com `staleTime: Infinity` por texto buscado e setas/Enter/Escape. A sugestão não restringe: o texto digitado continua valendo, então `BTC-USD` e o código tirado do nome do CSV seguem funcionando. A lista só aparece com a fonte yFinance; no CSV o campo fica como antes. Limitação: códigos de fora da B3 não aparecem na lista, só digitados à mão.

### F64 · arquivado em 2026-10-17

*Kanban:* Cache do perfil do ativo no yfinance · feature · ✅ Concluído · atende N13, N16 · decisões D9 · marco M8

**F64 — Cache do perfil do ativo no yfinance.** Serve N13 e N16; segue a D9. Antes, cada importação de ativo ainda sem classificação chamava `yf.Ticker(ticker).info` de novo, inclusive no "Atualizar todos", e o ativo que o yfinance devolve sem setor (ETF, cripto) era reconsultado toda vez. Agora a tabela `ticker_profile` (`ticker` como chave, `name`, `quote_type`, `sector`, `industry`, `fetched_at`), criada por migration do Alembic, guarda a resposta: `fetch_info` lê a linha antes da rede e só consulta o yfinance quando não há, gravando a resposta, inclusive a vazia, para o ETF sem setor não ser reconsultado. `infer_asset_class`, `suggest_segment` e o nome do ativo leem o perfil guardado. Sem expiração: setor e indústria quase não mudam, e a classificação feita à mão continua mandando sobre a sugestão. Se o yfinance falhar, nada é gravado e a importação segue sem sugestão. O botão "Atualizar perfil" na linha Classificar da Central refaz a consulta de um ativo (`POST /api/import-assets/stocks/{ticker}/profile/refresh`; falha da fonte vira 502) e recarrega a sugestão. A F63 não mostra setor ao lado da sugestão, então não lê desta tabela.

### F42 · arquivado em 2026-10-19

*Kanban:* Modo em equipes · feature · ✅ Concluído · atende N23 · marco M13

**F42 — Modo em equipes.** Serve N23. Cada um opera a própria carteira, mas o placar é da equipe: quem vence é a equipe, não a pessoa. O host escolhe nas Regras da partida, em "Modo de jogo", entre todos contra todos (o de hoje) e equipes; o modo é o `player_grouping` da `simulations` (enum nativo `INDIVIDUAL | TEAMS`, separado do critério de vitória, para a corrida à meta e o viver de renda se combinarem com equipes) e o nome das equipes, `team_naming` (`COLOR | NUMBER`: "Equipe Índigo" ou "Equipe 1"), também é regra da partida. Em equipes, cada jogador escolhe a equipe numa grade de 10 ao lado da cor; a equipe é um índice de 1 a 10 na coluna `team` da `simulation_players` (migration, D9, com `CHECK` de 1 a 10) e a cor dela vem de uma paleta própria de 10 tons escuros (`--team-N`), sempre em escudo, faixa, losango ou linha grossa, nunca na bolinha, que é do jogador. Ao ligar o modo todo mundo começa sem equipe e o Iniciar trava até todos terem uma e haver pelo menos duas (o servidor recusa também); o host tem "Distribuir quem falta", que põe cada um na equipe com menos gente. Equipes desiguais valem, com aviso: o valor da equipe em cada critério de vitória (F27) é a **média simples dos membros** (média da nota, do retorno, do Sharpe), para uma equipe de três não vencer uma de dois só por somar mais patrimônio. Quem não tem o valor no critério fica fora daquela média e a equipe mostra "2 de 3"; equipe de uma pessoa vale o valor dela; empate na média desempata pelo patrimônio médio. Numa partida salva, quem já jogou não troca de equipe; quem é novo, ou entra com a partida rodando, escolhe antes de entrar; voltar para todos contra todos apaga as equipes. As equipes moram em memória na sala (`UserManager`, sobrevivem à recarga da página) e passam para o banco ao iniciar; o evento `player_team` mantém todos em sincronia. No relatório, `features/statistics/teams.py` agrega por equipe (média em toda métrica; soma em volume, IR e negócios de Operações) e cada aba devolve `teams` ao lado de `players`: o Geral mostra o ranking por equipe com os membros abaixo (quanto cada um puxa a média), a nota da equipe em quatro eixos com a comparação de todas as equipes e os membros eixo a eixo; a Rentabilidade tem três visões do gráfico (Equipes, Jogadores, Dentro da equipe); o Risco ganha o losango da equipe com o tracejado dos membros; Composição e Operações agrupam por equipe. O fechamento (F27) ganha o pódio de equipes, a frase de vitória (e de desempate) e um cartão de "quem mais puxou" por equipe, com o consolo para quem puxou a própria equipe. Limitações: o Sharpe do app não tem trava de 63 pregões (só a nota tem), então um membro com poucos pregões já entra na média do Sharpe; a comparação entre partidas continua por jogador, sem equipes.

### F45 · arquivado em 2026-10-19

*Kanban:* Painel de desempenho · feature · ✅ Concluído · atende N24 · depende de F54

**F45 — Painel de desempenho.** Serve N24. Mede onde o tempo vai durante uma partida, para depois investigar só o ponto caro, sem serviço externo (o Sentry faz essa medição por rota, mas manda os dados para fora da máquina e é pago). Só funciona com o modo debug (F54) ligado: fora dele o coletor fica desligado, o middleware nem é instalado e a rota `/api/debug/*` responde 404. Um coletor em memória (`backend/core/metrics.py`) guarda, por item, as últimas 1.000 medições e calcula chamadas, tempo total, médio, p95 e máximo: (1) **HTTP** — `MetricsMiddleware` (ASGI puro) mede cada requisição pela rota declarada (`/api/stocks/{ticker}`, não o ticker) e devolve o tempo no cabeçalho `Server-Timing`; fora da conta ficam `/api/stream` (resposta infinita) e o próprio `/api/debug`; (2) **Socket.IO** — o tempo de cada handler recebido (`connect`, `disconnect`, `subscribe`) e, para os enviados, mensagens e bytes por segundo por evento, contados por destinatário dentro do `SocketBroker` e do `SSEBroker` (`stock_update:PETR4` e os demais tickers viram `stock_update:*`); (3) **motor** — quanto leva `next_tick()` para processar um dia, contra o tempo que cabe na velocidade (`1000 / velocidade` ms). Chamadas acima de 500 ms vão para o `slow.log`, pelo logger `backend.metrics` (linha em `AREA_LOGGERS`, F57). `GET /api/debug/metrics` e `POST /api/debug/metrics/reset` são **só do host** (`verify_host`): as medições são do servidor dele. A tela "Desempenho" (`features/performance`, variante A do canvas) atualiza a cada 2 s, com Pausar e Zerar medições: quatro cartões (ritmo do motor com a velocidade real quando atrasa, HTTP com o p95 geral e as rotas lentas, volume enviado ao navegador, onde mais vai tempo), a tabela de tempo com filtro por origem, busca, ordenação e "Mostrar todas", marcando **lenta** (p95 acima de 500 ms) e **trava às vezes** (p95 de 10 vezes a média ou mais), o tráfego por evento e o cartão do py-spy com o comando e o PID. O item "Desempenho" (selo "Debug") em Ferramentas só aparece com o debug ligado e para o host; a URL direta mostra como ligar o debug ou que só o host vê. Achado o ponto, a investigação segue com o `py-spy record --pid`, que gera o gráfico de chamas sem mudar código; a página "Investigando lentidão" dos docs ensina o caminho. Limitações: as medições somem ao reiniciar o app, um 500 tratado pelo servidor entra na conta mas fica sem `Server-Timing`, e o "p95 geral" do cartão HTTP é calculado sobre as janelas atuais de todas as rotas.

### F54 · arquivado em 2026-10-19

*Kanban:* Modo debug · feature · ✅ Concluído · atende N24 · dependência de F65

**F54 — Modo debug.** Serve N24. Um flag só, decidido ao subir o servidor: `[debug] enabled` no `config.toml` ou `--debug` na linha de comando (que liga mesmo com o arquivo desligado). **Vem desligado em todo lugar**, em desenvolvimento e no executável: "dev" e "executável" só dizem como o front é servido (Vite ou build), não são modos de debug, e não há botão na interface, mudar exige fechar e abrir o app. O backend o expõe em `GET /api/settings` (campo `debug`, somente leitura: o `PUT` não o grava e o valor do `config.toml` vale sobre qualquer coisa guardada). Ligado: (1) `TomlSettings.effective_logging_level()` força `DEBUG` no `app.log` e nos arquivos por área da F57, com `error.log` seguindo só em `ERROR`; `sqlalchemy`, `engineio`, `socketio`, `urllib3` e `asyncio` ficam em `INFO` (`NOISY_LOGGERS` em `logger.py`) para o DEBUG não afogar o arquivo; (2) o front carrega o TanStack Query Devtools pelo build de produção dele (`@tanstack/react-query-devtools/production`, em `lazy`), que funciona também no executável, e libera os `logger.debug`/`logger.log` do console. Desligado, o front é igual em dev e no executável: sem devtools e sem esses logs. O front lê o flag pelo hook `useDebugMode`, que a F45 usa para mostrar o painel e o item de menu; essas duas peças são da F45, não desta. Limitação: os logs do front anteriores à resposta de `/api/settings` se perdem; `warn` e `error` nunca são silenciados.

### F66 · arquivado em 2026-10-19

*Kanban:* Spike: reavaliar a manutenção do SSE · feature · ✅ Concluído · decisões D13

**F66 — Spike: reavaliar a manutenção do SSE.** Decidiu a D13: remover o SSE e dar ao Socket.IO o fallback de polling. O SSE não rodava (o front fixava o modo WebSocket e ligar `use_sse` desmontava o Socket.IO do servidor), não tinha teste e tinha defeitos no broker; o Quick Tunnel da Cloudflare, candidato da F5, não suporta SSE, e o polling do Socket.IO cobre o proxy que barra o WebSocket. Saíram o `SSEBroker`, a rota `/api/stream`, a `/api/update-subscription`, o `SSEClient`, o `use_sse` e a doc; o cliente passou a usar `transports: ["websocket", "polling"]`. Não foi testado em túnel real: a F5 confere se ao menos o polling atravessa cada candidato.

### F23 · arquivado em 2026-10-21

*Kanban:* Spike: gerador de séries sintéticas · feature · ✅ Concluído · atende N12 · decisões D7, D14 · marco M9 · dependência de F24, F28

**F23 — Spike: gerador de séries sintéticas.** Serve N12. Decidiu a D14 e completou a D7. A medição usou um harness descartável sobre o banco de desenvolvimento, com 37 ações e FIIs de 10 setores importados pelo importador oficial (2000–2026) e os indicadores reais, gerando 100 futuros de 5 anos por variante. Foram comparados o passeio aleatório, o bootstrap em blocos de 5, 20 e 60 dias e os blocos com biomas, pelos dias bruscos, pela memória da agitação, pela correlação dentro e entre setores, pela queda máxima anual, por um teste fora da amostra (2020–2024 gerado só com o histórico até 2019), pela temperatura de 0 a 3 e pela SELIC e pelo IPCA gerados. O gerador entrou como função pura em `backend/features/import_data/synthetic.py` (`SeriesGenerator`: histórico, data final, semente, temperatura, bioma inicial e ativos → linhas de preço e de indicador), sem ler nem gravar no banco, com testes em `tests/test_synthetic_series.py`; o `numpy` virou dependência direta. A cópia na troca para partidas salvas (D7) ficou desenhada e é da F24. Limitações: o GARCH não foi medido, porque o bootstrap passou em todos os critérios; a amostra tem 37 ativos; o teste fora da amostra cobre um período só (2020–2024).

### F52 · arquivado em 2026-10-21

*Kanban:* Modo corrida à meta · feature · ✅ Concluído · atende N23 · marco M13

**F52 — Modo corrida à meta.** Serve N23. Vence quem chega primeiro a um patrimônio-alvo, como a vitória por Maravilha do Age of Empires. **Tipo de partida:** em vez de um valor novo no critério de vitória, a partida ganhou um eixo próprio, o `ENUM` `game_type` (`CLASSIC`, `GOAL_RACE`, `FINANCIAL_INDEPENDENCE`) em `simulations`; os 4 critérios da F27 continuam e só valem na Clássica. No lobby, "Tipo de partida" são 3 cards entre "Modo de jogo" e o resto, e "Quem vence" some fora da Clássica. **Meta:** coluna `goal_net_worth`, escolhida pelo host com atalhos de 5×, 10× e 20× o saldo inicial (padrão 10×, `goal_multiple` no `config.toml`) e maior que o saldo inicial; as partidas salvas receberam 10× o saldo. **Fim:** depois dos snapshots do dia, `goal_reached` confere se alguém (ou, em equipes, a média do patrimônio dos membros) chegou; a partida encerra no pregão seguinte com `simulation_ended` e vai ao fechamento, e a partida salva terminada por meta aparece como terminada e não continua. **Ranking:** fora da Clássica o valor do critério é a fração da meta (patrimônio ÷ meta, 1 = chegou); ordenar por ela já dá as regras do card (dois no mesmo dia: o maior patrimônio; ninguém na meta: o mais perto), e em equipes a média das frações é o patrimônio médio ÷ meta. As Estatísticas mostram "% da meta" e "Falta para a meta", os gráficos de patrimônio ganham a linha da meta e o fechamento diz quem chegou primeiro ou que ninguém chegou. **Tempo real:** o evento `goal_progress_update` (meta e patrimônio de cada jogador) sai todo pregão e a rota `GET /api/simulation/goal-progress` dá o estado inicial; a topbar mostra a trilha com um marcador por jogador (um escudo por equipe) e a página "Meta" traz o progresso e a corrida de todos. A meta é em reais do dia, e o aporte mensal continua valendo.

### F53 · arquivado em 2026-10-21

*Kanban:* Modo viver de renda · feature · ✅ Concluído · atende N23 · marco M13 · depende de F52 · dependência de F69, F71

**F53 — Modo viver de renda.** Serve N23. Uma corrida à meta (F52) em que a meta é a independência financeira e o caminho tem a vida real no meio. **Tipo de partida:** o terceiro valor do `game_type`, `FINANCIAL_INDEPENDENCE`; o fim, o ranking por fração da meta e o fechamento são os da corrida. **Regras:** o host define no lobby o salário e a despesa mensal (padrões R$ 8 mil e R$ 5 mil no `config.toml`), a frequência dos imprevistos por ano (padrão 3), a taxa de retirada (padrão 4%, entre 1% e 10%, com a explicação da regra dos 4% e do estudo Trinity ao lado do campo) e se salário e despesa sobem pelo IPCA. Não há aporte: o salário entra no primeiro pregão do mês e a despesa sai no mesmo dia. **Meta:** 12 × a despesa ÷ a taxa de retirada (R$ 5 mil por mês a 4% dá R$ 1,5 milhão), maior que o saldo inicial. Com a correção ligada, salário, despesa e meta sobem uma vez por ano, no aniversário da partida, pelo IPCA acumulado dos 12 meses; o relatório guarda a meta em degraus (`goal_steps`) para a linha da meta nos gráficos, e a topbar avisa por 30 dias que a meta subiu. **Imprevistos:** um registro de tipos (`LIFE_EVENTS`), cada um com nome, efeito, peso no sorteio e múltiplo da despesa: conserto do carro (1 despesa), saúde (2 despesas) e demissão (o salário do mês seguinte não entra). O sorteio de cada pregão sai da semente da partida (`random_seed` em `simulations`) e da data, então todos recebem os mesmos imprevistos nos mesmos dias, inclusive ao continuar uma partida salva. **Caixa:** salário, despesa, imprevisto e juro do cheque especial são valores novos do `cashflow_event_type`, cada tipo com o próprio sinal; o imprevisto guarda a chave do tipo em `life_event_key`. Caixa negativo paga 8% ao mês de cheque especial (`overdraft_monthly_rate` no `config.toml`), composto por pregão, até ser coberto. Salário, despesa e imprevisto contam no capital aportado e o juro conta como perda. **Telas:** a página "Meta" ganha a vida financeira (salário, despesa, reserva em meses de despesa, juro do cheque especial, aviso de demissão) e o histórico com filtros por imprevisto, demissão e cheque especial, com o juro somado por mês; a topbar mostra o caixa e "Cheque especial" quando negativo; cada imprevisto e a entrada no negativo viram um aviso que leva ao histórico. **Desvios:** a reserva de emergência conta só o caixa, porque a renda fixa só volta no vencimento (fecha com a F71); o fechamento não diz quantos imprevistos cada um passou, o histórico não soma os juros pagos na partida, e a previsão de quando a meta chega fica fora em equipes. A meta pela renda passiva real, quando os proventos existirem (F22), segue em aberto.

### F65 · arquivado em 2026-10-21

*Kanban:* Rework dos loggings · feature · ✅ Concluído · atende N26

**F65 — Rework dos loggings.** Serve N26. Terminal e arquivos de log viraram destinos separados: o terminal do host é a tela de status do servidor, e os arquivos guardam o histórico. **Terminal:** só o bloco de abertura (banco, interfaces de rede, URL local, pasta de configurações e logs, modo debug), o que explica uma espera ou muda o banco (extração do PostgreSQL, migração) e todo aviso e erro, em uma linha curta; o traceback fica no `error.log`. Uma mensagem vai ao terminal quando leva `extra=TERMINAL`; o nível `INFO` deixou de decidir isso. **Níveis:** o raiz fica em `INFO`; o modo debug sobe só o `backend.*` para `DEBUG`, nos arquivos, e o terminal nunca mostra `DEBUG`. As bibliotecas (`sqlalchemy`, `engineio`, `socketio`, `urllib3`, `asyncio`) ficam em `WARNING` (`LIBRARY_LEVELS`, no lugar do `NOISY_LOGGERS`). O `logging_level` e o `[database] echo_sql` saíram do `config.toml` (as chaves antigas são ignoradas). **SQL:** só com `[debug] sql = true` junto do debug, e só no `database.log` (nível `INFO` do `sqlalchemy.engine`: consulta e parâmetros, sem as linhas de resultado). **Dica de firewall:** saiu do terminal e do `config.toml` (`show_firewall_hint`) e virou uma seção da página de multiplayer. **Logs revistos:** por dia, por ordem e por conexão de WebSocket viraram `DEBUG` com `%s`; os de ciclo da partida e de jogadores ficam em `INFO` só nos arquivos; mensagens em português; duplicatas unidas; `main.py` loga como `backend.main`. **`DEBUG` novos:** ordem recebida, cancelamento recebido e ordem casada, dia simulado, leitura do CSV e download por ticker. No front, o único `console.error` fora do `logger.ts` passou a usá-lo. A tabela de decisões log a log, os arquivos e o custo medido estão em `docs/docs/desenvolvimento/logs.md`. **Custo:** em micro-benchmark da escrita, uma linha `DEBUG` do app custa cerca de 84 µs e uma de SQL cerca de 57 µs; não pesou o bastante para o `QueueHandler`.

### F88 · arquivado em 2026-10-21

*Kanban:* Spike: indicadores gerados que reagem uns aos outros · feature · ✅ Concluído · atende N12 · decisões D14 · marco M9 · dependência de F24

**F88 — Spike: indicadores gerados que reagem uns aos outros.** Serve N12. Revisou a D14 na parte dos indicadores. O harness comparou, sobre o gerador da D14, a SELIC por uma regra fixa do Copom (alvo pela inflação de 12 meses, degraus por reunião) e o encaixe de nível (o próximo trecho sorteado entre os que começam com SELIC, IPCA de 12 meses e tendência do IPCA parecidos com o momento gerado), em 100 futuros de 10 anos, pelas reações entre IPCA, SELIC e Ibovespa, pelo juro real, pelos níveis e por um teste fora da amostra. O encaixe ficou perto do real em todas as relações; a regra do Copom saiu robótica (juro real nunca negativo) e desligou a SELIC da bolsa. O choque de inflação (−5 a +20 pontos) virou camada por cima dos mesmos trechos: inflação, SELIC pelo princípio de Taylor (1,5 vez) e bolsa pela reação histórica do Ibovespa à SELIC, porque, com o choque dentro do encaixe, a inflação contava em dobro e a bolsa sofria menos nos choques maiores. Entrou no `SeriesGenerator` (`inflation_shock`), com testes, e a metodologia foi documentada na página "Como o futuro é gerado" dos docs, com as referências de cada método. Limitações: o encaixe deixa os futuros mais estreitos (no teste fora da amostra, 23 de 36 séries dentro da faixa no retorno, contra 27 sem o encaixe), e o ciclo de juros de 2020–2022 fica fora de todos os futuros sem choque.

### F24 · arquivado em 2026-10-22

*Kanban:* Gerar dados futuros na Central de dados · feature · ✅ Concluído · atende N12 · decisões D7, D14 · marco M9

**F24 — Gerar dados futuros na Central de dados.** Serve N12; segue a D7 e a D14. (1) **Tela:** na Central (F21), o botão "Gerar dados futuros" abre um diálogo, com os controles à esquerda e a prévia à direita (desenho aprovado no canvas), que pede até quando gerar (cada série começa no dia útil seguinte ao seu último dado real), a semente, a temperatura (0 a 3, padrão 1), "começar em" (mercado de hoje, calmaria, normal ou crise, o `start_regime`) e o choque de inflação (−5 a +20 pontos, padrão 0, o `inflation_shock`). Temperatura e choque ganham descrição curta e dica com a leitura medida, como na página "Como o futuro é gerado" dos docs: temperatura 1 é o histórico como foi, 2 dá dois de cada três anos com queda acima de 30%, 3 é crise permanente; choque de +10 leva a inflação a uns 14% e a SELIC a 28%. O preview monta um `SeriesGenerator` uma vez e gera sem gravar poucos ativos a cada mudança de parâmetro (cerca de 0,1 s). (2) **Gravação:** os repositórios montam o `MarketHistory` (preços, segmento e setor de cada ativo e indicadores, só a origem real) e gravam o `GeneratedSeries` com origem "gerado"; indicador vira `Decimal` a partir do valor já arredondado; regerar troca o gerado comum, passando pela cópia na troca. A barra da linha do tempo já mostra o trecho gerado pelo `generated_end` da cobertura. (3) **Versão das séries (D7):** `stock_price_history` e `economic_indicator_history` ganham a coluna de versão na chave (a comum e a de cada partida), por migration (D9). As leituras do motor (`get_stocks_by_date`, `get_recent_closes`, `get_closes_on`, `get_stock_details` e o histórico de indicadores) passam a preferir a versão da partida. A cópia na troca: antes de trocar ou apagar gerado, cada partida salva cujo período, de `start_date` ao último dia simulado, cobre linhas geradas recebe a cópia delas na própria versão. (4) **Importador:** "Atualizar" troca o gerado pelo real à medida que o real chega. Hoje o `upsert_dataframe` incremental compara com a última data de qualquer origem, e um gerado no fim faria o real ser descartado: passa a comparar com a última data real e a trocar o gerado das datas que o real cobre. O `overwrite=True` apaga o histórico inteiro, gerado junto, e passa pela mesma troca. O upsert de indicador sobrescreve a origem no conflito, então a cópia na troca roda antes dele. O gerado que sobra depois do real continua do real antigo, com um salto no dia da emenda: a Central guarda até onde o real chegou e sugere "Gerar de novo" com os controles guardados, que emenda todas as séries a partir do real novo. (5) **Parâmetros do futuro gravado:** a semente, a temperatura, o "começar em" e o choque do futuro gravado ficam guardados; a Central mostra "semente 4821 · temperatura 1 · começo: hoje · choque 0" ao lado de "gerado até", e "Gerar de novo" abre o diálogo com esses valores. Não há "apagar o futuro gerado": gerar de novo substitui o anterior. Gatilho: livre; o gerador está pronto.

### F40 · arquivado em 2026-10-22

*Kanban:* Modo Especialista · feature · ✅ Concluído · atende N21 · decisões D2 · marco M13

**F40 — Modo Especialista.** Serve N21; segue a D2. Uma opção da partida no lobby, ao lado do critério de vitória, que tira as ajudas que decidem pelo jogador e o obriga a fazer as próprias contas. A filosofia é a do realismo de batalha do Total War e do Hardcore de Kingdom Come: Deliverance, que tiram da tela o que entrega a resposta. O que sai, pelo inventário de hoje: na renda fixa, a coluna e o card "Equivale hoje" (a taxa anual equivalente com CDI e IPCA do dia) e a ordenação por ela, que passa a ser por vencimento; no detalhe do título, a projeção "Quanto R$ X viram no vencimento", com o IR já descontado; e, quando existir, o "Resumo técnico" da F33 com a leitura compra/neutro/venda (os indicadores ficam). A pausa e a visão dos outros jogadores continuam como no modo normal. Guardado em `simulations` como uma coluna por ajuda (com o padrão "ligado"), por migration (D9); o lobby oferece os atalhos Normal e Especialista e mostra a lista para ajuste fino. O servidor omite os campos escondidos do DTO em vez de o front só não desenhá-los, porque no multiplayer quem abrir o DevTools veria a resposta.

### F41 · arquivado em 2026-10-22

*Kanban:* Conquistas · feature · ✅ Concluído · atende N22 · decisões D1 · marco M13

**F41 — Conquistas.** Serve N22; segue a D1. Um catálogo no código (`backend/features/achievements/catalog.py`): cada conquista tem código, nome, descrição, ícone (do `lucide-react`), categoria (Primeiros passos, Patrimônio, Mercado, Partida ou Secretas), se é secreta, e uma condição avaliada sobre os eventos e snapshots do jogador no fim de cada tick. As de meta numérica (R$ 1 milhão, 12 meses seguidos acima do CDI) trazem também uma regra de progresso, que devolve o valor atual e a meta. Exemplos: primeira compra de ação; primeiro R$ 1 milhão; bater o CDI 12 meses seguidos; atravessar uma queda de 30% do Ibovespa perdendo menos que ele; vencer uma sala cheia; vencer sem assistências (F40). A conquista desbloqueada vai para a tabela `achievements` (`user_id`, `code`, `simulation_id`, `unlocked_at`), por migration (D9), e chega ao jogador por um evento do Socket.IO que abre um toast rico, no estilo da Steam: ícone, nome e descrição, com `toast.custom` do sonner; várias no mesmo dia viram um toast só. Uma tela "Conquistas" mostra as do jogador em lista, das mais recentes para as mais antigas, com data real, partida e busca: desbloqueadas com data e partida, bloqueadas embaixo em cinza com a barra de progresso, e as secretas sem descrição até sair. Ao lado, um painel com o total, as três mais próximas de sair e o progresso por categoria. A tela fica na sidebar, em Você, e abre também no lobby, por um botão "Conquistas" no cabeçalho da sala, em rota própria sem a sidebar do jogo. As conquistas ficam no banco do host, como o resto do histórico: sem conta online, o jogador que entra na sala de outro host começa lá do zero.

### F47 · arquivado em 2026-10-22

*Kanban:* Gravação automática de demonstrações · feature · ✅ Concluído · atende N25 · marco M14

**F47 — Gravação automática de demonstrações.** Serve N25. `pnpm demo` (`scripts/demo/`) sobe o backend numa pasta de trabalho com o `config.toml` da demo. O banco-base (`POSTGRES_DEMO_DATABASE_URL` no `.env`) guarda cinco ações fixas, importadas dos CSVs de `scripts/demo/data/` (baixados uma vez com `pnpm demo fetch-data`), e os indicadores, que só são buscados no Banco Central quando faltam. Cada gravação roda numa cópia do banco-base, apagada no fim, e por isso sai sempre do mesmo estado. O roteiro percorre em Playwright o lobby, a compra de ação, a renda fixa, o avanço do tempo, as estatísticas e o fechamento. A gravação é o screencast do DevTools em 2× (e não o `recordVideo`, de bitrate baixo e sem o instante de cada quadro), com um cursor desenhado na página, porque o Chromium headless grava sem cursor. O zoom automático segue a ideia do Recordly: o roteiro anota onde e quando clica, e a câmera aproxima antes da ação, segura enquanto as ações seguem perto e afasta depois. Cada cena vira um GIF do `gifski` com até 10 MB, a partir de um MP4 intermediário que fica em `build/demo/`; as screenshots saem em `docs/static/demo/screens/`. As imagens não entram no `main`: `pnpm demo publish` as põe no branch `demo`, que guarda só a última publicação (um commit sem pai, com force-push), e o deploy dos docs as busca de lá; o `gh-pages` também passou a guardar só o último deploy. O link de convite é trocado por um IP de rede local fictício, para não expor o da máquina que grava. Os títulos de renda fixa são sorteados por partida, então essa cena muda um pouco a cada gravação.

### F48 · arquivado em 2026-10-22

*Kanban:* README e docs que mostram o produto · feature · ✅ Concluído · atende N25 · marco M14 · depende de F47

**F48 — README e docs que mostram o produto.** Serve N25. O README abre com um GIF do jogo rodando e, logo abaixo, o que ele faz, cada item com uma imagem ou um GIF curto da F47 (renda variável, renda fixa, estatísticas, multiplayer), o download e o link dos docs; a parte de desenvolvimento desce para o fim. Nos docs, uma página "Tour" com os GIFs das cenas, e as páginas de "Como usar" com as screenshots novas. As imagens moram no branch `demo`: o README aponta para os arquivos de lá (`github.com/<repo>/raw/demo/gifs/<cena>.gif`) e os docs usam `/demo/...`, que o deploy copia do branch. Junto, uma revisão do que está desatualizado em README e docs, página por página, contra o app de hoje. Feito com a skill de documentação (`engineering:documentation`).

### F70 · arquivado em 2026-10-22

*Kanban:* O que cada jogador está fazendo na sala · feature · ✅ Concluído · atende N29

**F70 — O que cada jogador está fazendo na sala.** Serve N29. Inspiração: a presença rica da Steam e dos jogos online ("Navegando nos menus", "No lobby"). **Onde aparece:** no lugar do selo "Online" do cartão de cada jogador no lobby, mantendo a bolinha verde e trocando só o texto; a lista da tela `/join` usa o mesmo selo para quem está na sala. O "Host" virou um selo ao lado do nome (como o "Novo"), e a linha de status do host mostra só a atividade. **Textos curtos** (cabem nos ~86 px do cartão no lobby em equipes), com a frase inteira numa dica ao passar o mouse: `/lobby` → "No lobby", `/import-assets` → "Na Central" ("Na Central de dados"), `/compare-simulations` → "Comparando" ("Comparando simulações"), `/match-result/:id` → "No resultado" ("Vendo o resultado de uma partida"), `/settings` → "Configurando" ("Nas configurações"); toda rota fora do mapa cai em "Nos menus" ("Navegando nos menus"). Tela nova ganha atividade própria acrescentando uma entrada no mapa único em `shared/lib/player-activity.ts`. **Mecanismo:** a cada troca de rota o cliente manda o evento `presence` pelo Socket.IO com a chave da tela; com a aba escondida (`visibilitychange`) manda `away` e o selo vira "Ausente", em amarelo e com a bolinha parada. O servidor guarda a chave em memória no `UserManager`, uma por aba aberta (com duas abas, a que está à vista ganha da ausente e, entre as à vista, vale a que avisou por último; fechar uma aba devolve o selo às que restam), devolve a atividade no payload dos jogadores da sala e avisa a sala pelo evento `player_activity`, sem banco e sem migration. **Durante a partida** a tela fica de fora: dizer quem está na renda variável ou num ticker entrega a jogada aos adversários. O cliente manda `null` ("Online") enquanto a partida roda, mas o "Ausente" vale: na `/join`, que só existe com partida rodando, o selo é Online, Ausente ou Offline. Quem jogou a partida salva e está fora da sala segue "Offline". Gatilho: quando houver mais telas fora da partida para a atividade dizer algo além de "No lobby".

### F73 · arquivado em 2026-10-22

*Kanban:* Mapeamento único entre as regras da partida e o formulário do lobby · feature · ✅ Concluído · dependência de F89

**F73 — Mapeamento único entre as regras da partida e o formulário do lobby.** As regras da partida viram valores do formulário em três lugares (`defaultValues` e o painel "Ver regras" em `lobby-match.tsx`, e o `form.reset` do `useRealtimeSyncSimulationForm`) e voltam para o corpo da API em dois (`createSimulationBody` em `lobby-match.tsx` e o `payload` do mesmo hook). As cópias já divergem: dinheiro sai por `formatMoney(toCentsString(...))` num lugar e por `displayMoney(...)` em outro, e o corpo da criação não passa por `toCentsString` enquanto o da sincronização passa. Cada campo novo de regra precisa ser lembrado nos cinco, e a regra que volta com o nome da partida anterior foi um erro desse tipo. (1) `features/lobby/lib/simulation-form.ts` com `toFormValues(settings)`, que recebe o tipo da API (`SimulationSettingsData`) e devolve `SimulationFormValues`, e `toSettingsBody(values)`, que devolve `CreateSimulationRequest`. Os dois tipos vêm da API e do schema do formulário, então um campo novo que falte numa das funções vira erro do `tsc`. (2) Os cinco lugares passam a chamar as duas funções; o `as TForm` do hook sai. (3) A ordem de chaves que o descarte de duplicata do hook compara por JSON passa a ser a da função. Se o Vitest da feature de testes de cálculo já existir, um teste de ida e volta (`toSettingsBody(toFormValues(x))` igual a `x`) fecha o contrato. Gatilho: a próxima regra de partida nova, ou qualquer mexida no lobby.

### F74 · arquivado em 2026-10-22

*Kanban:* Testes da conexão em tempo real e do loop da partida · feature · ✅ Concluído · dependência de F75

**F74 — Testes da conexão em tempo real e do loop da partida.** Os módulos do multiplayer são os menos cobertos do backend: `ws_handlers.py` 21%, `simulation_loop.py` 30%, `simulation_loader.py` 30% e `simulation.py` 45% (o total é 80%). A saída do jogador ao fechar uma de duas abas foi corrigida justamente na desconexão de `ws_handlers.py`, sem teste que a cobrisse. (1) **Conexão:** testes de `register_ws_handlers` com um `AsyncServer` dublê, chamando `connect`, `disconnect` e `subscribe` direto: recusa sem cookie, cookie `client_id` que não é UUID (hoje estoura `ValueError`; passa a recusar a conexão com aviso no log), duas abas do mesmo cliente com uma fechando (o jogador fica) e a última fechando (`UserManager.unregister`). (2) **Loop:** testes do `SimulationLoopController` com um `Simulation` dublê de tick instantâneo: start, pausa, retomada, velocidade, fim natural da partida (evento `simulation_ended`, flush e simulação liberada) e exceção no meio do tick. (3) **Carga:** `simulation_loader` com o banco de teste, carregando uma partida salva e conferindo jogadores, carteira e data. Gatilho: a próxima mudança em sala, abas ou loop; junto com a correção do encerramento do loop, que precisa desses testes para provar a corrida.

### F76 · arquivado em 2026-10-22

*Kanban:* Testes das contas feitas no frontend · feature · ✅ Concluído · atende N3

**F76 — Testes das contas feitas no frontend.** Serve N3. Parte dos números da tela é calculada no navegador e não tem teste nenhum: o frontend não tem runner configurado. O escopo é só função pura de cálculo, sem teste de componente, de tela ou ponta a ponta. (1) **Runner:** Vitest como dependência de desenvolvimento, sem configuração própria (reaproveita o `vite.config.ts` e o alias `@`), script `test` no `frontend/package.json` e entrada no `pnpm run check` da raiz. (2) **Alvos:** `shared/lib/goal.ts` (fração e restante até a meta, projeção da data da meta, classificação de jogadores e equipes), `shared/lib/financial-independence.ts` (meta de independência e múltiplo de despesa anual pela taxa de retirada), `features/performance/lib/stats.ts`, `features/statistics/lib/criterion.ts`, `features/correlation/lib/correlation.ts`, `features/goal/lib/life-history.ts` e os formatadores de `shared/lib/utils/display.ts`, que são a última etapa de todo número na tela (vírgula decimal, milhar, sinal, porcentagem). (3) **Casos:** valores calculados à mão, como nos testes do backend, mais as bordas: patrimônio zero, meta já batida, histórico de um ponto só, taxa de retirada nos limites de 1% e 10%. Arquivo de teste ao lado do arquivo testado (`goal.test.ts`). Gatilho: a próxima feature que mexa numa dessas contas.

### F77 · arquivado em 2026-10-22

*Kanban:* Dependências em dia, com o TypeScript 7 · feature · ✅ Concluído · decisões D15

**F77 — Dependências em dia, com o TypeScript 7.** Segue a D15. Quatro passos, um commit cada, todos fechados com `pnpm run check`. (1) **Versões menores:** `pnpm update` no frontend e `uv lock --upgrade` no backend; o FastAPI foi de 0.143 a 0.159 sem mudar o `docs/openapi.json`. (2) **`@hookform/resolvers` 6:** só o resolver do Effect quebrou; o `zodResolver` do login, da importação e do lobby seguiu igual. (3) **oxlint no lugar do ESLint:** `frontend/.oxlintrc.json` com as regras do React Compiler nativas, o `@shadcn/lint` como `jsPlugin` e as regras que olham os tipos; as promises disparadas sem esperar ganharam `void`. (4) **TypeScript 7:** o `tsc` caiu de 30,7 s para 6,5 s; o `openapi-typescript` usa a API do 6 pelo `frontend/.pnpmfile.cjs`. Fica: o hook sai quando o `openapi-typescript` aceitar o 7, e as regras que olham os tipos deixaram 7 avisos para revisar (spread de `style` em `avatar` e `progress`, template literal em `chart`, union duplicada em `team-score` e `String(d)` em `composition-tab`).

### F78 · arquivado em 2026-10-22

*Kanban:* Release só sai com o check passando · feature · ✅ Concluído

**F78 — Release só sai com o check passando.** O `release.yml` valida a versão e monta o executável nos três sistemas sem rodar teste nem lint; o único workflow que roda `pnpm run check` é o `dependabot-check.yml`, e sem banco, então os testes que precisam do PostgreSQL são pulados lá. A validação fica no release, não em cada push. (1) O job de check do `dependabot-check.yml` vira um workflow reutilizável, `check.yml` com `on: workflow_call`, chamado pelo `dependabot-check.yml` e pelo `release.yml`, para os dois rodarem a mesma coisa. (2) O job ganha um serviço `postgres` (a imagem oficial já sobe em UTF-8) e `POSTGRES_DATABASE_URL` apontando para ele, para os testes de banco rodarem. (3) No `release.yml`, o job `build` passa a ter `needs: [validate, check]`: check vermelho, nenhum executável é montado nem publicado. Gatilho: antes do próximo release.

### F79 · arquivado em 2026-10-22

*Kanban:* Tipos do frontend que vêm da API · feature · ✅ Concluído

**F79 — Tipos do frontend que vêm da API.** Dois lugares do front escrevem à mão um tipo que a API já define, e o `tsc` não acusa quando a API muda. (1) `features/portfolio/components/networth-chart.tsx` declara um `Point` com `date`, `cash`, `fixed`, `equity`, `total` e `provided` e converte para ele os campos de `PortfolioHistoryPoint` (`snapshot_date`, `total_cash`, `total_networth`…). O gráfico passa a ler `PortfolioHistoryPoint` direto (só o `goal`, que não vem do ponto, fica como campo calculado ao lado), e o mapeamento sai. (2) `features/variable-income/pages/variable-income.tsx` escreve o filtro como `"ALL" | "HELD" | "STOCK" | "FII" | "ETF"`, sem o `BDR` que o `AssetClass` da API tem: BDR só aparece em "Todos". O tipo vira `"ALL" | "HELD" | AssetClass`, e os botões saem de um `Record<AssetClass, string>` com o rótulo de cada classe, que obriga um rótulo para toda classe nova. O `LCI_LCA` da renda fixa é agrupamento de tela intencional e fica. Gatilho: a próxima mexida na carteira ou na renda variável.

### F82 · arquivado em 2026-10-22

*Kanban:* Repetições pequenas do frontend · feature · ✅ Concluído

**F82 — Repetições pequenas do frontend.** Seis repetições pequenas do frontend viraram uma definição cada. (1) `displayIsoDate` em `shared/lib/utils/display.ts` substitui o `formatIso` de cinco arquivos (`future-form.tsx` também tinha a cópia). (2) `niceTicks` mora em `shared/lib/chart-scale.ts` e o gráfico de patrimônio a usa no lugar do `niceScale`; as constantes de altura ficam em cada gráfico, porque os valores são diferentes. (3) `PodiumSteps` (`match-result/podium-steps.tsx`) guarda os degraus e o layout; `podium.tsx` e `team-podium.tsx` trazem só o conteúdo da coluna. (4) `AXIS_SCALE` está em `features/statistics/lib/metrics.ts`. (5) `Player` e `Team` (do relatório de visão geral) e `RiskPlayer`, `ReturnsPlayer`, `OperationsPlayer`, `CompositionPlayer` (um por aba, pois cada DTO tem formato próprio) estão em `types/api.ts`. (6) O hook de context virou `useNotificationPreferences`.

### F83 · arquivado em 2026-10-22

*Kanban:* Proxy do Vite na porta do config.toml · feature · ✅ Concluído

**F83 — Proxy do Vite na porta do config.toml.** O proxy de `/api` e `/socket.io` em `frontend/vite.config.ts` aponta para `localhost:8000` fixo, enquanto o backend sobe na porta de `[server] port` do `config.toml`. Mudando a porta, o `pnpm dev` perde o backend sem erro claro. O `vite.config.ts` passa a ler `../config.toml` com o `smol-toml` (dependência de desenvolvimento) e usa `server.port`, com 8000 quando o arquivo não existe, que é o mesmo padrão do backend. Gatilho: a qualquer momento; é uma mudança de um arquivo.

### F84 · arquivado em 2026-10-22

*Kanban:* Dependências do backend num sentido só · feature · ✅ Concluído

**F84 — Dependências do backend num sentido só.** Dois pontos do backend importam nos dois sentidos. (1) **Simulação e estatísticas:** `features/simulation/goal.py` usa o `mean` de `features/statistics/teams.py`, e `features/statistics/report.py` usa o `goal_on` e o `goal_steps` de `simulation/goal.py`. As contas de meta são estatística da partida: `goal.py` passa para `features/statistics/`, e a simulação (`simulation.py`, que usa `goal_on` e `goal_reached`) importa de lá. A simulação já depende das estatísticas pelo relatório, então tudo fica num sentido só. (2) **Core e renda variável:** `core/dto/order.py` e `core/dto/position.py` importam as entidades de `features/variable_income` para converter entidade em DTO. A conversão passa para a entidade (`Order.to_dto()`, `Position.to_dto()`), e o `core/dto` deixa de conhecer a feature. Fora do escopo: os imports dentro de métodos do `UserManager` para emitir eventos de tempo real, que só se desfazem mudando quem emite. Na implementação, o `LifeBudget` foi para `core/life_budget.py`, porque o `goal.py` depende dele e continuaria apontando para a simulação. Os enums de ordem foram para `core/enum`, e o `MARKET_CLIENT_ID` virou constante de `entities/order.py`, para o `Order.to_dto()` não fechar ciclo com o `market_liquidity.py`.

### F85 · arquivado em 2026-10-22

*Kanban:* Importar duas ações da mesma empresa · feature · ✅ Concluído · atende N13

**F85 — Importar duas ações da mesma empresa.** Serve N13. A importação de PETR3 depois da PETR4 caía com `UniqueViolation` em `stock_name_key`: o yfinance dá o mesmo nome às duas ("Petróleo Brasileiro S.A. - Petrobras") e o `upsert_dataframe` cria o ativo com esse nome. Feito: uma migration (D9) removeu o `UniqueConstraint("name", name="stock_name_key")` de `stock`, mantendo o `ticker` único; nenhum código busca ação pelo nome. Teste em `tests/test_ticker_profile.py`: importar dois tickers com o mesmo nome cria os dois.

### F86 · arquivado em 2026-10-22

*Kanban:* Sugestão de ticker que a importação aceita · feature · ✅ Concluído · atende N13

**F86 — Sugestão de ticker que a importação aceita.** Serve N13. A busca do yfinance sugeria `PETR4`, o combobox preenchia esse valor e a importação baixava `PETR4`, que o yfinance responde com 404 (ele só conhece `PETR4.SA`). Feito, no caminho do Finance Manager: a base guarda o código da B3 sem o `.SA` (o mesmo formato do CSV e da demonstração) e o sufixo entra só na chamada ao yfinance. `bare_ticker` tira o `.SA` digitado na entrada das rotas de importação (`PETR4.SA` vira `PETR4`), e `yfinance_symbol` o acrescenta em `from_yfinance`, no lote e no perfil quando o código tem o formato da B3; `BTC-USD`, `AAPL` e `^BVSP` seguem como estão. Uma migration de dados tirou o `.SA` dos ativos que já estavam gravados com ele, em `stock` e `ticker_profile`, e para sem mesclar quando o código já existe com e sem o sufixo. A doc de importação passou a mostrar os códigos sem `.SA`. Testes em `tests/test_import_ticker.py` e `tests/test_migrations.py`.

### F98 · arquivado em 2026-10-22

*Kanban:* Excluir partida salva · feature · ✅ Concluído · atende N35

**F98 — Excluir partida salva.** Serve N35. No diálogo "Simulações salvas" do lobby, cada partida ganha um botão de excluir, só para o host, com confirmação num `AlertDialog` que diz o nome, o período e quantos jogadores ela tem, e avisa que não dá para desfazer. O backend ganha `DELETE /api/simulation/{id}` com `HostVerified`, que recusa (409) a partida ativa e a selecionada no lobby. A maior parte dos dados sai em cascata, pelas chaves estrangeiras com `ondelete="CASCADE"` que apontam para `simulations`; a cópia congelada das séries da partida (as linhas com a versão igual ao id dela) não tem chave estrangeira e é apagada explicitamente na mesma transação. Depois da exclusão, um evento do Socket.IO avisa a sala para atualizar a lista. Gatilho: a lista de partidas salvas ficar difícil de usar.

### F80 · arquivado em 2026-10-22

*Kanban:* Cotações do dia numa consulta só · feature · ✅ Concluído

**F80 — Cotações do dia numa consulta só.** Implementada sobre a revisão 16eaa880, posterior à versão 2.1.0. `get_stocks_by_date` e `get_recent_closes` executam uma consulta cada, com JOIN LATERAL, corte temporal e ORDER BY price_date DESC LIMIT por ativo; a consulta externa reordena o minigráfico cronologicamente e o outer join mantém listas vazias. O filtro seen_by é aplicado antes do limite: respeita a versão explícita ou ativa, prefere a cópia congelada e usa a comum nos dias sem cópia, sem misturar partidas. A chave primária atual (stock_id, price_date, version) atende as buscas; não foi necessária migration ou índice duplicado. A consulta da última importação recebeu LIMIT 1 e preservou o filtro de origem real/versão comum. CandleDTO.from_prices centraliza as variações na lista e no detalhe sem mudar a API. O motor reutiliza nomes/classes por instância e o mercado usa sua classificação em cache; uma nova instância recarrega os metadados, e os preços continuam sem cache. LATERAL foi escolhido no lugar de DISTINCT ON/row_number para permitir buscas curtas pelo índice sem numerar todo o histórico. Ensaio local de 21/10/2026, Windows, Python 3.14.2, SQLAlchemy 2.1.4 e PostgreSQL 18.6: 50 ativos e 300.000 preços da versão comum, aquecimento e cinco repetições. Medianas: cotação de 51 consultas/1.821,949 ms para 1/3,287 ms; últimos 30 fechamentos de 51/28,155 ms para 1/4,462 ms. Resultados completos iguais aos da revisão de base; EXPLAIN ANALYZE confirmou busca reversa no índice do histórico e 1/30 linhas devolvidas por ativo. São 19 testes acrescentados: contagem constante com 1/50 ativos, datas sem pregão, corte temporal, janela vazia, valores zero, detalhe/mercado, catálogo e versões comum/congeladas/ativa. Suíte atual: 589 passaram e 3 testes do pacote embarcado foram pulados por falta dos arquivos empacotados; frontend: 74 testes passaram. Ruff do jogo, pyright, eslint, TypeScript e conferência do OpenAPI passaram. O check geral ainda encontra violações preexistentes em .plugin-build, trabalho separado preservado. A medição está em docs/docs/desenvolvimento/cotacoes-em-lote.md. Limitações: os tempos não medem o tick inteiro e a quantidade de cópias pode mudar o custo da filtragem; snapshots, apuração e notificações seguem com custos próprios.

### F112 · arquivado em 2026-10-22

*Kanban:* Ordenação em todas as tabelas de dados · feature · ✅ Concluído · atende N36

**F112 — Ordenação em todas as tabelas de dados.** Cabeçalhos com alternância crescente/decrescente em mercado, renda fixa, carteira, book, rankings, relatórios, exposição setorial, métricas da nota, histórico, séries, correlação, desempenho, tráfego e tabelas de ajuda. Comparadores sobre valores originais, textos em português, ausentes no fim e empates estáveis, sem alterar o cache. Escolha mantida nas atualizações enquanto a tabela está montada; membros acompanham a equipe, e a colocação oficial é preservada. Histórico ordenado no servidor antes da paginação, com coluna/direção na chave do cache; matriz mantém os índices originais dos pares ao ordenar os dois eixos. Cobertura: 627 testes de backend aprovados, 3 pulados, 102 de frontend aprovados, TypeScript, ESLint, pyright, Ruff do jogo e build; validação no navegador com dados de teste nos componentes reais. Frontend validado em cópia isolada com dependências anteriormente aprovadas, pois a instalação das versões mais recentes está incompleta; o check geral permanece bloqueado pelas violações preexistentes de .plugin-build. Evidências e limites em docs/docs/desenvolvimento/ordenacao-tabelas.md.

### F7 · arquivado em 2026-10-23

*Kanban:* Spike: estratégia Python escrita pelo usuário · feature · ✅ Concluído · atende N4 · decisões D5, D16 · marco M4

**F7 — Spike: estratégia Python escrita pelo usuário.** Mediu os dois lugares em que o código do usuário rodaria (D5), e com os números a escolha ficou na D16: o host roda só as estratégias do app, e quem quer uma estratégia própria usa um bot pela API. A medição usou quatro harnesses descartáveis: um executável de teste com o mesmo conjunto de módulos do app, que carrega um `.py` solto e tenta importar 45 módulos; um benchmark dos três jeitos de cortar uma estratégia travada (thread com exceção injetada, `sys.monitoring` e processo filho), com laço Python, laço em C e `sleep`; uma segunda instância do app, num banco descartável com o mercado sintético dos testes, operada por um bot em Python que só usa as rotas HTTP e o Socket.IO; e o mesmo bot com 80 ms de atraso simulado. Os números e os argumentos estão na D5. Limitações: o mercado sintético tem 4 ativos e 2 jogadores, então o tick a ×100 (36 a 44 ms) é bem mais rápido que o do mercado real; a rede remota foi simulada com atraso fixo, sem túnel de verdade; o processo filho foi medido fora do motor da simulação, com mensagens de exemplo.

### F8 · arquivado em 2026-10-23

*Kanban:* Modo automático: estratégia do jogador roda a cada tick · feature · ✅ Concluído · atende N4 · decisões D16, D8 · marco M4 · depende de F7 · dependência de F10, F110, F111

**F8 — Modo automático: estratégia do jogador roda a cada tick.** Origem: #2, #12, #14. Segue a D16 (as estratégias são classes do app) e a D8. Plano:
1. **Estratégia por jogador.** `SimulationEngine.set_strategy` deixa de guardar uma estratégia só para o motor e passa a `client_id` → estratégia, com a `ManualStrategy` (já é no-op) como padrão. Cada tick chama a estratégia de cada jogador antes do flush de eventos. Uma exceção na estratégia não derruba o tick: o motor a captura, devolve o jogador ao manual e registra o motivo, com o traceback, no log da estratégia.
2. **Classe base com contexto.** `next(ctx)` recebe a data, o caixa, as posições de renda variável e fixa, as ofertas de renda fixa do dia, as cotações com setor e segmento (`repository.stock.get_classification`), os indicadores do dia (CDI, Selic, IPCA) e o histórico OHLCV de um ativo como `DataFrame` do pandas, lido do banco na versão de séries da partida (o `MarketData` só guarda 30 candles). As ações são comprar e vender a mercado ou a limite, cancelar uma ordem aberta e aplicar em renda fixa; viram as mesmas chamadas que a interface faz (`matching_engine.submit`, `fixed_broker.buy`) em nome do jogador. O contexto é um retrato do dia em dados simples, montado pelo motor antes de chamar a estratégia.
3. **Registro das estratégias.** Cada estratégia do app declara nome, descrição, grupo (referência ou tática) e parâmetros (tipo, padrão e faixa); a página e a escolha de bot da F16 leem esse registro. As táticas que operam ações têm o parâmetro "ações que ela opera", uma lista editável que já vem com as 10 maiores do Ibovespa.
4. **Manual ou automático, um de cada vez.** Uma estratégia por jogador (combinar duas é a F110). Com o automático ligado, a boleta fica travada: para operar à mão, o jogador volta ao manual. A troca pede confirmação, que diz quantas ordens abertas do lado que sai serão canceladas, e as cancela. Estratégia ligada e parâmetro alterado valem a partir do próximo dia da partida.
5. **Página de Estratégias real.** Hoje é um mock que retorna 501. Passa a listar as estratégias registradas, separadas em referências e táticas, editar os parâmetros e alternar Manual | Automático, com três blocos para entender a estratégia: o painel "desde que ligou" (ordens emitidas, quanto o patrimônio andou e o Ibovespa no mesmo período); o gráfico do sinal, que mostra o que a estratégia olha (ex.: o preço com as médias de 50 e 200 dias) e se redesenha quando um parâmetro muda, antes de salvar; e o log das ordens, cada uma com o motivo em português, na mesma linha do tempo de ligar, desligar e erro.
6. **Log gravado.** Hoje só as execuções viram histórico. As ordens da estratégia, com o motivo, e as trocas de modo ganham tabela própria (migração), guardada pela partida toda e paginada na tela.
7. **Privado e no menu lateral.** Os outros jogadores não ficam sabendo do automático. Fora da página, ele aparece só em Estratégias no menu lateral (Ligada ou Desligada) e nos toasts: um por ordem em 1× e 2×, um resumo do dia em 4× ou mais. Erro na estratégia: toast com a causa e ponto vermelho em Estratégias até o jogador abrir a página, onde o traceback fica em "Detalhes técnicos".
8. **Retomada.** A estratégia ativa de cada jogador e os parâmetros dela ficam gravados na partida (migração) e voltam na retomada; o estado interno da estratégia não volta, ela deriva o que precisa do contexto, que tem o histórico.

Gatilho: a F7 está concluída; pode começar.

### F9 · arquivado em 2026-10-23

*Kanban:* Estratégias prontas de exemplo · feature · ✅ Concluído · atende N4 · marco M4 · depende de F8

**F9 — Estratégias prontas de exemplo.** Serve N4. Cinco estratégias simples e conhecidas, subclasses da classe base, com parâmetros editáveis na tela. Duas famílias: **referências**, para responder se uma estratégia bate o "não fazer nada", e **táticas**, para jogar no automático e como bots (F16) sem escrever código, como exemplo comentado para o guia da F10 e como teste da própria classe base.

- **Referências.** Comprar e segurar (BOVA11, ou a ação mais negociada se a partida não o tem) e rebalanceamento por meta, como o rebalanceamento do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): 60% em ações e 40% em renda fixa de liquidez diária, com limite de 5 p.p. por item; o aporte vai para o lado abaixo da meta.
- **Táticas.** IFR (compra ao cruzar abaixo do nível de compra, vende ao cruzar acima do de venda), rompimento com volume (compra ao passar a máxima dos últimos dias com volume acima da média, vende abaixo da mínima de saída) e momentum de 12 meses (as 3 de maior retorno, trocadas no 1º pregão do mês).
- **Bloco "O que ela olha".** Generalizado para cada estratégia: gráfico com 2º painel e faixas para o IFR, canal de máxima e mínima no rompimento, ranking em tabela no momentum e barras de atual × meta no rebalanceamento. A dica do termo técnico de cada estratégia vem do servidor.

Gatilho: F8 concluída.

### F16 · arquivado em 2026-10-23

*Kanban:* Bots na sala · feature · ✅ Concluído · atende N8 · decisões D8 · marco M6 · depende de F8 · dependência de F19

**F16 — Bots na sala.** Serve N8; segue a D8. O bot é um jogador sem socket: um registro em `users` marcado como bot, com carteira própria, e o motor chama o `next()` da estratégia dele a cada tick, como faz com a de um humano no automático. O host adiciona, configura e remove bots só no lobby, pela primeira vaga livre ("+ Adicionar bot"): um diálogo largo com as estratégias do app (referências e táticas) à esquerda e, à direita, o nome (da lista temática da estratégia, com sorteio e "<estratégia> #2" quando a lista acaba), a cor (a próxima livre, trocável), a equipe no modo em equipes e os parâmetros, com o exemplo em reais. Remover mostra um aviso com "Desfazer". O bot ocupa uma das 10 vagas e uma cor da paleta, e sai da sala na largada para morar só na partida; com uma partida salva escolhida, os bots dela entram travados, nas cores e equipes salvas. Recebe o aporte, o salário, as despesas e os imprevistos como qualquer jogador. Nas estatísticas entra no ranking e na nota como qualquer jogador, com o filtro "Todos | Só pessoas" (cada pessoa mantém a posição geral) e o cartão do bot ao passar o mouse no nome: quem o adicionou, a estratégia e os parâmetros. O log das ordens, com o porquê de cada uma, fica fechado durante a partida e abre para todos no fim. Bot em 1º não dá a ninguém as conquistas de vencer. Os apelidos de pessoas continuam únicos; o nome de um bot só precisa ser único na sala.

### F71 · arquivado em 2026-10-23

*Kanban:* Renda fixa com liquidez diária · feature · ✅ Concluído · atende N23

**F71 — Renda fixa com liquidez diária.** Serve N23. Títulos marcados com liquidez diária são resgatados em qualquer pregão, pelo valor corrigido até o dia: o dinheiro volta ao caixa no mesmo pregão. O IOF dos primeiros 30 dias entrou (96% do rendimento no 1º dia, caindo até 3% no 29º, zero a partir do 30º) e o IR regressivo incide sobre o que sobra depois dele. A reserva de emergência da página Meta passou a contar caixa + liquidez diária, e o aviso de cheque especial ganhou um botão que resgata o título que cobre a dívida. As estratégias ganharam a ação de resgate. O catálogo ganhou bancos reais, um CDB fixo de 100% do CDI sempre aberto e uma oferta rara acima de 100% do CDI com teto por jogador, que sai do catálogo quando o mês vira (quem já aplicou segue resgatando). A boleta ganhou a aba Resgatar com cotação ao vivo, e a Carteira mostra a tag de liquidez diária, o quanto é resgatável hoje e o botão Resgatar.

### F75 · arquivado em 2026-10-23

*Kanban:* Encerramento do loop sem thread viva nem simulação presa · feature · ✅ Concluído

**F75 — Encerramento do loop sem thread viva nem simulação presa.** Dois caminhos deixam o estado da partida inconsistente. (1) O `stop()` de `simulation_loop.py` espera a thread por 5 s e, se ela não terminar, só loga e segue: marca STOPPED, roda `EventManager.flush()` e `SimulationManager.clear_simulation()` enquanto a thread ainda pode processar um tick, gravando eventos de uma simulação que já foi liberada. (2) Uma exceção no loop cai no `finally`, que só muda o estado para STOPPED: a simulação continua registrada no `SimulationManager` sem loop rodando, e o `stop()` seguinte recusa com "Nenhuma simulação está em execução". Plano: o encerramento passa a ter um dono só, a própria thread: o `stop()` sinaliza e espera, e o flush e a liberação rodam no `finally` do loop, o mesmo caminho do fim natural da partida, que já faz isso. Se o join estourar o tempo, o `stop()` devolve erro em vez de liberar por cima. A exceção no tick também notifica os clientes (`simulation_ended` com motivo de erro), para a tela não ficar congelada. `pause()` e `unpause()` passam a usar o mesmo `_lock` de start e stop. Teste: o tick dublê que bloqueia além do tempo e o que lança exceção, nos testes do loop. Depende dos testes do loop para reproduzir os dois casos. Gatilho: junto com os testes do loop.

### F94 · arquivado em 2026-10-23

*Kanban:* Crédito · feature · ✅ Concluído · atende N33 · decisões D1 · dependência de F111

**F94 — Crédito.** Serve N33; segue a D1. Uma tela "Crédito" na partida, no grupo Você do menu lateral, no molde dos empréstimos do Capitalism Lab. O crédito existe em toda partida, sem chave nas regras.
1. **Patrimônio é sempre o líquido.** Em todo lugar (ranking, estatísticas, nota geral, fechamento), patrimônio passa a ser carteira menos dívida; sem dívida, o número não muda. A quebra ativos − dívida aparece na Carteira e só para quem deve.
2. **Nota de risco** em 8 níveis (AAA, AA, A, BBB, BB, B, CCC e D), recalculada todo mês a partir de 100 pontos: alavancagem (dívida ÷ patrimônio) vale 40, menos 4 a cada 10%; volatilidade da carteira vale 30, zero a partir de 45% ao ano; histórico de pagamento vale 30, menos 10 por parcela atrasada nos últimos 12 meses. A tela mostra a nota e o peso de cada parte, e um card de sugestões, separado e mais abaixo, diz o que a subiria (ex.: quanto quitar para chegar ao nível seguinte e quanto isso economiza).
3. **Oferta:** valor e prazo (6 a 60 meses), com o juro travado na contratação em SELIC do dia mais um spread por nota (+3, +4, +5, +6,5, +8, +10 e +13 pontos ao ano; D não recebe crédito novo) e um limite da dívida total em % do patrimônio (100, 80, 60, 45, 30, 20 e 10%). Esses números são o ponto de partida, ficam num lugar só do código e se calibram jogando. O jogador pode ter vários empréstimos até o limite, cada um com o seu juro travado: se a nota cair, só os próximos ficam mais caros. Antes de assinar, a tela mostra quanto se paga de juro no prazo todo e quanto a carteira precisa render ao ano para o empréstimo valer a pena. **Regra que impede dinheiro infinito:** o juro mais barato fica sempre acima da renda fixa mais cara oferecida no dia; ela vive só no código, porque com esses spreads quase nunca age.
4. **Parcelas** mensais fixas (Tabela Price), debitadas do caixa todo mês no dia da contratação. Quitação antecipada, total ou parcial (diminuindo o prazo ou a parcela), com abatimento proporcional dos juros, como garante o Código de Defesa do Consumidor (art. 52, § 2º).
5. **Sem caixa na data:** a parcela fica em atraso (fora do cheque especial), com multa de 2% (o teto do mesmo art. 52) e juro de mora de 1% ao mês, cobrado por dia; a nota cai e novos empréstimos ficam mais caros ou bloqueados. A partida não pausa: alguns dias antes do vencimento, se o caixa não cobre a parcela, um toast avisa e Crédito ganha um ponto no menu lateral. Nada é vendido à força: pagar o atraso é decisão do jogador.
6. **O que a sala vê.** O ranking mostra o patrimônio (em vermelho se negativo) e o selo "Negativado" em quem tem parcela atrasada; a dívida e a alavancagem de cada jogador ficam em Estatísticas › Risco.
7. **Eventos novos** (contratação, parcela paga, parcela em atraso, amortização, quitação), para a dívida se reconstruir numa retomada.

Estratégias e bots não pegam crédito (F111); quem está no automático paga normalmente as parcelas do que contratou à mão. Gatilho: livre; vem antes das expansões.

### F114 · arquivado em 2026-10-23

*Kanban:* Gráfico de ações que acompanha o preço · feature · ✅ Concluído · atende N19

**F114 — Gráfico de ações que acompanha o preço.** Serve N19. No `stock-chart.tsx` as duas séries (linha e velas) nascem com `priceScale().applyOptions({ autoScale: false })`, então a faixa de preços visível fica presa à do primeiro desenho; quando a partida avança e o preço sobe, ele passa da borda de cima e sai da área plotada. Plano: (1) tirar o `autoScale: false` das duas séries, deixando a escala vertical seguir o que está visível no período escolhido, com `scaleMargins` para o preço não encostar na borda; (2) quando a pessoa arrasta o eixo de preço à mão, a biblioteca desliga a escala automática, e o botão "Ir pro dia de hoje" a religa (`autoScale: true`) junto com o `scrollToRealTime()`; (3) conferir que os dias novos da partida entram na série sem refazer o gráfico, já que o efeito só recria nas trocas de tipo, período e ativo. Gatilho: o preço sair da área em qualquer ativo que sobe durante a partida.
**Aceite:** numa partida com o preço de um ativo subindo dia após dia, o preço fica dentro da área do gráfico em todos os períodos, sem mexer em nada.

### F115 · arquivado em 2026-10-23

*Kanban:* Estatísticas dizem que atualizam por mês e quando é a próxima · feature · ✅ Concluído · atende N38 · decisões D2

**F115 — Estatísticas dizem que atualizam por mês e quando é a próxima.** Serve N38; segue a D2. A tela de Estatísticas só busca o histórico de novo na virada do mês da partida (o evento `statistics_snapshot_update`, que `_create_daily_snapshots` emite só quando o mês muda), e nada na tela conta isso: os números ficam parados por semanas de jogo e parece que travaram. Plano: (1) o backend devolve, junto das estatísticas, a data da próxima virada do mês da partida, pela mesma regra que dispara o evento (cálculo de data no backend, como manda a D2); (2) o cabeçalho do relatório mostra "Atualizadas uma vez por mês de jogo · próxima atualização em X dias" (dias da partida, não do relógio), com uma dica explicando que as métricas fecham no mês porque risco e nota precisam de uma série de retornos mensais; (3) sem partida em andamento (pausada ou encerrada), o texto some. Gatilho: a dúvida de "por que não muda?" voltar.

### F116 · arquivado em 2026-10-23

*Kanban:* Gráfico da nota ao longo da partida · feature · ✅ Concluído · atende N9 · decisões D2, D10

**F116 — Gráfico da nota ao longo da partida.** Serve N9; segue a D10 e a D2. A nota geral era um número só, calculado sobre o último snapshot, e não dava para ver se o jogador vinha melhorando nem quando alguém passou alguém. Plano: (1) o backend calcula a nota (a mesma função da D10, sem versão paralela) sobre o histórico cortado no último snapshot de cada mês e no último dia, e devolve a série `data → nota total` de cada jogador, e de cada equipe como a média dos membros com nota, numa rota própria (`/api/statistics/score-history`); (2) a série começa no primeiro mês em que a nota existe, porque as métricas de risco ficam sem valor enquanto a série de retornos é curta; (3) na aba Geral, logo abaixo do ranking, um gráfico de linha no estilo dos outros, com uma linha por jogador (ou por equipe, na partida em equipes); você em destaque; com várias partidas comparadas, o gráfico não aparece. Decidido em 23/out: só a nota total, sem as linhas dos eixos. Gatilho: qualquer momento; a nota já existe, falta só a história dela.
**Aceite:** o último ponto da série é igual à nota geral mostrada hoje, para cada jogador.

### F117 · arquivado em 2026-10-23

*Kanban:* Atalhos de valor da renda fixa somam ao campo · feature · ✅ Concluído · atende N15

**F117 — Atalhos de valor da renda fixa somam ao campo.** Serve N15. Na boleta (`investment-ticket.tsx`), os atalhos "R$ 1 mil", "R$ 5 mil" e "R$ 10 mil" chamam `fill`, que troca o valor do campo; clicar duas vezes em "R$ 10 mil" deixa R$ 10 mil, e o esperado é R$ 20 mil. Plano: `fill` soma o atalho ao valor já digitado (`amount`, que já sai do texto normalizado) e reformata com `formatMoney(toCentsString(...))`; como o atalho deixa de recomeçar o valor, entra um botão "Limpar" ao lado, que zera o campo. O aviso de saldo insuficiente (`overCash`) continua valendo sobre a soma. Gatilho: qualquer momento, é um ajuste pequeno.

### F19 · arquivado em 2026-10-25

*Kanban:* Modo backtest: partida só de estratégias, sem interação · feature · ✅ Concluído · atende N4, N10 · decisões D8 · marco M6 · dependência de F28

**F19 — Modo backtest: partida só de estratégias, sem interação.** Serve N4 e N10; segue a D8. No lobby, "Rodar backtest" escolhe período, capital inicial, aporte e as estratégias participantes; cada estratégia vira um bot (F16) e a partida roda sem `sleep` entre ticks e sem eventos de socket por tick, mandando o progresso a cada N dias para a tela animar o gráfico. Ao fim, a partida fica salva como qualquer outra e abre no relatório da F17, já comparando as estratégias.

**Mercado isolado (padrão) ou compartilhado.** O backtest existe para comparar estratégias da forma mais justa e realista possível, então por padrão cada bot opera num mercado só dele: o impacto de preço da F13 é calculado a partir das ordens daquele jogador, e não da soma da sala, e o livro de ordens e a liquidez do market maker são separados por jogador. Todos veem o mesmo histórico, e só as próprias ordens movem o preço que cada um vê. Uma opção no lobby troca para mercado compartilhado, em que um interfere no preço do outro — o comportamento normal de uma partida multiplayer, que continua compartilhada sempre.

Referência de custo: o tick leva hoje ~50–100 ms (medido na F11), então 10 anos (~2.520 pregões) levam de 2 a 4 minutos — daí a animação. Medir onde vai o tempo do tick e tirar do caminho do backtest o que só serve à tela ao vivo (broadcast, snapshot por tick) faz parte. Gatilho: F16 concluída.
**Aceite:** duas estratégias idênticas, em mercado isolado e com a F13 ligada, terminam com o mesmo patrimônio.

### F33 · arquivado em 2026-10-25

*Kanban:* Indicadores técnicos · feature · ✅ Concluído · atende N19, N4 · decisões D2 · marco M11 · dependência de F34

**F33 — Indicadores técnicos.** Serve N19 e N4; segue a D2. `backend/features/technical_analysis/indicators.py` calcula, sobre o histórico de preço e volume, funções puras em pandas com parâmetros editáveis: médias móveis simples e exponencial (MMS, MME), Bandas de Bollinger (20 pregões, 2 desvios), IFR (14, faixas 70 e 30), MACD (12, 26, 9), estocástico (14, 3), ATR (14) e OBV. Implementação própria, sem TA-Lib, com teste de cada função contra valores calculados à mão; as estratégias de IFR, médias e rompimento importam dali, para decidir pelo mesmo número da tela. `POST /api/variable-income/{asset}/indicators` devolve as séries alinhadas às datas do preço, cortadas na data da partida, e o resumo do dia. No gráfico, médias (até 4) e Bollinger viram linhas sobre o preço, e volume, IFR, MACD, estocástico, ATR e OBV ganham painéis próprios. O botão "Indicadores" abre o seletor, que liga, desliga e edita cada um, com dica do que mede e como ler; as escolhas ficam salvas por jogador no campo `indicators` de `/api/settings` e valem para todas as ações. A legenda e os rótulos dos painéis acompanham a mira, e um X ou a engrenagem no hover desliga ou edita sem abrir o seletor. Embaixo do gráfico, o "Resumo técnico" lê os 7 indicadores com lado (o ATR aparece como "Sem lado"), ligados ou não, com os parâmetros do seletor: cada linha traz o valor, a leitura e o porquê, e o ponteiro mostra a nota (compras − vendas) ÷ indicadores lidos, em cinco faixas de Venda forte a Compra forte. Com pouco histórico, o resumo espera a maioria ter valor e diz a partir de qual pregão aparece. A página "Análise técnica" dos docs explica cada indicador.

### F49 · arquivado em 2026-10-25

*Kanban:* Spike: animação dos tópicos do tutorial · feature · ✅ Concluído · atende N25 · decisões D17 · marco M14

**F49 — Spike: animação dos tópicos do tutorial.** Fez o tópico "comprar uma ação" da janela "Como jogar" (F126) dos três jeitos — vídeo gravado pelo Playwright, animação em código com o `motion` e Remotion — e mediu tamanho no executável, nitidez, fidelidade e custo de manter. Com os números, a escolha ficou na D17: os tópicos se animam em código com o `motion`, e o vídeo e o Remotion ficam descartados para esse uso.

### F68 · arquivado em 2026-10-25

*Kanban:* Dica de firewall no lobby · feature · ✅ Concluído

**F68 — Dica de firewall no lobby.** Quando o link do lobby abre no computador do host mas não abre no dos amigos, o motivo costuma ser o firewall do Windows, e a orientação hoje só existe na página de multiplayer dos docs. Plano: no `frontend/features/lobby/components/lobby-header.tsx`, abaixo do link copiável, uma linha curta "Amigos não conseguem entrar?" que leva à seção "Amigos não conseguem entrar?" da página de multiplayer (o link do site de docs, em nova aba). Sem rota nova e sem estado: é texto estático com link. A tela do lobby é desenhada no canvas, então a linha entra primeiro lá (estado do lobby com a dica) e só depois no código.

### F87 · arquivado em 2026-10-25

*Kanban:* Erros de dado do yfinance na base · feature · ✅ Concluído · atende N3

**F87 — Erros de dado do yfinance na base.** Serve N3. Um dia é erro quando o fechamento se afasta mais de 50% do último pregão bom e, em até 5 pregões, volta ao nível de antes; o trecho vira interpolação linear entre o último pregão bom e o primeiro que volta, com abertura, máxima e mínima iguais ao fechamento e volume zero, e o dia fica marcado. Salto que não volta (B3SA3 −66% em 2011) e trecho no fim da série ficam como vieram; cripto fica de fora, porque pico que volta no dia seguinte é mercado. A importação aplica a correção usando o último fechamento guardado como âncora, e a Central de dados ganhou a chave "Corrigir ao importar" (ligada por padrão), o botão "Corrigir erros de dado" para a base já importada e o selo de dias corrigidos por ativo. O limiar foi medido em 15 ativos da B3: 50% e 70% pegam o CMIG4 sem marcar nenhum pregão legítimo, e 30% marca altas reais do MGLU3. O preço do dia corrigido é inventado, e a troca é essa: o erro deixa de aparecer na partida como se fosse mercado. A correção sobrescreve o preço original.

### F89 · arquivado em 2026-10-25

*Kanban:* Presets de partida · feature · ✅ Concluído · atende N30 · dependência de F90

**F89 — Presets de partida.** Serve N30. No lobby, o host salva as regras de agora com um nome ("Salvar como preset") e carrega um preset com um clique, no seletor do topo de "Editar regras". Entram período (as datas), saldo, aporte, modo de jogo (inclusive o modo em equipes), tipo de partida e suas regras, quem vence, assistências (Modo Especialista) e impacto de preço; não entram o nome da partida, quem está em cada equipe e o futuro gerado, que segue na Central de dados. Os presets moram numa tabela própria (nome único sem diferenciar maiúsculas, até 60 letras; configuração em JSON validada pelo mesmo DTO das regras da partida), por migration (D9), com rotas para listar, salvar, sobrescrever, renomear, apagar e carregar. Vêm prontos e não se renomeiam nem se apagam "Iniciante", "Clássico" e "Realista", semeados na migration. Carregar aplica na hora, sem confirmação, e avisa a sala pelo tempo real; preset que traz um campo que a versão atual não conhece ignora o campo, e o que falta vem do padrão, com um aviso ao host dos grupos que vieram do padrão. O servidor guarda qual preset está aplicado e o que mudou desde que foi carregado, então o seletor e o card da nova partida mostram o selo "modificado" para todos, e o host escolhe entre "Salvar alterações" (só em preset dele) e "Salvar como novo". Com uma partida salva selecionada o seletor fica desabilitado e salvar como preset continua.

### F95 · arquivado em 2026-10-25

*Kanban:* Expansão Governo & Política: partidos, eleição e impostos · feature · ✅ Concluído · atende N34, N23 · dependência de F106, F107, F128, F129, F130

**F95 — Expansão "Governo & Política": partidos, eleição e impostos.** Ligado à N34 e à N23. Mesmo molde da expansão "Gestoras" (F44): ligável por partida na aba "Expansões" do lobby, com nome, emblema e card próprios. Inspiração: a expansão de cidades do Capitalism Lab, em que o empresário funda um partido e disputa a prefeitura. Só liga em partida de pelo menos 5 anos, o tempo de uma campanha e um mandato. O card da aba Expansões traz duas opções: **qual ranking decide** a partida (o individual ou o de partidos) e a **dificuldade do computador** (fácil, médio ou difícil). (1) **Partidos:** só se concorre por partido; quem quer concorrer sozinho funda um partido de um filiado. O partido tem nome, sigla e cor (como o emblema da gestora, para não se confundir com jogador) e um **fundador**, que escolhe o candidato e o vice entre os filiados; o vice convidado aceita ou recusa. Cada filiado escolhe a **contribuição mensal** (pode ser zero), que sai do caixa dele e não volta, e a **verba de campanha** do partido é a soma das contribuições; a promessa da régua é a do partido. O jogador fica em um partido por vez; sair é livre e a contribuição para na hora; se quem sai é o candidato ou o vice, a vaga abre e o fundador indica outro filiado. O fundador pode **expulsar** um filiado, e a expulsão sai no feed da partida. Os candidatos do computador vêm de partidos do computador, com sigla e cor (cinza e tracejado nas telas). (2) **Rankings:** o ranking individual e o **ranking de partidos** aparecem lado a lado; o patrimônio do partido é a soma dos patrimônios dos filiados, e a opção do card diz qual dos dois decide a partida. O ganho de governar chega a cada um só pela própria carteira (imposto menor no que ele tem, setor isento que ele carrega), sem caixa do partido para repartir. (3) **Eleição:** a candidatura abre um ano antes. Concorrem os partidos de jogadores que inscrevem chapa e partidos do computador, que **só completam as vagas** quando há menos de 3 chapas. A verba vira apoio aos poucos e com retorno decrescente (dobrar a verba não dobra o voto), e por isso começar cedo pesa. Verba, contribuições e promessa são **públicas**, e o que cada filiado contribui **sai do patrimônio** dele no ranking. Uma pesquisa de intenção de voto mostra a corrida num gráfico ao longo dos meses, com a cor e a sigla de cada partido. Se ninguém passar de 50%, há **segundo turno 3 semanas depois** (1º turno em 7 de outubro, 2º em 28): os eleitores de quem ficou de fora vão para o finalista com a promessa mais parecida na régua. Entre os turnos, um jogador de partido eliminado pode **doar verba a um finalista**, a favor ou contra quem lidera; a doação é pública e sai do patrimônio dele. **Computador:** a verba mensal dele é 0,5, 1 ou 1,5 vez a média dos jogadores (fácil, médio ou difícil), e a promessa dele vai para a faixa mais vazia da régua. Mandato de 4 anos, com uma reeleição. (4) **Impostos por setor:** o governo mexe nos impostos que o jogo já cobra (os 15% e 20% da renda variável, a isenção de vendas de ações até R$ 20 mil, a tabela regressiva da renda fixa, a isenção de LCI e LCA) e pode taxar ou isentar um setor ou segmento, que todo ativo já tem: "isentar o IR de energia", "taxar bancos em mais 5 pontos". Imposto vale em qualquer período, porque não mexe em preço. (5) **Ritmo das medidas:** o presidente propõe a qualquer momento e a medida entra numa **fila do Congresso, pública desde a proposta**, sem pausar a partida. O Congresso vota a fila no fechamento do mês, com chance de passar igual à aprovação do governo (40% de aprovação, 40% de chance); o presidente pode retirar uma medida antes do voto, e a rejeitada pode voltar à fila. A aprovada só vale **90 dias depois**, como a noventena, para os outros terem tempo de reagir. (6) **Aprovação:** uma métrica sempre à vista, com o histórico num gráfico, que começa em 50% na posse e se move pelos fatores: inflação na meta soma 4 pontos e cada ponto de inflação acima da meta tira 3; a bolsa nos últimos 12 meses soma ou tira 1 ponto a cada 5% de alta ou queda (até 6 pontos); imposto novo tira de 1 a 5 pontos quando passa a valer, efeito que some em 6 meses; corte de imposto soma de 1 a 3; e a promessa descumprida tira 3 pontos por faixa de distância na régua. **Régua de 1 a 5:** corte geral de imposto é 1, isenção setorial 2, taxar um setor 4 e imposto geral novo 5 (o gasto público da F106 fica entre 4 e 5); a marca do governo é a média das medidas aprovadas, e a distância dela até a promessa da campanha é a que pesa. Aprovação baixa perde a reeleição e, abaixo de um piso por meses seguidos, leva a **impeachment**: assume o **vice**; sem vice, um governo neutro do computador, sem medidas novas, até a próxima eleição. No impeachment, a medida já aprovada segue os 90 dias, a fila não votada some e a carteira de quem saiu volta a operar. (7) **O presidente e a própria carteira:** ele **vence pelo patrimônio**, como todos, e tem a **carteira congelada**: não compra nem vende enquanto governa, porque sabe da medida antes de todos. Governar a favor da carteira congelada é o jeito de ele ganhar governando, e faz parte do jogo: quem vai assumir monta a carteira antes da posse, por isso a carteira congelada do presidente é pública, para a sala ler o interesse dele e se posicionar contra ou junto. Com a expansão Gestoras ligada, o que acontece com a gestora do presidente na posse está na F44. (8) **SELIC:** o Banco Central segue autônomo, como no Brasil desde 2021, e a SELIC reage à inflação como no gerador; a opção de pô-la nas mãos do governo é a F97. **Nas features seguintes:** o gasto público e a inflação, o efeito das medidas por cima das séries (F106), e os perfis de público na eleição (F107). **Decidido em 24/out:** o impeachment vem com a aprovação abaixo de 25% por 3 meses seguidos. A verba vira apoio pela raiz quadrada do gasto de cada mês, acumulada mês a mês, e a intenção de voto é a fatia de cada partido no apoio somado: R$ 10 mil por mês durante 4 meses dão 400 de apoio, e os mesmos R$ 40 mil num mês só dão 200. A expansão liga em qualquer tipo de partida de pelo menos 5 anos, e com ela ligada surge a **vitória política**, exclusiva da expansão e com o emblema dela: vence o partido com a maior soma de patrimônio dos filiados. O padrão continua sendo a vitória financeira, e por isso a escolha do ranking que decide sai do card da aba Expansões e vira um quarto tipo de partida, "Política", ao lado de Clássica, Corrida à meta e Viver de renda, só com a expansão ligada e no modo individual, porque os partidos já são os times; fora dela, o ranking de partidos aparece só como informação.

### F108 · arquivado em 2026-10-25

*Kanban:* Bot pela API: guia e exemplo · feature · ✅ Concluído · atende N4 · decisões D16 · marco M4

**F108 — Bot pela API: guia e exemplo.** Serve N4; segue a D16. A página "Bot pela API" (grupo "Como Usar" do Docusaurus) percorre o caminho de um bot: cookie em `/api/session/init`, nickname em `/api/user/register` (e `/api/user/claim` para voltar ao mesmo jogador), espera da partida por `pending_join` em `/api/session/me`, entrada em `/api/simulation/join` com uma cor da paleta, assinatura de `simulation_update` no Socket.IO e, a cada tick, a leitura do mercado e da carteira e as ordens de ações e de renda fixa. Traz o bot completo de exemplo em Python (`requests` + `python-socketio`), que segue o cruzamento de médias 50/200 das estratégias prontas e também está para download, e as limitações: o bot fica fora do backtest, e com o tick mais rápido que a reação dele as ordens caem dias depois (números na D5). O exemplo rodou de ponta a ponta contra uma segunda instância do app: entrou na partida, recebeu os ticks e executou compras e vendas. As rotas de hoje bastaram, sem rota nova. A página embute o código do exemplo, e um teste confere que as duas cópias são iguais.

### F113 · arquivado em 2026-10-25

*Kanban:* Classe de ativo cripto com quantidade fracionária · feature · ✅ Concluído · atende N37 · decisões D3 · dependência de F127

**F113 — Classe de ativo cripto com quantidade fracionária.** Serve N37; segue a D3. Hoje a quantidade é inteira da ordem ao banco (`equity_event.quantity` é `Integer`, e `quantity` é `int` nos DTOs de ordem, de prévia e de evento, no motor e no `max_quantity` da prévia), então um ativo de preço alto como o bitcoin só se compra em unidades inteiras. Plano: (1) **Classe nova:** `CRYPTO` no `AssetClass`, escolhível na tela de importação (que já troca a classe de um ativo) e valendo para `BTC-USD` e afins, que o importador já aceita. (2) **Quantidade decimal:** a coluna vira `NUMERIC(20,8)` por migration (oito casas, a precisão do satoshi) e os DTOs passam a `Decimal`, serializado em string (D3); ação, FII, ETF e BDR continuam aceitando só inteiro, e a validação da ordem recusa fração fora de `CRYPTO`. (3) **Motor:** compra, venda, preço médio, `max_quantity` da prévia (arredondado para baixo nas oito casas) e o impacto de preço passam a operar em `Decimal`. (4) **Imposto:** `income_tax` ganha a categoria cripto, com regra própria a conferir na implementação. (5) **Telas:** o campo de quantidade da ordem aceita vírgula quando o ativo é cripto, e a quantidade da carteira e do histórico exibe as casas necessárias. Gatilho: o uso pedir bitcoin na carteira, ou a F22 e a F100 mexerem em quantidade e proventos, já que convém migrar a coluna uma vez só.

### F118 · arquivado em 2026-10-25

*Kanban:* Lembrar a última configuração da partida · feature · ✅ Concluído · atende N30 · decisões D9

**F118 — Lembrar a última configuração da partida.** Serve N30; segue a D9. As regras pendentes moram em memória no `SettingsManager`, que nasce dos padrões do `config.toml` (início em 2000-01-01, por exemplo) a cada abertura do app, então o período, o capital, o aporte e o resto voltam ao padrão toda vez e o host refaz tudo. Plano: o lugar é o banco, porque as regras são do servidor do host (o formulário do lobby é semeado por elas) e o banco embarcado sobrevive entre aberturas. (1) Migration (D9) com uma tabela de uma linha só, `last_simulation_settings`, com a configuração em JSON validada pelo mesmo DTO das regras; (2) o `SettingsManager.update` grava essa linha quando as regras mudam, e o `get` a lê no lugar do `config.toml` quando existe, caindo nos padrões do arquivo se estiver vazia ou se um campo novo faltar; (3) o `config.toml` continua sendo o padrão de fábrica, e uma opção "Restaurar padrões" no formulário apaga a linha. O nome da partida não entra (é gerado a cada uma). A F89 (presets) pode ler a mesma linha como o preset "Última partida". Gatilho: o uso do lobby pedindo para não remontar as regras.
**Aceite:** mudar o início para 2012, fechar e abrir o app, e o formulário abre com 2012.

### F119 · arquivado em 2026-10-25

*Kanban:* Seletor de período da partida com linha do tempo · feature · ✅ Concluído · atende N15, N30

**F119 — Seletor de período da partida com linha do tempo.** Serve N15 e N30. O início e o fim da partida saíram dos dois `DateField` soltos para um bloco "Período" no `rules-sheet.tsx`: a duração no cabeçalho ("6 anos e 7 meses"), atalhos em dois grupos ("Até hoje": 5 anos, 10 anos, 20 anos e Tudo; "Pra frente": 5 anos e 10 anos), uma linha do tempo de 1993 a 2040 pintada pelo dado que a base tem (sem dado, dado real, futuro gerado e repete o último valor) com o marcador de hoje, duas alças e uma barra que move o período inteiro mantendo a duração, e os campos Início e Fim com o botão "Hoje" e o calendário com "Hoje", o dia de hoje em destaque e o futuro em violeta. A escolha vale na hora, sem botão de aplicar; alças e barra andam em meses inteiros (início no dia 1, fim no último dia do mês) e param no primeiro dia com dado e em 31/12/2040, com um aviso na linha. Atalho que começaria antes do primeiro dia com dado de um indicador fica desligado com o motivo. O aviso de cobertura (`CoverageAlerts`) continua abaixo, e a data digitada mantém o aviso. A matemática mora em `lobby/lib/period.ts`, com testes.

### F121 · arquivado em 2026-10-25

*Kanban:* Comprar tudo a mercado sem estourar o caixa · feature · ✅ Concluído · atende N15 · decisões D3

**F121 — Comprar tudo a mercado sem estourar o caixa.** Serve N15; segue a D3. A boleta de renda variável calcula o "Máx" com o caixa e o preço da prévia (`preview_order`: o melhor preço de venda do book, ou o último fechamento), mas a ordem a mercado só é conferida na execução, contra o preço do momento (`_validate_market_order` em `broker.py`). Com o jogo rodando, o preço anda entre o clique e a execução, e a quantidade que cabia na prévia volta como "Saldo insuficiente". Plano: (1) **Ordem a mercado por valor:** a boleta ganha o modo "por valor" e o botão "Tudo" (o caixa inteiro); o DTO da ordem aceita `amount` (Decimal em string) no lugar da quantidade, e o motor calcula a quantidade na execução com o preço que valeu, arredondando para baixo (inteiro, e oito casas para cripto); nunca estoura. (2) **Quantidade que se ajusta:** na compra a mercado por quantidade, o valor enviado vale como teto: se o preço subiu até a execução, o motor compra a maior quantidade que ainda cabe no caixa em vez de recusar, e só recusa se nem uma unidade couber. (3) A boleta mostra a quantidade como estimada antes do envio, e a executada no retorno e no histórico. O desenho do modo "por valor" e de como a boleta mostra a quantidade comprada sai do canvas antes do código. Gatilho: livre.
**Aceite:** com o preço subindo 5% entre o clique em "Tudo" e a execução, a compra executa sem "Saldo insuficiente" e deixa no caixa menos que o preço de uma unidade.

### F124 · arquivado em 2026-10-25

*Kanban:* Voltar o quadrado da marca no cabeçalho da sala · feature · ✅ Concluído · atende N15

**F124 — Voltar o quadrado da marca no cabeçalho da sala.** Serve N15. No lobby, o `BrandMark` ao lado de "Sala de ..." (`lobby-header.tsx`) virou a rosca de três fatias na troca da marca do app; antes era um quadrado arredondado azul com o ícone de barras crescentes (`ChartNoAxesColumnIncreasing`, traço 2,4). Plano: o `BrandMark` ganha a variante `square`, que traz de volta o quadrado azul (`bg-primary text-primary-foreground`, cantos arredondados e ícone proporcionais a cada tamanho, como era no commit anterior à troca) ao lado da variante `logo`, que continua sendo a rosca e o padrão; só o cabeçalho do lobby usa `square`, e a barra lateral, a tela de carregamento e o login mantêm a rosca. Gatilho: qualquer momento, é um ajuste pequeno.

### F10 · arquivado em 2026-10-26

*Kanban:* Guia de como escrever uma estratégia · feature · ✅ Concluído · atende N4 · marco M4

**F10 — Guia de como escrever uma estratégia.** Origem: #49. Página no Docusaurus (grupo "Desenvolvimento"): como acrescentar uma estratégia ao app, com a classe base, o contexto que ela recebe a cada tick, como declarar nome e parâmetros e onde registrá-la para aparecer na página de Estratégias, nos bots e no backtest; uma das estratégias da F9 comentada linha a linha; e os limites (uma exceção devolve o jogador ao manual, o estado interno não volta na retomada). Quem não quer mexer no código do app tem o bot pela API (F108). Gatilho: F8 concluída — a API da classe base só fica estável depois dela.

### F96 · arquivado em 2026-10-26

*Kanban:* Dicas de análise técnica · feature · ✅ Concluído · atende N19 · marco M11 · depende de F126 · dependência de F131

**F96 — Dicas de análise técnica.** Serve N19. Aprender análise técnica jogando: o gráfico de velas aponta e explica o que um trader enxergaria. É ajuda, então o modo Especialista (F40) a desliga, como as outras, com um interruptor próprio (Esconder dicas de análise técnica). (1) Padrões de vela: 11 padrões clássicos detectados por regras fixas (martelo, martelo invertido, enforcado, estrela cadente, doji, engolfo de alta e de baixa, estrela da manhã e da tarde, três soldados brancos e três corvos negros). Marcador com o nome sobre a vela, faixa atrás dos padrões de várias velas, interruptor "Padrões de vela" no topo do gráfico, lista recolhível dos padrões do período e card "E se ele acertou?" ao passar o mouse, com o desenho animado do padrão, o contorno dos 5 pregões seguintes e a taxa de acerto (só com 10 ocorrências ou mais). (2) Indicadores (F33): legendas "Sobrecomprado"/"Sobrevendido" no IFR e círculo com frase nos cruzamentos do MACD e das médias móveis. (3) Desafio da vela: quando surge um padrão com lado, o jogo pergunta "sobe ou desce?" e confere no fechamento do 5º pregão, com placar, cartão no fim da partida e as conquistas Primeira leitura e Leitor de velas. O preset Realista passou a esconder as dicas, para o rótulo Especialista continuar valendo.

### F125 · arquivado em 2026-10-26

*Kanban:* Revisão das regras de lint e da checagem de tipos · feature · ✅ Concluído

**F125 — Revisão das regras de lint e da checagem de tipos.** Cada candidata foi medida rodando a ferramenta no código atual e julgada regra a regra, não pela categoria inteira: fica o que aponta bug, código morto ou risco de segurança; saem reescrita de estilo e falso positivo. Toda regra ligada é erro, porque o pyright e o oxlint saem com código 0 em aviso e o aviso se acumularia.

**Ruff.** `ERA` (código comentado, 0 achados). `DTZ` (data sem fuso): o app grava `datetime.now(UTC)` e o banco usa `DateTime(timezone=True)`, então misturar data com e sem fuso é bug; os 5 `noqa` são de data local do app. `PLE` (erros que o Python só mostra ao executar, 0). `PLW` menos `PLW0603` (os `global` são caches de módulo) e `PLW0108` (o lambda do `monkeypatch` adia a busca do nome): pegou 2 `subprocess.run` sem `check` e uma variável de `for` reescrita. `S` (segurança) menos `S311` (o `random` é do jogo, não de criptografia), `S603` e `S607` (os `subprocess` chamam comandos fixos): os 15 achados eram de propósito (SQL montado nas migrations, `urlopen` do BCB, bind em `0.0.0.0` para a rede local) e levam `noqa` com o motivo. `LOG` (2 `logger.exception` fora de `except`, que podem sair sem traceback). `PGH` (11 `# type: ignore` sem código, que escondem erro novo na mesma linha). `FAST` (6: `Annotated` nas dependências e `response_model` redundante). `BLE` (4 `except Exception`, todos de propósito: erro de estratégia de terceiro devolve o jogador ao manual). Do `PT`, só a `PT011` (2 `pytest.raises` sem `match`, que passam pelo motivo errado). O lint também roda `ruff format --check` (os recortes de código dos guias em Markdown ficam fora).

**Asserts.** O executável é empacotado com `optimize=2`, que apaga docstrings e `assert`. Os 45 `assert` do backend viraram `required()` (`backend/core/utils`), que levanta erro também no executável, ou `if`/`raise` explícito onde a checagem não é de `None` (tipo de parâmetro de estratégia, quantidade zero numa ordem). A `S101` vale no backend e libera `tests/` e `scripts/`.

**pyright.** Modo `standard`. `reportUnusedFunction` e `reportUnnecessaryComparison` são erro. `reportUnnecessaryTypeIgnoreComment` (9 dos 11 `# type: ignore` sem código e 19 dos com código estavam mortos) e `reportDeprecated` (`Iterator` trocado por `Generator` nos `@contextmanager`) estão ligados. Ficam fora `reportUnnecessaryIsInstance` (1 achado, validação de fronteira em `base_strategy.py`) e `reportUnnecessaryCast` (3, casts do pandas, cuja inferência muda com a ordem em que o pyright avalia os arquivos).

**oxlint e tsc.** A categoria `correctness` inteira e o `exhaustive-deps` são erro, e `only-export-components`, `incompatible-library` e `unsupported-syntax` também. Ligadas: as `no-unsafe-assignment`, `-argument`, `-member-access`, `-return` e `-call` (`any` vazando de `JSON.parse` e do zod; os componentes do shadcn em `shared/components/ui` e o `.pnpmfile.cjs` ficam fora); `no-deprecated` (o `Cell` do Recharts virou o `fill` da fatia); `no-unnecessary-type-assertion`, `-type-arguments`, `-type-conversion` e `-template-expression` (código morto, com autofix); `switch-exhaustiveness-check` com `considerDefaultExhaustiveForUnions` (`switch` sem `default` que esquece um caso da união é erro). No `tsc`, `noImplicitReturns` garante que todo caminho de uma função com retorno retorna.

**Medidas e deixadas de fora.** Ruff `C4`, `RET`, `PIE`, `FBT`, `FURB157`, `SLF`, `INP` e `PLR` são estilo e refatoração. `ARG` (18 no backend) é quase toda assinatura exigida (handler do FastAPI, método base de estratégia, `lifespan`); os dois parâmetros mortos de verdade, em funções privadas do governo, saíram. No oxlint: `pedantic` (`prefer-readonly-parameter-types` 2.332, `no-confusing-void-expression` 490, `strict-boolean-expressions` 428), `no-unsafe-type-assertion` (141), `eqeqeq` (o `== null` é idioma), `no-unstable-nested-components` (17, funções de render do Recharts e do `toast`), `prefer-nullish-coalescing` (11, todos `||` de propósito), `no-unmodified-loop-condition` (o `setDate` muda a data dentro do laço), `style-prop-object` (o `style` textual do aviso do tutorial), `exhaustive-effect-dependencies` (o `id` no array é de propósito), `no-accumulating-spread` (listas de rótulos pequenas) e `jsx-no-constructed-context-values` (os providers ficam na raiz e o valor muda com o dado de todo jeito).

**Formatação.** O frontend é formatado pelo oxfmt (`frontend/.oxfmtrc.json`, 120 colunas: é a largura que menos mexe no código existente, 214 arquivos contra 470 com 100 e 317 com 140). O `check` do frontend roda `oxfmt --check` e o `pnpm format` da raiz formata backend e frontend. O `frontend/.gitattributes` fixa LF na cópia local, porque o oxfmt não aceita fim de linha automático e o Windows faz checkout em CRLF.

O que ficou para depois tem card próprio: tipos mais rígidos no frontend ([F135](#f135)), código e dependências sem uso ([F136](#f136)), acessibilidade ([F137](#f137)) e o piloto do strict do pyright ([F138](#f138)).

### F126 · arquivado em 2026-10-26

*Kanban:* Janela "Como jogar" · feature · ✅ Concluído · atende N25 · decisões D17 · marco M14 · dependência de F132, F133, F131, F158

**F126 — Janela "Como jogar".** Serve N25. Tutorial no molde das Dicas e truques do Factorio, com cada tópico animado em código com o `motion` (D17). **Entregue:** a janela (lista de tópicos à esquerda, tópico à direita com ilustração, passos e dica, "Próximo" no rodapé), o palco reutilizável (componentes reais do app com contextos de exemplo, um `fetch` de exemplo só para a prévia de ordem, cursor e destaque que medem o DOM) e três tópicos no grupo "Renda variável": "Comprar uma ação" e "Ordem a mercado e limitada" (passo a passo animado) e "Alavancagem" (conceito, ilustração numérica; é o destino do "Saiba mais" da dica de alavancagem em Crédito). Tópico novo entra no registro `features/tutorial/lib/topics.ts` com id, grupo, texto e ilustração. **Nunca abre sozinha:** abre pelo botão do lobby, ao lado de Conquistas, e por um acesso na partida que o jogador escolhe em Configurações (aba na borda, padrão; item no menu; botão na topbar; desligado). **Aviso pelo contexto:** o primeiro tópico não visto da tela avisa uma vez, ancorado no acesso escolhido. "Visto" é abrir o tópico; o navegador guarda o que foi visto e avisado. **Tempo:** com um só jogador humano (bots não contam) e o tempo andando, abrir pausa e fechar retoma só se a janela pausou; com mais gente o tempo segue e o cabeçalho avisa. Se a animação não carrega, fica a imagem parada com "Tentar de novo". Com movimento reduzido a animação nasce pausada. O estado "depois de atualizar" não foi desenhado: as Novidades (F56) ainda não existem. Os demais tópicos saem nas F132 e F133.

### F142 · arquivado em 2026-10-26

*Kanban:* Banco da 3.0: regras em JSON, conquistas preservadas e migrations por versão · feature · ✅ Concluído · decisões D18

**F142 — Banco da 3.0: regras em JSON, conquistas preservadas e migrations por versão.** Entregue com a D18. **Regras da partida:** as 24 colunas de regra de `simulations` viraram um campo JSON `rules`, no mesmo formato do preset e das últimas regras; a leitura é estrita e passa por um decodificador só, que serve a lista de salvas, as estatísticas e a troca das séries geradas. Regra nova é um campo do DTO com valor padrão, sem migration. **Conquistas:** sobrevivem à exclusão da partida em que saíram (a chave vira `SET NULL`), e a tela mostra "Partida excluída". **Migrations:** a inicial é o banco da 2.3 e a da 3.0 junta tudo o que veio depois; quem está na 2.3 atualiza sem perder nada, e da 2.0 à 2.2 o app recusa e manda abrir uma vez na 2.3. **Trava de dado perdido:** conta cada valor do primeiro nível de um JSONB como uma célula. Conferido com o `pg_dump --schema-only` da cadeia antiga contra o da nova, nos dois pontos (2.3 e 3.0), e com uma partida criada pela 2.3 aberta na 3.0.

### F146 · arquivado em 2026-10-26

*Kanban:* Bots "saindo" ao iniciar a partida · feature · ✅ Concluído · atende N8 · marco M16

**F146 — Bots "saindo" ao iniciar a partida.** Serve N8. A liberação dos bots no início da partida (`release_bots`) deixou de emitir a saída de cada um; o aviso "saiu da sala" só vem de `remove_bot` e da troca para uma partida salva. O front refaz a lista de jogadores ao receber o início da partida (`SimulationProvider`). Testes em `tests/test_bots.py`: nenhuma saída ao iniciar com bot na sala, e a saída continua saindo ao remover o bot.

### F148 · arquivado em 2026-10-26

*Kanban:* Empréstimo que não se deixa pagar com o jogador negativado · feature · ✅ Concluído · atende N33 · marco M16

**F148 — Empréstimo que não se deixa pagar com o jogador negativado.** Serve N33. A alavancagem (dívida ÷ patrimônio líquido) passou a ser nula quando o patrimônio é zero ou negativo, em todo lugar que a calcula: `leverage` devolve nulo (sem limite) e `leverage_points` pontua zero nesse caso. Isso tirou o `Infinity` que quebrava a simulação de empréstimo, o resumo da nota e o fechamento mensal. No DTO, `leverage_before` e `leverage_after` da simulação e o `value` da alavancagem na nota ficaram nulos, e a tela mostra "—". Testes em `tests/test_credit_book.py` (simulação e resumo com patrimônio zero e negativo) e `tests/test_credit_rating.py`. Em aberto: refazer o pagamento na partida salva do playtest para confirmar que a recusa vinha desse erro; no código, o valor do botão e a conferência de caixa (`_require_cash`) usam o mesmo caixa e as mesmas cobranças do dia.

### F147 · arquivado em 2026-10-26

*Kanban:* Nome do presidente eleito aparecendo como null · feature · ✅ Concluído · atende N34 · marco M16

**F147 — Nome do presidente eleito aparecendo como null.** Serve N34. O aviso da posse lia um campo que o servidor não enviava e mostrava "null toma posse". O evento da posse agora leva a sigla e o nome do presidente (apelido do jogador ou nome do candidato do computador), e a posse e o resultado do turno mostram "O candidato do ABC" quando a chapa não tem candidato.

### F144 · arquivado em 2026-10-26

*Kanban:* Ajustes de layout do playtest · feature · ✅ Concluído · atende N15, N34 · marco M16

**F144 — Ajustes de layout do playtest.** Serve N15 e N34. (1) Aba Expansões do lobby: o card do Governo ocupa a largura da aba (o grid externo deixou as duas colunas) e as regras internas se dividem em duas colunas só a partir de `lg` (`expansion-fields.tsx`). (2) Sigla do partido: o teto subiu de 5 para 8 letras no DTO (`PARTY_ABBR_PATTERN`), no `government_book.py`, no formulário de fundação (padrão, `maxLength` e textos), na descrição da rota e na página Governo da docs; `openapi.json` e os tipos regenerados. Os lugares que mostram a sigla (selo `PartyMark`, pesquisa, resultado do turno, ranking, topbar do governo) já têm o selo sem encolher e o resto da linha quebra ou trunca, então nenhum pedia ajuste. Teste em `tests/test_government_book.py`: sigla de 8 letras aceita; 1 e 9 recusadas. (3) Rentabilidade por jogador: a raiz da aba (`returns-tab.tsx`) passou a `grid-cols-1`, coluna `minmax(0,1fr)`, de modo que o conteúdo largo deixa de alargar a página e a tabela rola dentro do próprio card. Em aberto: conferir com uma partida longa e uma sigla de 8 letras rodando no app; nesta sessão a checagem foi só por código, `tsc` e testes.

### F149 · arquivado em 2026-10-26

*Kanban:* Desligar o automático na própria boleta · feature · ✅ Concluído · atende N4, N15 · marco M16

**F149 — Desligar o automático na própria boleta.** Serve N4 e N15. O aviso das boletas travadas ganhou o botão "Desligar o automático", que chama a mesma mutation da página de Estratégias (movida para shared/hooks/mutations) e destrava a boleta no lugar, mantendo ativo, lado, quantidade e preço; o link "Ir para Estratégias" continua. Vale para a boleta da renda variável e as da renda fixa. Sem confirmação: as ordens abertas são canceladas ao desligar, como na página de Estratégias.

### F155 · arquivado em 2026-10-26

*Kanban:* Filtro "Na carteira" na renda fixa · feature · ✅ Concluído · atende N15 · marco M16

**F155 — Filtro "Na carteira" na renda fixa.** Serve N15. Entregue: o filtro "Na carteira · N" (contagem dos títulos da lista que o jogador tem) ao lado dos filtros de liquidez e isenção; com ele ligado, cada título mostra o valor aplicado.

### F150 · arquivado em 2026-10-26

*Kanban:* Aviso de abertura da campanha · feature · ✅ Concluído · atende N34 · marco M17

**F150 — Aviso de abertura da campanha.** Serve N34. Entregue: no dia em que a campanha abre (inclusive quando já abre no primeiro dia da partida) a partida pausa para todos e um diálogo conta a data do 1º turno e o dia em que as chapas fecham, com atalhos para Fundar partido e Filiar-se (quem não tem partido) ou Contribuição (quem tem), que abrem a página da eleição já com o diálogo certo. Dois lembretes sem pausa, como toast: 7 dias antes de as chapas fecharem e na véspera do 1º turno (o último dia útil antes da votação). Os avisos são eventos em tempo real; a retomada de uma partida não repete a abertura. Teste novo garante que a contribuição de campanha não é cobrada antes da campanha, entre os turnos nem depois do resultado. Fora: cada aviso virar entrada da caixa de entrada, que ainda não existe.

### F156 · arquivado em 2026-10-26

*Kanban:* Estatísticas rápidas em partida longa · feature · ✅ Concluído · atende N40, N38 · marco M16

**F156 — Estatísticas rápidas em partida longa.** Serve N40 e N38. Entregue: medido numa partida sintética de 10 anos com 4 jogadores, a leitura dos snapshots leva ~0,5 s e o cálculo das abas fica entre 0,4 s e 0,9 s cada; o gargalo era a nota ao longo da partida, que recalculava a nota de cada mês desde o início (~16 s). Agora as abas Geral, Rentabilidade, Risco, Nota, Composição e Operações da partida em andamento são montadas uma vez por mês e servidas do guardado até a próxima virada; o guardado sai também quando a meta sobe pelo IPCA e quando entra jogador, e vive no objeto da partida, então a retomada começa vazia. A nota de cada mês já fechado é guardada à parte e a virada calcula só o mês novo (de ~16 s para ~0,7 s). Numa simulação só com mais de um ano, as séries dos gráficos trazem o fechamento de cada semana (até cinco anos) ou de cada mês; entre simulações e no backtest continua um ponto por pregão. Fora: a primeira abertura da nota depois de retomar uma partida longa ainda calcula todos os meses uma vez (~16 s em 10 anos); o fechamento e a comparação não usam o guardado; conferência com o painel de desempenho no app rodando.

### F145 · arquivado em 2026-10-26

*Kanban:* Convite de vice para qualquer jogador · feature · ✅ Concluído · atende N34 · marco M17

**F145 — Convite de vice para qualquer jogador.** Serve N34. Entregue: o vice pode ser qualquer jogador humano da sala, de outro partido ou sem partido, e continua filiado ao próprio partido (soma para ele no ranking). Ficam bloqueados quem já é vice (convidado ou aceito) de outra chapa, quem é candidato de alguma chapa e os bots; o servidor recusa com o motivo, e quem é vice de outra chapa também não concorre pelo próprio partido. Na montagem da chapa o Select do vice lista todos os jogadores com o partido de cada um, e os bloqueados aparecem desabilitados com o motivo ("já é vice do ABC", "candidato pelo XYZ"). O convite abre sozinho, em qualquer página, na tela de quem foi indicado (Socket.IO), reaproveitando o diálogo de convite, com aceitar e recusar; quem convida vê o convite pendente na chapa e recebe um aviso com a resposta. No impeachment assume o vice enquanto ele estiver na partida, sem exigir filiação. O painel da eleição ganhou o convite de vice de quem vê (de qualquer partido) e a lista de jogadores para a fundadora; o diálogo foi registrado no canvas. Fora: conferência no app rodando.

### F61 · arquivado em 2026-10-26

*Kanban:* Host remove jogador da sala · feature · ✅ Concluído · atende N28

**F61 — Host remove jogador da sala.** Cartão de cada pessoa no lobby ganhou o menu ⋯ (só para o host, nunca no próprio host nem nos bots) com "Remover da sala", que pede confirmação. A remoção só vale no lobby: com partida em andamento a rota recusa, então participante offline da partida salva segue dono da vaga e da cor e nada é apagado de simulation_players. A pessoa sai pelo mesmo caminho do logout, a vaga e a cor ficam livres na hora, e a página dela recebe o aviso "O host te removeu da sala" e encerra a sessão, como no botão Sair. A conta continua: o mesmo apelido pode entrar de novo se houver vaga.

### F67 · arquivado em 2026-10-26

*Kanban:* Abrir a pasta de configurações · feature · ✅ Concluído

**F67 — Abrir a pasta de configurações.** Nas configurações, o host ganhou o cartão "Pastas do app", com os botões "Abrir pasta de configurações" (config.toml e .env) e "Abrir pasta de logs", e o caminho de cada pasta sempre à vista, com botão Copiar. A rota POST /api/settings/open-folder só atende o host e só requisição vinda do próprio computador (127.0.0.1 ou ::1); abre a pasta no Explorer, Finder ou xdg-open, sem shell. Sem janela para abrir (servidor dedicado, Linux sem xdg-open), a rota responde 409 com o caminho no aviso. Um aviso fixo diz que db e postgres são do banco e não devem ser editados. Os caminhos vêm de GET /api/settings/folders, também só para o host.

### F122 · arquivado em 2026-10-26

*Kanban:* Novas conquistas para as features recentes e antigas · feature · ✅ Concluído · atende N22 · decisões D1

**F122 — Novas conquistas para as features recentes e antigas.** Oito conquistas novas entraram no catálogo (agora são 30): "Dentro da isenção" (fechar um mês com ganho em ações isento, abaixo do limite, e sem imposto), "Day trader" (comprar e vender o mesmo ativo no mesmo dia, fora a cripto), "Em todo setor" (ações de cinco setores ao mesmo tempo, com barra de progresso), "Mexeu o mercado" (uma ordem sua deslocar o preço em 0,5% ou mais, só com o impacto de preço ligado), "Sem muletas" (vencer no modo Especialista, com pelo menos mais um jogador), "Time vencedor" (vencer uma partida em equipes), "Além do horizonte" (jogar um dia depois do último com dado real) e "Nota de craque" (250 pontos na nota geral, com barra de progresso em pontos). Cada uma é uma linha em catalog.py; as medidas novas estão em metrics.py, e o avaliador recebe do motor da partida a apuração mensal do IR. A apuração do IR ganhou o ganho isento só de ações, para separar da cripto. A meta da nota de craque (250) vem do exemplo da documentação (212 é uma partida boa) e não foi calibrada com as partidas jogadas. Ficou de fora "Ordem com paciência" (primeira ordem limite executada): o evento de ordem não guarda se veio de ordem limite. Vale daqui para a frente que cada feature nova que mexe no jogo traga as próprias conquistas no mesmo trabalho (crédito, proventos, bots e estratégias automáticas, por exemplo).

### F134 · arquivado em 2026-10-26

*Kanban:* Acabamentos das telas · feature · ✅ Concluído · atende N15

**F134 — Acabamentos das telas.** Acabamentos das telas aplicados: melhor da sala em verde na aba Geral, cor do caixa e manchete da partida solo nas estatísticas; total de juros pagos no histórico de vida (campo novo na página do histórico); título do lobby com o nome da partida; selo do modo na tela de entrada; Expansões no preset; legenda de dias sem dado no calendário; estados de carregando e erro nas assistências; frase de leitura e células sem dado na correlação; régua de 0 a 100 na dica do IFR e do Estocástico; cartão do desafio da vela em cinza; e outros ajustes locais. Ficaram de fora: o aviso de imprevistos no fim da partida de independência (pede um campo novo no relatório), o clique no interruptor do Especialista com Personalizado ligado e a conferência no app rodando.

### F91 · arquivado em 2026-10-26

*Kanban:* Caixa de entrada e resumo do mês · feature · ✅ Concluído · atende N32 · marco M15 · dependência de F92

**F91 — Caixa de entrada e resumo do mês.** Caixa de entrada pronta: envelope na barra da partida com o número de não lidas, painel lateral com as entradas por data, aviso curto de entrada nova com Abrir e a tabela `inbox_entries` (jogador ou sala, data do jogo, tipo, conteúdo em JSONB, lida), preenchida pela simulação na virada do mês e entregue pelo Socket.IO. O resumo do mês traz patrimônio no início e no fim, rentabilidade ao lado do CDI e do Ibovespa, melhor e pior ação pelo resultado em reais, IR pago, aportes e a posição no ranking da aba Geral com quanto ela andou; a retrospectiva do ano chega na virada do ano com as barras mês a mês, o melhor mês e a maior queda, montada a partir dos resumos guardados. Ficaram de fora: o resumo do último mês quando a partida acaba antes da virada; proventos, que só aparecem quando há e hoje ficam em zero porque o jogo ainda não registra dividendos; e a conferência no app rodando. A leitura das entradas da sala inteira é uma marca só para todos, e o noticiário vai precisar dela por jogador.

### F136 · arquivado em 2026-10-26

*Kanban:* Código e dependências sem uso · feature · ✅ Concluído

**F136 — Código e dependências sem uso.** Entregue: Knip no frontend (`frontend/knip.json`, ignorando `shared/components/ui` e o arquivo gerado da API) e deptry no backend (`[tool.deptry]` no `pyproject.toml`), os dois dentro do `pnpm run check`. Apagado o que era morto: `base-card.tsx`, tipos e constantes sem uso (`types/api.ts`, `types/events.ts`, `metrics.ts`), `displayMonthYear`, `MAX_TEAMS`, `isOpenOn`, `ApiError`; os exports que só o próprio arquivo usa deixaram de ser exportados. Dependências: saíram `psycopg-pool`, `python-dotenv` (o pydantic-settings já o traz) e `@types/js-cookie`; `starlette` passou a ser declarada, pois o backend a importa direto. Os scripts `fta` chamam o binário direto, sem `npx`.

### F137 · arquivado em 2026-10-26

*Kanban:* Acessibilidade das telas · feature · ✅ Concluído

**F137 — Acessibilidade das telas.** Entregue: plugin `jsx-a11y` do oxlint ligado em `frontend/.oxlintrc.json`, como erro, dentro do `pnpm run check`. Dos 42 achados (o card contava 49): corrigidos o `<option>` vazio da lista de segmentos, a célula vazia da matriz de correlação (`aria-hidden`) e os dois seletores `role="combobox"` (setor e "Ver nota de"), que agora apontam com `aria-controls` para a lista que abrem. Três falsos positivos ficaram com desativação pontual e comentário: o botão de `render` do cartão do bot, a área de soltar do CSV e a lista de sugestões do ticker. Regras ajustadas: `label-has-associated-control` reconhece `Input` e `Switch`; `prefer-tag-over-role` desligada (os `role` de `img`, `status`, `radio`, `group`, `combobox` e `heading` são o padrão ARIA correto em `svg`, `div` e botões do shadcn); `no-autofocus` desligada (o único uso é o foco no primeiro campo do diálogo recém-aberto); as regras de clique e rótulo desligadas só em `shared/components/ui`.

### F138 · arquivado em 2026-10-26

*Kanban:* Piloto do modo strict do pyright · feature · ✅ Concluído

**F138 — Piloto do modo strict do pyright.** Concluído: `backend/config`, `backend/routes` e `main.py` estão em `strict` no `pyrightconfig.json`, com 0 achados. Eram 14, todos corrigidos em poucos minutos: dois nomes privados importados fora do módulo (`load_env_settings` e `load_toml_settings` viraram públicos), `dict` sem parâmetros de tipo (`dict[str, Any]`, `dict[str, str | None]`), o mapa `AVAILABLE_PROVIDERS` tipado como `dict[str, type[TunnelProvider]]`, o acesso a `TunnelManager._provider` no `main.py` trocado por `TunnelManager.start_tunnel()` e o stub ausente do `socketio` com um `pyright: ignore` pontual. Custo por achado: baixo, cerca de 20 segundos cada, sem mudar comportamento. O resto do projeto em `strict` dá 3.615 achados: cerca de 2.400 em `tests/` (os maiores: crédito 351, estratégias 318, séries sintéticas 219, governo 213), cerca de 1.100 em `backend/features` e `backend/core` (importação de dados 200, estatísticas 130, realtime 45, análise técnica 70) e 100 em `scripts/`. Próximo passo, se quiser seguir: pastas sem pandas primeiro (`backend/features/government`, `credit`, `inbox`, `achievements`, `strategy`), uma por commit; `tests/` por último.

### F135 · arquivado em 2026-10-26

*Kanban:* Tipos mais rígidos no frontend · feature · ✅ Concluído

**F135 — Tipos mais rígidos no frontend.** Ligadas as três checagens, uma por commit: `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes` e a regra `typescript/no-unnecessary-condition` do oxlint. Antes delas, o schema da API passou a marcar como obrigatório todo campo com valor padrão nas respostas (`json_schema_serialization_defaults_required`), então o tipo gerado do front deixou de oferecer campos opcionais à toa. Nas props dos componentes próprios, o opcional que recebe `undefined` escrito ficou como `prop?: T | undefined`; nas props de bibliotecas, o valor ausente sai por spread condicional.

### F92 · arquivado em 2026-10-31

*Kanban:* Noticiário da partida · feature · ✅ Concluído · atende N31 · decisões D7 · marco M15 · depende de F161 · dependência de F167, F93

**F92 — Noticiário da partida.** O noticiário (`features/newsroom/`) lê o pregão no tick e entrega manchetes ao jornal da partida pelo mesmo `news.publish` da política; sem LLM e sem internet, e a lista de regras vale para o futuro gerado e para a história real. Regra nova é só mais um item da lista em `Newsroom`. Economia: o Copom sobe ou baixa a SELIC (compara o nível anual com o do pregão anterior, com o tamanho e o novo nível), o IPCA do mês que fechou sai no primeiro pregão do mês seguinte (acima ou abaixo do anterior, com o acumulado em 12 meses) e o Ibovespa no recorde (no máximo um a cada 30 dias) ou na maior queda do ano (a partir de 2% no dia). Empresas: movimento forte no dia (acima de 5% contra o fechamento anterior, só ações, FIIs e BDRs) com a causa sorteada de um banco por setor e direção, e máxima de 52 semanas; cada regra põe no máximo 3 ativos por pregão, os de maior movimento, e a notícia sai depois do movimento, sem dar vantagem. A frase varia por sorteio com semente fixa na partida e no dia: o mesmo fato sai com a mesma frase. História: 14 marcos curados à mão em `history.py` (crise de 2008, Joesley Day, Covid-19, entre outros), que só saem em período real; um marco que cai no fim de semana sai no pregão seguinte. Os seis tipos entram no registro de tipos (seções Economia, Empresas e História, com os níveis padrão do board de Configurações do jornal) e a configuração ganha, nos tipos de empresas, o filtro "Só ativos da minha carteira": a manchete que não cita ativo da carteira do jogador fica de fora da janela, do cartão e do histórico dele. Fora: proventos anunciados (esperam a F22) e os marcadores no gráfico de preço (F167); "Copom manteve a SELIC" também fica de fora, porque as séries não guardam as datas das reuniões, só as mudanças.

### F106 · arquivado em 2026-10-31

*Kanban:* Governo & Política: medidas de gasto público · feature · ✅ Concluído · atende N34 · decisões D19, D14 · marco M19 · depende de F128, F107 · dependência de F97

**F106 — Governo & Política: medidas de gasto público.** As quatro medidas (`WELFARE_SPENDING`, `SERVANT_RAISE`, `RETIREE_RAISE`, `PUBLIC_WORKS`) seguem a fila, a votação e o prazo de 90 dias dos impostos; o gasto em vigor mora em `features/government/spending.py` e entra no orçamento (F128) como a fatia de cada categoria (auxílio, servidores, aposentadorias e obras, mais o resto do gasto, que não muda). O passo máximo por medida (0,5 ponto do PIB no auxílio e nas obras, 3 pontos nos reajustes) e o piso de 0% dos reajustes são validados em `government_book.py`. O efeito mora em `features/government/spending_effects.py`, função pura das medidas aprovadas, por isso a retomada de uma partida o reconstrói igual dos eventos (`tests/test_spending_effects.py`): nasce na vigência, sobe em linha reta por 6 meses e cai pela metade a cada 12; cada passo soma 0,25 ponto de IPCA no auxílio, 0,20 nos servidores, 0,25 nas aposentadorias e 0,15 nas obras, e o corte inverte o sinal. A SELIC reage com 1,5 vez a inflação a mais, o CDI sobe junto, e a bolsa cai 2,9% por ponto de SELIC ao longo do trimestre, mais nas ações de beta alto (fator em `price_impact.py`). A leitura do IPCA, da SELIC, do CDI e do Ibovespa passa por uma sobreposição em `repository.economic.get_history`, e a série guardada continua disponível para a linha tracejada do painel da economia. As obras somam 0,6 ponto de crescimento por passo.

No front: terceira opção «Gasto público» no diálogo de nova medida, em blocos; cartão «Gasto público» na aba Contas, abaixo de Impostos; coluna «Na inflação» e soma na fila; promessas com as quatro medidas; no painel da economia, a série guardada tracejada, o Ibovespa no lugar da dívida ÷ PIB no topo e o cartão «Efeitos das medidas de gasto». Reação por grupo: o auxílio avança Justiça social e recua Estabilidade, com o agrado direto de quem recebe.

Ficou de fora: a conferência de propor, votar e ver o efeito no app rodando: no banco de teste só a página da economia sem medidas foi vista, porque propor exige ganhar a eleição e virar presidente (cabe na partida guiada antes da release); a fase «cheio» (as fases são esperando valer, chegando, caindo e sumiu); estados de carregando e erro próprios do cartão de efeitos e da estimativa da medida (valem os da página); a frase «IPCA no pico de X para Y» na soma da fila; as dicas dos termos em coluna ao lado do diálogo (são tooltips). As demais diferenças do desenho estão na nota laranja da linha no canvas.

### F107 · arquivado em 2026-10-31

*Kanban:* Grupos de eleitores, com apoio e rejeição por partido · feature · ✅ Concluído · atende N34 · decisões D19 · marco M17 · dependência de F164

**F107 — Grupos de eleitores, com apoio e rejeição por partido.** Serve N34; a fundação do rework do governo, pelo modelo da D19. (1) **Seis grupos já na 3.1,** com um peso inicial no eleitorado: investidores 8%, empreendedores 12%, trabalhadores com carteira 35%, servidores 10%, aposentados 20% e quem depende de auxílio 15%. Cada grupo tem uma posição em cada valor (item 2) e lê três resultados do governo: a inflação contra a meta (pesa em todos, mais em aposentados, auxílio e carteira), a SELIC (alta agrada aposentados, porque a renda fixa rende mais, e irrita empreendedores e trabalhadores, porque o crédito encarece) e o Ibovespa (pesa para investidores e empreendedores). O emprego entra quando o orçamento trouxer o PIB (F128). Na 3.1, servidores e auxílio reagem à inflação, ao juro e ao ganho de capital taxado; as medidas próprias deles chegam com os gastos (F106). (2) **Seis valores,** que são as bandeiras e os eixos do radar: Mercado livre (imposto baixo na bolsa e na renda fixa), Justiça social (taxar o ganho de capital; auxílio na 3.2), Estabilidade (inflação na meta; conta pública na 3.2), Desenvolvimento (isentar setores; obras na 3.2), Proteção ao poupador (renda fixa e LCI/LCA isentas) e Serviço público (reajuste do servidor, que só ganha medida na 3.2). Cada tipo de medida tem uma tabela fixa dos valores que avança ou recua: cortar o imposto do day trade avança Mercado livre e recua Justiça social. (3) **Identidade do partido:** na fundação, o partido escolhe 3 valores; Mercado livre e Justiça social se excluem. Os valores dão a afinidade inicial com cada grupo, que é a proximidade entre o que o grupo quer e o perfil do partido; depois, o radar se move com as promessas, as medidas aprovadas e, na 3.2, os votos da bancada. A régua de promessa de 1 a 5 (`Party.promise`, `PROMISE_BANDS`, a régua em `measures.py`, `promise-ruler.tsx` e `promise-picker.tsx`) sai e dá lugar ao perfil por valor, com migration. Os partidos do computador nascem com 3 valores fixos cada, distintos entre si. (4) **Apoio e rejeição** de cada partido em cada grupo, de 0 a 100. O apoio sobe e desce com a campanha, as promessas e o governo. A rejeição sobe com promessa descumprida e com mês de governo reprovado pelo grupo, e não cai com o tempo: cai só com reparação, que é promessa cumprida ao grupo (cai muito), mês de governo do partido aprovado pelo grupo (cai pouco) e evento de campanha com o grupo (cai pouco, com um limite por campanha; é o caminho da oposição, que na 3.1 não vota nada). (5) **Voto:** em cada grupo, o saldo de cada partido é afinidade + campanha + promessas − rejeição; a fatia de cada partido no grupo é proporcional ao saldo positivo, e uma parte do grupo fica indecisa; o total é a soma dos grupos pelo peso. Substitui o `points` único de `Party` e o `intention` de `election.py`. (6) **Pesquisa com margem de erro:** a pesquisa mensal mostra a intenção de voto por grupo e no total com a margem ("48%, com margem de 3 pontos para mais ou para menos": o número real está entre 45% e 51%), sorteada pela semente da partida. A margem é uma regra da sala, na aba da expansão no lobby, ligada por padrão; desligada, a pesquisa mostra o número exato. **Protótipo:** os pesos dos grupos, a posição de cada grupo em cada valor, a tabela de medida para valor, quanto cada resultado mexe, o tamanho de cada reparação e a fatia de indecisos se calibram no protótipo de calibração dos grupos. **Gatilho:** depois do protótipo, com os números dele. **Canvas:** fundação do partido com a escolha dos 3 valores; radar do perfil do partido; apoio e rejeição do partido em cada grupo; pesquisa por grupo com a margem de erro; regra da margem na aba da expansão no lobby. **Decidido no canvas em 27 e 28/out:** (a) **Quem vê o quê:** apoio e rejeição exatos só do próprio partido (os filiados); dos adversários, só a pesquisa, com margem. O radar e as bandeiras de todos os partidos são públicos, inclusive os do computador. (b) **A margem cresce nos grupos menores,** porque poucos eleitores dão um número mais incerto: ±3 pontos no total, ±5 nos trabalhadores com carteira, ±7 nos aposentados e ±11 nos investidores (±7 quer dizer que 40% de intenção entre os aposentados está, de fato, entre 33% e 47%). (c) **Partido fundado antes da mudança:** o fundador escolhe as 3 bandeiras; até lá, o perfil é neutro. (d) **Eleitorado:** tabela e cartões são um interruptor no mesmo card, com os cartões por padrão. (e) **Onde mora:** a página Eleição tem as abas Corrida (pública: pesquisa, partidos, mandato e ranking) e Campanha do partido (só filiados: ações, eleitorado, histórico e meu partido); quem não é filiado vê só a Corrida, sem a barra de abas. **Calibrado no protótipo de 28/out** (`scripts/election_prototype.py`; 1.000 eleições por pergunta): (1) os pesos ficam como estão. (2) Posição de cada grupo, de −1 (rejeita) a +1 (quer), na ordem Mercado livre, Justiça social, Estabilidade, Desenvolvimento, Proteção ao poupador e Serviço público: investidores +1, −1, +0,5, +0,3, +0,5, −0,5; empreendedores +0,8, −0,5, +0,3, +1, 0, −0,5; trabalhadores com carteira −0,2, +0,5, +0,6, +0,5, +0,2, 0; servidores −0,6, +0,4, +0,3, 0, +0,2, +1; aposentados 0, +0,2, +1, −0,2, +1, +0,3; auxílio −0,8, +1, +0,5, +0,2, −0,3, +0,3. (3) Afinidade = 20 + 12 × a soma das posições do grupo nos 3 valores do partido, nunca abaixo de 0 (fica entre 0 e cerca de 48; Mercado livre, Estabilidade e Poupador dão 44 com os investidores). (4) Medida para valor, por passo (passo de referência entre parênteses), e o aumento é o inverso do corte: cortar o IR do ganho comum (5 pontos) Mercado +1, Justiça −1, Desenvolvimento +0,3; cortar o day trade (10 pontos) Mercado +1, Justiça −0,5; subir a isenção das vendas (R$ 20 mil) Mercado +0,5, Justiça −0,5, Poupador +0,5; cortar o IR da renda fixa (5 pontos) Mercado +0,5, Justiça −0,5, Poupador +1; taxar LCI e LCA (15%) Justiça +0,5, Desenvolvimento −0,3, Poupador −1; isentar setor Mercado +0,3, Justiça −0,5, Desenvolvimento +1; taxar setor (5 pontos) o inverso da isenção. A reação de um grupo à medida é a soma de posição × efeito, vezes os passos. (5) Indecisos: saldo fixo de 15 em cada grupo, que entra na divisão como um partido a mais (com dois partidos de saldo 30 e 25, 21% do grupo fica indeciso). As reparações estão nas notas da aprovação (mês aprovado), das ações (evento) e das promessas (cumprida). **Implementado em 28/out:** o modelo dos grupos mora num módulo próprio do backend (voto, apoio, afinidade e pesquisa com margem por grupo, com testes); o fundador escolhe 3 bandeiras ao fundar, e o partido antigo ganha o aviso para escolher; a eleição tem as abas Corrida e Campanha do partido, com o eleitorado em cartões ou tabela, os partidos na disputa com radar e a comparação com um grupo, e a pesquisa com a faixa da margem, empate técnico e indecisos; o lobby tem a chave da margem de erro, ligada por padrão. Fica para os cards seguintes: a rejeição segue em 0 até as promessas cobradas e a aprovação pelos grupos trazerem as causas.

### F120 · arquivado em 2026-10-31

*Kanban:* Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira · feature · ✅ Concluído · atende N15

**F120 — Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira.** Serve N15. A Carteira mostra a evolução do patrimônio e a distribuição em dois cards empilhados, pelo design aprovado no canvas. O gráfico traz o patrimônio de hoje e o ganho sobre o aportado no cabeçalho, o período (6M, 1A e Tudo, os períodos maiores que a partida ficam desligados) e dois modos: Ganho, com o aportado em cinza e verde ou vermelho entre as duas linhas, a dívida em faixa abaixo do zero e a meta da corrida; e Por classe, um painel por classe com a própria escala. O tooltip abre do lado que tem espaço e traz o patrimônio por classe, a dívida, o aportado e o ganho; o vazio, o carregando e o erro do histórico têm cada um o seu estado. A distribuição é um anel por classe com o caixa em cinza, a lista das classes, a dívida e o patrimônio no rodapé e os 8 maiores ativos de qualquer classe mais "Outros"; a fatia e a linha da classe se acendem juntas. Os gráficos parecidos (composição das Estatísticas e linha de desempenho) seguem o mesmo visual na migração da F72.

### F127 · arquivado em 2026-10-31

*Kanban:* Estratégias e bots operam cripto em fração · feature · ✅ Concluído · atende N4, N37 · decisões D3

**F127 — Estratégias e bots operam cripto em fração.** O contexto da estratégia ganhou a cotação com a classe fracionária e `affordable(ticker, dinheiro)`, que usa a mesma conta da boleta (módulo `variable_income/quantity.py`). Comprar e segurar, rebalanceamento, momentum, RSI, médias móveis e rompimento compram em fração (até oito casas) na cripto e em inteiro nas demais; `whole_shares` ganhou a variante fracionária. O texto do registro mostra a quantidade sem zeros à direita.

### F128 · arquivado em 2026-10-31

*Kanban:* Orçamento do governo, dívida pública e prêmio de risco · feature · ✅ Concluído · atende N34 · decisões D19, D14 · marco M19 · depende de F107 · dependência de F97, F165

**F128 — Orçamento do governo, dívida pública e prêmio de risco.** O orçamento mora em `features/government/budget.py` (receita pela alíquota com elasticidade, gasto, juros, resultado e dívida, calculados por mês a partir do estado da partida, sem tabela de estado) e o crescimento e o desemprego em `features/economy/growth.py`; `budget_panel.py` monta os DTOs. Receita de cada imposto = base × (alíquota ÷ referência)^(1 − elasticidade), mais a parte fixa; o resultado é o primário (receita − gasto) menos os juros da dívida (dívida × (SELIC + prêmio anterior)); a dívida sobe com o déficit e é diluída pelo PIB nominal (IPCA e crescimento). O prêmio de risco é 2 × (e^(0,02 × pontos acima de 50% do PIB) − 1) pontos, sem teto, e entra só nos títulos novos do Tesouro, gravado no ativo (`risk_premium`); o título comprado mantém a taxa. Crescimento: alvo de 2% − 0,4 × (juro real − 5%) + 5 × (Ibovespa em 12 meses − 5%), andando um quarto do caminho por mês; desemprego pela lei de Okun, entre 4% e 18%. A regra de sala "Conta inicial do governo" (Jogável ou Realista, `initial_account`) define a dívida e o déficit de partida (a realista usa a tabela anual do ano de início, e fora das tabelas vale o ano mais próximo). A aprovação e os eleitores leem o desemprego e o prêmio (`READINGS`). Rotas `GET /api/government/budget` e `/initial-account`, a prévia de medida e a fila com `budget_effect` e `queue_budget`, e o painel da economia com PIB, desemprego e dívida. Migration `c7f2a9d4b1e8` (coluna `risk_premium`) escrita à mão. Front: página Governo em abas Mandato, Contas e Congresso (`?tab=`), aba Contas com "A conta do país", "De onde vem a receita", "Dívida e prêmio de risco" e "Quem lê a conta"; bloco "Efeito no orçamento, estimado" no diálogo de medida; coluna "No orçamento" na fila; painel da economia com seis números e os cartões de crescimento, desemprego e dívida ÷ PIB; renda fixa com a faixa do prêmio, a etiqueta "inclui X de prêmio" e "comprado em <mês>, com prêmio de X"; "Conta inicial do governo" no lobby. Os testes com banco e a conferência da migration em Postgres ficaram para quando houver banco de teste. Diferenças do desenho estão na nota do canvas.

### F129 · arquivado em 2026-10-31

*Kanban:* Aprovação do governo pelos grupos de eleitores · feature · ✅ Concluído · atende N34 · decisões D19 · marco M17 · depende de F107

**F129 — Aprovação do governo pelos grupos de eleitores.** Serve N34; troca os fatores soltos de `approval.py` pelo modelo de grupos (D19, F107). (1) **Satisfação por grupo:** todo último dia útil do mês, os resultados (inflação contra a meta, SELIC e Ibovespa, pelo que cada grupo lê) e as medidas vigentes dão um alvo de 0 a 100 para cada grupo, e a satisfação anda um terço do caminho até ele: com alvo 70 e satisfação 40, fica 50, depois 57 e depois 61. O governo bom sobe até o alvo e para ali; o ruim desce até o alvo e para. Cada fator é simétrico em torno de um ponto neutro (o governo ganha tanto quanto perde), o que corrige a aprovação que só caía. (2) **Aprovação** é a média das satisfações, pesada pelo tamanho de cada grupo. (3) **Medidas:** o efeito de uma medida no alvo dos grupos é cheio quando ela passa a valer e cai pela metade em 6 meses, para quem gostou e para quem odiou; o rastro duradouro fica no radar do partido (F107). Substitui o corte que somava sem decair e o `FADE_DAYS` de 180 dias. (4) **Posse:** cada grupo começa satisfeito na proporção em que votou no presidente no turno que decidiu a eleição; quem ganhou com 54% começa perto de 54%. (5) **Memória:** todo mês, grupo com satisfação acima de 50 conta como mês aprovado (sobe o apoio ao partido do presidente e do vice e repara a rejeição, F107), e abaixo de 50 como mês reprovado (tira apoio e soma rejeição). O protótipo pode abrir uma faixa neutra no meio. (6) **Impeachment automático,** até o Congresso de bancadas (F153) passar a votá-lo: nenhum impeachment nos primeiros 12 meses do mandato; depois, cai quem fechar 6 meses seguidos abaixo de 25% (hoje são 3 meses, sem carência, em `approval.py` e `government_book.py:614`). **Protótipo:** o ponto neutro e a força de cada fator por grupo, o efeito de cada medida, o terço de passo, o piso de 25% e o quanto cada mês aprovado ou reprovado mexe em apoio e rejeição. **Gatilho:** depois da F107. **Canvas:** aprovação por grupo no card de aprovação, com o gráfico ao longo do mandato; alvo e direção de cada grupo (subindo ou caindo); aviso de risco de impeachment com a contagem de meses abaixo do piso e o fim da carência. **Decidido no canvas em 27 e 28/out:** (a) **Quem vê o quê:** a satisfação e o alvo de cada grupo são públicos e exatos para todos, porque decidem o impeachment; a contagem dos meses abaixo do piso também é pública no card, e o alerta vermelho e a pendência só aparecem para o presidente. (b) **Carência:** os meses abaixo do piso no 1º ano não contam; a contagem começa no 13º mês, então o impeachment mais cedo é no 18º. (c) **Faixa neutra de 45 a 55** no item 5: satisfação acima de 55 conta mês aprovado, abaixo de 45 conta mês reprovado, e entre as duas o mês não mexe em apoio nem em rejeição (com satisfação 52, o mês passa em branco). (d) **Tela:** aprovação por grupo no card de hoje, com a linha Geral no topo e o grupo selecionável: clicar num grupo troca o gráfico para a aprovação dele. **Calibrado no protótipo de 28/out** (1.000 mandatos por cenário): alvo = 50 + inflação + SELIC + Ibovespa + medidas, entre 0 e 100. Inflação, por ponto abaixo de meta + 1,5 (até 5 pontos para cada lado): investidores 2, empreendedores 2, carteira 3,5, servidores 3, aposentados 4, auxílio 4. SELIC, por ponto acima de 10% (até 6): investidores +0,5, empreendedores −2, carteira −1,5, servidores 0, aposentados +1,5, auxílio −0,5. Ibovespa, por 10% de alta acima de 5% em 12 meses (até 3 passos): investidores 8, empreendedores 4, carteira 1, aposentados 1, servidores e auxílio 0. Medida: 6 × passos × reação do grupo, meia-vida de 6 meses. O terço de passo, a faixa de 45 a 55, o piso de 25%, os 6 meses e a carência de 12 ficam. Mês aprovado: +1 de apoio ao partido do presidente (cai pela metade em 3 meses, como o de campanha) e −0,25 de rejeição; reprovado: −1 de apoio e +0,5 de rejeição. Resultado: governo bom termina com mediana de 57% (8 em 10 entre 51% e 63%), médio 51%, ruim 28%; impeachment em 0 de 1.000 no bom e no médio e em 337 de 1.000 no ruim, por volta do 31º mês.

### F130 · arquivado em 2026-10-31

*Kanban:* Ações de campanha: a eleição deixa de ser só dinheiro · feature · ✅ Concluído · atende N34 · decisões D19 · marco M17 · depende de F107

**F130 — Ações de campanha: a eleição deixa de ser só dinheiro.** Serve N34; a campanha passa a ter escolhas e sorte, sobre o modelo de grupos (D19, F107). (1) **Verba mensal de base:** a contribuição de cada filiado continua sendo cobrada no 1º dia útil de cada mês da campanha e vira apoio espalhado por todos os grupos pelo peso de cada um, com retorno decrescente (hoje é a raiz quadrada ÷ 64 num eleitorado de 100). A divisão da verba entre a campanha presidencial e a do Congresso chega com a F153. (2) **Ações avulsas:** qualquer filiado dispara uma ação e paga na hora, do caixa da própria carteira, como na doação; o partido não tem caixa. O preço de cada ação é fixo em reais e segue a chave "corrigir pela inflação" da partida: ligada, sobe pelo IPCA a cada aniversário, como o salário e a meta (o fator sai de `life_budget.py` para um lugar compartilhado). (3) **As quatro ações e o dado:** cada ação rola um d20, sorteado pela semente da partida e mostrado na tela. A tabela base: 1, desastre, perde o dobro do ganho normal; 2 a 6, fraco, metade; 7 a 14, normal; 15 a 19, bom, 1,5 vez; 20, viralizou, 3 vezes. **TV** (cara, todos os grupos pelo peso) rola com vantagem: dois dados, vale o maior, então o desastre sai 1 vez em 400. **Evento com um grupo** (preço médio) rola um d20 normal e também repara um pouco da rejeição do partido naquele grupo, até um limite por campanha (F107). **Comício** (barato, um grupo) rola normal com os extremos dobrados: o desastre perde 4 vezes o ganho e o viral rende 6. **Ataque ao rival** (preço médio, um grupo e um partido rival): na faixa normal, tira do rival o ganho normal naquele grupo; no 1, o tiro sai pela culatra: o grupo passa a rejeitar quem atacou, em 2 vezes o ganho normal (+10 de rejeição no exemplo de ganho normal 5, confirmado em 28/out), e o apoio de quem atacou e o do rival não mudam. Nas outras ações o desastre só tira apoio, sem somar rejeição. (4) **Retorno decrescente:** a mesma ação no mesmo grupo rende metade a cada repetição no mês (100%, 50%, 25%) e zera no mês seguinte; espalhar entre grupos rende mais do que insistir num só. (5) **Duração:** todo apoio de campanha, da verba e das ações, cai pela metade em 3 meses; no dia da eleição pesam sobretudo os últimos meses, o que abre espaço para a virada. Afinidade e promessas não caem com isso. (6) **Partidos do computador:** a verba segue a média dos partidos de jogadores vezes 0,5, 1 ou 1,5 pela dificuldade, gasta por regra: eventos nos grupos de maior afinidade e TV quando a verba cobre o preço; atacam só na dificuldade difícil. (7) **Notícia:** desastre e viral saem no jornal com uma manchete ("Candidato se envolve em polêmica no comício com aposentados"), assim como a abertura da campanha e o fechamento das chapas, quando o jornal (F161) existir. **Protótipo:** o preço de cada ação, o ganho normal de cada uma, a curva da verba de base e se o dado mexe o bastante para virar uma eleição sem decidir sozinho. **Gatilho:** depois da F107. Depois, ações por região com o mapa (F164). **Canvas:** painel de ações da campanha (ação, grupo, rival, preço e quantas vezes já foi feita no mês); rolagem do d20 com o resultado e o efeito no grupo; histórico de ações do partido na campanha; manchete de desastre e de viral no jornal. **Decidido no canvas em 27 e 28/out:** (a) **Quem vê o quê:** só o próprio partido vê as suas ações, o dado e o efeito; os outros percebem pela pesquisa e pelo jornal. Todo ataque sai no jornal, e não só o desastre e o viral; o atacado vê o efeito no histórico, sem o dado. (b) **Retorno decrescente por partido:** o 2º evento com aposentados no mês rende 50%, seja de qual filiado for. (c) **Sem limite de ações:** o preço e o retorno decrescente bastam. As ações valem até a véspera do 1º turno; entre os turnos, valem as regras do 2º turno (F151). (d) **Reparação:** o desastre não repara rejeição; as outras faixas reparam. (e) **Ataque:** fraco, normal, bom e viral tiram do rival 0,5, 1, 1,5 e 3 vezes o ganho normal (2,5, 5, 7,5 e 15 no exemplo de ganho normal 5); os valores em pontos seguem exemplos até o protótipo. (f) **Tela:** as ações moram na aba Campanha do partido da página Eleição, em passos que mudam com a ação (TV 1 etapa, comício 2, ataque 3), com o resumo do dado sempre à vista. O diálogo do dado mostra a tabela de faixas antes de pagar, sem a trilha de 1 a 20, e o número tirado aparece dentro do hexágono. **Calibrado no protótipo de 28/out** (verba de referência de R$ 10 mil por mês por partido; 1.000 eleições por pergunta): a verba de base fica na curva de hoje, raiz de R$ ÷ 64 pontos por mês em cada grupo. TV R$ 6.000, ganho normal 0,75 em todos os grupos; evento R$ 2.500, ganho normal 1,5 e repara 1 de rejeição, até 6 por campanha no grupo; comício R$ 800, ganho normal 0,5; ataque R$ 2.500, tira 1,5 do rival (no 1, +3 de rejeição para quem atacou). Os ganhos de 5 dos exemplos deixavam o dinheiro e o dado fortes demais (2× de verba vencia 78% e o dado trocava o vencedor em 23%, em 100 eleições). Com os calibrados: o mais rico com 2× a verba do segundo vence 62% (1,5× 51%, 5× 93%, 10× 99%); trocar só a semente do dado muda o vencedor em 8,5%; o líder da pesquisa 3 meses antes do 1º turno perde em 20,5%.
 **Entregue:** a aba Campanha da página Eleição ganhou o cartão de ações (quatro ações, passos por ação, resumo do dado), o diálogo do d20 com a tabela de faixas, as últimas ações do partido, a verba de base e o histórico com filtros; o dado, o retorno decrescente, o decaimento e os efeitos vivem no registro de eventos do governo. **Fica para o jornal (F161):** a manchete de desastre e de viral, que hoje aparece só no diálogo do dado e no aviso em tempo real.

### F143 · arquivado em 2026-10-31

*Kanban:* Preparação de cada jogador no lobby · feature · ✅ Concluído · atende N39, N34 · decisões D19

**F143 — Preparação de cada jogador no lobby.** Serve N39 e N34. O lobby prepara a partida pelas mãos do host; o que é de cada jogador só se fazia depois do início, com o relógio andando. Agora cada jogador tem o card "Minha preparação", com a expansão Governo & Política ligada numa partida nova. **Meu partido:** a identidade do partido (nome, sigla, cor e as 3 bandeiras) fica salva no perfil, no molde dos presets do host; o histórico do partido (D19) recomeça a cada partida. **O card:** fundar o Meu partido (com candidato e vice), entrar no partido que outro jogador preparou ou nada; o convidado para vice aceita ou recusa no próprio card. **Aplicação:** a preparação vive em memória na sala e vira um evento do livro do governo ao iniciar, então sobrevive a salvar e retomar antes da campanha; na abertura da campanha o partido nasce com contribuição zero, os filiados entram, a chapa é montada e o vice aceito vale. **Conflitos:** sigla, nome ou cor repetidos entre preparados, ou com os partidos do computador, avisam no lobby e bloqueiam o Iniciar do host. **Padrões:** quem não está na sala quando a partida começa não tem a preparação aplicada; o vice vale só para a partida; bots não têm preparação; com partida salva selecionada ou a expansão desligada o card fica travado.

### F151 · arquivado em 2026-10-31

*Kanban:* Segundo turno com disputa · feature · ✅ Concluído · atende N34 · decisões D19 · marco M17 · depende de F130, F152

**F151 — Segundo turno com disputa.** Serve N34. No playtest, o 2º turno repetiu o 1º sem chance de virada: entre os turnos não havia cobrança, os votos dos eliminados iam inteiros para o finalista de promessa mais próxima (`runoff` em `election.py`) e o único movimento era a doação de quem foi eliminado. (1) **Transferência grupo a grupo:** no dia seguinte ao 1º turno, os votos de cada eliminado se dividem, em cada grupo, pela afinidade do grupo com cada finalista (D19, F107). Uma parte fica indecisa, e essa parte cresce quando o grupo gosta pouco dos dois: aposentados com afinidade baixa com ambos deixam metade dos votos do eliminado indecisa, e investidores próximos de um finalista transferem 90%. (2) **Declaração de apoio:** o líder do partido eliminado declara apoio a um finalista ou neutralidade. Os grupos que confiam no eliminado (afinidade alta e rejeição baixa) seguem a indicação com parte dos votos indecisos. O partido do computador eliminado declara por regra, para o finalista de valores mais próximos. A declaração sai no jornal. A doação a um finalista continua. (3) **Campanha de 2º turno:** as ações avulsas (F130) valem entre os turnos, cada finalista pode fazer uma contribuição única de 2º turno, paga na hora e convertida como a verba mensal, e pode acrescentar 1 promessa (até 4 no total, F152); retirar promessa não é permitido. (4) **No dia do 2º turno,** os indecisos que sobraram se abstêm, e o vencedor sai dos votos válidos. A duração de 21 dias fica; volta à mesa se, jogando, ficar curta para a virada. O debate sorteado fica de fora. **Protótipo:** a curva da fração indecisa pela afinidade, quanto do apoio declarado os grupos seguem e se uma virada acontece numa fração razoável das eleições. **Gatilho:** depois da F130 e da F152. **Canvas:** resultado do 1º turno com a transferência por grupo (quanto foi para cada finalista e quanto ficou indeciso); painel do 2º turno com os indecisos por grupo, as ações, a contribuição única e a promessa extra; declaração de apoio do eliminado; resultado do 2º turno com a abstenção. **Decidido no canvas em 27 e 28/out:** (a) **Quem vê o quê:** a transferência grupo a grupo é pública como pesquisa, com a margem de cada grupo; o número exato só sai no resultado do 2º turno. (b) **Declaração:** o líder do eliminado declara uma vez, até a véspera, sem volta; sem declarar, conta como neutro. Quanto mais tarde, menos indecisos sobram para seguir. (c) **Contribuição de 2º turno:** uma por filiado do finalista; a soma vira apoio pela raiz, como a verba mensal (dobrar o dinheiro não dobra o apoio). (d) **Ações no 2º turno:** o ganho de uma ação sai primeiro dos indecisos do grupo; quando eles acabam, tira do rival. No ataque, o que o rival perde vira indeciso no grupo: os dois disputam, e quem sobrar no dia do 2º turno não vota. A repetição de ação no grupo zera no dia seguinte ao 1º turno, e tudo volta a render 100%. (e) **Pesquisa semanal entre os turnos,** porque a mensal só sairia depois da votação. (f) **Tela:** o 2º turno é um estado da página Eleição, nas abas Corrida e Campanha do partido, e não tem painel próprio (no lugar do painel do 2º turno da linha Canvas). **Calibrado no protótipo de 28/out:** a fração que fica indecisa na transferência é 1 ÷ (1 + (afinidade somada com os dois finalistas, descontada a rejeição, ÷ 20)²): somada 20 deixa metade indecisa, 60 deixa 1 em 10. A declaração leva até 50% dos indecisos vindos do eliminado, vezes a confiança no eliminado ((afinidade − rejeição) ÷ 50, entre 0 e 1). A contribuição única de 2º turno entra pela raiz da verba de base. Em 994 eleições com 2º turno, o 1º colocado do 1º turno perdeu o 2º em 15%, com abstenção média de 13%. Afrouxar a transferência (metade indecisa só com afinidade somada 30) não subiu a virada e subiu o peso do dado para 12%. **Entregue:** entre os turnos, os votos de cada partido eliminado se dividem em cada grupo de eleitores entre os dois finalistas e os indecisos (a fração indecisa é 1 dividido por 1 mais o quadrado de, afinidade somada com os dois finalistas descontada a rejeição, dividida por 20), na pesquisa semanal do 2º turno, pública e com a margem de cada grupo, a partir do dia seguinte ao 1º turno. O líder do eliminado declara apoio a um finalista ou neutralidade, uma vez e sem volta, e os grupos seguem com até metade dos indecisos vindos do eliminado, vezes a confiança no partido; o eliminado do computador declara pelos valores mais próximos. Os finalistas fazem as ações avulsas com o dado, em que o ganho sai primeiro dos indecisos do grupo e depois do rival, cada filiado de finalista faz uma contribuição única convertida pela raiz como a verba mensal, e a chapa acrescenta promessas até 4, sem retirar; o finalista do computador contribui com metade da verba e faz um evento por semana. No dia do 2º turno os indecisos que sobraram se abstêm e o vencedor sai dos votos dados. A tela é um estado da página Eleição: a aba Corrida traz a pesquisa e as tabelas de para onde foram os votos, a aba Campanha traz as ações com os indecisos, e o resultado do 2º turno mostra a votação por grupo e quem não votou. Os eventos novos entram no estado político por migração, e a doação a um finalista passa a somar na disputa. **Ficou de fora:** a queda do ganho do 2º turno com o tempo, o gráfico de linha do histórico da pesquisa semanal, a curva "quanto fica indeciso", o cartão "como o partido virou" e as manchetes do jornal (esperam o jornal); a transferência e os indecisos da campanha aparecem exatos, sem a margem da pesquisa. **Decidido na implementação:** o líder do partido é o fundador; a contribuição única reaproveita o tipo de caixa da doação de campanha.

### F152 · arquivado em 2026-10-31

*Kanban:* Promessas de campanha cobradas no mandato · feature · ✅ Concluído · atende N34 · decisões D19 · marco M17 · depende de F107

**F152 — Promessas de campanha cobradas no mandato.** Serve N34; substitui a régua de promessa por faixas, pelo modelo de grupos (D19, F107). (1) **O que se promete:** a chapa promete até 3 medidas da lista das que o governo pode propor: as de imposto, que já existem, e as de gasto quando a F106 chegar, na 3.2. Medida com valor leva um alvo ("day trade a 10%", hoje em 20%); medida de setor é sim ou não ("isentar o setor elétrico"). A promessa aparece no jornal ("Fulano prometeu isentar o setor elétrico"), na pesquisa, no resultado e na tela do governo, e move o radar do partido nos valores da medida. (2) **Na campanha:** a promessa rende apoio nos grupos que querem a medida e tira dos que não querem, na medida da posição de cada grupo no valor; quanto maior o passo prometido, mais rende e mais pesa se falhar. Num grupo, ela rende multiplicada por (1 − rejeição ÷ 100): com 40 de rejeição entre os aposentados, a promessa feita a eles rende 60%. Quem traiu promete de novo e rende menos onde traiu. (3) **No mandato:** no fim do mandato vale o que estiver em vigor. Chegou ao alvo, cumprida; parte do caminho, cumprida na proporção (de 20% para 15% numa promessa de 10% é metade); nada, descumprida. Cumprida sobe a lealdade e repara a rejeição dos grupos que queriam a medida (F107); descumprida soma rejeição neles, na mesma proporção. A tela do governo mostra cada promessa como cumprida, em andamento (com a fração do caminho) ou descumprida. (4) **Impeachment:** o vice que assume herda as promessas da chapa e é cobrado no fim do mandato; sem vice, o mandato acaba no impeachment e o que não foi cumprido vira rejeição. A cobrança fica sempre com o partido da chapa. (5) Os partidos do computador prometem por regra, com medidas dos próprios valores. **Protótipo:** quanto a promessa rende por grupo e por tamanho do passo, e quanto vale a lealdade e a rejeição de uma promessa cumprida ou quebrada. **Gatilho:** depois da F107. **Canvas:** escolha das promessas na chapa (medida, alvo e o rendimento esperado em cada grupo, já descontado pela rejeição); promessas da chapa na pesquisa e no resultado; promessas na tela do governo com o estado de cada uma; balanço do fim do mandato, com o que cada promessa deixou de lealdade e de rejeição em cada grupo. **Decidido no canvas em 27/out:** (a) **Desde o anúncio:** a promessa rende desde o anúncio. Depois dele, trocar, retirar ou baixar o alvo soma rejeição em quem queria; acrescentar até 3 e subir o alvo não custam. (b) **Cumprida soma afinidade,** a parte do apoio que não cai: é o que o item 3 chama de lealdade, sem nenhum número novo por grupo. (c) **Direção contrária pesa mais que não fazer nada:** de 20% para 25% numa promessa de 10% o governo andou meio caminho para trás (−50% do caminho), e a rejeição sai 1,5 vez a cheia. (d) **Reeleição:** com as chapas fechadas, metade do efeito do que estiver em vigor já pesa no voto; o balanço de 31 dez fecha a outra metade. (e) **Quem perdeu:** as promessas de quem perdeu ficam no histórico do partido, sem efeito. (f) **Tela:** a escolha é um diálogo, uma promessa por vez. **Calibrado no protótipo de 28/out:** a promessa rende 4 × passos × reação do grupo à medida, vezes (1 − rejeição ÷ 100) onde rende. Cumprida soma 3 de afinidade e repara 8 de rejeição por passo e unidade de reação, nos grupos que queriam, na proporção do caminho; descumprida soma 8 de rejeição, e na direção contrária 1,5 vez. Em 1.000 eleições seguintes com 2 promessas de 1 passo e verba igual: quem não prometeu vence 35%; cumpriu, 41% (49% com o balanço inteiro); metade do caminho, 33%; nada, 22% (10%); o contrário, 17% (4,5%). Trair custa mais do que cumprir rende, de propósito.
 **Entregue:** a chapa promete até 3 medidas num diálogo da aba Campanha do partido (uma por vez: medida, alvo com controle deslizante e o "hoje", valores que a medida move, tabela por grupo com o rendimento já descontado pela rejeição e o que soma se descumprir, total pelo peso dos grupos e o custo de voltar atrás antes do clique); a lista vale desde o anúncio e trava quando as chapas fecham. A promessa aparece como selo, com o dia do anúncio, nos perfis dos partidos (inclusive o histórico das eleições que passaram) e em "Seu partido"; os partidos do computador prometem por regra, até 2 medidas dos próprios valores, e não são cobrados. No Governo, o cartão das promessas mostra cada uma como cumprida, em andamento (com a fração do caminho), sem andar ou na direção contrária, a última votação que conta, o "se o mandato acabasse hoje" (só para os filiados) e o aviso de que metade já pesa na reeleição; os impostos ganham a etiqueta "prometido" e a fila, "cumpre a promessa". O balanço sai em 31 de dezembro (ou no impeachment sem vice; o vice herda as promessas) e fica num diálogo com o estado de cada promessa para a sala e a matriz de afinidade e rejeição por grupo só para os filiados; o aviso em tempo real abre o balanço. Tudo vive no registro de eventos do governo e se reconstrói no replay. **Escolhas:** o radar do partido não se move no anúncio (o diálogo mostra quais valores a medida avança ou recua, e o radar se move quando a medida é aprovada, como já era); a metade que pesa na reeleição é creditada uma vez, no primeiro dia depois de as chapas fecharem, e o balanço de 31 dez soma só o que falta; a promessa de setor é só a isenção; voltar atrás custa metade da rejeição de descumprir. **Fica para o jornal (F161):** as manchetes do anúncio, da volta atrás e da cobrança, que hoje aparecem só como aviso em tempo real. Promessas de gasto chegam com a F106.

### F153 · arquivado em 2026-10-31

*Kanban:* Congresso eleito, com bancadas orientadas pelo líder · feature · ✅ Concluído · atende N34 · decisões D19 · marco M19 · depende de F107, F130

**F153 — Congresso eleito, com bancadas orientadas pelo líder.** Serve N34. Hoje o Congresso é um sorteio: cada medida passa se um número de 0 a 100 sai abaixo da aprovação (`congress.py`). (1) **Casa de 101 cadeiras,** uma só (sem Senado), eleita junto com o presidente e mostrada como um hemiciclo de bolinhas na cor de cada partido. A medida passa com 51 votos Sim. A casa é eleita no 1º turno, e antes da 1ª eleição as 101 cadeiras são dos três partidos do computador, pelo eleitorado inicial; o partido de jogador entra na 1ª eleição que disputar. (2) **Eleição própria:** os votos de Congresso saem do mesmo modelo de grupos (D19, F107), pesando mais a afinidade de longo prazo e o histórico do partido do que a campanha, e com a verba de Congresso que o partido separou da presidencial: a contribuição mensal ganha a divisão entre as duas campanhas (F130), e cada filiado divide a própria contribuição entre a presidência e o Congresso. Os votos viram cadeiras de forma proporcional, com barreira de 5% (quem fica abaixo não elege ninguém), pelo método D'Hondt: os votos de cada partido são divididos por 1, 2, 3 e assim por diante, e as maiores divisões levam as cadeiras; quem tem 30% dos votos leva cerca de 31 cadeiras. Um partido com histórico bom e pouco dinheiro elege bancada sem ganhar a presidência, e o presidente pode governar com a oposição em maioria. (3) **Partidos do computador permanentes:** os três existem sempre na casa, com perfil próprio por grupo e valores fixos, mesmo quando não lançam candidato; um deles faz o papel do "centrão", que vende apoio (F154): a UPR. (4) **Líder orienta a bancada:** o líder é o fundador (se ele sair, o filiado mais antigo). Em cada medida, ele define o voto da bancada (Sim ou Não); uma orientação padrão vale quando ele não escolhe: uma regra Sim ou Não por valor, que só o líder muda e que nasce com Sim nos três valores do partido; a medida que puxa para mais de um valor segue o que ela puxa mais. A votação sem orientação vira pendência no jornal (F161). Quem perdeu a presidência continua jogando. Os partidos do computador orientam pelos próprios valores. A orientação de cada bancada é pública assim que o líder escolhe, e a fila mostra o placar previsto em faixa, do Sim com todos os que podem desobedecer votando contra até o Sim sem nenhum. O voto da bancada move o perfil do partido, como aprovar uma medida. (5) **Desobediência:** quanto mais a medida contraria os grupos que votaram no partido, mais deputados votam contra a orientação, até um terço da bancada, num sorteio pela semente da partida. (6) **Impeachment votado:** a régua da F129 (sem impeachment nos primeiros 12 meses, depois 6 meses seguidos abaixo de 25%) deixa de derrubar sozinha e passa a abrir o pedido; o pedido abre no 6º mês seguido abaixo de 25% e a casa vota no dia de votação do mês seguinte; o presidente cai com 68 das 101 cadeiras, dois terços como no Brasil, e sem os 68 a contagem recomeça do zero. Depois do impeachment, assume o vice; sem vice, governa o partido do computador com mais cadeiras, propondo medidas pelos grupos dele. No impeachment, a orientação padrão é pelos eleitores: Sim quando a satisfação deles com o governo está abaixo de 25%, e os partidos do computador seguem a mesma regra. Filiados como deputados individuais, com salário e eleição por estado, ficam para depois, se a bancada se mostrar divertida. **Protótipo:** quanto a eleição de Congresso pesa histórico contra campanha, e a curva da desobediência. **Gatilho:** depois da F107 e da F130. **Canvas:** a aba Congresso do Governo, pública para toda a sala, com o hemiciclo da casa, com a maioria e os dois terços marcados; resultado da eleição do Congresso (cadeiras de cada partido, ganhas e perdidas); votação de uma medida, com a orientação de cada bancada, o placar e quem desobedeceu; orientação padrão por valor na tela do partido; divisão da verba entre presidência e Congresso no diálogo de contribuição; votação do impeachment, com o pedido aberto no topo do Governo e da casa; no resultado do 1º turno, a casa eleita ao lado da presidência, com o aviso de quem ficou abaixo de 5% e a explicação de como os votos viram cadeiras, e a pesquisa com a aba Congresso e as cadeiras previstas; na votação, o líder vê antes de escolher o placar, a desobediência na própria bancada e o movimento do perfil, e depois o placar real com quem votou contra e a causa. **Calibrado no protótipo de 29/out** (1.000 partidas sintéticas com os 3 partidos do computador e 1 ou 2 de jogador, verba de Congresso entre 20% e 50% da total): (1) força de cada partido na casa, por grupo = afinidade (a mesma da presidência) + 1,5 × (lealdade − rejeição) + 0,5 × apoio da campanha de Congresso; votos = força ÷ (indecisos + soma das forças), pesados pelos grupos; D'Hondt com barreira de 5%. O histórico vale mais que a verba: com +3 de lealdade em todos os grupos, o partido elege 26 cadeiras, contra 25 com o dobro da verba e 24 na referência; com pouca verba e histórico bom, ainda 26; com +5 de rejeição, 19. O presidente tem em mediana 26% dos votos e 27 cadeiras (8 em 10 entre 22 e 32), com correlação 0,68 entre votos e cadeiras; nenhum partido elegeu maioria sozinho, e a oposição tem maioria em 24% de 1.000 mandatos. (2) Desobediência: contrariedade = quanto os eleitores da bancada querem o voto oposto ao orientado (a reação deles à medida, pesada pela composição da bancada, na escala das posições); fração que vota contra = 1/3 × contrariedade, cheia em 1, sorteada deputado a deputado. Média de 2,5 deputados contra a orientação por votação. (3) A orientação padrão fica como está. Sem acordo, passam 71% de 5.995 propostas do presidente: 29% de 1.457 com a oposição em maioria e 84% de 4.538 sem ela. (4) Impeachment votado: a contrariedade no pedido é (25 − satisfação dos eleitores) ÷ 25. O governo ruim cai em 78% de 1.000 mandatos, contra 91% pela régua automática; bom, médio e fraco nunca caem.

### F154 · arquivado em 2026-10-31

*Kanban:* Negociar apoio com as bancadas, por emendas · feature · ✅ Concluído · atende N34 · decisões D19 · marco M19 · depende de F153, F128

**F154 — Negociar apoio com as bancadas, por emendas.** Serve N34. Com o Congresso de bancadas (F153), o governo monta maioria pagando emendas: verba do orçamento (F128) destinada à base do partido aliado, que entra como gasto e agrada os grupos desse partido (D19). (1) **Apoio por prazo:** o aliado entra na base por 6 meses, renováveis, e o líder dele orienta Sim em tudo o que o governo propuser, em troca de uma emenda mensal. A desobediência da bancada (F153) continua valendo. Um mês antes do fim, o governo recebe o aviso para propor de novo, pelo preço do dia; sem proposta, o acordo acaba sem quebra. O acordo vale até a posse do novo Congresso e acaba ali sem quebra. O aliado de jogador ganha só o apoio dos grupos dele: nenhum dinheiro entra no caixa de ninguém. (2) **Preço por cadeira:** cada cadeira custa uma fração fixa do PIB, cobrada por mês (valor inicial: 0,01% do PIB por ano por cadeira, a confirmar no protótipo), e o centrão cobra 1,5 vez isso. O partido de jogador recebe a proposta num aviso de aceitar ou recusar, no mesmo molde do convite de vice (F145), com o valor e o prazo; ele tem 15 dias para responder, e sem resposta conta como recusa. O partido do computador responde pelo perfil: o centrão aceita quase sempre, e os outros só quando os valores do governo combinam com os deles, no pregão seguinte. A tela mostra a previsão em palavras (deve aceitar, deve recusar, quase sempre aceita), sem número. Depois de uma recusa, nova proposta ao mesmo partido só em 30 dias. Com um pedido de impeachment aberto, nenhum acordo novo até o resultado; os que existem seguem valendo. (3) **Quebra:** se o governo para de pagar, os grupos do aliado, que recebiam a emenda, somam rejeição ao partido do presidente; se o aliado orienta Não durante o prazo, os grupos do governo somam rejeição ao aliado. Nos dois casos o acordo acaba e sai no jornal (F161). Romper é um botão nos dois lados (o governo rompe, o aliado de jogador sai da base), com o custo e a base que sobra à vista antes do clique: é a mesma quebra de parar de pagar ou de orientar Não. Valores iniciais: +8 de rejeição na quebra e cerca de +1 de apoio por mês de acordo, a confirmar no protótipo. Acordos, valores e prazos são públicos, como o orçamento; quem não governa os vê sem os botões. Como a rejeição só cai com reparação (F107), trair a base cobra na eleição seguinte. **Protótipo:** o preço por cadeira e o tamanho da rejeição na quebra. **Gatilho:** depois da F153 e da F128. **Canvas:** proposta de acordo do governo clicando no hemiciclo, que é o seletor (cheia: na base; anel: entra com a proposta; clara: fora), com o partido escolhido, o preço e os efeitos, a descrição e a dica de emenda, o custo de romper antes de propor e o botão com o valor; aviso de proposta para o partido de jogador; a base do governo no hemiciclo, num cartão Base no Congresso entre o cabeçalho e o orçamento (folga sobre a maioria, total das emendas, desobediência e a tabela dos acordos com prazo e como orientou), e as emendas no orçamento como linha própria na conta do mês; aviso e manchete de quebra de acordo. **Calibrado no protótipo de 29/out** (1.000 partidas): (1) preço por cadeira 0,005% do PIB por ano, metade do valor inicial, e o centrão cobra 1,5 vez isso. A base mais barata até 51 cadeiras mais 5 de folga sai em mediana por 0,20% do PIB por ano (8 em 10 entre 0,13% e 0,29%), contra 0,33% de uma medida de gasto média; em 9% de 1.000 partidas os partidos que aceitam não somam 51. Com a base, passam 99% das propostas, inclusive com a oposição em maioria. (2) No protótipo, o partido do computador aceita com ao menos 2 bandeiras em comum com o governo, o centrão sempre, e o de jogador metade das vezes. (3) A emenda entra como gasto e não soma inflação. (4) Apoio do acordo +1 por mês nos grupos do aliado, que cai pela metade em 3 meses como o de campanha e se estabiliza perto de +4,8. (5) Quebra: +8 de rejeição, cheia no grupo em que o aliado é mais forte e proporcional nos outros. Na eleição seguinte, com verbas iguais, o partido do presidente cai de 24,5% para 23,1% dos votos no 1º turno, e a chance de vencer de 67% para 32% de 1.000.

**Entregue:** o card Base no Congresso na aba Contas do Governo (hemiciclo da base, folga sobre a maioria, total das emendas, desobediência e a tabela dos acordos com prazo e como a bancada orientou, pública, com os botões só para quem governa), o diálogo Negociar apoio com o hemiciclo como seletor (cheia, anel, clara), a previsão em palavras, o custo na dívida e na base antes de propor, o convite ao líder do partido de jogador (abre sozinho em qualquer página e fica como pendência e aviso fixo), a resposta do computador no pregão seguinte, o prazo de 15 dias e a espera de 30 dias depois da recusa, o preço de 0,005% do PIB por ano por cadeira (centrão 1,5 vez), o acordo de 6 meses que acaba sem quebra na posse do novo Congresso, o aviso de renovação um mês antes, a quebra nos dois lados com o custo à vista (+8 de rejeição pelos grupos mais fortes, cheia no mais forte), o selo de acordo e a confirmação de orientar Não na votação, a linha de emendas na conta do mês, as manchetes e os avisos de resposta, quebra e fim. Os acordos são eventos do estado político, refeitos na retomada, e a emenda do mês é gasto avaliado pelo dia anterior, para o fechamento do orçamento ser o mesmo ao vivo e na retomada. **Conferência:** pytest (36 testes novos), vitest e o check completo; a migration subiu no banco de teste e o app iniciou, mas a tela da base não foi conferida rodando porque ela só aparece depois da primeira posse.

### F160 · arquivado em 2026-10-31

*Kanban:* Imprevistos no fim da partida de independência · feature · ✅ Concluído · atende N15

**F160 — Imprevistos no fim da partida de independência.** Serve N15. O fim da partida no modo viver de renda ficou sem a frase "passou por N imprevistos", porque o relatório da partida não tinha esse número. Implementado: o backend conta os imprevistos de cada jogador a partir dos eventos de caixa da partida (a demissão tem categoria própria no histórico e fica fora da conta) e manda o total no campo `unexpected_count` de cada jogador do relatório de visão geral; `pnpm openapi` regenerou o tipo. O topo do fim de partida (`match-result/match-hero.tsx`) mostra "Você passou por N imprevistos" na partida de viver de renda com imprevistos ligados (quem só assiste vê a frase do líder). Teste: a contagem por jogador sobre eventos gravados no banco e o campo no ranking.

### F161 · arquivado em 2026-10-31

*Kanban:* Jornal da partida: notificações configuráveis por tipo · feature · ✅ Concluído · atende N31, N32 · marco M15

**F161 — Jornal da partida: notificações configuráveis por tipo.** Serve N31 e N32; retrabalho da F91. A caixa de entrada saiu como um e-mail (envelope com contagem de não lidas, painel lateral, marca de lida), e não é o que o jogo pede: com o tempo correndo, notícia é passageira. O modelo vem do OpenTTD (notícia grande em janela, pequena na faixa, e cada tipo configurável) e do Victoria 3 (cada tipo escolhe se aparece, fica só no registro ou some, e só o que é global pausa). Decidido no canvas em 27/out: (1) **Régua:** no jornal entra só o que pareceria notícia num jornal de verdade: economia, empresas, política (calendário da eleição, resultado, posse, medidas propostas, votadas e em vigor, vida dos partidos) e marcos históricos. O que é do jogador continua toast, com liga/desliga por tipo: ordens (manuais, a limite e do automático), jogador entrou ou saiu, parcelas pagas, empréstimo quitado, nota de risco, imprevisto, resposta do vice e resumo do mês. A resposta a um clique é toast e não se configura. O que pede ação é pendência, feature própria (F166). (2) **Como aparece**, escolha de cada jogador: o cartão do jornal num canto (embaixo à esquerda, o padrão; embaixo à direita; em cima à esquerda) ou a faixa de manchetes abaixo da topbar; os toasts ficam embaixo, no lado oposto (com a faixa, embaixo à direita). Em cima à direita fica de fora, porque divide a borda com a aba do tutorial. Várias manchetes no mesmo pregão: sobe a mais importante, com "+N neste pregão", sem fila. (3) **Configuração por tipo**, num registro único de tipos (categoria, texto, padrão): Janela, Jornal, Só no histórico ou Desligado. Janela abre a manchete no centro sem pausar e sem escurecer o fundo, fecha sozinha em 8 s, no máximo uma por pregão; no padrão fica para poucos tipos, e serve a quem quer ênfase numa categoria. Resultado de turno e impeachment ficam presos na janela com pausa. Em empresas, o filtro "só ativos da minha carteira". (4) **Histórico** da partida inteira, salvo com ela, por data, sem "lida" e sem contagem, com busca, filtro por seção e "só minha carteira". Ele mora numa página própria, com o item Jornal no menu lateral, sob Mercado; "Abrir o jornal" no cartão e o selo recolhido levam para ela. (5) **A caixa de entrada sai:** resumo do mês e retrospectiva viram toast com Abrir, e os passados ficam numa aba Resumos em Estatísticas. (6) **Multiplayer:** a configuração é de cada jogador e nunca pausa a sala. (7) **Ficam como estão,** fora do jornal e da configuração: aviso de que o host removeu o jogador, erro no servidor, conquista e aviso do backtest. O histórico em página própria foi escolhido no canvas em 28/out. **Entregue:** a caixa de entrada saiu e o jornal entrou. Um registro único de tipos de notificação (7 tipos de manchete em 4 seções e 9 tipos de aviso pessoal) manda no que o jogador vê: cada tipo de manchete tem nível Janela, Jornal, Só no histórico ou Desligado, e cada aviso pessoal liga e desliga. A manchete nova chega pronta pelo tempo real: a de nível Janela abre no centro da tela sem pausar e fecha em 8 s (a segunda espera a primeira; a terceira vira só cartão), a de nível Jornal vira cartão de papel num canto (ou uma faixa de 40 px sob a topbar) e recolhe num selo depois de cerca de 6 s; numa rajada no mesmo pregão aparece só a mais importante, com "+N neste pregão". Os avisos ficam embaixo, no lado oposto ao do cartão. A página Jornal, sob Mercado, guarda o histórico da partida inteira, com busca, abas por seção, "Só minha carteira" e os estados vazio, carregando, erro e filtro sem resultado. Em Configurações há o cartão Jornal (nível por tipo, com Restaurar padrão), a escolha da posição em quatro cartões de esboço e o cartão Avisos (um interruptor por tipo). O resumo do mês e a retrospectiva do ano viraram a aba Resumos de Estatísticas, com o toast "Resumo de <mês>" e o botão Abrir. Os toasts políticos que viraram manchete saíram do aviso. **Ficou de fora:** a opção "Só ativos da minha carteira" por tipo na configuração do jornal (o contrato de configurações não tem o campo; a página do jornal já filtra pela carteira); a aba Resumos não tem board no canvas. **Decidido na implementação:** a janela aceita uma fila de duas; a faixa mostra a última manchete elegível, apagada, depois do tempo do cartão; o aviso do ataque entre outros partidos saiu e o ataque ao partido do jogador segue como aviso.

### F162 · arquivado em 2026-10-31

*Kanban:* Sinal de partida pausada e destaque da velocidade máxima · feature · ✅ Concluído · atende N15 · marco M16

**F162 — Sinal de partida pausada e destaque da velocidade máxima.** Serve N15. A eleição e o impeachment pausam a partida para todos, e a única pista era o botão da barra da partida trocar de pausa para play. Implementado: (1) **Motivo da pausa:** o estado da simulação guarda o motivo (pausado pelo host, campanha aberta, resultado do 1º turno, resultado do 2º turno, impeachment), preenchido por quem pausa; o calendário do governo devolve o motivo em vez de um sim/não, e ele chega ao front junto da velocidade (rota de estado e evento de velocidade). (2) **Partida pausada:** a área da data ganha um selo âmbar "Pausado" com o motivo ("Pausado: resultado do 1º turno") e pulsação lenta (desligada para quem pede menos movimento), e o título da aba do navegador ganha "⏸" na frente. (3) **Velocidade máxima:** o segmento do x100 ganha ícone de raio e o tom azul das informações, e a data ganha fundo azul suave enquanto ele está ligado. Os tons saem dos tokens do tema, com variante nova no selo (tamanho de estado e pulsação) e no controle segmentado (nível máximo). Os estados entraram no canvas.

### F163 · arquivado em 2026-10-31

*Kanban:* Painel da economia: SELIC e IPCA ao longo da partida · feature · ✅ Concluído · atende N34 · marco M17

**F163 — Painel da economia: SELIC e IPCA ao longo da partida.** Serve N34. A SELIC e o IPCA já existiam no jogo, mas só apareciam como o número do dia: ninguém via a SELIC subindo em resposta à inflação, nem o efeito de uma medida meses depois. Implementado: (1) **Página nova Economia,** no menu em Mercado, para todas as partidas (não depende da expansão), com a introdução, três números no topo e o gráfico. (2) **Números de hoje,** cada um com descrição em reais e dica de como ler: a SELIC é o juro básico (10% ao ano quer dizer que R$ 100 parados nela viram R$ 110 em um ano), com a última mudança do Copom; o IPCA em 12 meses é a inflação oficial (5% quer dizer que o que custava R$ 100 custa R$ 105), com a meta do ano; o juro real é a SELIC menos o IPCA (10% − 4% = 6%) e fica vermelho quando é negativo. (3) **Gráfico "Juros e inflação":** SELIC e IPCA no mesmo gráfico de linha, desde o início da partida ou nos últimos 12 meses, com a meta de inflação do ano tracejada, a faixa de tolerância em volta dela (±1,5 ponto desde 2017, ±2 de 2005 a 2016 e ±2,5 em 2003 e 2004) e um ponto em cada dia em que a SELIC mudou de nível; a dica mostra os quatro números do dia e a mudança do Copom, e há uma tabela com os mesmos dados. (4) **Só o que o jogador já conhece:** a rota `/api/economy` devolve um ponto por mês e um por mudança da SELIC, até a data da partida, e a página se renova a cada 15 segundos. As mudanças do Copom saem dos degraus da SELIC (a partir de 0,1 ponto), igual na história real e no futuro gerado, já que a SELIC gerada copia as variações históricas; as reuniões em que o Copom manteve a taxa não aparecem. A meta e a tolerância ficam em `core/indicators.py`, de onde a aprovação do governo também lê a meta. É a base para as métricas que chegam com o orçamento (F128): PIB, desemprego e dívida ÷ PIB entram no mesmo painel, pelo board do canvas, quando existirem.

### F166 · arquivado em 2026-10-31

*Kanban:* Pendências da partida: o que pede ação fica à vista até ser resolvido · feature · ✅ Concluído · atende N15 · marco M15

**F166 — Pendências da partida.** Separada do jornal da partida (F161) em 27/out: notícia é passageira, e o que pede ação fica à vista até ser resolvido, como os alertas do Victoria 3. Tipos: parcela em atraso, caixa que não cobre a próxima parcela, caixa negativo, estratégia desligada por erro, risco de impeachment (só o presidente), convite de vice e campanha aberta sem filiação; a votação sem orientação do líder (F153) entra quando existir. Cada uma traz a ação que a resolve e some quando a condição acaba. Ao nascer, sobe um toast uma vez; depois ela fica no lugar dela. Campanha aberta e convite de vice deixam de abrir diálogo sozinhos: clicar na pendência abre o mesmo diálogo de hoje. Pendência não se desliga. Lugar na tela, escolhido no canvas em 28/out (janela ao lado): Pendências é uma linha no topo do menu lateral, com a contagem (vermelha se alguma é grave); clicar abre a lista numa janela ao lado, com a ação de cada pendência, que fecha fora dela ou no Esc, sem pausar o jogo. As graves vêm primeiro, e a janela rola por dentro se a lista passar da tela. A topbar fica fora, por falta de espaço no pior caso. **Entregue:** Pendências é uma linha no topo do menu lateral, com a contagem (vermelha se alguma é grave, âmbar se são só avisos) e sem aparecer quando não há nenhuma. Clicar abre a lista numa janela ao lado, com a ação de cada pendência; ela fecha fora ou no Esc, sem pausar o jogo, e rola por dentro. A lista é calculada no servidor a cada consulta (nada fica guardado) e some item a item quando a condição acaba; ela se renova com os eventos de caixa, parcela, estratégia e governo e depois de qualquer ação do jogador. Os sete tipos entraram: parcela em atraso e caixa negativo (graves), risco de impeachment, caixa que não cobre a próxima parcela, estratégia desligada por erro, convite de vice e campanha aberta sem filiação (avisos). Ao nascer, sobe um toast "Nova pendência" uma vez, com a ação; os toasts de atraso, de parcela sem caixa e de estratégia desligada saíram. Pagar leva ao pagamento da parcela, e religar, à estratégia. Campanha aberta e convite de vice não abrem mais diálogo sozinhos: a ação leva à Eleição e abre o mesmo diálogo (o da campanha ganhou lugar na página, com as datas e os atalhos). A barra lateral ganhou o selo vermelho para a contagem grave. **Ficou de fora:** a linha verde "resolvida" que ficaria 2 s na lista e o aviso "Role para ver mais N" do desenho; a votação sem orientação do líder, que entra com o Congresso. **Decidido na implementação:** o risco de impeachment aparece para o presidente com a aprovação até 10 pontos acima do piso ou com fechamentos seguidos abaixo dele, e só depois do período de carência; a estratégia desligada por erro fica na lista até o jogador ligar uma estratégia de novo; a abertura da campanha continua pausando a sala, embora o diálogo não abra mais sozinho.

### F168 · arquivado em 2026-10-31

*Kanban:* Desafio da vela no lobby · feature · ✅ Concluído · atende N19, N23

**F168 — Desafio da vela no lobby.** Serve N19 e N23. O "sobe ou desce?" deixa a partida e vira um minijogo do lobby, no estilo das Atividades do Discord: todos respondem a mesma pergunta ao mesmo tempo, com placar ao vivo, enquanto o host configura e os outros entram. Na partida, o desafio disputava atenção com ordens e eventos, a pergunta passava sem ser vista e o resultado só saía 5 pregões depois; no lobby o tempo está parado e o resultado sai na hora.

(1) **Sai da partida:** a faixa "sobe ou desce?" (`challenge-strip.tsx`), o placar e o cartão "Desafio da vela" do resultado (`candle-challenge-card.tsx`, `useCandleChallengeRanking`), com as rotas e o acerto no tick (`settle`) que só existiam para eles. Ficam os marcadores de padrão, o card "E se ele acertou?" e a lista de padrões. O texto das Assistências e da página de análise técnica perde o desafio.

(2) **Pergunta:** um recorte aleatório de qualquer período e ativo da base, de umas 30 velas, que termina num padrão com lado (o doji fica fora), detectado pelas mesmas regras de `technical_analysis/patterns.py`. O sorteio equilibra padrões de alta e de baixa. A tela esconde o ativo, a data e a escala de preço (eixo em % a partir da primeira vela), então o recorte não diz nada sobre a partida que vai começar.

(3) **Rodada:** a pergunta fica aberta ~8 s; ao fechar, as 5 velas seguintes entram animadas no gráfico, o acerto de cada um aparece e o ativo e a data são revelados ("Era PETR4, março de 2015"). Preço igual ao do padrão anula a pergunta, como hoje. Segue a próxima. O servidor sorteia e cronometra a rodada e a transmite pelo tempo real que o lobby já usa (`realtime_broker`); quem entra no meio joga a partir da próxima; o host iniciar a partida descarta a rodada em andamento. O placar é da sessão do lobby.

(4) **Sozinho:** no lobby solo o minijogo continua, como treino contra o próprio recorde.

(5) **Conquistas:** Primeira leitura (1 acerto) e Leitor de velas (10 acertos) passam a contar os acertos do lobby; a métrica `candle_challenge_hits` deixa de ser por partida e soma o total do jogador, incluindo as respostas já gravadas em partidas, então quem já tem acertos não perde o progresso. Conquista desbloqueada continua desbloqueada.

(6) **Fora das assistências:** não é ajuda dentro da partida, então não some no modo Especialista nem com "Esconder dicas de análise técnica".

Decidido no canvas em 30/out: a tela é a variante B, uma janela de atividade por cima do lobby que minimiza num cartão no canto; 1 ponto por acerto, rodada de 10 perguntas com pódio e vitória dividida no empate, qualquer jogador começa e os outros recebem o convite, quem entra no meio assiste e joga da próxima, os votos só aparecem na revelação e, sozinho na sala, o recorde é a maior sequência de acertos. **Entregue:** o desafio saiu da partida (faixa, cartão do resultado, rotas e conferência no tick) e virou o minijogo do lobby. O servidor sorteia a pergunta (30 velas de um ativo e uma época da base, terminando num padrão com lado, equilibrando alta e baixa, com o eixo em % sem ativo nem data), cronometra a rodada numa thread (8 s de pergunta, 5 s de revelação) e a transmite pelo tempo real. A janela tem gráfico com a faixa "próximos 5", dica do padrão, cronômetro que fica vermelho nos 2 s finais, teclas ↑ e ↓, placar sem o lado de cada um até a revelação, pódio, tabela pergunta a pergunta, cartão minimizado onde dá para responder, convite, "Assistindo" para quem entrou no meio e estados de carregando e de erro. O host é avisado ao lado do botão de iniciar quando há um desafio rolando, e iniciar a partida descarta a rodada sem vencedor. Os acertos totais e o recorde ficam gravados por jogador (os acertos antigos de partidas foram somados na migração), e Primeira leitura e Leitor de velas contam esse total, com desbloqueio no lobby. **Ficou de fora:** a recusa do convite não é guardada no servidor: quem diz "Agora não" só deixa de ver o convite nesta rodada, na própria tela. **Decidido na implementação:** o texto da barra da janela diz "Minimize para configurar a partida" em vez de "o lobby segue atrás", porque a janela cobre o lobby; as vitórias da sala ficam só na memória do servidor.

### F178 · arquivado em 2026-10-31

*Kanban:* Conferência visual de tudo o que mudou desde a 3.0 · feature · ✅ Concluído · atende N15

**F178 — Conferência visual de tudo o que mudou desde a 3.0.** Serve N15. A última conferência em tela foi na 3.0; da 3.1 à 3.3 as features saíram conferidas por teste e `tsc`, e o app aberto mostra overflow, texto pequeno e cartões desalinhados. Só o visual: o comportamento o jogador pega jogando, e bug de backend entra só se for óbvio na passada. (1) **Roteiro:** um subagente Haiku lista, do `git diff --name-only v3.0.0 HEAD -- frontend` (uns 290 componentes: 94 no governo, 40 compartilhados, 25 nas estatísticas, 15 no desafio de velas, 14 no lobby, 11 no noticiário e o resto espalhado) e dos cards ✅ desde a 3.0, cada tela e o estado final dela, na ordem de uma partida: lobby, mercado, carteira, renda fixa, crédito, estatísticas, economia, jornal e pendências, campanha, 1º e 2º turnos, Congresso, contas do governo, conquistas, Como jogar e configurações. Estado intermediário que não existe mais (a votação antes do Congresso, por exemplo) fica de fora: confere-se o estado de hoje. (2) **Passada:** o app no banco de teste, com a expansão do governo e a corrida pela meta ligadas (o pior caso da topbar), aberto pelo `chrome-devtools` em 1366×768 e 1920×1080, com a captura de cada tela e estado do roteiro; a partida chega aos estados pelo x100 ou por uma partida salva do banco de teste. (3) **O que se olha em cada tela:** elemento passando da borda do cartão ou rolagem horizontal; texto cortado sem dica; texto abaixo de 12 px; contraste baixo (texto colorido claro sobre branco); cartões irmãos desalinhados ou de alturas que não batem; espaço vazio grande; peça feita à mão no lugar do componente do design system. (4) **Entrega:** a lista de achados por tela, com a captura e o problema, como artifact; o usuário prioriza. Correção pequena e óbvia sai como `fix:` (cada uma um patch da 3.2.1); a que pede outro desenho vai para o canvas. Primeiro achado, no cartão "Partidos na disputa" da Eleição em três colunas: o selo "Computador" passa da borda, o nome do partido corta ("Movimento N…"), as promessas passam da largura do cartão, os rótulos do radar cortam nas bordas ("erviço público", "Estabilidade"), o radar muda de tamanho e de altura de um cartão para o outro conforme o número de bandeiras, os rótulos do radar são pequenos e claros demais, e a legenda mostra "Na fundação", uma linha que não aparece quando o perfil não mudou.

**Aceite:** toda tela do roteiro, em 1366×768, sem rolagem horizontal nem elemento passando da borda, e sem texto abaixo de 12 px.

**Entregue:**
- o roteiro de 199 linhas de tela × estado;
- a passada em 1366 e 1920 no banco de teste, com a lista de achados por tela e as capturas;
- uma passada complementar dos estados de carregando, erro e vazio.

Os consertos pequenos saíram como `fix:`, um por conserto:
- o enum do 2º turno;
- o crescimento do PIB;
- 22 consertos de tela;
- 11 decisões de jogo e de texto.

O que pede outro desenho ganhou card próprio:
- o retrato no canvas (F180);
- as regras visuais do conjunto (F181), que herdam o aceite desta;
- a Eleição (F182);
- o Como jogar (F183);
- a topbar (F179);
- a preparação do lobby (F174).

### F157 · arquivado em 2026-11-04

*Kanban:* Velocidade x100 que quase não acelera · Performance · ✅ Concluído · atende N40, N24 · marco M20

**F157 — Velocidade x100 que quase não acelera.** Serve N40 e N24. No playtest, o x100 andou quase como o x1: o loop dormia `1 / velocidade` depois de um dia que levava de 0,6 a 0,95 s. Entregue: medida por etapa do dia no modo debug, espera pela cadência (descontando a duração do dia, com folga mínima para a tela pegar o lock), snapshots do dia numa consulta só e fechamento do crédito lendo só a janela da nota. Numa partida de 8 jogadores o dia caiu para 130 a 170 ms e o x100 anda de 6 a 7 dias/s. O agrupamento das emissões ficou de fora: a 4 dias/s o navegador recebeu 13 mensagens/s sem engasgar.

### F169 · arquivado em 2026-11-04

*Kanban:* Contribuição de campanha salva no perfil · Feature · ✅ Concluído · atende N34, N39 · marco M20

**F169 — Contribuição de campanha salva no perfil.** Serve N34 e N39. A contribuição mensal de cada filiado fica salva no perfil do jogador (`Users.settings`, chave própria, ao lado do Meu partido), e vale para quem funda e para quem se filia: o partido em que ele entra começa a cobrá-la quando a campanha abre, em vez de começar com zero. Quem nunca salvou continua com zero. A cobrança mensal já pula quem não tem caixa (`government_book.py`, coleta do 1º dia útil); o que muda é que **o mês pulado abre uma pendência** ("sua contribuição de R$ X não foi paga em março, por falta de caixa"), resolvida quando a contribuição seguinte é paga ou quando o jogador muda o valor. Mudar a contribuição dentro da partida também grava o valor no perfil. O campo da preparação mora na tela redesenhada (F174).

### F170 · arquivado em 2026-11-04

*Kanban:* Parâmetros das estratégias salvos no perfil · Feature · ✅ Concluído · atende N39 · marco M20

**F170 — Parâmetros das estratégias salvos no perfil.** Serve N39. Quem ajusta uma estratégia do modo automático (os dias das médias, o ativo, a divisão do rebalanceamento) precisa lembrar e redigitar os valores a cada partida. Os parâmetros passam a ficar no perfil, por estratégia (`Users.settings`, chave `strategy_params`: `{chave_da_estratégia: {parâmetro: valor}}`), por dois caminhos: (1) **o último valor usado**: ao ligar o automático numa partida, os parâmetros escolhidos se gravam no perfil daquela estratégia; (2) **a preparação**: a aba Estratégias da tela redesenhada (F174) lista as estratégias com os parâmetros de cada uma, para ajustar antes de jogar. Ao ligar o automático, o formulário nasce com os valores do perfil, ou com o padrão da estratégia onde o jogador não salvou nada. A validação é a mesma dos bots do lobby (`validate` da estratégia: tipo, mínimo e máximo); o ticker salvo que não existe na partida cai no padrão da estratégia, com aviso no formulário. O automático continua sendo ligado pelo jogador dentro da partida, que nasce pausada no 1º dia.

### F173 · arquivado em 2026-11-04

*Kanban:* Partido desde o 1º dia · Feature · ✅ Concluído · atende N39, N34 · decisões D19 · marco M20 · dependência de F175

**F173 — Partido desde o 1º dia.** Serve N39 e N34; condicionada pela D19. Hoje fundar e filiar-se só abrem com a campanha, um ano antes do 1º turno (`_ensure_campaign_open` em `government_book.py`), e a preparação do lobby espera a abertura para virar partido. Como no Brasil, onde o partido existe o tempo todo e o que tem prazo é a filiação de quem concorre, a regra passa a ser: **fundar, filiar-se e sair ficam livres desde o 1º dia**; a **filiação para concorrer** fecha 6 meses antes do 1º turno (Lei 9.504/97, art. 9): quem entra depois disso é filiado, mas não pode ser candidato nem vice naquela eleição; a **chapa, as ações de campanha e a cobrança da contribuição** continuam só na janela da campanha (a cobrança mensal pula os meses antes da abertura). **A preparação do lobby é aplicada no 1º dia da partida**, e não mais na abertura da campanha: os partidos preparados nascem com os filiados, e a chapa e o vice preparados ficam guardados no partido até a campanha abrir. Entre os turnos, filiação e saída continuam travadas. Partido de jogador fundado no meio do mandato não tem cadeira até a eleição seguinte. A preparação ainda não saiu em versão, então não há partida salva com o evento antigo para manter. Gatilho: antes do redesenho da preparação (F174), que mostra os partidos já existentes.

### F174 · arquivado em 2026-11-04

*Kanban:* Preparação do lobby redesenhada · Melhoria · ✅ Concluído · atende N39, N34 · marco M20

**F174 — Preparação do lobby redesenhada.** Serve N39 e N34; retrabalho da F143. O card "Minha preparação" ficou ruim na tela, e a preparação vai crescer (partido, parâmetros das estratégias, gestora), o que um card no lobby não comporta. A rodada no canvas foi feita e o usuário escolheu em 03/11 a **variante A: um dialog largo com abas** (Partido, Estratégias e, com a expansão, Gestora), aberto por um botão "Minha preparação" no cabeçalho do lobby, ao lado de Copiar link e Sair. A variante dos partidos à vista no lobby polui a sala e foi descartada; o desenho da sala do host, que redesenhava só o card, também. O desenho já mostra a contribuição salva no perfil (F169), os parâmetros das estratégias (F170) e o partido que existe desde o 1º dia (F173), que vêm juntos na 3.3.

**Decidido em 03/11:**
- a aba Gestora vale, por já nascer pronta para a expansão;
- a aba Estratégias segue a tela dos bots: ícones por estratégia e seções separadas como lá; o selo "ajustada" sai (estilo e minúsculas) e a indicação de parâmetro alterado usa o padrão visual dos bots;
- os cartões do dialog levam os ícones e o estilo dos que já existem no app.

**Decidido em 03/11 (2ª rodada):**
- entrar num partido é direto, sem pedido nem aprovação do fundador;
- os partidos do computador não aparecem no "Entrar": ali só os partidos preparados na sala;
- o partido, os membros e a chapa confirmada são públicos na sala; o convite de vice pendente só aparece para quem convidou e para quem foi convidado, e o host vê só a contagem;
- convite de vice ainda sem resposta quando a partida começa entra nela como convite comum;
- a última escolha volta marcada na próxima sala: "Fundar" volta como Fundar, e "Entrar" volta como Sem partido, porque o partido de outro jogador pode não estar na sala nova.

### F180 · arquivado em 2026-11-04

*Kanban:* Retrato no canvas das telas que mudaram desde a 3.0 · Manutenção · ✅ Concluído · atende N15 · marco M20

**F180 — Retrato no canvas das telas que mudaram desde a 3.0.** Serve N15. Da 3.1 à 3.3, cada tela foi desenhada sozinha no canvas e implementada sem conferência na tela. Juntas, elas quebram a topbar, fazem tabelas rolarem de lado e desalinham cartões (conferência visual, F178). Os boards do governo e da eleição mostram o desenho aprovado de cada feature isolada, não o app de hoje. Esta feature põe no canvas o app como ele está, para as rodadas de redesenho (F179, F181, F182, F183) comentarem sobre o conjunto e para comparar o que foi aprovado com o que foi implementado.

(1) **Limpeza.** As linhas das features implementadas até a 3.0 vão para uma página nova do Arquivo, mudando só a página do board. Ficam no canvas:
- as linhas das features ainda não implementadas, inclusive as variantes à espera de escolha;
- as linhas do governo e da eleição, até o retrato substituí-las;
- um board de identidade visual, de onde a skill `design-canvas` copia o `<helmet>` (fonte, cores e classes) para os boards novos.

(2) **Retrato.** Uma captura em 1920 de largura, a janela que o jogo usa (navegador maximizado num monitor 1920×1080), de cada tela e estado que mudou desde a 3.0, seguindo o roteiro da conferência visual (199 linhas de tela × estado). As capturas são tiradas depois dos consertos do hotfix, no banco de teste, com o governo e a corrida ligados. Cada captura vira um board de imagem do lado do antes, com uma linha por área: lobby, mercado e carteira, crédito, estatísticas, eleição, governo, jornal, Como jogar e configurações. É imagem, e não réplica em HTML: a réplica seria uma terceira versão da tela, cara de fazer e com as próprias divergências.

(3) **Post-its.**
- Ao lado da captura, os achados da conferência que ficaram para o canvas.
- Onde a tela difere do board aprovado da feature, o post-it "implementado diferente do aprovado", com a diferença. A comparação é texto contra texto: a spec do board (`extract_spec.py`) contra a árvore da tela no devtools, por um Haiku por área, com a captura para o layout.

(4) **Notas.** O canvas comporta 200 notas, e a limpeza libera as das linhas arquivadas.

**Como roda:** sessão Sonnet, sem decisão de design: o que pede escolha vira post-it para as rodadas de redesenho. Pede, na mesma sessão, o app rodando com o `chrome-devtools` e escrita no canvas original. Sem escrita no original, a sessão para e avisa.

Na mesma passada, a sessão confere os estados que o playtest não provocou (lista no fim da F184).

**Aceite:** toda tela do roteiro que mudou desde a 3.0 tem captura no canvas, e o canvas fica com até 185 notas.

### F181 · arquivado em 2026-11-04

*Kanban:* Tabelas que cabem na tela e texto legível · Melhoria · ✅ Concluído · atende N15 · marco M20

**F181 — Tabelas que cabem na tela e texto legível.** Serve N15. A conferência visual (F178) e o playtest acharam problemas que se repetem pelo app inteiro; nesta rodada o usuário confirmou que a **rolagem lateral dentro de tabela é um problema** em várias telas. Sem rodada no canvas: a regra é uma só e o aceite é objetivo.

**Regra das tabelas:** em 1920 de largura nenhuma tabela rola de lado; em 1366 vale só que nada passe da borda. Rolagem lateral fica permitida apenas para uma tabela que é larga por natureza (matriz de correlação entre muitos ativos), e nunca para resumo ou lista. Para caber, a tabela esconde a coluna secundária (a informação vai para o hover), junta duas colunas numa (valor e variação) ou quebra o texto em duas linhas, nessa ordem de preferência. A mudança vai no `shared/components/ui/table.tsx` quando for comum e na tela quando for específica.

**Telas com rolagem lateral hoje** (Gasto público, a votação do Congresso, a Central de dados e o Backtest vão nos cards próprios, com desenho aprovado: F190, F204, F214 e F215):
- Renda fixa, lista (`features/fixed-income/pages/fixed-income.tsx`);
- Estatísticas: Rentabilidade (`statistics-report/returns-tab.tsx`) e "Quando cada um negociou" (`operations-tab.tsx`, wrapper com `overflow-x-auto` na linha 291);
- Comparar partidas (F210);

**Texto e contraste:** 125 usos de texto abaixo de 12 px viram 12 px, e os rótulos com contraste de 3,4 a 3,6 para 1 sobem para 4,5 para 1 (o mínimo da recomendação de acessibilidade WCAG AA para texto comum); a mudança é nos tokens do design system (`index.css`) e nas classes `text-[10px]` e `text-[11px]`, por substituição em lote.

**Fora deste card:** eixos de gráfico (o Recharts decide), largura máxima da página e o preenchimento de vazios, que ninguém apontou como problema, e a paleta de cores (F212).

**Aceite:** as telas acima em 1920 de largura sem rolagem lateral e sem texto abaixo de 12 px.

### F182 · arquivado em 2026-11-04

*Kanban:* Eleição: corrida entre partidos redesenhada · Melhoria · ✅ Concluído · atende N15, N34 · marco M20

**F182 — Eleição: corrida entre partidos redesenhada.** Serve N15 e N34. A página (`features/government/pages/election.tsx`) empilha telas de features desenhadas separadamente e, na conferência visual e no playtest de 31/out, quebrou em vários pontos: o Ranking sobrepõe outro cartão e o texto dele sai desalinhado, o "Partidos na disputa" tem o selo "Computador" passando da borda, o nome do partido cortado, as promessas fora da largura, o radar de tamanho diferente entre cartões e rótulos pequenos demais, e a legenda mostra "Na fundação" mesmo quando o perfil não mudou. O desenho foi aprovado no canvas em 03/11 (board da corrida, com os ajustes abaixo).

**O que existe:** `party-profiles-card.tsx` (bloco "Partidos na disputa", com o radar de `profile-radar.tsx`), a tabela "Partidos", `ranking-card.tsx`, a faixa por grupo do `electorate-card.tsx` e, no diálogo de fundar partido (`found-party-dialog.tsx`), o bloco "Como o eleitorado recebe" de `flags-picker.tsx`.

**O que muda:**
- **Um bloco só por partido** em `party-profiles-card.tsx`: cada card ganha chapa, filiados, verba por mês e gasto, e a tabela "Partidos" sai porque passa a repetir o card. O selo "Computador" vai para a linha do nome, que não trunca mais.
- **Badges das bandeiras com o mini-ícone** que o app já usa nelas; o badge "chapa padrão" sai.
- **Radar** (`profile-radar.tsx`) com rótulos de pelo menos 12 px, dentro do painel e do mesmo tamanho em todos os cartões; a legenda "Na fundação" só aparece quando o perfil mudou.
- **Ranking da partida** (`ranking-card.tsx`) na largura toda, com "Individual" e "Patrimônio do partido" em colunas iguais, sem sobrepor a coluna vizinha.
- **Faixa por grupo** com cabeçalho: UPR, MNV, PTD e Margem. A Margem ganha dica: quanto a pesquisa pode errar para mais ou para menos (31% com margem de 3 pontos quer dizer entre 28% e 34%).
- **Diálogo de fundar partido:** só o bloco "Como o eleitorado recebe" muda (rótulos do radar dentro do cartão, nomes dos grupos sem corte, texto de pelo menos 12 px); o resto do diálogo fica como está.

**Não muda:** os dados, a ordem das seções e o gráfico da série.

**Aceite:** a Eleição em 1920 de largura, nas três fases (campanha, entre os turnos e resultado), sem elemento passando da borda nem rolagem lateral, e o Ranking sem sobrepor nada.

### F184 · arquivado em 2026-11-04

*Kanban:* Correções da 3.3 · Correção · ✅ Concluído · marco M20

**F184 — Correções da 3.3.** Lote dos consertos achados desde a 3.2. Tudo em main, em `fix:`. Primeiro lote, 37 commits:
- **Eleição e Governo:** a leitura dos eventos do 2º turno, que quebrava o resumo do mês, as estatísticas e as conquistas; a pesquisa do 1º turno ao lado da do 2º; a tabela de transferência do 2º turno (estimativa chamada de exata, partes que não somavam o total); a cor dos partidos do computador; a chapa do fundador sem vice; os diálogos de promessas e da votação; a data da posse; os cartões de pesquisa, eleitorado e promessas.
- **Economia e crédito:** o crescimento do PIB, que derrubava partidas longas; a nota de crédito, que ignorava parcela vencida; a alavancagem sem patrimônio; os pontos da nota de risco; o tooltip das séries da Economia.
- **Estados de erro e carregamento:** a tela de resultado, o jornal e o cartão do desafio da vela, que ficavam no esqueleto ou sumiam; a mensagem de erro das páginas de Governo, Eleição, Economia e Crédito; o ranking velho das Estatísticas; o diálogo do resultado do turno depois de recarregar.
- **Textos e corte:** plurais e concordâncias (compras e vendas, promessas, pontos, prêmio de risco); nomes cortados sem dica no lobby, nos partidos e nas estatísticas; a faixa do dia da renda variável; a janela do desafio da vela acima de 768 px; o painel final do desafio, que comemorava com 0 acertos; o relatório final; a coluna Quando das ordens abertas; a janela de notícias com a partida pausada.

Segundo lote, triado do playtest de 31/out e conferido em tela com o banco de teste:
- **Estatísticas e backtest:** o tooltip do backtest que diz "cdi contributed"; clicar no Ibovespa durante o backtest não desenha o gráfico; no Comparar, o cartão Risco cola a nota e a coluna Pts na borda direita (a tabela é mais larga que o cartão), e o mesmo cartão aparece nas outras telas de nota; o retorno das Estatísticas (2,27%) diferente do da Carteira e da Evolução (1,06% e 1,1% sobre o aportado) na mesma data: conferir se é métrica diferente ou dado de outra data, e, se for métrica, dizer qual no rótulo.
- **Partido e eleição:** encerrar a conta e entrar de novo com o mesmo nome deixa a página do partido dizendo "Você não está em nenhum partido" com o resto da tela como filiado; o partido fundado por outra conta no diário dela, que não deu para reproduzir: com duas contas na mesma sala o fundador aparece na faixa do Diário e no jornal na hora; selecionar as bancadas em "Selecionar apoio" faz o diálogo piscar.
- **Governo:** o diálogo de nova medida passa da altura da tela em todos os tipos de medida, e o seletor "Mudança" tem um vão à direita de "Isentar", como se faltasse uma terceira opção; o botão "Sair da base" e o botão do alerta de erro ficam soltos dentro do alerta: o `Alert` do design system ganha o lugar da ação, em vez de cada tela encaixar o botão.
- **Visual:** na barra lateral, os selos de Pendências, Conquistas, Eleição, Debug e estratégia desligada ficam descentrados na vertical, e o ponto da Eleição sai oval; os números do jornal na fonte serifada descem da linha (algarismos de estilo antigo: `font-variant-numeric: lining-nums`); "Restaurar padrão" é menor que "Ligar esta estratégia" (`strategy-detail.tsx`, `size="sm"` contra o tamanho padrão); o "i" de Padrões de vela não abre a dica (o gatilho é um svg solto, sem elemento que receba o foco).
- **Gerador de futuro:** o campo "até quando" aceita qualquer ano e dispara a prévia a cada dígito (21000 por engano): o campo virou seletor de ano, com teto de 30 anos além do último dado real, e o backend recusa o que passar disso.

Ficam para a sessão do retrato (F180), que roda o app com o devtools, os estados que não deu para provocar no playtest: Crédito com parcela atrasada, o esqueleto e o erro do cartão do desafio da vela (forçados bloqueando a requisição) e o diálogo do resultado numa pausa real.

### F185 · arquivado em 2026-11-04

*Kanban:* Dia da partida que fica mais lento ao longo da partida · Performance · ✅ Concluído · atende N40, N24 · marco M20

**F185 — Dia da partida que fica mais lento ao longo da partida.** Serve N40 e N24. No playtest de 31/out o passo "Processar um dia" subiu de 576 ms de mediana no primeiro terço da sessão para 757 e 940 ms nos seguintes, e no backtest de 10 anos com 5 bots a previsão de tempo não caía com o progresso.

A medição apontou o fator de impacto de preço no histórico que os bots pedem: a cada pedido, o fator de cada dia da janela era refeito de todos os fluxos de ordens desde o começo da partida. O fator de um dia passado passou a ser calculado uma vez e guardado, só com as ordens ainda dentro do decaimento; um teste confere que ele sai igual ao recálculo completo. O snapshot do dia passou a gravar só o balanço (ações, renda fixa, dívida), sem montar a carteira da tela, que segue saindo só para quem está conectado.

Em `pnpm profile:match --days 1000 --bots 7`, três rodadas: o dia no fim da partida caiu de 190–201 ms para 89–95 ms de mediana, a razão fim ÷ início de 1,51–1,65 para 1,07–1,13, e os 1.000 dias de ~163 s para ~93 s. O que ainda cresce é o envio da carteira (imposto refeito sobre todas as operações e duas somas no banco), medido com os 8 jogadores tratados como conectados; na partida real só os humanos recebem. A previsão do backtest de 10 anos passou a cair, conferida na tela.

**Aceite:** a mediana do dia depois de 1.000 dias fica a até 10% da mediana dos primeiros 50, e a previsão do backtest de 10 anos com 5 bots cai de forma contínua até o fim.

### F186 · arquivado em 2026-11-04

*Kanban:* Estatísticas lentas numa partida longa · Performance · ✅ Concluído · atende N38, N24 · marco M20

**F186 — Estatísticas lentas numa partida longa.**
Na partida longa de 10 anos e 8 jogadores, as abas caíram de 1 a 24 s para 0,3 a 0,85 s: nota ao longo da partida numa passada só, volume médio do impacto numa consulta por ativo, leitura do histórico só com as colunas usadas e cada consulta planejada com os valores dela. Cinco abas ficam entre 0,65 e 0,85 s, acima dos 500 ms, aceitas. Sem leitura dupla em produção: o par de pedidos na tela é o StrictMode do dev, e a aba já montada no mês volta do servidor em 5 a 11 ms.

### F187 · arquivado em 2026-11-04

*Kanban:* Um log por boot do servidor · Manutenção · ✅ Concluído · atende N26 · marco M20

**F187 — Um log por boot do servidor.** Serve N26. Cada arquivo da pasta de logs tinha o próprio `RotatingFileHandler`, de 10 MB com 5 cópias, e as sessões se emendavam no mesmo arquivo: achar o log de um playtest era procurar pelo horário.

Agora a pasta segue a estrutura do Victoria 3. `app.log` é o boot atual, `app.1.log` é o boot anterior, e assim até `app.5.log`. O mesmo vale para `error`, `database`, `import`, `realtime`, `simulation` e `slow`. No boot, antes de abrir cada arquivo, o logger empurra a fila uma casa e descarta o mais antigo (`_shift_previous_boots` em `backend/core/logger.py`). Não há mais rotação por tamanho: cada arquivo guarda um boot inteiro. A primeira linha de cada arquivo diz a versão, se o modo debug está ligado e a hora do boot, no mesmo formato das outras linhas. O giro roda uma vez, no único processo do servidor, que sobe com `reload=False`.

A pasta que as Configurações abrem e os nomes dos arquivos atuais continuam os mesmos. Para conferir, os testes do logger fazem dois e oito boots seguidos numa pasta temporária, e dois boots do app contra o banco de teste deixaram `app.1.log` com o primeiro boot inteiro.

### F188 · arquivado em 2026-11-04

*Kanban:* Eventos do Socket.IO no modo debug, com contagem acumulada, tamanho e atraso · Melhoria · ✅ Concluído · atende N24 · marco M20

**F188 — Eventos do Socket.IO no modo debug, com contagem acumulada, tamanho e atraso.** Serve N24. O cartão "O que vai para o navegador" do painel de desempenho mostrava só uma janela de 10 s, que esvaziava com a partida pausada (não era bug: a janela andava sem emissões), e a aba Socket.IO da tabela de tempo tem só os 4 eventos que o navegador manda. Um evento pesado sumia antes de ser visto, e o custo dos eventos enviados ficava escondido em "Processar um dia".

**O que mudou:** o coletor (`backend/core/metrics.py`) guarda, por evento enviado e desde o boot ou o último "Zerar medições", os envios, os envios sem ninguém inscrito, o total de bytes, o tamanho típico (mediana) e o p95 sobre os últimos 1.000 envios, o atraso p95 na fila de saída (do `notify` à entrega ao socket, medido no `ws_broker`) e a hora do último envio; a janela de 10 s continua como "Agora". O bloco que publica o fim do dia virou a medição "Publicar o dia", dentro de "Processar um dia" e fora da soma da fatia. A tela tem uma tabela única, ordenável, com as colunas "Agora" e "Desde que zerou" e a dica de cada coluna; pausado, a linha fica e o "Agora" mostra "—". O primeiro uso já mostrou `stock_update:*` e `order_book_snapshot:*` com 100% dos envios sem ninguém.

### F189 · arquivado em 2026-11-04

*Kanban:* Retoques de interface do playtest de outubro · Melhoria · ✅ Concluído · atende N15, N21 · marco M20

**F189 — Retoques de interface do playtest de outubro.** Serve N15 e N21. Mudanças pequenas, sem rodada no canvas, que o playtest de 31/out pediu:
- **Log das ordens do bot** num drawer lateral, como as configurações do lobby, no lugar do cartão que abre embaixo da listagem e obriga a rolar a página; o cartão de hoje se adapta à largura do drawer, o "Ver mais" continua no `useInfiniteQuery` que já existe (`useBotLog`, `useStrategyLog`) e fechar o drawer fecha o log.
- **Seletor do vice** com o avatar e o nome de cada jogador, como no resto do app.
- **Filtro "Na carteira"** na renda variável, igual ao da renda fixa.
- **Período do backtest** com o mesmo seletor de intervalo da sala.
- **Correlação** sem a ordenação pelos cabeçalhos (`correlation-matrix.tsx:74`): a matriz fica na ordem em que os ativos foram escolhidos.
- **Selos "a sala vê" e "a sala vê na fila"** saem; fica só o "a sala não vê", com ícone, como na estratégia.
- **"Quem tem esses ativos"** sai do diálogo de nova medida: a mesa não aponta quem a medida machuca, e quem quiser saber descobre olhando os outros jogadores (N21).
- **Curvas internas fora da tela:** o gráfico do prêmio de risco pela dívida e o da escala do investimento da eleição saem das telas; a explicação passa para o tópico de conceito do Como jogar, quando houver.
- **Configurações** com os cartões reordenados: a zona de perigo por último, e o Como jogar ao lado da configuração irmã e no mesmo layout dela.
- **Aviso de atualização das Estatísticas** (`update-notice.tsx`) também com a partida pausada, dizendo a data da última atualização; a contagem até a próxima aparece só com a partida andando.

Cada item sai num commit `feat:` próprio.

### F190 · arquivado em 2026-11-04

*Kanban:* Contas do governo redesenhadas · Melhoria · ✅ Concluído · atende N15, N34 · marco M20

**F190 — Contas do governo redesenhadas.** Serve N15 e N34. No playtest de 31/out, a página do Governo confundiu: muita informação, o painel das contas misturado com o Congresso e as medidas, os gráficos de barra da conta do país difíceis de ler e o Gasto público rolando de lado. O que funcionou e serve de molde: a explicação "inclui 2,3 de prêmio", com a soma que monta a taxa de hoje. O desenho foi aprovado no canvas em 03/11 (board "governo-contas").

**O que existe:** a aba "Contas" (`features/government/components/accounts-tab.tsx`) monta `taxes-card.tsx` (Impostos), `revenue-card.tsx` (De onde vem a receita), `spending-card.tsx` (Gasto público), `budget-card.tsx` (A conta do país), `debt-premium-card.tsx` (Dívida e prêmio de risco) e `budget-readers-card.tsx` (Quem lê a conta).

**O que muda:**
- **Uma coluna só**, na ordem da conta: Base, A conta do país, o que Entra, o que Sai, e a Dívida.
- **Impostos e receita viram uma tabela só** (`taxes-card.tsx` absorve `revenue-card.tsx`): alíquota de hoje, padrão (a regra de antes da expansão) e quanto arrecada, lado a lado. A isenção de R$ 20 mil vira nota na linha "Ações · vendas com lucro".
- **Gasto público** (`spending-card.tsx`) na largura toda, sem rolagem lateral, com o nome da medida numa linha e a descrição embaixo.
- **Dívida:** o título e o texto de "prêmio de risco" saem, porque descreviam um gráfico que já foi removido; o eixo do gráfico continua o automático do Recharts.
- **"Quem lê a conta"** (`budget-readers-card.tsx`) não aparece no desenho e sai da aba.

**Aceite:** a aba "Contas" em 1920 de largura sem rolagem lateral e sem cartão que repita número de outro.

### F203 · arquivado em 2026-11-04

*Kanban:* Eleição: aba da campanha reorganizada · Melhoria · ✅ Concluído · atende N15, N34 · marco M20

**F203 — Eleição: aba da campanha reorganizada.** Serve N15 e N34. Na aba "Campanha do {sigla}" (`features/government/components/campaign-section.tsx`), o playtest e a conferência de 02/11 acharam a tela confusa: a mesma informação mora em mais de um lugar (Eleitorado, Últimas ações e Histórico, Verba de base). O desenho foi aprovado no canvas em 03/11, com uma ressalva: o cartão "Ações de campanha" (`campaign-actions-card.tsx`) fica exatamente como está, porque já foi bem desenhado e não é o problema da página.

**O que muda** (cada coisa num lugar só):
- **Pesquisa no grupo:** o passo 2 das ações ganha a coluna "Pesquisa no grupo" (por exemplo, PTD 0% com margem de 11 pontos), que mostra também o líder do grupo; o Eleitorado (`electorate-card.tsx`) sobe para logo abaixo das ações, onde a escolha acontece.
- **Últimas ações e Histórico** (`campaign-recent-card.tsx`, `campaign-history-card.tsx`) viram um cartão só, com um único estado vazio; o "Histórico ›" rola até esse bloco.
- **Verba de base** (`campaign-base-card.tsx`) entra no cartão "Seu partido", com um botão "Mudar". "Seu partido" ocupa a largura toda em três colunas: verba e filiados, promessas e bandeiras, orientação da bancada.
- **Ícones:** os ícones dos grupos (Investidores e os demais), das ações (Comício e as outras) e das bandeiras ficam como estão hoje no app. O board é um esboço sem eles; na implementação a referência é a tela atual.

**Aceite:** a aba em 1920 de largura, com a campanha aberta e sem campanha, e sem informação repetida entre cartões.

### F204 · arquivado em 2026-11-04

*Kanban:* Congresso: votação com placar e casa eleita · Melhoria · ✅ Concluído · atende N15, N34 · marco M20

**F204 — Congresso: votação com placar e casa eleita.** Serve N15 e N34. Na aba "Congresso" do Governo (`features/government/components/congress-tab.tsx`), a tabela da votação (`vote-table.tsx`, usada pelo `vote-dialog.tsx`) rola de lado e não mostra o placar da medida em andamento; e a conferência de 02/11 achou duas coisas do desenho aprovado que o app não tem: o acesso a "Como a casa foi eleita" e a "Ver votações anteriores". O desenho da votação foi aprovado no canvas em 03/11.

**O que muda:**
- **Faixa de placar** no topo da votação: "30 Sim" numa barra de 0 a 101, com a marca dos 51 votos Sim necessários para passar (maioria fixa de 51 em 101 cadeiras, `house.py:21-24`).
- **Tabela sem rolagem lateral** (`vote-table.tsx`): a orientação vira selo Sim/Não com quem orientou embaixo, e a explicação de "Pode desobedecer" vira uma linha abaixo do número.
- **Legenda** com as cores reais do hemiciclo (escura = Sim, cinza claro = Não), e o hemiciclo (`hemicycle.tsx`) ganha a linha tracejada dos 51 votos.
- **"Como a casa foi eleita ›"** na `house-card.tsx`, levando ao bloco da casa eleita (`elected-house.tsx`), e **"Ver votações anteriores"** no `vote-history-card.tsx`.

**Aceite:** a aba "Congresso" e o diálogo de votação em 1920 de largura, sem rolagem lateral, com o placar visível enquanto a votação está aberta.

### F205 · arquivado em 2026-11-04

*Kanban:* Jornal igual ao desenho aprovado, com histórico paginado · Melhoria · ✅ Concluído · atende N15, N31 · marco M20

**F205 — Jornal igual ao desenho aprovado, com histórico paginado.** Serve N15 e N31. A página do jornal (`features/news/pages/journal.tsx`, com `journal-paper.tsx` e `journal-entries.tsx`) ficou longe do desenho aprovado, e o usuário concorda que o aprovado era mais bonito. Ela também carregava o histórico inteiro de uma vez, sem paginação.

**O que mudou** (regras decididas em 02/11 e 03/11):
- **"Hoje" virou edição de jornal:** uma manchete grande, a de maior variação do dia (duplicata do mesmo ativo no dia vira uma só), e três menores em colunas. A variação passou a ser gravada na manchete (`change_pct`, anulável).
- **Dias anteriores** viraram linhas compactas (editoria, título, resumo, chip).
- **Histórico em rolagem contínua, um mês por página:** `useInfiniteQuery` em que cada página é um mês, aberto no mês atual; ao chegar ao fim da lista, o mês anterior carrega sozinho. A coluna da direita é o arquivo da partida: clicar num mês recomeça a lista dele, e "Voltar a hoje" restaura a abertura. "Hoje" e o arquivo ficam fixos; só a lista rola. `GET /api/news` recebe o mês.
- O chip da carteira ganhou o texto "na carteira".

**Aceite:** a página do jornal numa partida longa abre sem carregar o histórico inteiro, e a edição de "Hoje" bate com o board aprovado, rolar até o fim carrega o mês anterior sem clique e clicar num mês do arquivo salta direto para ele.

**Conferido na tela (03/11):** abre com uma requisição só (o mês atual); rolar até o fim carrega o mês anterior sem clique; o salto pelo arquivo e o "Voltar a hoje" funcionam; a busca sem resultado percorre os meses até o primeiro da partida. Ficou de fora a contagem "N manchetes em M pregões" do cabeçalho, que pede um endpoint de total.

### F206 · arquivado em 2026-11-04

*Kanban:* Carteira: percentuais com base, alturas iguais e meta na escala · Melhoria · ✅ Concluído · atende N15 · marco M20

**F206 — Carteira: percentuais com base, alturas iguais e meta na escala.** Serve N15. Na conferência de 02/11 o usuário aprovou três melhorias da carteira (`features/portfolio/`), e a quarta é um desvio do desenho aprovado:
- **Cada percentual diz a sua base:** "% dos ativos" nos blocos de distribuição (`allocation-donut.tsx`, `sector-allocation-card.tsx`) e "% do investido" na coluna da tabela de posições (`positions-card.tsx`). Setor sem linha repetida, só o ramo.
- **Setor e imposto de renda com a mesma altura** (`sector-allocation-card.tsx` e `income-tax-card.tsx`).
- **Meta no gráfico:** a linha da meta (`networth-gain-chart.tsx:35`, hoje sempre na escala do eixo) só entra na escala quando o patrimônio passa de uns 10% dela; abaixo disso, o eixo acompanha o patrimônio e a meta vira um selo acima do gráfico ("abaixo da escala, você está em 0%"). Nada além disso muda no gráfico.
- **Carteira vazia:** a mensagem "O gráfico começa no próximo pregão" que o desenho aprovado tem e o app não (`networth-chart.tsx`, componente `Empty`).

**Aceite:** a carteira com patrimônio de 7% da meta mostra o gráfico em escala útil, e os cartões de setor e imposto de renda saem com a mesma altura.

### F207 · arquivado em 2026-11-04

*Kanban:* Placar da vela com os votos de cada jogador · Correção · ✅ Concluído · atende N15, N22 · marco M20

**F207 — Placar da vela com os votos de cada jogador.** Serve N15 e N22. A conferência de 02/11 comparou o desafio da vela com o desenho aprovado, e o usuário confirmou que faltam o placar com os votos e a posição do jogador. O que o código mostra hoje: `scoreboard.tsx` só entra na janela (`challenge-window.tsx:94`) fora da sala solo e mostra contadores ("N disseram sobe", "N disseram desce") e o ✓/✗ de acerto; o backend já manda a direção de cada voto (`ChallengeVoteDTO`, em `core/dto/candle_challenge.py`), que a tela não usa; e o "Você 2º" só existe no dock minimizado (`challenge-dock.tsx:61`) e no fim (`final-panel.tsx:91`).

**O que muda:**
- Na revelação (`reveal-panel.tsx` e `scoreboard.tsx`), cada jogador aparece com o lado em que votou (sobe ou desce) ao lado do ✓/✗, como no desenho aprovado; o texto de `scoreboard.tsx:56` ("✓ e ✗ ao lado de cada nome") passa a dizer o que a tela mostra.
- Na pergunta, o placar continua mostrando só quem já respondeu (sem revelar o lado).
- A posição do jogador ("Você 2º") aparece no cabeçalho da janela (`challenge-header.tsx`) nas duas fases, e não só no dock.
- A legenda da linha do gráfico (`candle-chart.tsx`) segue o desenho aprovado.
- Passo de conferência antes de codar: abrir o desafio numa sala com dois jogadores e confirmar se o placar aparece também na pergunta e na revelação (nas capturas de 02/11 ele não apareceu, e a sala solo o esconde de propósito).

**Aceite:** numa sala com dois jogadores, a revelação mostra o voto de cada um e a posição do jogador aparece nas duas fases.

### F208 · arquivado em 2026-11-04

*Kanban:* Empréstimo: o custo inteiro antes de assinar · Melhoria · ✅ Concluído · atende N15, N33 · marco M20

**F208 — Empréstimo: o custo inteiro antes de assinar.** Serve N15 e N33. Na simulação de empréstimo (`features/credit/components/loan-offer-card.tsx`), quem decide não vê o que a assinatura muda na dívida e na nota. O usuário aprovou em 03/11 o desenho do canvas, pequeno, para sair junto da 3.3.

**O que muda:**
- Um bloco **"Se você assinar"** no resultado, com hoje e depois: dívida, parcelas por mês, alavancagem (dívida dividida pelo patrimônio) e sobra do limite.
- A comparação entre o juro e o rendimento vira um aviso amarelo com os dois números lado a lado.
- A barra do limite engrossa e diz quanto sobra.
- Os textos da escada de notas (`risk-rating-card.tsx`) sobem para 12 px, e os botões Amortizar e Quitar (`loans-table.tsx`) ganham 32 px de altura.
- Decidido em 02/11: empréstimo novo com parcela em atraso continua liberado (a tela só avisa o atraso e o estado "bloqueado" da proposta sai); o bloco projeta só a alavancagem depois do empréstimo.

**Aceite:** a simulação mostra a alavancagem de depois sem o jogador fazer conta.

### F209 · arquivado em 2026-11-04

*Kanban:* Crédito em atraso: valor do diálogo, nota do mês e aviso no topo · Melhoria · ✅ Concluído · atende N33, N15 · marco M20

**F209 — Crédito em atraso: valor do diálogo, nota do mês e aviso no topo.** Serve N33 e N15. Na conferência de 02/11 o usuário estranhou a tela de atraso: o jogador tinha caixa e a parcela não foi descontada, e os valores do diálogo pareciam divergir (botão "Pagar" em R$ 1.565,60 contra R$ 45,60 de multa e mora). O código mostra o seguinte:
- **O débito automático só olha o caixa no dia do vencimento** (`credit_book.py:494-531`, `_settle_due`): se o caixa cobre a parcela naquele dia, ela é descontada; se não cobre, a parcela vira atraso e nada é vendido, nem o cheque especial entra. Caixa que chega depois do vencimento não paga a parcela sozinho; só o botão "Pagar" paga.
- **O botão e a linha "Total" usam o mesmo número** (`overdue_charges` em `price.py:131`, somado em `pay-overdue-dialog.tsx:34`); o servidor recalcula no dia do pagamento (`credit_book.py:699`). Com o diálogo aberto e o dia do jogo avançando, o valor na tela fica velho até recarregar, e a multa e a mora do dia novo não são as mostradas.
- **A alavancagem de 0,0% na nota** vem do fechamento do mês (`overview.py:238`, `close_rating`): um empréstimo contratado neste mês só entra na nota quando o mês fecha, enquanto o resumo do topo (`credit-summary.tsx`) usa o valor ao vivo.

**O que fazer:**
1. Reproduzir no banco de teste: empréstimo com parcela vencida sem caixa, depois com caixa; abrir o diálogo, avançar o dia e comparar o "Total" com o valor cobrado. Escrever um teste do backend para o valor cobrado no dia seguinte e do front para o diálogo recarregar o valor a cada dia (`pay-overdue-dialog.tsx`), e corrigir o que o teste mostrar (`fix:`).
2. A nota mostra, ao lado da alavancagem, que ela é a do último fechamento ("fechamento de <mês>"), e o texto "muda no fim do mês" fica visível quando há empréstimo novo (`risk-rating-card.tsx`).
3. Aviso do desenho aprovado em 03/11 (`feat:`): um aviso vermelho no topo da página diz qual parcela atrasou, há quanto tempo e quanto já custou de multa, e traz o botão Pagar; o cartão de parcelas do topo soma o atraso; a lista Pagamentos abre com a parcela atrasada; o mês atrasado no histórico ganha rótulo vermelho além da cor.

**Aceite:** o valor do botão "Pagar" é o mesmo cobrado, em qualquer dia, e a página de crédito com parcela em atraso mostra o aviso no topo.

### F210 · arquivado em 2026-11-04

*Kanban:* Comparar partidas: eixos em grade e Risco inteiro · Melhoria · ✅ Concluído · atende N6, N15 · marco M20

**F210 — Comparar partidas: eixos em grade e Risco inteiro.** Serve N6 e N15. A página de comparação (`features/statistics/pages/compare-simulations.tsx`) tem o cartão de nota por eixo (`statistics-report/player-score-card.tsx`) estreito demais: o "0" do cartão Risco continua colado na borda em 1920 de largura, mesmo depois da correção de 02/11, e o ranking corta a coluna Pregões. O usuário aprovou em 03/11 o desenho do canvas.

**O que muda:**
- Título e explicação da nota em linha inteira; os seletores de jogador numa linha própria abaixo (o título vira "Nota de <jogador>" ao escolher outro).
- Os eixos numa grade 2×2 de uns 500 px cada, onde cada métrica cabe numa linha; isso resolve o Risco, que no layout de 4 colunas não tem espaço.
- O ranking tira a barra de retorno e fica com o número colorido, o que libera espaço para mostrar Pregões (dias de pregão jogados) sem corte.
- Nada mais muda de ordem.

**Aceite:** a comparação em 1920 de largura sem valor colado na borda nem coluna cortada.

### F212 · arquivado em 2026-11-04

*Kanban:* Paleta de cores de jogadores e partidos · Melhoria · ✅ Concluído · atende N20, N15 · marco M20

**F212 — Paleta de cores de jogadores e partidos.**
Serve N20 e N15. As 13 cores saíram de um script que maximiza a menor distância CIEDE2000 entre cada par na visão normal e nas simulações de protanopia, deuteranopia e tritanopia, com 3:1 de contraste sobre o fundo claro, sigla legível (4,5:1) em branco ou tinta e sem vermelho nem verde puros. O par mais parecido passou de 4,5 a 8,5 para 17,2 na visão normal, 11,0 na protanopia, 11,2 na deuteranopia e 8,6 na tritanopia. Dez são dos jogadores (`chart-1` a `chart-10`, cada uma no lugar da antiga mais parecida) e três dos partidos do computador (UPR cinza, ACI petróleo, MNV oliva). O partido de jogador escolhe entre as dez cores de jogador, já marcada a de quem funda quando está livre, e a sigla do partido usa o texto da cor de jogador de mesmo hex. O ranking de partidos das Estatísticas ainda manda o cinza `#7d879b` para todo partido do computador.

### F213 · arquivado em 2026-11-04

*Kanban:* Pendências: consequência inteira e Pagar em destaque · Melhoria · ✅ Concluído · atende N15 · marco M20

**F213 — Pendências: consequência inteira e Pagar em destaque.** Serve N15. A lista de pendências (popover da barra lateral, `features/pending/components/pending-menu-item.tsx`, com `pending-row.tsx` por item) corta a consequência de cada item, a gravidade só se distingue pela cor da borda e a dica tem texto pequeno e apagado. O desenho da lista foi aprovado no canvas em 03/11.

**O que muda:**
- **Consequência inteira em linha própria** (`pending-row.tsx`): o texto de "quando some" e o detalhe deixam de ser cortados e ganham uma linha cada.
- **Gravidade também em texto:** o item grave leva a palavra "Grave", além da borda vermelha, para quem não distingue as cores.
- **Dica em 12 px com contraste:** a legenda ("Vermelha quando já custa dinheiro, âmbar quando ainda dá tempo.") sobe para o rodapé da lista, com cor de texto legível.
- **Pagar como botão principal** da linha; a ação de cada item (rótulo de `pendingTarget`) usa a variante principal do botão.
- **Lista de 400 px de largura** (o popover hoje tem `w-80`, 320 px).

**Aceite:** o popover em 1920 de largura, com uma pendência grave e uma leve, sem texto cortado e com a gravidade legível sem depender da cor.

### F214 · arquivado em 2026-11-04

*Kanban:* Central de dados: tabela que cabe no cartão · Melhoria · ✅ Concluído · atende N15 · marco M20

**F214 — Central de dados: tabela que cabe no cartão.** Serve N15. A tabela de séries da Central de dados (`features/import-assets/components/series-table.tsx`, página `import-assets.tsx`) rola de lado e deixa o botão de atualizar azul em todas as linhas, o que apaga a ação em massa. O desenho foi aprovado no canvas em 03/11.

**O que muda:**
- **Sem rolagem lateral:** as colunas Série, Setor · segmento, Dados reais até, Situação e Ações cabem no cartão em 1920 de largura; texto longo termina em reticências e mostra o conteúdo inteiro no hover.
- **Linha de cerca de 62 px** (hoje a altura varia com o conteúdo).
- **"Atualizar" por linha em contorno**; o azul cheio fica só na ação em massa "Atualizar desatualizadas (n)" do cabeçalho do cartão.
- **Selo "Parou em …"** (o `Badge` de aviso da coluna Situação) mantido e alinhado à coluna, sem quebrar a linha.

**Aceite:** a página `/import-assets` em 1920 de largura sem rolagem lateral e com uma única ação em azul cheio.

### F215 · arquivado em 2026-11-04

*Kanban:* Backtest: formulário do período sem estouro · Melhoria · ✅ Concluído · atende N15 · marco M20

**F215 — Backtest: formulário do período sem estouro.** Serve N15. No formulário do backtest em modo lista (`features/backtest/components/backtest-form.tsx`), a coluna do período e dinheiro (`period-card.tsx`, com o `period-picker.tsx` compartilhado) estoura: os atalhos e as datas passam da borda. O usuário viu o estouro ao testar o backtest em 03/11. O desenho foi aprovado no canvas em 03/11.

**O que muda:**
- **Coluna do período com 440 px** (hoje `grid-cols-[360px_minmax(0,1fr)]`), as estratégias (`participant-list.tsx`) ocupam o resto.
- **Atalhos em duas linhas** no `period-picker.tsx` (hoje `grid-cols-[4fr_2fr]`), e **datas Início e Fim lado a lado**.
- **Campos inteiros:** nome, saldo inicial e aporte mensal cabem sem corte.
- O seletor de período é compartilhado: a mudança vale também para onde ele é usado.

**Aceite:** `/backtest/new` em modo lista, em 1920 de largura, sem texto cortado nem rolagem lateral na coluna do período.

### F97 · arquivado em 2026-11-07

*Kanban:* SELIC nas mãos do governo · Feature · ✅ Concluído · atende N34 · decisões D19, D14, D20 · marco M21

**F97 — SELIC nas mãos do governo.** Ligado à N34; uma opção da expansão "Governo & Política" (F95), no lugar do Banco Central autônomo, que continua sendo o padrão. (1) **Ritmo do Copom:** o governo decide a SELIC em reuniões a cada 45 dias, como o Copom, que se reúne 8 vezes por ano desde 2006; entre reuniões ela não muda. (2) **Teto por reunião, pelo que aconteceu de verdade.** Das 150 mudanças da meta da SELIC entre 2000 e outubro de 2026 (série do Banco Central): 34 foram de 0,25 ponto, 67 de 0,5, 19 de 0,75, 19 de 1, 7 de 1,5, uma de 2, uma de 2,5 e duas de 3; desde 2006, nunca passou de 1,5. O teto vem do IPCA de 12 meses: 0,75 ponto em tempo normal (80% das mudanças reais), 1,5 com o IPCA acima do teto da meta (a meta mais a tolerância de 1,5 ponto), como em 2021 e 2022, e 3 com o IPCA acima de 15%, o que só aconteceu em 2002 e 2003. (3) **O efeito vem do juro real, contínuo e sem faixa morta.** Juro real é a SELIC menos o IPCA de 12 meses; o juro neutro, que nem aquece nem esfria, é 5%, perto da estimativa do Banco Central. A distância até o neutro age pelo mecanismo de efeito por cima das séries da F106: cada ponto abaixo do neutro, mantido por um ano, sobe o IPCA em uns 0,3 ponto ao longo dos 4 trimestres seguintes, com o pico no 2º e no 3º (o modelo Samba do Banco Central), e cada ponto acima o derruba na mesma medida. Abaixo do neutro o crescimento aquece na hora; acima, esfria e a bolsa cai pelo coeficiente da D14. Como o efeito é contínuo, nenhuma faixa de juro sai de graça. Os limites de 2% e 7% de juro real servem só para os avisos e para a reação dos grupos (D19): abaixo de 2%, aposentados e quem vive de investimento perdem apoio; acima de 7%, quem trabalha e empreende. (4) **Credibilidade.** Cada reunião que deixa o juro real abaixo do neutro com o IPCA acima da meta gasta credibilidade; cada reunião que aperta devolve um pouco, devagar. Com pouca credibilidade a inflação reage mais rápido ao juro baixo, porque o mercado já espera que ela suba, e o prêmio de risco dos títulos (F128) sobe: o governo que usou a SELIC para ganhar a eleição herda uma inflação que não cede. A tela mostra a credibilidade com uma dica do que ela mede e do que a move. O 0,3 é ordem de grandeza dos modelos semiestruturais e se calibra no playtest; não se mede no histórico do banco, porque a SELIC reage à inflação e a regressão direta sai com o sinal trocado. Fontes: [Relatório de Inflação de junho de 2013, box do Samba](https://www.bcb.gov.br/content/ri/relatorioinflacao/201306/RELINF201306-ri201306b6p.pdf); [um modelo semiestrutural simples](https://coolassessor.substack.com/p/um-modelo-semiestrutural-simples); [Blog do IBRE sobre o efeito da SELIC](https://blogdoibre.fgv.br/posts/deve-o-bc-reduzir-selic-replica-jose-julio-senna).

**Entregue em 05/11.** Decidido com a Lilo na implementação: (1) o efeito na inflação mede o desvio da história, 0,3 × (juro real da história − juro real da partida), como o crescimento (D20); o neutro de 5% fica para a credibilidade, os avisos e os grupos. (2) O efeito vale nos dois modos: no Banco Central autônomo, a reação de 1,5 ponto de SELIC por ponto de IPCA passa a trazer a inflação de volta. (3) Os grupos reagem ao juro real com a faixa de 2% a 7% em toda partida, no lugar do fator da SELIC nominal contra 10%. (4) A reunião não pausa o jogo: o presidente marca a decisão antes, ela vale do dia seguinte à reunião, uma pendência avisa nos 7 dias anteriores sem decisão, sem decisão a SELIC fica, e o presidente do computador decide como o Banco Central autônomo, dentro do teto. Até o primeiro presidente de jogador tomar posse, o Banco Central decide como na história. A credibilidade perde 4 por ponto de juro real abaixo do neutro (até 20 por reunião) com o IPCA acima da meta e ganha 3 a cada alta; em 0, soma 2 pontos ao prêmio da dívida e dobra o efeito, que chega mais cedo. A janela da reunião parte da SELIC efetiva guardada (13,65% com a meta em 13,75%) e vai nos passos de 0,25 dentro do teto. Card do governo na aba Contas e escolha no lobby; retrato do card no canvas. Fica para o playtest: calibrar o 0,3, a perda de credibilidade e a faixa dos grupos; e mostrar a escolha da SELIC no resumo do lobby.

### F165 · arquivado em 2026-11-07

*Kanban:* Tela do Tesouro: títulos pelo risco do governo · Feature · ✅ Concluído · atende N34 · marco M21

**F165 — Tela do Tesouro: títulos pelo risco do governo.** Serve N34. Com o prêmio de risco (F128), a taxa dos títulos conta a história do governo: sobe quando a dívida cresce. Hoje o Tesouro sai misturado na vitrine mensal da renda fixa, sorteado como os títulos dos bancos e com o prêmio somado à taxa (`fixed_income/factory/__init__.py`). (1) **O Tesouro sai da renda fixa e ganha item próprio** no menu Mercado, logo abaixo de Renda fixa; a renda fixa fica com CDB, LCI e LCA, no sorteio de hoje, e aponta para o Tesouro. (2) **Catálogo fixo, como o Tesouro Direto:** seis títulos sempre à venda, numa escada de prazos: um Selic de uns 3 anos, dois Prefixados (uns 3 e uns 7 anos) e três IPCA+ (uns 5, 10 e 20 anos), com vencimento em datas fixas (Selic em 1º de março, Prefixado em 1º de janeiro, IPCA+ em 15 de maio). No fechamento do ano, o título cujo prazo caiu abaixo do piso do degrau sai da vitrine e entra o seguinte da escada (ex.: o Prefixado 2029 dá lugar ao Prefixado 2032); quem comprou segue com ele na carteira. Quem quer reinvestir no mesmo título o acha por anos. (3) **Taxa revista todo mês, sem sorteio**, no fechamento, junto com o prêmio: Selic = SELIC + 0,10 + prêmio; Prefixado = SELIC − 1 + 0,15 por ano de prazo + prêmio; IPCA+ = IPCA + (SELIC − IPCA + 0,10 por ano de prazo + prêmio). Quem compra trava a taxa do dia; duas compras do mesmo título em meses diferentes são duas posições. (4) **A tela mostra** os títulos à venda, com a taxa aberta em "taxa base + prêmio de risco do país" e a compra dali mesmo; a taxa de cada tipo ao longo da partida, em "equivale hoje" (% ao ano, com o IPCA de 12 meses no IPCA+), com a dívida pública ÷ PIB no mesmo eixo de tempo; e o termômetro do risco: o prêmio atual, a dívida ÷ PIB e quanto falta para a próxima faixa. As faixas são só de leitura, a fórmula do prêmio segue contínua: Sem prêmio (até 50% do PIB), Moderado (50% a 80%), Alto (80% a 100%) e Crítico (acima de 100%); a dica da dívida ÷ PIB passa a usar as mesmas faixas. Cada métrica tem uma descrição curta e uma dica com a definição e como ler. Para o gráfico, o backend guarda a taxa de cada título e o prêmio em cada fechamento de mês. (5) Sem a expansão Governo & Política, a tela existe com a taxa base, sem prêmio e sem termômetro. A marcação a mercado (F177) se faz junto: o desenho das duas está no canvas, na linha do Tesouro.

### F177 · arquivado em 2026-11-07

*Kanban:* Marcação a mercado do Tesouro · Feature · ✅ Concluído · atende N34 · marco M21

**F177 — Marcação a mercado do Tesouro.** Serve N34; feita junto com a tela do Tesouro (F165), no mesmo desenho do canvas. Na vida real, quem compra um Prefixado e vê as taxas subirem perde dinheiro se vender antes do vencimento: um título de 12% ao ano vale menos quando o mercado paga 15%, porque ninguém paga o mesmo preço por 12% podendo ter 15%. Os títulos do Tesouro ganham resgate antes do vencimento, em qualquer dia, inteiro ou em parte: o Selic pelo valor acumulado, o Prefixado e o IPCA+ pelo preço de hoje, o valor no vencimento trazido a valor presente pela taxa de hoje do mesmo título (o catálogo da F165 é fixo, então o título vendido é o mesmo que está à venda). O Tesouro recompra pela mesma taxa em que vende, sem diferença; o ganho ou a perda vem só da taxa ter mudado desde a compra. IR regressivo sobre o ganho, como no vencimento; com perda, sem IR. Como a taxa muda no fechamento do mês, o preço anda todo dia pelo tempo e salta no fechamento. A tela do Tesouro lista os títulos do jogador com a taxa da compra, a de hoje, o valor de hoje, a marcação e o valor no vencimento, e a venda mostra o que se recebe hoje ao lado do que se receberia esperando; a carteira mostra o ganho ou a perda da marcação ao lado do rendimento. O risco do governo fica palpável para quem investe, e o presidente com Prefixado na carteira perde com a própria gastança. Mexe na renda fixa toda (`liquidity.py`, `fixed_broker.redeem`), que hoje só resgata antes do vencimento o que tem liquidez diária.

### F191 · arquivado em 2026-11-07

*Kanban:* Economia interligada: bolsa, PIB, IPCA, SELIC, desemprego e dívida · Feature · ✅ Concluído · atende N34 · decisões D20 · marco M21 · dependência de F194

**F191 — Economia interligada: bolsa, PIB, IPCA, SELIC, desemprego e dívida.** Serve N34; condicionado por D20. A economia da partida passou a ser a história mais o desvio que o governo causa. Cada fechamento de mês calcula a partida e a história lado a lado (`government/linked_economy.py`, o `LinkedEconomy`, chamado no tick antes dos preços do dia), e as ligações saem da diferença entre as duas (`economy/links.py`):
- **Curva de Phillips:** cada ponto de desemprego abaixo da história soma 0,35 ponto ao IPCA.
- **Risco fiscal:** cada ponto de prêmio acima da história soma 0,5 ponto ao IPCA, pesa na bolsa como um ponto de SELIC (−2,9%) e encarece o crédito na mesma medida.
- **PIB → bolsa e arrecadação:** cada 1% de PIB acima da história levanta a bolsa em 2,5% (pelo beta) e soma 0,06 ponto do PIB de receita.
- **Ciclo fiscal:** o seguro-desemprego custa 0,05% do PIB por ponto de desemprego acima da história, e o impulso fiscal (a piora do primário sem obras em 12 meses) soma metade ao crescimento.

O overlay das séries (`economy/layer.py`, `EconomyLayer`) soma os pontos do gasto e das ligações, e a reação do Banco Central (1,5 vez a inflação somada) virou a função única `central_bank_reaction`, que a SELIC do governo vai trocar. Cada mês fechado vale a partir do dia 1 do mês seguinte.

O crescimento do PIB e o desemprego viraram séries baixadas do SGS (PIB do IBGE em 4 trimestres e desocupação da PNAD Contínua), na Central de dados, e são a história da partida; o modelo cobre só onde não há dado. A dívida paga taxa mista (45% na SELIC do dia, 55% na média de 36 meses do que os títulos travaram) e o prêmio segue sem teto. O juro do mês passou a incidir sobre a dívida anterior. A dívida ÷ PIB reproduzida com a série da partida fecha: o resultado é nominal, e a razão anda pelo juro menos a inflação e o crescimento. O que a subia com SELIC baixa era o prêmio cobrado sobre a dívida inteira, que a taxa mista corrige. O painel agora abre a variação em juro, crescimento, inflação e primário.

Na tela de Economia, o cartão de efeitos lista medidas e ligações; o do crescimento mostra a série do IBGE mais as quatro parcelas (juro real, bolsa, obras, impulso); o do desemprego, a história mais o que a partida somou; o da dívida, a taxa média e de onde veio a variação de 12 meses. A seção "A economia interligada" do guia do governo explica tudo. O peso da bolsa no crescimento era 0,05 mesmo: o "5" do registro antigo era erro de digitação.

Limitação: as linhas das ligações no painel foram conferidas em teste automatizado, mas não numa partida com medidas aprovadas no app. O banco principal precisa da migration e de baixar as duas séries novas na Central de dados.

### F192 · arquivado em 2026-11-07

*Kanban:* Gerador de futuro: inflação por regime e horizonte em anos · Melhoria · ✅ Concluído · atende N12 · marco M21

**F192 — Gerador de futuro: inflação por regime e horizonte em anos.** Serve N12. O choque de inflação, que era um pulso no começo do futuro, virou dois controles: o nível (de −5 a +20 pontos, permanente: a SELIC sobe 1,5× na subida e assenta em 1×) e os surtos (frequência de 0 a 5 por década e intensidade de 2 a 20 pontos, sorteados por ano a partir da semente). O "Começar em" saiu. O "até quando" virou escolha de ano, com teto de 30 anos: a prévia de 30 anos leva 0,41 s, abaixo do 1 s que pediria um aviso, então não há aviso.

A prévia ganhou o crescimento do PIB e o desemprego, calculados mês a mês pelo modelo de `economy/growth.py` a partir da SELIC, do IPCA e da bolsa gerados, sem gravar nada. Na Central, o PIB e o desemprego aparecem com uma cor e uma legenda próprias, "calculado na partida", no trecho depois do dado real.

Decidido na revisão, em 06/11: no nível, a bolsa reage ao juro real (a SELIC acima da inflação somada), e não à SELIC inteira, e todo ativo recebe a inflação do nível no nominal, qualquer que seja o beta. Com +10, o Ibovespa descontada a inflação fica 13% abaixo do futuro sem nível no sexto mês e volta em uns 4 anos; em 10 anos a bolsa real fica parecida em qualquer nível. O alvo do crescimento do PIB passou a descontar a inflação da bolsa, como já descontava do juro, na partida e na prévia: com +10, o PIB cai na transição e, depois de 10 anos, fica a menos de 0,5 ponto do PIB sem nível. O tempo do nível e dos surtos conta os pregões do calendário gerado (260,9 por ano), para que um ano deles seja um ano do IPCA mensal. Fica para o playtest: arrastar o slider do nível no navegador e ver a prévia reagir.

### F196 · arquivado em 2026-11-07

*Kanban:* Evolução do patrimônio por tipo de renda variável · Melhoria · ✅ Concluído · atende N16

**F196 — Evolução do patrimônio por tipo de renda variável.** Serve N16. Hoje a evolução do patrimônio (`portfolio/components/networth-chart.tsx`) tem as visões "Ganho" e "Por classe", que separa renda fixa, renda variável e caixa, um painel por classe. O playtest de 31/out pediu ver a renda variável aberta por tipo.

**O que muda:** uma visão "Por tipo", ao lado de "Por classe", com um painel por tipo de renda variável (Ações, FII, ETF, BDR e Cripto) no mesmo estilo dos painéis de hoje; o tipo que a carteira nunca teve não ganha painel. O backend soma a série da carteira pelo tipo do ativo, que já está no cadastro, no mesmo endpoint da visão por classe. Sem rodada no canvas: o layout é o da visão por classe.

### F216 · arquivado em 2026-11-07

*Kanban:* Pontas soltas das features entregues · Correção · ✅ Concluído · atende N15, N34 · marco M21

**F216 — Pontas soltas das features entregues.** Serve N15 e N34. Perguntas que ficaram abertas em features já concluídas e arquivadas, decididas uma a uma em 05/nov. Três viram conserto aqui. (1) **Governo do computador eleito:** o partido do computador que vence a eleição toma posse sem presidente (`state.py`, `pending_term` com `president_id` nulo), e `caretaker()` em `government_book.py` só reconhece o computador que assume por impeachment sem vice (`term.succession`); o mandato eleito passa quatro anos sem medida. O conserto é `caretaker()` (e com ele `governs()` e `_propose_as_caretaker`) valer para todo mandato de partido do computador sem presidente, eleito ou herdado; teste de que o computador eleito propõe com a fila vazia. (2) **Parcela com o jogador negativado:** reproduzir no app de teste (banco de teste, backend 8100 e Vite 5273) a parcela que vence sem caixa, o selo "Negativado", a pendência de atraso e o pagamento por ela, conferindo caixa, multa, juros de atraso e a pendência que some; o backend já tem os testes em `test_credit_book.py`, e o bug que aparecer na tela é consertado aqui. (3) **Logs do bot e da estratégia:** `bot-log-sheet.tsx` e `strategy-log.tsx` trocam o texto fixo "A conexão com a partida caiu…" pela mensagem de erro do servidor, como nas páginas do governo. Ficam assim, decididas: o artigo masculino antes da sigla do partido ("ao ACI"), que é o uso comum para sigla; o erro único por página em Governo, Eleição e Economia, que leem o painel numa consulta só; as cinco peças do board da Campanha que o app não tem (passo "Rival" desabilitado, tabela "Comício: extremos dobrados", cartões de reparação, "O que a manchete conta" e do partido do computador), e o board deixa de ser referência para elas; as manchetes novas como estão escritas; o clique no interruptor do Especialista com o Personalizado ativo, que segue aplicando direto; e a meta de 250 pontos da nota de craque. Os marcadores de notícia no gráfico de preço, que não têm board, ficam na F167. Gatilho: a 3.4, na posição do plano.

### F217 · arquivado em 2026-11-07

*Kanban:* Correções da 3.4 · Correção · ✅ Concluído · atende N15 · marco M21

**F217 — Correções da 3.4.** Lote dos consertos achados no playtest de 04/11, em main, em `fix:`:
- (1) **Log das ordens do bot** (`statistics-report/bot-log-sheet.tsx`): o painel tem 520 px e a tabela não quebra linha (`whitespace-nowrap` em `ui/table.tsx`), então rola na horizontal. Alargar o painel e deixar as colunas de texto quebrarem; a comparação com uma partida de versão antiga pelo navegador mostra como era.
- (2) **Radar na aba Partido da preparação** (`preparation/party-found-tab.tsx`): o mesmo `ProfileRadar` da tela de fundar partido no jogo (`flags-picker.tsx`).
- (3) **Pendências sempre na barra lateral** (`pending-menu-item.tsx`): o item aparece também sem pendência, e o clique abre "Sem pendências".
- (4) **Selo de pausa só "Pausado"** (`layouts/partial/topbar.tsx`), com o motivo numa dica ao passar o mouse.
- (5) **Jornal rola a página inteira** (`journal-paper.tsx`): a lista deixa de ter rolagem própria, e o "Arquivo da partida" fica fixo na lateral como navegação.
- (6) **Estratégias repetem a ordem:** o comprar e segurar, e outras, tenta comprar todo dia que tem caixa para uma cota (`buy_and_hold.py`), e cada recusa vira uma linha de erro no log (`runner._execute`). Reproduzir, achar o motivo da recusa e fazer as estratégias esperarem em vez de repetir.
- (7) **Selects de jogador e partido com avatar e marca**, na lista e no valor escolhido: candidato e vice em `ticket-dialog.tsx` e `party-found-tab.tsx`, com `PlayerOption` e `PartyMark`.

### F218 · arquivado em 2026-11-07

*Kanban:* Textos que explicam o óbvio ou o sistema por dentro · Melhoria · ✅ Concluído · atende N15 · marco M21

**F218 — Textos que explicam o óbvio ou o sistema por dentro.** Serve N15. Cortados os textos das telas que o jogador vê e aprovou no app: o card de novo empréstimo, o card do partido, as telas de eleição e orientação do partido e a tela de governo antes da posse. Os diálogos e as telas que a varredura listou e não foram revisados no app ficaram como estão, sem corte.

### F219 · arquivado em 2026-11-07

*Kanban:* Terminal do backend sem o aviso do pandas do yfinance · Correção · ✅ Concluído · atende N26 · marco M21

**F219 — Terminal do backend sem o aviso do pandas do yfinance.** Serve N26. Achado no playtest de 05/11: o yfinance, ao baixar as séries, disparava `Pandas4Warning` (o parâmetro `inplace` em `DataFrame.drop`, `rename` e `sort_index`) a cada download, e o aviso entupia o terminal do backend. A 1.8.0, que não usa mais `inplace`, exige o curl-cffi 0.17, que trava toda requisição até o timeout; o yfinance ficou na 1.7.0, com o curl-cffi limitado abaixo da 0.17, e o aviso é filtrado só quando vem do código do yfinance, no `main.py`.

### F222 · arquivado em 2026-11-07

*Kanban:* Resgate automático de renda fixa para cobrir despesas · Feature · ✅ Concluído · atende N34 · marco M21

**F222 — Resgate automático de renda fixa para cobrir despesas.** Serve N34; vem junto com a tela do Tesouro (F165) e a marcação a mercado (F177). Hoje o caixa que não cobre a despesa do mês, o imposto de renda ou a parcela do empréstimo vira cheque especial ou parcela atrasada, mesmo com dinheiro parado na renda fixa. A regra nova põe uma porta só para os débitos automáticos, `SimulationEngine.cover_before_debit(client, needed, kind)`: se o caixa é menor que o necessário, ela vende títulos antes de debitar, na ordem (1) liquidez diária e Tesouro Selic, da menor taxa para a maior, e (2) só com a opção ligada, Prefixado e IPCA+, do que perde menos (ou ganha mais) para o que perde mais na marcação. Se não der para cobrir tudo, cobre o que dá; a venda é ação do sistema e não passa por `_ensure_can_operate`. Passam pela porta: despesa mensal e imprevisto do viver de renda, DARF, parcela de empréstimo (antes do teste de caixa, para a parcela não atrasar com saldo em renda fixa) e a contribuição mensal automática da campanha; o juro do cheque especial fica de fora, porque é consequência de não ter coberto. Cada resgate vira um toast para o jogador (`ToastType.AUTO_REDEEM`): "Resgatado R$ X de <título> para cobrir <despesa>". A opção `cover_with_treasury` (desligada por padrão) mora nas preferências do usuário, com o interruptor no cabeçalho de "Seus títulos" da tela do Tesouro. `overdraft_cover` e a ação de cobertura do card de vida saem; o card passa a mostrar uma linha dizendo se a cobertura está ligada, com link para o Tesouro.

**Aceite:** ordem de resgate coberta por teste; opção desligada não vende Prefixado nem IPCA+; cobertura parcial; parcela de empréstimo coberta antes de atrasar; toast emitido; testes em `tests/test_auto_cover.py`.

### F223 · arquivado em 2026-11-07

*Kanban:* Credibilidade do Banco Central medida contra a história · Correção · ✅ Concluído · atende N34 · decisões D20 · marco M21

**F223 — Credibilidade do Banco Central medida contra a história.** Serve N34; condicionado por D20. **Sintoma:** na partida com a SELIC nas mãos do governo, um presidente que marca exatamente a SELIC da história em toda reunião perde credibilidade sem ter feito nada diferente. Simulada de 2001 a 2025, ela cai para 32 em 2012–2013, fica presa perto de 55 de 2016 a 2018, zera em dezembro de 2019 e fica em 0 até 2021. Com 0, a dívida paga 2 pontos de prêmio a mais, o que soma cerca de 1 ponto ao IPCA pelo risco fiscal, tira cerca de 5,8% da bolsa no trimestre e dobra o efeito do juro real na inflação. Com o Banco Central autônomo, a mesma janela fica em 100. **Reproduzir:** aplicar `next_credibility` às reuniões de `meeting_days` de 2001 a 2025, com a SELIC e o IPCA guardados. **Causa** (`next_credibility` em `backend/features/economy/monetary.py`, chamada por `_hold_selic_meeting` no `government_book.py`): (1) compara o juro real com o neutro fixo de 5%, e não com o juro real da história no mesmo dia, e cobra de novo o que a série real já contém, contra a D20; (2) só devolve credibilidade com alta da SELIC, e entregar a inflação na meta nunca a reconstrói (em 2016–2018 o IPCA caiu de 10,7% para 2,5% e a credibilidade não voltou); (3) dispara com o IPCA acima da meta, e não acima da meta mais a tolerância (em dezembro de 2019, 4,31% contra a meta de 4,25%, dentro da tolerância de 1,5 ponto, tirou 15,8 pontos). **Conserto:** (1) a reunião tira credibilidade quando o juro real da partida fica abaixo do da história (SELIC e IPCA guardados no dia) e o IPCA em 12 meses da partida passa da meta mais a tolerância: 4 pontos por ponto abaixo da história, até 20; (2) devolve 3 quando sobe a SELIC ou quando o juro real da partida fica igual ou acima do da história; (3) `_hold_selic_meeting` passa o juro real da história e a `inflation_tolerance` do dia. Os testes da credibilidade e o trecho da credibilidade em `docs/docs/como-usar/governo.md` mudam junto. **Aceite:** um presidente que copia a SELIC da história de 2001 a 2025 termina toda reunião com credibilidade 100. **Gatilho:** agora, antes do release da 3.4.

### F224 · arquivado em 2026-11-07

*Kanban:* Primário que estabiliza a dívida no painel da Economia · Feature · ✅ Concluído · atende N34, N41 · decisões D20 · marco M21

**F224 — Primário que estabiliza a dívida no painel da Economia.** Serve N34 e N41; condicionado por D20. Hoje o painel da Economia mostra a dívida/PIB, a taxa média que ela paga e o que a moveu nos últimos meses (juros, crescimento, inflação e primário, em `debt_summary` de `backend/features/economy/panel.py`), mas não diz quanto superávit seguraria a dívida parada. O jogador passa a ver, ao lado do resultado primário, o **primário que estabiliza a dívida**: o superávit, em % do PIB, que mantém a dívida/PIB no mesmo lugar. A conta é s = d × (r − g) / (1 + g), com d a dívida/PIB, r a taxa nominal média que a dívida paga (a mista, que `budget.debt_rate` já calcula) e g o crescimento nominal do PIB em 12 meses (o crescimento real da partida mais o IPCA). Exemplo: dívida de 80% do PIB, taxa de 12% e PIB nominal crescendo 8% pedem 0,8 × 0,04 / 1,08 ≈ 3,0% do PIB de superávit; com um primário de 1%, a dívida sobe cerca de 2 pontos do PIB por ano. A linha mostra os dois números e a diferença em palavras ("faltam 2,0 pontos do PIB de superávit para a dívida parar de subir"), com o número da história ao lado, que é a régua da D20. A dica traz a definição, o exemplo e o que é bom e ruim: primário acima do que estabiliza faz a dívida cair; abaixo, ela sobe, e com r acima de g sobe sozinha, que é a espiral da dívida. **Mecanismo:** função pura `stabilizing_primary(debt, rate, nominal_growth)` em `backend/features/economy/`, no molde da de `backend/domain/debt.py` do [EconomicStatistics](https://github.com/LiloMarino/EconomicStatistics); o `DebtSummaryDTO` ganha o primário que estabiliza da partida e o da história, e o `pnpm openapi` regenera os tipos do front. **Gatilho:** depois da credibilidade medida contra a história, antes do release da 3.4.

### F228 · arquivado em 2026-11-07

*Kanban:* Gasto do governo contado uma vez só na inflação · Correção · ✅ Concluído · atende N34 · decisões D20 · marco M21

**F228 — Gasto do governo contado uma vez só na inflação.** Serve N34; condicionado por D20. Uma medida de gasto chega à inflação por dois caminhos. O direto é `INFLATION_PER_STEP` em `backend/features/government/spending_effects.py`: cada passo de auxílio ou de reajuste de aposentado soma 0,25 ponto ao IPCA de 12 meses, o de servidor 0,20 e o de obras 0,15. O indireto passa pelo resto da economia. O gasto piora o primário, e o impulso fiscal (`IMPULSE` em `backend/features/economy/links.py`) empurra o PIB. As obras ainda somam PIB direto, por `GROWTH_PER_STEP`. O PIB maior baixa o desemprego pela lei de Okun (`OKUN` em `growth.py`), e o desemprego abaixo do normal soma inflação pela curva de Phillips (`PHILLIPS` em `links.py`). Se o passo direto foi pensado como o efeito inteiro, o indireto conta o mesmo gasto duas vezes. A estimativa, sem medição, é de 10 a 20% a mais. **Mecanismo:** script de CLI no molde de `.claude/trabalho/economia/calibrate.py`, sobre o banco de teste. Ele roda a mesma partida com e sem o caminho indireto (com o impulso e o PIB das obras zerados) para um passo de cada medida e mede, mês a mês por 36 meses, quanto de IPCA cada caminho soma. Se o indireto passar de 20% do direto no pico, `INFLATION_PER_STEP` é descontado até o total voltar ao valor de hoje, e o teste da medida passa a conferir o total. Abaixo disso, fica como está e entra como simplificação na página da docs sobre gasto e inflação. **Aceite:** a medição registrada com o número de cada medida, e o IPCA somado por um passo, pelos dois caminhos juntos, dentro de 10% do valor de `INFLATION_PER_STEP`. **Gatilho:** depois do primário que estabiliza a dívida, antes da calibragem da partida longa. **Medição:** `.claude/trabalho/economia/measure_f228.py`, sobre o banco de teste, um passo de cada medida vigente em janeiro, 36 meses, com e sem o impulso fiscal e o PIB das obras (o `MacroCourse` com os dois zerados); quatro partidas (2006, 2011, 2016 e 2021) deram o mesmo resultado dentro de meio ponto percentual. No mês em que o efeito direto enche (o 6º), o indireto soma ao IPCA 0,009 ponto no auxílio (3,5% dos 0,249 do direto), 0,002 nos servidores (0,9% de 0,199), 0,004 nos aposentados (1,7% de 0,249) e 0,013 nas obras (8,8% de 0,149). A soma dos dois caminhos no pico fica em 102,4% a 103,1% de `INFLATION_PER_STEP` no auxílio, 99,9% a 100,5% nos servidores, 100,7% a 101,3% nos aposentados e 107,3% a 108,5% nas obras, todas dentro dos 10% do aceite. Aos 24 meses o direto caiu a cerca de um terço do pico e o indireto, que chega devagar pelo desemprego, ficou em 0,033 no auxílio (0,083 de direto), 0,012 nos servidores (0,067), 0,029 nos aposentados (0,083) e 0,090 nas obras (0,050); nas obras ele ainda sobe aos 36 meses (0,113), porque o PIB a mais deixa o desemprego abaixo da história sem voltar. **Decisão:** o indireto fica abaixo dos 20% do direto no pico, então `INFLATION_PER_STEP` não muda e o número do passo vale como o efeito total; o indireto tardio das obras vai para a calibragem da partida longa. A simplificação entrou no trecho do gasto de `docs/docs/como-usar/governo.md`.

### F229 · arquivado em 2026-11-07

*Kanban:* Calibragem da economia numa partida de 10 anos · Spike · ✅ Concluído · atende N34 · decisões D20 · marco M21

**F229 — Calibragem da economia numa partida de 10 anos.** Serve N34; condicionado por D20. Mediu a partida longa com um presidente jogando, de jan/2001 a dez/2010, sobre o banco de teste, com os scripts `calibrate10.py`, `analyze10.py` e `report10.py` em `.claude/trabalho/economia/`. Cinco presidentes roteirizados rodaram, cada um com a SELIC do presidente e com o Banco Central autônomo: o que copia a história, o gastador, o gastador que corrige, o austero e o alternado. **Rodada 1:** achou dois defeitos, que viraram correções na 3.4: o desemprego da partida que nunca voltava ao normal e o teto da SELIC do presidente preso à inflação. **Rodada 2, depois das correções:**
- **Quem copia a história:** fica a até 0,2 ponto da série real no IPCA, no desemprego e no prêmio, e a 0,12 ponto da SELIC em todas as 80 reuniões. A dívida termina 1,2 ponto do PIB acima, por arredondamentos que se somam em 10 anos.
- **Gastador:** inflação +11 pontos e credibilidade a zero. A dívida cai pelo imposto inflacionário.
- **Gastador que corrige:** o IPCA volta à história em 19 meses e a credibilidade volta a 100 em 44 meses.
- **Austero:** o desemprego volta a menos de 1 ponto em 44 meses. A dívida sobe porque o roteiro também sobe a SELIC; com o Banco Central autônomo, tudo anda na direção certa.
- **Gastador com Banco Central autônomo:** entra na espiral da dívida, a consequência de um rombo permanente.

O único ponto implausível é o gastador que nunca para, que cresce no teto do jogo com um rombo de 22,7% do PIB. Ele virou o card do crescimento que sente o rombo do governo. O relatório completo está em `.claude/trabalho/economia/calibragem-10-anos.md`.

### F230 · arquivado em 2026-11-07

*Kanban:* Desemprego da partida volta devagar ao normal da época · Correção · ✅ Concluído · atende N34 · decisões D20 · marco M21

**F230 — Desemprego da partida volta devagar ao normal da época.** Serve N34; condicionado por D20. Hoje, em `next_month` de `backend/features/economy/growth.py`, o desvio do desemprego só muda pela lei de Okun: cada ponto de crescimento acima da história baixa o desemprego em 0,5 ponto por ano. Nada fecha esse desvio, então ele fica para sempre. Na calibragem de 10 anos, um presidente austero deixou o desemprego 5,5 pontos acima da história sem volta, mesmo com o PIB crescendo igual ao da história. As obras, pelo mesmo motivo, deixam o desemprego baixo por anos e seguem somando inflação pela curva de Phillips (0,092 ponto de IPCA aos 24 meses contra 0,050 do efeito direto). Na economia real o desemprego volta à taxa natural, a que sobra sem a economia aquecida nem em recessão, e no jogo a história faz esse papel (D20). No Brasil a volta foi lenta: de 13,7% em 2017 para perto de 9% em 2022. O que o jogador fez continua na dívida, na folha, na credibilidade e na bolsa; só o desvio do desemprego se fecha. **Mecanismo:** o desvio do mês passa a ser o do mês anterior vezes um fator de volta, menos o termo de Okun de hoje. A constante `UNEMPLOYMENT_HALF_LIFE_MONTHS` em `growth.py` começa em 24 meses, ajustada por CLI para que um desvio de 5 pontos caia abaixo de 1 ponto em cerca de 5 anos. O teste da partida longa em `tests/` confere a volta. Na mesma entrega, a medição do gasto pelos dois caminhos da inflação roda de novo para as obras (os scripts estão em `.claude/trabalho/economia/measure_f228.py`). A frase de `docs/docs/como-usar/governo.md` sobre o indireto das obras "seguir crescendo" sai, e o parágrafo da economia interligada ganha a volta do desemprego. **Aceite:** austero com SELIC do presidente, depois de parar, com o desvio do desemprego abaixo de 1 ponto em até 5 anos; IPCA somado pelas obras, nos dois caminhos, dentro de 20% do passo aos 24 meses. **Medição:** `UNEMPLOYMENT_HALF_LIFE_MONTHS` ficou em 36 meses, não nos 24 do plano: com 24 o desemprego voltava tão depressa que as obras somavam 0,116 de IPCA aos 24 meses (77% do passo de 0,15, fora dos 20% do aceite); com 36 somam 0,123 e 0,121 (partidas de 2006 e de 2016, 82% e 81% do passo), e com 48 o austero deixaria 1,5 ponto de desvio no quinto ano. O austero com SELIC do presidente (`.claude/trabalho/economia/calibrate10.py`, 2001 a 2010) chegou a 3,1 pontos de desemprego acima da história em jan/2005, quando parou, e ficou em 2,6 pontos um ano depois, 1,6 três anos depois e 0,94 cinco anos depois (antes não voltava: +5,5 no fim). Nas obras, aos 24 meses, o direto é 0,050 e o indireto 0,073 (2006) e 0,071 (2016), contra 0,090 antes; aos 36 meses a soma é 0,083 e 0,099 (antes o indireto ainda subia). No pico (6º mês) os demais gastos seguem como na medição anterior: o indireto soma 3,4% do direto no auxílio, 0,8% nos servidores, 1,6% nos aposentados e 8,5% nas obras. **Decisão:** a meia-vida de 36 meses é a menor que fecha os dois aceites; um desvio isolado de 5 pontos leva cerca de 7 anos para cair abaixo de 1 ponto, mais lento que a estimativa do plano, mas o desvio que um mandato realmente deixa (3 pontos no austero) fecha em 5. A frase do indireto das obras que seguia crescendo saiu de `docs/docs/como-usar/governo.md`, e o parágrafo da economia interligada ganhou a volta do desemprego.

### F231 · arquivado em 2026-11-07

*Kanban:* SELIC do presidente livre até 3 pontos por reunião · Melhoria · ✅ Concluído · atende N34 · decisões D20 · marco M21

**F231 — SELIC do presidente livre até 3 pontos por reunião.** Serve N34; condicionado por D20. Hoje, com a SELIC nas mãos do governo, cada reunião move no máximo 0,75 ponto, ou 1,5 com o IPCA acima do teto da meta e 3 com ele acima de 15% (`meeting_cap` em `backend/features/economy/monetary.py`). Essa é a regra de um Banco Central de verdade, imposta a um presidente que tirou a autonomia dele. Ela também impede copiar a história: o Copom real subiu 3 pontos em out/2002, com o IPCA perto de 8%, e cortou 1,5 em 2009, dentro da meta. Na calibragem de 10 anos, quem copiou a história ficou até 4,4 pontos de SELIC longe dela. A SELIC passa a ser estratégia do presidente: o limite vira um teto fixo de 3 pontos por reunião, para cima e para baixo, a maior alta do Copom desde 1999, sem depender da inflação. O custo de "meter o louco" vem do mercado e não da regra: a credibilidade já cobra de quem segura o juro real abaixo da história, e o mercado que reage à surpresa (4.3) cobrará de quem surpreende. **Mecanismo:** a janela da reunião é a SELIC guardada mais ou menos `PRESIDENT_CAP = Decimal("0.03")` (3 pontos, em passos de 0,25) e sempre inclui a SELIC da história no dia (passo mais próximo), por mais que ela tenha andado desde a reunião anterior: o piso é o menor entre a SELIC menos 3 pontos e a da história, o teto é o maior entre a SELIC mais 3 pontos e a da história, sem passar de zero. `cap_window` e `within_cap` em `backend/features/economy/monetary.py` recebem a SELIC da história como argumento; `meeting_cap` e as constantes `NORMAL_CAP`, `TOLERANCE_CAP`, `CRISIS_CAP` e `CRISIS_INFLATION` saem; `selic_cap` e `selic_history` em `backend/features/government/government_book.py` alimentam a janela do `set_selic` e do bot presidente, e o cartão monetário (`MonetaryDTO`) ganha `history_selic` para o controle da tela. O passo de 0,25 ponto e o calendário de 8 reuniões ficam. Os testes do teto passam a conferir a janela de 3 pontos com qualquer IPCA e o alcance da história, e a seção "O teto por reunião" de `docs/docs/como-usar/governo.md` (e a frase das fontes) é reescrita. O Banco Central autônomo não muda. **Aceite:** o presidente que copia a história fica dentro de 0,25 ponto da SELIC real em todas as reuniões de 2001 a 2010. **Medição:** só com o teto de 3 pontos, 2 das 80 reuniões ficavam fora de 0,25 (dez/2002, com a história 0,9 ponto abaixo da janela, e set/2003, 1,41 ponto), porque a história andou mais de 3 pontos entre duas reuniões; com a história sempre dentro da janela, as 80 reuniões de 2001 a 2010 ficam dentro de 0,25 ponto, com o maior desvio em 0,12 ponto (ago/2004, 16,00% contra 15,88%), a diferença do arredondamento ao passo de 0,25.

### F164 · arquivado em 2026-11-07

*Kanban:* Mapa do Brasil por região e por estado · Feature · ✅ Concluído · atende N34 · decisões D19 · marco M23 · dependência de F176

**F164 — Mapa do Brasil por região e por estado.** Serve N34. Uma página Mapa no menu, logo abaixo de Eleição, com o Brasil dividido por região ou por estado e visto por lentes, no molde dos mapas do Victoria 3: quem lidera, desempenho de um partido, variação desde a pesquisa anterior, rejeição de um partido, aprovação do presidente e onde vive cada grupo de eleitores (degradê, um grupo por vez). As lentes ficam num painel fixo à esquerda, com Região | Estado no topo; à direita, o lugar escolhido (intenção com a variação, quem vota ali) e a lista dos estados, que é a alternativa acessível ao mapa. O mesmo componente volta pequeno na Corrida, no card de aprovação do Governo e no dialog do resultado do turno, cada um com "Abrir no mapa". Pelo modelo da D19 um lugar é uma mistura de grupos de eleitores, então o voto e a aprovação por lugar saem do modelo sem mudá-lo. Cada um dos 27 estados tem a sua mistura, de dados públicos por UF: beneficiários do Bolsa Família (quem depende de auxílio), benefícios do INSS (aposentados), PNAD Contínua do IBGE (trabalhadores formais e servidores) e investidores da B3 (quem vive de investimento), com a fonte de quem empreende escolhida na implementação e citada no código. A região é a soma dos estados dela, pesada pelo eleitorado do TSE de 2022 (Sudeste 42,6%, Nordeste 27,1%, Sul 14,7%, Norte 8,1%, Centro-Oeste 7,5%). As misturas moram ao lado de `voters.WEIGHTS`, e a soma pesada fecha os pesos nacionais. A pesquisa mensal sai também por estado, cada um com a margem do tamanho da amostra (São Paulo ±3, Acre ±12); quando a diferença entre o 1º e o 2º cabe na margem, o lugar fica listrado nas duas cores (empate técnico). O mapa mostra só a pesquisa atual, com a variação desde a anterior; entre os turnos, só os dois finalistas. O resultado sai de uma vez, sem animação, e a frase diz o melhor e o pior lugar do partido em % dos votos válidos. Quem vence continua sendo o voto do país, e o Congresso continua nacional. O mapa vem sempre com Governo & Política, sem opção própria no lobby. O design aprovado está no canvas, com as lentes, os usos pequenos e os estados. O upgrade seguinte são as cadeiras por região (F176), que entram como mais uma lente, e, se valer, ações de campanha por região ("comício no Nordeste") na F130.

### F175 · arquivado em 2026-11-07

*Kanban:* Federações partidárias · Feature · ✅ Concluído · atende N34 · decisões D19 · marco M23

**F175 — Federações partidárias.** Serve N34. Na regra real (Lei 14.208/2021), dois ou mais partidos se unem e agem como um só por no mínimo 4 anos; a federação é diferente da chapa com vice de outro partido, que já existe e vale só para a eleição. Aqui: (1) **Formação:** um partido propõe a outro, no molde do convite de vice (`election.vice_blocker`, `government_book.answer_vice`), e a federação tem só 2 partidos. Num partido de jogadores, o fundador propõe e responde, e os filiados veem o aviso. Os partidos do computador também propõem (os abaixo da barreira, ao parceiro de bandeiras mais próximas) e respondem por regra; a proposta ao jogador chega no topo da Eleição e em Pendências. A proposta vale até 6 meses antes do 1º turno, o mesmo prazo da filiação para concorrer (F173), e cada partido tem uma proposta aberta por vez. (2) **Um partido só, por um mandato:** a federação dura até o fim do mandato que vem depois da eleição em que se formou. Nela há uma chapa presidencial, com o candidato que a proposta nomeia e o vice de qualquer partido federado; uma lista no Congresso, com os votos somados para a barreira de 5% e para o D'Hondt de `house.distribute`, e as cadeiras da federação repartidas entre os partidos dela pelo D'Hondt sobre o voto de cada um; e uma orientação, a do partido com mais cadeiras (sem cadeira ou com empate, a do partido que propôs). O parceiro pode desobedecer, com o custo normal da desobediência. As promessas da chapa são as do partido do candidato; as do parceiro saem sem custo no dia em que a federação se forma. Cada partido continua com a sua verba e as próprias ações de campanha, todas pela mesma chapa. (3) **O preço:** o partido pequeno escapa da barreira, mas perde o próprio candidato; os dois ficam presos pelo mandato e herdam, enquanto durar a federação, metade da rejeição que cada grupo de eleitores (D19) tem pelo parceiro. Sair antes do prazo desfaz a federação e impede quem saiu de se federar na eleição seguinte. (4) **Tela:** o design está no canvas: o botão de propor no cartão do seu partido e o dialog com o custo antes do clique (ganho na lista, chapa, orientação, promessas que saem, prazo e rejeição herdada por grupo, em números), o dialog de quem recebe, a federação como uma linha na pesquisa e um cartão em Partidos na disputa, o colchete das cadeiras dela no hemiciclo com a tabela da barreira, as manchetes de formada e desfeita no jornal, e os estados (proposta enviada, recusada, prazo encerrado, saída antes do prazo, desfeita, expansão desligada).

### F195 · arquivado em 2026-11-07

*Kanban:* Acordo de base até o fim do mandato · Feature · ✅ Concluído · atende N34 · marco M23

**F195 — Acordo de base até o fim do mandato.** Serve N34. Hoje o apoio de cada bancada vale 6 meses (`deals.TERM_MONTHS`) e se renova à mão; no playtest de 31/out isso virou tarefa repetida. A regra nova troca o prazo curto por uma negociação por mandato que um governo fraco perde:
- (1) **Duração:** o acordo vale até a véspera da posse seguinte (`term_end`). O preço é o de hoje (`SEAT_PRICE` por cadeira, 1,5 vez no centrão), pago por mês enquanto o acordo durar. O card da base perde o aviso "O acordo com o X acaba em…" e o "Propor de novo", e a coluna "Prazo" mostra o fim do mandato.
- (2) **Cobrança com o governo fraco:** quando o fechamento do mês deixa a aprovação abaixo de 35 (`FLOOR + RISK_MARGIN`, o mesmo ponto em que as Pendências mostram o risco de impeachment), cada bancada da base cobra 50% a mais. A cobrança fica 15 dias nas Pendências (`ANSWER_DAYS`) e no card da base: aceitar mantém o acordo, com o preço novo, até o fim do mandato; recusar ou deixar vencer tira a bancada da base sem contar como quebra do governo (sem a rejeição de `BREAK_REJECTION`).
- (3) **Uma cobrança por queda:** a bancada volta a cobrar só depois que a aprovação fechar um mês acima de 45 e cair de novo abaixo de 35, para a cobrança não virar a tarefa repetida que este card tira.
- (4) **Voltar à base:** a bancada que saiu pode ser chamada pela proposta de hoje; com a aprovação abaixo de 35, o preço da proposta já vem com os 50%.
- (5) **Jornal:** manchete quando uma bancada deixa a base por causa da aprovação ("O PP deixa a base do governo").
- (6) **Partida salva:** acordo já assinado vale até a data dele; os novos valem até o fim do mandato. O governo do computador continua sem negociar.

As constantes novas (o limite, os 50% e a volta acima de 45) moram em `deals.py`, ao lado das de hoje.

**Aceite:** um mandato inteiro sem renovar acordo; uma queda abaixo de 35 gera uma cobrança por bancada, uma vez só até a aprovação passar de 45; recusar tira a bancada sem a rejeição da quebra; testes em `tests/test_deals.py` e `tests/test_deals_book.py`.

### F22 · arquivado em 2026-11-08

*Kanban:* Preço bruto, desdobramentos e dividendos na partida · Feature · ✅ Concluído · atende N3, N7 · decisões D1, D3, D7, D12 · marco M22

**F22 — Preço bruto, desdobramentos e dividendos na partida.** Serve N3 e N7; segue a D1, a D3, a D7 e a D12. A importação do Yahoo Finance passou a `auto_adjust=False, actions=True`, e `features/import_data/corporate_events.py` reconstrói o preço bruto: cada pregão e cada dividendo é multiplicado pelo produto das razões dos desdobramentos com data ex posterior, e o volume é dividido por ele. Como toda atualização baixa o histórico inteiro, o bruto de um dia antigo não muda, e uma atualização depois de um 2:1 novo não cria queda de 50%. Desdobramentos e dividendos moram na tabela `stock_corporate_event` (data ex, tipo, razão ou valor por cota, origem e versão, no formato das séries da D7), com o repositório `corporate_event`; o congelar, o apagar e a troca do futuro gerado cobrem os eventos junto das séries. Na partida, `Simulation.next_tick` aplica os eventos da data ex antes de atualizar o mercado: o desdobramento muda a quantidade pela razão como evento `SPLIT` (o custo total fica, e o preço médio acompanha), a fração que sobra numa classe sem fração vira `FRACTION_SELL` ao close do dia (a cripto guarda a fração), as ordens abertas do ativo são canceladas e o dividendo entra no caixa como `DIVIDEND` com o ativo de origem (`event_cashflow.stock_id`), valor por cota vezes a quantidade da abertura, truncado ao centavo. O replay, as estatísticas, os setores, o imposto de renda e as conquistas leem `SPLIT` como mais quantidade e `FRACTION_SELL` como venda. O gerador do futuro calibra pelo retorno total (preço corrigido por desdobramento mais dividendos) e escreve o dividendo sintético na mesma tabela, com origem gerada e a mesma semente: o rendimento é a média dos últimos anos reais, com variação sorteada, nos meses do histórico; quem ficou 2 anos sem pagar continua sem pagar; a cripto não paga; e cada data ex gerada tira do preço o valor pago. Como não há banco anterior a converter, a migration é a da linha recomeçada da 4.0 mais a dos eventos, sem marca de série bruta. A F100 lê o `PlayerCorporateActions` que `apply_corporate_events` devolve.

### F100 · arquivado em 2026-11-08

*Kanban:* Proventos na carteira e nas telas · Feature · ✅ Concluído · atende N3, N7 · decisões D3 · marco M22 · dependência de F105

**F100 — Proventos na carteira e nas telas.** Serve N3 e N7; segue a D3. Continua a F22, que guarda os dividendos de cada ativo, reais e gerados, e os credita no caixa na data ex com o ativo de origem; aqui o provento passa a aparecer no jogo. O provento cai no caixa e nunca reinveste sozinho: o que fazer com o dinheiro é do jogador. As telas passam antes pelo canvas. Plano: (1) **Carteira:** o total de proventos recebidos aparece no resumo e, em cada posição, o rendimento (proventos dos últimos 12 meses sobre o valor da posição hoje), em Decimal (D3), com a dica do que ele mede e de como ler. (2) **Detalhe do ativo:** a tela do ativo ganha o histórico de proventos (data ex, valor por cota, total recebido pelo jogador). (3) **Estatísticas e fechamento:** o que entrou como provento soma ao relatório da partida e à decomposição do retorno. (4) **IR:** dividendo e rendimento de FII são isentos para pessoa física, e a regra do simulador trata todo provento como isento; o `yfinance` não separa o JCP (juros sobre capital próprio, com 15% retidos na fonte) do dividendo, e essa simplificação entra escrita na página de impostos dos docs. Gatilho: F22 concluída; sai com ela na 4.0 e destrava os rendimentos mensais da gestora (F105).
**Aceite:** num ativo que pagou dividendos, o total recebido na carteira bate com a soma dos créditos no caixa na data ex, e o rendimento da posição bate com a conta feita à mão.

### F220 · arquivado em 2026-11-08

*Kanban:* Jornal: voltar para hoje e edição destacada no arquivo · Melhoria · ✅ Concluído · atende N15 · marco M22

**F220 — Jornal: voltar para hoje.** Serve N15. Com a rolagem infinita do Jornal (a lista rola a página inteira, e o "Arquivo da partida" fica fixo na lateral), quem desceu muito pelas edições antigas só volta a hoje rolando de volta até o topo. O pedido do playtest de 05/11: um botão "Voltar para hoje" que aparece assim que a página desce da primeira edição, e um scroll spy que marca na lateral a edição que está na tela. A decisão em aberto é o desenho: onde o botão fica, o que o destaque do arquivo mostra e como os dois convivem com o carregamento de mais edições ao rolar. É tela nova, então vai ao canvas.

### F233 · arquivado em 2026-11-08

*Kanban:* Constantes de calendário unificadas no core · Manutenção · ✅ Concluído · marco M22

**F233 — Constantes de calendário unificadas no core.** Nasceu `backend/core/periods.py` com `BUSINESS_DAYS_PER_YEAR = 252` (movido de `core/indicators.py`), `CALENDAR_DAYS_PER_YEAR = Decimal("365.25")`, `MONTHS_PER_YEAR = 12` e `DAYS_PER_MONTH`, e a docstring afirma que dia útil é sessão da B3 e dia corrido é dia de calendário. O tesouro, as estatísticas (`risk`, `returns`, `score`), o gerador sintético, o futuro gerado, o orçamento de vida, os efeitos do governo e o crédito importam de lá; os cinco `MONTHS_PER_YEAR` e os dois `DAYS_PER_MONTH` locais saíram, e o literal `12` virou a constante. As janelas de "um ano de pregões" (`achievements/metrics.py`, `newsroom/companies.py` e `newsroom/newsroom.py`) usam `BUSINESS_DAYS_PER_YEAR`. O `synthetic.py` renomeou a régua de dias sem feriado para `WEEKDAYS_PER_YEAR` e a manteve local. `economy/layer.py` ganhou `months_to_days`, que converte meses em dias corridos no mês médio, e `statistics/risk.py` ganhou `VOLATILITY_ANNUALIZER` (√252) em Decimal. Ficaram como estavam as janelas ajustáveis que só coincidem com 252 (`strategy/momentum.py`, `base_strategy.py`) e o `MONTH_DAYS = 30` do crédito, que é outra convenção.

As regras da corrida à meta e de viver de renda, antes escritas duas vezes (no DTO e na requisição da rota), viraram `validate_goal` e `validate_independence` em `core/dto/simulation.py`, no padrão de `validate_government`; a requisição continua validando na entrada (422) e chama as mesmas funções do DTO.

Por fora nada mudou: os números exibidos são os mesmos, `pyright` e `pytest` passam sem nenhum valor esperado alterado.

### F234 · arquivado em 2026-11-08

*Kanban:* Juros compostos num módulo só · Manutenção · ✅ Concluído · marco M22

**F234 — Juros compostos num módulo só.** Nasceu `backend/core/rates.py`, só em Decimal, com `compound(rate, periods)` = (1+r)^n − 1, `period_rate(rate, periods)` = (1+r)^(1/n) − 1 e `compose(*rates)` = ∏(1+r) − 1, com teste próprio. Passam a chamá-las `credit/price.py` (taxa mensal e saldo do ciclo), `fixed_income/accrual.py` (`annual_to_daily_factor` virou `1 + period_rate(...)` e manteve o `lru_cache`; o spread composto virou `compose`), `economy/debt.py`, `government/budget.py` (a dívida e o PIB do mês), `simulation/life_events.py` (juro do cheque especial), `core/indicators.py` (`daily_rate` e `annualize_daily`) e `summaries/summary.py` (o composto dos meses, que tinha o seu `_compound`).

`annualize_growth` mudou de `statistics/returns.py` para `statistics/risk.py`, porque o `returns` já importa do `risk` e o `risk` precisava dela; o `returns` importa de lá e o `score.py` a chama como `risk.annualize_growth`. Com isso `risk.annual_return` e a nota anual do `score.py` deixaram de repetir a conta e o guarda de acumulado ≤ −100%. Os caminhos em float/numpy (`economy/layer.annual_to_daily` e os helpers do `synthetic.py`) ficaram com os helpers próprios; `to_annual` e `to_daily` do `synthetic.py` passaram a públicos e o `future.py` chama `to_annual` em vez de repetir a conta.

Por fora nada mudou: o resultado em Decimal é idêntico e nenhum valor esperado dos testes foi alterado.

### F235 · arquivado em 2026-11-08

*Kanban:* Tipo Percent no indicador do BCB · Manutenção · ✅ Concluído · marco M22

**F235 — Tipo Percent no indicador do BCB.** `Percent = NewType("Percent", Decimal)` e `from_percent(value: Percent) -> Decimal` moram em `core/rates.py`, com a afirmação de que o valor é como o BCB publica (0,0551 = 0,0551%). `index_value_on` devolve `Percent`; `daily_rate` e `annualize_daily` só aceitam `Percent`, e os `/ 100` de `core/indicators.py` e das tabelas de meta, tolerância, dívida bruta e resultado primário viraram `from_percent`. Como `last_known_value` também lê o IBOV, que é nível de índice em pontos, a leitura das taxas ganhou `last_known_rate` (CDI/SELIC/IPCA, devolve `Percent`) e `last_known_value` ficou só para as séries de nível; `accrual.py`, `economy/panel.py` e a checagem de cobertura migraram para `last_known_rate`. Onde a história é lida direto (`economy/panel.py`, `economy/layer.py`, `newsroom/macro.py`) o `Percent(...)` nasce na leitura, e os testes de `economy_layer` e `economy_panel` passam `Percent`. A chamada de prova com um `Decimal` cru em `annualize_daily` falhou no pyright e foi removida.

Por fora nada mudou: os valores são os mesmos; `pyright` e `pytest` passam sem nenhum valor esperado alterado.

### F236 · arquivado em 2026-11-08

*Kanban:* Prévia do impacto de preço fora da rota · Manutenção · ✅ Concluído · marco M22

**F236 — Prévia do impacto de preço fora da rota.** A conta da curva saiu de `routes/simulation.py` e virou `preview_curve(k, decay_days)` em `features/variable_income/price_impact.py`, junto de `impact()` e `decay()`, levando `PREVIEW_VOLUME_SHARE` e o volume médio fixo do exemplo (`PREVIEW_AVERAGE_VOLUME`, 1 milhão). A função devolve o impacto de cada pregão afetado, e a rota só chama `preview_curve` e monta o `PriceImpactPreviewDTO`. Um teste novo confere `preview_curve` contra `impact()` e `decay()`.

Por fora nada mudou: a resposta da rota é a mesma e o `docs/openapi.json` não mudou.

### F237 · arquivado em 2026-11-08

*Kanban:* Componentes do mercado na pasta da renda variável · Manutenção · ✅ Concluído · marco M22

**F237 — Componentes do mercado na pasta da renda variável.** `market-mark.tsx` e `scale-ruler.tsx` saíram de `shared/components/` e foram para `features/variable-income/components/`, a única feature que os usa (`order-book-card.tsx` e `indicator-selector.tsx`). `chart-scale.ts` e `tutorial-topic-ids.ts` ficam em `shared/`, porque também têm consumidores lá.

Por fora nada mudou: só os caminhos de import.

### F238 · arquivado em 2026-11-08

*Kanban:* Features do front sem import atravessado · Manutenção · ✅ Concluído · marco M22

**F238 — Features do front sem import atravessado.** Os padrões de vela passaram a ser compartilhados: `candle-patterns.ts`, `pattern-geometry.ts`, `pattern-view.ts` (com o seu teste) foram para `shared/lib/`, e `pattern-drawing.tsx` com o `pattern-drawing-animated.tsx` que ele carrega foram para `shared/components/candle-patterns/`. A geometria e o desenho animado subiram junto porque o desenho depende deles e nenhum outro código os usa; assim `shared/` não importa de feature. O resto de `candle-patterns/` (cartão, lista, controles) ficou em variable-income.

O minigame de candles desceu para dentro do lobby, o único que o usa: `features/candle-challenge/` virou `features/lobby/candle-challenge/`, com `components/`, `hooks/` e `lib/` preservados. O `lobby-button.tsx` do tutorial desceu para `lobby/components/`.

Dentro de `features/`, a única aresta entre features que sobra é a do tutorial para variable-income, aceita como exceção.

### F239 · arquivado em 2026-11-08

*Kanban:* Formatadores de percentual unificados · Manutenção · ✅ Concluído · marco M22

**F239 — Formatadores de percentual unificados.** `displayPercent` ganhou a opção `{ trim: true }`, que mostra casas só quando há (0,4 → "40%", 0,0025 → "0,25%"). O `chancePercent` do governo saiu e seus 4 usos viraram `displayPercent(x, 2, { trim: true })`; os três `formatPercent(Number(x) * 100, 1)` dos cards do mapa viraram `displayPercent(x, 1)`. O `formatPercent` ficou, porque é o formatador de pontos (52 = "52%"), unidade só do governo, e a docstring dele agora afirma isso.

Uma varredura das formatações à mão trocou mais cinco pontos por `displayPercent`: `percentLabel` (governo), o toast do 2º turno, `percentOf` do tesouro, as três linhas da ilustração de alavancagem do tutorial e `cashShare` do lobby. O texto exibido é o mesmo de antes.

Ficaram de fora, por não terem equivalente exato: `yearShare` (mínimo de 2 e máximo de 3 casas) e os formatadores de valores que já chegam na escala 0–100, ou sem o "%" (`pointsOf`, `signedPointsOf`, `pollPercent`, os de pontos percentuais do mapa).

### F240 · arquivado em 2026-11-08

*Kanban:* Badge de passo como variante do design system · Manutenção · ✅ Concluído · marco M22

**F240 — Badge de passo como variante do design system.** O círculo numerado do `Step` em `pyspy-card.tsx` era um `Badge` reimplementado com classes inline. O `Badge` ganhou `size="step"` (`size-5.5 px-0 font-semibold`) em `badgeVariants.ts`, e o `Step` passou a `<Badge variant="secondary" size="step">`.

O círculo de `measure-steps.tsx` ficou de fora: é outro selo, maior (`size-7`), em tom de informação e com fonte mono, e não o mesmo círculo do py-spy.

### F241 · arquivado em 2026-11-08

*Kanban:* Card de ações de campanha em arquivos por parte · Manutenção · ✅ Concluído · marco M22

**F241 — Card de ações de campanha em arquivos por parte.** `campaign-actions-card.tsx` virou a pasta `campaign-actions-card/`, com `index.tsx` (o card e o subtítulo do dado) e um arquivo por parte: `action-body.tsx`, `tv-reach.tsx`, `action-choice.tsx`, `group-choices.tsx`, `group-poll-cell.tsx`, `summary-body.tsx`, `summary-row.tsx` e `summary-title.ts`, no padrão de `statistics-report/`. Quem importa o card continua com o mesmo caminho.

O rival antes era resolvido duas vezes, no card e no corpo da ação. Agora o `index.tsx` resolve uma vez e passa o `rival` pronto ao `ActionBody`, com o tipo tirado do `CampaignPanel`.

Por fora nada mudou.

### F242 · arquivado em 2026-11-08

*Kanban:* Partida do lobby em arquivos por parte · Manutenção · ✅ Concluído · marco M22

**F242 — Partida do lobby em arquivos por parte.** `lobby-match.tsx` virou a pasta `lobby-match/`, com `index.tsx` (o card, os hooks e as duas folhas de regras) e um arquivo por parte: `summary-rows.tsx` (as linhas do resumo das regras), `newcomers-alert.tsx`, `teams-block.tsx` e `start-actions.tsx` (continuar, iniciar nova e esperar o host). Quem importa o card continua com o mesmo caminho.

`dateField`, `simulationFormSchema` e o tipo `SimulationFormValues` foram para `lobby/lib/simulation-form.ts`, que já era dono de `toFormValues` e `toSettingsBody`; os oito arquivos que importavam o tipo do card agora importam de lá, e a lib deixou de depender de um componente.

As linhas do resumo ficaram como função (`summaryRows`) e não como componente, porque o `index.tsx` também usa os rótulos delas no esqueleto de carregamento.

Por fora nada mudou.

### F243 · arquivado em 2026-11-08

*Kanban:* Folha de regras do lobby em arquivos por parte · Manutenção · ✅ Concluído · marco M22

**F243 — Folha de regras do lobby em arquivos por parte.** `rules-sheet.tsx` virou a pasta `rules-sheet/`, com `index.tsx` (a folha, as abas, o `useWatch` e as escolhas de tipo de partida e de impacto de preço) e um arquivo por seção do formulário: `basics-fields.tsx`, `grouping-fields.tsx`, `game-type-fields.tsx`, `goal-fields.tsx`, `victory-fields.tsx` e `price-impact-fields.tsx`. Cada seção recebe o `form`, o `readOnly` e só os valores observados que usa. Quem importa a folha continua com o mesmo caminho.

O `SaveStatus` ganhou arquivo próprio, com o tipo `RulesSaveStatus` que a folha e o lobby passam a compartilhar, e o `useNow` foi para `shared/hooks`.

Por fora nada mudou.

### F244 · arquivado em 2026-11-08

*Kanban:* Gráfico de ações em arquivos por parte e um hook · Manutenção · ✅ Concluído · marco M22

**F244 — Gráfico de ações em arquivos por parte e um hook.** `stock-chart.tsx` (994 linhas) virou a pasta `stock-chart/`: `index.tsx` com o componente e a composição, `chart-config.ts` (constantes, formatos e tipos), `chart-helpers.ts` (funções puras do dia, do período e dos textos da mira), `pop-row.tsx`, `legend-item.tsx`, `pane-label.tsx` e o hook `useStockChartInstance.ts`, que cria o gráfico, mantém as séries preenchidas e assina a mira. O corpo do efeito de criação e o preenchimento das séries foram movidos sem mudança de lógica; os efeitos mantêm a ordem de antes.

### F245 · arquivado em 2026-11-08

*Kanban:* Limpeza de scripts e docs · Manutenção · ✅ Concluído · marco M22

**F245 — Limpeza de scripts e docs.** Saíram `scripts/plot_beta_distribution.py`, `scripts/tree.py` e `scripts/tree_descriptions.yaml`, junto com a seção "Atualização da Árvore de Estrutura" de `docs/docs/desenvolvimento/estrutura-pastas.md`, que ensinava a rodá-los. Os scripts `profile:line` e `profile:line:view` saíram do `package.json`, e com eles `line-profiler` (`pyproject.toml`, exclude do `.spec`) e `cross-env`; os dois lockfiles foram regenerados e o deptry confirma. O padrão `*.lprof` saiu do script `clean`. Na docs de estrutura de pastas, o exemplo `base-card.tsx`, que não existe, passou a `shared/components/kpi.tsx`. O `matplotlib`, que só o `plot_beta_distribution.py` usava, continua no grupo `dev` do `pyproject.toml`.

### F69 · arquivado em 2026-11-13

*Kanban:* Imprevistos configuráveis e tipos novos · Feature · ✅ Concluído · atende N23 · marco M26

**F69 — Imprevistos configuráveis e tipos novos.** Serve N23. O modo viver de renda (F53) já nasce com os tipos de imprevisto num registro, em que cada tipo é uma entrada com nome, múltiplo da despesa mensal, efeito (sai do caixa ou corta o salário do mês seguinte) e peso no sorteio; adicionar um tipo é acrescentar uma entrada, sem mexer no motor, no log nem nas telas. Esta feature expõe esse registro ao host: no lobby, o host edita o valor de cada tipo (por exemplo, o conserto passa de 1 para 2 despesas mensais), liga e desliga tipos e cria tipos próprios com nome, valor e efeito. O sorteio continua saindo da semente da partida, então todos os jogadores seguem recebendo os mesmos imprevistos nos mesmos dias, e a configuração vale para a partida salva.

### F194 · arquivado em 2026-11-13

*Kanban:* Dólar e ativos internacionais · Feature · ✅ Concluído · atende N34, N11 · decisões D20 · marco M26

**F194 — Dólar e ativos internacionais.** Serve N34 e N11; condicionado por D20. Ideia do playtest de 31/out: a cotação do dólar no jogo, subindo com a desconfiança na moeda e caindo com o juro real alto, e os ativos internacionais andando junto. Antes tudo era em real: não existia a desvalorização da moeda, e investir fora não protegia de nada. Agora ter ativo dolarizado é estratégia de proteção, e o governo irresponsável pesa no câmbio e, pelo câmbio, na inflação.

**Feito.**
1. **O dólar da partida** é a PTAX da história vezes e elevado ao desvio: cada ponto de prêmio de risco acima da história soma 4% ao dólar e cada ponto de juro real acima da história tira 2%, cada causa com teto no expoente. Sem governo, o dólar da partida é a PTAX. Depois do último dado real a PTAX vira série macro e anda pela paridade do poder de compra.
2. **Repasse à inflação:** cada 1% de alta do dólar em 12 meses, contra a da história, soma 0,07 ponto ao IPCA em 12 meses. O prêmio de risco deixou de entrar direto no IPCA e chega a ele só pelo dólar. Para fechar o ciclo prêmio, dólar, inflação e juro com números finitos, a dívida do governo tem teto de 300% do PIB.
3. **Origem do ativo:** Nacional ou Internacional, inferida na importação (moeda USD ou classe BDR é Internacional), com troca manual na Central de dados que a reimportação preserva. O ativo Internacional anda só com o fator do dólar da partida (a razão entre o dólar da partida e a PTAX do dia, para o câmbio não contar duas vezes).
4. **Na tela:** card do dólar e KPI no painel da Economia, com o detalhe de cada ligação; seletor de origem com bandeirinha na Central de dados; filtro e bandeira na listagem de renda variável.

**Fica de fora.** O caixa em dólar com o juro americano é a F260. A calibragem dos pesos usa o CLI da economia (`.claude/trabalho/economia/calibrate10.py`); o teto de 300% do PIB deixa o cenário de gasto desenfreado com o BC cooperando derrubar a bolsa a perto de 5 mil pontos em 2010.

### F226 · arquivado em 2026-11-13

*Kanban:* Mercado reage à surpresa: o Focus da partida · Feature · ✅ Concluído · atende N34, N31, N41 · decisões D20 · marco M26

**F226 — Mercado reage à surpresa: o Focus da partida.** Serve N34, N31 e N41; condicionado por D20. Antes a bolsa reagia ao tamanho do desvio da SELIC no mesmo dia da decisão, anunciada ou não. No mercado real o preço já carrega o esperado, e no dia só mexe a parte que ninguém esperava. Agora a bolsa separa o esperado da surpresa, e a pesquisa Focus do Banco Central entra na base.

**Feito.**
1. **A bolsa reage em duas partes.** O esperado é a regra do Banco Central e se dilui no trimestre; a surpresa é o afastamento que o presidente mostrou na última reunião e entra inteira no dia em que a decisão passa a valer (o dia seguinte à reunião). Os 2,9% por ponto valem para as duas, então um desvio mantido por um ano dá o mesmo efeito acumulado de antes: muda o momento, não o tamanho. O presidente que segue a regra move a bolsa antes da reunião; quem segura a SELIC com a inflação alta surpreende no dia.
2. **O Focus é importado:** a SELIC da próxima reunião, o IPCA dos próximos 12 meses, o PIB do ano e o câmbio do fim do ano, todos pela mediana da pesquisa inteira, a partir da API de expectativas do Banco Central. As quatro aparecem na Central de dados, num grupo próprio, com dica de como ler; não limitam o período da partida nem ganham futuro gerado.
3. **No cartão da SELIC,** o KPI "Mercado espera": a mediana do Focus quando a última pesquisa tem até 30 dias (senão, a SELIC de hoje) mais o que o mercado espera do presidente, com a dica do que é o Focus e de como a surpresa mexe na bolsa.

**Fica de fora.** Só a SELIC esperada entra na conta da bolsa; IPCA, PIB e câmbio do Focus ficam como informação. O comunicado do Copom, que move a expectativa e cobra credibilidade, segue fora.

### F232 · arquivado em 2026-11-13

*Kanban:* Crescimento que sente o rombo do governo · Correção · ✅ Concluído · atende N34 · decisões D20 · marco M26

**F232 — Crescimento que sente o rombo do governo.** Serve N34; condicionado por D20. Na calibragem de 10 anos, o presidente que dá reajuste real de 15% ao ano por 10 anos chega a um primário de −22,7% do PIB e mesmo assim cresce 8% ao ano, o teto do jogo (`MAX_GROWTH` em `backend/features/economy/growth.py`), em 78 de 120 meses, com o desemprego no piso de 4% em 81. O crescimento do jogo já é o real, descontada a inflação, então o número é implausível de fato. O impulso fiscal (`IMPULSE` em `backend/features/economy/links.py`) empurra o PIB a cada piora do primário, e nada do outro lado segura o crescimento. Pior: o presidente que gasta e segura a SELIC baixa gera inflação alta e juro real muito negativo, e o modelo lê o juro real negativo como estímulo, então a inflação alta empurra o PIB para cima.

**Plano.** Duas ligações novas no alvo de crescimento (`GrowthAim`), cada uma sobre "partida menos história" (D20), uma linha própria no detalhe do PIB e uma entrada no `EconomyLink`, com a fonte na docs da economia:
1. **Inflação acima do limiar tira crescimento.** O IPCA de 12 meses acima de 12% ao ano tira crescimento a cada ponto acima do limiar; abaixo dele, nada. Base: Khan e Senhadji (FMI, 2001) acharam que, em países emergentes, a inflação acima de 11 a 12% ao ano passa a reduzir o crescimento, porque a incerteza trava o investimento; Bruno e Easterly (1998) mostram a queda forte do crescimento nas crises acima de 40% ao ano, como a dos anos 1980 no Brasil.
2. **O prêmio de risco encarece o crédito (efeito expulsão).** O prêmio acima da história tira crescimento mesmo com a SELIC baixa, porque o juro longo que as empresas pagam sobe com a desconfiança no governo, e elas investem menos. Foi o caminho do Brasil em 2002 e de 2014 a 2016.

**Sai a faixa do crescimento da partida:** o teto de 8% e o piso de −6% deixam de valer para o desvio (`next_month`), e quem segura o crescimento passa a ser o freio, com cada número explicado por uma ligação. Só sobra um piso de −15% ao ano (`COLLAPSE_GROWTH`), porque abaixo disso o ciclo dívida, prêmio e crescimento deixa de ser finito; para cima não há teto. Calibrado em 1,2 ponto por ponto de IPCA acima de 12% e 0,75 ponto por ponto de prêmio acima da história. A faixa do modelo da história onde a série não cobre (`step_growth`) fica, porque ali nenhuma medida do governo age.

**Calibragem** pelo CLI, com os cinco presidentes do roteiro em `.claude/trabalho/economia/calibrate10.py`, junto com a dos impostos e cortes (F253), que mexe na mesma conta.

**Aceite:** na calibragem de 10 anos, o gastador que nunca para cresce abaixo da história na média dos anos 6 a 10 e entra em recessão quando o prêmio dispara; os presidentes que não geram inflação acima de 12% (historiador, austero, austero com Banco Central autônomo) ficam a menos de 0,5 ponto do crescimento médio que já fecharam; nenhum mês de nenhum presidente passa de 15% ou de −15% ao ano. Quem gasta por 4 anos passa de 12% de IPCA e perde crescimento pelo freio, que é o efeito pedido.

### F250 · arquivado em 2026-11-13

*Kanban:* Correções da 4.1 · Correção · ✅ Concluído · atende N15, N34 · marco M26

**F250 — Correções da 4.1.** Lote do playtest de 08/11. Serve N15 e N34.

1. **Nome do jogador com limite.** O apelido não tem tamanho máximo em lugar nenhum (`backend/routes/auth.py:16`, `frontend/features/auth/pages/login.tsx:17`; a coluna `users.nickname` é `Text`), e um apelido gigante quebrou os diálogos da partida. Entra o limite de 20 caracteres no DTO e no formulário do login. Na mesma varredura, o nome do bot (30 no front e sem limite no backend, `routes/simulation.py:198`), o nome da partida e o do backtest (sem limite nos dois lados) ganham o mesmo limite no DTO e no formulário, e a sigla do partido aceita o mesmo tamanho nos dois lados (o front aceita de 2 a 8 letras e o DTO recusa acima de 5, `core/dto/government.py:44`). Os diálogos que mostram o apelido inteiro cortam com reticências e mostram o nome completo numa dica: `lobby-player-menu.tsx:52`, `expel-dialog.tsx:30`, `danger-zone-card.tsx:60` e `frozen-portfolio-card.tsx:38`. Os apelidos longos das partidas salvas continuam valendo e aparecem cortados; confere-se abrindo uma partida salva com o apelido longo.
2. **"Ver como tabela" do Mapa e tabela da Economia.** No Mapa, o link (`map-view.tsx:80`) rola até a tabela de lugares, e com pouca página para rolar o clique parece não fazer nada: sai o link, e a tabela de lugares fica no fim da página. Na Economia sai a tabela que abre e fecha (`economy-table.tsx`, usada só em `economy.tsx:55`), porque os gráficos já mostram os números.
3. **Card da aprovação sem o mapa.** O mini mapa de `approval-regions.tsx` abre um vão grande no card da aprovação (`approval-card.tsx`). Sai o mapa, e ficam o gráfico e um botão "Ver no mapa", que abre o Mapa na lente de aprovação (`mapLink("approval", "region")` de `lib/map-url.ts`, que o Mapa já lê da URL).
4. **Sai o aviso "Novo: indicadores técnicos".** O aviso (`stock-chart/index.tsx:338`) aparece sempre que nenhum indicador está ligado e não tem botão de dispensar. Ele depende do estado, e não de um "já visto": volta toda vez que o jogador desliga o último indicador, e em toda conta nova. Os indicadores já não são novidade, então o aviso sai, e o botão de indicadores do gráfico continua.
5. **Abertura da campanha na janela central do Jornal.** O resultado de turno e o "vão ao 2º turno" saem na janela central, porque o tipo resultado de eleição tem o nível janela fixo (`features/notifications/registry.py:108`). A manchete da abertura da campanha é do tipo calendário eleitoral, que sai como cartão por padrão (`registry.py:130`, `government/headlines.py:73`). Ela passa a sair na janela central, com o nível fixo como o do resultado de turno, e o diálogo de campanha aberta que pausa a partida continua. A janela do Jornal e o diálogo da pausa aparecem um depois do outro, sem se cobrir.
6. **Triagem: orientar a bancada num governo do computador.** O backend respeita a orientação do líder da bancada num governo do computador (teste em `tests/test_congress.py`). O relato de que a orientação Sim por padrão não podia ser recusada tem três causas de desenho, sem bug de código: o acordo de apoio força Sim e o Não só pega depois de "Orientar Não e romper"; o controle aparece mesmo quando a federação tem outro partido como líder e o clique volta 403; e em velocidade alta o mês passa antes de a medida ser orientada, porque a janela vai até a véspera, o último dia útil do mês.

### F251 · arquivado em 2026-11-13

*Kanban:* Mapa da eleição ao longo do tempo · Melhoria · ✅ Concluído · atende N34 · marco M26

**F251 — Mapa da eleição ao longo do tempo.** Serve N34; retrabalho do mapa por região (F164). O Mapa mostrava só o momento atual; agora uma linha do tempo percorre o ciclo inteiro de cada eleição da partida.

**Entregue:** o seletor escolhe o ano e a régua cobre o ciclo (pesquisas mensais do 1º turno, apuração do 1º turno, pesquisas semanais do 2º turno e apuração do 2º). A lente "Quem lidera" junta a pesquisa e o resultado: ponto de pesquisa mostra quem lidera (listras no empate técnico), ponto de resultado mostra quem venceu. Aprovação, Rejeição e Onde vive cada grupo não têm data e escondem a linha do tempo inteira. A Variação compara com o ponto anterior. Marcos entre as pesquisas (promessa, ações de campanha e aliança) aparecem na régua, no máximo dois por intervalo e o resto em "+N". O card do lugar ganha o gráfico "<Lugar> ao longo da campanha", e clicar num ponto leva a régua até ele. As setas ← e → andam a régua, "Reproduzir" anda um ponto por segundo até o hoje e "Voltar ao hoje" sai do ponto passado. Com cinco eleições ou mais, os anos antigos vão para a grade "Anteriores". Se o histórico falha, só a régua mostra o erro, com "Tentar de novo"; o mapa segue no hoje.

**Aceite:** a rota `/api/government/map/timeline` devolve anos, pontos e marcos; conferido no app de teste com duas eleições passadas, a 1920 e a 1366, e com a rota do histórico falhando.

### F252 · arquivado em 2026-11-13

*Kanban:* Atalhos de valor no Tesouro e varredura de qualidade de vida · Melhoria · ✅ Concluído · atende N15 · marco M26

**F252 — Atalhos de valor no Tesouro e varredura de qualidade de vida.** Atalhos de 25%, 50% e Tudo na compra e na venda do Tesouro (a venda perdeu o seletor e ganhou o campo sempre visível). Varredura: Enter confirma, foco no primeiro campo e motivo do botão desabilitado (dica ao passar o mouse) nas telas de valor e de ação; atalhos de valor no pagamento antecipado do crédito.

### F253 · arquivado em 2026-11-13

*Kanban:* Impostos e cortes que fecham a conta do governo · Melhoria · ✅ Concluído · atende N34, N41 · decisões D20 · marco M26

**F253 — Impostos e cortes que fecham a conta do governo.** Serve N34 e N41; condicionado por D20. No playtest de 08/11, taxar não pagou a dívida e não houve como cortar gasto, e o código confirma as duas coisas.

**Receita hoje:** os impostos do jogo são só os do investimento (IR das vendas comuns, do day trade, da renda fixa e da LCI/LCA, e as regras por setor), modelados em % do PIB. Com a política padrão eles somam 0,69% do PIB (`backend/features/government/budget.py:213`); o resto da receita é um valor fixo que fecha o gasto-base de 19% do PIB (`spending.py:26`). Cada imposto rende `base × (alíquota ÷ referência)^(1 − elasticidade)`. A renda fixa a 50% (a referência é 17,5%) passa de 0,60% para cerca de 1,46% do PIB, e as vendas de ações a 100% (referência de 15%) passam de 0,06% para cerca de 0,19%. Na vida real, o IR sobre aplicações também é uma fatia pequena de uma carga de cerca de 32% do PIB: o grosso vem do imposto de renda de pessoas e empresas, dos impostos sobre consumo e da contribuição à previdência.

**Gasto hoje:** só o auxílio e as obras descem, e só até zero. O gasto-base não se mexe, e o reajuste de servidores e de aposentadorias não aceita valor negativo (`spending.py:43`).

**Plano.**
1. **Quatro impostos novos abrem o valor fixo da receita**, cada um um `MeasureKind` novo com a alíquota de referência que reproduz a história e a mesma fórmula de rendimento dos de hoje. Com as alíquotas de referência, a soma deles é o valor fixo de hoje, então sem governo a conta não muda (D20). Cada um cobra um preço, como parcela do desvio:
   - **Consumo (ICMS/IPI):** arrecada muito e com elasticidade baixa; sobe a inflação na hora e tira aprovação dos grupos de renda baixa (D19).
   - **IR das empresas:** tira lucro e derruba a bolsa, no molde do risco fiscal no Ibovespa.
   - **IR das pessoas:** pesa nos grupos de renda alta e desconta do salário no viver de renda (F257).
   - **Contribuição sobre a folha:** arrecada bem e encarece contratar: sobe o desvio do desemprego.
2. **O gasto-base se abre em folha, previdência e custeio**, nos pesos do orçamento real. O reajuste de servidores e de aposentadorias aceita valor real negativo, o reajuste abaixo da inflação do teto de gastos de 2016, e irrita servidores e aposentados. O corte de custeio é uma medida nova que freia o PIB, no molde das obras com o sinal trocado. A reforma da previdência fica fora.
3. **A isenção move o setor:** enquanto a isenção por setor vale, as ações do setor ganham uma alta como camada sobre o preço histórico, como a redução do IPI dos carros em 2012.
4. **Calibragem** pelo CLI (`.claude/trabalho/economia/calibrate10.py`), junto com a do crescimento que sente o rombo (F232), que mexe na mesma conta: a elasticidade e o efeito de cada imposto e corte na inflação, no PIB, no desemprego e na aprovação.

A aba Contas mostra cada imposto e cada parte do gasto-base como card próprio, com a dica do que ele custa. A docs da economia ganha os impostos e os cortes novos.

**Aceite:** sem governo, receita, gasto e primário saem iguais aos de antes da mudança em toda a calibragem; um presidente que usa as alavancas novas consegue mudar o primário em 3 pontos do PIB dentro de um mandato, e cada alavanca cobra o preço dela (inflação, bolsa, desemprego ou aprovação) no painel da Economia.

### F254 · arquivado em 2026-11-13

*Kanban:* Programas de governo com nome · Feature · ✅ Concluído · atende N34, N31 · decisões D19 · marco M26

**F254 — Programas de governo com nome.** Serve N34 e N31; condicionado por D19. Hoje o auxílio é uma medida de gasto sem nome (`WELFARE_SPENDING`, em passos de 0,5 ponto do PIB até 5%). A ideia do playtest de 08/11: o presidente cria o programa com nome ("Bolsa Família", "Auxílio Brasil"), e o nome aparece no Jornal ("Governo lança o Bolsa Família") e no card de gasto da aba Contas.

**Plano.** O nome é um campo da medida de hoje, sem medida nova:
1. O auxílio (`WELFARE_SPENDING`) e as obras (`PUBLIC_WORKS`) aceitam nome ao propor a medida, com até 30 caracteres no DTO e no formulário, no molde dos outros nomes da partida. O nome sai no Jornal e no card de gasto da aba Contas; sem nome, tudo fica como hoje.
2. **Extinguir custa mais:** levar a verba de um programa com nome a zero soma rejeição no grupo que a medida atende (a memória da D19), além da queda de apoio que o mesmo corte sem nome já dá. Reduzir sem zerar funciona como hoje.
3. **Rebatizar** (o "Auxílio Brasil" no lugar do "Bolsa Família", em 2021) mantém a verba e o apoio do programa e custa uma vez um pouco de aprovação geral, com a manchete no Jornal.
4. O tamanho do custo de extinguir e de rebatizar se calibra jogando, como os outros números da D19.

Plano econômico com nome ("Plano Real") fica fora: não existe medida de plano econômico.

### F256 · arquivado em 2026-11-13

*Kanban:* SELIC abaixo de zero em futuro com deflação · Melhoria · ✅ Concluído · atende N34 · decisões D20 · marco M26

**F256 — SELIC abaixo de zero em futuro com deflação.** Serve N34; condicionado por D20. Hoje o piso da SELIC é 0%, no DTO (`SelicRequest`, `backend/core/dto/government.py:1098`) e na janela de cada reunião (`backend/features/economy/monetary.py:76` e `frontend/features/government/lib/monetary.ts:17`). No histórico do Brasil a inflação é sempre positiva, e com a SELIC a 0% o juro real já fica muito negativo. A SELIC negativa só faz sentido num futuro gerado com deflação (o regime de inflação do gerador vai até −5 pontos), como no Japão e na Europa dos anos 2010.

**Plano.**
1. Com o IPCA de 12 meses negativo, o piso da SELIC desce para −0,5%, o do Banco Central Europeu; com ele de volta acima de zero, a reunião seguinte volta a ter piso 0%. A regra vale no DTO, na janela da reunião e no formulário, e a dica da SELIC explica quando o piso abaixo de zero abre.
2. O caixa do jogador continua rendendo 0%. Com a SELIC negativa, o dinheiro foge da renda fixa pós-fixada para o caixa, que é a lição real do piso perto de zero: os bancos centrais não descem muito porque as pessoas sacam o dinheiro.
3. A renda fixa pós-fixada rende negativo e mostra isso como qualquer perda, e o IR sobre o rendimento negativo é zero; confere-se o cálculo do IR e do extrato com o rendimento abaixo de zero.

**Aceite:** num futuro gerado com deflação, o presidente leva a SELIC a −0,5%, o Tesouro Selic perde valor dia a dia e o caixa não; com o IPCA de volta acima de zero, a reunião seguinte recusa valor abaixo de 0%.

### F257 · arquivado em 2026-11-13

*Kanban:* Viver de renda que sente a economia · Feature · ✅ Concluído · atende N23, N34 · decisões D20 · marco M26

**F257 — Viver de renda que sente a economia.** Serve N23 e N34; condicionado por D20. No modo viver de renda, o salário e a despesa são valores fixos da partida (`backend/core/life_budget.py:39`). Eles só se corrigem pelo IPCA de 12 meses em cada aniversário do começo da partida, e só com a correção pela inflação ligada (`life_budget.py:55`, `core/indicators.py:254`). O IPCA lido é o da camada da economia (`features/economy/layer.py:270`), então o gasto do governo, que sobe a inflação, chega ao salário e à despesa por esse caminho indireto. Nada mais chega. O IR é só sobre o investimento (`simulation.py:1645`), sem tocar no salário. O juro do cheque especial é fixo e não segue a SELIC (`simulation.py:225`). A demissão é sorteada da semente com a mesma chance por pregão, sem ler o desemprego nem o PIB (`features/simulation/life_events.py:76`).

**Plano.** Quatro ligações, cada uma lendo a série da partida, que sem governo é a história:
1. **A demissão segue o desemprego:** a chance por pregão passa a ser a de hoje vezes o desemprego da partida sobre o neutro de 9%. Com 18% de desemprego, demite o dobro; com 4%, menos da metade. O sorteio continua saindo da semente.
2. **Reajuste real pelo PIB:** no aniversário da partida, além da correção pelo IPCA, o salário ganha parte do crescimento real do PIB dos 12 meses quando ele é positivo; na recessão, não há reajuste real.
3. **O cheque especial segue a SELIC:** o juro passa a ser a SELIC mais um spread fixo, escolhido para que, na SELIC média da história, dê o juro fixo de hoje.
4. **O IR das pessoas desconta do salário:** o desvio da alíquota do IR das pessoas (F253) contra a referência desconta do salário. Sem governo, o salário líquido é o de hoje.

O registro do orçamento mostra cada mudança no salário, na despesa e no juro com a origem ("reajuste pelo PIB de 3,1%", "demissão com desemprego de 14%"). A profissão do jogador, que liga o salário a um grupo do eleitorado, é um card próprio que parte deste.

**Aceite:** com a mesma semente, uma partida sem governo e de desemprego alto sorteia mais demissões que uma de desemprego baixo, e o registro do orçamento mostra a origem de toda mudança de salário, despesa e juro.

### F258 · arquivado em 2026-11-13

*Kanban:* Orientação da bancada que se explica · Melhoria · ✅ Concluído · atende N34 · marco M26

**F258 — Orientação da bancada que se explica.** Serve N34. O líder orienta a bancada até o fim do dia da votação, e a casa apura à noite, com a orientação que ele deu até lá. O acordo de apoio mostra o Não pendente, com o aviso do rompimento e o botão de confirmar; fechar sem confirmar mantém o Sim e avisa. Na federação em que outro partido orienta, o controle aparece travado, dizendo quem orienta.

### F259 · arquivado em 2026-11-13

*Kanban:* Preço dos ativos cotados em dólar convertido para real · Correção · ✅ Concluído · atende N11, N34 · marco M26

**F259 — Preço dos ativos cotados em dólar convertido para real.** Serve N11. O importador manda ao Yahoo Finance o ticker como está quando ele não é da B3 (`yfinance_symbol` em `backend/features/import_data/importer_service.py:44`), e o download (`from_yfinance`, linhas 55-85, e `from_yfinance_batch`) guarda o preço sem ler a moeda que o Yahoo devolve. A AAPL a US$ 200 entra como R$ 200, e o mesmo vale para a MSFT e para o BTC-USD; a tela formata tudo em real (`frontend/shared/lib/utils/format.ts:50`). Comprar uma ação americana sai cinco vezes mais barato do que na vida real, e a alta do dólar não mexe nela. Os BDRs (AAPL34) já vêm em reais e não mudam.

**Plano.**
1. A PTAX, a cotação oficial do dólar que o Banco Central publica todo dia (série 1 do SGS), entra como série nova, desde 1994, e aparece na Central de dados.
2. O importador lê a moeda do ativo no Yahoo e guarda numa coluna nova do ativo (migração pelo `pnpm db:revision`). O preço em dólar se converte para real pela PTAX de cada dia na importação e na atualização, e o histórico antes da PTAX fica de fora. Ativo em outra moeda é recusado na importação com o motivo.
3. Os ativos em dólar já importados ganham a moeda e o preço convertido pela atualização de ativos que já existe. As partidas salvas com esses ativos mudam de preço, então o commit leva `!`.
4. A docs da importação passa a dizer que o preço de fora vem convertido pela PTAX do dia.

**Aceite:** a AAPL e o BTC-USD importados mostram, num dia qualquer, o fechamento do Yahoo vezes a PTAX daquele dia, ao centavo; os ativos da B3 saem iguais aos de antes.

### F260 · arquivado em 2026-11-13

*Kanban:* Caixa em dólar com o juro americano · Feature · ✅ Concluído · atende N41, N34 · marco M26

**F260 — Caixa em dólar com o juro americano.** Serve N41 e N34; amplia o dólar e os ativos internacionais ([F194](#f194)). O carry trade é tomar dinheiro onde o juro é baixo e aplicar onde é alto, ganhando a diferença enquanto a moeda não vira contra. Exemplo: com o CDI a 13% e o juro americano a 5%, quem aplica em real ganha 8 pontos ao ano a mais, e uma alta de 10% do dólar come todo esse ganho. Antes o dólar já se movia e os ativos de fora já protegiam, mas não existia um ativo em dólar que só rendesse juro, e a escolha "CDI ou dólar com juro americano" não aparecia. Agora ela aparece, com o dólar que empata a conta à vista.

**Feito.**
1. **O juro americano da partida:** a série Fed Funds (taxa básica dos EUA, em % ao ano, baixada do FRED na Central de dados) entra como série macro com início em jul/1994, o da PTAX. Depois do último dado real ela volta a 3% pela metade do caminho a cada 2 anos.
2. **A conta em dólar (Nomad):** ativo de liquidez diária que rende 100% do juro americano, marcado pelo dólar da partida. A compra paga 1,1% de IOF de câmbio e vira dólares ao dólar do dia; o saldo em dólar cresce com o fator diário do Fed e o valor em reais acompanha o dólar. O resgate leva IR de 15% sobre o ganho em reais, sem IOF, e a cobertura automática do caixa vende a conta como vende o CDB de liquidez diária. A conta não entra no cálculo da melhor taxa de renda fixa do crédito.
3. **Na tela:** dois cards lado a lado no topo da Renda fixa (CDB de liquidez diária e conta em dólar, com o "empata se o dólar subir"), prévia em dólares e IOF na boleta de investir, "sai da conta" e IR de 15% na de resgatar, saldo em dólar nos detalhes e na carteira, e a série do Fed com dica na Central de dados.

**Fica de fora.** Empréstimo em dólar (o carry trade completo), título do Tesouro americano, apuração anual do IR sobre a variação cambial e alíquota de IR do câmbio definida pelo governo.

### F261 · arquivado em 2026-11-13

*Kanban:* Profissão no viver de renda · Feature · ✅ Concluído · atende N23, N34 · decisões D19 · marco M26

**F261 — Profissão no viver de renda.** Serve N23 e N34; parte do viver de renda que sente a economia ([F257](#f257)). Hoje o salário e a despesa são os mesmos para todos os jogadores da partida (`SimulationSettingsDTO`, `backend/core/dto/simulation.py:108`; `_live` em `simulation.py:1340`). A ideia do playtest de 08/11: uma opção do modo, "salário igual para todos" (o de hoje) ou "cada um escolhe a profissão", como uma classe de RPG. Cada profissão pertence a um grupo do eleitorado (D19), então a medida que taxa os mais ricos, reforça o auxílio ou reajusta as aposentadorias chega direto na renda dos jogadores daquele grupo: o jogador que governa mexe na vida dos outros, e o servidor sente na pele o ajuste fiscal que o presidente aprova.

**Equilíbrio sem limitar a renda.** A renda muda de verdade entre as profissões e oscila com a economia; nenhuma é a melhor em tudo. As alavancas candidatas:
- **Com o que a renda oscila:** o CLT pela demissão que segue o desemprego; o servidor pelo reajuste do governo, que congela no ajuste fiscal, mas não é demitido; o aposentado pelo reajuste das aposentadorias, com renda menor e sem demissão; o empresário pelo PIB e pela bolsa, com renda alta nos anos bons e meses sem retirada, ou com aporte, na recessão; quem vive de auxílio pelo auxílio do governo, que é cortado quando a renda passa do limite.
- **Padrão de vida:** a despesa acompanha a profissão, e a meta do modo (o patrimônio que paga a despesa do ano, `goal_on` em `backend/features/statistics/goal.py:13`) passa a ser a de cada jogador. O empresário ganha mais e precisa de mais para viver de renda. Hoje a meta é uma só por partida: mudar isso muda o contrato do `goal_on`.
- **Alvo das medidas:** o IR das pessoas ([F253](#f253)) e as medidas por grupo pesam mais em quem ganha mais.
- **Vantagens próprias:** a estabilidade do servidor, o FGTS e o seguro-desemprego do CLT na demissão, o crédito do empresário.

**Falta:** a lista de profissões e os números de cada uma; se a meta passa a ser de cada jogador ou se o placar compensa a renda de outro jeito; qual profissão os bots escolhem; e como o imprevisto, que é um múltiplo da despesa mensal ([F69](#f69)), se comporta com a despesa de cada jogador: o dia do sorteio segue igual para todos, e o valor sai da despesa de cada um.

**Feito.**

### F262 · arquivado em 2026-11-13

*Kanban:* Pedido de impeachment aberto por jogador · Feature · ✅ Concluído · atende N34 · marco M26

**F262 — Pedido de impeachment aberto por jogador.** Serve N34. O líder de um partido com pelo menos uma cadeira na casa, fora o do partido do presidente, abre o pedido enquanto a aprovação de um presidente jogador está abaixo do piso de 25% e fora da carência dos 12 primeiros meses. Há um pedido aberto por vez e cada partido pede uma vez por mandato. O pedido rejeitado soma 5 pontos de rejeição ao partido de quem pediu, nos grupos de eleitores que ainda aprovam o presidente. O pedido sai em manchete para a sala toda e em aviso ao presidente, com o partido que pediu; a tela do Congresso mostra o botão com o custo explicado antes de confirmar. A bancada na base orienta Não e protege o presidente, sem código novo. Os 5 pontos ficam para a calibragem pelo CLI.

### F263 · arquivado em 2026-11-13

*Kanban:* Bolsa com piso e dividendo que acompanha o preço da partida · Correção · ✅ Concluído · atende N3, N34 · decisões D20 · marco M26

**F263 — Bolsa com piso e dividendo que acompanha o preço da partida.** Serve N3 e N34; condicionado por D20. Na Simulação #3, o nível da bolsa da partida (`level` em `backend/features/economy/layer.py:270`, a exponencial da soma das forças, sem limite para baixo) levou as ações a 1/400 da série guardada: a PETR4 foi de ~R$ 4,40 a R$ 0,01 no fim de 2031 e ficou assim até o fim. O provento continuou igual ao histórico por ação (`broker.py:142` paga `event.value` sem o fator da partida), e o rendimento passou de ~9% para milhares de por cento ao ano. Uma jogadora aplicou R$ 50 mi em PETR4 entre 2033 e 2035 e recebeu R$ 3,69 bi em dividendos. O arredondamento ao centavo (`_scale` em `variable_income/price_impact.py`) piora o quadro: a ação alterna entre R$ 0,00 e R$ 0,01, e a carteira de um bot foi de R$ 30 mil a R$ 0,01 num pregão e voltou a R$ 7,5 mil.

**Plano.**
1. **Provento na escala da partida.** O dividendo e o JCP por ação são multiplicados pelo `stock_factor` do dia do pagamento, o mesmo do preço. O histórico de proventos e o rendimento (`dividends.py`, `trailing_per_share`) leem o valor já escalado.
2. **Piso com amortecimento no nível da bolsa.** Abaixo de um limiar, a queda do nível se comprime em vez de seguir a exponencial. O limiar e o piso são calibrados na calibragem de 10 anos, com o pior governo que ela simula.
3. **Preço que não arredonda a zero.** O OHLC escalado tem piso de R$ 0,01.

**Aceite.** Teste com o fator da bolsa a 1/400: o provento sai a 1/400 do histórico. A calibragem de 10 anos com o pior governo não leva a bolsa abaixo do piso. Nenhum preço de ação sai R$ 0,00.

### F264 · arquivado em 2026-11-13

*Kanban:* Nota de desempenho que não explode com patrimônio quase zero · Correção · ✅ Concluído · atende N9, N3 · decisões D10 · marco M26

**F264 — Nota de desempenho que não explode com patrimônio quase zero.** Serve N9 e N3; condicionado por D10.

**Sintoma.** Na Simulação #3 o bot Vovô Investidor venceu por nota com 9.067.544 pontos tendo perdido 42%; os outros ficaram entre 117 e 367. O patrimônio dele foi de R$ 30 mil a R$ 0,01 num pregão (ação arredondada a R$ 0,00) e voltou a R$ 7,5 mil dias depois.

**Como reproduzir.** Um histórico de pelo menos 63 pregões que rende perto do CDI, com um pregão em que o patrimônio vai de 30.000 a 0,01 e outro em que volta a 7.500, sem aporte entre eles. `player_score` devolve milhões de pontos no eixo de eficiência.

**Causa.** O retorno do dia é o ganho dividido pelo patrimônio da véspera (`_ScoreWalk.add`, `backend/features/statistics/score.py:122-141`). Sobre uma véspera de R$ 0,01, o dia da volta vale dezenas de milhões de por cento. A média de retornos simples não é simétrica: cair 50% e subir 100% deixa o patrimônio igual, mas a média dos dois dias dá +25% por dia. Esse único dia puxa a média do excesso sobre o CDI para cima, o desvio só das quedas quase não se mexe, e o Sortino (retorno acima do CDI dividido pela oscilação para baixo) sai em centenas de milhares; como a reta de pontos não tem teto (`Band.points`, `score.py:40-42`), viram milhões de pontos. O mesmo cálculo existe uma segunda vez em `backend/features/statistics/risk.py` (`annual_volatility` :92, `rolling_volatility` :99, `sharpe_ratio` :160, `sortino_ratio` :172), que alimenta a aba de risco, o ranking e o critério de vitória por Sharpe (`ranking.py:318-319`), e sofre do mesmo dia.

**O que muda.** As métricas que são média ou desvio de retornos diários passam a usar o retorno em escala logarítmica, `ln(1 + retorno)`. Nessa escala cair 50% vale −0,693 e subir 100% vale +0,693: os dois se anulam, e a ida a R$ 0,01 e a volta entram como dois dias enormes de sinais opostos, que contam como oscilação e não como ganho. A nota continua sem teto de pontos (a D10 fica como está): uma carteira só de renda fixa acima do CDI continua podendo tirar nota muito alta em eficiência, por decisão.

1. Em `risk.py`, uma função `log_return(daily)` devolve `ln(max(1 + daily, LOG_FLOOR))`, com `LOG_FLOOR = Decimal("1e-9")`: a perda total do dia entra como −99,9999999%, porque o logaritmo de zero não existe. O piso fica abaixo de qualquer queda com patrimônio positivo (de R$ 30 mil a R$ 0,01 o fator é 3,3e-7); com piso de 0,0001 a ida a R$ 0,01 seria cortada e a volta não a anularia. O CDI do dia ganha a versão logarítmica guardada junto da tabela que `cdi_return` já mantém.
2. Passam para a escala logarítmica: `annual_volatility`, `rolling_volatility`, `sharpe_ratio` e `sortino_ratio` em `risk.py`, e as somas `_sum`, `_squares`, `_excess` e `_downside` de `_ScoreWalk`. O excesso do dia é `log_return(daily) - ln(1 + cdi)`.
3. Ficam como estão, compostos pelo retorno simples: a cota, a queda máxima, o tempo abaixo do pico, os retornos mensais, o retorno anual e os retornos sobre o CDI e o Ibovespa. `daily_returns` continua devolvendo o retorno simples; a conversão acontece dentro das quatro funções.
4. O caminho incremental (`_ScoreWalk`) e o direto (`player_score` sobre `risk.py`) continuam dando a mesma nota: os testes que comparam os dois ficam.
5. `tests/test_statistics_score.py` e `tests/test_statistics_risk.py` ganham o caso do patrimônio quase zero e o caso simétrico (−50% e +100%), e os valores esperados dos casos atuais são recalculados.
6. `docs/docs/como-usar/estatisticas.md` (trechos de volatilidade, Sharpe e Sortino) e as descrições das métricas em `frontend/features/statistics/lib/metrics.ts` passam a dizer que a oscilação é medida numa escala em que queda e alta do mesmo tamanho se anulam, com o exemplo dos 50% e 100%.
7. `Decimal.ln()` roda duas vezes por snapshot. Medir o tempo do histórico da nota numa partida de 10 anos antes e depois; se passar de 10% a mais, calcular com `math.log1p` sobre `float` e converter para `Decimal`.

**Efeito nas partidas salvas.** A nota é recalculada dos snapshots a cada leitura, então toda partida muda um pouco. Estimativa: de 2 a 7 pontos a menos no eixo de eficiência, mais para quem oscila mais (com volatilidade de 20% ao ano o Sharpe cai cerca de 0,1). A conquista dos 250 pontos (`achievements/catalog.py:282-288`) usa a nota nova.

**Aceite:** no histórico do "como reproduzir", Sharpe e Sortino saem negativos, a volatilidade dá 0 ponto e a nota total fica na casa das dezenas (antes, 9 milhões de pontos). Num histórico de dois dias com −50% e +100%, a média dos retornos usada no Sharpe é 0. Um histórico comum, com volatilidade de até 30% ao ano, muda menos de 10 pontos na nota total.

### F265 · arquivado em 2026-11-13

*Kanban:* Acabamentos do mapa, do Tesouro e dos cards da economia · Correção · ✅ Concluído · atende N15, N34 · marco M26

**F265 — Acabamentos do mapa, do Tesouro e dos cards da economia.** Serve N15 e N34. Lote de consertos pequenos que saíram da partida de 10/11.

1. **Mapa que acompanha a eleição.** `useElectionMap.ts` e `useElectionTimeline.ts` não ouvem o socket nem recarregam: só invalidam no resultado da eleição (`government-notifications.tsx:66-69`). Com isso, a pesquisa nova não aparece até a apuração. Passam a invalidar a cada pesquisa publicada. As pesquisas semanais do 2º turno já estão na linha do tempo (`map_timeline.py:163-172`), e a nota de que elas não apareciam entre os turnos provavelmente tem a mesma causa: conferir no app depois do conserto.
2. **Tesouro sem título vencido.** O catálogo só renova no dia 1 do mês (`useTreasuryCatalog.ts:11-14`). O título vencido continua na lista e devolve 409 ao investir (`fixed_broker.py:159-161`). O catálogo passa a ser invalidado no vencimento.
3. **Card do dólar sem vão.** O `dollar-card.tsx` abre um vão na grade da Economia.
4. **Card Dívida ÷ PIB.** O gráfico não ocupa a altura do card e sobra um vão acima dele. O eixo x repete rótulos ("dez/21 dez/21", "fev/22 fev/22"). "Resultado primário 0,0%" aparece ao lado de "Resultado do mês −R$ 61,6 bi": conferir se o 0,0% é arredondamento ou leitura errada.
5. **Diálogo do resultado da eleição.** Os três botões de `round-result-dialog.tsx:159-172` (Ver no mapa, Fechar e o principal) ficam desalinhados, e o conteúdo fica mais curto.
6. **Lentes do mapa alinhadas.** Os rótulos "precisa de 2 pesquisas" e "sem dados por lugar" na mesma linha desalinham os atalhos numerados. O espaçamento fica igual em todas as lentes.
7. **Atalhos de valor que somam.** Na contribuição mensal (`contribution-field.tsx:9`) e na doação (`donate-dialog.tsx:36`), o atalho substitui o valor; na renda fixa (`investment-ticket.tsx:30-34`), ele soma. Os dois passam a somar, como na renda fixa.
8. **Selo do partido no jornal.** A manchete cita a sigla só em texto ("UPR"); passa a mostrar o selo do partido, o mesmo das telas de governo.
9. **Juro americano na prévia do futuro gerado.** O FED_FUNDS é gerado (`synthetic.py:854-870`), mas não está no `FuturePreviewDTO` (`dto/generated_future.py:78-95`), então não aparece na prévia do diálogo de geração.

### F266 · arquivado em 2026-11-13

*Kanban:* Central de dados redesenhada · Melhoria · ✅ Concluído · atende N13, N15 · marco M26

**F266 — Central de dados redesenhada.** Serve N13 e N15. A tabela de séries ficou apertada: nomes cortados ("FOCUS_S…", "GDP_GRO…") e três colunas que só mostram "—". As séries do Focus são importadas e não ganham futuro gerado, por desenho (F226), mas a legenda genérica "repete o último valor" (`how-to-read.tsx:29`) não diz isso.

### F267 · arquivado em 2026-11-13

*Kanban:* Lobby com topo enxuto e profissão na preparação · Melhoria · ✅ Concluído · atende N15, N39 · marco M26

**F267 — Lobby com topo enxuto e profissão na preparação.** Serve N15 e N39. O topo do lobby quebra linha e fica desarmônico: Conquistas, Minha preparação e Como jogar dividem a linha com o título, o link de convite e o Desafio da vela. No card do bot, "Bot", "CLT" e "robô não prepara" se sobrepõem e "Comp…" corta (`lobby-player-list.tsx:173`, `:192-198`). A profissão sai do seletor do card e vira uma aba do diálogo Minha preparação (`preparation-dialog.tsx:73`, que hoje tem as abas partido e estratégias).

### F268 · arquivado em 2026-11-13

*Kanban:* Tela do Mapa repensada · Melhoria · ✅ Concluído · atende N34, N15 · marco M26

**F268 — Tela do Mapa repensada.** Serve N34 e N15. Em "Estados, do maior para o menor", o "Ver mais" abre um card pequeno numa coluna estreita à direita, com rolagem horizontal, e deixa a página vazia à esquerda. Os rótulos das lentes ocupam espaços desiguais.

### F269 · arquivado em 2026-11-13

*Kanban:* Governo e Eleição com as ações do jogador num lugar só · Melhoria · ✅ Concluído · atende N34, N15 · marco M26

**F269 — Governo e Eleição com as ações do jogador num lugar só.** Serve N34 e N15. Governo e Eleição ganharam a aba "Suas ações", a primeira de cada página, com "Para decidir agora" (o que tem prazo), as ações por papel (presidente, líder, filiado, fundador) e o motivo de cada ação apagada escrito à vista. Cada linha abre o diálogo que já existe ou leva à aba onde a ação mora. A faixa "O país" (PIB, crescimento em 12 meses e dívida) fica no cabeçalho das duas páginas, em todas as abas.

### F270 · arquivado em 2026-11-13

*Kanban:* Cards permanentes da Renda fixa integrados à tela · Melhoria · ✅ Concluído · atende N15 · marco M26

**F270 — Cards permanentes da Renda fixa integrados à tela.** Serve N15. Os cards fixos "CDB Nubank Liquidez Diária", em verde, e "Conta em dólar", em azul, destoam da tela: as cores, o layout e a posição não seguem o resto da Renda fixa.

### F271 · arquivado em 2026-11-13

*Kanban:* Paleta de 20 cores para os partidos, sala de 12 jogadores e um seletor de cor único · Melhoria · ✅ Concluído · atende N20 · marco M26 · dependência de F285

**F271 — Paleta de 20 cores para os partidos, sala de 12 jogadores e um seletor de cor único.** Serve N20.

**O que foi feito.** Os partidos têm 20 cores com nome em `PARTY_PALETTE` (`frontend/shared/lib/party-colors.ts`): as 12 dos jogadores, na mesma ordem, mais 8 só de partido: Vermelho `#D92D20`, Laranja `#E8590C`, Caramelo `#A85F00`, Verde `#1A9A44`, Vinho `#800020`, Magenta `#B5179E`, Âmbar `#CC8A00` e Musgo `#517722`. Os jogadores passaram de 10 para 12 cores (`chart-1` a `chart-12`; Rosa e Azul-céu são as novas) e a sala, de 10 para 12 vagas. O teto de bots, o do backtest e a documentação acompanham `PLAYER_COLORS`/`MAX_PLAYERS`; as equipes mantêm o teto próprio de 10. Vermelho e Âmbar ficam só de partido: nos gráficos de carteira o vermelho significa perda e o âmbar, alerta. A paleta de partido tem sempre mais cores que a sala tem vagas, então toda fundadora acha uma cor livre (o teste confere).

**Avaliação com as tintas do Minecraft.** O alvo do card era uma paleta no nível das 16 tintas do Minecraft. Medidas lado a lado (sem branco, cinzas e preto, que o sistema reserva):

- Contraste contra o fundo do app (de 1, cores iguais, a 21, preto no branco; 3 é o mínimo para um elemento gráfico ser visto): 6 das 12 tintas coloridas ficam abaixo de 3 (Amarelo 1,2; Lima 1,8; Rosa 2,0; Azul-claro 2,1; Laranja 2,3; Ciano 2,9). Nas nossas, só 3 ficavam abaixo, por pouco (Lima, Salmão e Lavanda, entre 2,88 e 2,97), e foram escurecidas de forma imperceptível (ΔE de cada uma contra a original abaixo de 2) até passar de 3.
- Distinção entre cores, pelo ΔE (CIEDE2000: mede o quanto duas cores parecem diferentes; abaixo de 2 quase ninguém nota, perto de 10 dá para distinguir lado a lado, acima de 20 são claramente outras cores): o par mais próximo do Minecraft é Azul~Roxo (14,5) e o da nossa paleta de 16 era Laranja~Vermelho (13,0). Empatam.
- O Minecraft é uma paleta feita para tingir blocos, não para marcar partido sobre fundo claro. O que ele tem de bom é a gama (as famílias de cor cobrem o círculo todo) e o reconhecimento; a nossa pega a mesma gama, com a luminosidade corrigida para o fundo.
- Daltonismo (simulação de Machado, 2009, com ΔE sobre as cores simuladas): as duas têm pares críticos. No Minecraft, Azul~Roxo (2,4 na protanopia) e Verde~MNV (1,2 na deuteranopia); na nossa, Caramelo~MNV (0,8 na protanopia), Vermelho~Caramelo (2,8) e Verde-água~sem cor (2,4 na deuteranopia). A escolha das cores foi só pelo contraste e pelo ΔE normal; o modo daltonismo é um card à parte.

**Por que 20.** Com a paleta de 16, cabiam mais 22 cores com ΔE de pelo menos 12 e contraste de pelo menos 3, mas quase todas quase pretas ou neon. Entraram as 4 que ficam vivas e fáceis de nomear: Vinho (ΔE 14,2 para a Marrom), Magenta (14,5 para a Rosa), Âmbar (15,9 para o Caramelo) e Musgo (14,5 para o Verde). Turquesa não entrou: contra a Verde-água fica a ΔE 5 a 7, e o tom que se separa dela cai abaixo de 3 de contraste. Amarelo e contraste não combinam: o amarelo vivo (`#FFD400`) dá 1,25 para 1 contra o fundo e some, e o mais claro que passa de 3 para 1 é uma mostarda (`#B4811A`), que ficou feia ao lado das outras. O Âmbar é o meio-termo escolhido: `#CC8A00` tem 2,55 para 1 contra o fundo mais escuro do app (abaixo do piso de 3, a única exceção), é bem mais amarelo que a mostarda e se separa de todas as outras por ΔE de pelo menos 15,9. Para um amarelo mais vivo ainda, `#E0A100` dá 1,98 para 1: o preço é sumir mais no fundo.

- O teste da paleta (`party-colors.test.ts`) exige as 20 cores com hex único, contraste de 3 para 1 contra cada fundo do app (2,5 para 1 no Âmbar), texto da sigla com 4,5 para 1 (o mínimo para texto) e ΔE de pelo menos 12 entre as 20, incluídas UPR, ACI, MNV e o cinza sem cor, além de a paleta ter mais cores que a sala tem vagas. O cálculo fica em `frontend/shared/lib/color-math.ts`, sem dependência nova.
- `ColorSwatchPicker` (`frontend/shared/components/color-swatch-picker.tsx`) substitui os três seletores antigos: `radiogroup` com setas, Home e End, nome da cor embaixo, cor em uso esmaecida com a sigla de quem usa, 10 colunas para partidos (2 linhas) e 6 para jogadores (2 linhas). Usam o componente o lobby, a entrada na partida, o diálogo de bot, o editor do backtest e a fundação de partido (preparação e partida).
- Bot não funda nem entra em partido: a cor dele é só a de jogador, escolhida no diálogo de bot entre as livres. As cores dos partidos do computador (UPR, ACI, MNV) ficam fixas e fora da paleta de escolha.
- Conferido no navegador: seletor de 20 cores na fundação de partido, 12 cores no lobby e no diálogo de bot (com a cor do host esmaecida e a sigla dele) e sala com 12 vagas. A Eleição, o mapa por estado com contorno do lugar selecionado e o gráfico de intenção de voto foram conferidos com a paleta de 16 cores da primeira versão; as 4 cores acrescentadas depois (Vinho, Magenta, Âmbar e Musgo) passaram nos testes de contraste e ΔE, mas ainda não foram vistas no mapa.

**Aceite:** o teste da paleta passa com 20 cores de partido; fundar partido, lobby, diálogo de bot e editor do backtest usam o mesmo componente de seletor; a paleta dos jogadores tem 12 cores, `chart-1` a `chart-12`, e a sala tem 12 vagas.

### F272 · arquivado em 2026-11-13

*Kanban:* Seletores e combobox novos · Melhoria · ✅ Concluído · atende N15 · marco M26

**F272 — Seletores e combobox novos.** Serve N15. Um componente só (`OptionSelect`, em cima do Combobox do base-ui) no lugar do `select.tsx` e dos quatro combobox de Command: busca a partir de 8 opções, grupo "Indisponíveis" com o motivo escrito, lista que abre embaixo e opções de 48 px. O campo "Ações que ela opera" ganhou a variante com a contagem no botão e as ações marcadas em etiquetas (limite de 30 vindo do backend, "Só as da carteira", "Voltar ao padrão" e "Limpar"), e `/api/simulation/bots/tickers` passou a devolver código e nome da empresa.

### F273 · arquivado em 2026-11-13

*Kanban:* Convites que se escolhem e se acumulam · Melhoria · ✅ Concluído · atende N34, N23 · marco M26

**F273 — Convites que se escolhem e se acumulam.** Serve N34 e N23. Convidar o vice virou ação própria: escolher no seletor não envia nada, o botão Convidar envia e Retirar convite desfaz, na partida e no lobby. Inscrever a chapa e salvar a fundação deixam de convidar. Quem recebe acumula convites de vice e propostas de federação; aceitar um recusa os incompatíveis do mesmo tipo (vice e federação não se cruzam) e avisa quem convidou. O proponente envia uma proposta de federação por vez. O convite recusado aparece na tela da chapa e no card público do partido.

### F274 · arquivado em 2026-11-13

*Kanban:* Presidência e base do governo que valem a pena · Feature · ✅ Concluído · atende N34 · marco M26

**F274 — Presidência e base do governo que valem a pena.** Serve N34. Revisa duas escolhas antigas do arquivo morto (F95, "o ganho de governar chega só pela própria carteira", e F154, "o aliado ganha só o apoio dos grupos dele"). O presidente recebe 3 vezes o salário da partida no lugar da renda da profissão, sem perda por imprevisto, e acumula legado: 5% de um salário por ponto de aprovação acima de 40 a cada mês fechado, pago no fim normal do mandato e perdido no impeachment (`presidency.py`, `GovernmentBook._pay_legacy`). A medida de obras aceita setor e segmento: as ações do alvo sobem 2,5 vezes a fatia do PIB, até 7,5%, em rampa de 6 meses, e apontar para um setor em que o presidente tem ações tira 6 pontos de aprovação vezes a fatia dele, gravada na medida (`sector_boost.py`, `approval.favoritism_factor`). Ao aceitar o acordo, o líder aliado escolhe o setor da emenda: alta de 30 vezes a fatia do PIB por ano, até 6%, que cai quando o acordo acaba ou é rompido; o partido do computador escolhe um setor fixo, mostrado na prévia. Isenção, obra e emendas somam até 20% por setor. A proposta, a negociação e o card da base mostram o apoio mensal do acordo em verba de campanha (R$ 4.096 por mês, `voters.campaign_amount`). As regras estão em `docs/docs/como-usar/governo.md`. Ficam para o playtest: partida com salário zero não paga a presidência, salário alto pode dominar, e o presidente pode empurrar o próprio setor pela emenda de um aliado sem pagar favorecimento. O ministério para o aliado virou card próprio (F284).

### F275 · arquivado em 2026-11-13

*Kanban:* Vitória política separada do capital · Feature · ✅ Concluído · atende N34, N22 · marco M26

**F275 — Vitória política separada do capital.** Serve N34 e N22. A vitória política deixa de somar o patrimônio dos filiados: vence o partido com mais **capital político**, pontos acumulados a cada mês fechado (`backend/features/government/capital.py`, `party_capital`). Só partidos de jogador pontuam: 1 ponto por cadeira na casa em exercício; a aprovação do fechamento (0 a 100) para o partido do presidente (`governed_months` no `GovernmentState`, gravado no `APPROVAL_MEASURED`); `100 × fração cumprida` por promessa no balanço do mandato; e o impeachment tira metade do que a presidência rendeu naquele mandato. Desempate por cadeiras na casa atual. Decisões: medida aprovada não pontua por si (pesa pela aprovação); vence o partido e os filiados dividem a colocação; continua o tipo "Política", sem tipo novo nas regras (a vitória da Expansão Gestoras citada como molde ainda não existe); o ranking de partidos é por capital político em toda partida com a expansão, e a soma de patrimônio saiu de tela, diálogos e textos. O ranking individual segue em patrimônio, informativo. `PoliticalCapitalDTO` (total e as quatro parcelas) substitui `total_networth` no painel e no relatório; a página Eleição mostra total e parcelas, e a tela de resultado ganhou o pódio de partidos. Sem evento novo: partida salva recalcula pelo replay, e uma migration de dados zera o resultado guardado das partidas políticas. Limite conhecido, fora deste card: com o patrimônio fora do placar, gastar tudo em campanha deixa de ter custo na vitória política.

### F276 · arquivado em 2026-11-13

*Kanban:* Governo ruim perde aprovação · Correção · ✅ Concluído · atende N34, N41 · marco M26

**F276 — Governo ruim perde aprovação.** Serve N34 e N41.

**Sintoma.** Na Simulação #3, com SELIC de 30 a 33% (2030–2031), IPCA de 1 a 1,9% ao mês (2028–2032) e a bolsa em −99,8%, o governo de um jogador (posse em janeiro de 2031) passou 2032 inteiro com aprovação entre 26 e 30 e só caiu no 35º dos 48 meses do mandato.

**O que os eventos da partida mostram.** O contador de meses abaixo do piso funcionou. Em 2031 valeu a carência de 12 meses. Em 2032 a aprovação nunca fechou abaixo de 25, então o contador ficou em 0. De maio a outubro de 2033 fechou em 24, 23, 22, 21, 20 e 19: o contador chegou a 6, o pedido de impeachment abriu e foi aprovado por 79 a 22 em 30/11/2033. A aprovação de 21 com contador em 0, de janeiro de 2034, é do governo interino do computador, para quem o piso não conta por desenho (`_close_month`, `backend/features/government/government_book.py:2970-2976`). A satisfação dos investidores em 0,0006 é só o caminho de um terço por mês até um alvo 0.

**Causa.** A aprovação satura. Cada fator do alvo tem um limite de punição em `backend/features/government/approval.py`: a inflação para de pesar 5 pontos percentuais além da meta mais 1,5 (`INFLATION_CAP`; com meta de 3%, inflação de 25% ao ano pune igual a 9,5%), a bolsa para em 3 passos de 10% (`STOCKS_CAP`; −99,8% pune igual a −25%) e o juro real para 6 pontos fora da faixa de 2% a 7% (`REAL_RATE_CAP`). Com tudo no limite, o alvo geral sem medidas fica em 17,6, contra um piso de 25. Uma crise comum dá 24,6 e a catástrofe total dá cerca de 20: sete pontos separam as duas, e uma medida popular soma 6 por unidade de reação.

**Como reproduzir.** `group_target` para os seis grupos com meta 3%, IPCA 22%, SELIC 31%, bolsa −99,8% em 12 meses, desemprego 13% e prêmio de risco de 6 pontos, sem medidas: `overall` dos alvos dá 20,6.

**O que muda.**

1. Punição que segue crescendo. No lado ruim de inflação, juro real e bolsa, o que passa do limite atual continua tirando pontos com metade do peso (constante nova, `EXCESS_WEIGHT = Decimal("0.5")`). A distância usada na conta deixa de ser `min(distância, limite)` e passa a ser `limite + (distância − limite) × 0,5` quando a distância passa do limite. Vale para: inflação acima da meta mais 1,5 (`inflation_factor`), juro real abaixo de 2% e acima de 7% (`real_rate_factor`) e bolsa em queda (`stocks_factor`). O lado bom continua com o teto de hoje (inflação abaixo da meta, bolsa em alta), e desemprego e prêmio de risco ficam como estão. `group_target` continua limitando o alvo de cada grupo a 0–100. Piso (25), carência (12) e meses seguidos (6) não mudam.
2. Dentro dos limites atuais nada muda: governo medíocre e governo bom recebem exatamente os mesmos pontos de antes.
3. Governo do computador continua imune ao piso, e a tela passa a dizer isso. O DTO da aprovação (`GovernmentApproval`, em `backend/core/dto/government.py`) ganha um campo booleano que diz se o piso vale para o governo em curso (falso quando `term.president_id` é nulo). Em `frontend/features/government/components/impeachment-floor.tsx` o contador ("N de 6") dá lugar a "não conta", com o texto "Governo do computador: o piso de impeachment não conta e ele fica até o fim do mandato"; `impeachment-alert.tsx` segue sem aparecer nesse caso. Rodar `pnpm openapi`.
4. `docs/docs/como-usar/governo.md` (trecho do piso e dos fatores) explica a regra da metade do peso com um exemplo (inflação de 12% com meta de 3%: 5 pontos percentuais cheios mais 2,5 pela metade) e o caso do governo do computador.

**Testes.** Em `tests/test_government_rules.py`, a tabela de cenários do aceite e um teste de que cada fator, no valor exato do limite e antes dele, devolve os mesmos pontos de hoje. Em `tests/test_government_book.py`, um governo de jogador sob o cenário de catástrofe abre o pedido de impeachment no 18º fechamento do mandato (12 de carência mais 6), e o governo do computador no mesmo cenário mantém o contador em 0. Em `frontend/features/government/lib`, o rótulo do piso para o governo do computador.

**Aceite:** alvo geral sem medidas, com meta de inflação de 3% (IPCA, SELIC, bolsa em 12 meses, desemprego, prêmio de risco):

- neutro (4,5%, 9%, +5%, 9%, 0): 50,0, igual a hoje;
- medíocre (8%, 13%, −10%, 10%, 1 ponto): 34,6, igual a hoje;
- tudo no limite (9,5%, 22,5%, −25%, 13%, 6 pontos): 17,6, igual a hoje;
- crise (12%, 18%, −30%, 12%, 3 pontos): 20,0 (hoje 24,6);
- crise forte (15%, 22%, −45%, 13%, 4 pontos): 13,1 (hoje 23,4);
- Simulação #3 em 2031–2032 (22%, 31%, −99,8%, 13%, 6 pontos): abaixo de 5 (hoje 20,6).

Com o cenário da Simulação #3 mantido desde a posse, o pedido de impeachment de um governo de jogador abre no 18º mês do mandato (na partida, abriu no 34º).

### F277 · arquivado em 2026-11-13

*Kanban:* Jornal com eventos raros em destaque e manchetes variadas · Melhoria · ✅ Concluído · atende N31 · marco M26

**F277 — Jornal com eventos raros em destaque e manchetes variadas.** Serve N31.

**O que existe.** Na Simulação #3 o jornal teve 6.815 notícias em 14 anos, e duas regras fizeram 88,6% delas: movimento forte de ativo (3.053, cerca de 18 por mês) e máxima de 52 semanas (2.983, cerca de 18 por mês); "GOLD11 renova a máxima de 52 semanas" saiu 195 vezes. As duas moram em `backend/features/newsroom/companies.py`: movimento forte é toda variação acima de 5% no dia (`MOVE_THRESHOLD`), até 3 por pregão, sem intervalo por ativo; a máxima é todo fechamento acima do maior dos últimos 252, até 3 por pregão, então um ativo em tendência de alta vira notícia quase todo dia. No meio disso se perdem os eventos raros: campanha teve 43 notícias (15 ações que viralizaram), vida de partido 11, e programa lançado, rebatizado ou extinto 3. As manchetes do governo (`backend/features/government/headlines.py`, 30 construtores) têm texto fixo; só a redação das empresas sorteia variações com `pick()` (`backend/features/newsroom/text.py:156-161`), semeado por partida, dia e ativo.

**O que muda e por quê.**

1. Três tipos de notícia novos, que abrem a janela central por padrão (nível `WINDOW` sem `fixed`: a manchete grande por 8 segundos, sem pausar a sala), cada um rebaixável nas preferências como os outros:
   - ação de campanha crítica: tudo o que `campaign_action` (`headlines.py:535-581`) publica, que já é só o dado crítico (viraliza ou dá errado) e o ataque;
   - programa com nome: o lançamento, o rebatismo e a extinção de `program_event` (`headlines.py:353-361`), que hoje saem como medida votada;
   - ruptura de partido: `expelled`, `federation_formed`, `federation_left`, `deal_broken` e `deal_left`.
   Promessas e apoio no 2º turno continuam no tipo de campanha; fundação, doação e acordo fechado continuam em vida de partido. Os tipos entram em `NewsType` (`backend/core/enum/__init__.py:1073-1092`), no registro (`backend/features/notifications/registry.py`, na posição de importância deles, com rótulo e descrição; a descrição do tipo de campanha perde o que saiu) e no catálogo do front (`frontend/features/news/lib/catalog.ts`). `news.news_type` é texto, então não há migration; as notícias já gravadas ficam com o tipo antigo. Rodar `pnpm openapi`.
2. Movimento forte relativo ao próprio ativo. Vira notícia a variação do dia que é pelo menos K vezes a oscilação normal daquele ativo, e não mais um percentual fixo. Oscilação normal é a média do tamanho da variação diária (em módulo) dos últimos 126 pregões; com menos de 63 pregões de histórico vale o limite fixo de 5% de hoje. Exemplo: uma ação que costuma mexer 2% por dia só é notícia a partir de 6%; um fundo imobiliário que costuma mexer 0,8% é notícia com 3%. K começa em 3 e há um piso absoluto de 3%, para que um ativo quase parado não vire manchete com 1%. A ordem dentro do pregão passa a ser por quantas vezes a oscilação normal, e ficam os 3 por pregão. O texto da manchete não muda. K é calibrado numa partida de 10 anos até a meta do aceite.
3. Máxima de 52 semanas só no rompimento: vira notícia quando o fechamento supera uma máxima que já tinha pelo menos 63 pregões (3 meses) de idade. A renovação diária de quem está em tendência de alta deixa de sair, e o mesmo ativo aparece no máximo 4 vezes por ano.
4. Três redações para cada manchete do governo. Cada um dos 30 construtores de `headlines.py` passa a ter 3 variações de título (e de linha fina, onde há), escolhidas por `pick()` com a semente da partida, a data e o identificador do fato (medida, partido ou ação), para a sala inteira ver o mesmo texto e a repetição da leitura dar o mesmo resultado. Os construtores passam a receber essa semente de quem os chama em `government_book.py`. As linhas finas de campanha hoje escolhidas por `action_id % len` passam para o mesmo `pick()`. São cerca de 90 títulos, escritos no tom do jornal e com os mesmos dados da manchete atual.
5. `tests/test_newsroom.py` cobre o limite relativo (os dois exemplos acima, o piso de 3% e o histórico curto) e o rompimento da máxima; `tests/test_government_headlines.py` passa a conferir, por construtor, 3 textos distintos entre sementes e o mesmo texto para a mesma semente; os testes do front cobrem os tipos novos no catálogo e na fila da janela (`frontend/features/news/lib`).
6. `docs/docs/como-usar` (página do jornal) descreve os tipos novos e a regra do movimento forte.

**Como medir.** Uma partida de 10 anos rodada pela linha de comando no banco de teste, contando as notícias por tipo e por manchete na tabela `news`, antes e depois.

**Aceite:** na partida de 10 anos, movimento forte fica entre 5 e 8 notícias por mês em média (hoje cerca de 18) e máxima de 52 semanas em até 4 por mês (hoje cerca de 18); os dois tipos somados ficam abaixo de 60% do total (hoje 88,6% de 6.815); nenhum ativo tem mais de 4 manchetes de máxima no mesmo ano; cada construtor de manchete do governo tem 3 redações.

### F278 · arquivado em 2026-11-13

*Kanban:* Imprevistos e eventos de vida mais variados · Feature · ✅ Concluído · atende N23 · marco M26

**F278 — Imprevistos e eventos de vida mais variados.** Serve N23.

**O que o jogador passa a poder fazer.** Viver imprevistos que não são sempre os mesmos três nem sempre ruins: cerca de 20 tipos, um em cada quatro deles bom (dinheiro que entra), com o texto da profissão de cada um e dois eventos próprios da profissão. O anfitrião regula a frequência por família de evento no lobby, em vez de criar tipos.

**O que existe.** Três tipos de fábrica em `DEFAULT_LIFE_EVENTS` (`backend/core/dto/life.py:35-60`): conserto do carro (1 despesa mensal, peso 3), despesa de saúde (2 despesas, peso 2) e demissão (pula o próximo salário, peso 1). Dois efeitos (`LifeEventEffect`: `CASH_OUT` e `SKIP_NEXT_SALARY`). O sorteio é diário, semeado pela semente da partida e pelo dia, e o evento é o mesmo para a sala inteira (`backend/features/simulation/life_events.py:35-61`); a aplicação fica em `simulation.py:1408-1478`. A demissão já tem versão por profissão (demissão, perda do bico, imóvel vago, pelo `income_loss` de `backend/core/professions.py:108-142`) e pula quem não tem. O lobby deixa criar tipos (`frontend/features/lobby/components/life-events-editor.tsx`), que só repetem os dois efeitos; a frequência é uma só para tudo (`unexpected_per_year`: Nenhum 0, Raros 1, Normais 3, Frequentes 6) e o peso de cada tipo não aparece na tela. `validate_life_events` limita a 12 tipos.

**Mecanismo.**

1. Efeito novo `CASH_IN`: credita no caixa o múltiplo da despesa mensal do jogador. O multiplicador de saúde do aposentado continua valendo só para despesa de saúde.
2. Três famílias (enum novo): despesas, renda e emprego, e eventos bons. Cada tipo do catálogo tem família, peso e múltiplo. Catálogo de fábrica, com o múltiplo da despesa mensal entre parênteses (textos e múltiplos podem ser ajustados na implementação, mantendo a contagem e a regra do item 3):
   - despesas: conserto do carro (1), despesa de saúde (2), conserto da casa (1,5), eletrodoméstico queimado (0,75), celular quebrado (0,5), multa de trânsito (0,25), veterinário (0,5), dentista de urgência (0,75), golpe no cartão (1), viagem de emergência (1), rateio extra do condomínio (0,5), ajuda a um parente (1);
   - renda e emprego: demissão (pula o salário) e revés da profissão (1);
   - eventos bons: restituição do imposto de renda (1), bônus do trabalho (1), prêmio de sorteio (0,5), herança pequena (3), venda de um bem usado (0,75), presente de família (0,5) e boa fase da profissão (1).
3. Um em quatro é bom: com as três famílias em Normal, os pesos dos eventos bons somam 25% do peso total, e o valor esperado dos bons fica abaixo do dos ruins, para o imprevisto continuar sendo, na média, um custo que pede reserva de emergência.
4. Profissão em dois níveis, os dois com o mesmo efeito e o mesmo tamanho para todos, para nenhuma profissão sair favorecida:
   - texto por profissão nos eventos genéricos em que faz sentido (o bônus vira PLR para o CLT, gratificação para o servidor, cliente que pagou adiantado para o empresário, 13º adiantado para o aposentado, bico extra para quem recebe auxílio, reajuste do aluguel para quem vive de aluguel);
   - "revés da profissão" e "boa fase da profissão" são dois tipos do catálogo que cada jogador vive na versão da própria profissão (empresário: máquina quebrada e contrato grande; quem vive de aluguel: reforma entre inquilinos e multa de rescisão recebida; e um par para cada uma das outras quatro profissões). É o mesmo padrão que a demissão já usa, e o sorteio continua único para a sala.
   Os textos por profissão moram junto do catálogo, que sai do arquivo de DTO para um módulo próprio em `backend/core/`.
5. Frequência por família no lobby. A frequência geral (`unexpected_per_year`) continua e diz quantos imprevistos por ano saem com tudo em Normal. Cada família ganha Desligado, Raro, Normal ou Frequente, que multiplica a chance dos tipos dela por 0, 0,5, 1 ou 2; dentro da família, cada tipo tem liga e desliga. Deixar despesas em Frequente não tira chance dos eventos bons. A chance por pregão de um tipo é `(por ano ÷ 252) × (peso do tipo ÷ peso total do catálogo ligado em Normal) × multiplicador da família`, e a correção da demissão pelo desemprego continua. As configurações da sala ganham o nível de cada família, com Normal de padrão.
6. Sai a criação de tipos: `life-events-editor.tsx` perde "Adicionar tipo", o nome editável, o campo de valor e o seletor de efeito, e passa a mostrar as três famílias com o controle de frequência e os tipos de cada uma com o interruptor; `lib/simulation-form.ts` perde `newLifeEvent()`. O DTO do tipo continua aceitando os tipos criados em salas e partidas já salvas (família deduzida do efeito), e `validate_life_events` sobe o limite para caber o catálogo. Partida em andamento segue com os tipos com que foi criada.
7. Exibição: o aviso em tempo real (`frontend/shared/notifications/life-notifications.tsx:30-55`) usa aviso de sucesso e valor com sinal de mais para os bons, e o histórico (`backend/features/simulation/life_history.py`, `frontend/features/goal/components/life-history.tsx`) mostra o sinal certo. O nome mostrado é o da profissão do jogador. O contador de imprevistos conta só os que tiram dinheiro ou salário.
8. Mudou DTO: `pnpm openapi`; se as configurações da sala não forem JSON livre, `pnpm db:revision`. `docs/docs/como-usar/lobby.md` (trecho dos imprevistos) descreve as famílias e o catálogo.

**Testes.** `tests/test_life_events.py`: `CASH_IN` credita o valor certo; em 10.000 sorteios semeados com tudo em Normal, os eventos bons ficam entre 22% e 28%; família em Desligado nunca sai e em Frequente sai o dobro; os dois tipos de profissão aplicam o mesmo valor a todos, com o texto de cada profissão. `tests/test_life_history.py` e `test_unexpected_count.py` para o sinal e o contador; `simulation-form.test.ts` e `life-history.test.ts` no front.

**Aceite:** o catálogo de fábrica tem pelo menos 20 tipos; com tudo em Normal, de 22% a 28% dos sorteios são eventos bons (10.000 sorteios); numa sala com as seis profissões, o mesmo sorteio aplica o mesmo valor a todos; o lobby não cria mais tipos e uma sala salva com tipo criado continua abrindo e jogando.

### F280 · arquivado em 2026-11-13

*Kanban:* Corrida eleitoral com bots sempre presentes e campanha que pesa · Melhoria · ✅ Concluído · atende N34, N8 · marco M26

**F280 — Corrida eleitoral com bots sempre presentes e campanha que pesa.**

Disputa sempre com os três partidos do computador, fundo público mensal de R$ 8.000 por concorrente (metade igual, metade por cadeiras), teto de contribuição de R$ 8.000 por filiado, caixa único do partido e sobra virando propaganda com √sobra ÷ 128. Limite conhecido: os finalistas chegam ao 2º turno com o caixa zerado até o playtest decidir.

### F281 · arquivado em 2026-11-13

*Kanban:* Banco Central autônomo que decide em reunião, em passos de 0,25, olhando através do imposto · Correção · ✅ Concluído · atende N34 · decisões D20 · marco M26

**F281 — Banco Central autônomo que decide em reunião, olhando através do imposto.** O Banco Central autônomo decide só nos dias de reunião do Copom (`meeting_days`, hoje em `backend/core/copom.py`, com `SELIC_STEP` e `to_step`): em cada uma leva a regra do dia ao passo de 0,25 ponto, a até 1 ponto da decisão anterior (`autonomous_decision` e `AUTONOMOUS_CAP` em `monetary.py`), e mantém os pontos até a reunião seguinte. A SELIC da partida é a história do dia mais esses pontos segurados (`EconomyLayer.autonomous_points`, `layer.py`); sem efeito do governo nada muda, e entre `first_day` e a primeira reunião o desvio vale 0. A regra olha através do imposto: `reading_points` tira de `inflation_points` o degrau de preço do imposto sobre consumo (`consumption_points`), então um corte do imposto não derruba a SELIC; a regra também alimenta o presidente computador e o esperado do mercado, e a linha do imposto sobre consumo no painel da economia deixa de mostrar efeito na SELIC e na bolsa. No futuro gerado (`synthetic.py`, `_decided_in_meetings`), a SELIC inteira (trecho sorteado mais regime e surto) só muda no pregão seguinte a uma reunião, em múltiplos de 0,25, e o CDI anda colado; o gráfico "Juros e inflação" fica com no máximo 8 marcadores do Copom por ano no futuro. Limite conhecido: no trecho histórico da partida o marcador soma as mudanças reais da história e as reuniões do autônomo, e a SELIC absoluta segue a da história (o múltiplo de 0,25 vale para o desvio do autônomo).

### F282 · arquivado em 2026-11-13

*Kanban:* Texto dos gráficos com no mínimo 12 px · Correção · ✅ Concluído · atende N15 · marco M26

**F282 — Texto dos gráficos com no mínimo 12 px.** Serve N15. O texto de gráfico (eixos, legendas, rótulos e tooltips) usa um token só, de 12 px: `CHART_TICK` e `CHART_FONT_SIZE`, em `shared/lib/chart-text.ts`. O teste de tamanho mínimo passou a pegar também `fontSize` literal abaixo de 12, além das classes `text-[Npx]`.

### F283 · arquivado em 2026-11-13

*Kanban:* Campos de valor com o mesmo controle de R$ e de porcentagem · Melhoria · ✅ Concluído · atende N15 · marco M26

**F283 — Campos de valor com o mesmo controle de R$ e de porcentagem.**
Os campos de valor (comprar e vender Tesouro, amortizar, aplicar e resgatar renda fixa, doação) ganharam o mesmo controle R$ | % antes dos atalhos, com Shift para ver o outro modo, modo lembrado por tipo de campo e atalho em R$ que para no máximo. A contribuição mensal ficou só com a grade de quatro. Conferido no app em todos menos doação e contribuição mensal.

## Itens descartados

### F15 · arquivado em 2026-10-17

*Kanban:* Cliente desktop em Tauri · feature · 🚫 Descartado

**F15 — Descartado.** 🚫 O núcleo do Tauri é Rust: o backend Python iria como sidecar (o executável do PyInstaller dentro do pacote Tauri), o que dá dois executáveis, toolchain Rust nas três plataformas da CI e um WebView diferente em cada SO. O ganho — janela própria em vez de aba do navegador — é o mesmo da F14, que faz isso em Python dentro do executável atual. Electron daria o mesmo resultado com ~150 MB de Chromium a mais. Em qualquer dos dois, os convidados do multiplayer continuam no navegador.

### F59 · arquivado em 2026-10-17

*Kanban:* Separar em dois executáveis: cliente e servidor · feature · 🚫 Descartado · atende N2

**F59 — Descartado.** 🚫 Separar o app em dois executáveis, um cliente e um servidor. Hoje o app já é cliente e servidor: o executável é o servidor, e o navegador é o cliente, que o próprio servidor entrega pronto. Separar não traz nada que isso não dê, e custa três coisas: (1) os convidados do multiplayer teriam de baixar um programa em vez de abrir um link, o que fere a N2; (2) quem hospeda passaria a abrir dois programas, e a versão do cliente teria de combinar com a do servidor, coisa que hoje é garantida porque o front vai dentro do servidor; (3) a CI geraria o dobro de artefatos nos três sistemas. O Tauri não muda a conta: o Rust nas três plataformas e o motor web diferente em cada sistema continuam (F15), e o ganho de uma janela própria é o da F14, em Python, dentro do executável atual. O que a ideia buscava, um servidor sem jogador na frente, é a F60.

### F99 · arquivado em 2026-10-22

*Kanban:* Partidos na expansão Governo · feature · 🚫 Descartado

**F99 — Descartado.** 🚫 Juntada ao núcleo da expansão Governo (F95): os partidos deixaram de ser camada opcional por cima da eleição e viraram a única forma de concorrer, com fundador, filiados, contribuições, expulsão e ranking de partidos decididos no card da F95.

### F109 · arquivado em 2026-10-23

*Kanban:* Estratégia em .py do usuário carregada pelo host · feature · 🚫 Descartado · atende N4

**F109 — Descartado.** 🚫 Estratégia em `.py` do usuário carregada pelo host: pasta ao lado do `config.toml`, processo filho com timeout por tick, cópia do código no banco ao iniciar a partida e contrato de bibliotecas no build. Descartada pela D16: quem desenvolve acrescenta a estratégia como classe do app, e ela vale no automático, nos bots e no backtest; quem tem só o executável usa o bot pela API (F108). O único caso que sobraria, estratégia própria no backtest sem mexer no código, não paga o custo de manter processo filho, timeout, pasta, cópia no banco e lista de bibliotecas, nem o risco de executar código de fora no PC do host. As medições desse caminho estão na D5.

### F171 · arquivado em 2026-10-31

*Kanban:* Ordens de abertura na preparação do lobby · feature · 🚫 Descartado

**F171 — Descartado.** 🚫 A partida nasce pausada no 1º dia: ligar o automático, com os parâmetros salvos no perfil (F170), ou comprar na mão custa um clique antes de soltar o relógio. Executar pelo lobby exigiria guardar a escolha na partida, aplicá-la no 1º pregão e tratar quem saiu da sala, só para economizar esse clique.

### F172 · arquivado em 2026-10-31

*Kanban:* Meta pessoal na preparação do lobby · feature · 🚫 Descartado

**F172 — Descartado.** 🚫 A meta é da partida. Com meta por jogador, numa corrida à meta ganha quem escolhe a menor; e a preparação do lobby existe para tirar o que o jogador refaz igual a cada partida, não para mudar a regra da vitória.

### F183 · arquivado em 2026-11-04

*Kanban:* Como jogar sem cobrir a tela · Melhoria · 🚫 Descartado · atende N15, N25

**F183 — Descartado.** 🚫 Sem problema na tela: o usuário avaliou os retratos de 03/11 e não vê a aba do Como jogar nem o balão cobrindo conteúdo que justifique um desenho. A F179 segue com a topbar, e o palco do Como jogar fica para depois da avaliação dele.

## Marcos

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

### M13 · arquivado em 2026-10-22

*Marco:* Mais jeitos de jogar · serve N21, N22, N23

> **Objetivo:** Partidas com outras regras e objetivos: sem assistências, em equipes, com conquistas.

### M6 · arquivado em 2026-10-25

*Marco:* Estratégia contra estratégia · serve N4, N8, N10

> **Objetivo:** Pôr bots na sala e rodar uma partida só de estratégias, do começo ao fim, sem esperar.

### M4 · arquivado em 2026-10-26

*Marco:* Estratégias automáticas · serve N4

> **Objetivo:** Escrever ou escolher uma estratégia e deixar o simulador operar com ela.

### M17 · arquivado em 2026-10-31

*Marco:* Eleição disputada · serve N34

> **Objetivo:** Uma eleição decidida por grupos de eleitores que lembram promessas e traições, com campanha de ações, 2º turno com virada e a aprovação medida pelos grupos; sai na versão 3.1.

### M19 · arquivado em 2026-10-31

*Marco:* Governo com conta a fechar e Congresso · serve N34

> **Objetivo:** Um governo com orçamento e dívida, em que gastar e isentar têm preço, e um Congresso eleito, em que cada partido orienta a própria bancada; sai na versão 3.2.

### M16 · arquivado em 2026-10-31

*Marco:* Partida sem tropeços · serve N4, N8, N15, N33, N34, N40 · itens F144, F146, F147, F148, F149, F155, F156, F162

> **Objetivo:** Repetir uma partida com amigos, do lobby ao fim, sem os erros e as travas que o playtest mostrou; sai na versão 3.1, junto da eleição disputada.

### M20 · arquivado em 2026-11-04

*Marco:* Preparação no lobby · versão 3.3 · serve N39, N15, N40, N24 · itens F143, F168, F178, F184, F189, F188, F187, F185, F209, F207, F213, F214, F215, F181, F182, F203, F190, F204, F205, F206, F208, F210, F173, F174, F169, F170, F212, F157, F186, F180

> **Objetivo:** Cada jogador chega à partida já preparado no lobby, e as telas que mudaram desde a 3.0 voltam a formar um conjunto.

### M21 · arquivado em 2026-11-07

*Marco:* Juros e Tesouro · versão 3.4 · serve N34, N39 · itens F191, F217, F216, F218, F97, F165, F177, F222, F192, F219, F223, F224, F228, F230, F231, F229

> **Objetivo:** O governo decide a SELIC, e os títulos do Tesouro rendem pelo risco que ele cria.

### M23 · arquivado em 2026-11-07

*Marco:* Congresso e eleição · versão 3.5 · serve N34 · itens F195, F164, F175

> **Objetivo:** As bancadas, as regiões e as federações viram decisões de governo e de campanha.

### M22 · arquivado em 2026-11-08

*Marco:* Dividendos · versão 4.0 · serve N3, N7 · itens F22, F100, F233, F234, F235, F236, F237, F238, F239, F240, F241, F242, F243, F244, F245, F220

> **Objetivo:** O preço é o negociado na época, e o ativo desdobra e paga dividendo na partida, no real e no futuro gerado.

### M26 · arquivado em 2026-11-13

*Marco:* Câmbio e Poder · versão 4.1 · serve N15, N34, N23, N11, N31, N41 · itens F250, F252, F253, F232, F254, F256, F251, F69, F257, F226, F259, F194, F260, F261, F258, F262, F263, F264, F265, F266, F267, F268, F269, F270, F271, F272, F273, F274, F275, F276, F277, F278, F280, F281, F282, F283

> **Objetivo:** O governo ganha impostos de verdade, cortes com preço e programas com nome; o crescimento sente o rombo; o mapa da eleição percorre o tempo; o viver de renda sente a economia, ganha imprevistos novos e a profissão de cada jogador; a economia traz o Focus e o dólar reage, com os ativos de fora cotados em real, protegendo a carteira, e o caixa em dólar rendendo o juro americano. Abre com os consertos e os atalhos que o playtest de 08/11 pediu.

## Decisões

### D5 · arquivado em 2026-10-23

*Glossário:* Onde roda o código de estratégia escrito pelo usuário · 🔁

### D5 — Onde roda o código de estratégia escrito pelo usuário
**Status:** 🔁 Revista (ver D16)

**Decisão:** os dois lugares, com a mesma classe base. A estratégia recebe a cada tick um contexto (data, caixa, posições, renda fixa, histórico de preços, setor e segmento, indicadores) e emite ordens por ele; o que muda de um lugar para o outro é só quem implementa o contexto.
1. **No host, num processo filho por estratégia.** O simulador carrega o `.py` de uma pasta da máquina do host e chama `next()` a cada tick, esperando a resposta até um tempo máximo. Estourou o tempo, o host mata o processo e desliga a estratégia, e o jogador volta ao manual. É onde rodam a estratégia do próprio host, os bots (F16) e o backtest (F19).
2. **Como cliente da API, na máquina do jogador remoto.** O mesmo arquivo roda contra as rotas HTTP e o tick do Socket.IO que a interface já usa.

O código mora numa pasta, para editar no editor de sempre; ao iniciar a partida, o texto de cada estratégia usada é gravado no banco junto da simulação, e retomar usa essa cópia. A estratégia importa o que o executável empacota: numpy, pandas e a biblioteca padrão.

**Por quê:** o spike (F7) mediu as duas opções no app real.
- **Carregar um `.py` de fora do executável funciona.** Num executável de teste com o mesmo conjunto de módulos do app (a mesma análise do spec, em arquivo único), o `importlib` carregou um arquivo solto em 0,8 ms. numpy, pandas, requests e os 30 módulos da biblioteca padrão testados importaram; scipy, scikit-learn, statsmodels, matplotlib (excluído no spec), ta e httpx não existem lá dentro. `assert` e docstrings da estratégia continuam valendo, apesar do `optimize=2` do spec.
- **Só um processo separado corta qualquer travamento.** Com 0,5 s de orçamento por tick: uma thread com exceção injetada corta um laço Python em 0,55 s, mas um laço que roda dentro de C (`sum(range(10**12))`) segura o GIL e congela o servidor inteiro, inclusive o código que aplicaria o timeout; e, enquanto um laço fugitivo vive em outra thread, o tick normal dobra de tempo (188 → 362 ms). O `sys.monitoring` na mesma thread corta o laço Python, custando 27% a mais no código da estratégia (0,60 → 0,76 ms), mas não corta laço em C nem `time.sleep`. O processo filho é morto em 0,51 s em todos os casos. Ele sobe em 115 ms (228 ms no executável), uma vez por estratégia, e a ida e volta de cada tick custa 0,07 ms mandando só o dia novo, ou 5 ms mandando o mercado inteiro (40 ativos × 200 pregões, 352 KB).
- **O cliente da API funciona sem mudar o servidor, mas o tick não o espera.** Um bot em Python pegou o cookie em `/api/session/init`, entrou na partida, assinou o tick no Socket.IO e mandou uma ordem a mercado por dia, numa segunda instância do app com o mercado sintético dos testes. Na mesma máquina, a ordem foi aceita 6 a 9 ms depois do tick, em 100% dos ticks, a ×1, ×10 e ×100. Com 80 ms de atraso simulado (rede ou estratégia pesada), ×1 e ×10 seguiram em 100%; a ×100, com um tick a cada 36 ms, o bot agiu em 73 de 210 ticks (35%), e 72 dessas 73 ordens caíram num dia posterior ao que ele analisou. Com o mercado real o tick leva 0,6 a 0,9 s (D4), então um jogador remoto com menos de 100 ms de rede acompanha; o backtest, que não espera entre ticks, não comporta estratégia remota.
- **Nenhum dos dois lugares é sandbox.** O processo filho lê disco e rede como o próprio host. Por isso o host roda só o código da pasta dele, e o jogador remoto roda o dele na própria máquina. A pasta é o único caminho do código até o host: ser host é ter o nickname do `config.toml`, e com o host desconectado qualquer jogador assume esse nickname por `/api/user/claim` (o bot do spike fez isso), então uma rota de envio de estratégia restrita ao host executaria código de qualquer um.
- **Pasta mais cópia no banco.** A pasta deixa editar no editor; a cópia faz a partida retomada decidir com o mesmo código que a jogou até ali, em vez de seguir com o arquivo editado depois.

**Consequências:** a classe base ganha o contexto e o jogador dono da estratégia (hoje ela só recebe o `MatchingEngine`, sem `client_id`). O `MarketData` guarda só os 30 últimos candles, então o histórico longo (a média de 200 dias da F9) vem do banco, na versão de séries da partida (D7). A renda fixa só volta ao caixa no vencimento, então uma estratégia não tira dinheiro dela antes da F71. O estado interno da estratégia (atributos do objeto) não sobrevive à retomada: a estratégia deriva o que precisa do contexto, que tem o histórico. O PyInstaller só empacota o que o app importa, então a lista de bibliotecas prometidas é conferida no build da release. Reabre se o custo por tick do processo filho pesar no backtest ou se as estratégias pedirem com frequência uma biblioteca que o executável não traz.

## Necessidades

### N5 · arquivado em 2026-11-13

*Glossário:* Saber quanto risco foi corrido para chegar num resultado · —

**N5. Saber quanto risco foi corrido para chegar num resultado**
Retorno sozinho não diz se a estratégia foi boa: ganhar 20% passando por uma queda de 50% no meio do caminho é diferente de ganhar 20% de forma estável.

### N6 · arquivado em 2026-11-13

*Glossário:* Comparar resultados de simulações diferentes · —

**N6. Comparar resultados de simulações diferentes**
Pôr lado a lado o desempenho de partidas distintas (a mesma pessoa em duas simulações, duas estratégias em períodos iguais).

### N16 · arquivado em 2026-11-13

*Glossário:* Ver a carteira e o mercado por setor e segmento · —

**N16. Ver a carteira e o mercado por setor e segmento**
Saber quanto está em bancos, em energia, em varejo; e poder escrever estratégias que decidem por setor.

### N17 · arquivado em 2026-11-13

*Glossário:* Enxergar a estrutura do banco e esboçar mudanças nela · —

**N17. Enxergar a estrutura do banco e esboçar mudanças nela**
Ter uma visão do schema atual — tabelas, colunas, relações — para entender o que existe e conversar sobre uma modelagem nova ("e se fosse 1-N aqui?") antes de virar código.

### N18 · arquivado em 2026-11-13

*Glossário:* Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia · —

**N18. Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia**
Diversificar só funciona entre ativos que não caem juntos. Sem medir isso, duas posições "diferentes" podem ser a mesma aposta.

### N27 · arquivado em 2026-11-13

*Glossário:* Entrar numa partida que já começou · —

**N27. Entrar numa partida que já começou**
Quem chega depois do início, ou volta a uma partida salva sem ter jogado nela, precisa poder participar sem estragar a conta de quem já está jogando: com depósito inicial, cor própria e o mesmo ranking.

### N28 · arquivado em 2026-11-13

*Glossário:* Liberar uma vaga sem depender de o jogador sair · —

**N28. Liberar uma vaga sem depender de o jogador sair**
Com a sala cheia, ou com uma partida salva que não comporta quem está nela, o host precisa poder abrir a vaga sozinho, em vez de pedir pelo chat para alguém fechar a aba.

### N29 · arquivado em 2026-11-13

*Glossário:* Saber o que cada jogador está fazendo enquanto a partida não começa · —

**N29. Saber o que cada jogador está fazendo enquanto a partida não começa**
Na espera do lobby, "Online" diz só que a pessoa está lá. Saber que ela está na Central de dados ou olhando o resultado da última partida dá vida à sala e explica a demora de quem ainda não está pronto, como o "Navegando nos menus" dos jogos online.

### N30 · arquivado em 2026-11-13

*Glossário:* Repetir uma configuração de partida sem montá-la de novo · —

**N30. Repetir uma configuração de partida sem montá-la de novo**
A cada feature nova a partida ganha mais o que configurar (período, capital, regras, modo de jogo, o futuro gerado). O host quer salvar a combinação que gosta e voltar a ela num clique, em vez de refazer tudo a cada partida.

### N32 · arquivado em 2026-11-13

*Glossário:* Saber como foi o mês sem montar a conta · —

**N32. Saber como foi o mês sem montar a conta**
Com o tempo correndo, um mês passa em segundos. Quanto o patrimônio andou, se bateu o CDI, o que rendeu e o que afundou, quanto entrou de provento e saiu de imposto: tudo isso existe espalhado pelas telas, e ninguém para a partida para juntar.

### N35 · arquivado em 2026-11-13

*Glossário:* Tirar da lista as partidas que não interessam mais · —

**N35. Tirar da lista as partidas que não interessam mais**
Partidas de teste, abandonadas no começo ou repetidas se acumulam em "Simulações salvas" e na comparação de partidas, e hoje não há como apagar nenhuma: a lista só cresce, e achar a partida que importa fica cada vez mais difícil.

### N36 · arquivado em 2026-11-13

*Glossário:* Encontrar rapidamente os menores e maiores valores nos dados do jogo · —

**N36. Encontrar rapidamente os menores e maiores valores nos dados do jogo**
Comparar preços, taxas, quantidades e resultados sem procurar linha por linha. O usuário pediu essa capacidade em todas as tabelas de dados, incluindo estatísticas e telas de manutenção, e precisa que as atualizações da partida preservem a escolha de comparação.

### N37 · arquivado em 2026-11-13

*Glossário:* Comprar bitcoin do jeito que dá na vida real, em frações · —

**N37. Comprar bitcoin do jeito que dá na vida real, em frações**
Um bitcoin custa dezenas de milhares de reais, e hoje o jogo só vende ativo em quantidade inteira: ou se compra 1 bitcoin inteiro, ou nenhum. Na vida real se compra 0,5 ou 0,001, pelo valor que o investidor quer aplicar. Sem isso, o bitcoin fica fora do alcance de quem joga com uma carteira normal, e a partida perde um dos ativos mais conhecidos do mundo real.

### N38 · arquivado em 2026-11-13

*Glossário:* Saber quando as estatísticas vão mudar, sem achar que travaram · —

**N38. Saber quando as estatísticas vão mudar, sem achar que travaram**
As estatísticas fecham uma vez por mês de jogo, e entre uma virada e outra os números ficam parados. Sem a tela dizer isso, parece defeito; o jogador precisa saber que a atualização é mensal e quanto falta para a próxima.
