<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-10-24):** Proventos na carteira e nas telas (F100) decididos e pendentes: provento cai no caixa, rendimento sintético pelo histórico do ativo e tudo isento de IR.

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | [F22](#f22), [F100](#f100) | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F10](#f10), [F110](#f110), [F111](#f111), [F127](#f127) | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | — | — |
| **N6** | Comparar resultados de simulações diferentes | — | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | [F22](#f22), [F100](#f100) | — |
| **N8** | Jogar contra oponentes controlados pelo computador | — | — |
| **N9** | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — |
| **N10** | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | — | — |
| **N11** | Que o cenário econômico simulado seja o histórico real | — | — |
| **N12** | Continuar jogando depois do último dia com dado real | — | — |
| **N13** | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | — |
| **N14** | Atualizar para uma versão nova sem perder as partidas salvas | [F56](#f56) | — |
| **N15** | Usar uma interface agradável e coerente, à altura de um jogo | [F37](#f37), [F72](#f72) | — |
| **N16** | Ver a carteira e o mercado por setor e segmento | — | — |
| **N17** | Enxergar a estrutura do banco e esboçar mudanças nela | — | — |
| **N18** | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — |
| **N19** | Analisar um ativo com as ferramentas de um trader | [F96](#f96) | — |
| **N20** | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | — |
| **N21** | Jogar "na unha", sem a interface apontar a melhor escolha | — | — |
| **N22** | Ter objetivos para buscar além de vencer a partida | [F122](#f122) | — |
| **N23** | Jogar com os amigos de outras formas além de cada um por si | [F69](#f69), [F101](#f101) | — |
| **N24** | Saber onde está a lentidão durante uma partida | — | — |
| **N25** | Entender o que é o simulador e como se joga, sem ler um manual | [F126](#f126), [F132](#f132), [F133](#f133) | — |
| **N26** | Achar a causa de um erro sem vasculhar o log inteiro | — | — |
| **N27** | Entrar numa partida que já começou | — | — |
| **N28** | Liberar uma vaga sem depender de o jogador sair | [F61](#f61) | — |
| **N29** | Saber o que cada jogador está fazendo enquanto a partida não começa | — | — |
| **N30** | Repetir uma configuração de partida sem montá-la de novo | — | — |
| **N31** | Saber o que está movendo o mercado da partida, como quem lê o noticiário | [F92](#f92) | — |
| **N32** | Saber como foi o mês sem montar a conta | [F91](#f91) | — |
| **N33** | Investir com dinheiro emprestado, pagando o juro do momento | [F111](#f111) | — |
| **N34** | Disputar o poder de mudar as regras da economia da partida | — | — |
| **N35** | Tirar da lista as partidas que não interessam mais | — | — |
| **N36** | Encontrar rapidamente os menores e maiores valores nos dados do jogo | — | — |
| **N37** | Comprar bitcoin do jeito que dá na vida real, em frações | [F127](#f127) | — |
| **N38** | Saber quando as estatísticas vão mudar, sem achar que travaram | — | — |
| [**F5**](#f5) | Spike: provider de túnel pela internet | — | 🔍 |
| [**F6**](#f6) | Link de convite pela internet no lobby | — | ⏳ |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F22**](#f22) | Preço ajustado e proventos | — | ⏳ |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | — | 🔍 |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 |
| [**F37**](#f37) | Tema escuro | — | 💤 |
| [**F44**](#f44) | Expansão Gestoras: fundar a gestora e abrir capital | — | 🔍 |
| [**F55**](#f55) | Modo aquisição hostil | — | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | 💤 |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | ⏳ |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | 💤 |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F81**](#f81) | CORS restrito à mesma origem | — | 💤 |
| [**F90**](#f90) | Cenários | — | 🔍 |
| [**F91**](#f91) | Caixa de entrada e resumo do mês | — | ⏳ |
| [**F92**](#f92) | Noticiário da partida | — | ⏳ |
| [**F93**](#f93) | Rumores antecipados | — | 🔍 |
| [**F96**](#f96) | Dicas de análise técnica | — | ⏳ |
| [**F97**](#f97) | SELIC nas mãos do governo | — | 🔍 |
| [**F100**](#f100) | Proventos na carteira e nas telas | — | ⏳ |
| [**F101**](#f101) | Carteira separada do jogador | — | 💤 |
| [**F102**](#f102) | Gestoras: emissão de novas cotas e recompra | — | 🔍 |
| [**F103**](#f103) | Gestoras: troca de gestor pela assembleia | — | 🔍 |
| [**F104**](#f104) | Gestoras: co-gestores | — | 🔍 |
| [**F105**](#f105) | Gestoras: rendimentos mensais | — | 🔍 |
| [**F106**](#f106) | Governo & Política: gasto público e inflação | — | 🔍 |
| [**F107**](#f107) | Perfis de público na eleição | — | 🔍 |
| [**F110**](#f110) | Combinar estratégias | — | 💤 |
| [**F111**](#f111) | Crédito para estratégias e bots | — | 💤 |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | 🔍 |
| [**F122**](#f122) | Novas conquistas para as features recentes e antigas | — | ⏳ |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 🔍 |
| [**F125**](#f125) | Revisão das regras de lint e da checagem de tipos | — | 🔍 |
| [**F127**](#f127) | Estratégias e bots operam cripto em fração | — | 💤 |
| [**F128**](#f128) | Governo & Política: rever os impostos por setor | — | 🔍 |
| [**F129**](#f129) | Governo & Política: rever a aprovação do governo | — | 🔍 |
| [**F130**](#f130) | Governo & Política: rever os votos e a eleição | — | 🔍 |
| [**F131**](#f131) | Catálogo de padrões de vela | — | 🔍 |
| [**F132**](#f132) | Tópicos de "como se joga" do Como jogar | — | ⏳ |
| [**F133**](#f133) | Tópicos de conceitos do Como jogar | — | ⏳ |

<details>
<summary><strong>Concluído / decidido / descartado (18 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | [F22](#f22), [F100](#f100), [F122](#f122) | ✅ |
| **D2** | Cálculo financeiro acontece só no backend; o frontend exibe | — | ✅ |
| **D3** | Dinheiro e quantidade trafegam como Decimal serializado em string | [F22](#f22), [F100](#f100), [F127](#f127) | ✅ |
| **D4** | Banco de dados embarcado no executável | — | ✅ |
| **D6** | A retomada continua no dia seguinte ao último evento | — | ✅ |
| **D7** | O simulador lê as séries sem saber a origem | [F22](#f22), [F92](#f92), [F100](#f100) | ✅ |
| **D8** | Bot, modo automático e backtest são o mesmo mecanismo | [F110](#f110), [F111](#f111) | ✅ |
| **D9** | De onde nasce uma mudança de schema | [F101](#f101) | ✅ |
| **D10** | Como a nota geral é calculada | — | ✅ |
| **D11** | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | ✅ |
| **D12** | Como numerar as versões | — | ✅ |
| **D13** | Um canal de tempo real só: Socket.IO, com fallback de polling | — | ✅ |
| **D14** | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | — | ✅ |
| **D15** | Lint com oxlint e o TypeScript 7 com a API do 6 ao lado | — | ✅ |
| **D16** | Estratégias do app no host, personalização pela API | — | ✅ |
| **D17** | Os tópicos do tutorial se animam em código, com o motion | [F126](#f126) | ✅ |
| [**F10**](#f10) | Guia de como escrever uma estratégia | — | ✅ |
| [**F126**](#f126) | Janela "Como jogar" | — | ✅ |

</details>

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: as `F#` que podem ser pegas agora — toda dependência já ✅. "Destrava" é quantas `F#` em aberto esperam por ela, direta ou indiretamente; é por aí que a tabela está ordenada. 💤 (sem prioridade) e 🚫 não entram.

| ID | Resumo | Marco | Destrava | Status |
| --- | --- | --- | --- | --- |
| [**F5**](#f5) | Spike: provider de túnel pela internet | M3 | 2 | 🔍 |
| [**F22**](#f22) | Preço ajustado e proventos | M8 | 2 | ⏳ |
| [**F91**](#f91) | Caixa de entrada e resumo do mês | M15 | 2 | ⏳ |
| [**F96**](#f96) | Dicas de análise técnica | M11 | 1 | ⏳ |
| [**F106**](#f106) | Governo & Política: gasto público e inflação | — | 1 | 🔍 |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | M9 | 0 | 🔍 |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | M11 | 0 | 🔍 |
| [**F56**](#f56) | Novidades no app | — | 0 | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | 0 | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | 0 | ⏳ |
| [**F90**](#f90) | Cenários | — | 0 | 🔍 |
| [**F107**](#f107) | Perfis de público na eleição | — | 0 | 🔍 |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | 0 | 🔍 |
| [**F122**](#f122) | Novas conquistas para as features recentes e antigas | — | 0 | ⏳ |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 0 | 🔍 |
| [**F125**](#f125) | Revisão das regras de lint e da checagem de tipos | — | 0 | 🔍 |
| [**F128**](#f128) | Governo & Política: rever os impostos por setor | — | 0 | 🔍 |
| [**F129**](#f129) | Governo & Política: rever a aprovação do governo | — | 0 | 🔍 |
| [**F130**](#f130) | Governo & Política: rever os votos e a eleição | — | 0 | 🔍 |
| [**F132**](#f132) | Tópicos de "como se joga" do Como jogar | M14 | 0 | ⏳ |
| [**F133**](#f133) | Tópicos de conceitos do Como jogar | M14 | 0 | ⏳ |

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
> **Progresso:** 1/1 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| — | *(nada em aberto)* | — | — |

<details><summary>Concluído (1 item)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F10**](#f10) | Guia de como escrever uma estratégia | — | ✅ |

</details>

### M8 — Dados reais, cuidados fora da partida

> **Objetivo:** Indicadores e preços fiéis ao histórico, geridos numa central antes de jogar.
>
> **Serve:** N3, N11, N13
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F22**](#f22) | Preço ajustado e proventos | — | ⏳ |
| [**F100**](#f100) | Proventos na carteira e nas telas | [F22](#f22) | ⏳ |

### M9 — Mercado sem fim

> **Objetivo:** Jogar além do último dia real sobre dados gerados que a simulação trata como reais.
>
> **Serve:** N12
>
> **Progresso:** 0/1 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | — | 🔍 |

### M11 — Análise técnica

> **Objetivo:** Analisar um ativo com os indicadores e as ferramentas de desenho de uma plataforma de trader.
>
> **Serve:** N19
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 |
| [**F96**](#f96) | Dicas de análise técnica | [F126](#f126) | ⏳ |
| [**F131**](#f131) | Catálogo de padrões de vela | [F96](#f96), [F126](#f126) | 🔍 |

### M14 — Vitrine e primeiros passos

> **Objetivo:** Ver o jogo funcionando antes de baixar e aprender a jogar vendo, não lendo.
>
> **Serve:** N25
>
> **Progresso:** 1/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F132**](#f132) | Tópicos de "como se joga" do Como jogar | [F126](#f126) | ⏳ |
| [**F133**](#f133) | Tópicos de conceitos do Como jogar | [F126](#f126) | ⏳ |

<details><summary>Concluído (1 item)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F126**](#f126) | Janela "Como jogar" | — | ✅ |

</details>

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

> **Progresso:** 0/30 concluídas

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
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | 💤 |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F81**](#f81) | CORS restrito à mesma origem | [F6](#f6) | 💤 |
| [**F90**](#f90) | Cenários | — | 🔍 |
| [**F97**](#f97) | SELIC nas mãos do governo | [F106](#f106) | 🔍 |
| [**F101**](#f101) | Carteira separada do jogador | — | 💤 |
| [**F102**](#f102) | Gestoras: emissão de novas cotas e recompra | [F44](#f44) | 🔍 |
| [**F103**](#f103) | Gestoras: troca de gestor pela assembleia | [F44](#f44) | 🔍 |
| [**F104**](#f104) | Gestoras: co-gestores | [F44](#f44) | 🔍 |
| [**F105**](#f105) | Gestoras: rendimentos mensais | [F44](#f44), [F100](#f100) | 🔍 |
| [**F106**](#f106) | Governo & Política: gasto público e inflação | — | 🔍 |
| [**F107**](#f107) | Perfis de público na eleição | — | 🔍 |
| [**F110**](#f110) | Combinar estratégias | — | 💤 |
| [**F111**](#f111) | Crédito para estratégias e bots | — | 💤 |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | 🔍 |
| [**F122**](#f122) | Novas conquistas para as features recentes e antigas | — | ⏳ |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 🔍 |
| [**F125**](#f125) | Revisão das regras de lint e da checagem de tipos | — | 🔍 |
| [**F127**](#f127) | Estratégias e bots operam cripto em fração | — | 💤 |
| [**F128**](#f128) | Governo & Política: rever os impostos por setor | — | 🔍 |
| [**F129**](#f129) | Governo & Política: rever a aprovação do governo | — | 🔍 |
| [**F130**](#f130) | Governo & Política: rever os votos e a eleição | — | 🔍 |

---

## 1. Atende necessidade

| ID | Resumo | Atende (N#) | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F6** | Link de convite pela internet no lobby | N2 | — | M3 | [F5](#f5) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F10** | Guia de como escrever uma estratégia | N4 | — | M4 | — | Baixo | Baixo | Médio | Bom | ✅ Concluído |
| **F37** | Tema escuro | N15 | — | — | — | Médio | Baixo | Médio | Médio | 💤 Registrado, sem prioridade |
| **F56** | Novidades no app | N14 | — | — | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F61** | Host remove jogador da sala | N28 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F69** | Imprevistos configuráveis e tipos novos | N23 | — | — | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F72** | Gráficos padronizados sobre o ChartContainer do shadcn | N15 | — | — | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F91** | Caixa de entrada e resumo do mês | N32 | — | M15 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F92** | Noticiário da partida | N31 | D7 | M15 | [F91](#f91) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F96** | Dicas de análise técnica | N19 | — | M11 | [F126](#f126) | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F101** | Carteira separada do jogador | N23 | D9 | — | — | Alto | Alto | Médio | Médio | 💤 Registrado, sem prioridade |
| **F110** | Combinar estratégias | N4 | D8 | — | — | Médio | Médio | Médio | Bom | 💤 Registrado, sem prioridade |
| **F111** | Crédito para estratégias e bots | N4, N33 | D8 | — | — | Baixo | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F122** | Novas conquistas para as features recentes e antigas | N22 | D1 | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F126** | Janela "Como jogar" | N25 | D17 | M14 | — | Médio | Baixo | Alto | Bom | ✅ Concluído |
| **F127** | Estratégias e bots operam cripto em fração | N4, N37 | D3 | — | — | Médio | Baixo | Baixo | Regular | 💤 Registrado, sem prioridade |
| **F22** | Preço ajustado e proventos | N3, N7 | D1, D3, D7 | M8 | — | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F100** | Proventos na carteira e nas telas | N3, N7 | D1, D3, D7 | M8 | [F22](#f22) | Médio | Médio | Médio | Bom | ⏳ Pendente |
| **F132** | Tópicos de "como se joga" do Como jogar | N25 | — | M14 | [F126](#f126) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F133** | Tópicos de conceitos do Como jogar | N25 | — | M14 | [F126](#f126) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |

<a id="f6"></a>
**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Abrir para a internet exige fechar antes a tomada do host: hoje ser host é ter o nickname do `config.toml`, e com o host desconectado qualquer jogador assume esse nickname por `/api/user/claim` e passa a poder parar a partida e apagar partidas salvas. O app gera um segredo a cada abertura e abre o navegador do host com ele; o servidor reconhece como host só a sessão que apresentou o segredo, e `/api/user/claim` recusa o nickname do host. O endereço de origem não distingue o host, porque num túnel o tráfego de fora costuma chegar ao servidor pela própria máquina. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada; com o host desconectado, nenhum outro jogador consegue virar host.

<a id="f10"></a>
**F10 — Guia de como escrever uma estratégia.** Origem: #49. Página no Docusaurus (grupo "Desenvolvimento"): como acrescentar uma estratégia ao app, com a classe base, o contexto que ela recebe a cada tick, como declarar nome e parâmetros e onde registrá-la para aparecer na página de Estratégias, nos bots e no backtest; uma das estratégias da F9 comentada linha a linha; e os limites (uma exceção devolve o jogador ao manual, o estado interno não volta na retomada). Quem não quer mexer no código do app tem o bot pela API (F108). Gatilho: F8 concluída — a API da classe base só fica estável depois dela.

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

<a id="f91"></a>
**F91 — Caixa de entrada e resumo do mês.** Serve N32. Como a caixa de entrada dos jogos de gerência de time: tudo o que a partida tem a contar chega num lugar só, sem pausar. (1) **Caixa de entrada:** um envelope na barra da partida, com o número de não lidas, abre um painel lateral com as entradas por data. Cada entrada tem um tipo (resumo, e depois notícia e conquista) e é de um jogador ou da sala inteira. Fica numa tabela `inbox_entries` (simulação, jogador ou nulo para a sala, data do jogo, tipo, conteúdo em JSONB, lida), é criada pelo motor da simulação na virada do mês e chega pelo Socket.IO com um aviso curto que some sozinho. (2) **Resumo do mês, de cada jogador:** patrimônio no início e no fim, rentabilidade do mês ao lado do CDI e do Ibovespa, melhor e pior posição, proventos recebidos, IR pago, aportes e a posição no ranking com quanto ela andou. Sai dos snapshots e dos eventos do mês, calculado no backend. (3) **Retrospectiva do ano:** na virada do ano, uma entrada maior com o ano mês a mês num gráfico pequeno, o melhor mês e a maior queda. Gatilho: antes do noticiário, que entrega as notícias por esta caixa.

<a id="f92"></a>
**F92 — Noticiário da partida.** Serve N31; segue a D7. Um noticiário sintético: as manchetes nascem das séries que a partida já lê, e por isso funcionam igual no futuro gerado, que é onde o jogo passa a maior parte do tempo, e na história real. Sem LLM e sem internet. (1) **Motor genérico:** uma lista de regras, cada uma olhando as séries no tick e, quando dispara, criando uma entrada da sala na caixa de entrada (F91) a partir de um modelo de texto com algumas variações, para a mesma frase não se repetir. Regra nova é só mais um item da lista. (2) **Macro, as manchetes padrão:** Copom subiu, baixou ou manteve a SELIC, com o tamanho ("Copom sobe a SELIC em 0,5 ponto, para 14,25%"); IPCA do mês acima ou abaixo do anterior; Ibovespa no recorde ou na maior queda do ano. (3) **Empresas:** a mesma lógica para um ativo que sobe ou cai mais de um limite no dia, chega à máxima de 52 semanas ou anuncia provento. O movimento ganha uma causa sintética plausível, sorteada de um banco de causas por setor e direção ("resultado do trimestre acima do esperado", "troca no comando", "vendas de fim de ano fracas" para o varejo). A notícia sai depois do movimento: dá contexto e não dá vantagem. (4) As notícias de um ativo aparecem também na tela dele, como marcadores no gráfico de preço. (5) **Extra, para período real:** marcos históricos curados à mão (crise de 2008, Joesley Day em 2017, Covid em março de 2020), num arquivo de dados com data, manchete e ativos ligados. O futuro gerado sempre começa depois do último dia real, então um marco datado só aparece em período real, e um cenário (F90) pode trazer os seus. Gatilho: depois da caixa de entrada.

<a id="f96"></a>
**F96 — Dicas de análise técnica.** Serve N19. Aprender análise técnica jogando: o gráfico aponta e explica o que um trader enxergaria, para quem quer jogar pelo gráfico sem já saber as regras. É ajuda, então o modo Especialista (F40) a desliga, como as outras. (1) **Padrões de vela:** regras fixas sobre abertura, máxima, mínima e fechamento de cada pregão detectam uns dez padrões clássicos (martelo, estrela cadente, engolfo de alta e de baixa, doji, três soldados brancos). O candle ganha um marcador; ao passar o mouse, um card com o nome, o desenho do padrão e o que ele costuma sugerir. **E se ele acertou:** o card conta quantas vezes o padrão apareceu neste ativo no período já jogado e em quantas o preço foi para o lado sugerido nos 5 pregões seguintes ("apareceu 12 vezes; em 7 o preço subiu"), o que ensina também que padrão não é garantia. (2) **Indicadores (F33):** as faixas ganham legenda (IFR acima de 70, "sobrecomprado": subiu rápido demais e costuma devolver; abaixo de 30, "sobrevendido") e os cruzamentos do MACD e das médias móveis ganham marcador com uma frase do que significam. (3) **Desafio da vela:** quando aparece um padrão, o jogo pergunta "e agora, sobe ou desce?" e confere dias depois, com um placar de acertos que pode virar conquista (F41). Gatilho: a janela "Como jogar" (F126) pronta, porque o desenho animado do padrão no card e o catálogo da F131 usam o palco e as animações em código que ela monta; os indicadores (F33) já estão prontos.

<a id="f101"></a>
**F101 — Carteira separada do jogador.** Serve N23; segue a D9. A base da expansão Gestoras (F44): hoje eventos e snapshots pertencem ao jogador (`user_id`), e a gestora precisa de carteira própria. Entra uma tabela `portfolios`, e eventos e snapshots passam a apontar para a carteira; a carteira pessoal de cada jogador é migrada uma a uma, inclusive nas partidas salvas. Nada muda na tela: cada jogador segue com uma carteira só até a F44 existir. Gatilho: a F44 sair da avaliação.

<a id="f110"></a>
**F110 — Combinar estratégias.** Serve N4; segue a D8. O jogador liga mais de uma estratégia ao mesmo tempo, cada uma com uma fatia do patrimônio (ex.: 30% em 100% no CDI e 70% no cruzamento de médias). O motor guarda, por jogador, a lista de estratégias com a fatia de cada uma e a origem de cada posição; cada estratégia recebe um contexto restrito à fatia dela (caixa e posições que ela comprou) e só opera dentro dele. A página de Estratégias passa de um interruptor para uma lista de fatias que somam 100%, e o log de ordens ganha o filtro por estratégia. Gatilho: F8 concluída e o uso pedir mais de uma estratégia.

<a id="f111"></a>
**F111 — Crédito para estratégias e bots.** Serve N4 e N33; segue a D8. O contexto da estratégia ganha a dívida, a nota de risco e a oferta do dia, e as ações ganham pegar empréstimo, amortizar e quitar, que chamam o mesmo serviço da tela de Crédito em nome do jogador. Uma estratégia de exemplo alavancada (ex.: rebalanceamento por meta com 20% emprestado) mostra o uso e entra na lista dos bots. O log da estratégia registra cada contratação e pagamento com o motivo. Gatilho: F8 e F94 concluídas.

<a id="f122"></a>
**F122 — Novas conquistas para as features recentes e antigas.** Serve N22; segue a D1. O catálogo tem 22 conquistas, quase todas de antes das últimas features, e várias coisas que o jogo já faz não rendem nada. Acrescentar uma é uma linha em `catalog.py` mais, quando a medida não existe, uma função `@metric` em `metrics.py` (o `code` nunca muda; nome, descrição e ícone podem mudar). Primeira leva, sobre o que já existe: (1) **Dentro da isenção** (IR da venda): fechar um mês vendendo ações sem pagar imposto por ficar abaixo do limite de isenção; (2) **Day trader** (IR): comprar e vender o mesmo ativo no mesmo dia; (3) **Em todo setor** (setores): ter ativos de cinco setores diferentes ao mesmo tempo, com barra de progresso; (4) **Mexeu o mercado** (impacto de preço): uma ordem sua mover o preço do ativo, valendo só em partida com o impacto ligado; (5) **Sem muletas** (modo Especialista): vencer a partida no modo Especialista; (6) **Time vencedor** (equipes): vencer uma partida em equipes; (7) **Além do horizonte** (dados gerados): jogar um dia além do último dia com dado real; (8) **Nota de craque** (nota geral): chegar a uma nota geral alta, com a meta calibrada nas notas das partidas já jogadas; (9) **Ordem com paciência**: ter a primeira ordem limite executada. Vale também uma regra daqui para a frente: cada feature nova que mexe no jogo traz as próprias conquistas no mesmo trabalho (crédito, proventos, bots e estratégias automáticas, por exemplo), em vez de esperar uma leva à parte. Gatilho: qualquer momento; nomes, descrições e ícones se fecham na hora de escrever cada linha.

<a id="f126"></a>
**F126 — Janela "Como jogar".** Serve N25. Tutorial no molde das Dicas e truques do Factorio, com cada tópico animado em código com o `motion` (D17). **Entregue:** a janela (lista de tópicos à esquerda, tópico à direita com ilustração, passos e dica, "Próximo" no rodapé), o palco reutilizável (componentes reais do app com contextos de exemplo, um `fetch` de exemplo só para a prévia de ordem, cursor e destaque que medem o DOM) e três tópicos no grupo "Renda variável": "Comprar uma ação" e "Ordem a mercado e limitada" (passo a passo animado) e "Alavancagem" (conceito, ilustração numérica; é o destino do "Saiba mais" da dica de alavancagem em Crédito). Tópico novo entra no registro `features/tutorial/lib/topics.ts` com id, grupo, texto e ilustração. **Nunca abre sozinha:** abre pelo botão do lobby, ao lado de Conquistas, e por um acesso na partida que o jogador escolhe em Configurações (aba na borda, padrão; item no menu; botão na topbar; desligado). **Aviso pelo contexto:** o primeiro tópico não visto da tela avisa uma vez, ancorado no acesso escolhido. "Visto" é abrir o tópico; o navegador guarda o que foi visto e avisado. **Tempo:** com um só jogador humano (bots não contam) e o tempo andando, abrir pausa e fechar retoma só se a janela pausou; com mais gente o tempo segue e o cabeçalho avisa. Se a animação não carrega, fica a imagem parada com "Tentar de novo". Com movimento reduzido a animação nasce pausada. O estado "depois de atualizar" não foi desenhado: as Novidades (F56) ainda não existem. Os demais tópicos saem nas F132 e F133.

<a id="f127"></a>
**F127 — Estratégias e bots operam cripto em fração.** Serve N4 e N37. Com a classe de cripto e a quantidade fracionária no ar, as estratégias seguem comprando só unidades inteiras (`int(caixa // preço)`), então um bot só compra bitcoin se o caixa pagar 1 unidade inteira. Plano: o contexto da estratégia passa a conhecer a classe do ativo, e as estratégias (comprar e segurar, rebalanceamento, momentum, RSI, médias móveis, rompimento) arredondam a quantidade em oito casas para cripto e em inteiro para as demais; `whole_shares` ganha a variante fracionária. Gatilho: a F113 concluída e o uso pedir bot com bitcoin.

<a id="f22"></a>
**F22 — Preço ajustado e proventos.** Serve N3 e N7; segue a D1, a D3 e a D7. O importador usa `yf.download(auto_adjust=True)`: o preço vem ajustado por dividendos e desdobramentos até o dia da importação, e a atualização incremental (`upsert_dataframe` só grava linhas depois da última data guardada) emenda duas séries ajustadas em dias diferentes. Um desdobramento 2:1 entre a importação e a atualização vira um degrau falso, uma queda de 50% que não existiu; além disso, o preço exibido não é o que se negociava na época. Escolhido: preço bruto mais proventos como evento. Plano: (1) **Importação:** `auto_adjust=False` guarda o fechamento bruto, e as listas de dividendos e de desdobramentos que o `yfinance` traz entram numa tabela de eventos corporativos por ativo (data ex, tipo, valor ou razão), por migration. A série bruta não muda quando sai um provento novo, então a atualização incremental passa a emendar séries do mesmo tipo e o degrau some. (2) **Desdobramento e grupamento:** na data ex, a quantidade de cada posição é multiplicada pela razão e o preço médio dividido por ela, como evento da partida reconstruível (D1), com a quantidade em Decimal (D3). (3) **Dividendo:** na data ex, o valor por cota vezes a quantidade entra no caixa, como evento; sem esse crédito o retorno de quem paga dividendo cairia, porque o preço bruto cai na data ex e o ajuste que antes embutia o provento deixa de existir. Telas, rendimento por posição, IR e provento sintético ficam na F100. (4) **Números que mudam:** o retorno e a nota geral (D10) mudam de valor, então os testes de números fixos são regerados e conferidos contra uma conta à mão antes de aceitar. (5) **Partidas salvas:** jogaram sobre o preço ajustado; o primeiro passo é verificar se o congelamento por versão da D7 (hoje usado só para trecho gerado) cobre também o trecho real, ou se as partidas salvas são recalculadas. Gatilho: livre; a F100 espera esta.
**Aceite:** num desdobramento 2:1 ocorrido depois da importação, a atualização incremental não produz queda de 50% no preço, e a posição de quem tinha o ativo dobra de quantidade sem mudar de valor.

<a id="f100"></a>
**F100 — Proventos na carteira e nas telas.** Serve N3 e N7; segue a D1, a D3 e a D7. Continua a F22, que guarda a lista de dividendos de cada ativo e credita o valor no caixa na data ex; aqui o provento passa a aparecer no jogo e a existir onde a API não o traz. O provento cai no caixa e nunca reinveste sozinho: o que fazer com o dinheiro é do jogador. Plano: (1) **Provento sintético:** para o futuro gerado, o gerador (D14) escreve os proventos na mesma tabela de eventos corporativos da F22, com origem gerada, junto com as séries; o motor lê real e gerado do mesmo jeito e o trecho congela com a partida salva, como as séries (D7). O rendimento anual de cada ativo é a média que ele pagou nos últimos anos do histórico real, com variação sorteada pela semente da geração, para todos receberem os mesmos nos mesmos dias; ativo sem histórico de proventos usa a média do setor, numa tabela de rendimento por setor. (2) **Carteira:** o total de proventos recebidos aparece no resumo e, em cada posição, o rendimento (proventos dos últimos 12 meses sobre o valor da posição hoje), em Decimal (D3). (3) **Detalhe do ativo:** a tela do ativo ganha o histórico de proventos (data ex, valor por cota, total recebido pelo jogador). (4) **Estatísticas e fechamento:** o que entrou como provento soma ao relatório da partida e à decomposição do retorno. (5) **IR:** dividendo e rendimento de FII são isentos para pessoa física, e a regra do simulador trata todo provento como isento; o `yfinance` não separa o JCP (juros sobre capital próprio, com 15% retidos na fonte) do dividendo, e essa simplificação entra escrita na página de impostos dos docs. Teste: um ativo com histórico paga o mesmo rendimento médio no futuro gerado com a mesma semente, e um ativo sem histórico usa a média do setor. Gatilho: F22 concluída; destrava os rendimentos mensais da gestora (F105).
**Aceite:** num ativo que pagou dividendos, o total recebido na carteira bate com a soma dos créditos no caixa na data ex, e o rendimento da posição bate com a conta feita à mão.

<a id="f132"></a>
**F132 — Tópicos de "como se joga" do Como jogar.** Serve N25. Completa o grupo de passo a passo da janela (F126) com os tópicos que faltam: entrar na sala, avançar o tempo, aplicar em renda fixa, ler as estatísticas e pegar crédito. Cada um é animado como "Comprar uma ação": componentes reais do app no palco, com contextos e dados de exemplo, e cursor e destaque que medem o DOM; entra no registro `features/tutorial/lib/topics.ts` com a cena em `features/tutorial/topics/`. Cada tópico pede um roteiro no canvas antes do código (quais passos, quanto dura, o que o cursor toca), e quem precisar de um dado novo no palco o acrescenta em `stage-data.ts`. Cada tela declara o tópico dela para o aviso pelo contexto.

<a id="f133"></a>
**F133 — Tópicos de conceitos do Como jogar.** Serve N25. Completa o grupo de conceitos da janela (F126), ao lado de "Alavancagem": médias móveis, nota de risco e correlação. Cada um é uma ilustração numérica com um exemplo concreto, no molde de "Alavancagem" (`features/tutorial/topics/leverage.tsx`): números pequenos que mostram a ideia, texto curto e um aviso "Bom e ruim" que diz o que é valor bom e ruim. Entra no registro `features/tutorial/lib/topics.ts`, e a dica da métrica correspondente ganha o "Saiba mais" apontando para ele (campo `topic` do `MetricInfo`). Não pede roteiro animado: pede o desenho da ilustração no canvas.

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F60** | Modo servidor dedicado (--headless) | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F67** | Abrir a pasta de configurações | — | — | — | Baixo | Baixo | Médio | Excelente | ⏳ Pendente |
| **F81** | CORS restrito à mesma origem | — | — | [F6](#f6) | Baixo | Médio | Baixo | Médio | 💤 Registrado, sem prioridade |

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

<a id="f60"></a>
**F60 — Modo servidor dedicado (`--headless`).** O mesmo executável, sem o navegador: para rodar numa VPS ou num PC ligado direto, sem ninguém jogando nele. `--headless` na linha de comando, ou `[server] headless = true` no `config.toml`, pula o `webbrowser.open` do `main.py`, que hoje roda sempre que o app é o executável, e imprime no terminal os endereços para entrar (o da rede local e, com a F6, o do túnel). O administrador é quem entra com o apelido de `[host] nickname`, que é como o host é definido hoje (`routes/simulation.py`). Como a recuperação de login é por apelido, num servidor exposto à internet qualquer um que digite esse apelido viraria o host; por isso, no modo servidor, o `config.toml` ganha `[host] pin`, e o login com o apelido do host só passa com ele. Serve a quem quer deixar uma sala aberta para os amigos entrarem quando quiserem, sem depender de o host estar com o computador ligado jogando.

<a id="f67"></a>
**F67 — Abrir a pasta de configurações.** O executável guarda `config.toml`, `.env` e `logs` na pasta de dados do usuário (`%LOCALAPPDATA%\SimuladorFinanceiro` no Windows), que o Windows esconde. Em vez de mudar os arquivos de lugar, a tela de configurações ganha o botão "Abrir pasta de configurações", como o "abrir pasta de mods" de vários jogos. (1) **Rota** `POST /api/settings/open-folder` em `routes/settings.py`, protegida por `verify_host` e que só aceita requisição vinda do próprio computador (`request.client.host` em `127.0.0.1` ou `::1`): o servidor também atende a rede local, e um convidado não pode abrir janelas na máquina do host. (2) **Abertura** da pasta de `app_files_dir()` com `os.startfile` no Windows, `open` no macOS e `xdg-open` no Linux, por `subprocess` sem shell. (3) **Sem interface gráfica** (servidor dedicado, Linux sem `xdg-open`) ou pedido fora do computador do host: a rota responde 409 com o caminho, e o front o mostra num campo com botão "Copiar". O caminho aparece sempre ao lado do botão, então o jogador também o encontra sem abrir nada. (4) Um segundo botão, "Abrir pasta de logs", usa a mesma rota com `target=logs`. Um aviso junto aos botões diz que `db` e `postgres` são do banco e não devem ser editados. Teste: a rota recusa quem não é o host e quem vem de outro IP, e chama o abridor do sistema (substituído por um dublê) com a pasta certa. Não serve nenhuma necessidade listada: o ganho é achar o `config.toml` sem caçar uma pasta oculta.

**Aceite:** no executável do Windows aberto por duplo clique, o botão abre o Explorer na pasta que contém o `config.toml`; um convidado da rede local que chama a rota recebe 403.

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
| **F28** | Muitos futuros (Monte Carlo) | Serve N10; revisa ou confirma a D7 | M9 | — | 🔍 Em avaliação |
| **F34** | Gráfico de ações em tela cheia, com ferramentas de trader | Serve N19; escolhe a biblioteca de gráfico | M11 | — | 🔍 Em avaliação |
| **F44** | Expansão Gestoras: fundar a gestora e abrir capital | Serve N23; falta o protótipo do preço da cota com o formador sintético | — | [F101](#f101) | 🔍 Em avaliação |
| **F55** | Modo aquisição hostil | Serve N23; faltam parte mínima no mercado e o destino do incorporado | — | [F103](#f103) | 🔍 Em avaliação |
| **F90** | Cenários | Serve N22; um preset com objetivo | — | — | 🔍 Em avaliação |
| **F93** | Rumores antecipados | N31; opção da partida | M15 | [F92](#f92) | 🔍 Em avaliação |
| **F97** | SELIC nas mãos do governo | N34; opção da expansão Governo & Política | — | [F106](#f106) | 🔍 Em avaliação |
| **F102** | Gestoras: emissão de novas cotas e recompra | Serve N23; falta o prazo da preferência e o preço da emissão | — | [F44](#f44) | 🔍 Em avaliação |
| **F103** | Gestoras: troca de gestor pela assembleia | Serve N23; falta como a assembleia escolhe o novo gestor | — | [F44](#f44) | 🔍 Em avaliação |
| **F104** | Gestoras: co-gestores | Serve N23; falta a divisão das taxas | — | [F44](#f44) | 🔍 Em avaliação |
| **F105** | Gestoras: rendimentos mensais | Serve N23; falta a parte do lucro distribuída | — | [F44](#f44), [F100](#f100) | 🔍 Em avaliação |
| **F106** | Governo & Política: gasto público e inflação | Serve N34; falta quanto cada medida soma ao IPCA | — | — | 🔍 Em avaliação |
| **F107** | Perfis de público na eleição | Serve N34; eleitores com perfil sobre a eleição da F95 | — | — | 🔍 Em avaliação |
| **F120** | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | Serve N15; falta escolher o desenho dos dois cards no canvas; liga à F72 | — | — | 🔍 Em avaliação |
| **F123** | Redesenhar o aviso de conquista desbloqueada | Serve N22 e N15; falta escolher o desenho do aviso no canvas; liga à F122 | — | — | 🔍 Em avaliação |
| **F125** | Revisão das regras de lint e da checagem de tipos | Nenhuma N#; qualidade do código. A configuração do oxlint é da D15 | — | — | 🔍 Em avaliação |
| **F128** | Governo & Política: rever os impostos por setor | Serve N34; revisão da versão jogável | — | — | 🔍 Em avaliação |
| **F129** | Governo & Política: rever a aprovação do governo | Serve N34; inclui a aprovação pesar na reeleição | — | — | 🔍 Em avaliação |
| **F130** | Governo & Política: rever os votos e a eleição | Serve N34; revisão da versão jogável | — | — | 🔍 Em avaliação |
| **F131** | Catálogo de padrões de vela | Serve N19; tópico do Como jogar com cada padrão animado | M11 | [F96](#f96), [F126](#f126) | 🔍 Em avaliação |

<a id="f5"></a>
**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO; se não passar, se ao menos o polling atravessa (o SSE saiu na D13, então o polling é o único fallback). O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

<a id="f28"></a>
**F28 — Muitos futuros (Monte Carlo).** Serve N10. Em vez de testar a estratégia num futuro gerado só, testá-la em muitos (ex.: 100, cada um com uma semente) e mostrar o resultado como distribuição: "perdeu para o CDI em 23 de 100 futuros; no pior, −35%; no do meio, +40% em 5 anos". Lê-se pela fração de futuros ruins e pelo pior caso: poucos futuros perdendo para o CDI é bom; uma estratégia que só ganha no histórico real e perde na maioria dos futuros plausíveis teve sorte, não mérito. É o backtest da F19 repetido sobre gerações do gerador da D14. Falta definir: **onde vivem os 100 futuros.** A D7 dá às tabelas de série uma dimensão de versão, que a F24 implementa para congelar partidas salvas. Opções: (1) cada futuro de Monte Carlo é uma versão descartável nessa dimensão, gravando 100 vezes as linhas geradas (cerca de 5 milhões para 37 ativos × 5 anos); (2) o motor lê as séries por um provedor que pode ser o banco ou uma geração em memória (o `SeriesGenerator` gera 37 ativos × 5 anos em cerca de 1 s), o que estende a D7 de "mesmas tabelas" para "mesma interface". Sai daqui com essa escolha, que revisa ou confirma a D7.

<a id="f34"></a>
**F34 — Gráfico de ações em tela cheia, com ferramentas de trader.** Serve N19; segue a D2. Um botão no card "Histórico de Preços" abre o gráfico em tela cheia, com os indicadores da F33 e o que uma plataforma de trader oferece: barra de ferramentas de desenho (linha de tendência, linha horizontal de suporte e resistência, canal, retângulo, retração de Fibonacci, texto), régua que mede variação % e pregões entre dois pontos, escala logarítmica, legenda com abertura, máxima, mínima, fechamento e volume do candle sob o cursor, comparação com outro ticker ou com o Ibovespa em %, e uma boleta compacta para comprar e vender sem sair da tela. Os desenhos ficam salvos por jogador e ticker numa tabela nova (`chart_drawings`, com os pontos em JSON), entrando por migration (D9). Falta escolher a biblioteca: (1) continuar no `lightweight-charts` e escrever as ferramentas de desenho como plugins (a API de primitives da versão 5; os exemplos oficiais trazem linha de tendência e retângulo); (2) trocar pelo KLineChart (Apache 2.0), que já vem com cerca de 15 ferramentas de desenho, mas calcula indicadores no navegador, e pela D2 eles viriam do backend como indicador customizado; (3) o Advanced Charts da TradingView tem tudo pronto, mas a licença pede cadastro e não permite publicar a biblioteca em repositório público, o que o deixa fora deste projeto. Sai daqui com um protótipo de linha de tendência e Fibonacci nas opções 1 e 2, e a escolha.

<a id="f44"></a>
**F44 — Expansão "Gestoras": fundar a gestora e abrir capital.** Serve N23. Inspiração: o Capitalism Lab (oferta pública, emissão de novas ações, recompra, compra de ações dos concorrentes), o OpenTTD e o Software Inc. Lá cada jogador é uma empresa que fabrica ou transporta; aqui tudo é finanças, então a empresa de cada jogador é uma gestora, e o que ela vende é o próprio desempenho. **Como expansão:** ligável por partida numa **aba própria "Expansões"** no lobby, com banner, emblema e "o que muda", como a loja de DLC dos jogos da Paradox; é enfeite visual, o sistema é o mesmo ligado ou não. **A gestora** tem nome e ticker de 4 letras mais 11, como cota de FII na B3 (o servidor recusa letras que já existam entre os ativos importados), e no livro de ofertas a linha leva a cor e a sigla do jogador, para não se confundir com ativo real. O jogador a funda levando **caixa, ações e títulos** da carteira em troca de cotas, e a opera por um **modo na topbar** ("Operando: Aurora Gestão"), que troca a conta de todas as telas de mercado, com uma faixa verde-petróleo e o caixa da gestora dizendo qual conta está ativa. **É um fundo fechado listado, como um FII:** (1) **oferta pública** quando o gestor quiser — cotas novas ao preço do patrimônio por cota (patrimônio de R$ 100 mil em 1.000 cotas dá R$ 100), e o dinheiro de quem compra entra na gestora: é investir no amigo; (2) **mercado** — depois da oferta, as cotas são negociadas no livro de ofertas que a renda variável já tem, e o preço sai da oferta e da procura, acima do patrimônio por cota (ágio) quando a sala acredita no gestor e abaixo (deságio) quando não; (3) **liquidez** — a liquidez de fundo do livro nasce dos candles de cada ativo, e a cota não tem candle, então um formador de mercado sintético põe ordens de compra e venda em volta do patrimônio por cota, numa faixa de 20% para cima e para baixo recalculada todo dia; dentro da faixa, o preço sai dos jogadores, e o livro tem contraparte até numa sala de 2; (4) **taxas** — a gestora paga aos gestores taxa de administração todo mês sobre o patrimônio e taxa de performance a cada 6 meses sobre o que passar do CDI, com teto na partida de **2% ao ano de administração e 20% de performance**, e cada gestor escolhe até o teto. A performance respeita a **marca d'água**, o maior patrimônio por cota sobre o qual a taxa já foi cobrada: se a cota cai de R$ 100 para 80 e volta a 100, a recuperação não paga performance. **O lucro fica dentro da gestora** e valoriza a cota. **Por que abrir capital, e quando:** as taxas são sobre o dinheiro dos outros, e com ágio as cotas do próprio gestor valem mais no ranking; o custo é ficar exposto, porque vender mais da metade abre a porta para perder o controle (F103). Abrir cedo, sem histórico, tende a sair com pouca procura; abrir depois de um bom ano tende a sair com ágio. **O gestor e a própria gestora:** o gestor negocia com a gestora pelo livro como qualquer jogador; a linha leva a sigla dele, então a negociação fica à vista, e quem cobra é a sala, vendendo a cota (deságio) ou trocando o gestor (F103). **Regras para o cálculo fechar:** só pessoas compram cotas, nunca gestoras, o que impede a participação cruzada (A com cotas da B, que tem cotas da A). No ranking, cada jogador soma a carteira pessoal, as taxas recebidas e as cotas que tem pelo **preço de ranking**: a média dos negócios dos últimos 20 pregões, ponderada pelo volume e limitada a 30% acima ou abaixo do patrimônio por cota; sem negócio no período, vale o patrimônio por cota. Um ágio de até 30% conta, e um negócio forçado a R$ 1.000 numa cota de R$ 100 conta no máximo como R$ 130. A carteira da gestora só conta através das cotas, sem contar o mesmo dinheiro duas vezes. **Estrutura:** a carteira própria da gestora é a F101; a cota é um ativo no livro de ofertas, com o patrimônio por cota publicado a cada dia. **Com a expansão Governo & Política (F95):** quando o gestor vence a eleição, na posse ele deixa de operar a gestora e de receber as taxas, porque a carteira do presidente fica congelada; um co-gestor (F104) assume e, sem co-gestor, a gestora congela até o fim do mandato; as cotas que ele tem continuam dele. A F95 sai antes, então a carteira congelada do presidente já existe quando a gestora for implementada: cabe a esta feature estender o congelamento à gestora. **Nas features seguintes:** emissão de novas cotas e recompra (F102), troca de gestor pela assembleia (F103), co-gestores (F104) e rendimentos mensais (F105). Falta: um protótipo do preço da cota no livro, com o formador sintético e jogadores comprando e vendendo, para calibrar a faixa de 20%.

<a id="f55"></a>
**F55 — Modo aquisição hostil.** Serve N23. Um modo de jogo da expansão "Gestoras" (F44) em que perder o controle tira o jogador da partida. Todo o patrimônio de cada jogador está na própria gestora, e quem juntar mais da metade das cotas de outra a incorpora: o dono anterior sai da partida e a gestora dele passa a ser controlada pelo comprador. Vence quem sobrar, ou quem tiver o maior patrimônio na data final. **Carência:** nos primeiros meses (padrão 12) ninguém pode passar de metade de outra gestora, para que abrir capital cedo não seja suicídio. **Ninguém fica invulnerável:** sem oferta pública, a gestora seria impossível de comprar, então no fim da carência todas precisam ter uma parte mínima das cotas no mercado (padrão 50%); quem não abriu capital entra numa oferta automática pelo patrimônio por cota. **Defesa:** recompra de cotas com o caixa da gestora e compra com as taxas recebidas, como uma empresa que recompra ações para não ser comprada. Falta decidir: a parte mínima no mercado; se o incorporado sai da partida ou vira co-gestor do comprador (como numa fusão); e se há um preço mínimo por cota durante a tentativa de aquisição, como nas ofertas públicas de aquisição reais.

<a id="f90"></a>
**F90 — Cenários.** Serve N22. Como nos jogos de estratégia: uma partida montada com intenção, um preset (F89) com objetivo e texto de abertura. Exemplos: "Crise de 2008" (começa em setembro de 2008 com R$ 100 mil, meta de não perder mais de 20%), "Década perdida" (futuro gerado com choque de inflação de +15 pontos) e "Plano Real". O objetivo usa os modos de jogo que já existem (corrida à meta, viver de renda) e o ranking. Falta definir: quais cenários entram primeiro e o objetivo de cada um; se o objetivo pode ser algo que os modos não cobrem (perda máxima, bater o CDI); se há campanha, com um cenário liberando o seguinte; e se o usuário cria os próprios cenários ou só joga os que vêm com o app.

<a id="f93"></a>
**F93 — Rumores antecipados.** Ligado à N31; uma opção da partida, desligada por padrão. O simulador já sabe o futuro: as séries até a data final estão no banco antes de a partida começar, sejam reais ou geradas. O rumor usa isso e chega antes do fato, ao contrário do noticiário (F92): dias antes de um movimento grande (queda forte de um setor, mudança da SELIC), aparece na caixa de entrada algo como "analistas veem risco no varejo". O valor do rumor é obrigar o jogador a pensar: pode acontecer ou não, e a frase pede interpretação. Por isso só uma parte dos rumores se confirma, outra parte é alarme falso sorteado onde nada vai acontecer, e alguns não dizem a direção ("mudanças na diretoria da X"). Falta definir: a taxa de acerto e a antecedência; quão vago o rumor é (setor ou ativo, com ou sem direção); se é da sala inteira ou informação de um jogador só (comprada, como um informante); e se vale no modo Especialista.

<a id="f97"></a>
**F97 — SELIC nas mãos do governo.** Ligado à N34; uma opção da expansão "Governo & Política" (F95), no lugar do Banco Central autônomo. (1) **Ritmo do Copom:** o governo decide a SELIC em reuniões a cada 45 dias, como o Copom, que se reúne 8 vezes por ano desde 2006; entre reuniões ela não muda. (2) **Teto por reunião, pelo que aconteceu de verdade.** Das 150 mudanças da meta da SELIC entre 2000 e outubro de 2026 (série do Banco Central): 34 foram de 0,25 ponto, 67 de 0,5, 19 de 0,75, 19 de 1, 7 de 1,5, uma de 2, uma de 2,5 (cortes de 2003) e duas de 3 (as altas da crise de 2002); desde 2006, nunca passou de 1,5. O teto acompanha isso: até 0,75 ponto por reunião em tempo normal (80% das mudanças reais), 1,5 com a inflação bem acima da meta, como em 2021 e 2022, e 3 só com a inflação explodindo, como em 2002. (3) **O preço de cada lado:** a SELIC abaixo do que o Banco Central autônomo faria (a da série, ou a do gerador) faz a inflação subir com alguns meses de atraso, pelo mesmo mecanismo de efeito por cima das séries da F106, e inflação alta derruba a aprovação; a SELIC alta demais derruba a bolsa pelo coeficiente da D14, o que também pesa na aprovação. Falta definir: quanto a inflação reage à SELIC e com quanto atraso (medir no histórico, como a D14 mediu a reação da SELIC à inflação), e os limites de inflação que liberam cada degrau do teto.

<a id="f102"></a>
**F102 — Gestoras: emissão de novas cotas e recompra.** Serve N23; amplia a expansão Gestoras (F44). (1) **Emissão:** depois da oferta pública, o gestor emite cotas novas com preferência para quem já é cotista, na proporção das cotas de cada um, para ninguém ser diluído sem escolher; o dinheiro entra na gestora. (2) **Recompra:** a gestora compra as próprias cotas no livro com o caixa dela; vale quando a cota está com deságio (pagar R$ 80 por R$ 100 de patrimônio valoriza a cota de quem fica) e é a defesa contra a troca de gestor (F103). Falta decidir: quanto tempo dura a preferência, e se o preço da emissão é o patrimônio por cota ou o preço de mercado (com ágio, emitir a mercado traz mais dinheiro por cota).

<a id="f103"></a>
**F103 — Gestoras: troca de gestor pela assembleia.** Serve N23; amplia a expansão Gestoras (F44). Quem juntar mais da metade das cotas troca o gestor pela assembleia de cotistas e passa a operar a carteira e a receber as taxas. É o custo de abrir capital, e a defesa é a recompra (F102) e comprar cotas com as taxas recebidas. O modo aquisição hostil (F55) se apoia nesta regra. Falta decidir: se a troca é automática ao passar de metade ou uma votação convocada; se o novo gestor é sempre quem juntou as cotas ou alguém que ele indica; e o que o gestor afastado mantém além das próprias cotas.

<a id="f104"></a>
**F104 — Gestoras: co-gestores.** Serve N23; amplia a expansão Gestoras (F44). A gestora pode ter mais de um gestor, por convite: eles operam a mesma carteira pelo modo na topbar e dividem as taxas, como sócios da mesma empresa. Com a expansão Governo & Política, o co-gestor é quem assume a gestora quando o gestor vira presidente (F95). Falta decidir: como as taxas se dividem (em partes iguais ou pelas cotas de cada um) e quem convida ou tira um co-gestor.

<a id="f105"></a>
**F105 — Gestoras: rendimentos mensais.** Serve N23; amplia a expansão Gestoras (F44) e espera os proventos (F100), porque hoje nem os FIIs importados pagam rendimento. Como um FII, a gestora distribui todo mês parte do lucro aos cotistas, em dinheiro no caixa de cada um, e a cota deixa de render só por valorização. Falta decidir: a parte do lucro distribuída (os FIIs reais distribuem pelo menos 95% do lucro do semestre), se ela é fixa ou escolha do gestor, e o que conta como lucro (só o realizado ou também a valorização da carteira).

<a id="f106"></a>
**F106 — Governo & Política: gasto público e inflação.** Ligado à N34; amplia a expansão Governo & Política (F95) com a segunda alavanca, o gasto público, que mexe na economia em vez de só nos impostos. A medida vira um efeito por cima das séries, do mesmo jeito que o impacto de preço de ordens grandes: o preço do dia é o da série vezes (1 + a soma dos efeitos ativos), cada efeito nasce de um evento, vale cheio no começo e decai com o tempo, e tudo se reconstrói a partir dos eventos numa retomada. Aqui o efeito soma pontos ao IPCA, e o resto segue os coeficientes que a D14 já mediu: a SELIC reage com 1,5 vez a inflação (com o Banco Central autônomo) e a bolsa cai 2,9% no trimestre por ponto de alta da SELIC, ativo a ativo pelo beta. A série guardada não muda, e por isso vale também na história real. Gastar puxa a régua da campanha para "gasto alto", e a inflação que vem dele derruba a aprovação. Falta definir: quantos pontos de IPCA cada medida de gasto soma, com quanto atraso e em quanto tempo o efeito decai; e se, na história real, a SELIC da série também ganha o efeito, para reagir à inflação somada.

<a id="f107"></a>
**F107 — Perfis de público na eleição.** Ligado à N34; amplia a eleição da expansão Governo & Política (F95). Em vez de um eleitorado único, a eleição ganha eleitores artificiais agrupados em perfis (por exemplo, quem vive de renda, quem empreende, quem depende de serviço público), cada um com a própria posição na régua de promessa e a própria sensibilidade à verba. A transferência de votos do segundo turno deixa de ser "vai inteiro para o finalista com a promessa mais parecida" e passa a ser perfil a perfil, pela distância entre a promessa de cada finalista e a posição daquele perfil, e a pesquisa de intenção de voto pode mostrar o voto por perfil. Falta definir: quais perfis existem e quanto cada um pesa no eleitorado, se o peso muda com a economia da partida (desemprego, inflação), e se a aprovação do governo também passa a ser medida por perfil.

<a id="f120"></a>
**F120 — Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira.** O que incomoda: o tooltip do donut (`allocation-donut.tsx`, um `Tooltip` do Recharts com estilo avulso) não agrada; o estilo do gráfico de evolução (`networth-chart.tsx`: áreas empilhadas por classe, linha tracejada do aportado, rótulos de fim à direita) parece estranho; e outros lugares usam um gráfico parecido (a área de composição das Estatísticas e a linha de desempenho). Falta escolher o desenho dos dois cards: que tipo de gráfico mostra a evolução (áreas empilhadas, uma linha de patrimônio contra o aportado, ou o patrimônio com o ganho destacado), o que o donut conta e como o tooltip responde, e se os dois cards continuam lado a lado. Parte de uma rodada no canvas, com variantes dos dois cards e do estado vazio e com poucos pontos. Ao aprovar, o visual vale para os gráficos parecidos, e a F72 (convenção de pasta e `ChartContainer`) é o lugar de migrá-los. Sai daqui para Pendente com a variante escolhida.

<a id="f123"></a>
**F123 — Redesenhar o aviso de conquista desbloqueada.** Hoje o aviso (`achievement-toast.tsx`, aberto com `toast.custom` do sonner) é um cartão escuro de 380 px com uma faixa amarela de 3 px à esquerda, o ícone, o rótulo amarelo em maiúsculas ("Conquista desbloqueada"), o nome e a descrição; quando várias saem no mesmo dia, vira uma lista com "Ver todas". O incômodo existe, mas não está claro de onde vem: pode ser a faixa amarela do canto, o rótulo, o peso do cartão escuro, o tamanho ou a falta de movimento. Falta escolher o desenho depois de ver variantes lado a lado no canvas: (a) o cartão atual sem a faixa, com o ícone em destaque; (b) um cartão claro, no tema do app; (c) um formato compacto, com o ícone e o nome numa linha só e a descrição ao passar o mouse; (d) um formato de "selo" com a categoria e a cor dela. A rodada cobre os estados uma conquista, várias no mesmo dia, secreta revelada e conquista com barra de progresso completa, e decide a posição na tela e a entrada e saída. Sai daqui para Pendente com a variante escolhida.

<a id="f125"></a>
**F125 — Revisão das regras de lint e da checagem de tipos.** Os pares do projeto são o Ruff e o oxlint no lint, o pyright e o `tsc` nos tipos, e cada um liga e desliga regras uma a uma. A configuração atual nasceu aos poucos: o Ruff seleciona `E`, `F`, `W`, `I`, `N`, `B`, `UP`, `SIM`, `PERF`, `RUF`, `TRY`, `PTH` e `PLC0415`, e ignora `E501`, `UP047` e `TRY003` (`pyproject.toml`); o oxlint liga só os plugins `react`, `typescript` e `oxc`, com as regras do React Compiler, três regras de promise que olham os tipos e o `@shadcn/lint` (`frontend/.oxlintrc.json`); o pyright roda em `typeCheckingMode: "basic"` (`pyrightconfig.json`). A revisão responde duas perguntas: que regra desligada pegaria erro de verdade aqui, e que regra ligada só gera ruído e pode afrouxar.

O que falta definir para sair deste estado é a lista final, e ela sai de medição. (1) **Candidatas a ligar:** no Ruff, rodar `ruff check --select <grupo> --statistics` para `C4`, `RET`, `ARG`, `DTZ` (datas sem fuso), `PT` (estilo do pytest), `PL` (pylint), `ERA` (código comentado), `FBT` e `S` (bandit, segurança); no oxlint, as categorias `suspicious` e `pedantic` e os plugins `import`, `unicorn`, `promise`, `jsx-a11y` e `vitest`; no pyright, o modo `standard` e o `strict` por pasta. Cada grupo é julgado pelos achados reais: os que apontam bug ou código morto ficam, os que só pedem reescrita de estilo saem. (2) **Candidatas a afrouxar:** as regras com mais `noqa` hoje (`PLC0415` tem 12 dos 19 no backend) e as que forçam reescrita sem ganho; cada uma é confrontada com o motivo de ter entrado. (3) **Ferramentas além dessas quatro:** se cabe uma checagem que nenhuma delas faz, como export, arquivo e dependência sem uso no front (Knip), dependência sem uso no backend (deptry) e sintaxe dos workflows do GitHub Actions (actionlint). O resultado vira uma `F#` de aplicação, com as regras escolhidas e as violações corrigidas; o que mudar no oxlint atualiza a D15.

<a id="f128"></a>
**F128 — Governo & Política: rever os impostos por setor.** Serve N34; revisão da versão jogável que a F95 entregou. **Como funciona hoje:** a política de impostos padrão é a de antes da expansão (15% no ganho comum de ações, 20% no day trade e no FII, isenção das vendas de ações até R$ 20 mil no mês, tabela da renda fixa de 22,5% a 15% por prazo, LCI e LCA isentas). O presidente propõe medidas gerais (alíquota do ganho comum, alíquota do day trade, teto da isenção de ações, uma alíquota única no lugar da tabela da renda fixa e a alíquota de LCI e LCA, de 0 a 100% e diferente da vigente) e medidas de setor ou segmento (isentar, ou taxar de mais de 0 até 20 pontos por medida, que se empilham sem teto acumulado). No IR do mês, vale a regra do dia de cada venda; segmento vence setor e, entre iguais, vale a mais nova. A venda de setor isento conta no volume dos R$ 20 mil, mas o ganho e o prejuízo dela saem do cálculo; a venda de setor taxado soma os pontos extras ao resultado positivo. A medida aprovada vale 90 dias depois. Na régua da promessa, corte geral é 1, isenção de setor 2, taxar setor 4 e imposto geral novo 5; na aprovação, isentar setor soma 2, taxar setor tira de 1 a 5 (pontos ÷ 2), corte geral soma de 1 a 3 e imposto geral novo tira de 1 a 5. Falta definir: o que muda nessa mecânica, a partir das ideias de refazer o sistema.

<a id="f129"></a>
**F129 — Governo & Política: rever a aprovação do governo.** Serve N34; revisão da versão jogável que a F95 entregou. **Como funciona hoje:** a aprovação começa em 50% na posse e é recalculada no último dia útil de cada mês, só com um jogador na presidência, limitada entre 0 e 100%. Fatores: inflação de 12 meses contra a meta do CMN do ano (tabela de 2000 a 2024; fora dela, 3%), +4 dentro ou abaixo da meta e −3 por ponto acima, sem teto; Ibovespa de 12 meses, 1 ponto a cada 5% de alta ou queda, até ±6; medidas aprovadas e já vigentes, em que o corte de imposto soma e não decai, e o imposto novo e a taxação de setor tiram pontos que somem em linha reta em 180 dias; e a promessa, que tira 3 pontos por faixa de distância entre a marca do governo (a média das faixas das medidas aprovadas) e a promessa da campanha. O Congresso vota a fila no mesmo dia: cada medida passa se um sorteio de 0 a 100, feito a partir da semente da partida, da data e do número da medida, sair abaixo da aprovação. A fila não aceita duas medidas iguais; a retirada vale só antes do voto, e a rejeitada pode voltar. Impeachment com aprovação abaixo de 25% em 3 fechamentos de mês seguidos, com aviso no 2º; o vice assume se ainda for filiado, senão entra um governo neutro do computador, sem medidas. Na troca, a fila some, o histórico de aprovação zera, as medidas aprovadas seguem valendo e a carteira de quem saiu volta a operar. **Ainda não existe:** a aprovação não pesa na eleição; a única trava da reeleição é o limite de 2 mandatos seguidos, e por isso "aprovação baixa perde a reeleição" ainda não vale. Falta definir: o que muda nos fatores e nos pesos, e quanto a aprovação do mandato pesa no voto da eleição seguinte.

<a id="f130"></a>
**F130 — Governo & Política: rever os votos e a eleição.** Serve N34; revisão da versão jogável que a F95 entregou. **Como funciona hoje:** a primeira eleição é escolhida no lobby e precisa cair dentro da partida; o mandato é de 4 anos, com até 2 seguidos. A campanha abre 1 ano antes do 1º turno (ou no início da partida), as chapas fecham no último dia do mês anterior, o 1º turno é em 7 de outubro e o 2º, 21 dias depois, no próximo dia útil quando a data cai em fim de semana; a posse é em 1º de janeiro. No 1º dia útil de cada mês da campanha, cada filiado paga a contribuição que escolheu, se tiver caixa, e o gasto vira pontos pela raiz quadrada ÷ 64 (R$ 8 mil dão 1,4 ponto) num eleitorado de 100; o que sobra são os indecisos, e a pesquisa guarda uma foto por mês. No 1º turno, vence quem tiver mais de 50% dos votos válidos; senão, vão os dois mais votados, e o empate fica com o partido mais antigo. No 2º turno, os votos de quem ficou de fora vão inteiros para o finalista com a promessa mais próxima. Entre os turnos, até a véspera do 2º, quem está num partido eliminado pode doar a um finalista; a doação rende pela mesma raiz e entra na hora. Os partidos do computador (União do Progresso, Movimento Novo Vigor e Aliança Cidadã) completam até 3 chapas, com a verba da média dos partidos de jogadores vezes 0,5, 1 ou 1,5 pela dificuldade, e a promessa na faixa mais longe dos partidos que já existem. Cada resultado de turno e o impeachment pausam a partida. Só jogadores fundam e se filiam, durante a campanha e fora do 2º turno; bots ficam fora. Na vitória política, vence o partido com a maior soma de patrimônio dos filiados, sem os do computador. Falta definir: o que muda no voto e na eleição, a partir das ideias de refazer o sistema; a F107 (perfis de público) já é uma dessas mudanças.

<a id="f131"></a>
**F131 — Catálogo de padrões de vela.** Serve N19. Um tópico do "Como jogar" (F126) que lista todos os padrões que as dicas de análise técnica (F96) reconhecem, cada um com o ícone e o nome que aparecem no gráfico (o martelo com o símbolo dele, por exemplo). Navegar pelo catálogo mostra um padrão por vez, com a animação das velas se formando no molde dos roteiros do tutorial, o que o padrão costuma sugerir e o lembrete de que padrão não é garantia. Em aberto: se o catálogo é um tópico do tutorial ou uma tela própria, e se o card do padrão no gráfico ganha um "ver no catálogo". Gatilho: com as dicas de análise técnica e a janela "Como jogar" prontas.
