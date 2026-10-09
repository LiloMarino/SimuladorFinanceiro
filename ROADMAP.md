<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Última mudança (2026-10-09):** F31 definida com diagrama Mermaid validado por teste; F27 ganhou pódio e critério de vitória; registrada a F32 (correlação entre ativos).

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | [F4](#f4), [F25](#f25) | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | [F1](#f1), [F2](#f2), [F21](#f21) | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F8](#f8), [F9](#f9), [F10](#f10), [F19](#f19) | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | [F11](#f11), [F17](#f17), [F27](#f27) | — |
| **N6** | Comparar resultados de simulações diferentes | [F12](#f12), [F17](#f17), [F27](#f27) | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | [F13](#f13), [F29](#f29) | — |
| **N8** | Jogar contra oponentes controlados pelo computador | [F16](#f16) | — |
| **N9** | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | [F27](#f27) | — |
| **N10** | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | [F19](#f19) | — |
| **N11** | Que o cenário econômico simulado seja o histórico real | [F20](#f20) | — |
| **N12** | Continuar jogando depois do último dia com dado real | [F24](#f24) | — |
| **N13** | Saber que dados a base tem e mantê-los atualizados, fora da partida | [F21](#f21) | — |
| **N14** | Atualizar para uma versão nova sem perder as partidas salvas | [F25](#f25) | — |
| **N15** | Usar uma interface agradável e coerente, à altura de um jogo | — | — |
| **N16** | Ver a carteira e o mercado por setor e segmento | [F30](#f30) | — |
| **N17** | Enxergar a estrutura do banco e esboçar mudanças nela | [F31](#f31) | — |
| **N18** | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | [F32](#f32) | — |
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
| [**F16**](#f16) | Bots na sala | — | ⏳ |
| [**F17**](#f17) | Estatísticas em abas, como o relatório de fim de partida de um RTS | — | ⏳ |
| [**F18**](#f18) | Pontuação geral (overall) | — | 🔍 |
| [**F19**](#f19) | Modo backtest: partida só de estratégias, sem interação | — | ⏳ |
| [**F20**](#f20) | Indicadores reais (CDI, SELIC, IPCA) do Banco Central | — | ⏳ |
| [**F21**](#f21) | Central de dados, fora da partida | — | ⏳ |
| [**F22**](#f22) | Preço ajustado e proventos | — | 🔍 |
| [**F23**](#f23) | Spike: gerador de séries sintéticas | — | 🔍 |
| [**F24**](#f24) | Gerar dados futuros na Central de dados | — | ⏳ |
| [**F25**](#f25) | Migrations com Alembic | — | ⏳ |
| [**F26**](#f26) | Redesign visual | — | 🔍 |
| [**F27**](#f27) | Fechamento de partida: pódio e critério de vitória | — | ⏳ |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | — | 🔍 |
| [**F29**](#f29) | IR na venda de renda variável | — | ⏳ |
| [**F30**](#f30) | Setores e segmentos | — | ⏳ |
| [**F31**](#f31) | Diagrama do banco sempre em dia | — | ⏳ |
| [**F32**](#f32) | Ferramenta de correlação entre ativos | — | ⏳ |

<details>
<summary><strong>Concluído / decidido / descartado (13 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | [F2](#f2), [F11](#f11), [F13](#f13), [F29](#f29) | ✅ |
| **D2** | Cálculo financeiro acontece só no backend; o frontend exibe | [F2](#f2), [F11](#f11), [F12](#f12), [F17](#f17), [F32](#f32) | ✅ |
| **D3** | Dinheiro e quantidade trafegam como Decimal serializado em string | [F1](#f1) | ✅ |
| **D6** | A retomada continua no dia seguinte ao último evento | [F2](#f2) | ✅ |
| **D7** | O simulador lê as séries sem saber a origem | [F20](#f20), [F21](#f21), [F24](#f24) | ✅ |
| **D8** | Bot, modo automático e backtest são o mesmo mecanismo | [F8](#f8), [F16](#f16), [F19](#f19), [F27](#f27) | ✅ |
| **D9** | De onde nasce uma mudança de schema | [F25](#f25), [F31](#f31) | ✅ |
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
| [**F7**](#f7) | Spike: estratégia Python escrita pelo usuário | M4 | 6 | 🔍 |
| [**F20**](#f20) | Indicadores reais (CDI, SELIC, IPCA) do Banco Central | M8 | 3 | ⏳ |
| [**F3**](#f3) | Spike: banco embarcado no executável | M2 | 1 | 🔍 |
| [**F5**](#f5) | Spike: provider de túnel pela internet | M3 | 1 | 🔍 |
| [**F17**](#f17) | Estatísticas em abas, como o relatório de fim de partida de um RTS | M7 | 1 | ⏳ |
| [**F18**](#f18) | Pontuação geral (overall) | M7 | 1 | 🔍 |
| [**F21**](#f21) | Central de dados, fora da partida | M8 | 1 | ⏳ |
| [**F22**](#f22) | Preço ajustado e proventos | M8 | 0 | 🔍 |
| [**F25**](#f25) | Migrations com Alembic | M2 | 0 | ⏳ |
| [**F26**](#f26) | Redesign visual | — | 0 | 🔍 |
| [**F29**](#f29) | IR na venda de renda variável | M10 | 0 | ⏳ |
| [**F30**](#f30) | Setores e segmentos | — | 0 | ⏳ |
| [**F31**](#f31) | Diagrama do banco sempre em dia | — | 0 | ⏳ |
| [**F32**](#f32) | Ferramenta de correlação entre ativos | — | 0 | ⏳ |

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

> **Objetivo:** Abrir o executável numa máquina limpa e chegar ao lobby sem instalar nada, e atualizar de versão sem perder os saves.
>
> **Serve:** N1, N14
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F3**](#f3) | Spike: banco embarcado no executável | — | 🔍 |
| [**F4**](#f4) | Executável sobe sem banco instalado | [F3](#f3) | ⏳ |
| [**F25**](#f25) | Migrations com Alembic | — | ⏳ |

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

### M6 — Estratégia contra estratégia

> **Objetivo:** Pôr bots na sala e rodar uma partida só de estratégias, do começo ao fim, sem esperar.
>
> **Serve:** N4, N8, N10
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F16**](#f16) | Bots na sala | [F8](#f8) | ⏳ |
| [**F19**](#f19) | Modo backtest: partida só de estratégias, sem interação | [F16](#f16) | ⏳ |

### M7 — Relatório de fim de partida

> **Objetivo:** Ver o desempenho por dimensão ao longo do tempo e numa nota geral, na partida e na comparação.
>
> **Serve:** N5, N6, N9
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F17**](#f17) | Estatísticas em abas, como o relatório de fim de partida de um RTS | — | ⏳ |
| [**F18**](#f18) | Pontuação geral (overall) | — | 🔍 |
| [**F27**](#f27) | Fechamento de partida: pódio e critério de vitória | [F17](#f17), [F18](#f18) | ⏳ |

### M8 — Dados reais, cuidados fora da partida

> **Objetivo:** Indicadores e preços fiéis ao histórico, geridos numa central antes de jogar.
>
> **Serve:** N3, N11, N13
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F20**](#f20) | Indicadores reais (CDI, SELIC, IPCA) do Banco Central | — | ⏳ |
| [**F21**](#f21) | Central de dados, fora da partida | — | ⏳ |
| [**F22**](#f22) | Preço ajustado e proventos | — | 🔍 |

### M9 — Mercado sem fim

> **Objetivo:** Jogar além do último dia real sobre dados gerados que a simulação trata como reais.
>
> **Serve:** N12
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F23**](#f23) | Spike: gerador de séries sintéticas | [F20](#f20) | 🔍 |
| [**F24**](#f24) | Gerar dados futuros na Central de dados | [F21](#f21), [F23](#f23) | ⏳ |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | [F19](#f19), [F23](#f23) | 🔍 |

### M10 — Custos do mercado real

> **Objetivo:** Operar paga o que pagaria fora do simulador: impacto de preço e imposto.
>
> **Serve:** N7
>
> **Progresso:** 1/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F29**](#f29) | IR na venda de renda variável | — | ⏳ |

<details><summary>Concluído (1 item)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F13**](#f13) | Impacto de preço de ordens grandes | — | ✅ |

</details>

### Sem marco

> **Progresso:** 0/5 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F26**](#f26) | Redesign visual | — | 🔍 |
| [**F30**](#f30) | Setores e segmentos | — | ⏳ |
| [**F31**](#f31) | Diagrama do banco sempre em dia | — | ⏳ |
| [**F32**](#f32) | Ferramenta de correlação entre ativos | — | ⏳ |

---

## 1. Atende necessidade

| ID | Resumo | Atende (N#) | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F1** | Decimal como string do backend ao frontend | N3 | D3 | M1 | — | Médio | Médio | Alto | Bom | ✅ Concluído |
| **F2** | Renda fixa com cálculo único no backend e retomada consistente | N3 | D1, D2, D6 | M1 | — | Alto | Alto | Alto | Bom | ✅ Concluído |
| **F4** | Executável sobe sem banco instalado | N1 | D4 | M2 | [F3](#f3) | Médio | Médio | Alto | Excelente | ⏳ Pendente |
| **F6** | Link de convite pela internet no lobby | N2 | — | M3 | [F5](#f5) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F8** | Modo automático: estratégia do jogador roda a cada tick | N4 | D5, D8 | M4 | [F7](#f7) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F9** | Estratégias prontas de exemplo | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F10** | Guia de como escrever uma estratégia | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F11** | Métricas de risco do desempenho | N5 | D1, D2 | M5 | — | Médio | Baixo | Alto | Excelente | ✅ Concluído |
| **F12** | Comparação entre simulações | N6 | D2 | M5 | — | Médio | Baixo | Médio | Bom | ✅ Concluído |
| **F13** | Impacto de preço de ordens grandes | N7 | D1 | M10 | — | Alto | Alto | Médio | Médio | ✅ Concluído |
| **F16** | Bots na sala | N8 | D8 | M6 | [F8](#f8) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F17** | Estatísticas em abas, como o relatório de fim de partida de um RTS | N5, N6 | D2 | M7 | — | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F20** | Indicadores reais (CDI, SELIC, IPCA) do Banco Central | N11 | D7 | M8 | — | Médio | Médio | Alto | Excelente | ⏳ Pendente |
| **F21** | Central de dados, fora da partida | N13, N3 | D7 | M8 | — | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F24** | Gerar dados futuros na Central de dados | N12 | D7 | M9 | [F21](#f21), [F23](#f23) | Médio | Alto | Alto | Bom | ⏳ Pendente |
| **F25** | Migrations com Alembic | N14, N1 | D9 | M2 | — | Médio | Médio | Alto | Excelente | ⏳ Pendente |
| **F19** | Modo backtest: partida só de estratégias, sem interação | N4, N10 | D8 | M6 | [F16](#f16) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F27** | Fechamento de partida: pódio e critério de vitória | N5, N6, N9 | D8 | M7 | [F17](#f17), [F18](#f18) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F29** | IR na venda de renda variável | N7 | D1 | M10 | — | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F30** | Setores e segmentos | N16 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F31** | Diagrama do banco sempre em dia | N17 | D9 | — | — | Baixo | Baixo | Médio | Excelente | ⏳ Pendente |
| **F32** | Ferramenta de correlação entre ativos | N18 | D2 | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |

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
**F9 — Estratégias prontas de exemplo.** Estratégias simples e conhecidas, implementadas como subclasses da classe base com parâmetros editáveis na UI. Duas famílias: **referências**, para responder se uma estratégia bate o "não fazer nada" — comprar e segurar um ETF de índice (BOVA11), 100% no CDI e rebalanceamento por meta (ex.: 60% ações / 40% renda fixa, voltando à meta todo mês, como o rebalanceamento do [Finance Manager](https://github.com/LiloMarino/Finance-Manager)); e **táticas**, as três do mock atual de `strategies.tsx` — cruzamento de médias móveis de 50 e 200 dias, RSI (compra abaixo de 30, vende acima de 70) e rompimento de máxima com volume — mais momentum (compra os ativos que mais subiram nos últimos 12 meses). Servem para jogar no automático e como bots (F16) sem escrever código, como exemplo comentado para o guia da F10 e como teste da própria classe base: o rebalanceamento e o 100% CDI só cabem se a estratégia enxergar caixa, posições e renda fixa, e cada estratégia que não couber limpa aponta o que falta na API da F7/F8.

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

<a id="f16"></a>
**F16 — Bots na sala.** Serve N8; segue a D8. No lobby, o host clica "Adicionar bot" e escolhe a estratégia — as prontas da F9 ou as escritas pelo usuário na F8; cada estratégia é um "tipo de IA", como as IAs do OpenTTD — e um nome. O bot é um jogador sem socket: registro em `users` marcado como bot, carteira própria, e o motor chama o `next()` da estratégia dele a cada tick, como faz com a de um humano no automático. Aparece no ranking e nas estatísticas como qualquer jogador, com um ícone que o distingue. Quem escolhe o código do bot é o host, então ele roda no processo do host qualquer que seja a D5 — a restrição da D5 é sobre código vindo de jogador remoto. Com a F13 ligada, as ordens do bot movem preço como as de qualquer jogador. Gatilho: F8 concluída.

<a id="f17"></a>
**F17 — Estatísticas em abas, como o relatório de fim de partida de um RTS.** Serve N5 e N6. Inspiração: a tela de estatísticas do fim de partida do Age of Empires II, com uma aba por dimensão e a curva de cada jogador ao longo do tempo. `statistics.tsx` deixa de empilhar cards e passa a abas, cada uma com gráfico temporal por jogador e tabela: **Rentabilidade** (patrimônio, retorno % acumulado e as linhas de referência do CDI e do IBOV no período); **Risco** (curva de drawdown — quanto cada jogador está abaixo do próprio pico, dia a dia —, volatilidade em janela móvel de 63 pregões, ~3 meses, e um gráfico de dispersão risco × retorno com um ponto por jogador, como o do [Finance Manager](https://github.com/LiloMarino/Finance-Manager)); **Composição** (área empilhada de caixa, renda variável e renda fixa); **Operações** (ordens executadas, giro, IR pago e, com a F13 ligada, custo de impacto pago — preço executado menos preço histórico). As séries vêm prontas do backend (D2), um endpoint por aba sobre os snapshots diários da F11. O mesmo componente de abas serve a tela de Estatísticas durante a partida, o fechamento (F27) e a comparação (`/compare-simulations`, alimentada por `/api/statistics/compare`). A aba Geral entra com a F18.

<a id="f20"></a>
**F20 — Indicadores reais (CDI, SELIC, IPCA) do Banco Central.** Serve N11. `EconomicRepository` deixa de devolver constantes e lê a tabela `economic_indicator_history` (série, data, valor em `NUMERIC`, origem — D7). A busca segue o desenho do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): API SGS do Banco Central (`api.bcb.gov.br/dados/serie/bcdata.sgs.{código}/dados`), séries 12 (CDI diário), 11 (SELIC diária) e 433 (IPCA mensal), em janelas de até 10 anos (acima disso a API recusa), valor lido do texto direto para `Decimal`. A primeira carga traz a série inteira; as seguintes buscam só a partir do 1º dia do mês do último valor guardado, com intervalo mínimo de 6 horas e uma `fetch_log` registrando tentativa e sucesso; falha na busca mantém o que já está no banco. O IBOV entra na mesma tabela, pelo yfinance (`^BVSP`), como referência para os gráficos da F17. O [EconomicStatistics](https://github.com/LiloMarino/EconomicStatistics) é a referência se o IPCA precisar vir do IBGE ou se dado antigo for revisado. Na renda fixa, CDI e SELIC diários viram o fator do dia direto, sem passar pela taxa anual; o IPCA do mês é distribuído pelos dias úteis do mês. Depois do último dado real vale o último valor conhecido, como no preço das ações. Resolve a limitação de CDI constante da F2 e da F11. A busca roda na Central de dados (F21) e na inicialização, quando a última tiver mais de 6 horas.
**Aceite:** um CDB 100% do CDI comprado no primeiro dia útil de 2020 e resgatado no último rende, antes do IR, o CDI acumulado de 2020 publicado pelo Banco Central.

<a id="f21"></a>
**F21 — Central de dados, fora da partida.** Serve N13 e N3. `/import-assets` vira a Central de dados, aberta pelo lobby: uma tabela com toda série da base — ativos e indicadores (F20) — com início, fim do dado real e, quando houver, fim do dado gerado (D7), e uma barra de linha do tempo por série com o trecho real e o gerado em cores diferentes. Dela se atualiza uma série ou todas, se importa por yfinance ou CSV e, com a F24, se geram dados. Hoje a importação já fica no lobby, mas a rota segue acessível com partida ativa (`guard-layout.tsx:33` libera `/import-assets`), o backend não barra nada e o motor lê as tabelas vivas a cada tick — importar no meio de uma partida muda os preços dela. A Central passa a ser só de fora da partida: as rotas de `/api/import-assets` respondem 409 com partida ativa e o guard tira a rota durante o jogo. No lobby, o período escolhido é conferido contra a cobertura dos dados, com aviso quando passa do fim do dado real.

<a id="f24"></a>
**F24 — Gerar dados futuros na Central de dados.** Serve N12; segue a D7. Na Central (F21), "Gerar dados": o usuário escolhe até quando gerar (o início é sempre o dia útil seguinte ao último dado real de cada série), a semente e a temperatura, vendo no preview como a geração fica antes de gravar; o gerador da F23 grava as linhas nas mesmas tabelas de preço e de indicadores, com origem "gerado", e a barra da linha do tempo mostra o trecho. "Atualizar" passa a trocar o trecho gerado pelo real à medida que o real fica disponível, seguindo a regra para partidas salvas que a F23 fechar. A simulação lê as séries como sempre. Gatilho: F21 e F23 concluídas.

<a id="f25"></a>
**F25 — Migrations com Alembic.** Serve N14 e N1; segue a D9. O schema nasce de `Base.metadata.create_all` (`backend/core/database.py:69`), que cria tabela que falta mas não adiciona coluna: cada mudança de model (F11, F13) exigiu banco novo, e as próximas (estratégia por jogador, bots, indicadores, origem da série da D7) mudam o banco de novo. Segue o desenho do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): Alembic configurado no `pyproject.toml`; `pnpm db:revision "<descrição>"` gera a revisão por autogenerate a partir dos models e o arquivo é revisado antes de aplicar; o `main.py` leva o banco ao head antes de subir o uvicorn, no lugar do `create_all`; a migration roda antes numa cópia do banco e só é aplicada se nenhuma tabela perder linha ou célula preenchida; `tests/test_migrations.py` confere que as migrations chegam exatamente no schema dos models. O `sqlacodegen` sai das dependências.

**Ponto de partida.** A primeira revisão é o schema da última release (`v1.0.0`); a segunda leva dele aos models atuais (as mudanças da F11 e da F13). Banco sem `alembic_version` cujo schema bate com o da `v1.0.0` recebe `stamp` e sobe pelo upgrade normal; banco num estado intermediário (de desenvolvimento, entre releases) é recusado com mensagem, e o banco local de desenvolvimento é acertado uma vez nessa entrega. A partir daí, toda feature que mexe no banco entrega a sua migration.

A pasta de migrations entra no executável como dado do PyInstaller (`SimuladorFinanceiro.spec`). A cópia de teste depende do dialeto (D4): no Postgres, `CREATE DATABASE ... TEMPLATE`; no SQLite, `VACUUM INTO`, e lá o Alembic precisa do modo batch para alterar coluna. Gatilho: antes das features que mexem no banco (F8, F16, F20, F21, F29, F30).
**Aceite:** um banco criado na `v1.0.0` abre na versão nova com as partidas salvas intactas e retomáveis.

<a id="f19"></a>
**F19 — Modo backtest: partida só de estratégias, sem interação.** Serve N4 e N10; segue a D8. No lobby, "Rodar backtest" escolhe período, capital inicial, aporte e as estratégias participantes; cada estratégia vira um bot (F16) e a partida roda sem `sleep` entre ticks e sem eventos de socket por tick, mandando o progresso a cada N dias para a tela animar o gráfico. Ao fim, a partida fica salva como qualquer outra e abre no relatório da F17, já comparando as estratégias.

**Mercado isolado (padrão) ou compartilhado.** O backtest existe para comparar estratégias da forma mais justa e realista possível, então por padrão cada bot opera num mercado só dele: o impacto de preço da F13 é calculado a partir das ordens daquele jogador, e não da soma da sala, e o livro de ordens e a liquidez do market maker são separados por jogador. Todos veem o mesmo histórico, e só as próprias ordens movem o preço que cada um vê. Uma opção no lobby troca para mercado compartilhado, em que um interfere no preço do outro — o comportamento normal de uma partida multiplayer, que continua compartilhada sempre.

Referência de custo: o tick leva hoje ~50–100 ms (medido na F11), então 10 anos (~2.520 pregões) levam de 2 a 4 minutos — daí a animação. Medir onde vai o tempo do tick e tirar do caminho do backtest o que só serve à tela ao vivo (broadcast, snapshot por tick) faz parte. Gatilho: F16 concluída.
**Aceite:** duas estratégias idênticas, em mercado isolado e com a F13 ligada, terminam com o mesmo patrimônio.

<a id="f27"></a>
**F27 — Fechamento de partida: pódio e critério de vitória.** Serve N5, N6 e N9. Hoje, quando a partida chega na data final (`StopIteration` em `simulation.py:114`) ou o host encerra, o `simulation_ended` vira um toast e o guard devolve todo mundo ao lobby. No lugar disso, todos os jogadores vão para a tela de fechamento, como o fim de partida de um RTS: o pódio com os três primeiros, a classificação completa e as abas da F17 sobre a partida inteira, com o botão "Voltar ao lobby". É diferente da tela de comparação: a comparação põe resultados lado a lado, o pódio declara quem venceu.

**Critério de vitória.** Como as condições de vitória do Civilization VI, o host escolhe no lobby o que decide a partida: a nota geral da F18 (padrão), rentabilidade, patrimônio final ou Sharpe. O critério é uma coluna de `simulations` (migration da F25), ordena o pódio e também o ranking durante a partida, e aparece no topo do fechamento ("Vitória por: nota geral").

A tela lê `/api/statistics/compare?simulation_ids=<id>`, que já funciona sem partida ativa, então ela também abre depois, a partir da lista de simulações salvas. O payload de `simulation_ended` passa a levar o id da simulação. Gatilho: F17 concluída e a fórmula da F18 fechada.

<a id="f29"></a>
**F29 — IR na venda de renda variável.** Serve N7. A renda fixa já desconta IR no resgate (F2); a renda variável não desconta nada, então uma estratégia que gira muito parece melhor do que é. A apuração segue o motor fiscal do [Finance Manager](https://github.com/LiloMarino/Finance-Manager) (`backend/domain/tax.py`, regras conferidas no Perguntas e Respostas do IRPF da Receita): todo mês, por jogador, o lucro das vendas sobre o preço médio da `Position`, separado por categoria — ações em operação comum, 15%, isentas quando as vendas de ações do mês somam até R$ 20.000; FIIs, 20%, sem isenção; ETFs, 15%, sem isenção; day trade, 20%. Prejuízo de um mês abate lucro dos meses seguintes da mesma categoria. O imposto sai do caixa no último dia útil do mês seguinte (o vencimento do DARF), como evento de caixa (D1), então a retomada o reconstrói. Aparece na carteira e na aba Operações da F17. O IRRF de 0,005% ("dedo-duro") fica fora: é antecipação do mesmo imposto e não muda o total.
**Aceite:** vender R$ 30.000 em ações com R$ 5.000 de lucro num mês debita R$ 750 no mês seguinte; vender R$ 15.000 com lucro no mês não debita nada.

<a id="f30"></a>
**F30 — Setores e segmentos.** Serve N16. Mesmo modelo do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): tabelas `sectors` (nome único) e `segments` (nome único dentro do setor), com `segment_id` anulável em `stock`. Na importação, o setor e a indústria que o yfinance dá ao ticker viram uma sugestão de segmento, e a classificação é editável na Central de dados (F21). Com isso: a carteira ganha a visão por setor e segmento (barras e tabela de valor e fração), a aba Composição da F17 ganha o recorte por setor, e a estratégia (F8) enxerga o setor de cada ativo — o que permite estratégias como rotação setorial.

<a id="f31"></a>
**F31 — Diagrama do banco sempre em dia.** Serve N17; segue a D9. O `docs/erd/simulador_financeiro.erd` (extensão ERD Editor do VS Code) era editado à mão e está defasado desde 2025-12-29; com a D9, a fonte do schema são os models. `pnpm db:erd` lê o `Base.metadata` e escreve a página `docs/docs/desenvolvimento/banco-de-dados.md` com um `erDiagram` em Mermaid: cada tabela com colunas, tipos, PK e FK, e as relações tiradas das chaves estrangeiras. O Docusaurus já tem o Mermaid ligado, então o diagrama renderiza no site da documentação (e no GitHub, que também renderiza Mermaid). `tests/test_erd.py` gera o diagrama em memória e compara com a página: se um model mudou e a página não, o teste falha pedindo `pnpm db:erd`. O `.erd` sai do repositório. Ideias de modelagem são esboçadas em Mermaid na conversa, antes de virar model e migration.
**Aceite:** acrescentar uma coluna num model sem rodar `pnpm db:erd` faz o teste falhar.

<a id="f32"></a>
**F32 — Ferramenta de correlação entre ativos.** Serve N18. Como a do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): escolhem-se tickers quaisquer, e o IBOV ou o CDI como referência, e uma janela (6 meses, 1, 3 ou 5 anos); o backend (D2) calcula a correlação dos retornos diários de cada par e devolve a matriz, mostrada como mapa de calor. A correlação vai de −1 a 1: perto de 1, os dois sobem e caem juntos (dois bancos, ~0,8); perto de 0, um não diz nada sobre o outro; negativa, um tende a subir quando o outro cai. Para diversificar, quanto mais baixa melhor. A tela traz essa leitura ao lado e num tooltip, com o tamanho da amostra (quantos pregões em comum entraram no cálculo). Durante a partida, a janela termina na data da simulação, para a ferramenta não revelar o futuro; fora da partida, vale qualquer período. Também serve para conferir o gerador da F23: a correlação entre ativos nos dados gerados deve ficar perto da do histórico.

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
| **F18** | Pontuação geral (overall) | Serve N9; a aba Geral da F17 | M7 | — | 🔍 Em avaliação |
| **F22** | Preço ajustado e proventos | Serve N3, N7; degrau falso na atualização incremental | M8 | — | 🔍 Em avaliação |
| **F23** | Spike: gerador de séries sintéticas | Serve N12; fecha o método e o contrato da F24 | M9 | [F20](#f20) | 🔍 Em avaliação |
| **F26** | Redesign visual | Serve N15; referência das telas das F16–F30 | — | — | 🔍 Em avaliação |
| **F28** | Muitos futuros (Monte Carlo) | Serve N10; revisa ou confirma a D7 | M9 | [F19](#f19), [F23](#f23) | 🔍 Em avaliação |

<a id="f3"></a>
**F3 — Spike: banco embarcado no executável.** Decide a D4. Falta medir as três opções finalistas com o executável real: (1) aumento de tamanho do `.exe` e tempo até o lobby abrir; (2) quantos tipos específicos do Postgres os models usam hoje (JSONB e outros) e o custo de trocá-los; (3) escrita concorrente com 4+ jogadores no mesmo tick (SQLite em modo WAL aguenta?); (4) como ficam as migrations da F25 em cada opção (o SQLite exige o modo batch do Alembic para alterar coluna). Sai daqui com a D4 decidida e o plano da F4 fechado.

<a id="f5"></a>
**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO sem cair para polling. O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

<a id="f7"></a>
**F7 — Spike: estratégia Python escrita pelo usuário.** Origem: #2, #12. Decide a D5 e define a API da classe base. Falta responder: (1) carregar um `.py` externo via `importlib` funciona dentro do executável do PyInstaller, e quais bibliotecas a estratégia enxerga (só as empacotadas — pandas sim, outras não); (2) como proteger o tick de uma estratégia em loop infinito ou lenta (timeout por tick); (3) o que a estratégia vê e pode fazer — hoje `BaseStrategy` só recebe `matching_engine`/`market_data`, ou seja, renda variável, e faltam caixa, posição e renda fixa; (4) onde o código fica guardado — numa pasta (fácil de editar no editor) ou no banco junto da simulação (retomar reusa exatamente a mesma versão do código); (5) a viabilidade da opção "bot cliente da API" no multiplayer.

<a id="f18"></a>
**F18 — Pontuação geral (overall).** Serve N9. Uma nota por jogador, decomposta por dimensão, na aba Geral da F17 e no ranking, com a fórmula nos docs em LaTeX (o Docusaurus precisa de `remark-math` + `rehype-katex`, hoje ausentes). Falta definir: (1) **os componentes** — candidatos: retorno anual acima do CDI, drawdown máximo, volatilidade, Sharpe (que já mistura retorno e volatilidade, então somá-lo à volatilidade conta o risco duas vezes) e consistência (fração dos meses em que bateu o CDI); (2) **a normalização** para uma escala comum — absoluta, com faixas fixas (drawdown de 0% vale 100 pontos, de 50% vale 0), que permite comparar partidas diferentes, ou relativa à sala (o melhor jogador vale 100), que não permite; (3) **a agregação** — soma de pontos por categoria, como o placar do Age of Empires II, ou média ponderada com pesos configuráveis. Sai daqui com a fórmula escolhida e o card em Atende necessidade.

<a id="f22"></a>
**F22 — Preço ajustado e proventos.** Serve N3 e N7. O importador usa `yf.download(auto_adjust=True)`: o preço vem ajustado por dividendos e desdobramentos *até o dia da importação*. A atualização incremental (`upsert_dataframe` só grava linhas depois da última data guardada) emenda duas séries ajustadas em dias diferentes, então um provento ou desdobramento ocorrido entre a importação e a atualização vira um degrau falso na emenda — num desdobramento 2:1, uma queda de 50% que não existiu. Além disso, o preço exibido não é o que se negociava na época, e dividendo nunca entra no caixa. Falta escolher: (1) **atualizar sempre baixando a série inteira** e sobrescrevendo — corrige o degrau com pouca mudança, mas reescreve o passado de partidas salvas a cada provento novo; (2) **preço bruto + proventos como evento** — `auto_adjust=False`; desdobramento ajusta a quantidade da posição e dividendo credita o caixa na data ex (o `yfinance` traz as duas listas); fiel e reprodutível, mas mexe no motor, na carteira e na F13. Sai daqui com a escolha e o plano de implementação.

<a id="f23"></a>
**F23 — Spike: gerador de séries sintéticas.** Serve N12. Gera um futuro plausível para depois do último dia real, gravado como dado comum (D7), sempre numa lacuna sem dado canônico e emendando no último valor real. Plausível quer dizer com a estrutura do mercado real: quedas bruscas, períodos agitados que duram, e ativos parecidos andando juntos (uma crise bancária derruba todos os bancos). Falta definir:

1. **O método** — recomendado: *bootstrap em blocos conjunto*, que sorteia trechos reais de algumas semanas do passado (o mesmo trecho para todos os ativos e indicadores ao mesmo tempo) e emenda os retornos diários desses trechos a partir do último preço real. Preserva as crises, a volatilidade e a correlação entre ativos e setores do histórico sem modelo para treinar, e com semente fixa a mesma geração sai igual (N3); o limite é não inventar um tipo de crise que nunca aconteceu. Alternativas: passeio aleatório com volatilidade constante (GBM — simples, mas sem crises nem correlação), GARCH (volatilidade que vem em ondas como no mercado real, mas um modelo por ativo e a correlação à parte) e rede neural treinada no histórico (MLP/LSTM — tende a prever a média e gerar uma curva lisa, porque o preço diário é quase imprevisível).
2. **A "temperatura"** — um controle só, como a temperatura de uma LLM: em 1 o sorteio dos trechos é uniforme (o histórico como foi); abaixo de 1 favorece trechos calmos; acima de 1 favorece trechos agitados (o peso de cada trecho cresce com a volatilidade dele). Com um preview: gerar sem gravar uma amostra de poucos ativos e mostrar o gráfico a cada mudança de parâmetro.
3. **Indicador é nível, não retorno** — a SELIC gerada a partir de variações sorteadas pode derivar para valores absurdos e precisa de limites, e o CDI anda colado na SELIC.
4. **Partida salva sobre dado gerado** quando o real chega e o substitui (D7) — congelar a geração para aquela partida, impedir a troca enquanto alguma partida usar o trecho, ou aceitar a mudança.

Sai daqui com o método e o contrato fechados para a F24.

<a id="f26"></a>
**F26 — Redesign visual.** Serve N15. Remake visual do app inteiro, iterado no Claude Design: identidade visual, design system (tokens de cor, tipografia, espaçamento, tema claro e escuro), navegação e telas. As features em aberto deste roadmap são a referência para as telas novas e as refeitas: o lobby com bots e backtest (F16, F19), as estatísticas em abas e o fechamento de partida (F17, F27), a central de dados com a linha do tempo real × gerado (F21, F24). Pela D8, estatísticas, comparação, fechamento e resultado de backtest são uma família só de tela. Falta: fechar o design no canvas — design system e telas. Com ele fechado, o card ganha o plano de implementação: os tokens no CSS do frontend, os componentes do design system estendidos com as variantes novas, e a migração tela a tela.

<a id="f28"></a>
**F28 — Muitos futuros (Monte Carlo).** Serve N10. Em vez de testar a estratégia num futuro gerado só, testá-la em muitos (ex.: 100, cada um com uma semente) e mostrar o resultado como distribuição: "perdeu para o CDI em 23 de 100 futuros; no pior, −35%; no do meio, +40% em 5 anos". Lê-se pela fração de futuros ruins e pelo pior caso: poucos futuros perdendo para o CDI é bom; uma estratégia que só ganha no histórico real e perde na maioria dos futuros plausíveis teve sorte, não mérito. É o backtest da F19 repetido sobre gerações da F23. Falta definir: **onde vivem os 100 futuros.** A D7 guarda *um* futuro gerado nas tabelas de série, e Monte Carlo precisa de muitos ao mesmo tempo. Opções: (1) as tabelas de série ganham uma dimensão de cenário (o canônico é o cenário 0, e cada futuro de Monte Carlo é um cenário descartável); (2) o motor passa a ler as séries por um provedor, que pode ser o banco ou uma geração em memória — o que estende a D7 de "mesmas tabelas" para "mesma interface". Sai daqui com essa escolha, que revisa ou confirma a D7.
