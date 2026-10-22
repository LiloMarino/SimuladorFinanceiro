<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-10-22):** Decididas as expansões Gestoras e Governo na rodada de design (modo na topbar, segundo turno, vice, Congresso, 90 dias de prazo e carteira congelada); registrados os proventos e os partidos como features novas.

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | — | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F8](#f8), [F9](#f9), [F10](#f10), [F19](#f19), [F33](#f33) | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | — | — |
| **N6** | Comparar resultados de simulações diferentes | — | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | — | — |
| **N8** | Jogar contra oponentes controlados pelo computador | [F16](#f16) | — |
| **N9** | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — |
| **N10** | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | [F19](#f19) | — |
| **N11** | Que o cenário econômico simulado seja o histórico real | — | — |
| **N12** | Continuar jogando depois do último dia com dado real | — | — |
| **N13** | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | — |
| **N14** | Atualizar para uma versão nova sem perder as partidas salvas | [F56](#f56) | — |
| **N15** | Usar uma interface agradável e coerente, à altura de um jogo | [F37](#f37), [F72](#f72) | — |
| **N16** | Ver a carteira e o mercado por setor e segmento | — | — |
| **N17** | Enxergar a estrutura do banco e esboçar mudanças nela | — | — |
| **N18** | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — |
| **N19** | Analisar um ativo com as ferramentas de um trader | [F33](#f33), [F96](#f96) | — |
| **N20** | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | — |
| **N21** | Jogar "na unha", sem a interface apontar a melhor escolha | — | — |
| **N22** | Ter objetivos para buscar além de vencer a partida | — | — |
| **N23** | Jogar com os amigos de outras formas além de cada um por si | [F69](#f69), [F71](#f71) | — |
| **N24** | Saber onde está a lentidão durante uma partida | — | — |
| **N25** | Entender o que é o simulador e como se joga, sem ler um manual | — | — |
| **N26** | Achar a causa de um erro sem vasculhar o log inteiro | — | — |
| **N27** | Entrar numa partida que já começou | — | — |
| **N28** | Liberar uma vaga sem depender de o jogador sair | [F61](#f61) | — |
| **N29** | Saber o que cada jogador está fazendo enquanto a partida não começa | — | — |
| **N30** | Repetir uma configuração de partida sem montá-la de novo | [F89](#f89) | — |
| **N31** | Saber o que está movendo o mercado da partida, como quem lê o noticiário | [F92](#f92) | — |
| **N32** | Saber como foi o mês sem montar a conta | [F91](#f91) | — |
| **N33** | Investir com dinheiro emprestado, pagando o juro do momento | [F94](#f94) | — |
| **N34** | Disputar o poder de mudar as regras da economia da partida | — | — |
| **N35** | Tirar da lista as partidas que não interessam mais | — | — |
| **D5** | Onde roda o código de estratégia escrito pelo usuário | [F8](#f8) | 🔍 |
| [**F5**](#f5) | Spike: provider de túnel pela internet | — | 🔍 |
| [**F6**](#f6) | Link de convite pela internet no lobby | — | ⏳ |
| [**F7**](#f7) | Spike: estratégia Python escrita pelo usuário | — | 🔍 |
| [**F8**](#f8) | Modo automático: estratégia do jogador roda a cada tick | — | ⏳ |
| [**F9**](#f9) | Estratégias prontas de exemplo | — | ⏳ |
| [**F10**](#f10) | Guia de como escrever uma estratégia | — | ⏳ |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F16**](#f16) | Bots na sala | — | ⏳ |
| [**F19**](#f19) | Modo backtest: partida só de estratégias, sem interação | — | ⏳ |
| [**F22**](#f22) | Preço ajustado e proventos | — | 🔍 |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | — | 🔍 |
| [**F33**](#f33) | Indicadores técnicos | — | ⏳ |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 |
| [**F37**](#f37) | Tema escuro | — | 💤 |
| [**F44**](#f44) | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | — | 🔍 |
| [**F49**](#f49) | Spike: tutorial animado | — | 🔍 |
| [**F55**](#f55) | Modo aquisição hostil | — | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | ⏳ |
| [**F68**](#f68) | Dica de firewall no lobby | — | ⏳ |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | ⏳ |
| [**F71**](#f71) | Renda fixa com liquidez diária | — | ⏳ |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F75**](#f75) | Encerramento do loop sem thread viva nem simulação presa | — | ⏳ |
| [**F81**](#f81) | CORS restrito à mesma origem | — | 💤 |
| [**F87**](#f87) | Erros de dado do yfinance na base | — | 🔍 |
| [**F89**](#f89) | Presets de partida | — | ⏳ |
| [**F90**](#f90) | Cenários | — | 🔍 |
| [**F91**](#f91) | Caixa de entrada e resumo do mês | — | 💤 |
| [**F92**](#f92) | Noticiário da partida | — | 💤 |
| [**F93**](#f93) | Rumores antecipados | — | 🔍 |
| [**F94**](#f94) | Crédito | — | 💤 |
| [**F95**](#f95) | Expansão Governo: ganhar a eleição e mexer nas regras | — | 🔍 |
| [**F96**](#f96) | Dicas de análise técnica | — | 💤 |
| [**F97**](#f97) | SELIC nas mãos do governo | — | 🔍 |
| [**F99**](#f99) | Partidos na expansão Governo | — | 🔍 |
| [**F100**](#f100) | Proventos na carteira e nas telas | — | 🔍 |

<details>
<summary><strong>Concluído / decidido / descartado (14 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | [F94](#f94) | ✅ |
| **D2** | Cálculo financeiro acontece só no backend; o frontend exibe | [F33](#f33) | ✅ |
| **D3** | Dinheiro e quantidade trafegam como Decimal serializado em string | — | ✅ |
| **D4** | Banco de dados embarcado no executável | — | ✅ |
| **D6** | A retomada continua no dia seguinte ao último evento | — | ✅ |
| **D7** | O simulador lê as séries sem saber a origem | [F92](#f92) | ✅ |
| **D8** | Bot, modo automático e backtest são o mesmo mecanismo | [F8](#f8), [F16](#f16), [F19](#f19) | ✅ |
| **D9** | De onde nasce uma mudança de schema | — | ✅ |
| **D10** | Como a nota geral é calculada | — | ✅ |
| **D11** | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | ✅ |
| **D12** | Como numerar as versões | — | ✅ |
| **D13** | Um canal de tempo real só: Socket.IO, com fallback de polling | — | ✅ |
| **D14** | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | — | ✅ |
| **D15** | Lint com oxlint e o TypeScript 7 com a API do 6 ao lado | — | ✅ |

</details>

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: as `F#` que podem ser pegas agora — toda dependência já ✅. "Destrava" é quantas `F#` em aberto esperam por ela, direta ou indiretamente; é por aí que a tabela está ordenada. 💤 (sem prioridade) e 🚫 não entram.

| ID | Resumo | Marco | Destrava | Status |
| --- | --- | --- | --- | --- |
| [**F7**](#f7) | Spike: estratégia Python escrita pelo usuário | M4 | 6 | 🔍 |
| [**F22**](#f22) | Preço ajustado e proventos | M8 | 3 | 🔍 |
| [**F5**](#f5) | Spike: provider de túnel pela internet | M3 | 2 | 🔍 |
| [**F95**](#f95) | Expansão Governo: ganhar a eleição e mexer nas regras | — | 2 | 🔍 |
| [**F33**](#f33) | Indicadores técnicos | M11 | 1 | ⏳ |
| [**F89**](#f89) | Presets de partida | — | 1 | ⏳ |
| [**F49**](#f49) | Spike: tutorial animado | M14 | 0 | 🔍 |
| [**F56**](#f56) | Novidades no app | — | 0 | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | 0 | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | 0 | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | 0 | ⏳ |
| [**F68**](#f68) | Dica de firewall no lobby | — | 0 | ⏳ |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | 0 | ⏳ |
| [**F71**](#f71) | Renda fixa com liquidez diária | — | 0 | ⏳ |
| [**F75**](#f75) | Encerramento do loop sem thread viva nem simulação presa | — | 0 | ⏳ |
| [**F87**](#f87) | Erros de dado do yfinance na base | — | 0 | 🔍 |

---

## 🧭 Marcos

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

### M8 — Dados reais, cuidados fora da partida

> **Objetivo:** Indicadores e preços fiéis ao histórico, geridos numa central antes de jogar.
>
> **Serve:** N3, N11, N13
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F22**](#f22) | Preço ajustado e proventos | — | 🔍 |
| [**F100**](#f100) | Proventos na carteira e nas telas | [F22](#f22) | 🔍 |

### M9 — Mercado sem fim

> **Objetivo:** Jogar além do último dia real sobre dados gerados que a simulação trata como reais.
>
> **Serve:** N12
>
> **Progresso:** 0/1 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | [F19](#f19) | 🔍 |

### M11 — Análise técnica

> **Objetivo:** Analisar um ativo com os indicadores e as ferramentas de desenho de uma plataforma de trader.
>
> **Serve:** N19
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F33**](#f33) | Indicadores técnicos | — | ⏳ |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | [F33](#f33) | 🔍 |
| [**F96**](#f96) | Dicas de análise técnica | — | 💤 |

### M14 — Vitrine e primeiros passos

> **Objetivo:** Ver o jogo funcionando antes de baixar e aprender a jogar vendo, não lendo.
>
> **Serve:** N25
>
> **Progresso:** 0/1 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F49**](#f49) | Spike: tutorial animado | — | 🔍 |

### M15 — Notícias e resumo do mês

> **Objetivo:** A partida conta o que acontece no mercado e como foi o mês de cada jogador.
>
> **Serve:** N31, N32
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F91**](#f91) | Caixa de entrada e resumo do mês | — | 💤 |
| [**F92**](#f92) | Noticiário da partida | [F91](#f91) | 💤 |
| [**F93**](#f93) | Rumores antecipados | [F92](#f92) | 🔍 |

### Sem marco

> **Progresso:** 0/21 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F37**](#f37) | Tema escuro | — | 💤 |
| [**F44**](#f44) | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | [F100](#f100) | 🔍 |
| [**F55**](#f55) | Modo aquisição hostil | [F44](#f44) | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | ⏳ |
| [**F68**](#f68) | Dica de firewall no lobby | — | ⏳ |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | ⏳ |
| [**F71**](#f71) | Renda fixa com liquidez diária | — | ⏳ |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F75**](#f75) | Encerramento do loop sem thread viva nem simulação presa | — | ⏳ |
| [**F81**](#f81) | CORS restrito à mesma origem | [F6](#f6) | 💤 |
| [**F87**](#f87) | Erros de dado do yfinance na base | — | 🔍 |
| [**F89**](#f89) | Presets de partida | — | ⏳ |
| [**F90**](#f90) | Cenários | [F89](#f89) | 🔍 |
| [**F94**](#f94) | Crédito | — | 💤 |
| [**F95**](#f95) | Expansão Governo: ganhar a eleição e mexer nas regras | — | 🔍 |
| [**F97**](#f97) | SELIC nas mãos do governo | [F95](#f95) | 🔍 |
| [**F99**](#f99) | Partidos na expansão Governo | [F95](#f95) | 🔍 |

---

## 1. Atende necessidade

| ID | Resumo | Atende (N#) | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F6** | Link de convite pela internet no lobby | N2 | — | M3 | [F5](#f5) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F8** | Modo automático: estratégia do jogador roda a cada tick | N4 | D5, D8 | M4 | [F7](#f7) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F9** | Estratégias prontas de exemplo | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F10** | Guia de como escrever uma estratégia | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F16** | Bots na sala | N8 | D8 | M6 | [F8](#f8) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F19** | Modo backtest: partida só de estratégias, sem interação | N4, N10 | D8 | M6 | [F16](#f16) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F33** | Indicadores técnicos | N19, N4 | D2 | M11 | — | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F37** | Tema escuro | N15 | — | — | — | Médio | Baixo | Médio | Médio | 💤 Registrado, sem prioridade |
| **F56** | Novidades no app | N14 | — | — | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F61** | Host remove jogador da sala | N28 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F69** | Imprevistos configuráveis e tipos novos | N23 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F71** | Renda fixa com liquidez diária | N23 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F72** | Gráficos padronizados sobre o ChartContainer do shadcn | N15 | — | — | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F89** | Presets de partida | N30 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F91** | Caixa de entrada e resumo do mês | N32 | — | M15 | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F92** | Noticiário da partida | N31 | D7 | M15 | [F91](#f91) | Médio | Baixo | Alto | Bom | 💤 Registrado, sem prioridade |
| **F94** | Crédito | N33 | D1 | — | — | Alto | Médio | Alto | Bom | 💤 Registrado, sem prioridade |
| **F96** | Dicas de análise técnica | N19 | — | M11 | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |

<a id="f6"></a>
**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada.

<a id="f8"></a>
**F8 — Modo automático: estratégia do jogador roda a cada tick.** Origem: #2, #12, #14. Hoje `SimulationEngine.set_strategy` guarda uma estratégia só para o engine inteiro; ela passa a ser por jogador (`client_id` → estratégia), com `ManualStrategy` (já é no-op) como padrão. Cada tick chama `next()` da estratégia de cada jogador antes do flush de eventos. A página de Estratégias (hoje um mock que retorna 501) vira real: escolher a estratégia, ativar e desativar (a alternância manual ↔ automático da #14) e ver o log das ordens que ela emitiu. Onde a estratégia roda e quem pode carregá-la segue a D5. Gatilho: F7 concluída.

<a id="f9"></a>
**F9 — Estratégias prontas de exemplo.** Estratégias simples e conhecidas, implementadas como subclasses da classe base com parâmetros editáveis na UI. Duas famílias: **referências**, para responder se uma estratégia bate o "não fazer nada" — comprar e segurar um ETF de índice (BOVA11), 100% no CDI e rebalanceamento por meta (ex.: 60% ações / 40% renda fixa, voltando à meta todo mês, como o rebalanceamento do [Finance Manager](https://github.com/LiloMarino/Finance-Manager)); e **táticas**, as três do mock atual de `strategies.tsx` — cruzamento de médias móveis de 50 e 200 dias, RSI (compra abaixo de 30, vende acima de 70) e rompimento de máxima com volume — mais momentum (compra os ativos que mais subiram nos últimos 12 meses). Servem para jogar no automático e como bots (F16) sem escrever código, como exemplo comentado para o guia da F10 e como teste da própria classe base: o rebalanceamento e o 100% CDI só cabem se a estratégia enxergar caixa, posições e renda fixa, e cada estratégia que não couber limpa aponta o que falta na API da F7/F8.

<a id="f10"></a>
**F10 — Guia de como escrever uma estratégia.** Origem: #49. Página no Docusaurus (grupo "Como Usar"): a classe base, quais métodos o usuário implementa e quais já vêm prontos, o que acontece em cada tick, uma das estratégias da F9 comentada linha a linha, e as limitações (bibliotecas disponíveis no executável, tempo máximo por tick, regra de multiplayer da D5). Gatilho: F8 concluída — a API da classe base só fica estável depois dela.

<a id="f16"></a>
**F16 — Bots na sala.** Serve N8; segue a D8. No lobby, o host clica "Adicionar bot" e escolhe a estratégia — as prontas da F9 ou as escritas pelo usuário na F8; cada estratégia é um "tipo de IA", como as IAs do OpenTTD — e um nome. O bot é um jogador sem socket: registro em `users` marcado como bot, carteira própria, e o motor chama o `next()` da estratégia dele a cada tick, como faz com a de um humano no automático. Aparece no ranking e nas estatísticas como qualquer jogador, com um ícone que o distingue. Quem escolhe o código do bot é o host, então ele roda no processo do host qualquer que seja a D5 — a restrição da D5 é sobre código vindo de jogador remoto. Com a F13 ligada, as ordens do bot movem preço como as de qualquer jogador. Gatilho: F8 concluída.

<a id="f19"></a>
**F19 — Modo backtest: partida só de estratégias, sem interação.** Serve N4 e N10; segue a D8. No lobby, "Rodar backtest" escolhe período, capital inicial, aporte e as estratégias participantes; cada estratégia vira um bot (F16) e a partida roda sem `sleep` entre ticks e sem eventos de socket por tick, mandando o progresso a cada N dias para a tela animar o gráfico. Ao fim, a partida fica salva como qualquer outra e abre no relatório da F17, já comparando as estratégias.

**Mercado isolado (padrão) ou compartilhado.** O backtest existe para comparar estratégias da forma mais justa e realista possível, então por padrão cada bot opera num mercado só dele: o impacto de preço da F13 é calculado a partir das ordens daquele jogador, e não da soma da sala, e o livro de ordens e a liquidez do market maker são separados por jogador. Todos veem o mesmo histórico, e só as próprias ordens movem o preço que cada um vê. Uma opção no lobby troca para mercado compartilhado, em que um interfere no preço do outro — o comportamento normal de uma partida multiplayer, que continua compartilhada sempre.

Referência de custo: o tick leva hoje ~50–100 ms (medido na F11), então 10 anos (~2.520 pregões) levam de 2 a 4 minutos — daí a animação. Medir onde vai o tempo do tick e tirar do caminho do backtest o que só serve à tela ao vivo (broadcast, snapshot por tick) faz parte. Gatilho: F16 concluída.
**Aceite:** duas estratégias idênticas, em mercado isolado e com a F13 ligada, terminam com o mesmo patrimônio.

<a id="f33"></a>
**F33 — Indicadores técnicos.** Serve N19 e N4; segue a D2. Hoje o gráfico de ações mostra só o preço (área ou velas); os indicadores que um site como o Investing.com mostra não existem. `backend/features/technical_analysis/indicators.py` calcula, sobre o histórico de preço e volume (`stock_price_history` já guarda o volume), funções puras em pandas com parâmetros editáveis: médias móveis simples e exponencial (MMS, MME), MACD (12, 26, 9: linha, sinal e histograma), IFR (14), Bandas de Bollinger (20 pregões, 2 desvios), estocástico (14, 3), ATR (14) e OBV. Implementação própria, sem TA-Lib, que exige uma biblioteca em C no executável; cada função tem teste contra uma série curta com valores calculados à mão. `GET /api/stocks/{ticker}/indicators` devolve as séries alinhadas às datas do preço; na partida, só até a data da simulação, como na correlação (F32). No gráfico, o que se desenha sobre o preço (médias, Bollinger) vira série no mesmo painel, e os osciladores (MACD, IFR, estocástico, volume) ganham painéis próprios embaixo, que o `lightweight-charts` 5 tem nativos. Um seletor "Indicadores" liga e desliga cada um e edita os parâmetros, e cada indicador traz a dica com o que mede e como ler (IFR acima de 70 costuma ser lido como sobrecomprado, abaixo de 30 como sobrevendido). Ao lado do gráfico, um "Resumo técnico" no formato do Investing.com: o valor de cada indicador no dia e a leitura (compra, neutro, venda). As mesmas funções entram no contexto da estratégia (F8), para que a estratégia decida pelo mesmo número que aparece na tela. Uma página "Análise Técnica" nos docs explica cada indicador.

<a id="f37"></a>
**F37 — Tema escuro.** Serve N15. Hoje só existe o tema claro (F26): o `:root` de `frontend/index.css` é a única fonte dos tokens, e o `@custom-variant dark` ficou inerte.

**Plano.**
1. Desenhar o tema escuro no canvas do Claude Design, sobre as mesmas telas da F26.
2. Reescrever os mesmos tokens num bloco `.dark`, com passos próprios das mesmas rampas, sem inverter as cores claras.
3. Validar as oito cores de gráfico contra a superfície escura com o validador de paleta da skill de dataviz.
4. Fazer o `lightweight-charts` ler as cores do token (`getComputedStyle`) em vez de fixá-las, para o gráfico de velas acompanhar.
5. Criar um card "Aparência" nas Configurações, com claro, escuro ou "seguir o sistema". A escolha fica no `localStorage`, por ser preferência deste navegador; o padrão é seguir o sistema (`prefers-color-scheme`).

**Gatilho:** quando o design escuro estiver fechado no canvas.

<a id="f56"></a>
**F56 — Novidades no app.** Serve N14. Como as notas de patch de um jogo: o `CHANGELOG.md` da F51 vai junto no executável, o backend o serve com a versão, e o lobby mostra as novidades da versão atual. Na primeira abertura depois de atualizar, o card ou o selo de novidades fica em destaque até ser aberto (o navegador guarda a última versão vista); aberto, mostra "O que há de novo na versão X" e dá acesso ao histórico inteiro. O lugar exato no lobby, que já está cheio, sai de uma iteração no Claude Design antes de implementar.

<a id="f61"></a>
**F61 — Host remove jogador da sala.** Serve N28. Hoje a vaga só abre quando o jogador sai por conta própria: com a sala cheia ou a partida salva recusada por causa de novatos (F58), o host tem de pedir pelo chat para alguém fechar a aba. O plano: um botão "Remover" no cartão de cada jogador do lobby, só para o host, que encerra a sessão do jogador pelo mesmo caminho do `player_logout`, com um aviso "o host te removeu da sala" na tela dele, e libera a cor e a vaga na hora. Fica em aberto se a remoção também vale para participante offline da partida em andamento; a leitura provável é que não, porque tirar a linha de `simulation_players` apaga o saldo e o histórico dele.

<a id="f69"></a>
**F69 — Imprevistos configuráveis e tipos novos.** Serve N23. O modo viver de renda (F53) já nasce com os tipos de imprevisto num registro, em que cada tipo é uma entrada com nome, múltiplo da despesa mensal, efeito (sai do caixa ou corta o salário do mês seguinte) e peso no sorteio; adicionar um tipo é acrescentar uma entrada, sem mexer no motor, no log nem nas telas. Esta feature expõe esse registro ao host: no lobby, o host edita o valor de cada tipo (por exemplo, o conserto passa de 1 para 2 despesas mensais), liga e desliga tipos e cria tipos próprios com nome, valor e efeito. O sorteio continua saindo da semente da partida, então todos os jogadores seguem recebendo os mesmos imprevistos nos mesmos dias, e a configuração vale para a partida salva.

<a id="f71"></a>
**F71 — Renda fixa com liquidez diária.** Serve N23. Hoje todo título de renda fixa só volta ao caixa no vencimento, então não existe onde guardar uma reserva de emergência que renda e se resgate no mesmo dia, como o CDB de liquidez diária ou o Tesouro Selic do mercado real. O plano: ofertas marcadas com liquidez diária, que o jogador resgata em qualquer pregão pelo valor corrigido até aquele dia, com o IR regressivo do prazo que passou (como já vale no vencimento); se o IOF dos primeiros 30 dias entra, fica em aberto. Fecha um desvio do modo viver de renda (F53): a reserva de emergência da página Meta conta só o caixa, porque não há o que resgatar rápido, e com esta feature passa a contar caixa + renda fixa de liquidez diária, como o design previa ("dá pra resgatar no mesmo dia, sem vender ação na baixa"). Isso dá peso de verdade ao imprevisto: quem tem a reserva aplicada cobre o conserto sem cair no cheque especial.

<a id="f72"></a>
**F72 — Gráficos padronizados sobre o `ChartContainer` do shadcn.** Serve N15; continua a padronização da interface no shadcn, que deixou o `shared/components/ui/chart.tsx` sem nenhum consumidor. Hoje cada gráfico Recharts repete o `ResponsiveContainer`, a cor da grade e um array `{ key, label, color }` de séries (que é o `ChartConfig`), e uns cinco cards de tooltip feitos à mão reimplementam o `ChartTooltipContent`. Plano: (1) antes|depois no canvas de `player-line-chart` e `networth-chart` com `ChartContainer` + `ChartTooltipContent`, para aprovar o visual do tooltip (texto menor, indicador) e decidir se o `ui/chart.tsx` ganha variante; (2) convenção de pasta por gráfico: `<nome>-chart/` com `<nome>-chart.tsx` (componente puro, recebe o dado da API por prop), `chart-data.ts` (`ChartConfig`, tipos de linha e `build*`), `chart-legend.tsx` opcional (a legenda clicável que liga e desliga série continua própria) e `index.ts` exportando só o componente; gráfico sem legenda nem transformação fica arquivo solto `<nome>-chart.tsx`; (3) migrar `player-line-chart/` (`utils.ts` + `series.ts` → `chart-data.ts`, sai o tooltip próprio), `networth-chart`, `allocation-donut` e os gráficos embutidos em `composition-tab.tsx` (`AreaChart`) e `risk-tab.tsx` (`ScatterChart`), extraídos para pastas próprias; o `stock-chart` (lightweight-charts, imperativo) fica fora do `ChartContainer`; (4) a seção Gráficos entra em `docs/docs/desenvolvimento/convencoes-frontend.md`. Gatilho: a próxima rodada de design no canvas, ou o próximo gráfico novo.

<a id="f89"></a>
**F89 — Presets de partida.** Serve N30. No lobby, o host salva a configuração atual com um nome ("Salvar como preset") e carrega um preset salvo, que preenche o formulário inteiro: período, capital inicial, aporte, regras, modo de jogo e os parâmetros do futuro gerado (temperatura, bioma inicial e choque de inflação). Os presets moram numa tabela própria (nome, data, configuração em JSON validada pelo mesmo DTO de criação da partida), por migration (D9), com rotas para listar, salvar, renomear e apagar. Alguns vêm prontos e não se apagam ("Iniciante", "Clássico", "Realista"). Preset que traz um campo que a versão atual não conhece ignora o campo, e o que falta vem do padrão, então um preset antigo continua abrindo. Gatilho: F73 concluída, porque salvar e carregar é mais um lugar que converte entre as regras da partida e o formulário, e a F73 deixa essa conversão num lugar só.

<a id="f91"></a>
**F91 — Caixa de entrada e resumo do mês.** Serve N32. Como a caixa de entrada dos jogos de gerência de time: tudo o que a partida tem a contar chega num lugar só, sem pausar. (1) **Caixa de entrada:** um envelope na barra da partida, com o número de não lidas, abre um painel lateral com as entradas por data. Cada entrada tem um tipo (resumo, e depois notícia e conquista) e é de um jogador ou da sala inteira. Fica numa tabela `inbox_entries` (simulação, jogador ou nulo para a sala, data do jogo, tipo, conteúdo em JSONB, lida), é criada pelo motor da simulação na virada do mês e chega pelo Socket.IO com um aviso curto que some sozinho. (2) **Resumo do mês, de cada jogador:** patrimônio no início e no fim, rentabilidade do mês ao lado do CDI e do Ibovespa, melhor e pior posição, proventos recebidos, IR pago, aportes e a posição no ranking com quanto ela andou. Sai dos snapshots e dos eventos do mês, calculado no backend. (3) **Retrospectiva do ano:** na virada do ano, uma entrada maior com o ano mês a mês num gráfico pequeno, o melhor mês e a maior queda. Gatilho: antes do noticiário, que entrega as notícias por esta caixa.

<a id="f92"></a>
**F92 — Noticiário da partida.** Serve N31; segue a D7. Um noticiário sintético: as manchetes nascem das séries que a partida já lê, e por isso funcionam igual no futuro gerado, que é onde o jogo passa a maior parte do tempo, e na história real. Sem LLM e sem internet. (1) **Motor genérico:** uma lista de regras, cada uma olhando as séries no tick e, quando dispara, criando uma entrada da sala na caixa de entrada (F91) a partir de um modelo de texto com algumas variações, para a mesma frase não se repetir. Regra nova é só mais um item da lista. (2) **Macro, as manchetes padrão:** Copom subiu, baixou ou manteve a SELIC, com o tamanho ("Copom sobe a SELIC em 0,5 ponto, para 14,25%"); IPCA do mês acima ou abaixo do anterior; Ibovespa no recorde ou na maior queda do ano. (3) **Empresas:** a mesma lógica para um ativo que sobe ou cai mais de um limite no dia, chega à máxima de 52 semanas ou anuncia provento. O movimento ganha uma causa sintética plausível, sorteada de um banco de causas por setor e direção ("resultado do trimestre acima do esperado", "troca no comando", "vendas de fim de ano fracas" para o varejo). A notícia sai depois do movimento: dá contexto e não dá vantagem. (4) As notícias de um ativo aparecem também na tela dele, como marcadores no gráfico de preço. (5) **Extra, para período real:** marcos históricos curados à mão (crise de 2008, Joesley Day em 2017, Covid em março de 2020), num arquivo de dados com data, manchete e ativos ligados. O futuro gerado sempre começa depois do último dia real, então um marco datado só aparece em período real, e um cenário (F90) pode trazer os seus. Gatilho: depois da caixa de entrada.

<a id="f94"></a>
**F94 — Crédito.** Serve N33; segue a D1. Uma tela "Crédito" na partida, no molde dos empréstimos do Capitalism Lab. (1) **Nota de risco** de AAA a D, recalculada todo mês a partir da alavancagem (dívida ÷ patrimônio), da volatilidade da carteira e do histórico de pagamento (parcelas atrasadas nos últimos 12 meses). A tela mostra a nota, o peso de cada parte e o que a melhoraria. (2) **Oferta:** valor e prazo (6 a 60 meses), com o juro travado na contratação em SELIC do dia mais um spread que cresce com a nota pior (por exemplo, AAA paga SELIC + 3 pontos ao ano; nota D não recebe crédito novo), e um limite de dívida total proporcional ao patrimônio, menor quanto pior a nota. Antes de assinar, a tela mostra quanto se paga de juro no prazo todo e quanto a carteira precisa render ao ano para o empréstimo valer a pena. **Regra que impede dinheiro infinito:** o juro mais barato fica sempre acima da renda fixa mais cara oferecida no dia; senão, pegar emprestado e aplicar num CDB daria lucro sem risco. (3) **Parcelas** mensais fixas (Tabela Price), debitadas do caixa na data. Quitação antecipada, total ou parcial, com abatimento proporcional dos juros, como garante o Código de Defesa do Consumidor (art. 52, § 2º). (4) **Sem caixa na data:** a parcela fica em atraso, com multa de 2% (o teto do mesmo art. 52) e juro de mora por dia; a nota cai e novos empréstimos ficam mais caros ou bloqueados. Nada é vendido à força: pagar o atraso é decisão do jogador. (5) **Eventos novos** (contratação, parcela paga, parcela em atraso, amortização, quitação), para a dívida se reconstruir numa retomada, e o patrimônio passa a ser carteira menos dívida em todo lugar: ranking, estatísticas e nota geral. Gatilho: quando houver vontade de abrir a alavancagem no jogo.

<a id="f96"></a>
**F96 — Dicas de análise técnica.** Serve N19. Aprender análise técnica jogando: o gráfico aponta e explica o que um trader enxergaria, para quem quer jogar pelo gráfico sem já saber as regras. É ajuda, então o modo Especialista (F40) a desliga, como as outras. (1) **Padrões de vela:** regras fixas sobre abertura, máxima, mínima e fechamento de cada pregão detectam uns dez padrões clássicos (martelo, estrela cadente, engolfo de alta e de baixa, doji, três soldados brancos). O candle ganha um marcador; ao passar o mouse, um card com o nome, o desenho do padrão e o que ele costuma sugerir. **E se ele acertou:** o card conta quantas vezes o padrão apareceu neste ativo no período já jogado e em quantas o preço foi para o lado sugerido nos 5 pregões seguintes ("apareceu 12 vezes; em 7 o preço subiu"), o que ensina também que padrão não é garantia. (2) **Indicadores (F33):** as faixas ganham legenda (IFR acima de 70, "sobrecomprado": subiu rápido demais e costuma devolver; abaixo de 30, "sobrevendido") e os cruzamentos do MACD e das médias móveis ganham marcador com uma frase do que significam. (3) **Desafio da vela:** quando aparece um padrão, o jogo pergunta "e agora, sobe ou desce?" e confere dias depois, com um placar de acertos que pode virar conquista (F41). Gatilho: com o gráfico de indicadores; os padrões de vela não dependem dele.

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F60** | Modo servidor dedicado (--headless) | — | — | — | Baixo | Baixo | Baixo | Bom | ⏳ Pendente |
| **F67** | Abrir a pasta de configurações | — | — | — | Baixo | Baixo | Médio | Excelente | ⏳ Pendente |
| **F68** | Dica de firewall no lobby | — | — | — | Baixo | Baixo | Médio | Ótimo | ⏳ Pendente |
| **F75** | Encerramento do loop sem thread viva nem simulação presa | — | — | — | Baixo | Médio | Médio | Bom | ⏳ Pendente |
| **F81** | CORS restrito à mesma origem | — | — | [F6](#f6) | Baixo | Médio | Baixo | Médio | 💤 Registrado, sem prioridade |

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

<a id="f60"></a>
**F60 — Modo servidor dedicado (`--headless`).** O mesmo executável, sem o navegador: para rodar numa VPS ou num PC ligado direto, sem ninguém jogando nele. `--headless` na linha de comando, ou `[server] headless = true` no `config.toml`, pula o `webbrowser.open` do `main.py`, que hoje roda sempre que o app é o executável, e imprime no terminal os endereços para entrar (o da rede local e, com a F6, o do túnel). O administrador é quem entra com o apelido de `[host] nickname`, que é como o host é definido hoje (`routes/simulation.py`). Como a recuperação de login é por apelido, num servidor exposto à internet qualquer um que digite esse apelido viraria o host; por isso, no modo servidor, o `config.toml` ganha `[host] pin`, e o login com o apelido do host só passa com ele. Serve a quem quer deixar uma sala aberta para os amigos entrarem quando quiserem, sem depender de o host estar com o computador ligado jogando.

<a id="f67"></a>
**F67 — Abrir a pasta de configurações.** O executável guarda `config.toml`, `.env` e `logs` na pasta de dados do usuário (`%LOCALAPPDATA%\SimuladorFinanceiro` no Windows), que o Windows esconde. Em vez de mudar os arquivos de lugar, a tela de configurações ganha o botão "Abrir pasta de configurações", como o "abrir pasta de mods" de vários jogos. (1) **Rota** `POST /api/settings/open-folder` em `routes/settings.py`, protegida por `verify_host` e que só aceita requisição vinda do próprio computador (`request.client.host` em `127.0.0.1` ou `::1`): o servidor também atende a rede local, e um convidado não pode abrir janelas na máquina do host. (2) **Abertura** da pasta de `app_files_dir()` com `os.startfile` no Windows, `open` no macOS e `xdg-open` no Linux, por `subprocess` sem shell. (3) **Sem interface gráfica** (servidor dedicado, Linux sem `xdg-open`) ou pedido fora do computador do host: a rota responde 409 com o caminho, e o front o mostra num campo com botão "Copiar". O caminho aparece sempre ao lado do botão, então o jogador também o encontra sem abrir nada. (4) Um segundo botão, "Abrir pasta de logs", usa a mesma rota com `target=logs`. Um aviso junto aos botões diz que `db` e `postgres` são do banco e não devem ser editados. Teste: a rota recusa quem não é o host e quem vem de outro IP, e chama o abridor do sistema (substituído por um dublê) com a pasta certa. Não serve nenhuma necessidade listada: o ganho é achar o `config.toml` sem caçar uma pasta oculta.

**Aceite:** no executável do Windows aberto por duplo clique, o botão abre o Explorer na pasta que contém o `config.toml`; um convidado da rede local que chama a rota recebe 403.

<a id="f68"></a>
**F68 — Dica de firewall no lobby.** Quando o link do lobby abre no computador do host mas não abre no dos amigos, o motivo costuma ser o firewall do Windows, e a orientação hoje só existe na página de multiplayer dos docs. Plano: no `frontend/features/lobby/components/lobby-header.tsx`, abaixo do link copiável, uma linha curta "Amigos não conseguem entrar?" que leva à seção "Amigos não conseguem entrar?" da página de multiplayer (o link do site de docs, em nova aba). Sem rota nova e sem estado: é texto estático com link. A tela do lobby é desenhada no canvas, então a linha entra primeiro lá (estado do lobby com a dica) e só depois no código.

<a id="f75"></a>
**F75 — Encerramento do loop sem thread viva nem simulação presa.** Dois caminhos deixam o estado da partida inconsistente. (1) O `stop()` de `simulation_loop.py` espera a thread por 5 s e, se ela não terminar, só loga e segue: marca STOPPED, roda `EventManager.flush()` e `SimulationManager.clear_simulation()` enquanto a thread ainda pode processar um tick, gravando eventos de uma simulação que já foi liberada. (2) Uma exceção no loop cai no `finally`, que só muda o estado para STOPPED: a simulação continua registrada no `SimulationManager` sem loop rodando, e o `stop()` seguinte recusa com "Nenhuma simulação está em execução". Plano: o encerramento passa a ter um dono só, a própria thread: o `stop()` sinaliza e espera, e o flush e a liberação rodam no `finally` do loop, o mesmo caminho do fim natural da partida, que já faz isso. Se o join estourar o tempo, o `stop()` devolve erro em vez de liberar por cima. A exceção no tick também notifica os clientes (`simulation_ended` com motivo de erro), para a tela não ficar congelada. `pause()` e `unpause()` passam a usar o mesmo `_lock` de start e stop. Teste: o tick dublê que bloqueia além do tempo e o que lança exceção, nos testes do loop. Depende dos testes do loop para reproduzir os dois casos. Gatilho: junto com os testes do loop.

<a id="f81"></a>
**F81 — CORS restrito à mesma origem.** O backend libera CORS para qualquer origem com credenciais (`allow_origins=["*"]` e `allow_credentials=True` no FastAPI, `cors_allowed_origins="*"` no Socket.IO). Não é necessário: o front é servido pelo próprio backend e, no `pnpm dev`, chega pelo proxy do Vite. Hoje o que protege o jogador de um site malicioso aberto durante a partida é o cookie `client_id` com `SameSite=Lax`, que o navegador não manda em requisição de outro site; o CORS liberado só deixa outro site ler as rotas que não pedem identidade. (1) Sai o `CORSMiddleware` de `main.py`. (2) O Socket.IO fica com `cors_allowed_origins` na mesma origem, mais `http://localhost:5173` quando o modo debug estiver ligado: o proxy do Vite troca o `Host` (`changeOrigin: true`) mas mantém o `Origin` do Vite, e o Socket.IO recusaria a conexão em dev sem essa exceção. (3) Teste manual antes de fechar: jogo pelo `localhost`, por outro computador da LAN pelo IP e pelo `pnpm dev`. Gatilho: junto com o link de convite pela internet, quando o servidor passa a ficar exposto fora da LAN.

---
## 3. Descartada

> Nenhum item nesta categoria atualmente.

---
## 4. Incerta / exploratória

| ID | Resumo | Conexão | Marco | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| **F5** | Spike: provider de túnel pela internet | Serve N2; escolhe o provider da F6 | M3 | — | 🔍 Em avaliação |
| **F7** | Spike: estratégia Python escrita pelo usuário | Serve N4; decide D5 | M4 | — | 🔍 Em avaliação |
| **F22** | Preço ajustado e proventos | Serve N3, N7; degrau falso na atualização incremental | M8 | — | 🔍 Em avaliação |
| **F28** | Muitos futuros (Monte Carlo) | Serve N10; revisa ou confirma a D7 | M9 | [F19](#f19) | 🔍 Em avaliação |
| **F34** | Gráfico de ações em tela cheia, com ferramentas de trader | Serve N19; escolhe a biblioteca de gráfico | M11 | [F33](#f33) | 🔍 Em avaliação |
| **F44** | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | Serve N23; falta o protótipo do preço da cota; rendimentos mensais esperam os proventos (F100) | — | [F100](#f100) | 🔍 Em avaliação |
| **F49** | Spike: tutorial animado | Serve N25; compara vídeo, framer-motion e Remotion | M14 | — | 🔍 Em avaliação |
| **F55** | Modo aquisição hostil | Serve N23; faltam parte mínima no mercado e o destino do incorporado | — | [F44](#f44) | 🔍 Em avaliação |
| **F87** | Erros de dado do yfinance na base | Serve N3; encosta na F22 | — | — | 🔍 Em avaliação |
| **F90** | Cenários | Serve N22; um preset com objetivo | — | [F89](#f89) | 🔍 Em avaliação |
| **F93** | Rumores antecipados | N31; opção da partida | M15 | [F92](#f92) | 🔍 Em avaliação |
| **F95** | Expansão Governo: ganhar a eleição e mexer nas regras | N34, N23; mesmo molde da F44; os partidos são a F99 | — | — | 🔍 Em avaliação |
| **F97** | SELIC nas mãos do governo | N34; opção da expansão Governo | — | [F95](#f95) | 🔍 Em avaliação |
| **F99** | Partidos na expansão Governo | Serve N34, N23; partido com filiados sobre a eleição da F95 | — | [F95](#f95) | 🔍 Em avaliação |
| **F100** | Proventos na carteira e nas telas | Fecha o que a F22 deixa em aberto (dividendo nunca entra no caixa); destrava os rendimentos da gestora (F44) | M8 | [F22](#f22) | 🔍 Em avaliação |

<a id="f5"></a>
**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO; se não passar, se ao menos o polling atravessa (o SSE saiu na D13, então o polling é o único fallback). O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

<a id="f7"></a>
**F7 — Spike: estratégia Python escrita pelo usuário.** Origem: #2, #12. Decide a D5 e define a API da classe base. Falta responder: (1) carregar um `.py` externo via `importlib` funciona dentro do executável do PyInstaller, e quais bibliotecas a estratégia enxerga (só as empacotadas — pandas sim, outras não); (2) como proteger o tick de uma estratégia em loop infinito ou lenta (timeout por tick); (3) o que a estratégia vê e pode fazer — hoje `BaseStrategy` só recebe `matching_engine`/`market_data`, ou seja, renda variável, e faltam caixa, posição, renda fixa e o setor e segmento de cada ativo (já no banco pela F30, em `repository.stock.get_classification`); (4) onde o código fica guardado — numa pasta (fácil de editar no editor) ou no banco junto da simulação (retomar reusa exatamente a mesma versão do código); (5) a viabilidade da opção "bot cliente da API" no multiplayer.

<a id="f22"></a>
**F22 — Preço ajustado e proventos.** Serve N3 e N7. O importador usa `yf.download(auto_adjust=True)`: o preço vem ajustado por dividendos e desdobramentos *até o dia da importação*. A atualização incremental (`upsert_dataframe` só grava linhas depois da última data guardada) emenda duas séries ajustadas em dias diferentes, então um provento ou desdobramento ocorrido entre a importação e a atualização vira um degrau falso na emenda — num desdobramento 2:1, uma queda de 50% que não existiu. Além disso, o preço exibido não é o que se negociava na época, e dividendo nunca entra no caixa. Falta escolher: (1) **atualizar sempre baixando a série inteira** e sobrescrevendo — corrige o degrau com pouca mudança, mas reescreve o passado de partidas salvas a cada provento novo; (2) **preço bruto + proventos como evento** — `auto_adjust=False`; desdobramento ajusta a quantidade da posição e dividendo credita o caixa na data ex (o `yfinance` traz as duas listas); fiel e reprodutível, mas mexe no motor, na carteira e na F13. Sai daqui com a escolha e o plano de implementação.

<a id="f28"></a>
**F28 — Muitos futuros (Monte Carlo).** Serve N10. Em vez de testar a estratégia num futuro gerado só, testá-la em muitos (ex.: 100, cada um com uma semente) e mostrar o resultado como distribuição: "perdeu para o CDI em 23 de 100 futuros; no pior, −35%; no do meio, +40% em 5 anos". Lê-se pela fração de futuros ruins e pelo pior caso: poucos futuros perdendo para o CDI é bom; uma estratégia que só ganha no histórico real e perde na maioria dos futuros plausíveis teve sorte, não mérito. É o backtest da F19 repetido sobre gerações do gerador da D14. Falta definir: **onde vivem os 100 futuros.** A D7 dá às tabelas de série uma dimensão de versão, que a F24 implementa para congelar partidas salvas. Opções: (1) cada futuro de Monte Carlo é uma versão descartável nessa dimensão, gravando 100 vezes as linhas geradas (cerca de 5 milhões para 37 ativos × 5 anos); (2) o motor lê as séries por um provedor que pode ser o banco ou uma geração em memória (o `SeriesGenerator` gera 37 ativos × 5 anos em cerca de 1 s), o que estende a D7 de "mesmas tabelas" para "mesma interface". Sai daqui com essa escolha, que revisa ou confirma a D7.

<a id="f34"></a>
**F34 — Gráfico de ações em tela cheia, com ferramentas de trader.** Serve N19; segue a D2. Um botão no card "Histórico de Preços" abre o gráfico em tela cheia, com os indicadores da F33 e o que uma plataforma de trader oferece: barra de ferramentas de desenho (linha de tendência, linha horizontal de suporte e resistência, canal, retângulo, retração de Fibonacci, texto), régua que mede variação % e pregões entre dois pontos, escala logarítmica, legenda com abertura, máxima, mínima, fechamento e volume do candle sob o cursor, comparação com outro ticker ou com o Ibovespa em %, e uma boleta compacta para comprar e vender sem sair da tela. Os desenhos ficam salvos por jogador e ticker numa tabela nova (`chart_drawings`, com os pontos em JSON), entrando por migration (D9). Falta escolher a biblioteca: (1) continuar no `lightweight-charts` e escrever as ferramentas de desenho como plugins (a API de primitives da versão 5; os exemplos oficiais trazem linha de tendência e retângulo); (2) trocar pelo KLineChart (Apache 2.0), que já vem com cerca de 15 ferramentas de desenho, mas calcula indicadores no navegador, e pela D2 eles viriam do backend como indicador customizado; (3) o Advanced Charts da TradingView tem tudo pronto, mas a licença pede cadastro e não permite publicar a biblioteca em repositório público, o que o deixa fora deste projeto. Sai daqui com um protótipo de linha de tendência e Fibonacci nas opções 1 e 2, e a escolha.

<a id="f44"></a>
**F44 — Expansão "Gestoras": abrir capital, cobrar taxa e disputar o controle.** Serve N23. Inspiração: o Capitalism Lab (oferta pública, emissão de novas ações, recompra, compra de ações dos concorrentes), o OpenTTD e o Software Inc. Lá cada jogador é uma empresa que fabrica ou transporta; aqui tudo é finanças, então a empresa de cada jogador é uma gestora, e o que ela vende é o próprio desempenho. **Como expansão:** ligável por partida no lobby, com nome, emblema e card próprios, como as DLCs dos jogos da Paradox; é enfeite visual, o sistema é o mesmo ligado ou não. **A gestora** tem nome e ticker de 4 letras mais 11, como cota de FII na B3 (o servidor recusa letras que já existam entre os ativos importados), e no livro de ofertas a linha leva a cor e a sigla do jogador, para não se confundir com ativo real. O jogador a funda levando parte da carteira em troca de cotas. **É um fundo fechado listado, como um FII, o que junta as duas ideias:** (1) **oferta pública** quando o gestor quiser — cotas novas ao preço do patrimônio por cota (patrimônio de R$ 100 mil em 1.000 cotas dá R$ 100), e o dinheiro de quem compra entra na gestora: é investir no amigo; (2) **mercado** — depois da oferta, as cotas são negociadas no livro de ofertas que a renda variável já tem, e o preço sai da oferta e da procura, acima do patrimônio por cota (ágio) quando a sala acredita no gestor e abaixo (deságio) quando não; (3) **emissão de novas cotas**, com preferência para quem já é cotista, e **recompra**, que vale quando a cota está com deságio (pagar R$ 80 por R$ 100 de patrimônio valoriza a cota de quem fica); (4) **taxas** — todo mês a gestora paga aos gestores taxa de administração sobre o patrimônio e taxa de performance sobre o que passar do CDI, como um fundo real; (5) **controle** — quem juntar mais da metade das cotas troca o gestor pela assembleia de cotistas e passa a operar a carteira e a receber as taxas. **Por que abrir capital, e quando:** as taxas são sobre o dinheiro dos outros, e com ágio as cotas do próprio gestor valem mais no ranking; o custo é ficar exposto, porque vender mais da metade abre a porta para perder o controle. Abrir cedo, sem histórico, tende a sair com pouca procura; abrir depois de um bom ano tende a sair com ágio. **Co-op:** a gestora pode ter mais de um gestor, por convite; eles operam a mesma carteira e dividem as taxas, como sócios da mesma empresa. **Regras para o cálculo fechar:** só pessoas compram cotas, nunca gestoras, o que impede a participação cruzada (A com cotas da B, que tem cotas da A); no ranking, cada jogador soma a carteira pessoal, as cotas que tem pelo preço de mercado e as taxas recebidas, e a carteira da gestora só conta através das cotas, sem contar o mesmo dinheiro duas vezes. **Estrutura:** hoje eventos e snapshots pertencem ao jogador (`user_id`); a gestora precisa de carteira própria, então entra uma tabela `portfolios` e eventos e snapshots passam a apontar para a carteira, com a carteira pessoal de cada jogador migrada uma a uma (D9); a cota é um ativo no livro de ofertas, com o patrimônio por cota publicado a cada dia. **Decidido em 22/out (rodada de design):** (a) a expansão liga numa **aba própria "Expansões"** no lobby, com banner, emblema e "o que muda", como a loja de DLC; (b) o gestor opera a gestora por um **modo na topbar** ("Operando: Aurora Gestão"), que troca a conta de todas as telas de mercado, com uma faixa verde-petróleo e o caixa da gestora dizendo qual conta está ativa; (c) ao fundar, o jogador leva **caixa e também ações e títulos** em troca de cotas; (d) as taxas têm teto na partida, **2% ao ano de administração e 20% de performance** sobre o que passar do CDI, e cada gestor escolhe até o teto; (e) **o lucro fica dentro da gestora** e valoriza a cota: distribuir rendimentos todo mês, como um FII, espera a feature de proventos (F100), que vem antes, porque hoje nem os FIIs importados pagam proventos. Falta: um protótipo do preço da cota no livro com bots (F16) comprando e vendendo.

<a id="f49"></a>
**F49 — Spike: tutorial animado.** Serve N25. O tutorial é um diálogo quase em tela cheia, em passos (avançar, voltar, pular), que aparece na primeira vez no lobby e fica num botão "Como jogar"; cada passo mostra uma animação do próprio app (entrar na sala, comprar uma ação, aplicar em renda fixa, avançar o tempo, ler as estatísticas) com um texto curto. O spike faz o mesmo passo — comprar uma ação — dos três jeitos e compara: (1) **vídeo gravado pelo Playwright**, o mesmo da F47; mais barato e sempre fiel ao app, mas não acompanha o tema escuro nem fica nítido em qualquer tamanho; (2) **animação em código com o `framer-motion`**, que o projeto já tem — os componentes reais com dados de exemplo e um cursor roteirizado; nítido e segue o tema, mas cada passo é código; (3) **Remotion**, que escreve vídeo em React e tem skills oficiais para agentes de código (`npx remotion skills add`); junta a precisão do código com a saída em vídeo, ao custo de uma ferramenta a mais (a licença é gratuita para uso individual). Critérios: fidelidade ao que o usuário imaginou, nitidez, custo de manter quando a tela muda, e tamanho no executável. Entrada necessária: o roteiro desse passo (o que aparece, o que se mexe, quanto dura, o texto). Sai daqui com o jeito escolhido e o plano dos passos restantes.

<a id="f55"></a>
**F55 — Modo aquisição hostil.** Serve N23. Um modo de jogo da expansão "Gestoras" (F44) em que perder o controle tira o jogador da partida. Todo o patrimônio de cada jogador está na própria gestora, e quem juntar mais da metade das cotas de outra a incorpora: o dono anterior sai da partida e a gestora dele passa a ser controlada pelo comprador. Vence quem sobrar, ou quem tiver o maior patrimônio na data final. **Carência:** nos primeiros meses (padrão 12) ninguém pode passar de metade de outra gestora, para que abrir capital cedo não seja suicídio. **Ninguém fica invulnerável:** sem oferta pública, a gestora seria impossível de comprar, então no fim da carência todas precisam ter uma parte mínima das cotas no mercado (padrão 50%); quem não abriu capital entra numa oferta automática pelo patrimônio por cota. **Defesa:** recompra de cotas com o caixa da gestora e compra com as taxas recebidas, como uma empresa que recompra ações para não ser comprada. Falta decidir: a parte mínima no mercado; se o incorporado sai da partida ou vira co-gestor do comprador (como numa fusão); e se há um preço mínimo por cota durante a tentativa de aquisição, como nas ofertas públicas de aquisição reais.

<a id="f87"></a>
**F87 — Erros de dado do yfinance na base.** Serve N3. A base tem dias em que o preço vai a quase zero e volta: CMIG4 sobe 878% e cai 90% em agosto de 2003, XPML11 cai 99% em 14/01/2026 e volta 758 vezes cinco dias depois, e UGPA3, GOAU4, LREN3 e SUZB3 têm dias de −100%. A partida mostra esses dias como reais. O gerador (D14) já os trata como dia sem pregão. Falta escolher o que a importação faz com eles: (1) descartar a linha, deixando o dia sem pregão; (2) interpolar o fechamento entre os vizinhos; (3) só sinalizar na Central para o usuário decidir. Parte dos saltos que não voltam (B3SA3 −66% em 2011) pode ser ajuste de desdobramento, que é assunto da F22. Sai daqui com a regra e o limiar.

<a id="f90"></a>
**F90 — Cenários.** Serve N22. Como nos jogos de estratégia: uma partida montada com intenção, um preset (F89) com objetivo e texto de abertura. Exemplos: "Crise de 2008" (começa em setembro de 2008 com R$ 100 mil, meta de não perder mais de 20%), "Década perdida" (futuro gerado com choque de inflação de +15 pontos) e "Plano Real". O objetivo usa os modos de jogo que já existem (corrida à meta, viver de renda) e o ranking. Falta definir: quais cenários entram primeiro e o objetivo de cada um; se o objetivo pode ser algo que os modos não cobrem (perda máxima, bater o CDI); se há campanha, com um cenário liberando o seguinte; e se o usuário cria os próprios cenários ou só joga os que vêm com o app.

<a id="f93"></a>
**F93 — Rumores antecipados.** Ligado à N31; uma opção da partida, desligada por padrão. O simulador já sabe o futuro: as séries até a data final estão no banco antes de a partida começar, sejam reais ou geradas. O rumor usa isso e chega antes do fato, ao contrário do noticiário (F92): dias antes de um movimento grande (queda forte de um setor, mudança da SELIC), aparece na caixa de entrada algo como "analistas veem risco no varejo". O valor do rumor é obrigar o jogador a pensar: pode acontecer ou não, e a frase pede interpretação. Por isso só uma parte dos rumores se confirma, outra parte é alarme falso sorteado onde nada vai acontecer, e alguns não dizem a direção ("mudanças na diretoria da X"). Falta definir: a taxa de acerto e a antecedência; quão vago o rumor é (setor ou ativo, com ou sem direção); se é da sala inteira ou informação de um jogador só (comprada, como um informante); e se vale no modo Especialista.

<a id="f95"></a>
**F95 — Expansão "Governo": ganhar a eleição e mexer nas regras.** Ligado à N34 e à N23. Mesmo molde da expansão "Gestoras" (F44): ligável por partida no lobby, com nome, emblema e card próprios. Inspiração: a expansão de cidades do Capitalism Lab, em que o empresário funda um partido e disputa a prefeitura (os partidos entram na F99). (1) **Eleição:** a candidatura abre um ano antes da eleição. Concorrem os jogadores que se inscrevem, cada um em **chapa com um vice** (opcional: o candidato convida outro jogador, que aceita ou recusa), e candidatos do computador, que **só completam as vagas** quando há menos de 3 candidatos. A eleição tem **segundo turno**: se ninguém passar de 50%, os dois mais votados disputam de novo. Cada um define uma verba mensal de campanha, que sai do caixa e não volta, e assim compete com investir; a verba vira apoio aos poucos e com retorno decrescente (dobrar a verba não dobra o voto), e por isso começar cedo pesa. Cada candidato marca a promessa numa régua de "impostos baixos" a "gasto alto". Uma pesquisa de intenção de voto mostra a corrida num gráfico ao longo dos meses, com a cor e a sigla de cada jogador. Mandato de 4 anos, com uma reeleição. (2) **Impostos por setor:** o governo mexe nos impostos que o jogo já cobra (os 15% e 20% da renda variável, a isenção de vendas de ações até R$ 20 mil, a tabela regressiva da renda fixa, a isenção de LCI e LCA) e pode taxar ou isentar um setor ou segmento, que todo ativo já tem: "isentar o IR de energia", "taxar bancos em mais 5 pontos". Imposto vale em qualquer período, porque não mexe em preço. (3) **Gasto público e inflação, como o impacto de preço:** a medida vira um efeito por cima das séries, do mesmo jeito que o impacto de preço de ordens grandes: o preço do dia é o da série vezes (1 + a soma dos efeitos ativos), cada efeito nasce de um evento, vale cheio no começo e decai com o tempo, e tudo se reconstrói a partir dos eventos numa retomada. Aqui o efeito soma pontos ao IPCA, e o resto segue os coeficientes que a D14 já mediu: a SELIC reage com 1,5 vez a inflação (quando é autônoma) e a bolsa cai 2,9% no trimestre por ponto de alta da SELIC, ativo a ativo pelo beta. A série guardada não muda, e por isso vale também na história real. (4) **SELIC:** configurável na expansão. Por padrão o Banco Central é autônomo, como é no Brasil desde 2021, e a SELIC continua reagindo à inflação como no gerador; a outra opção a põe nas mãos do governo (F97). (5) **Popularidade:** uma métrica de aprovação do governo atual, sempre à vista, com o histórico num gráfico. Cai com inflação alta, que deixa as pessoas nervosas, com imposto novo e com promessa descumprida (o que foi feito contra a régua da campanha); sobe com inflação controlada e bolsa subindo. **Freio decidido: aprovação e reeleição.** Aprovação baixa perde a reeleição e, abaixo de um piso por meses seguidos, leva a impeachment. **Decidido em 22/out (rodada de design):** (a) a aba "Expansões" do lobby liga a expansão, como na F44; (b) verba e promessa de cada candidato são **públicas**, e o gasto de campanha **sai do patrimônio** no ranking; (c) o presidente **vence pelo patrimônio**, como todos; (d) outros freios: o **Congresso vota cada medida**, com chance de passar igual à aprovação do governo (40% de aprovação, 40% de chance), e a medida aprovada só vale **90 dias depois**, como a noventena, para os outros terem tempo de reagir; o **truste é a carteira congelada**: o presidente não compra nem vende enquanto governa, porque sabe da medida antes de todos; (e) no **impeachment** assume o **vice**; sem vice, um governo neutro do computador, sem medidas novas, até a próxima eleição. Falta definir: os pesos da aprovação.

<a id="f97"></a>
**F97 — SELIC nas mãos do governo.** Ligado à N34; uma opção da expansão "Governo" (F95), no lugar do Banco Central autônomo. (1) **Ritmo do Copom:** o governo decide a SELIC em reuniões a cada 45 dias, como o Copom, que se reúne 8 vezes por ano desde 2006; entre reuniões ela não muda. (2) **Teto por reunião, pelo que aconteceu de verdade.** Das 150 mudanças da meta da SELIC entre 2000 e outubro de 2026 (série do Banco Central): 34 foram de 0,25 ponto, 67 de 0,5, 19 de 0,75, 19 de 1, 7 de 1,5, uma de 2, uma de 2,5 (cortes de 2003) e duas de 3 (as altas da crise de 2002); desde 2006, nunca passou de 1,5. O teto acompanha isso: até 0,75 ponto por reunião em tempo normal (80% das mudanças reais), 1,5 com a inflação bem acima da meta, como em 2021 e 2022, e 3 só com a inflação explodindo, como em 2002. (3) **O preço de cada lado:** a SELIC abaixo do que o Banco Central autônomo faria (a da série, ou a do gerador) faz a inflação subir com alguns meses de atraso, pelo mesmo mecanismo de efeito por cima das séries da F95, e inflação alta derruba a aprovação; a SELIC alta demais derruba a bolsa pelo coeficiente da D14, o que também pesa na aprovação. Falta definir: quanto a inflação reage à SELIC e com quanto atraso (medir no histórico, como a D14 mediu a reação da SELIC à inflação), e os limites de inflação que liberam cada degrau do teto.

<a id="f99"></a>
**F99 — Partidos na expansão Governo.** Ligado à N34 e à N23; depende da expansão Governo (F95). Em vez de concorrer sozinho, o jogador funda ou se filia a um **partido** com nome, sigla e cor (como o emblema da gestora, para não se confundir com jogador). (1) **Filiados:** jogadores da sala se filiam ao partido e ele concorre com um candidato escolhido entre os filiados; o partido vence ou perde junto, então os filiados dividem o resultado. (2) **Verba de campanha** do partido vem das contribuições mensais dos filiados, em vez de só do caixa do candidato; a promessa da régua é a do partido. (3) **Governo:** o partido que ganha a eleição forma o governo, o presidente e o vice saem dos filiados, e a popularidade pesa no partido inteiro. (4) **Fidelidade:** filiado que sai deixa de contribuir; o que acontece com o candidato que troca de partido, e se há expulsão, fica em aberto. Falta decidir: como os filiados dividem o ganho do governo (impostos mais baixos valem para todos, mas medida setorial favorece quem tem aquele setor); se o patrimônio do presidente ou do partido conta para a vitória; e se é possível filiar-se a mais de um partido.

<a id="f100"></a>
**F100 — Proventos na carteira e nas telas.** Ligado à F22 e à F44. Hoje o conceito de provento não existe no jogo: o preço vem ajustado por dividendos, o dinheiro nunca entra no caixa e nem os FIIs importados pagam rendimento mensal. Esta feature cria o provento como evento da partida: (1) **a fonte** é a que a F22 escolher; o `yfinance` traz a lista de dividendos de cada ativo, e é daí que saem os proventos reais; onde a API não trouxer (ativo gerado, ou sem histórico), eles são **gerados sinteticamente** com um rendimento coerente com o ativo (por exemplo, o dividend yield médio do setor), sorteado pela semente da partida, para todos receberem os mesmos nos mesmos dias; (2) **o crédito** entra no caixa na data ex (ou na de pagamento, a decidir) e vira evento reconstruível, como as ordens; (3) **as telas**: a carteira ganha o total de proventos recebidos e o rendimento (yield) de cada posição, o detalhe do ativo ganha o histórico de proventos, e as estatísticas e o fechamento da partida contam o que entrou; (4) **IR**: a tributação de provento (isenção de dividendo e de FII para pessoa física) segue a regra do mercado brasileiro. Destrava os rendimentos mensais da gestora (F44), que só distribui como um FII depois desta. Falta decidir: data ex ou de pagamento; se o provento reinveste sozinho; e como o yield sintético é calibrado.
