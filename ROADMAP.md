<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-10-21):** Registrados a caixa de entrada com resumo do mês, o noticiário sintético, os rumores, o crédito, as dicas de análise técnica e a expansão Governo com a SELIC controlável (F91–F97).

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | [F76](#f76) | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F8](#f8), [F9](#f9), [F10](#f10), [F19](#f19), [F33](#f33) | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | — | — |
| **N6** | Comparar resultados de simulações diferentes | — | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | — | — |
| **N8** | Jogar contra oponentes controlados pelo computador | [F16](#f16) | — |
| **N9** | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — |
| **N10** | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | [F19](#f19) | — |
| **N11** | Que o cenário econômico simulado seja o histórico real | — | — |
| **N12** | Continuar jogando depois do último dia com dado real | [F24](#f24) | — |
| **N13** | Saber que dados a base tem e mantê-los atualizados, fora da partida | [F85](#f85), [F86](#f86) | — |
| **N14** | Atualizar para uma versão nova sem perder as partidas salvas | [F56](#f56) | — |
| **N15** | Usar uma interface agradável e coerente, à altura de um jogo | [F37](#f37), [F72](#f72) | — |
| **N16** | Ver a carteira e o mercado por setor e segmento | — | — |
| **N17** | Enxergar a estrutura do banco e esboçar mudanças nela | — | — |
| **N18** | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — |
| **N19** | Analisar um ativo com as ferramentas de um trader | [F33](#f33), [F96](#f96) | — |
| **N20** | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | — |
| **N21** | Jogar "na unha", sem a interface apontar a melhor escolha | [F40](#f40) | — |
| **N22** | Ter objetivos para buscar além de vencer a partida | [F41](#f41) | — |
| **N23** | Jogar com os amigos de outras formas além de cada um por si | [F69](#f69), [F71](#f71) | — |
| **N24** | Saber onde está a lentidão durante uma partida | — | — |
| **N25** | Entender o que é o simulador e como se joga, sem ler um manual | [F47](#f47), [F48](#f48) | — |
| **N26** | Achar a causa de um erro sem vasculhar o log inteiro | — | — |
| **N27** | Entrar numa partida que já começou | — | — |
| **N28** | Liberar uma vaga sem depender de o jogador sair | [F61](#f61) | — |
| **N29** | Saber o que cada jogador está fazendo enquanto a partida não começa | [F70](#f70) | — |
| **N30** | Repetir uma configuração de partida sem montá-la de novo | [F89](#f89) | — |
| **N31** | Saber o que está movendo o mercado da partida, como quem lê o noticiário | [F92](#f92) | — |
| **N32** | Saber como foi o mês sem montar a conta | [F91](#f91) | — |
| **N33** | Investir com dinheiro emprestado, pagando o juro do momento | [F94](#f94) | — |
| **N34** | Disputar o poder de mudar as regras da economia da partida | — | — |
| **N35** | Tirar da lista as partidas que não interessam mais | [F98](#f98) | — |
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
| [**F40**](#f40) | Modo Especialista | — | ⏳ |
| [**F41**](#f41) | Conquistas | — | ⏳ |
| [**F44**](#f44) | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | — | 🔍 |
| [**F48**](#f48) | README e docs que mostram o produto | — | ⏳ |
| [**F49**](#f49) | Spike: tutorial animado | — | 🔍 |
| [**F55**](#f55) | Modo aquisição hostil | — | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | ⏳ |
| [**F68**](#f68) | Dica de firewall no lobby | — | ⏳ |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | ⏳ |
| [**F70**](#f70) | O que cada jogador está fazendo na sala | — | ⏳ |
| [**F71**](#f71) | Renda fixa com liquidez diária | — | ⏳ |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F73**](#f73) | Mapeamento único entre as regras da partida e o formulário do lobby | — | ⏳ |
| [**F74**](#f74) | Testes da conexão em tempo real e do loop da partida | — | ⏳ |
| [**F75**](#f75) | Encerramento do loop sem thread viva nem simulação presa | — | ⏳ |
| [**F76**](#f76) | Testes das contas feitas no frontend | — | ⏳ |
| [**F77**](#f77) | Dependências em dia, com o TypeScript 7 | — | ⏳ |
| [**F80**](#f80) | Cotações do dia numa consulta só | — | ⏳ |
| [**F81**](#f81) | CORS restrito à mesma origem | — | 💤 |
| [**F84**](#f84) | Dependências do backend num sentido só | — | ⏳ |
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

<details>
<summary><strong>Concluído / decidido / descartado (22 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | [F41](#f41), [F94](#f94) | ✅ |
| **D2** | Cálculo financeiro acontece só no backend; o frontend exibe | [F33](#f33), [F40](#f40) | ✅ |
| **D3** | Dinheiro e quantidade trafegam como Decimal serializado em string | — | ✅ |
| **D4** | Banco de dados embarcado no executável | — | ✅ |
| **D6** | A retomada continua no dia seguinte ao último evento | — | ✅ |
| **D7** | O simulador lê as séries sem saber a origem | [F24](#f24), [F92](#f92) | ✅ |
| **D8** | Bot, modo automático e backtest são o mesmo mecanismo | [F8](#f8), [F16](#f16), [F19](#f19) | ✅ |
| **D9** | De onde nasce uma mudança de schema | — | ✅ |
| **D10** | Como a nota geral é calculada | — | ✅ |
| **D11** | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | ✅ |
| **D12** | Como numerar as versões | — | ✅ |
| **D13** | Um canal de tempo real só: Socket.IO, com fallback de polling | — | ✅ |
| **D14** | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | [F24](#f24) | ✅ |
| [**F24**](#f24) | Gerar dados futuros na Central de dados | — | ✅ |
| [**F47**](#f47) | Gravação automática de demonstrações | — | ✅ |
| [**F78**](#f78) | Release só sai com o check passando | — | ✅ |
| [**F79**](#f79) | Tipos do frontend que vêm da API | — | ✅ |
| [**F82**](#f82) | Repetições pequenas do frontend | — | ✅ |
| [**F83**](#f83) | Proxy do Vite na porta do config.toml | — | ✅ |
| [**F85**](#f85) | Importar duas ações da mesma empresa | — | ✅ |
| [**F86**](#f86) | Sugestão de ticker que a importação aceita | — | ✅ |
| [**F98**](#f98) | Excluir partida salva | — | ✅ |

</details>

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: as `F#` que podem ser pegas agora — toda dependência já ✅. "Destrava" é quantas `F#` em aberto esperam por ela, direta ou indiretamente; é por aí que a tabela está ordenada. 💤 (sem prioridade) e 🚫 não entram.

| ID | Resumo | Marco | Destrava | Status |
| --- | --- | --- | --- | --- |
| [**F7**](#f7) | Spike: estratégia Python escrita pelo usuário | M4 | 6 | 🔍 |
| [**F5**](#f5) | Spike: provider de túnel pela internet | M3 | 2 | 🔍 |
| [**F73**](#f73) | Mapeamento único entre as regras da partida e o formulário do lobby | — | 2 | ⏳ |
| [**F33**](#f33) | Indicadores técnicos | M11 | 1 | ⏳ |
| [**F44**](#f44) | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | — | 1 | 🔍 |
| [**F74**](#f74) | Testes da conexão em tempo real e do loop da partida | — | 1 | ⏳ |
| [**F95**](#f95) | Expansão Governo: ganhar a eleição e mexer nas regras | — | 1 | 🔍 |
| [**F22**](#f22) | Preço ajustado e proventos | M8 | 0 | 🔍 |
| [**F40**](#f40) | Modo Especialista | M13 | 0 | ⏳ |
| [**F41**](#f41) | Conquistas | M13 | 0 | ⏳ |
| [**F48**](#f48) | README e docs que mostram o produto | M14 | 0 | ⏳ |
| [**F49**](#f49) | Spike: tutorial animado | M14 | 0 | 🔍 |
| [**F56**](#f56) | Novidades no app | — | 0 | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | 0 | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | 0 | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | 0 | ⏳ |
| [**F68**](#f68) | Dica de firewall no lobby | — | 0 | ⏳ |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | 0 | ⏳ |
| [**F70**](#f70) | O que cada jogador está fazendo na sala | — | 0 | ⏳ |
| [**F71**](#f71) | Renda fixa com liquidez diária | — | 0 | ⏳ |
| [**F76**](#f76) | Testes das contas feitas no frontend | — | 0 | ⏳ |
| [**F77**](#f77) | Dependências em dia, com o TypeScript 7 | — | 0 | ⏳ |
| [**F80**](#f80) | Cotações do dia numa consulta só | — | 0 | ⏳ |
| [**F84**](#f84) | Dependências do backend num sentido só | — | 0 | ⏳ |
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
> **Progresso:** 0/1 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F22**](#f22) | Preço ajustado e proventos | — | 🔍 |

### M9 — Mercado sem fim

> **Objetivo:** Jogar além do último dia real sobre dados gerados que a simulação trata como reais.
>
> **Serve:** N12
>
> **Progresso:** 1/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | [F19](#f19) | 🔍 |

<details><summary>Concluído (1 item)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F24**](#f24) | Gerar dados futuros na Central de dados | — | ✅ |

</details>

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

### M13 — Mais jeitos de jogar

> **Objetivo:** Partidas com outras regras e objetivos: sem assistências, em equipes, com conquistas.
>
> **Serve:** N21, N22, N23
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F40**](#f40) | Modo Especialista | — | ⏳ |
| [**F41**](#f41) | Conquistas | — | ⏳ |

### M14 — Vitrine e primeiros passos

> **Objetivo:** Ver o jogo funcionando antes de baixar e aprender a jogar vendo, não lendo.
>
> **Serve:** N25
>
> **Progresso:** 1/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F48**](#f48) | README e docs que mostram o produto | [F47](#f47) | ⏳ |
| [**F49**](#f49) | Spike: tutorial animado | — | 🔍 |

<details><summary>Concluído (1 item)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F47**](#f47) | Gravação automática de demonstrações | — | ✅ |

</details>

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

> **Progresso:** 7/34 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F37**](#f37) | Tema escuro | — | 💤 |
| [**F44**](#f44) | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | — | 🔍 |
| [**F55**](#f55) | Modo aquisição hostil | [F44](#f44) | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | ⏳ |
| [**F68**](#f68) | Dica de firewall no lobby | — | ⏳ |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | ⏳ |
| [**F70**](#f70) | O que cada jogador está fazendo na sala | — | ⏳ |
| [**F71**](#f71) | Renda fixa com liquidez diária | — | ⏳ |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F73**](#f73) | Mapeamento único entre as regras da partida e o formulário do lobby | — | ⏳ |
| [**F74**](#f74) | Testes da conexão em tempo real e do loop da partida | — | ⏳ |
| [**F75**](#f75) | Encerramento do loop sem thread viva nem simulação presa | [F74](#f74) | ⏳ |
| [**F76**](#f76) | Testes das contas feitas no frontend | — | ⏳ |
| [**F77**](#f77) | Dependências em dia, com o TypeScript 7 | — | ⏳ |
| [**F80**](#f80) | Cotações do dia numa consulta só | — | ⏳ |
| [**F81**](#f81) | CORS restrito à mesma origem | [F6](#f6) | 💤 |
| [**F84**](#f84) | Dependências do backend num sentido só | — | ⏳ |
| [**F87**](#f87) | Erros de dado do yfinance na base | — | 🔍 |
| [**F89**](#f89) | Presets de partida | [F73](#f73) | ⏳ |
| [**F90**](#f90) | Cenários | [F89](#f89) | 🔍 |
| [**F94**](#f94) | Crédito | — | 💤 |
| [**F95**](#f95) | Expansão Governo: ganhar a eleição e mexer nas regras | — | 🔍 |
| [**F97**](#f97) | SELIC nas mãos do governo | [F95](#f95) | 🔍 |

<details><summary>Concluído (7 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F78**](#f78) | Release só sai com o check passando | — | ✅ |
| [**F79**](#f79) | Tipos do frontend que vêm da API | — | ✅ |
| [**F82**](#f82) | Repetições pequenas do frontend | — | ✅ |
| [**F83**](#f83) | Proxy do Vite na porta do config.toml | — | ✅ |
| [**F85**](#f85) | Importar duas ações da mesma empresa | — | ✅ |
| [**F86**](#f86) | Sugestão de ticker que a importação aceita | — | ✅ |
| [**F98**](#f98) | Excluir partida salva | — | ✅ |

</details>

---

## 1. Atende necessidade

| ID | Resumo | Atende (N#) | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F6** | Link de convite pela internet no lobby | N2 | — | M3 | [F5](#f5) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F8** | Modo automático: estratégia do jogador roda a cada tick | N4 | D5, D8 | M4 | [F7](#f7) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F9** | Estratégias prontas de exemplo | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F10** | Guia de como escrever uma estratégia | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F16** | Bots na sala | N8 | D8 | M6 | [F8](#f8) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F24** | Gerar dados futuros na Central de dados | N12 | D7, D14 | M9 | — | Médio | Alto | Alto | Bom | ✅ Concluído |
| **F19** | Modo backtest: partida só de estratégias, sem interação | N4, N10 | D8 | M6 | [F16](#f16) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F33** | Indicadores técnicos | N19, N4 | D2 | M11 | — | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F37** | Tema escuro | N15 | — | — | — | Médio | Baixo | Médio | Médio | 💤 Registrado, sem prioridade |
| **F40** | Modo Especialista | N21 | D2 | M13 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F41** | Conquistas | N22 | D1 | M13 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F47** | Gravação automática de demonstrações | N25 | — | M14 | — | Médio | Médio | Alto | Bom | ✅ Concluído |
| **F48** | README e docs que mostram o produto | N25 | — | M14 | [F47](#f47) | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F56** | Novidades no app | N14 | — | — | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F61** | Host remove jogador da sala | N28 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F69** | Imprevistos configuráveis e tipos novos | N23 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F70** | O que cada jogador está fazendo na sala | N29 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F71** | Renda fixa com liquidez diária | N23 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F72** | Gráficos padronizados sobre o ChartContainer do shadcn | N15 | — | — | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F76** | Testes das contas feitas no frontend | N3 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F85** | Importar duas ações da mesma empresa | N13 | — | — | — | Baixo | Baixo | Médio | Excelente | ✅ Concluído |
| **F86** | Sugestão de ticker que a importação aceita | N13 | — | — | — | Baixo | Baixo | Médio | Excelente | ✅ Concluído |
| **F89** | Presets de partida | N30 | — | — | [F73](#f73) | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F91** | Caixa de entrada e resumo do mês | N32 | — | M15 | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F92** | Noticiário da partida | N31 | D7 | M15 | [F91](#f91) | Médio | Baixo | Alto | Bom | 💤 Registrado, sem prioridade |
| **F94** | Crédito | N33 | D1 | — | — | Alto | Médio | Alto | Bom | 💤 Registrado, sem prioridade |
| **F96** | Dicas de análise técnica | N19 | — | M11 | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F98** | Excluir partida salva | N35 | — | — | — | Baixo | Baixo | Médio | Bom | ✅ Concluído |

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

<a id="f24"></a>
**F24 — Gerar dados futuros na Central de dados.** Serve N12; segue a D7 e a D14. (1) **Tela:** na Central (F21), o botão "Gerar dados futuros" abre um diálogo, com os controles à esquerda e a prévia à direita (desenho aprovado no canvas), que pede até quando gerar (cada série começa no dia útil seguinte ao seu último dado real), a semente, a temperatura (0 a 3, padrão 1), "começar em" (mercado de hoje, calmaria, normal ou crise, o `start_regime`) e o choque de inflação (−5 a +20 pontos, padrão 0, o `inflation_shock`). Temperatura e choque ganham descrição curta e dica com a leitura medida, como na página "Como o futuro é gerado" dos docs: temperatura 1 é o histórico como foi, 2 dá dois de cada três anos com queda acima de 30%, 3 é crise permanente; choque de +10 leva a inflação a uns 14% e a SELIC a 28%. O preview monta um `SeriesGenerator` uma vez e gera sem gravar poucos ativos a cada mudança de parâmetro (cerca de 0,1 s). (2) **Gravação:** os repositórios montam o `MarketHistory` (preços, segmento e setor de cada ativo e indicadores, só a origem real) e gravam o `GeneratedSeries` com origem "gerado"; indicador vira `Decimal` a partir do valor já arredondado; regerar troca o gerado comum, passando pela cópia na troca. A barra da linha do tempo já mostra o trecho gerado pelo `generated_end` da cobertura. (3) **Versão das séries (D7):** `stock_price_history` e `economic_indicator_history` ganham a coluna de versão na chave (a comum e a de cada partida), por migration (D9). As leituras do motor (`get_stocks_by_date`, `get_recent_closes`, `get_closes_on`, `get_stock_details` e o histórico de indicadores) passam a preferir a versão da partida. A cópia na troca: antes de trocar ou apagar gerado, cada partida salva cujo período, de `start_date` ao último dia simulado, cobre linhas geradas recebe a cópia delas na própria versão. (4) **Importador:** "Atualizar" troca o gerado pelo real à medida que o real chega. Hoje o `upsert_dataframe` incremental compara com a última data de qualquer origem, e um gerado no fim faria o real ser descartado: passa a comparar com a última data real e a trocar o gerado das datas que o real cobre. O `overwrite=True` apaga o histórico inteiro, gerado junto, e passa pela mesma troca. O upsert de indicador sobrescreve a origem no conflito, então a cópia na troca roda antes dele. O gerado que sobra depois do real continua do real antigo, com um salto no dia da emenda: a Central guarda até onde o real chegou e sugere "Gerar de novo" com os controles guardados, que emenda todas as séries a partir do real novo. (5) **Parâmetros do futuro gravado:** a semente, a temperatura, o "começar em" e o choque do futuro gravado ficam guardados; a Central mostra "semente 4821 · temperatura 1 · começo: hoje · choque 0" ao lado de "gerado até", e "Gerar de novo" abre o diálogo com esses valores. Não há "apagar o futuro gerado": gerar de novo substitui o anterior. Gatilho: livre; o gerador está pronto.

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

<a id="f40"></a>
**F40 — Modo Especialista.** Serve N21; segue a D2. Uma opção da partida no lobby, ao lado do critério de vitória, que tira as ajudas que decidem pelo jogador e o obriga a fazer as próprias contas. A filosofia é a do realismo de batalha do Total War e do Hardcore de Kingdom Come: Deliverance, que tiram da tela o que entrega a resposta. O que sai, pelo inventário de hoje: na renda fixa, a coluna e o card "Equivale hoje" (a taxa anual equivalente com CDI e IPCA do dia) e a ordenação por ela, que passa a ser por vencimento; no detalhe do título, a projeção "Quanto R$ X viram no vencimento", com o IR já descontado; e, quando existir, o "Resumo técnico" da F33 com a leitura compra/neutro/venda (os indicadores ficam). A pausa e a visão dos outros jogadores continuam como no modo normal. Guardado em `simulations` como uma coluna por ajuda (com o padrão "ligado"), por migration (D9); o lobby oferece os atalhos Normal e Especialista e mostra a lista para ajuste fino. O servidor omite os campos escondidos do DTO em vez de o front só não desenhá-los, porque no multiplayer quem abrir o DevTools veria a resposta.

<a id="f41"></a>
**F41 — Conquistas.** Serve N22; segue a D1. Um catálogo no código (`backend/features/achievements/catalog.py`): cada conquista tem código, nome, descrição, ícone (do `lucide-react`), categoria (Primeiros passos, Patrimônio, Mercado, Partida ou Secretas), se é secreta, e uma condição avaliada sobre os eventos e snapshots do jogador no fim de cada tick. As de meta numérica (R$ 1 milhão, 12 meses seguidos acima do CDI) trazem também uma regra de progresso, que devolve o valor atual e a meta. Exemplos: primeira compra de ação; primeiro R$ 1 milhão; bater o CDI 12 meses seguidos; atravessar uma queda de 30% do Ibovespa perdendo menos que ele; vencer uma sala cheia; vencer sem assistências (F40). A conquista desbloqueada vai para a tabela `achievements` (`user_id`, `code`, `simulation_id`, `unlocked_at`), por migration (D9), e chega ao jogador por um evento do Socket.IO que abre um toast rico, no estilo da Steam: ícone, nome e descrição, com `toast.custom` do sonner; várias no mesmo dia viram um toast só. Uma tela "Conquistas" mostra as do jogador em lista, das mais recentes para as mais antigas, com data real, partida e busca: desbloqueadas com data e partida, bloqueadas embaixo em cinza com a barra de progresso, e as secretas sem descrição até sair. Ao lado, um painel com o total, as três mais próximas de sair e o progresso por categoria. A tela fica na sidebar, em Você, e abre também no lobby, por um botão "Conquistas" no cabeçalho da sala, em rota própria sem a sidebar do jogo. As conquistas ficam no banco do host, como o resto do histórico: sem conta online, o jogador que entra na sala de outro host começa lá do zero.

<a id="f47"></a>
**F47 — Gravação automática de demonstrações.** Serve N25. `pnpm demo` (`scripts/demo/`) sobe o backend numa pasta de trabalho com o `config.toml` da demo. O banco-base (`POSTGRES_DEMO_DATABASE_URL` no `.env`) guarda cinco ações fixas, importadas dos CSVs de `scripts/demo/data/` (baixados uma vez com `pnpm demo fetch-data`), e os indicadores, que só são buscados no Banco Central quando faltam. Cada gravação roda numa cópia do banco-base, apagada no fim, e por isso sai sempre do mesmo estado. O roteiro percorre em Playwright o lobby, a compra de ação, a renda fixa, o avanço do tempo, as estatísticas e o fechamento. A gravação é o screencast do DevTools em 2× (e não o `recordVideo`, de bitrate baixo e sem o instante de cada quadro), com um cursor desenhado na página, porque o Chromium headless grava sem cursor. O zoom automático segue a ideia do Recordly: o roteiro anota onde e quando clica, e a câmera aproxima antes da ação, segura enquanto as ações seguem perto e afasta depois. Cada cena vira um GIF do `gifski` com até 10 MB, a partir de um MP4 intermediário que fica em `build/demo/`; as screenshots saem em `docs/static/demo/screens/`. As imagens não entram no `main`: `pnpm demo publish` as põe no branch `demo`, que guarda só a última publicação (um commit sem pai, com force-push), e o deploy dos docs as busca de lá; o `gh-pages` também passou a guardar só o último deploy. O link de convite é trocado por um IP de rede local fictício, para não expor o da máquina que grava. Os títulos de renda fixa são sorteados por partida, então essa cena muda um pouco a cada gravação.

<a id="f48"></a>
**F48 — README e docs que mostram o produto.** Serve N25. O README abre com um GIF do jogo rodando e, logo abaixo, o que ele faz, cada item com uma imagem ou um GIF curto da F47 (renda variável, renda fixa, estatísticas, multiplayer), o download e o link dos docs; a parte de desenvolvimento desce para o fim. Nos docs, uma página "Tour" com os GIFs das cenas, e as páginas de "Como usar" com as screenshots novas. As imagens moram no branch `demo`: o README aponta para os arquivos de lá (`github.com/<repo>/raw/demo/gifs/<cena>.gif`) e os docs usam `/demo/...`, que o deploy copia do branch. Junto, uma revisão do que está desatualizado em README e docs, página por página, contra o app de hoje. Feito com a skill de documentação (`engineering:documentation`).

<a id="f56"></a>
**F56 — Novidades no app.** Serve N14. Como as notas de patch de um jogo: o `CHANGELOG.md` da F51 vai junto no executável, o backend o serve com a versão, e o lobby mostra as novidades da versão atual. Na primeira abertura depois de atualizar, o card ou o selo de novidades fica em destaque até ser aberto (o navegador guarda a última versão vista); aberto, mostra "O que há de novo na versão X" e dá acesso ao histórico inteiro. O lugar exato no lobby, que já está cheio, sai de uma iteração no Claude Design antes de implementar.

<a id="f61"></a>
**F61 — Host remove jogador da sala.** Serve N28. Hoje a vaga só abre quando o jogador sai por conta própria: com a sala cheia ou a partida salva recusada por causa de novatos (F58), o host tem de pedir pelo chat para alguém fechar a aba. O plano: um botão "Remover" no cartão de cada jogador do lobby, só para o host, que encerra a sessão do jogador pelo mesmo caminho do `player_logout`, com um aviso "o host te removeu da sala" na tela dele, e libera a cor e a vaga na hora. Fica em aberto se a remoção também vale para participante offline da partida em andamento; a leitura provável é que não, porque tirar a linha de `simulation_players` apaga o saldo e o histórico dele.

<a id="f69"></a>
**F69 — Imprevistos configuráveis e tipos novos.** Serve N23. O modo viver de renda (F53) já nasce com os tipos de imprevisto num registro, em que cada tipo é uma entrada com nome, múltiplo da despesa mensal, efeito (sai do caixa ou corta o salário do mês seguinte) e peso no sorteio; adicionar um tipo é acrescentar uma entrada, sem mexer no motor, no log nem nas telas. Esta feature expõe esse registro ao host: no lobby, o host edita o valor de cada tipo (por exemplo, o conserto passa de 1 para 2 despesas mensais), liga e desliga tipos e cria tipos próprios com nome, valor e efeito. O sorteio continua saindo da semente da partida, então todos os jogadores seguem recebendo os mesmos imprevistos nos mesmos dias, e a configuração vale para a partida salva.

<a id="f70"></a>
**F70 — O que cada jogador está fazendo na sala.** Serve N29. Inspiração: a presença rica da Steam e dos jogos online ("Navegando nos menus", "No lobby"). **Onde aparece:** no lugar do selo "Online" do cartão de cada jogador no lobby, mantendo a bolinha verde e trocando só o texto ("Na Central de dados", "Vendo o resultado de uma partida"); a lista da tela `/join` usa o mesmo selo para quem está online. O host continua com o selo "Host" e ganha a atividade ao lado. **Mecanismo:** o front sabe a tela pela rota; um mapa único em `shared/` liga cada rota ao texto da atividade (`/lobby` → "No lobby", `/import-assets` → "Na Central de dados", `/compare-simulations` → "Comparando simulações", `/match-result/:id` → "Vendo o resultado de uma partida", `/settings` → "Nas configurações"), e toda rota fora do mapa cai em "Navegando nos menus". Tela nova ganha atividade própria acrescentando uma entrada no mapa. A cada troca de rota o cliente manda o evento `presence` pelo Socket.IO com a chave da tela; com a aba escondida (`visibilitychange`) manda "ausente" e o selo vira "Ausente", em amarelo. O servidor guarda a chave em memória no `UserManager`, junto do jogador ativo, devolve no payload dos jogadores da sala e avisa a sala pelo evento `player_activity`, sem banco e sem migration. **Durante a partida** a atividade fica de fora: dizer quem está na renda variável ou num ticker entrega a jogada aos adversários. Gatilho: quando houver mais telas fora da partida para a atividade dizer algo além de "No lobby".

<a id="f71"></a>
**F71 — Renda fixa com liquidez diária.** Serve N23. Hoje todo título de renda fixa só volta ao caixa no vencimento, então não existe onde guardar uma reserva de emergência que renda e se resgate no mesmo dia, como o CDB de liquidez diária ou o Tesouro Selic do mercado real. O plano: ofertas marcadas com liquidez diária, que o jogador resgata em qualquer pregão pelo valor corrigido até aquele dia, com o IR regressivo do prazo que passou (como já vale no vencimento); se o IOF dos primeiros 30 dias entra, fica em aberto. Fecha um desvio do modo viver de renda (F53): a reserva de emergência da página Meta conta só o caixa, porque não há o que resgatar rápido, e com esta feature passa a contar caixa + renda fixa de liquidez diária, como o design previa ("dá pra resgatar no mesmo dia, sem vender ação na baixa"). Isso dá peso de verdade ao imprevisto: quem tem a reserva aplicada cobre o conserto sem cair no cheque especial.

<a id="f72"></a>
**F72 — Gráficos padronizados sobre o `ChartContainer` do shadcn.** Serve N15; continua a padronização da interface no shadcn, que deixou o `shared/components/ui/chart.tsx` sem nenhum consumidor. Hoje cada gráfico Recharts repete o `ResponsiveContainer`, a cor da grade e um array `{ key, label, color }` de séries (que é o `ChartConfig`), e uns cinco cards de tooltip feitos à mão reimplementam o `ChartTooltipContent`. Plano: (1) antes|depois no canvas de `player-line-chart` e `networth-chart` com `ChartContainer` + `ChartTooltipContent`, para aprovar o visual do tooltip (texto menor, indicador) e decidir se o `ui/chart.tsx` ganha variante; (2) convenção de pasta por gráfico: `<nome>-chart/` com `<nome>-chart.tsx` (componente puro, recebe o dado da API por prop), `chart-data.ts` (`ChartConfig`, tipos de linha e `build*`), `chart-legend.tsx` opcional (a legenda clicável que liga e desliga série continua própria) e `index.ts` exportando só o componente; gráfico sem legenda nem transformação fica arquivo solto `<nome>-chart.tsx`; (3) migrar `player-line-chart/` (`utils.ts` + `series.ts` → `chart-data.ts`, sai o tooltip próprio), `networth-chart`, `allocation-donut` e os gráficos embutidos em `composition-tab.tsx` (`AreaChart`) e `risk-tab.tsx` (`ScatterChart`), extraídos para pastas próprias; o `stock-chart` (lightweight-charts, imperativo) fica fora do `ChartContainer`; (4) a seção Gráficos entra em `docs/docs/desenvolvimento/convencoes-frontend.md`. Gatilho: a próxima rodada de design no canvas, ou o próximo gráfico novo.

<a id="f76"></a>
**F76 — Testes das contas feitas no frontend.** Serve N3. Parte dos números da tela é calculada no navegador e não tem teste nenhum: o frontend não tem runner configurado. O escopo é só função pura de cálculo, sem teste de componente, de tela ou ponta a ponta. (1) **Runner:** Vitest como dependência de desenvolvimento, sem configuração própria (reaproveita o `vite.config.ts` e o alias `@`), script `test` no `frontend/package.json` e entrada no `pnpm run check` da raiz. (2) **Alvos:** `shared/lib/goal.ts` (fração e restante até a meta, projeção da data da meta, classificação de jogadores e equipes), `shared/lib/financial-independence.ts` (meta de independência e múltiplo de despesa anual pela taxa de retirada), `features/performance/lib/stats.ts`, `features/statistics/lib/criterion.ts`, `features/correlation/lib/correlation.ts`, `features/goal/lib/life-history.ts` e os formatadores de `shared/lib/utils/display.ts`, que são a última etapa de todo número na tela (vírgula decimal, milhar, sinal, porcentagem). (3) **Casos:** valores calculados à mão, como nos testes do backend, mais as bordas: patrimônio zero, meta já batida, histórico de um ponto só, taxa de retirada nos limites de 1% e 10%. Arquivo de teste ao lado do arquivo testado (`goal.test.ts`). Gatilho: a próxima feature que mexa numa dessas contas.

<a id="f85"></a>
**F85 — Importar duas ações da mesma empresa.** Serve N13. A importação de PETR3 depois da PETR4 caía com `UniqueViolation` em `stock_name_key`: o yfinance dá o mesmo nome às duas ("Petróleo Brasileiro S.A. - Petrobras") e o `upsert_dataframe` cria o ativo com esse nome. Feito: uma migration (D9) removeu o `UniqueConstraint("name", name="stock_name_key")` de `stock`, mantendo o `ticker` único; nenhum código busca ação pelo nome. Teste em `tests/test_ticker_profile.py`: importar dois tickers com o mesmo nome cria os dois.

<a id="f86"></a>
**F86 — Sugestão de ticker que a importação aceita.** Serve N13. A busca do yfinance sugeria `PETR4`, o combobox preenchia esse valor e a importação baixava `PETR4`, que o yfinance responde com 404 (ele só conhece `PETR4.SA`). Feito, no caminho do Finance Manager: a base guarda o código da B3 sem o `.SA` (o mesmo formato do CSV e da demonstração) e o sufixo entra só na chamada ao yfinance. `bare_ticker` tira o `.SA` digitado na entrada das rotas de importação (`PETR4.SA` vira `PETR4`), e `yfinance_symbol` o acrescenta em `from_yfinance`, no lote e no perfil quando o código tem o formato da B3; `BTC-USD`, `AAPL` e `^BVSP` seguem como estão. Uma migration de dados tirou o `.SA` dos ativos que já estavam gravados com ele, em `stock` e `ticker_profile`, e para sem mesclar quando o código já existe com e sem o sufixo. A doc de importação passou a mostrar os códigos sem `.SA`. Testes em `tests/test_import_ticker.py` e `tests/test_migrations.py`.

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

<a id="f98"></a>
**F98 — Excluir partida salva.** Serve N35. No diálogo "Simulações salvas" do lobby, cada partida ganha um botão de excluir, só para o host, com confirmação num `AlertDialog` que diz o nome, o período e quantos jogadores ela tem, e avisa que não dá para desfazer. O backend ganha `DELETE /api/simulation/{id}` com `HostVerified`, que recusa (409) a partida ativa e a selecionada no lobby. A maior parte dos dados sai em cascata, pelas chaves estrangeiras com `ondelete="CASCADE"` que apontam para `simulations`; a cópia congelada das séries da partida (as linhas com a versão igual ao id dela) não tem chave estrangeira e é apagada explicitamente na mesma transação. Depois da exclusão, um evento do Socket.IO avisa a sala para atualizar a lista. Gatilho: a lista de partidas salvas ficar difícil de usar.

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F60** | Modo servidor dedicado (--headless) | — | — | — | Baixo | Baixo | Baixo | Bom | ⏳ Pendente |
| **F67** | Abrir a pasta de configurações | — | — | — | Baixo | Baixo | Médio | Excelente | ⏳ Pendente |
| **F68** | Dica de firewall no lobby | — | — | — | Baixo | Baixo | Médio | Ótimo | ⏳ Pendente |
| **F73** | Mapeamento único entre as regras da partida e o formulário do lobby | — | — | — | Baixo | Baixo | Médio | Excelente | ⏳ Pendente |
| **F74** | Testes da conexão em tempo real e do loop da partida | — | — | — | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F75** | Encerramento do loop sem thread viva nem simulação presa | — | — | [F74](#f74) | Baixo | Médio | Médio | Bom | ⏳ Pendente |
| **F77** | Dependências em dia, com o TypeScript 7 | — | — | — | Baixo | Médio | Baixo | Médio | ⏳ Pendente |
| **F78** | Release só sai com o check passando | — | — | — | Baixo | Baixo | Alto | Excelente | ✅ Concluído |
| **F79** | Tipos do frontend que vêm da API | — | — | — | Baixo | Baixo | Médio | Excelente | ✅ Concluído |
| **F80** | Cotações do dia numa consulta só | — | — | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F81** | CORS restrito à mesma origem | — | — | [F6](#f6) | Baixo | Médio | Baixo | Médio | 💤 Registrado, sem prioridade |
| **F82** | Repetições pequenas do frontend | — | — | — | Baixo | Baixo | Baixo | Médio | ✅ Concluído |
| **F83** | Proxy do Vite na porta do config.toml | — | — | — | Baixo | Baixo | Baixo | Bom | ✅ Concluído |
| **F84** | Dependências do backend num sentido só | — | — | — | Médio | Médio | Baixo | Médio | ⏳ Pendente |

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

<a id="f60"></a>
**F60 — Modo servidor dedicado (`--headless`).** O mesmo executável, sem o navegador: para rodar numa VPS ou num PC ligado direto, sem ninguém jogando nele. `--headless` na linha de comando, ou `[server] headless = true` no `config.toml`, pula o `webbrowser.open` do `main.py`, que hoje roda sempre que o app é o executável, e imprime no terminal os endereços para entrar (o da rede local e, com a F6, o do túnel). O administrador é quem entra com o apelido de `[host] nickname`, que é como o host é definido hoje (`routes/simulation.py`). Como a recuperação de login é por apelido, num servidor exposto à internet qualquer um que digite esse apelido viraria o host; por isso, no modo servidor, o `config.toml` ganha `[host] pin`, e o login com o apelido do host só passa com ele. Serve a quem quer deixar uma sala aberta para os amigos entrarem quando quiserem, sem depender de o host estar com o computador ligado jogando.

<a id="f67"></a>
**F67 — Abrir a pasta de configurações.** O executável guarda `config.toml`, `.env` e `logs` na pasta de dados do usuário (`%LOCALAPPDATA%\SimuladorFinanceiro` no Windows), que o Windows esconde. Em vez de mudar os arquivos de lugar, a tela de configurações ganha o botão "Abrir pasta de configurações", como o "abrir pasta de mods" de vários jogos. (1) **Rota** `POST /api/settings/open-folder` em `routes/settings.py`, protegida por `verify_host` e que só aceita requisição vinda do próprio computador (`request.client.host` em `127.0.0.1` ou `::1`): o servidor também atende a rede local, e um convidado não pode abrir janelas na máquina do host. (2) **Abertura** da pasta de `app_files_dir()` com `os.startfile` no Windows, `open` no macOS e `xdg-open` no Linux, por `subprocess` sem shell. (3) **Sem interface gráfica** (servidor dedicado, Linux sem `xdg-open`) ou pedido fora do computador do host: a rota responde 409 com o caminho, e o front o mostra num campo com botão "Copiar". O caminho aparece sempre ao lado do botão, então o jogador também o encontra sem abrir nada. (4) Um segundo botão, "Abrir pasta de logs", usa a mesma rota com `target=logs`. Um aviso junto aos botões diz que `db` e `postgres` são do banco e não devem ser editados. Teste: a rota recusa quem não é o host e quem vem de outro IP, e chama o abridor do sistema (substituído por um dublê) com a pasta certa. Não serve nenhuma necessidade listada: o ganho é achar o `config.toml` sem caçar uma pasta oculta.

**Aceite:** no executável do Windows aberto por duplo clique, o botão abre o Explorer na pasta que contém o `config.toml`; um convidado da rede local que chama a rota recebe 403.

<a id="f68"></a>
**F68 — Dica de firewall no lobby.** Quando o link do lobby abre no computador do host mas não abre no dos amigos, o motivo costuma ser o firewall do Windows, e a orientação hoje só existe na página de multiplayer dos docs. Plano: no `frontend/features/lobby/components/lobby-header.tsx`, abaixo do link copiável, uma linha curta "Amigos não conseguem entrar?" que leva à seção "Amigos não conseguem entrar?" da página de multiplayer (o link do site de docs, em nova aba). Sem rota nova e sem estado: é texto estático com link. A tela do lobby é desenhada no canvas, então a linha entra primeiro lá (estado do lobby com a dica) e só depois no código.

<a id="f73"></a>
**F73 — Mapeamento único entre as regras da partida e o formulário do lobby.** As regras da partida viram valores do formulário em três lugares (`defaultValues` e o painel "Ver regras" em `lobby-match.tsx`, e o `form.reset` do `useRealtimeSyncSimulationForm`) e voltam para o corpo da API em dois (`createSimulationBody` em `lobby-match.tsx` e o `payload` do mesmo hook). As cópias já divergem: dinheiro sai por `formatMoney(toCentsString(...))` num lugar e por `displayMoney(...)` em outro, e o corpo da criação não passa por `toCentsString` enquanto o da sincronização passa. Cada campo novo de regra precisa ser lembrado nos cinco, e a regra que volta com o nome da partida anterior foi um erro desse tipo. (1) `features/lobby/lib/simulation-form.ts` com `toFormValues(settings)`, que recebe o tipo da API (`SimulationSettingsData`) e devolve `SimulationFormValues`, e `toSettingsBody(values)`, que devolve `CreateSimulationRequest`. Os dois tipos vêm da API e do schema do formulário, então um campo novo que falte numa das funções vira erro do `tsc`. (2) Os cinco lugares passam a chamar as duas funções; o `as TForm` do hook sai. (3) A ordem de chaves que o descarte de duplicata do hook compara por JSON passa a ser a da função. Se o Vitest da feature de testes de cálculo já existir, um teste de ida e volta (`toSettingsBody(toFormValues(x))` igual a `x`) fecha o contrato. Gatilho: a próxima regra de partida nova, ou qualquer mexida no lobby.

<a id="f74"></a>
**F74 — Testes da conexão em tempo real e do loop da partida.** Os módulos do multiplayer são os menos cobertos do backend: `ws_handlers.py` 21%, `simulation_loop.py` 30%, `simulation_loader.py` 30% e `simulation.py` 45% (o total é 80%). A saída do jogador ao fechar uma de duas abas foi corrigida justamente na desconexão de `ws_handlers.py`, sem teste que a cobrisse. (1) **Conexão:** testes de `register_ws_handlers` com um `AsyncServer` dublê, chamando `connect`, `disconnect` e `subscribe` direto: recusa sem cookie, cookie `client_id` que não é UUID (hoje estoura `ValueError`; passa a recusar a conexão com aviso no log), duas abas do mesmo cliente com uma fechando (o jogador fica) e a última fechando (`UserManager.unregister`). (2) **Loop:** testes do `SimulationLoopController` com um `Simulation` dublê de tick instantâneo: start, pausa, retomada, velocidade, fim natural da partida (evento `simulation_ended`, flush e simulação liberada) e exceção no meio do tick. (3) **Carga:** `simulation_loader` com o banco de teste, carregando uma partida salva e conferindo jogadores, carteira e data. Gatilho: a próxima mudança em sala, abas ou loop; junto com a correção do encerramento do loop, que precisa desses testes para provar a corrida.

<a id="f75"></a>
**F75 — Encerramento do loop sem thread viva nem simulação presa.** Dois caminhos deixam o estado da partida inconsistente. (1) O `stop()` de `simulation_loop.py` espera a thread por 5 s e, se ela não terminar, só loga e segue: marca STOPPED, roda `EventManager.flush()` e `SimulationManager.clear_simulation()` enquanto a thread ainda pode processar um tick, gravando eventos de uma simulação que já foi liberada. (2) Uma exceção no loop cai no `finally`, que só muda o estado para STOPPED: a simulação continua registrada no `SimulationManager` sem loop rodando, e o `stop()` seguinte recusa com "Nenhuma simulação está em execução". Plano: o encerramento passa a ter um dono só, a própria thread: o `stop()` sinaliza e espera, e o flush e a liberação rodam no `finally` do loop, o mesmo caminho do fim natural da partida, que já faz isso. Se o join estourar o tempo, o `stop()` devolve erro em vez de liberar por cima. A exceção no tick também notifica os clientes (`simulation_ended` com motivo de erro), para a tela não ficar congelada. `pause()` e `unpause()` passam a usar o mesmo `_lock` de start e stop. Teste: o tick dublê que bloqueia além do tempo e o que lança exceção, nos testes do loop. Depende dos testes do loop para reproduzir os dois casos. Gatilho: junto com os testes do loop.

<a id="f77"></a>
**F77 — Dependências em dia, com o TypeScript 7.** Mesmo processo da rodada anterior de dependências: dois passos, cada um fechado com `pnpm run check`. (1) **Versões menores:** `pnpm update` no frontend e `uv lock --upgrade` no backend; o maior salto é o FastAPI, de 0.143 para 0.156, com a regeneração do `docs/openapi.json` e dos tipos do front (`pnpm openapi`) para pegar mudança de schema. (2) **Versões maiores, uma por commit:** `@hookform/resolvers` 6 (o `zodResolver` é o único uso; conferir a assinatura nos formulários do lobby, da importação e das configurações) e TypeScript 7. O TypeScript 7 é o compilador reescrito em Go, que checa o projeto bem mais rápido; ele já foi testado aqui e esbarra no lint, porque o `typescript-eslint` (8.72, a versão atual) só aceita o TypeScript abaixo de 6.1. O passo do TypeScript espera essa faixa abrir; até lá o 6 continua. Gatilho: as versões menores a qualquer momento; o TypeScript 7 quando o `typescript-eslint` publicar suporte.

<a id="f78"></a>
**F78 — Release só sai com o check passando.** O `release.yml` valida a versão e monta o executável nos três sistemas sem rodar teste nem lint; o único workflow que roda `pnpm run check` é o `dependabot-check.yml`, e sem banco, então os testes que precisam do PostgreSQL são pulados lá. A validação fica no release, não em cada push. (1) O job de check do `dependabot-check.yml` vira um workflow reutilizável, `check.yml` com `on: workflow_call`, chamado pelo `dependabot-check.yml` e pelo `release.yml`, para os dois rodarem a mesma coisa. (2) O job ganha um serviço `postgres` (a imagem oficial já sobe em UTF-8) e `POSTGRES_DATABASE_URL` apontando para ele, para os testes de banco rodarem. (3) No `release.yml`, o job `build` passa a ter `needs: [validate, check]`: check vermelho, nenhum executável é montado nem publicado. Gatilho: antes do próximo release.

<a id="f79"></a>
**F79 — Tipos do frontend que vêm da API.** Dois lugares do front escrevem à mão um tipo que a API já define, e o `tsc` não acusa quando a API muda. (1) `features/portfolio/components/networth-chart.tsx` declara um `Point` com `date`, `cash`, `fixed`, `equity`, `total` e `provided` e converte para ele os campos de `PortfolioHistoryPoint` (`snapshot_date`, `total_cash`, `total_networth`…). O gráfico passa a ler `PortfolioHistoryPoint` direto (só o `goal`, que não vem do ponto, fica como campo calculado ao lado), e o mapeamento sai. (2) `features/variable-income/pages/variable-income.tsx` escreve o filtro como `"ALL" | "HELD" | "STOCK" | "FII" | "ETF"`, sem o `BDR` que o `AssetClass` da API tem: BDR só aparece em "Todos". O tipo vira `"ALL" | "HELD" | AssetClass`, e os botões saem de um `Record<AssetClass, string>` com o rótulo de cada classe, que obriga um rótulo para toda classe nova. O `LCI_LCA` da renda fixa é agrupamento de tela intencional e fica. Gatilho: a próxima mexida na carteira ou na renda variável.

<a id="f80"></a>
**F80 — Cotações do dia numa consulta só.** `StockRepository.get_stocks_by_date` faz uma consulta para listar as ações e mais uma por ação para achar o último preço até a data, e é chamado a cada dia simulado (`Simulation.next_tick` via `get_stocks`) e de novo em `get_market`; `get_recent_closes`, do mini gráfico do mercado, repete o padrão. Com 50 ações são 51 consultas por tick, multiplicadas pela velocidade da partida. (1) `get_stocks_by_date`: uma consulta com `DISTINCT ON (stock_id)` do PostgreSQL, ordenada por `stock_id, price_date DESC`, filtrando `price_date <= current_date` e trazendo a ação junto (`joinedload`). (2) `get_recent_closes`: uma consulta com `row_number() OVER (PARTITION BY stock_id ORDER BY price_date DESC)`, filtrando as `days` primeiras de cada ação e reordenando por data. (3) O cálculo de `change` e `change_pct` sai do repositório para o `CandleDTO` (um campo calculado), e o repositório só devolve dado. Conferir se o índice de `stock_price_history` cobre `(stock_id, price_date)`; se não, ele entra por migration. Teste: as duas funções devolvem o mesmo resultado que hoje numa base de teste com várias ações. Gatilho: a próxima vez que o painel de desempenho apontar o tick como lento, ou junto com mudanças no mercado.

**Aceite:** cada função faz uma consulta só, qualquer que seja o número de ações (contado por um listener `before_cursor_execute` no teste).

<a id="f81"></a>
**F81 — CORS restrito à mesma origem.** O backend libera CORS para qualquer origem com credenciais (`allow_origins=["*"]` e `allow_credentials=True` no FastAPI, `cors_allowed_origins="*"` no Socket.IO). Não é necessário: o front é servido pelo próprio backend e, no `pnpm dev`, chega pelo proxy do Vite. Hoje o que protege o jogador de um site malicioso aberto durante a partida é o cookie `client_id` com `SameSite=Lax`, que o navegador não manda em requisição de outro site; o CORS liberado só deixa outro site ler as rotas que não pedem identidade. (1) Sai o `CORSMiddleware` de `main.py`. (2) O Socket.IO fica com `cors_allowed_origins` na mesma origem, mais `http://localhost:5173` quando o modo debug estiver ligado: o proxy do Vite troca o `Host` (`changeOrigin: true`) mas mantém o `Origin` do Vite, e o Socket.IO recusaria a conexão em dev sem essa exceção. (3) Teste manual antes de fechar: jogo pelo `localhost`, por outro computador da LAN pelo IP e pelo `pnpm dev`. Gatilho: junto com o link de convite pela internet, quando o servidor passa a ficar exposto fora da LAN.

<a id="f82"></a>
**F82 — Repetições pequenas do frontend.** Seis repetições pequenas do frontend viraram uma definição cada. (1) `displayIsoDate` em `shared/lib/utils/display.ts` substitui o `formatIso` de cinco arquivos (`future-form.tsx` também tinha a cópia). (2) `niceTicks` mora em `shared/lib/chart-scale.ts` e o gráfico de patrimônio a usa no lugar do `niceScale`; as constantes de altura ficam em cada gráfico, porque os valores são diferentes. (3) `PodiumSteps` (`match-result/podium-steps.tsx`) guarda os degraus e o layout; `podium.tsx` e `team-podium.tsx` trazem só o conteúdo da coluna. (4) `AXIS_SCALE` está em `features/statistics/lib/metrics.ts`. (5) `Player` e `Team` (do relatório de visão geral) e `RiskPlayer`, `ReturnsPlayer`, `OperationsPlayer`, `CompositionPlayer` (um por aba, pois cada DTO tem formato próprio) estão em `types/api.ts`. (6) O hook de context virou `useNotificationPreferences`.

<a id="f83"></a>
**F83 — Proxy do Vite na porta do config.toml.** O proxy de `/api` e `/socket.io` em `frontend/vite.config.ts` aponta para `localhost:8000` fixo, enquanto o backend sobe na porta de `[server] port` do `config.toml`. Mudando a porta, o `pnpm dev` perde o backend sem erro claro. O `vite.config.ts` passa a ler `../config.toml` com o `smol-toml` (dependência de desenvolvimento) e usa `server.port`, com 8000 quando o arquivo não existe, que é o mesmo padrão do backend. Gatilho: a qualquer momento; é uma mudança de um arquivo.

<a id="f84"></a>
**F84 — Dependências do backend num sentido só.** Dois pontos do backend importam nos dois sentidos. (1) **Simulação e estatísticas:** `features/simulation/goal.py` usa o `mean` de `features/statistics/teams.py`, e `features/statistics/report.py` usa o `goal_on` e o `goal_steps` de `simulation/goal.py`. As contas de meta são estatística da partida: `goal.py` passa para `features/statistics/`, e a simulação (`simulation.py`, que usa `goal_on` e `goal_reached`) importa de lá. A simulação já depende das estatísticas pelo relatório, então tudo fica num sentido só. (2) **Core e renda variável:** `core/dto/order.py` e `core/dto/position.py` importam as entidades de `features/variable_income` para converter entidade em DTO. A conversão passa para a entidade (`Order.to_dto()`, `Position.to_dto()`), e o `core/dto` deixa de conhecer a feature. Fora do escopo: os imports dentro de métodos do `UserManager` para emitir eventos de tempo real, que só se desfazem mudando quem emite. Gatilho: a próxima mexida nas contas de meta ou nas ordens.

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
| **F44** | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | Serve N23; faltam taxas padrão, rendimentos e protótipo do preço da cota | — | — | 🔍 Em avaliação |
| **F49** | Spike: tutorial animado | Serve N25; compara vídeo, framer-motion e Remotion | M14 | — | 🔍 Em avaliação |
| **F55** | Modo aquisição hostil | Serve N23; faltam parte mínima no mercado e o destino do incorporado | — | [F44](#f44) | 🔍 Em avaliação |
| **F87** | Erros de dado do yfinance na base | Serve N3; encosta na F22 | — | — | 🔍 Em avaliação |
| **F90** | Cenários | Serve N22; um preset com objetivo | — | [F89](#f89) | 🔍 Em avaliação |
| **F93** | Rumores antecipados | N31; opção da partida | M15 | [F92](#f92) | 🔍 Em avaliação |
| **F95** | Expansão Governo: ganhar a eleição e mexer nas regras | N34, N23; mesmo molde da F44 | — | — | 🔍 Em avaliação |
| **F97** | SELIC nas mãos do governo | N34; opção da expansão Governo | — | [F95](#f95) | 🔍 Em avaliação |

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
**F44 — Expansão "Gestoras": abrir capital, cobrar taxa e disputar o controle.** Serve N23. Inspiração: o Capitalism Lab (oferta pública, emissão de novas ações, recompra, compra de ações dos concorrentes), o OpenTTD e o Software Inc. Lá cada jogador é uma empresa que fabrica ou transporta; aqui tudo é finanças, então a empresa de cada jogador é uma gestora, e o que ela vende é o próprio desempenho. **Como expansão:** ligável por partida no lobby, com nome, emblema e card próprios, como as DLCs dos jogos da Paradox; é enfeite visual, o sistema é o mesmo ligado ou não. **A gestora** tem nome e ticker de 4 letras mais 11, como cota de FII na B3 (o servidor recusa letras que já existam entre os ativos importados), e no livro de ofertas a linha leva a cor e a sigla do jogador, para não se confundir com ativo real. O jogador a funda levando parte da carteira em troca de cotas. **É um fundo fechado listado, como um FII, o que junta as duas ideias:** (1) **oferta pública** quando o gestor quiser — cotas novas ao preço do patrimônio por cota (patrimônio de R$ 100 mil em 1.000 cotas dá R$ 100), e o dinheiro de quem compra entra na gestora: é investir no amigo; (2) **mercado** — depois da oferta, as cotas são negociadas no livro de ofertas que a renda variável já tem, e o preço sai da oferta e da procura, acima do patrimônio por cota (ágio) quando a sala acredita no gestor e abaixo (deságio) quando não; (3) **emissão de novas cotas**, com preferência para quem já é cotista, e **recompra**, que vale quando a cota está com deságio (pagar R$ 80 por R$ 100 de patrimônio valoriza a cota de quem fica); (4) **taxas** — todo mês a gestora paga aos gestores taxa de administração sobre o patrimônio e taxa de performance sobre o que passar do CDI, como um fundo real; (5) **controle** — quem juntar mais da metade das cotas troca o gestor pela assembleia de cotistas e passa a operar a carteira e a receber as taxas. **Por que abrir capital, e quando:** as taxas são sobre o dinheiro dos outros, e com ágio as cotas do próprio gestor valem mais no ranking; o custo é ficar exposto, porque vender mais da metade abre a porta para perder o controle. Abrir cedo, sem histórico, tende a sair com pouca procura; abrir depois de um bom ano tende a sair com ágio. **Co-op:** a gestora pode ter mais de um gestor, por convite; eles operam a mesma carteira e dividem as taxas, como sócios da mesma empresa. **Regras para o cálculo fechar:** só pessoas compram cotas, nunca gestoras, o que impede a participação cruzada (A com cotas da B, que tem cotas da A); no ranking, cada jogador soma a carteira pessoal, as cotas que tem pelo preço de mercado e as taxas recebidas, e a carteira da gestora só conta através das cotas, sem contar o mesmo dinheiro duas vezes. **Estrutura:** hoje eventos e snapshots pertencem ao jogador (`user_id`); a gestora precisa de carteira própria, então entra uma tabela `portfolios` e eventos e snapshots passam a apontar para a carteira, com a carteira pessoal de cada jogador migrada uma a uma (D9); a cota é um ativo no livro de ofertas, com o patrimônio por cota publicado a cada dia. Falta: os valores padrão das taxas, se a gestora distribui rendimentos como um FII, e um protótipo do preço da cota no livro com bots (F16) comprando e vendendo.

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
**F95 — Expansão "Governo": ganhar a eleição e mexer nas regras.** Ligado à N34 e à N23. Mesmo molde da expansão "Gestoras" (F44): ligável por partida no lobby, com nome, emblema e card próprios. Inspiração: a expansão de cidades do Capitalism Lab, em que o empresário funda um partido e disputa a prefeitura. (1) **Eleição:** a candidatura abre um ano antes da eleição. Concorrem os jogadores que se inscrevem e candidatos do computador. Cada um define uma verba mensal de campanha, que sai do caixa e não volta, e assim compete com investir; a verba vira apoio aos poucos e com retorno decrescente (dobrar a verba não dobra o voto), e por isso começar cedo pesa. Cada candidato marca a promessa numa régua de "impostos baixos" a "gasto alto". Uma pesquisa de intenção de voto mostra a corrida num gráfico ao longo dos meses, com a cor e a sigla de cada jogador. Mandato de 4 anos, com uma reeleição. (2) **Impostos por setor:** o governo mexe nos impostos que o jogo já cobra (os 15% e 20% da renda variável, a isenção de vendas de ações até R$ 20 mil, a tabela regressiva da renda fixa, a isenção de LCI e LCA) e pode taxar ou isentar um setor ou segmento, que todo ativo já tem: "isentar o IR de energia", "taxar bancos em mais 5 pontos". Imposto vale em qualquer período, porque não mexe em preço. (3) **Gasto público e inflação, como o impacto de preço:** a medida vira um efeito por cima das séries, do mesmo jeito que o impacto de preço de ordens grandes: o preço do dia é o da série vezes (1 + a soma dos efeitos ativos), cada efeito nasce de um evento, vale cheio no começo e decai com o tempo, e tudo se reconstrói a partir dos eventos numa retomada. Aqui o efeito soma pontos ao IPCA, e o resto segue os coeficientes que a D14 já mediu: a SELIC reage com 1,5 vez a inflação (quando é autônoma) e a bolsa cai 2,9% no trimestre por ponto de alta da SELIC, ativo a ativo pelo beta. A série guardada não muda, e por isso vale também na história real. (4) **SELIC:** configurável na expansão. Por padrão o Banco Central é autônomo, como é no Brasil desde 2021, e a SELIC continua reagindo à inflação como no gerador; a outra opção a põe nas mãos do governo (F97). (5) **Popularidade:** uma métrica de aprovação do governo atual, sempre à vista, com o histórico num gráfico. Cai com inflação alta, que deixa as pessoas nervosas, com imposto novo e com promessa descumprida (o que foi feito contra a régua da campanha); sobe com inflação controlada e bolsa subindo. **Freio decidido: aprovação e reeleição.** Aprovação baixa perde a reeleição e, abaixo de um piso por meses seguidos, leva a impeachment. Falta definir: os outros freios (um Congresso que vota cada medida, com chance pela aprovação; o prazo para valer, como a noventena e a anterioridade, que dão aos outros tempo de reagir a um imposto novo; o truste cego, que congela a carteira do presidente ou a entrega a um bot, porque ele sabe da medida antes de todos); os pesos da aprovação; como o presidente vence a partida, se pelo patrimônio, pela aprovação ou pelos dois; e quem são os candidatos do computador.

<a id="f97"></a>
**F97 — SELIC nas mãos do governo.** Ligado à N34; uma opção da expansão "Governo" (F95), no lugar do Banco Central autônomo. (1) **Ritmo do Copom:** o governo decide a SELIC em reuniões a cada 45 dias, como o Copom, que se reúne 8 vezes por ano desde 2006; entre reuniões ela não muda. (2) **Teto por reunião, pelo que aconteceu de verdade.** Das 150 mudanças da meta da SELIC entre 2000 e outubro de 2026 (série do Banco Central): 34 foram de 0,25 ponto, 67 de 0,5, 19 de 0,75, 19 de 1, 7 de 1,5, uma de 2, uma de 2,5 (cortes de 2003) e duas de 3 (as altas da crise de 2002); desde 2006, nunca passou de 1,5. O teto acompanha isso: até 0,75 ponto por reunião em tempo normal (80% das mudanças reais), 1,5 com a inflação bem acima da meta, como em 2021 e 2022, e 3 só com a inflação explodindo, como em 2002. (3) **O preço de cada lado:** a SELIC abaixo do que o Banco Central autônomo faria (a da série, ou a do gerador) faz a inflação subir com alguns meses de atraso, pelo mesmo mecanismo de efeito por cima das séries da F95, e inflação alta derruba a aprovação; a SELIC alta demais derruba a bolsa pelo coeficiente da D14, o que também pesa na aprovação. Falta definir: quanto a inflação reage à SELIC e com quanto atraso (medir no histórico, como a D14 mediu a reação da SELIC à inflação), e os limites de inflação que liberam cada degrau do teto.
