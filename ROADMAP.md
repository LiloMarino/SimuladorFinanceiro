<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-10-23):** Prioridades revistas: servidor dedicado (F60) e imprevistos configuráveis (F69) sem prioridade; caixa de entrada (F91) e noticiário (F92) pendentes; comprar tudo sem estourar o caixa (F121), erros do yfinance (F87) e preço ajustado e proventos (F22) decididos e pendentes.

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | [F22](#f22), [F87](#f87) | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F10](#f10), [F19](#f19), [F33](#f33), [F108](#f108), [F110](#f110), [F111](#f111), [F127](#f127) | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | — | — |
| **N6** | Comparar resultados de simulações diferentes | — | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | [F22](#f22) | — |
| **N8** | Jogar contra oponentes controlados pelo computador | — | — |
| **N9** | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — |
| **N10** | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | [F19](#f19) | — |
| **N11** | Que o cenário econômico simulado seja o histórico real | — | — |
| **N12** | Continuar jogando depois do último dia com dado real | — | — |
| **N13** | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | — |
| **N14** | Atualizar para uma versão nova sem perder as partidas salvas | [F56](#f56) | — |
| **N15** | Usar uma interface agradável e coerente, à altura de um jogo | [F37](#f37), [F72](#f72), [F119](#f119), [F121](#f121), [F124](#f124) | — |
| **N16** | Ver a carteira e o mercado por setor e segmento | — | — |
| **N17** | Enxergar a estrutura do banco e esboçar mudanças nela | — | — |
| **N18** | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — |
| **N19** | Analisar um ativo com as ferramentas de um trader | [F33](#f33), [F96](#f96) | — |
| **N20** | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | — |
| **N21** | Jogar "na unha", sem a interface apontar a melhor escolha | — | — |
| **N22** | Ter objetivos para buscar além de vencer a partida | [F122](#f122) | — |
| **N23** | Jogar com os amigos de outras formas além de cada um por si | [F69](#f69), [F101](#f101) | — |
| **N24** | Saber onde está a lentidão durante uma partida | — | — |
| **N25** | Entender o que é o simulador e como se joga, sem ler um manual | [F126](#f126) | — |
| **N26** | Achar a causa de um erro sem vasculhar o log inteiro | — | — |
| **N27** | Entrar numa partida que já começou | — | — |
| **N28** | Liberar uma vaga sem depender de o jogador sair | [F61](#f61) | — |
| **N29** | Saber o que cada jogador está fazendo enquanto a partida não começa | — | — |
| **N30** | Repetir uma configuração de partida sem montá-la de novo | [F89](#f89), [F118](#f118), [F119](#f119) | — |
| **N31** | Saber o que está movendo o mercado da partida, como quem lê o noticiário | [F92](#f92) | — |
| **N32** | Saber como foi o mês sem montar a conta | [F91](#f91) | — |
| **N33** | Investir com dinheiro emprestado, pagando o juro do momento | [F111](#f111) | — |
| **N34** | Disputar o poder de mudar as regras da economia da partida | — | — |
| **N35** | Tirar da lista as partidas que não interessam mais | — | — |
| **N36** | Encontrar rapidamente os menores e maiores valores nos dados do jogo | — | — |
| **N37** | Comprar bitcoin do jeito que dá na vida real, em frações | [F113](#f113), [F127](#f127) | — |
| **N38** | Saber quando as estatísticas vão mudar, sem achar que travaram | — | — |
| [**F5**](#f5) | Spike: provider de túnel pela internet | — | 🔍 |
| [**F6**](#f6) | Link de convite pela internet no lobby | — | ⏳ |
| [**F10**](#f10) | Guia de como escrever uma estratégia | — | ⏳ |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F19**](#f19) | Modo backtest: partida só de estratégias, sem interação | — | ⏳ |
| [**F22**](#f22) | Preço ajustado e proventos | — | ⏳ |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | — | 🔍 |
| [**F33**](#f33) | Indicadores técnicos | — | ⏳ |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 |
| [**F37**](#f37) | Tema escuro | — | 💤 |
| [**F44**](#f44) | Expansão Gestoras: fundar a gestora e abrir capital | — | 🔍 |
| [**F49**](#f49) | Spike: animação dos tópicos do tutorial | — | 🔍 |
| [**F55**](#f55) | Modo aquisição hostil | — | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | 💤 |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | ⏳ |
| [**F68**](#f68) | Dica de firewall no lobby | — | ⏳ |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | 💤 |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F81**](#f81) | CORS restrito à mesma origem | — | 💤 |
| [**F87**](#f87) | Erros de dado do yfinance na base | — | ⏳ |
| [**F89**](#f89) | Presets de partida | — | ⏳ |
| [**F90**](#f90) | Cenários | — | 🔍 |
| [**F91**](#f91) | Caixa de entrada e resumo do mês | — | ⏳ |
| [**F92**](#f92) | Noticiário da partida | — | ⏳ |
| [**F93**](#f93) | Rumores antecipados | — | 🔍 |
| [**F95**](#f95) | Expansão Governo: partidos, eleição e impostos | — | 🔍 |
| [**F96**](#f96) | Dicas de análise técnica | — | 💤 |
| [**F97**](#f97) | SELIC nas mãos do governo | — | 🔍 |
| [**F100**](#f100) | Proventos na carteira e nas telas | — | 🔍 |
| [**F101**](#f101) | Carteira separada do jogador | — | 💤 |
| [**F102**](#f102) | Gestoras: emissão de novas cotas e recompra | — | 🔍 |
| [**F103**](#f103) | Gestoras: troca de gestor pela assembleia | — | 🔍 |
| [**F104**](#f104) | Gestoras: co-gestores | — | 🔍 |
| [**F105**](#f105) | Gestoras: rendimentos mensais | — | 🔍 |
| [**F106**](#f106) | Governo: gasto público e inflação | — | 🔍 |
| [**F107**](#f107) | Perfis de público na eleição | — | 🔍 |
| [**F108**](#f108) | Bot pela API: guia e exemplo | — | ⏳ |
| [**F110**](#f110) | Combinar estratégias | — | 💤 |
| [**F111**](#f111) | Crédito para estratégias e bots | — | 💤 |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | 🔍 |
| [**F121**](#f121) | Comprar tudo a mercado sem estourar o caixa | — | ⏳ |
| [**F122**](#f122) | Novas conquistas para as features recentes e antigas | — | ⏳ |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 🔍 |
| [**F124**](#f124) | Voltar o quadrado da marca no cabeçalho da sala | — | ⏳ |
| [**F125**](#f125) | Revisão das regras de lint e da checagem de tipos | — | 🔍 |
| [**F126**](#f126) | Janela "Como jogar" | — | ⏳ |
| [**F127**](#f127) | Estratégias e bots operam cripto em fração | — | 💤 |

<details>
<summary><strong>Concluído / decidido / descartado (18 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | [F22](#f22), [F122](#f122) | ✅ |
| **D2** | Cálculo financeiro acontece só no backend; o frontend exibe | [F33](#f33) | ✅ |
| **D3** | Dinheiro e quantidade trafegam como Decimal serializado em string | [F22](#f22), [F113](#f113), [F121](#f121), [F127](#f127) | ✅ |
| **D4** | Banco de dados embarcado no executável | — | ✅ |
| **D6** | A retomada continua no dia seguinte ao último evento | — | ✅ |
| **D7** | O simulador lê as séries sem saber a origem | [F22](#f22), [F92](#f92) | ✅ |
| **D8** | Bot, modo automático e backtest são o mesmo mecanismo | [F19](#f19), [F110](#f110), [F111](#f111) | ✅ |
| **D9** | De onde nasce uma mudança de schema | [F101](#f101), [F118](#f118) | ✅ |
| **D10** | Como a nota geral é calculada | — | ✅ |
| **D11** | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | ✅ |
| **D12** | Como numerar as versões | — | ✅ |
| **D13** | Um canal de tempo real só: Socket.IO, com fallback de polling | — | ✅ |
| **D14** | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | — | ✅ |
| **D15** | Lint com oxlint e o TypeScript 7 com a API do 6 ao lado | — | ✅ |
| **D16** | Estratégias do app no host, personalização pela API | [F108](#f108) | ✅ |
| [**F113**](#f113) | Classe de ativo cripto com quantidade fracionária | — | ✅ |
| [**F118**](#f118) | Lembrar a última configuração da partida | — | ✅ |
| [**F119**](#f119) | Seletor de período da partida com linha do tempo | — | ✅ |

</details>

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: as `F#` que podem ser pegas agora — toda dependência já ✅. "Destrava" é quantas `F#` em aberto esperam por ela, direta ou indiretamente; é por aí que a tabela está ordenada. 💤 (sem prioridade) e 🚫 não entram.

| ID | Resumo | Marco | Destrava | Status |
| --- | --- | --- | --- | --- |
| [**F95**](#f95) | Expansão Governo: partidos, eleição e impostos | — | 3 | 🔍 |
| [**F5**](#f5) | Spike: provider de túnel pela internet | M3 | 2 | 🔍 |
| [**F22**](#f22) | Preço ajustado e proventos | M8 | 2 | ⏳ |
| [**F91**](#f91) | Caixa de entrada e resumo do mês | M15 | 2 | ⏳ |
| [**F19**](#f19) | Modo backtest: partida só de estratégias, sem interação | M6 | 1 | ⏳ |
| [**F33**](#f33) | Indicadores técnicos | M11 | 1 | ⏳ |
| [**F89**](#f89) | Presets de partida | — | 1 | ⏳ |
| [**F10**](#f10) | Guia de como escrever uma estratégia | M4 | 0 | ⏳ |
| [**F49**](#f49) | Spike: animação dos tópicos do tutorial | M14 | 0 | 🔍 |
| [**F56**](#f56) | Novidades no app | — | 0 | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | 0 | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | 0 | ⏳ |
| [**F68**](#f68) | Dica de firewall no lobby | — | 0 | ⏳ |
| [**F87**](#f87) | Erros de dado do yfinance na base | — | 0 | ⏳ |
| [**F108**](#f108) | Bot pela API: guia e exemplo | M4 | 0 | ⏳ |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | 0 | 🔍 |
| [**F121**](#f121) | Comprar tudo a mercado sem estourar o caixa | — | 0 | ⏳ |
| [**F122**](#f122) | Novas conquistas para as features recentes e antigas | — | 0 | ⏳ |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 0 | 🔍 |
| [**F124**](#f124) | Voltar o quadrado da marca no cabeçalho da sala | — | 0 | ⏳ |
| [**F125**](#f125) | Revisão das regras de lint e da checagem de tipos | — | 0 | 🔍 |
| [**F126**](#f126) | Janela "Como jogar" | M14 | 0 | ⏳ |

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
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F10**](#f10) | Guia de como escrever uma estratégia | — | ⏳ |
| [**F108**](#f108) | Bot pela API: guia e exemplo | — | ⏳ |

### M6 — Estratégia contra estratégia

> **Objetivo:** Pôr bots na sala e rodar uma partida só de estratégias, do começo ao fim, sem esperar.
>
> **Serve:** N4, N8, N10
>
> **Progresso:** 0/1 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F19**](#f19) | Modo backtest: partida só de estratégias, sem interação | — | ⏳ |

### M8 — Dados reais, cuidados fora da partida

> **Objetivo:** Indicadores e preços fiéis ao histórico, geridos numa central antes de jogar.
>
> **Serve:** N3, N11, N13
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F22**](#f22) | Preço ajustado e proventos | — | ⏳ |
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
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F49**](#f49) | Spike: animação dos tópicos do tutorial | — | 🔍 |
| [**F126**](#f126) | Janela "Como jogar" | — | ⏳ |

### M15 — Notícias e resumo do mês

> **Objetivo:** A partida conta o que acontece no mercado e como foi o mês de cada jogador.
>
> **Serve:** N31, N32
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F91**](#f91) | Caixa de entrada e resumo do mês | — | ⏳ |
| [**F92**](#f92) | Noticiário da partida | [F91](#f91) | ⏳ |
| [**F93**](#f93) | Rumores antecipados | [F92](#f92) | 🔍 |

### Sem marco

> **Progresso:** 3/36 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F37**](#f37) | Tema escuro | — | 💤 |
| [**F44**](#f44) | Expansão Gestoras: fundar a gestora e abrir capital | [F101](#f101) | 🔍 |
| [**F55**](#f55) | Modo aquisição hostil | [F103](#f103) | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | 💤 |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | ⏳ |
| [**F68**](#f68) | Dica de firewall no lobby | — | ⏳ |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | 💤 |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F81**](#f81) | CORS restrito à mesma origem | [F6](#f6) | 💤 |
| [**F87**](#f87) | Erros de dado do yfinance na base | — | ⏳ |
| [**F89**](#f89) | Presets de partida | — | ⏳ |
| [**F90**](#f90) | Cenários | [F89](#f89) | 🔍 |
| [**F95**](#f95) | Expansão Governo: partidos, eleição e impostos | — | 🔍 |
| [**F97**](#f97) | SELIC nas mãos do governo | [F106](#f106) | 🔍 |
| [**F101**](#f101) | Carteira separada do jogador | — | 💤 |
| [**F102**](#f102) | Gestoras: emissão de novas cotas e recompra | [F44](#f44) | 🔍 |
| [**F103**](#f103) | Gestoras: troca de gestor pela assembleia | [F44](#f44) | 🔍 |
| [**F104**](#f104) | Gestoras: co-gestores | [F44](#f44) | 🔍 |
| [**F105**](#f105) | Gestoras: rendimentos mensais | [F44](#f44), [F100](#f100) | 🔍 |
| [**F106**](#f106) | Governo: gasto público e inflação | [F95](#f95) | 🔍 |
| [**F107**](#f107) | Perfis de público na eleição | [F95](#f95) | 🔍 |
| [**F110**](#f110) | Combinar estratégias | — | 💤 |
| [**F111**](#f111) | Crédito para estratégias e bots | — | 💤 |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | 🔍 |
| [**F121**](#f121) | Comprar tudo a mercado sem estourar o caixa | — | ⏳ |
| [**F122**](#f122) | Novas conquistas para as features recentes e antigas | — | ⏳ |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 🔍 |
| [**F124**](#f124) | Voltar o quadrado da marca no cabeçalho da sala | — | ⏳ |
| [**F125**](#f125) | Revisão das regras de lint e da checagem de tipos | — | 🔍 |
| [**F127**](#f127) | Estratégias e bots operam cripto em fração | [F113](#f113) | 💤 |

<details><summary>Concluído (3 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F113**](#f113) | Classe de ativo cripto com quantidade fracionária | — | ✅ |
| [**F118**](#f118) | Lembrar a última configuração da partida | — | ✅ |
| [**F119**](#f119) | Seletor de período da partida com linha do tempo | — | ✅ |

</details>

---

## 1. Atende necessidade

| ID | Resumo | Atende (N#) | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F6** | Link de convite pela internet no lobby | N2 | — | M3 | [F5](#f5) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F10** | Guia de como escrever uma estratégia | N4 | — | M4 | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F19** | Modo backtest: partida só de estratégias, sem interação | N4, N10 | D8 | M6 | — | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F33** | Indicadores técnicos | N19, N4 | D2 | M11 | — | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F37** | Tema escuro | N15 | — | — | — | Médio | Baixo | Médio | Médio | 💤 Registrado, sem prioridade |
| **F56** | Novidades no app | N14 | — | — | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F61** | Host remove jogador da sala | N28 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F69** | Imprevistos configuráveis e tipos novos | N23 | — | — | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F72** | Gráficos padronizados sobre o ChartContainer do shadcn | N15 | — | — | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F89** | Presets de partida | N30 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F91** | Caixa de entrada e resumo do mês | N32 | — | M15 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F92** | Noticiário da partida | N31 | D7 | M15 | [F91](#f91) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F96** | Dicas de análise técnica | N19 | — | M11 | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F101** | Carteira separada do jogador | N23 | D9 | — | — | Alto | Alto | Médio | Médio | 💤 Registrado, sem prioridade |
| **F108** | Bot pela API: guia e exemplo | N4 | D16 | M4 | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F110** | Combinar estratégias | N4 | D8 | — | — | Médio | Médio | Médio | Bom | 💤 Registrado, sem prioridade |
| **F111** | Crédito para estratégias e bots | N4, N33 | D8 | — | — | Baixo | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F113** | Classe de ativo cripto com quantidade fracionária | N37 | D3 | — | — | Médio | Médio | Médio | Bom | ✅ Concluído |
| **F118** | Lembrar a última configuração da partida | N30 | D9 | — | — | Baixo | Baixo | Médio | Bom | ✅ Concluído |
| **F122** | Novas conquistas para as features recentes e antigas | N22 | D1 | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F124** | Voltar o quadrado da marca no cabeçalho da sala | N15 | — | — | — | Baixo | Baixo | Baixo | Bom | ⏳ Pendente |
| **F126** | Janela "Como jogar" | N25 | — | M14 | — | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F127** | Estratégias e bots operam cripto em fração | N4, N37 | D3 | — | [F113](#f113) | Médio | Baixo | Baixo | Regular | 💤 Registrado, sem prioridade |
| **F119** | Seletor de período da partida com linha do tempo | N15, N30 | — | — | — | — | — | — | — | ✅ Concluído |
| **F121** | Comprar tudo a mercado sem estourar o caixa | N15 | D3 | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F87** | Erros de dado do yfinance na base | N3 | — | — | — | Baixo | Médio | Médio | Bom | ⏳ Pendente |
| **F22** | Preço ajustado e proventos | N3, N7 | D1, D3, D7 | M8 | — | Alto | Alto | Alto | Bom | ⏳ Pendente |

<a id="f6"></a>
**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Abrir para a internet exige fechar antes a tomada do host: hoje ser host é ter o nickname do `config.toml`, e com o host desconectado qualquer jogador assume esse nickname por `/api/user/claim` e passa a poder parar a partida e apagar partidas salvas. O app gera um segredo a cada abertura e abre o navegador do host com ele; o servidor reconhece como host só a sessão que apresentou o segredo, e `/api/user/claim` recusa o nickname do host. O endereço de origem não distingue o host, porque num túnel o tráfego de fora costuma chegar ao servidor pela própria máquina. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada; com o host desconectado, nenhum outro jogador consegue virar host.

<a id="f10"></a>
**F10 — Guia de como escrever uma estratégia.** Origem: #49. Página no Docusaurus (grupo "Desenvolvimento"): como acrescentar uma estratégia ao app, com a classe base, o contexto que ela recebe a cada tick, como declarar nome e parâmetros e onde registrá-la para aparecer na página de Estratégias, nos bots e no backtest; uma das estratégias da F9 comentada linha a linha; e os limites (uma exceção devolve o jogador ao manual, o estado interno não volta na retomada). Quem não quer mexer no código do app tem o bot pela API (F108). Gatilho: F8 concluída — a API da classe base só fica estável depois dela.

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

<a id="f72"></a>
**F72 — Gráficos padronizados sobre o `ChartContainer` do shadcn.** Serve N15; continua a padronização da interface no shadcn, que deixou o `shared/components/ui/chart.tsx` sem nenhum consumidor. Hoje cada gráfico Recharts repete o `ResponsiveContainer`, a cor da grade e um array `{ key, label, color }` de séries (que é o `ChartConfig`), e uns cinco cards de tooltip feitos à mão reimplementam o `ChartTooltipContent`. Plano: (1) antes|depois no canvas de `player-line-chart` e `networth-chart` com `ChartContainer` + `ChartTooltipContent`, para aprovar o visual do tooltip (texto menor, indicador) e decidir se o `ui/chart.tsx` ganha variante; (2) convenção de pasta por gráfico: `<nome>-chart/` com `<nome>-chart.tsx` (componente puro, recebe o dado da API por prop), `chart-data.ts` (`ChartConfig`, tipos de linha e `build*`), `chart-legend.tsx` opcional (a legenda clicável que liga e desliga série continua própria) e `index.ts` exportando só o componente; gráfico sem legenda nem transformação fica arquivo solto `<nome>-chart.tsx`; (3) migrar `player-line-chart/` (`utils.ts` + `series.ts` → `chart-data.ts`, sai o tooltip próprio), `networth-chart`, `allocation-donut` e os gráficos embutidos em `composition-tab.tsx` (`AreaChart`) e `risk-tab.tsx` (`ScatterChart`), extraídos para pastas próprias; o `stock-chart` (lightweight-charts, imperativo) fica fora do `ChartContainer`; (4) a seção Gráficos entra em `docs/docs/desenvolvimento/convencoes-frontend.md`. Gatilho: a próxima rodada de design no canvas, ou o próximo gráfico novo.

<a id="f89"></a>
**F89 — Presets de partida.** Serve N30. No lobby, o host salva a configuração atual com um nome ("Salvar como preset") e carrega um preset salvo, que preenche o formulário inteiro: período, capital inicial, aporte, regras, modo de jogo e os parâmetros do futuro gerado (temperatura, bioma inicial e choque de inflação). Os presets moram numa tabela própria (nome, data, configuração em JSON validada pelo mesmo DTO de criação da partida), por migration (D9), com rotas para listar, salvar, renomear e apagar. Alguns vêm prontos e não se apagam ("Iniciante", "Clássico", "Realista"). Preset que traz um campo que a versão atual não conhece ignora o campo, e o que falta vem do padrão, então um preset antigo continua abrindo. Gatilho: F73 concluída, porque salvar e carregar é mais um lugar que converte entre as regras da partida e o formulário, e a F73 deixa essa conversão num lugar só.

<a id="f91"></a>
**F91 — Caixa de entrada e resumo do mês.** Serve N32. Como a caixa de entrada dos jogos de gerência de time: tudo o que a partida tem a contar chega num lugar só, sem pausar. (1) **Caixa de entrada:** um envelope na barra da partida, com o número de não lidas, abre um painel lateral com as entradas por data. Cada entrada tem um tipo (resumo, e depois notícia e conquista) e é de um jogador ou da sala inteira. Fica numa tabela `inbox_entries` (simulação, jogador ou nulo para a sala, data do jogo, tipo, conteúdo em JSONB, lida), é criada pelo motor da simulação na virada do mês e chega pelo Socket.IO com um aviso curto que some sozinho. (2) **Resumo do mês, de cada jogador:** patrimônio no início e no fim, rentabilidade do mês ao lado do CDI e do Ibovespa, melhor e pior posição, proventos recebidos, IR pago, aportes e a posição no ranking com quanto ela andou. Sai dos snapshots e dos eventos do mês, calculado no backend. (3) **Retrospectiva do ano:** na virada do ano, uma entrada maior com o ano mês a mês num gráfico pequeno, o melhor mês e a maior queda. Gatilho: antes do noticiário, que entrega as notícias por esta caixa.

<a id="f92"></a>
**F92 — Noticiário da partida.** Serve N31; segue a D7. Um noticiário sintético: as manchetes nascem das séries que a partida já lê, e por isso funcionam igual no futuro gerado, que é onde o jogo passa a maior parte do tempo, e na história real. Sem LLM e sem internet. (1) **Motor genérico:** uma lista de regras, cada uma olhando as séries no tick e, quando dispara, criando uma entrada da sala na caixa de entrada (F91) a partir de um modelo de texto com algumas variações, para a mesma frase não se repetir. Regra nova é só mais um item da lista. (2) **Macro, as manchetes padrão:** Copom subiu, baixou ou manteve a SELIC, com o tamanho ("Copom sobe a SELIC em 0,5 ponto, para 14,25%"); IPCA do mês acima ou abaixo do anterior; Ibovespa no recorde ou na maior queda do ano. (3) **Empresas:** a mesma lógica para um ativo que sobe ou cai mais de um limite no dia, chega à máxima de 52 semanas ou anuncia provento. O movimento ganha uma causa sintética plausível, sorteada de um banco de causas por setor e direção ("resultado do trimestre acima do esperado", "troca no comando", "vendas de fim de ano fracas" para o varejo). A notícia sai depois do movimento: dá contexto e não dá vantagem. (4) As notícias de um ativo aparecem também na tela dele, como marcadores no gráfico de preço. (5) **Extra, para período real:** marcos históricos curados à mão (crise de 2008, Joesley Day em 2017, Covid em março de 2020), num arquivo de dados com data, manchete e ativos ligados. O futuro gerado sempre começa depois do último dia real, então um marco datado só aparece em período real, e um cenário (F90) pode trazer os seus. Gatilho: depois da caixa de entrada.

<a id="f96"></a>
**F96 — Dicas de análise técnica.** Serve N19. Aprender análise técnica jogando: o gráfico aponta e explica o que um trader enxergaria, para quem quer jogar pelo gráfico sem já saber as regras. É ajuda, então o modo Especialista (F40) a desliga, como as outras. (1) **Padrões de vela:** regras fixas sobre abertura, máxima, mínima e fechamento de cada pregão detectam uns dez padrões clássicos (martelo, estrela cadente, engolfo de alta e de baixa, doji, três soldados brancos). O candle ganha um marcador; ao passar o mouse, um card com o nome, o desenho do padrão e o que ele costuma sugerir. **E se ele acertou:** o card conta quantas vezes o padrão apareceu neste ativo no período já jogado e em quantas o preço foi para o lado sugerido nos 5 pregões seguintes ("apareceu 12 vezes; em 7 o preço subiu"), o que ensina também que padrão não é garantia. (2) **Indicadores (F33):** as faixas ganham legenda (IFR acima de 70, "sobrecomprado": subiu rápido demais e costuma devolver; abaixo de 30, "sobrevendido") e os cruzamentos do MACD e das médias móveis ganham marcador com uma frase do que significam. (3) **Desafio da vela:** quando aparece um padrão, o jogo pergunta "e agora, sobe ou desce?" e confere dias depois, com um placar de acertos que pode virar conquista (F41). Gatilho: com o gráfico de indicadores; os padrões de vela não dependem dele.

<a id="f101"></a>
**F101 — Carteira separada do jogador.** Serve N23; segue a D9. A base da expansão Gestoras (F44): hoje eventos e snapshots pertencem ao jogador (`user_id`), e a gestora precisa de carteira própria. Entra uma tabela `portfolios`, e eventos e snapshots passam a apontar para a carteira; a carteira pessoal de cada jogador é migrada uma a uma, inclusive nas partidas salvas. Nada muda na tela: cada jogador segue com uma carteira só até a F44 existir. Gatilho: a F44 sair da avaliação.

<a id="f108"></a>
**F108 — Bot pela API: guia e exemplo.** Serve N4; segue a D16. Página no Docusaurus (grupo "Como Usar") para quem quer uma estratégia própria sem mexer no código do app: o bot é um programa na máquina do jogador que entra na partida como um jogador qualquer. O guia percorre o caminho medido no spike: cookie em `/api/session/init`, nickname do bot em `/api/user/register`, entrada na partida em `/api/simulation/join` (com uma cor da paleta), assinatura de `simulation_update` no Socket.IO e, a cada tick, leitura de `/api/variable-income` (cotações com setor e segmento), `/api/variable-income/{ativo}` (histórico), `/api/portfolio`, `/api/portfolio/cash`, `/api/fixed-income` e `/api/economic-indicators`, com as ordens em `/api/variable-income/{ativo}/orders` e `/api/fixed-income/{id}/buy`. Traz um bot de exemplo completo em Python (`requests` + `python-socketio`) que segue uma das estratégias da F9, e as limitações: o bot fica fora do backtest, e com o tick mais rápido que a reação dele as ordens caem dias depois (números na D5). Rota que faltar ao escrever o exemplo entra nesta feature. Fora da rede local depende da F6. Gatilho: livre; o exemplo fica melhor depois da F9.

<a id="f110"></a>
**F110 — Combinar estratégias.** Serve N4; segue a D8. O jogador liga mais de uma estratégia ao mesmo tempo, cada uma com uma fatia do patrimônio (ex.: 30% em 100% no CDI e 70% no cruzamento de médias). O motor guarda, por jogador, a lista de estratégias com a fatia de cada uma e a origem de cada posição; cada estratégia recebe um contexto restrito à fatia dela (caixa e posições que ela comprou) e só opera dentro dele. A página de Estratégias passa de um interruptor para uma lista de fatias que somam 100%, e o log de ordens ganha o filtro por estratégia. Gatilho: F8 concluída e o uso pedir mais de uma estratégia.

<a id="f111"></a>
**F111 — Crédito para estratégias e bots.** Serve N4 e N33; segue a D8. O contexto da estratégia ganha a dívida, a nota de risco e a oferta do dia, e as ações ganham pegar empréstimo, amortizar e quitar, que chamam o mesmo serviço da tela de Crédito em nome do jogador. Uma estratégia de exemplo alavancada (ex.: rebalanceamento por meta com 20% emprestado) mostra o uso e entra na lista dos bots. O log da estratégia registra cada contratação e pagamento com o motivo. Gatilho: F8 e F94 concluídas.

<a id="f113"></a>
**F113 — Classe de ativo cripto com quantidade fracionária.** Serve N37; segue a D3. Hoje a quantidade é inteira da ordem ao banco (`equity_event.quantity` é `Integer`, e `quantity` é `int` nos DTOs de ordem, de prévia e de evento, no motor e no `max_quantity` da prévia), então um ativo de preço alto como o bitcoin só se compra em unidades inteiras. Plano: (1) **Classe nova:** `CRYPTO` no `AssetClass`, escolhível na tela de importação (que já troca a classe de um ativo) e valendo para `BTC-USD` e afins, que o importador já aceita. (2) **Quantidade decimal:** a coluna vira `NUMERIC(20,8)` por migration (oito casas, a precisão do satoshi) e os DTOs passam a `Decimal`, serializado em string (D3); ação, FII, ETF e BDR continuam aceitando só inteiro, e a validação da ordem recusa fração fora de `CRYPTO`. (3) **Motor:** compra, venda, preço médio, `max_quantity` da prévia (arredondado para baixo nas oito casas) e o impacto de preço passam a operar em `Decimal`. (4) **Imposto:** `income_tax` ganha a categoria cripto, com regra própria a conferir na implementação. (5) **Telas:** o campo de quantidade da ordem aceita vírgula quando o ativo é cripto, e a quantidade da carteira e do histórico exibe as casas necessárias. Gatilho: o uso pedir bitcoin na carteira, ou a F22 e a F100 mexerem em quantidade e proventos, já que convém migrar a coluna uma vez só.

<a id="f118"></a>
**F118 — Lembrar a última configuração da partida.** Serve N30; segue a D9. As regras pendentes moram em memória no `SettingsManager`, que nasce dos padrões do `config.toml` (início em 2000-01-01, por exemplo) a cada abertura do app, então o período, o capital, o aporte e o resto voltam ao padrão toda vez e o host refaz tudo. Plano: o lugar é o banco, porque as regras são do servidor do host (o formulário do lobby é semeado por elas) e o banco embarcado sobrevive entre aberturas. (1) Migration (D9) com uma tabela de uma linha só, `last_simulation_settings`, com a configuração em JSON validada pelo mesmo DTO das regras; (2) o `SettingsManager.update` grava essa linha quando as regras mudam, e o `get` a lê no lugar do `config.toml` quando existe, caindo nos padrões do arquivo se estiver vazia ou se um campo novo faltar; (3) o `config.toml` continua sendo o padrão de fábrica, e uma opção "Restaurar padrões" no formulário apaga a linha. O nome da partida não entra (é gerado a cada uma). A F89 (presets) pode ler a mesma linha como o preset "Última partida". Gatilho: o uso do lobby pedindo para não remontar as regras.
**Aceite:** mudar o início para 2012, fechar e abrir o app, e o formulário abre com 2012.

<a id="f122"></a>
**F122 — Novas conquistas para as features recentes e antigas.** Serve N22; segue a D1. O catálogo tem 22 conquistas, quase todas de antes das últimas features, e várias coisas que o jogo já faz não rendem nada. Acrescentar uma é uma linha em `catalog.py` mais, quando a medida não existe, uma função `@metric` em `metrics.py` (o `code` nunca muda; nome, descrição e ícone podem mudar). Primeira leva, sobre o que já existe: (1) **Dentro da isenção** (IR da venda): fechar um mês vendendo ações sem pagar imposto por ficar abaixo do limite de isenção; (2) **Day trader** (IR): comprar e vender o mesmo ativo no mesmo dia; (3) **Em todo setor** (setores): ter ativos de cinco setores diferentes ao mesmo tempo, com barra de progresso; (4) **Mexeu o mercado** (impacto de preço): uma ordem sua mover o preço do ativo, valendo só em partida com o impacto ligado; (5) **Sem muletas** (modo Especialista): vencer a partida no modo Especialista; (6) **Time vencedor** (equipes): vencer uma partida em equipes; (7) **Além do horizonte** (dados gerados): jogar um dia além do último dia com dado real; (8) **Nota de craque** (nota geral): chegar a uma nota geral alta, com a meta calibrada nas notas das partidas já jogadas; (9) **Ordem com paciência**: ter a primeira ordem limite executada. Vale também uma regra daqui para a frente: cada feature nova que mexe no jogo traz as próprias conquistas no mesmo trabalho (crédito, proventos, bots e estratégias automáticas, por exemplo), em vez de esperar uma leva à parte. Gatilho: qualquer momento; nomes, descrições e ícones se fecham na hora de escrever cada linha.

<a id="f124"></a>
**F124 — Voltar o quadrado da marca no cabeçalho da sala.** Serve N15. No lobby, o `BrandMark` ao lado de "Sala de ..." (`lobby-header.tsx`) virou a rosca de três fatias na troca da marca do app; antes era um quadrado arredondado azul com o ícone de barras crescentes (`ChartNoAxesColumnIncreasing`, traço 2,4). Plano: o `BrandMark` ganha a variante `square`, que traz de volta o quadrado azul (`bg-primary text-primary-foreground`, cantos arredondados e ícone proporcionais a cada tamanho, como era no commit anterior à troca) ao lado da variante `logo`, que continua sendo a rosca e o padrão; só o cabeçalho do lobby usa `square`, e a barra lateral, a tela de carregamento e o login mantêm a rosca. Gatilho: qualquer momento, é um ajuste pequeno.

<a id="f126"></a>
**F126 — Janela "Como jogar".** Serve N25. É o tutorial em si, no molde das Dicas e truques do Factorio; como animar cada tópico é o spike F49, e esta feature não espera por ele. **A janela:** um diálogo quase em tela cheia, com a lista de tópicos à esquerda em dois grupos, "Como se joga" (entrar na sala, comprar uma ação, aplicar em renda fixa, avançar o tempo, ler as estatísticas) e "Conceitos" (alavancagem, médias móveis, nota de risco), e o tópico aberto à direita: título, a ilustração e um texto curto em passos, com "Próximo tópico" no rodapé. A ilustração é o componente real do app com dados de exemplo e sem interação, para seguir o tema e ficar nítida em qualquer tamanho; quando a F49 escolher o jeito de animar, a animação entra no mesmo lugar. Os tópicos moram no front, num registro com id, grupo, título, texto e ilustração, e cada tela declara os tópicos dela. Feature que traz uma explicação longa acrescenta o tópico dela ao registro. **Nunca abre sozinha.** Abre pelo botão "Como jogar" no topo do lobby, ao lado de Conquistas, e por um acesso dentro da partida. **Aviso pelo contexto:** a primeira vez que o jogador abre uma tela com um tópico que ele não viu, aparece um aviso pequeno, que não bloqueia a tela ("Tem um tópico sobre isto: Renda variável", com "Ver" e "Agora não"); cada tópico avisa uma vez só. Na lista, tópico não visto leva um ponto, e o botão mostra quantos faltam. O navegador guarda o que foi visto e o que já avisou. Para não disputar com as Novidades (F56), que também se destacam no lobby, o lobby nunca destaca as duas ao mesmo tempo: depois de uma atualização, quem se destaca são as Novidades. **Tempo:** com um só jogador humano na sala (bots não contam), abrir a janela pausa a partida e fechar retoma; com mais gente, o tempo segue e a janela avisa isso no cabeçalho. **Sai do canvas antes de implementar:** o lugar do acesso dentro da partida (aba flutuante na borda direita, item no menu lateral ou botão na topbar) e se a dica de um termo leva ao tópico dele.

<a id="f127"></a>
**F127 — Estratégias e bots operam cripto em fração.** Serve N4 e N37. Com a classe de cripto e a quantidade fracionária no ar, as estratégias seguem comprando só unidades inteiras (`int(caixa // preço)`), então um bot só compra bitcoin se o caixa pagar 1 unidade inteira. Plano: o contexto da estratégia passa a conhecer a classe do ativo, e as estratégias (comprar e segurar, rebalanceamento, momentum, RSI, médias móveis, rompimento) arredondam a quantidade em oito casas para cripto e em inteiro para as demais; `whole_shares` ganha a variante fracionária. Gatilho: a F113 concluída e o uso pedir bot com bitcoin.

<a id="f119"></a>
**F119 — Seletor de período da partida com linha do tempo.** Serve N15 e N30. O início e o fim da partida saíram dos dois `DateField` soltos para um bloco "Período" no `rules-sheet.tsx`: a duração no cabeçalho ("6 anos e 7 meses"), atalhos em dois grupos ("Até hoje": 5 anos, 10 anos, 20 anos e Tudo; "Pra frente": 5 anos e 10 anos), uma linha do tempo de 1993 a 2040 pintada pelo dado que a base tem (sem dado, dado real, futuro gerado e repete o último valor) com o marcador de hoje, duas alças e uma barra que move o período inteiro mantendo a duração, e os campos Início e Fim com o botão "Hoje" e o calendário com "Hoje", o dia de hoje em destaque e o futuro em violeta. A escolha vale na hora, sem botão de aplicar; alças e barra andam em meses inteiros (início no dia 1, fim no último dia do mês) e param no primeiro dia com dado e em 31/12/2040, com um aviso na linha. Atalho que começaria antes do primeiro dia com dado de um indicador fica desligado com o motivo. O aviso de cobertura (`CoverageAlerts`) continua abaixo, e a data digitada mantém o aviso. A matemática mora em `lobby/lib/period.ts`, com testes.

<a id="f121"></a>
**F121 — Comprar tudo a mercado sem estourar o caixa.** Serve N15; segue a D3. A boleta de renda variável calcula o "Máx" com o caixa e o preço da prévia (`preview_order`: o melhor preço de venda do book, ou o último fechamento), mas a ordem a mercado só é conferida na execução, contra o preço do momento (`_validate_market_order` em `broker.py`). Com o jogo rodando, o preço anda entre o clique e a execução, e a quantidade que cabia na prévia volta como "Saldo insuficiente". Plano: (1) **Ordem a mercado por valor:** a boleta ganha o modo "por valor" e o botão "Tudo" (o caixa inteiro); o DTO da ordem aceita `amount` (Decimal em string) no lugar da quantidade, e o motor calcula a quantidade na execução com o preço que valeu, arredondando para baixo (inteiro, e oito casas para cripto); nunca estoura. (2) **Quantidade que se ajusta:** na compra a mercado por quantidade, o valor enviado vale como teto: se o preço subiu até a execução, o motor compra a maior quantidade que ainda cabe no caixa em vez de recusar, e só recusa se nem uma unidade couber. (3) A boleta mostra a quantidade como estimada antes do envio, e a executada no retorno e no histórico. O desenho do modo "por valor" e de como a boleta mostra a quantidade comprada sai do canvas antes do código. Gatilho: livre.
**Aceite:** com o preço subindo 5% entre o clique em "Tudo" e a execução, a compra executa sem "Saldo insuficiente" e deixa no caixa menos que o preço de uma unidade.

<a id="f87"></a>
**F87 — Erros de dado do yfinance na base.** Serve N3. A base tem dias em que o preço vai a quase zero e volta: CMIG4 sobe 878% e cai 90% em agosto de 2003, XPML11 cai 99% em 14/01/2026 e volta 758 vezes cinco dias depois, e UGPA3, GOAU4, LREN3 e SUZB3 têm dias de −100%. A partida mostra esses dias como reais. O gerador (D14) já os trata como dia sem pregão. Escolhido: interpolar. Plano: (1) **Detector** no importador (`import_data/importer_service.py`): um dia é erro quando o fechamento se afasta do pregão anterior além de um limiar e, em poucos pregões, o preço volta ao nível anterior; salto que não volta (B3SA3 −66% em 2011) não é tocado, porque pode ser desdobramento, assunto da F22. (2) **Correção:** o fechamento do dia erro vira a interpolação linear entre o último pregão bom e o primeiro bom depois; abertura, máxima e mínima recebem o mesmo valor e o volume fica zerado, para o dia não desenhar uma vela falsa. (3) **Limiar por medição:** antes de fixar, uma varredura da base lista os dias candidatos em limiares de 30%, 50% e 70%; o limiar escolhido pega os casos acima e não pega B3SA3. (4) **Base já importada:** uma ação na Central de dados reaplica a correção às linhas guardadas, e o importador a aplica daí em diante; a Central mostra quantos dias foram corrigidos por ativo. Teste: série curta com um dia a quase zero que volta é corrigida, e série com degrau que não volta fica igual. O preço do dia corrigido é inventado, e a troca é essa: o erro deixa de aparecer na partida como se fosse mercado.

<a id="f22"></a>
**F22 — Preço ajustado e proventos.** Serve N3 e N7; segue a D1, a D3 e a D7. O importador usa `yf.download(auto_adjust=True)`: o preço vem ajustado por dividendos e desdobramentos até o dia da importação, e a atualização incremental (`upsert_dataframe` só grava linhas depois da última data guardada) emenda duas séries ajustadas em dias diferentes. Um desdobramento 2:1 entre a importação e a atualização vira um degrau falso, uma queda de 50% que não existiu; além disso, o preço exibido não é o que se negociava na época. Escolhido: preço bruto mais proventos como evento. Plano: (1) **Importação:** `auto_adjust=False` guarda o fechamento bruto, e as listas de dividendos e de desdobramentos que o `yfinance` traz entram numa tabela de eventos corporativos por ativo (data ex, tipo, valor ou razão), por migration. A série bruta não muda quando sai um provento novo, então a atualização incremental passa a emendar séries do mesmo tipo e o degrau some. (2) **Desdobramento e grupamento:** na data ex, a quantidade de cada posição é multiplicada pela razão e o preço médio dividido por ela, como evento da partida reconstruível (D1), com a quantidade em Decimal (D3). (3) **Dividendo:** na data ex, o valor por cota vezes a quantidade entra no caixa, como evento; sem esse crédito o retorno de quem paga dividendo cairia, porque o preço bruto cai na data ex e o ajuste que antes embutia o provento deixa de existir. Telas, rendimento por posição, IR e provento sintético ficam na F100. (4) **Números que mudam:** o retorno e a nota geral (D10) mudam de valor, então os testes de números fixos são regerados e conferidos contra uma conta à mão antes de aceitar. (5) **Partidas salvas:** jogaram sobre o preço ajustado; o primeiro passo é verificar se o congelamento por versão da D7 (hoje usado só para trecho gerado) cobre também o trecho real, ou se as partidas salvas são recalculadas. Gatilho: livre; a F100 espera esta.
**Aceite:** num desdobramento 2:1 ocorrido depois da importação, a atualização incremental não produz queda de 50% no preço, e a posição de quem tinha o ativo dobra de quantidade sem mudar de valor.

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F60** | Modo servidor dedicado (--headless) | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F67** | Abrir a pasta de configurações | — | — | — | Baixo | Baixo | Médio | Excelente | ⏳ Pendente |
| **F68** | Dica de firewall no lobby | — | — | — | Baixo | Baixo | Médio | Ótimo | ⏳ Pendente |
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
| **F28** | Muitos futuros (Monte Carlo) | Serve N10; revisa ou confirma a D7 | M9 | [F19](#f19) | 🔍 Em avaliação |
| **F34** | Gráfico de ações em tela cheia, com ferramentas de trader | Serve N19; escolhe a biblioteca de gráfico | M11 | [F33](#f33) | 🔍 Em avaliação |
| **F44** | Expansão Gestoras: fundar a gestora e abrir capital | Serve N23; falta o protótipo do preço da cota com o formador sintético | — | [F101](#f101) | 🔍 Em avaliação |
| **F49** | Spike: animação dos tópicos do tutorial | Serve N25; decide como os tópicos da F126 se animam: vídeo, framer-motion ou Remotion | M14 | — | 🔍 Em avaliação |
| **F55** | Modo aquisição hostil | Serve N23; faltam parte mínima no mercado e o destino do incorporado | — | [F103](#f103) | 🔍 Em avaliação |
| **F90** | Cenários | Serve N22; um preset com objetivo | — | [F89](#f89) | 🔍 Em avaliação |
| **F93** | Rumores antecipados | N31; opção da partida | M15 | [F92](#f92) | 🔍 Em avaliação |
| **F95** | Expansão Governo: partidos, eleição e impostos | Serve N34, N23; o gasto público é a F106 e os perfis de público são a F107 | — | — | 🔍 Em avaliação |
| **F97** | SELIC nas mãos do governo | N34; opção da expansão Governo | — | [F106](#f106) | 🔍 Em avaliação |
| **F100** | Proventos na carteira e nas telas | Fecha o que a F22 deixa em aberto (dividendo nunca entra no caixa); destrava os rendimentos da gestora (F105) | M8 | [F22](#f22) | 🔍 Em avaliação |
| **F102** | Gestoras: emissão de novas cotas e recompra | Serve N23; falta o prazo da preferência e o preço da emissão | — | [F44](#f44) | 🔍 Em avaliação |
| **F103** | Gestoras: troca de gestor pela assembleia | Serve N23; falta como a assembleia escolhe o novo gestor | — | [F44](#f44) | 🔍 Em avaliação |
| **F104** | Gestoras: co-gestores | Serve N23; falta a divisão das taxas | — | [F44](#f44) | 🔍 Em avaliação |
| **F105** | Gestoras: rendimentos mensais | Serve N23; falta a parte do lucro distribuída | — | [F44](#f44), [F100](#f100) | 🔍 Em avaliação |
| **F106** | Governo: gasto público e inflação | Serve N34; falta quanto cada medida soma ao IPCA | — | [F95](#f95) | 🔍 Em avaliação |
| **F107** | Perfis de público na eleição | Serve N34; eleitores com perfil sobre a eleição da F95 | — | [F95](#f95) | 🔍 Em avaliação |
| **F120** | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | Serve N15; falta escolher o desenho dos dois cards no canvas; liga à F72 | — | — | 🔍 Em avaliação |
| **F123** | Redesenhar o aviso de conquista desbloqueada | Serve N22 e N15; falta escolher o desenho do aviso no canvas; liga à F122 | — | — | 🔍 Em avaliação |
| **F125** | Revisão das regras de lint e da checagem de tipos | Nenhuma N#; qualidade do código. A configuração do oxlint é da D15 | — | — | 🔍 Em avaliação |

<a id="f5"></a>
**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO; se não passar, se ao menos o polling atravessa (o SSE saiu na D13, então o polling é o único fallback). O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

<a id="f28"></a>
**F28 — Muitos futuros (Monte Carlo).** Serve N10. Em vez de testar a estratégia num futuro gerado só, testá-la em muitos (ex.: 100, cada um com uma semente) e mostrar o resultado como distribuição: "perdeu para o CDI em 23 de 100 futuros; no pior, −35%; no do meio, +40% em 5 anos". Lê-se pela fração de futuros ruins e pelo pior caso: poucos futuros perdendo para o CDI é bom; uma estratégia que só ganha no histórico real e perde na maioria dos futuros plausíveis teve sorte, não mérito. É o backtest da F19 repetido sobre gerações do gerador da D14. Falta definir: **onde vivem os 100 futuros.** A D7 dá às tabelas de série uma dimensão de versão, que a F24 implementa para congelar partidas salvas. Opções: (1) cada futuro de Monte Carlo é uma versão descartável nessa dimensão, gravando 100 vezes as linhas geradas (cerca de 5 milhões para 37 ativos × 5 anos); (2) o motor lê as séries por um provedor que pode ser o banco ou uma geração em memória (o `SeriesGenerator` gera 37 ativos × 5 anos em cerca de 1 s), o que estende a D7 de "mesmas tabelas" para "mesma interface". Sai daqui com essa escolha, que revisa ou confirma a D7.

<a id="f34"></a>
**F34 — Gráfico de ações em tela cheia, com ferramentas de trader.** Serve N19; segue a D2. Um botão no card "Histórico de Preços" abre o gráfico em tela cheia, com os indicadores da F33 e o que uma plataforma de trader oferece: barra de ferramentas de desenho (linha de tendência, linha horizontal de suporte e resistência, canal, retângulo, retração de Fibonacci, texto), régua que mede variação % e pregões entre dois pontos, escala logarítmica, legenda com abertura, máxima, mínima, fechamento e volume do candle sob o cursor, comparação com outro ticker ou com o Ibovespa em %, e uma boleta compacta para comprar e vender sem sair da tela. Os desenhos ficam salvos por jogador e ticker numa tabela nova (`chart_drawings`, com os pontos em JSON), entrando por migration (D9). Falta escolher a biblioteca: (1) continuar no `lightweight-charts` e escrever as ferramentas de desenho como plugins (a API de primitives da versão 5; os exemplos oficiais trazem linha de tendência e retângulo); (2) trocar pelo KLineChart (Apache 2.0), que já vem com cerca de 15 ferramentas de desenho, mas calcula indicadores no navegador, e pela D2 eles viriam do backend como indicador customizado; (3) o Advanced Charts da TradingView tem tudo pronto, mas a licença pede cadastro e não permite publicar a biblioteca em repositório público, o que o deixa fora deste projeto. Sai daqui com um protótipo de linha de tendência e Fibonacci nas opções 1 e 2, e a escolha.

<a id="f44"></a>
**F44 — Expansão "Gestoras": fundar a gestora e abrir capital.** Serve N23. Inspiração: o Capitalism Lab (oferta pública, emissão de novas ações, recompra, compra de ações dos concorrentes), o OpenTTD e o Software Inc. Lá cada jogador é uma empresa que fabrica ou transporta; aqui tudo é finanças, então a empresa de cada jogador é uma gestora, e o que ela vende é o próprio desempenho. **Como expansão:** ligável por partida numa **aba própria "Expansões"** no lobby, com banner, emblema e "o que muda", como a loja de DLC dos jogos da Paradox; é enfeite visual, o sistema é o mesmo ligado ou não. **A gestora** tem nome e ticker de 4 letras mais 11, como cota de FII na B3 (o servidor recusa letras que já existam entre os ativos importados), e no livro de ofertas a linha leva a cor e a sigla do jogador, para não se confundir com ativo real. O jogador a funda levando **caixa, ações e títulos** da carteira em troca de cotas, e a opera por um **modo na topbar** ("Operando: Aurora Gestão"), que troca a conta de todas as telas de mercado, com uma faixa verde-petróleo e o caixa da gestora dizendo qual conta está ativa. **É um fundo fechado listado, como um FII:** (1) **oferta pública** quando o gestor quiser — cotas novas ao preço do patrimônio por cota (patrimônio de R$ 100 mil em 1.000 cotas dá R$ 100), e o dinheiro de quem compra entra na gestora: é investir no amigo; (2) **mercado** — depois da oferta, as cotas são negociadas no livro de ofertas que a renda variável já tem, e o preço sai da oferta e da procura, acima do patrimônio por cota (ágio) quando a sala acredita no gestor e abaixo (deságio) quando não; (3) **liquidez** — a liquidez de fundo do livro nasce dos candles de cada ativo, e a cota não tem candle, então um formador de mercado sintético põe ordens de compra e venda em volta do patrimônio por cota, numa faixa de 20% para cima e para baixo recalculada todo dia; dentro da faixa, o preço sai dos jogadores, e o livro tem contraparte até numa sala de 2; (4) **taxas** — a gestora paga aos gestores taxa de administração todo mês sobre o patrimônio e taxa de performance a cada 6 meses sobre o que passar do CDI, com teto na partida de **2% ao ano de administração e 20% de performance**, e cada gestor escolhe até o teto. A performance respeita a **marca d'água**, o maior patrimônio por cota sobre o qual a taxa já foi cobrada: se a cota cai de R$ 100 para 80 e volta a 100, a recuperação não paga performance. **O lucro fica dentro da gestora** e valoriza a cota. **Por que abrir capital, e quando:** as taxas são sobre o dinheiro dos outros, e com ágio as cotas do próprio gestor valem mais no ranking; o custo é ficar exposto, porque vender mais da metade abre a porta para perder o controle (F103). Abrir cedo, sem histórico, tende a sair com pouca procura; abrir depois de um bom ano tende a sair com ágio. **O gestor e a própria gestora:** o gestor negocia com a gestora pelo livro como qualquer jogador; a linha leva a sigla dele, então a negociação fica à vista, e quem cobra é a sala, vendendo a cota (deságio) ou trocando o gestor (F103). **Regras para o cálculo fechar:** só pessoas compram cotas, nunca gestoras, o que impede a participação cruzada (A com cotas da B, que tem cotas da A). No ranking, cada jogador soma a carteira pessoal, as taxas recebidas e as cotas que tem pelo **preço de ranking**: a média dos negócios dos últimos 20 pregões, ponderada pelo volume e limitada a 30% acima ou abaixo do patrimônio por cota; sem negócio no período, vale o patrimônio por cota. Um ágio de até 30% conta, e um negócio forçado a R$ 1.000 numa cota de R$ 100 conta no máximo como R$ 130. A carteira da gestora só conta através das cotas, sem contar o mesmo dinheiro duas vezes. **Estrutura:** a carteira própria da gestora é a F101; a cota é um ativo no livro de ofertas, com o patrimônio por cota publicado a cada dia. **Nas features seguintes:** emissão de novas cotas e recompra (F102), troca de gestor pela assembleia (F103), co-gestores (F104) e rendimentos mensais (F105). Falta: um protótipo do preço da cota no livro, com o formador sintético e jogadores comprando e vendendo, para calibrar a faixa de 20%.

<a id="f49"></a>
**F49 — Spike: animação dos tópicos do tutorial.** Serve N25. Decide como os tópicos da janela "Como jogar" (F126) se animam quando o movimento é o que explica; a janela, a lista de tópicos e a ilustração estática são da F126. O spike faz o mesmo tópico — comprar uma ação — dos três jeitos e compara: (1) **vídeo gravado pelo Playwright**, o mesmo da F47; mais barato e sempre fiel ao app, mas não acompanha o tema escuro nem fica nítido em qualquer tamanho; (2) **animação em código com o `framer-motion`**, que o projeto já tem — os componentes reais com dados de exemplo e um cursor roteirizado; nítido e segue o tema, mas cada tópico é código; (3) **Remotion**, que escreve vídeo em React e tem skills oficiais para agentes de código (`npx remotion skills add`); junta a precisão do código com a saída em vídeo, ao custo de uma ferramenta a mais (a licença é gratuita para uso individual). Critérios: fidelidade ao que o usuário imaginou, nitidez, custo de manter quando a tela muda, e tamanho no executável. O tema escuro (F37) está sem prioridade, então não seguir o tema pesa pouco hoje. Entrada: o roteiro desse tópico (o que aparece, o que se mexe, quanto dura, o texto), desenhado no canvas junto da F126. Sai daqui com o jeito escolhido e o plano de animação dos tópicos restantes.

<a id="f55"></a>
**F55 — Modo aquisição hostil.** Serve N23. Um modo de jogo da expansão "Gestoras" (F44) em que perder o controle tira o jogador da partida. Todo o patrimônio de cada jogador está na própria gestora, e quem juntar mais da metade das cotas de outra a incorpora: o dono anterior sai da partida e a gestora dele passa a ser controlada pelo comprador. Vence quem sobrar, ou quem tiver o maior patrimônio na data final. **Carência:** nos primeiros meses (padrão 12) ninguém pode passar de metade de outra gestora, para que abrir capital cedo não seja suicídio. **Ninguém fica invulnerável:** sem oferta pública, a gestora seria impossível de comprar, então no fim da carência todas precisam ter uma parte mínima das cotas no mercado (padrão 50%); quem não abriu capital entra numa oferta automática pelo patrimônio por cota. **Defesa:** recompra de cotas com o caixa da gestora e compra com as taxas recebidas, como uma empresa que recompra ações para não ser comprada. Falta decidir: a parte mínima no mercado; se o incorporado sai da partida ou vira co-gestor do comprador (como numa fusão); e se há um preço mínimo por cota durante a tentativa de aquisição, como nas ofertas públicas de aquisição reais.

<a id="f90"></a>
**F90 — Cenários.** Serve N22. Como nos jogos de estratégia: uma partida montada com intenção, um preset (F89) com objetivo e texto de abertura. Exemplos: "Crise de 2008" (começa em setembro de 2008 com R$ 100 mil, meta de não perder mais de 20%), "Década perdida" (futuro gerado com choque de inflação de +15 pontos) e "Plano Real". O objetivo usa os modos de jogo que já existem (corrida à meta, viver de renda) e o ranking. Falta definir: quais cenários entram primeiro e o objetivo de cada um; se o objetivo pode ser algo que os modos não cobrem (perda máxima, bater o CDI); se há campanha, com um cenário liberando o seguinte; e se o usuário cria os próprios cenários ou só joga os que vêm com o app.

<a id="f93"></a>
**F93 — Rumores antecipados.** Ligado à N31; uma opção da partida, desligada por padrão. O simulador já sabe o futuro: as séries até a data final estão no banco antes de a partida começar, sejam reais ou geradas. O rumor usa isso e chega antes do fato, ao contrário do noticiário (F92): dias antes de um movimento grande (queda forte de um setor, mudança da SELIC), aparece na caixa de entrada algo como "analistas veem risco no varejo". O valor do rumor é obrigar o jogador a pensar: pode acontecer ou não, e a frase pede interpretação. Por isso só uma parte dos rumores se confirma, outra parte é alarme falso sorteado onde nada vai acontecer, e alguns não dizem a direção ("mudanças na diretoria da X"). Falta definir: a taxa de acerto e a antecedência; quão vago o rumor é (setor ou ativo, com ou sem direção); se é da sala inteira ou informação de um jogador só (comprada, como um informante); e se vale no modo Especialista.

<a id="f95"></a>
**F95 — Expansão "Governo": partidos, eleição e impostos.** Ligado à N34 e à N23. Mesmo molde da expansão "Gestoras" (F44): ligável por partida na aba "Expansões" do lobby, com nome, emblema e card próprios. Inspiração: a expansão de cidades do Capitalism Lab, em que o empresário funda um partido e disputa a prefeitura. Só liga em partida de pelo menos 5 anos, o tempo de uma campanha e um mandato. O card da aba Expansões traz duas opções: **qual ranking decide** a partida (o individual ou o de partidos) e a **dificuldade do computador** (fácil, médio ou difícil). (1) **Partidos:** só se concorre por partido; quem quer concorrer sozinho funda um partido de um filiado. O partido tem nome, sigla e cor (como o emblema da gestora, para não se confundir com jogador) e um **fundador**, que escolhe o candidato e o vice entre os filiados; o vice convidado aceita ou recusa. Cada filiado escolhe a **contribuição mensal** (pode ser zero), que sai do caixa dele e não volta, e a **verba de campanha** do partido é a soma das contribuições; a promessa da régua é a do partido. O jogador fica em um partido por vez; sair é livre e a contribuição para na hora; se quem sai é o candidato ou o vice, a vaga abre e o fundador indica outro filiado. O fundador pode **expulsar** um filiado, e a expulsão sai no feed da partida. Os candidatos do computador vêm de partidos do computador, com sigla e cor (cinza e tracejado nas telas). (2) **Rankings:** o ranking individual e o **ranking de partidos** aparecem lado a lado; o patrimônio do partido é a soma dos patrimônios dos filiados, e a opção do card diz qual dos dois decide a partida. O ganho de governar chega a cada um só pela própria carteira (imposto menor no que ele tem, setor isento que ele carrega), sem caixa do partido para repartir. (3) **Eleição:** a candidatura abre um ano antes. Concorrem os partidos de jogadores que inscrevem chapa e partidos do computador, que **só completam as vagas** quando há menos de 3 chapas. A verba vira apoio aos poucos e com retorno decrescente (dobrar a verba não dobra o voto), e por isso começar cedo pesa. Verba, contribuições e promessa são **públicas**, e o que cada filiado contribui **sai do patrimônio** dele no ranking. Uma pesquisa de intenção de voto mostra a corrida num gráfico ao longo dos meses, com a cor e a sigla de cada partido. Se ninguém passar de 50%, há **segundo turno 3 semanas depois** (1º turno em 7 de outubro, 2º em 28): os eleitores de quem ficou de fora vão para o finalista com a promessa mais parecida na régua. Entre os turnos, um jogador de partido eliminado pode **doar verba a um finalista**, a favor ou contra quem lidera; a doação é pública e sai do patrimônio dele. **Computador:** a verba mensal dele é 0,5, 1 ou 1,5 vez a média dos jogadores (fácil, médio ou difícil), e a promessa dele vai para a faixa mais vazia da régua. Mandato de 4 anos, com uma reeleição. (4) **Impostos por setor:** o governo mexe nos impostos que o jogo já cobra (os 15% e 20% da renda variável, a isenção de vendas de ações até R$ 20 mil, a tabela regressiva da renda fixa, a isenção de LCI e LCA) e pode taxar ou isentar um setor ou segmento, que todo ativo já tem: "isentar o IR de energia", "taxar bancos em mais 5 pontos". Imposto vale em qualquer período, porque não mexe em preço. (5) **Ritmo das medidas:** o presidente propõe a qualquer momento e a medida entra numa **fila do Congresso, pública desde a proposta**, sem pausar a partida. O Congresso vota a fila no fechamento do mês, com chance de passar igual à aprovação do governo (40% de aprovação, 40% de chance); o presidente pode retirar uma medida antes do voto, e a rejeitada pode voltar à fila. A aprovada só vale **90 dias depois**, como a noventena, para os outros terem tempo de reagir. (6) **Aprovação:** uma métrica sempre à vista, com o histórico num gráfico, que começa em 50% na posse e se move pelos fatores: inflação na meta soma 4 pontos e cada ponto de inflação acima da meta tira 3; a bolsa nos últimos 12 meses soma ou tira 1 ponto a cada 5% de alta ou queda (até 6 pontos); imposto novo tira de 1 a 5 pontos quando passa a valer, efeito que some em 6 meses; corte de imposto soma de 1 a 3; e a promessa descumprida tira 3 pontos por faixa de distância na régua. **Régua de 1 a 5:** corte geral de imposto é 1, isenção setorial 2, taxar um setor 4 e imposto geral novo 5 (o gasto público da F106 fica entre 4 e 5); a marca do governo é a média das medidas aprovadas, e a distância dela até a promessa da campanha é a que pesa. Aprovação baixa perde a reeleição e, abaixo de um piso por meses seguidos, leva a **impeachment**: assume o **vice**; sem vice, um governo neutro do computador, sem medidas novas, até a próxima eleição. No impeachment, a medida já aprovada segue os 90 dias, a fila não votada some e a carteira de quem saiu volta a operar. (7) **O presidente e a própria carteira:** ele **vence pelo patrimônio**, como todos, e tem a **carteira congelada**: não compra nem vende enquanto governa, porque sabe da medida antes de todos. Governar a favor da carteira congelada é o jeito de ele ganhar governando, e faz parte do jogo: quem vai assumir monta a carteira antes da posse, por isso a carteira congelada do presidente é pública, para a sala ler o interesse dele e se posicionar contra ou junto. Com a expansão Gestoras ligada, na posse ele deixa de operar a gestora e de receber taxas; um co-gestor (F104) assume, e sem co-gestor a gestora congela até o fim do mandato; as cotas que ele tem continuam dele. (8) **SELIC:** o Banco Central segue autônomo, como no Brasil desde 2021, e a SELIC reage à inflação como no gerador; a opção de pô-la nas mãos do governo é a F97. **Nas features seguintes:** o gasto público e a inflação, o efeito das medidas por cima das séries (F106), e os perfis de público na eleição (F107). Falta definir: o piso de aprovação e quantos meses abaixo dele levam ao impeachment, e a curva que transforma verba em apoio.

<a id="f97"></a>
**F97 — SELIC nas mãos do governo.** Ligado à N34; uma opção da expansão "Governo" (F95), no lugar do Banco Central autônomo. (1) **Ritmo do Copom:** o governo decide a SELIC em reuniões a cada 45 dias, como o Copom, que se reúne 8 vezes por ano desde 2006; entre reuniões ela não muda. (2) **Teto por reunião, pelo que aconteceu de verdade.** Das 150 mudanças da meta da SELIC entre 2000 e outubro de 2026 (série do Banco Central): 34 foram de 0,25 ponto, 67 de 0,5, 19 de 0,75, 19 de 1, 7 de 1,5, uma de 2, uma de 2,5 (cortes de 2003) e duas de 3 (as altas da crise de 2002); desde 2006, nunca passou de 1,5. O teto acompanha isso: até 0,75 ponto por reunião em tempo normal (80% das mudanças reais), 1,5 com a inflação bem acima da meta, como em 2021 e 2022, e 3 só com a inflação explodindo, como em 2002. (3) **O preço de cada lado:** a SELIC abaixo do que o Banco Central autônomo faria (a da série, ou a do gerador) faz a inflação subir com alguns meses de atraso, pelo mesmo mecanismo de efeito por cima das séries da F106, e inflação alta derruba a aprovação; a SELIC alta demais derruba a bolsa pelo coeficiente da D14, o que também pesa na aprovação. Falta definir: quanto a inflação reage à SELIC e com quanto atraso (medir no histórico, como a D14 mediu a reação da SELIC à inflação), e os limites de inflação que liberam cada degrau do teto.

<a id="f100"></a>
**F100 — Proventos na carteira e nas telas.** Ligado à F22 e à F44. Hoje o conceito de provento não existe no jogo: o preço vem ajustado por dividendos, o dinheiro nunca entra no caixa e nem os FIIs importados pagam rendimento mensal. Esta feature cria o provento como evento da partida: (1) **a fonte** é a que a F22 escolher; o `yfinance` traz a lista de dividendos de cada ativo, e é daí que saem os proventos reais; onde a API não trouxer (ativo gerado, ou sem histórico), eles são **gerados sinteticamente** com um rendimento coerente com o ativo (por exemplo, o dividend yield médio do setor), sorteado pela semente da partida, para todos receberem os mesmos nos mesmos dias; (2) **o crédito** entra no caixa na data ex (ou na de pagamento, a decidir) e vira evento reconstruível, como as ordens; (3) **as telas**: a carteira ganha o total de proventos recebidos e o rendimento (yield) de cada posição, o detalhe do ativo ganha o histórico de proventos, e as estatísticas e o fechamento da partida contam o que entrou; (4) **IR**: a tributação de provento (isenção de dividendo e de FII para pessoa física) segue a regra do mercado brasileiro. Destrava os rendimentos mensais da gestora (F105), que só distribui como um FII depois desta. Falta decidir: data ex ou de pagamento; se o provento reinveste sozinho; e como o yield sintético é calibrado.

<a id="f102"></a>
**F102 — Gestoras: emissão de novas cotas e recompra.** Serve N23; amplia a expansão Gestoras (F44). (1) **Emissão:** depois da oferta pública, o gestor emite cotas novas com preferência para quem já é cotista, na proporção das cotas de cada um, para ninguém ser diluído sem escolher; o dinheiro entra na gestora. (2) **Recompra:** a gestora compra as próprias cotas no livro com o caixa dela; vale quando a cota está com deságio (pagar R$ 80 por R$ 100 de patrimônio valoriza a cota de quem fica) e é a defesa contra a troca de gestor (F103). Falta decidir: quanto tempo dura a preferência, e se o preço da emissão é o patrimônio por cota ou o preço de mercado (com ágio, emitir a mercado traz mais dinheiro por cota).

<a id="f103"></a>
**F103 — Gestoras: troca de gestor pela assembleia.** Serve N23; amplia a expansão Gestoras (F44). Quem juntar mais da metade das cotas troca o gestor pela assembleia de cotistas e passa a operar a carteira e a receber as taxas. É o custo de abrir capital, e a defesa é a recompra (F102) e comprar cotas com as taxas recebidas. O modo aquisição hostil (F55) se apoia nesta regra. Falta decidir: se a troca é automática ao passar de metade ou uma votação convocada; se o novo gestor é sempre quem juntou as cotas ou alguém que ele indica; e o que o gestor afastado mantém além das próprias cotas.

<a id="f104"></a>
**F104 — Gestoras: co-gestores.** Serve N23; amplia a expansão Gestoras (F44). A gestora pode ter mais de um gestor, por convite: eles operam a mesma carteira pelo modo na topbar e dividem as taxas, como sócios da mesma empresa. Com a expansão Governo, o co-gestor é quem assume a gestora quando o gestor vira presidente (F95). Falta decidir: como as taxas se dividem (em partes iguais ou pelas cotas de cada um) e quem convida ou tira um co-gestor.

<a id="f105"></a>
**F105 — Gestoras: rendimentos mensais.** Serve N23; amplia a expansão Gestoras (F44) e espera os proventos (F100), porque hoje nem os FIIs importados pagam rendimento. Como um FII, a gestora distribui todo mês parte do lucro aos cotistas, em dinheiro no caixa de cada um, e a cota deixa de render só por valorização. Falta decidir: a parte do lucro distribuída (os FIIs reais distribuem pelo menos 95% do lucro do semestre), se ela é fixa ou escolha do gestor, e o que conta como lucro (só o realizado ou também a valorização da carteira).

<a id="f106"></a>
**F106 — Governo: gasto público e inflação.** Ligado à N34; amplia a expansão Governo (F95) com a segunda alavanca, o gasto público, que mexe na economia em vez de só nos impostos. A medida vira um efeito por cima das séries, do mesmo jeito que o impacto de preço de ordens grandes: o preço do dia é o da série vezes (1 + a soma dos efeitos ativos), cada efeito nasce de um evento, vale cheio no começo e decai com o tempo, e tudo se reconstrói a partir dos eventos numa retomada. Aqui o efeito soma pontos ao IPCA, e o resto segue os coeficientes que a D14 já mediu: a SELIC reage com 1,5 vez a inflação (com o Banco Central autônomo) e a bolsa cai 2,9% no trimestre por ponto de alta da SELIC, ativo a ativo pelo beta. A série guardada não muda, e por isso vale também na história real. Gastar puxa a régua da campanha para "gasto alto", e a inflação que vem dele derruba a aprovação. Falta definir: quantos pontos de IPCA cada medida de gasto soma, com quanto atraso e em quanto tempo o efeito decai; e se, na história real, a SELIC da série também ganha o efeito, para reagir à inflação somada.

<a id="f107"></a>
**F107 — Perfis de público na eleição.** Ligado à N34; amplia a eleição da expansão Governo (F95). Em vez de um eleitorado único, a eleição ganha eleitores artificiais agrupados em perfis (por exemplo, quem vive de renda, quem empreende, quem depende de serviço público), cada um com a própria posição na régua de promessa e a própria sensibilidade à verba. A transferência de votos do segundo turno deixa de ser "vai inteiro para o finalista com a promessa mais parecida" e passa a ser perfil a perfil, pela distância entre a promessa de cada finalista e a posição daquele perfil, e a pesquisa de intenção de voto pode mostrar o voto por perfil. Falta definir: quais perfis existem e quanto cada um pesa no eleitorado, se o peso muda com a economia da partida (desemprego, inflação), e se a aprovação do governo também passa a ser medida por perfil.

<a id="f120"></a>
**F120 — Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira.** O que incomoda: o tooltip do donut (`allocation-donut.tsx`, um `Tooltip` do Recharts com estilo avulso) não agrada; o estilo do gráfico de evolução (`networth-chart.tsx`: áreas empilhadas por classe, linha tracejada do aportado, rótulos de fim à direita) parece estranho; e outros lugares usam um gráfico parecido (a área de composição das Estatísticas e a linha de desempenho). Falta escolher o desenho dos dois cards: que tipo de gráfico mostra a evolução (áreas empilhadas, uma linha de patrimônio contra o aportado, ou o patrimônio com o ganho destacado), o que o donut conta e como o tooltip responde, e se os dois cards continuam lado a lado. Parte de uma rodada no canvas, com variantes dos dois cards e do estado vazio e com poucos pontos. Ao aprovar, o visual vale para os gráficos parecidos, e a F72 (convenção de pasta e `ChartContainer`) é o lugar de migrá-los. Sai daqui para Pendente com a variante escolhida.

<a id="f123"></a>
**F123 — Redesenhar o aviso de conquista desbloqueada.** Hoje o aviso (`achievement-toast.tsx`, aberto com `toast.custom` do sonner) é um cartão escuro de 380 px com uma faixa amarela de 3 px à esquerda, o ícone, o rótulo amarelo em maiúsculas ("Conquista desbloqueada"), o nome e a descrição; quando várias saem no mesmo dia, vira uma lista com "Ver todas". O incômodo existe, mas não está claro de onde vem: pode ser a faixa amarela do canto, o rótulo, o peso do cartão escuro, o tamanho ou a falta de movimento. Falta escolher o desenho depois de ver variantes lado a lado no canvas: (a) o cartão atual sem a faixa, com o ícone em destaque; (b) um cartão claro, no tema do app; (c) um formato compacto, com o ícone e o nome numa linha só e a descrição ao passar o mouse; (d) um formato de "selo" com a categoria e a cor dela. A rodada cobre os estados uma conquista, várias no mesmo dia, secreta revelada e conquista com barra de progresso completa, e decide a posição na tela e a entrada e saída. Sai daqui para Pendente com a variante escolhida.

<a id="f125"></a>
**F125 — Revisão das regras de lint e da checagem de tipos.** Os pares do projeto são o Ruff e o oxlint no lint, o pyright e o `tsc` nos tipos, e cada um liga e desliga regras uma a uma. A configuração atual nasceu aos poucos: o Ruff seleciona `E`, `F`, `W`, `I`, `N`, `B`, `UP`, `SIM`, `PERF`, `RUF`, `TRY`, `PTH` e `PLC0415`, e ignora `E501`, `UP047` e `TRY003` (`pyproject.toml`); o oxlint liga só os plugins `react`, `typescript` e `oxc`, com as regras do React Compiler, três regras de promise que olham os tipos e o `@shadcn/lint` (`frontend/.oxlintrc.json`); o pyright roda em `typeCheckingMode: "basic"` (`pyrightconfig.json`). A revisão responde duas perguntas: que regra desligada pegaria erro de verdade aqui, e que regra ligada só gera ruído e pode afrouxar.

O que falta definir para sair deste estado é a lista final, e ela sai de medição. (1) **Candidatas a ligar:** no Ruff, rodar `ruff check --select <grupo> --statistics` para `C4`, `RET`, `ARG`, `DTZ` (datas sem fuso), `PT` (estilo do pytest), `PL` (pylint), `ERA` (código comentado), `FBT` e `S` (bandit, segurança); no oxlint, as categorias `suspicious` e `pedantic` e os plugins `import`, `unicorn`, `promise`, `jsx-a11y` e `vitest`; no pyright, o modo `standard` e o `strict` por pasta. Cada grupo é julgado pelos achados reais: os que apontam bug ou código morto ficam, os que só pedem reescrita de estilo saem. (2) **Candidatas a afrouxar:** as regras com mais `noqa` hoje (`PLC0415` tem 12 dos 19 no backend) e as que forçam reescrita sem ganho; cada uma é confrontada com o motivo de ter entrado. (3) **Ferramentas além dessas quatro:** se cabe uma checagem que nenhuma delas faz, como export, arquivo e dependência sem uso no front (Knip), dependência sem uso no backend (deptry) e sintaxe dos workflows do GitHub Actions (actionlint). O resultado vira uma `F#` de aplicação, com as regras escolhidas e as violações corrigidas; o que mudar no oxlint atualiza a D15.
