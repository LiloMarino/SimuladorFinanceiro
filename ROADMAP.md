<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-10-27):** Fechadas as regras do governo das versões 3.1 e 3.2: os nove cards do rework passaram a pendentes, com os números marcados para o protótipo (27/out)

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | [F22](#f22), [F100](#f100) | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F110](#f110), [F111](#f111), [F127](#f127) | — |
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
| **N15** | Usar uma interface agradável e coerente, à altura de um jogo | [F37](#f37), [F72](#f72), [F120](#f120), [F160](#f160), [F162](#f162), [F166](#f166) | — |
| **N16** | Ver a carteira e o mercado por setor e segmento | — | — |
| **N17** | Enxergar a estrutura do banco e esboçar mudanças nela | — | — |
| **N18** | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — |
| **N19** | Analisar um ativo com as ferramentas de um trader | — | — |
| **N20** | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | — |
| **N21** | Jogar "na unha", sem a interface apontar a melhor escolha | — | — |
| **N22** | Ter objetivos para buscar além de vencer a partida | [F159](#f159) | — |
| **N23** | Jogar com os amigos de outras formas além de cada um por si | [F69](#f69), [F101](#f101) | — |
| **N24** | Saber onde está a lentidão durante uma partida | — | — |
| **N25** | Entender o que é o simulador e como se joga, sem ler um manual | [F132](#f132), [F133](#f133), [F139](#f139), [F140](#f140), [F141](#f141) | — |
| **N26** | Achar a causa de um erro sem vasculhar o log inteiro | — | — |
| **N27** | Entrar numa partida que já começou | — | — |
| **N28** | Liberar uma vaga sem depender de o jogador sair | — | — |
| **N29** | Saber o que cada jogador está fazendo enquanto a partida não começa | — | — |
| **N30** | Repetir uma configuração de partida sem montá-la de novo | — | — |
| **N31** | Saber o que está movendo o mercado da partida, como quem lê o noticiário | [F92](#f92), [F161](#f161) | — |
| **N32** | Saber como foi o mês sem montar a conta | [F161](#f161) | — |
| **N33** | Investir com dinheiro emprestado, pagando o juro do momento | [F111](#f111) | — |
| **N34** | Disputar o poder de mudar as regras da economia da partida | [F106](#f106), [F107](#f107), [F128](#f128), [F129](#f129), [F130](#f130), [F151](#f151), [F152](#f152), [F153](#f153), [F154](#f154), [F163](#f163) | — |
| **N35** | Tirar da lista as partidas que não interessam mais | — | — |
| **N36** | Encontrar rapidamente os menores e maiores valores nos dados do jogo | — | — |
| **N37** | Comprar bitcoin do jeito que dá na vida real, em frações | [F127](#f127) | — |
| **N38** | Saber quando as estatísticas vão mudar, sem achar que travaram | — | — |
| **N39** | Chegar ao primeiro dia da partida com as próprias escolhas já feitas | — | — |
| **N40** | Jogar partidas longas e na velocidade máxima sem a tela travar | — | — |
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
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | 💤 |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F81**](#f81) | CORS restrito à mesma origem | — | 💤 |
| [**F90**](#f90) | Cenários | — | 🔍 |
| [**F92**](#f92) | Noticiário da partida | — | ⏳ |
| [**F93**](#f93) | Rumores antecipados | — | 🔍 |
| [**F97**](#f97) | SELIC nas mãos do governo | — | 🔍 |
| [**F100**](#f100) | Proventos na carteira e nas telas | — | ⏳ |
| [**F101**](#f101) | Carteira separada do jogador | — | 💤 |
| [**F102**](#f102) | Gestoras: emissão de novas cotas e recompra | — | 🔍 |
| [**F103**](#f103) | Gestoras: troca de gestor pela assembleia | — | 🔍 |
| [**F104**](#f104) | Gestoras: co-gestores | — | 🔍 |
| [**F105**](#f105) | Gestoras: rendimentos mensais | — | 🔍 |
| [**F106**](#f106) | Governo & Política: medidas de gasto público | — | ⏳ |
| [**F107**](#f107) | Grupos de eleitores, com apoio e rejeição por partido | — | ⏳ |
| [**F110**](#f110) | Combinar estratégias | — | 💤 |
| [**F111**](#f111) | Crédito para estratégias e bots | — | 💤 |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 🔍 |
| [**F128**](#f128) | Orçamento do governo, dívida pública e prêmio de risco | — | ⏳ |
| [**F129**](#f129) | Aprovação do governo pelos grupos de eleitores | — | ⏳ |
| [**F130**](#f130) | Ações de campanha: a eleição deixa de ser só dinheiro | — | ⏳ |
| [**F131**](#f131) | Catálogo de padrões de vela | — | 🔍 |
| [**F132**](#f132) | Tópicos de "como se joga" do Como jogar | — | ⏳ |
| [**F133**](#f133) | Tópicos de conceitos do Como jogar | — | ⏳ |
| [**F139**](#f139) | Demonstração regravada com o jogo de hoje | — | ⏳ |
| [**F140**](#f140) | Docs reorganizada por tipo de leitor | — | ⏳ |
| [**F141**](#f141) | README com as features de hoje | — | ⏳ |
| [**F143**](#f143) | Preparação de cada jogador no lobby | — | 🔍 |
| [**F151**](#f151) | Segundo turno com disputa | — | ⏳ |
| [**F152**](#f152) | Promessas de campanha cobradas no mandato | — | ⏳ |
| [**F153**](#f153) | Congresso eleito, com bancadas orientadas pelo líder | — | ⏳ |
| [**F154**](#f154) | Negociar apoio com as bancadas, por emendas | — | ⏳ |
| [**F157**](#f157) | Velocidade x100 que quase não acelera | — | 🔍 |
| [**F158**](#f158) | Animações do Como jogar revistas | — | 🔍 |
| [**F159**](#f159) | Conquista "Ordem com paciência" | — | ⏳ |
| [**F161**](#f161) | Jornal da partida: notificações configuráveis por tipo | — | ⏳ |
| [**F163**](#f163) | Painel da economia: SELIC e IPCA ao longo da partida | — | ⏳ |
| [**F164**](#f164) | Mapa do Brasil por região na eleição | — | 🔍 |
| [**F165**](#f165) | Tela do Tesouro: títulos pelo risco do governo | — | 🔍 |
| [**F166**](#f166) | Pendências da partida: o que pede ação fica à vista até ser resolvido | — | ⏳ |

<details>
<summary><strong>Concluído / decidido / descartado (22 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | [F22](#f22), [F100](#f100), [F159](#f159) | ✅ |
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
| **D14** | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | [F106](#f106), [F128](#f128) | ✅ |
| **D15** | Lint com oxlint, formatação com oxfmt e o TypeScript 7 com a API do 6 ao lado | — | ✅ |
| **D16** | Estratégias do app no host, personalização pela API | — | ✅ |
| **D17** | Os tópicos do tutorial se animam em código, com o motion | — | ✅ |
| **D18** | Uma migration por versão; caminho antigo só cai numa major | — | ✅ |
| **D19** | O eleitorado são grupos, cada um com apoio e rejeição por partido | [F106](#f106), [F107](#f107), [F128](#f128), [F129](#f129), [F130](#f130), [F151](#f151), [F152](#f152), [F153](#f153), [F154](#f154) | ✅ |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | ✅ |
| [**F127**](#f127) | Estratégias e bots operam cripto em fração | — | ✅ |
| [**F160**](#f160) | Imprevistos no fim da partida de independência | — | ✅ |
| [**F162**](#f162) | Sinal de partida pausada e destaque da velocidade máxima | — | ✅ |

</details>

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: as `F#` que podem ser pegas agora — toda dependência já ✅. "Destrava" é quantas `F#` em aberto esperam por ela, direta ou indiretamente; é por aí que a tabela está ordenada. 💤 (sem prioridade) e 🚫 não entram.

| ID | Resumo | Marco | Destrava | Status |
| --- | --- | --- | --- | --- |
| [**F107**](#f107) | Grupos de eleitores, com apoio e rejeição por partido | M17 | 11 | ⏳ |
| [**F5**](#f5) | Spike: provider de túnel pela internet | M3 | 2 | 🔍 |
| [**F22**](#f22) | Preço ajustado e proventos | M8 | 2 | ⏳ |
| [**F161**](#f161) | Jornal da partida: notificações configuráveis por tipo | M15 | 2 | ⏳ |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | M9 | 0 | 🔍 |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | M11 | 0 | 🔍 |
| [**F56**](#f56) | Novidades no app | — | 0 | ⏳ |
| [**F90**](#f90) | Cenários | — | 0 | 🔍 |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 0 | 🔍 |
| [**F131**](#f131) | Catálogo de padrões de vela | M11 | 0 | 🔍 |
| [**F132**](#f132) | Tópicos de "como se joga" do Como jogar | M14 | 0 | ⏳ |
| [**F133**](#f133) | Tópicos de conceitos do Como jogar | M14 | 0 | ⏳ |
| [**F143**](#f143) | Preparação de cada jogador no lobby | — | 0 | 🔍 |
| [**F157**](#f157) | Velocidade x100 que quase não acelera | M16 | 0 | 🔍 |
| [**F158**](#f158) | Animações do Como jogar revistas | M14 | 0 | 🔍 |
| [**F163**](#f163) | Painel da economia: SELIC e IPCA ao longo da partida | M17 | 0 | ⏳ |
| [**F166**](#f166) | Pendências da partida: o que pede ação fica à vista até ser resolvido | M15 | 0 | ⏳ |

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
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 |
| [**F131**](#f131) | Catálogo de padrões de vela | — | 🔍 |

### M14 — Vitrine e primeiros passos

> **Objetivo:** Ver o jogo funcionando antes de baixar e aprender a jogar vendo, não lendo.
>
> **Serve:** N25
>
> **Progresso:** 0/6 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F132**](#f132) | Tópicos de "como se joga" do Como jogar | — | ⏳ |
| [**F133**](#f133) | Tópicos de conceitos do Como jogar | — | ⏳ |
| [**F139**](#f139) | Demonstração regravada com o jogo de hoje | [F44](#f44) | ⏳ |
| [**F140**](#f140) | Docs reorganizada por tipo de leitor | [F44](#f44) | ⏳ |
| [**F141**](#f141) | README com as features de hoje | [F139](#f139) | ⏳ |
| [**F158**](#f158) | Animações do Como jogar revistas | — | 🔍 |

### M15 — Notícias e resumo do mês

> **Objetivo:** A partida conta o que acontece no mercado e como foi o mês de cada jogador.
>
> **Serve:** N31, N32
>
> **Progresso:** 0/4 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F92**](#f92) | Noticiário da partida | [F161](#f161) | ⏳ |
| [**F93**](#f93) | Rumores antecipados | [F92](#f92) | 🔍 |
| [**F161**](#f161) | Jornal da partida: notificações configuráveis por tipo | — | ⏳ |
| [**F166**](#f166) | Pendências da partida: o que pede ação fica à vista até ser resolvido | — | ⏳ |

### M16 — Partida sem tropeços

> **Objetivo:** Repetir uma partida com amigos, do lobby ao fim, sem os erros e as travas que o playtest mostrou; sai na versão 3.1, junto da eleição disputada.
>
> **Serve:** N4, N8, N15, N33, N34, N40
>
> **Progresso:** 1/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F157**](#f157) | Velocidade x100 que quase não acelera | — | 🔍 |

<details><summary>Concluído (1 item)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F162**](#f162) | Sinal de partida pausada e destaque da velocidade máxima | — | ✅ |

</details>

### M17 — Eleição disputada

> **Objetivo:** Uma eleição decidida por grupos de eleitores que lembram promessas e traições, com campanha de ações, 2º turno com virada e a aprovação medida pelos grupos; sai na versão 3.1.
>
> **Serve:** N34
>
> **Progresso:** 0/6 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F107**](#f107) | Grupos de eleitores, com apoio e rejeição por partido | — | ⏳ |
| [**F129**](#f129) | Aprovação do governo pelos grupos de eleitores | [F107](#f107) | ⏳ |
| [**F130**](#f130) | Ações de campanha: a eleição deixa de ser só dinheiro | [F107](#f107) | ⏳ |
| [**F151**](#f151) | Segundo turno com disputa | [F130](#f130), [F152](#f152) | ⏳ |
| [**F152**](#f152) | Promessas de campanha cobradas no mandato | [F107](#f107) | ⏳ |
| [**F163**](#f163) | Painel da economia: SELIC e IPCA ao longo da partida | — | ⏳ |

### M18 — Expansão Gestoras

> **Objetivo:** Fundar a própria gestora, abrir capital e disputar as cotas na sala; sai na versão 4.0, depois da 3.2.
>
> **Serve:** N23
>
> **Progresso:** 0/7 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F44**](#f44) | Expansão Gestoras: fundar a gestora e abrir capital | [F101](#f101) | 🔍 |
| [**F55**](#f55) | Modo aquisição hostil | [F103](#f103) | 🔍 |
| [**F101**](#f101) | Carteira separada do jogador | — | 💤 |
| [**F102**](#f102) | Gestoras: emissão de novas cotas e recompra | [F44](#f44) | 🔍 |
| [**F103**](#f103) | Gestoras: troca de gestor pela assembleia | [F44](#f44) | 🔍 |
| [**F104**](#f104) | Gestoras: co-gestores | [F44](#f44) | 🔍 |
| [**F105**](#f105) | Gestoras: rendimentos mensais | [F44](#f44), [F100](#f100) | 🔍 |

### M19 — Governo com conta a fechar e Congresso

> **Objetivo:** Um governo com orçamento e dívida, em que gastar e isentar têm preço, e um Congresso eleito, em que cada partido orienta a própria bancada; sai na versão 3.2.
>
> **Serve:** N34
>
> **Progresso:** 0/4 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F106**](#f106) | Governo & Política: medidas de gasto público | [F128](#f128), [F107](#f107) | ⏳ |
| [**F128**](#f128) | Orçamento do governo, dívida pública e prêmio de risco | [F107](#f107) | ⏳ |
| [**F153**](#f153) | Congresso eleito, com bancadas orientadas pelo líder | [F107](#f107), [F130](#f130) | ⏳ |
| [**F154**](#f154) | Negociar apoio com as bancadas, por emendas | [F153](#f153), [F128](#f128) | ⏳ |

### Sem marco

> **Progresso:** 3/19 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F37**](#f37) | Tema escuro | — | 💤 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | 💤 |
| [**F69**](#f69) | Imprevistos configuráveis e tipos novos | — | 💤 |
| [**F72**](#f72) | Gráficos padronizados sobre o ChartContainer do shadcn | — | 💤 |
| [**F81**](#f81) | CORS restrito à mesma origem | [F6](#f6) | 💤 |
| [**F90**](#f90) | Cenários | — | 🔍 |
| [**F97**](#f97) | SELIC nas mãos do governo | [F106](#f106), [F128](#f128) | 🔍 |
| [**F110**](#f110) | Combinar estratégias | — | 💤 |
| [**F111**](#f111) | Crédito para estratégias e bots | — | 💤 |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 🔍 |
| [**F143**](#f143) | Preparação de cada jogador no lobby | — | 🔍 |
| [**F159**](#f159) | Conquista "Ordem com paciência" | [F44](#f44) | ⏳ |
| [**F164**](#f164) | Mapa do Brasil por região na eleição | [F107](#f107) | 🔍 |
| [**F165**](#f165) | Tela do Tesouro: títulos pelo risco do governo | [F128](#f128) | 🔍 |

<details><summary>Concluído (3 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | ✅ |
| [**F127**](#f127) | Estratégias e bots operam cripto em fração | — | ✅ |
| [**F160**](#f160) | Imprevistos no fim da partida de independência | — | ✅ |

</details>

---

## 1. Atende necessidade

| ID | Resumo | Atende (N#) | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F6** | Link de convite pela internet no lobby | N2 | — | M3 | [F5](#f5) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F37** | Tema escuro | N15 | — | — | — | Médio | Baixo | Médio | Médio | 💤 Registrado, sem prioridade |
| **F56** | Novidades no app | N14 | — | — | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F69** | Imprevistos configuráveis e tipos novos | N23 | — | — | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F72** | Gráficos padronizados sobre o ChartContainer do shadcn | N15 | — | — | — | Médio | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F92** | Noticiário da partida | N31 | D7 | M15 | [F161](#f161) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F101** | Carteira separada do jogador | N23 | D9 | M18 | — | Alto | Alto | Médio | Médio | 💤 Registrado, sem prioridade |
| **F110** | Combinar estratégias | N4 | D8 | — | — | Médio | Médio | Médio | Bom | 💤 Registrado, sem prioridade |
| **F111** | Crédito para estratégias e bots | N4, N33 | D8 | — | — | Baixo | Baixo | Médio | Bom | 💤 Registrado, sem prioridade |
| **F127** | Estratégias e bots operam cripto em fração | N4, N37 | D3 | — | — | Médio | Baixo | Baixo | Regular | ✅ Concluído |
| **F22** | Preço ajustado e proventos | N3, N7 | D1, D3, D7 | M8 | — | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F100** | Proventos na carteira e nas telas | N3, N7 | D1, D3, D7 | M8 | [F22](#f22) | Médio | Médio | Médio | Bom | ⏳ Pendente |
| **F132** | Tópicos de "como se joga" do Como jogar | N25 | — | M14 | — | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F133** | Tópicos de conceitos do Como jogar | N25 | — | M14 | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F139** | Demonstração regravada com o jogo de hoje | N25 | — | M14 | [F44](#f44) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F140** | Docs reorganizada por tipo de leitor | N25 | — | M14 | [F44](#f44) | Alto | Baixo | Alto | Bom | ⏳ Pendente |
| **F141** | README com as features de hoje | N25 | — | M14 | [F139](#f139) | Baixo | Baixo | Alto | Excelente | ⏳ Pendente |
| **F159** | Conquista "Ordem com paciência" | N22 | D1 | — | [F44](#f44) | Baixo | Baixo | Baixo | Bom | ⏳ Pendente |
| **F160** | Imprevistos no fim da partida de independência | N15 | — | — | — | Baixo | Baixo | Baixo | Bom | ✅ Concluído |
| **F120** | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | N15 | — | — | — | Médio | Baixo | Médio | Bom | ✅ Concluído |
| **F162** | Sinal de partida pausada e destaque da velocidade máxima | N15 | — | M16 | — | Baixo | Baixo | Alto | Excelente | ✅ Concluído |
| **F163** | Painel da economia: SELIC e IPCA ao longo da partida | N34 | — | M17 | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F107** | Grupos de eleitores, com apoio e rejeição por partido | N34 | D19 | M17 | — | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F129** | Aprovação do governo pelos grupos de eleitores | N34 | D19 | M17 | [F107](#f107) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F130** | Ações de campanha: a eleição deixa de ser só dinheiro | N34 | D19 | M17 | [F107](#f107) | Alto | Médio | Alto | Bom | ⏳ Pendente |
| **F152** | Promessas de campanha cobradas no mandato | N34 | D19 | M17 | [F107](#f107) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F151** | Segundo turno com disputa | N34 | D19 | M17 | [F130](#f130), [F152](#f152) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F128** | Orçamento do governo, dívida pública e prêmio de risco | N34 | D19, D14 | M19 | [F107](#f107) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F106** | Governo & Política: medidas de gasto público | N34 | D19, D14 | M19 | [F128](#f128), [F107](#f107) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F153** | Congresso eleito, com bancadas orientadas pelo líder | N34 | D19 | M19 | [F107](#f107), [F130](#f130) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F154** | Negociar apoio com as bancadas, por emendas | N34 | D19 | M19 | [F153](#f153), [F128](#f128) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F161** | Jornal da partida: notificações configuráveis por tipo | N31, N32 | — | M15 | — | Alto | Médio | Alto | Bom | ⏳ Pendente |
| **F166** | Pendências da partida: o que pede ação fica à vista até ser resolvido | N15 | — | M15 | — | Médio | Baixo | Alto | Bom | ⏳ Pendente |

<a id="f6"></a>
**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Abrir para a internet exige fechar antes a tomada do host: hoje ser host é ter o nickname do `config.toml`, e com o host desconectado qualquer jogador assume esse nickname por `/api/user/claim` e passa a poder parar a partida e apagar partidas salvas. O app gera um segredo a cada abertura e abre o navegador do host com ele; o servidor reconhece como host só a sessão que apresentou o segredo, e `/api/user/claim` recusa o nickname do host. O endereço de origem não distingue o host, porque num túnel o tráfego de fora costuma chegar ao servidor pela própria máquina. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada; com o host desconectado, nenhum outro jogador consegue virar host.

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

<a id="f69"></a>
**F69 — Imprevistos configuráveis e tipos novos.** Serve N23. O modo viver de renda (F53) já nasce com os tipos de imprevisto num registro, em que cada tipo é uma entrada com nome, múltiplo da despesa mensal, efeito (sai do caixa ou corta o salário do mês seguinte) e peso no sorteio; adicionar um tipo é acrescentar uma entrada, sem mexer no motor, no log nem nas telas. Esta feature expõe esse registro ao host: no lobby, o host edita o valor de cada tipo (por exemplo, o conserto passa de 1 para 2 despesas mensais), liga e desliga tipos e cria tipos próprios com nome, valor e efeito. O sorteio continua saindo da semente da partida, então todos os jogadores seguem recebendo os mesmos imprevistos nos mesmos dias, e a configuração vale para a partida salva.

<a id="f72"></a>
**F72 — Gráficos padronizados sobre o `ChartContainer` do shadcn.** Serve N15; continua a padronização da interface no shadcn, que deixou o `shared/components/ui/chart.tsx` sem nenhum consumidor. Hoje cada gráfico Recharts repete o `ResponsiveContainer`, a cor da grade e um array `{ key, label, color }` de séries (que é o `ChartConfig`), e uns cinco cards de tooltip feitos à mão reimplementam o `ChartTooltipContent`. Plano: (1) antes|depois no canvas de `player-line-chart` e `networth-chart` com `ChartContainer` + `ChartTooltipContent`, para aprovar o visual do tooltip (texto menor, indicador) e decidir se o `ui/chart.tsx` ganha variante; (2) convenção de pasta por gráfico: `<nome>-chart/` com `<nome>-chart.tsx` (componente puro, recebe o dado da API por prop), `chart-data.ts` (`ChartConfig`, tipos de linha e `build*`), `chart-legend.tsx` opcional (a legenda clicável que liga e desliga série continua própria) e `index.ts` exportando só o componente; gráfico sem legenda nem transformação fica arquivo solto `<nome>-chart.tsx`; (3) migrar `player-line-chart/` (`utils.ts` + `series.ts` → `chart-data.ts`, sai o tooltip próprio), `networth-chart`, `allocation-donut` e os gráficos embutidos em `composition-tab.tsx` (`AreaChart`) e `risk-tab.tsx` (`ScatterChart`), extraídos para pastas próprias; o `stock-chart` (lightweight-charts, imperativo) fica fora do `ChartContainer`; (4) a seção Gráficos entra em `docs/docs/desenvolvimento/convencoes-frontend.md`. Gatilho: a próxima rodada de design no canvas, ou o próximo gráfico novo.

<a id="f92"></a>
**F92 — Noticiário da partida.** Serve N31; segue a D7. Um noticiário sintético: as manchetes nascem das séries que a partida já lê, e por isso funcionam igual no futuro gerado, que é onde o jogo passa a maior parte do tempo, e na história real. Sem LLM e sem internet. (1) **Motor genérico:** uma lista de regras, cada uma olhando as séries no tick e, quando dispara, criando uma notícia da sala entregue pelo jornal da partida (F161) a partir de um modelo de texto com algumas variações, para a mesma frase não se repetir. Regra nova é só mais um item da lista. (2) **Macro, as manchetes padrão:** Copom subiu, baixou ou manteve a SELIC, com o tamanho ("Copom sobe a SELIC em 0,5 ponto, para 14,25%"); IPCA do mês acima ou abaixo do anterior; Ibovespa no recorde ou na maior queda do ano. (3) **Empresas:** a mesma lógica para um ativo que sobe ou cai mais de um limite no dia, chega à máxima de 52 semanas ou anuncia provento. O movimento ganha uma causa sintética plausível, sorteada de um banco de causas por setor e direção ("resultado do trimestre acima do esperado", "troca no comando", "vendas de fim de ano fracas" para o varejo). A notícia sai depois do movimento: dá contexto e não dá vantagem. (4) As notícias de um ativo aparecem também na tela dele, como marcadores no gráfico de preço. (5) **Extra, para período real:** marcos históricos curados à mão (crise de 2008, Joesley Day em 2017, Covid em março de 2020), num arquivo de dados com data, manchete e ativos ligados. O futuro gerado sempre começa depois do último dia real, então um marco datado só aparece em período real, e um cenário (F90) pode trazer os seus. Gatilho: depois da caixa de entrada.

<a id="f101"></a>
**F101 — Carteira separada do jogador.** Serve N23; segue a D9. A base da expansão Gestoras (F44): hoje eventos e snapshots pertencem ao jogador (`user_id`), e a gestora precisa de carteira própria. Entra uma tabela `portfolios`, e eventos e snapshots passam a apontar para a carteira; a carteira pessoal de cada jogador é migrada uma a uma, inclusive nas partidas salvas. Nada muda na tela: cada jogador segue com uma carteira só até a F44 existir. Gatilho: a F44 sair da avaliação.

<a id="f110"></a>
**F110 — Combinar estratégias.** Serve N4; segue a D8. O jogador liga mais de uma estratégia ao mesmo tempo, cada uma com uma fatia do patrimônio (ex.: 30% em 100% no CDI e 70% no cruzamento de médias). O motor guarda, por jogador, a lista de estratégias com a fatia de cada uma e a origem de cada posição; cada estratégia recebe um contexto restrito à fatia dela (caixa e posições que ela comprou) e só opera dentro dele. A página de Estratégias passa de um interruptor para uma lista de fatias que somam 100%, e o log de ordens ganha o filtro por estratégia. Gatilho: F8 concluída e o uso pedir mais de uma estratégia.

<a id="f111"></a>
**F111 — Crédito para estratégias e bots.** Serve N4 e N33; segue a D8. O contexto da estratégia ganha a dívida, a nota de risco e a oferta do dia, e as ações ganham pegar empréstimo, amortizar e quitar, que chamam o mesmo serviço da tela de Crédito em nome do jogador. Uma estratégia de exemplo alavancada (ex.: rebalanceamento por meta com 20% emprestado) mostra o uso e entra na lista dos bots. O log da estratégia registra cada contratação e pagamento com o motivo. Gatilho: F8 e F94 concluídas.

<a id="f127"></a>
**F127 — Estratégias e bots operam cripto em fração.** O contexto da estratégia ganhou a cotação com a classe fracionária e `affordable(ticker, dinheiro)`, que usa a mesma conta da boleta (módulo `variable_income/quantity.py`). Comprar e segurar, rebalanceamento, momentum, RSI, médias móveis e rompimento compram em fração (até oito casas) na cripto e em inteiro nas demais; `whole_shares` ganhou a variante fracionária. O texto do registro mostra a quantidade sem zeros à direita.

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

<a id="f139"></a>
**F139 — Demonstração regravada com o jogo de hoje.** Serve N25; retrabalho da F47 e da F48. A última publicação do branch `demo` é de 2026-10-21, e de lá para cá entraram dezenas de features que a demonstração não mostra: modo automático com estratégias e bots na sala, backtest, crédito, governo e eleição, cripto, indicadores técnicos e dicas de análise técnica, presets e linha do tempo do período no lobby, compra a mercado por valor na boleta, a janela "Como jogar". Plano: (1) **Inventário:** cruzar o `git log` de `frontend/src` desde a última publicação com as cenas de `scripts/demo/script.py` (lobby, ações, renda fixa, tempo, estatísticas, fechamento) e as screenshots de `docs/static/demo/screens/`, listando cena por cena o que mudou na tela e o que não tem imagem. (2) **Cenas que mudaram:** o lobby passa pelo preset e pela linha do tempo; a cena de ações usa a compra por valor e mostra o gráfico com um indicador ligado. (3) **Cenas novas:** uma do modo automático (escolher a estratégia e ver o bot negociar) e screenshots de crédito, governo, análise técnica, backtest e "Como jogar"; o banco-base da demo ganha o que essas telas precisarem (um ativo cripto, os indicadores do governo). (4) **Página das imagens:** cada screenshot nova ganha o nome que a página dos docs vai usar, e a lista de screenshots esperadas fica no próprio roteiro, para a reorganização da docs (F140) pedir imagem acrescentando uma linha. (5) `pnpm demo` e `pnpm demo publish`. Gatilho: agora; destrava o README (F141).

<a id="f140"></a>
**F140 — Docs reorganizada por tipo de leitor.** Serve N25; retrabalho da F48. As páginas cresceram junto com as features e misturam três leituras: o passo a passo de quem joga, a referência campo a campo e a explicação de como o simulador calcula (o lobby tem 3 mil palavras e uma seção "Como funciona internamente"; estatísticas e futuro gerado carregam a metodologia inteira no meio do guia). "Novidades" mora dentro de "Como Usar", o "Desenvolvimento" põe o setup lado a lado com notas internas (async × sync, investigação de lentidão, cotações em lote, ordenação de tabelas), e há features sem página para quem joga (modo automático e backtest só aparecem em `desenvolvimento/estrategias.md`; a janela "Como jogar" não aparece em lugar nenhum); a intro e o README ainda dizem "Estratégias automáticas: em breve". Guia de escrita: o Diátaxis (https://diataxis.fr), que separa tutorial (aprender fazendo), guia prático (resolver uma tarefa), referência (consultar) e explicação (entender o porquê). Plano: (1) **Auditoria** página por página contra o app de hoje: o que está desatualizado, o que falta e de qual dos quatro tipos é cada seção, numa tabela entregue ao usuário com a barra lateral proposta antes de mover arquivo. (2) **Barra lateral nova:** "Primeiros passos" (instalação e uma primeira partida curta, apoiada no tour), "Como usar" com uma página curta por tela dizendo o que dá para fazer nela, "Referência" (os campos do lobby, as regras de imposto, os tipos de ordem) e "Como funciona" (a nota da partida, o futuro gerado, o governo, a correlação), para onde a metodologia sai do meio dos guias. "Novidades" vai para a barra superior, ao lado da API. (3) **Desenvolvimento:** o caminho de quem contribui (setup, estrutura de pastas, convenções, contribuindo, versionamento) separado das notas internas, num subgrupo próprio. (4) **Páginas novas:** modo automático e bots na sala, backtest, e a menção à janela "Como jogar" na primeira partida. (5) **Tom:** caixa-alta, negrito em sequência, avisos em excesso e seções "Próximos passos" saem; cada página abre dizendo para que serve a tela, e toda métrica ganha a definição curta e um exemplo numérico. (6) Os links do README, do app (link de ajuda da sala) e entre páginas são conferidos depois de mover, com o build do Docusaurus, que já falha em link quebrado entre páginas (`onBrokenLinks`); os links de fora (README e app) são conferidos à mão. As imagens que faltarem entram no roteiro da demonstração (F139). Gatilho: agora; a auditoria do passo 1 não depende da regravação.

<a id="f141"></a>
**F141 — README com as features de hoje.** Serve N25; retrabalho da F48. O README lista o que o jogo fazia em 2026-10-21 e termina em "Estratégias automáticas: em breve", que já existe. Plano: (1) "O que ele faz" ganha modo automático com estratégias e bots, crédito, governo e eleição, cripto e análise técnica, cada um com uma frase e a imagem da demonstração regravada (F139); as seções com GIF ficam nas quatro ou cinco mais fortes, e o resto vai para "E também", que deixa de ter item "em breve". (2) O parágrafo de abertura e os tipos de partida conferidos contra o lobby de hoje (presets, período). (3) Os links para os docs apontam para as páginas da reorganização (F140) quando ela tiver mudado os caminhos. (4) A intro dos docs repete a mesma lista, e as duas mudam juntas. Gatilho: F139 publicada.

<a id="f159"></a>
**F159 — Conquista "Ordem com paciência".** Serve N22; segue a D1. A 9ª conquista da leva de novas conquistas ficou de fora porque o evento de ordem de ações (`event_equity`) não guarda o tipo da ordem que gerou a execução. Plano: coluna `order_type` em `event_equity` (mercado ou limitada), por migration, com as linhas antigas como mercado; o `Broker` grava o tipo na execução; uma `@metric` em `metrics.py` conta as execuções de ordem limitada do jogador, e a conquista entra no `catalog.py`. Vale qualquer ordem limitada executada, inclusive a que executa na hora porque o preço já estava bom. Fica para a rodada de conquistas feita com o usuário depois da Gestoras, junto com a docs, quando dá para ver todas as features que pedem conquista.

<a id="f160"></a>
**F160 — Imprevistos no fim da partida de independência.** Serve N15. O fim da partida no modo viver de renda ficou sem a frase "passou por N imprevistos", porque o relatório da partida não tinha esse número. Implementado: o backend conta os imprevistos de cada jogador a partir dos eventos de caixa da partida (a demissão tem categoria própria no histórico e fica fora da conta) e manda o total no campo `unexpected_count` de cada jogador do relatório de visão geral; `pnpm openapi` regenerou o tipo. O topo do fim de partida (`match-result/match-hero.tsx`) mostra "Você passou por N imprevistos" na partida de viver de renda com imprevistos ligados (quem só assiste vê a frase do líder). Teste: a contagem por jogador sobre eventos gravados no banco e o campo no ranking.

<a id="f120"></a>
**F120 — Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira.** Serve N15. A Carteira mostra a evolução do patrimônio e a distribuição em dois cards empilhados, pelo design aprovado no canvas. O gráfico traz o patrimônio de hoje e o ganho sobre o aportado no cabeçalho, o período (6M, 1A e Tudo, os períodos maiores que a partida ficam desligados) e dois modos: Ganho, com o aportado em cinza e verde ou vermelho entre as duas linhas, a dívida em faixa abaixo do zero e a meta da corrida; e Por classe, um painel por classe com a própria escala. O tooltip abre do lado que tem espaço e traz o patrimônio por classe, a dívida, o aportado e o ganho; o vazio, o carregando e o erro do histórico têm cada um o seu estado. A distribuição é um anel por classe com o caixa em cinza, a lista das classes, a dívida e o patrimônio no rodapé e os 8 maiores ativos de qualquer classe mais "Outros"; a fatia e a linha da classe se acendem juntas. Os gráficos parecidos (composição das Estatísticas e linha de desempenho) seguem o mesmo visual na migração da F72.

<a id="f162"></a>
**F162 — Sinal de partida pausada e destaque da velocidade máxima.** Serve N15. A eleição e o impeachment pausam a partida para todos, e a única pista era o botão da barra da partida trocar de pausa para play. Implementado: (1) **Motivo da pausa:** o estado da simulação guarda o motivo (pausado pelo host, campanha aberta, resultado do 1º turno, resultado do 2º turno, impeachment), preenchido por quem pausa; o calendário do governo devolve o motivo em vez de um sim/não, e ele chega ao front junto da velocidade (rota de estado e evento de velocidade). (2) **Partida pausada:** a área da data ganha um selo âmbar "Pausado" com o motivo ("Pausado: resultado do 1º turno") e pulsação lenta (desligada para quem pede menos movimento), e o título da aba do navegador ganha "⏸" na frente. (3) **Velocidade máxima:** o segmento do x100 ganha ícone de raio e o tom azul das informações, e a data ganha fundo azul suave enquanto ele está ligado. Os tons saem dos tokens do tema, com variante nova no selo (tamanho de estado e pulsação) e no controle segmentado (nível máximo). Os estados entraram no canvas.

<a id="f163"></a>
**F163 — Painel da economia: SELIC e IPCA ao longo da partida.** Serve N34. A SELIC e o IPCA já existem no jogo, mas só aparecem como o número do dia: ninguém vê a SELIC subindo em resposta à inflação, nem o efeito de uma medida meses depois. O painel mostra as duas séries desde o início da partida, no mesmo gráfico de linha, com a meta de inflação do ano como faixa de referência e as reuniões do Copom marcadas. Cada métrica leva uma descrição curta e uma dica: a SELIC é o juro básico da economia (10% ao ano quer dizer que R$ 100 parados nela viram R$ 110 em um ano); o IPCA é a inflação oficial (5% em 12 meses quer dizer que o que custava R$ 100 custa R$ 105); e o juro real é a SELIC menos o IPCA (10% − 4% = 6%), que mede quanto o dinheiro rende de verdade. É a base para as métricas que chegam com o orçamento (F128): dívida pública ÷ PIB e crescimento da economia entram no mesmo painel quando existirem.

<a id="f107"></a>
**F107 — Grupos de eleitores, com apoio e rejeição por partido.** Serve N34; a fundação do rework do governo, pelo modelo da D19. (1) **Seis grupos já na 3.1,** com um peso inicial no eleitorado: investidores 8%, empreendedores 12%, trabalhadores com carteira 35%, servidores 10%, aposentados 20% e quem depende de auxílio 15%. Cada grupo tem uma posição em cada valor (item 2) e lê três resultados do governo: a inflação contra a meta (pesa em todos, mais em aposentados, auxílio e carteira), a SELIC (alta agrada aposentados, porque a renda fixa rende mais, e irrita empreendedores e trabalhadores, porque o crédito encarece) e o Ibovespa (pesa para investidores e empreendedores). O emprego entra quando o orçamento trouxer o PIB (F128). Na 3.1, servidores e auxílio reagem à inflação, ao juro e ao ganho de capital taxado; as medidas próprias deles chegam com os gastos (F106). (2) **Seis valores,** que são as bandeiras e os eixos do radar: Mercado livre (imposto baixo na bolsa e na renda fixa), Justiça social (taxar o ganho de capital; auxílio na 3.2), Estabilidade (inflação na meta; conta pública na 3.2), Desenvolvimento (isentar setores; obras na 3.2), Proteção ao poupador (renda fixa e LCI/LCA isentas) e Serviço público (reajuste do servidor, que só ganha medida na 3.2). Cada tipo de medida tem uma tabela fixa dos valores que avança ou recua: cortar o imposto do day trade avança Mercado livre e recua Justiça social. (3) **Identidade do partido:** na fundação, o partido escolhe 3 valores; Mercado livre e Justiça social se excluem. Os valores dão a afinidade inicial com cada grupo, que é a proximidade entre o que o grupo quer e o perfil do partido; depois, o radar se move com as promessas, as medidas aprovadas e, na 3.2, os votos da bancada. A régua de promessa de 1 a 5 (`Party.promise`, `PROMISE_BANDS`, a régua em `measures.py`, `promise-ruler.tsx` e `promise-picker.tsx`) sai e dá lugar ao perfil por valor, com migration. Os partidos do computador nascem com 3 valores fixos cada, distintos entre si. (4) **Apoio e rejeição** de cada partido em cada grupo, de 0 a 100. O apoio sobe e desce com a campanha, as promessas e o governo. A rejeição sobe com promessa descumprida e com mês de governo reprovado pelo grupo, e não cai com o tempo: cai só com reparação, que é promessa cumprida ao grupo (cai muito), mês de governo do partido aprovado pelo grupo (cai pouco) e evento de campanha com o grupo (cai pouco, com um limite por campanha; é o caminho da oposição, que na 3.1 não vota nada). (5) **Voto:** em cada grupo, o saldo de cada partido é afinidade + campanha + promessas − rejeição; a fatia de cada partido no grupo é proporcional ao saldo positivo, e uma parte do grupo fica indecisa; o total é a soma dos grupos pelo peso. Substitui o `points` único de `Party` e o `intention` de `election.py`. (6) **Pesquisa com margem de erro:** a pesquisa mensal mostra a intenção de voto por grupo e no total com a margem ("48%, com margem de 3 pontos para mais ou para menos": o número real está entre 45% e 51%), sorteada pela semente da partida. A margem é uma regra da sala, na aba da expansão no lobby, ligada por padrão; desligada, a pesquisa mostra o número exato. **Protótipo:** os pesos dos grupos, a posição de cada grupo em cada valor, a tabela de medida para valor, quanto cada resultado mexe, o tamanho de cada reparação e a fatia de indecisos se calibram no protótipo de calibração dos grupos. **Gatilho:** depois do protótipo, com os números dele. **Canvas:** fundação do partido com a escolha dos 3 valores; radar do perfil do partido; apoio e rejeição do partido em cada grupo; pesquisa por grupo com a margem de erro; regra da margem na aba da expansão no lobby. **Decidido no canvas em 27 e 28/out:** (a) **Quem vê o quê:** apoio e rejeição exatos só do próprio partido (os filiados); dos adversários, só a pesquisa, com margem. O radar e as bandeiras de todos os partidos são públicos, inclusive os do computador. (b) **A margem cresce nos grupos menores,** porque poucos eleitores dão um número mais incerto: ±3 pontos no total, ±5 nos trabalhadores com carteira, ±7 nos aposentados e ±11 nos investidores (±7 quer dizer que 40% de intenção entre os aposentados está, de fato, entre 33% e 47%). (c) **Partido fundado antes da mudança:** o fundador escolhe as 3 bandeiras; até lá, o perfil é neutro. (d) **Eleitorado:** tabela e cartões são um interruptor no mesmo card, com os cartões por padrão. (e) **Onde mora:** a página Eleição tem as abas Corrida (pública: pesquisa, partidos, mandato e ranking) e Campanha do partido (só filiados: ações, eleitorado, histórico e meu partido); quem não é filiado vê só a Corrida, sem a barra de abas.

<a id="f129"></a>
**F129 — Aprovação do governo pelos grupos de eleitores.** Serve N34; troca os fatores soltos de `approval.py` pelo modelo de grupos (D19, F107). (1) **Satisfação por grupo:** todo último dia útil do mês, os resultados (inflação contra a meta, SELIC e Ibovespa, pelo que cada grupo lê) e as medidas vigentes dão um alvo de 0 a 100 para cada grupo, e a satisfação anda um terço do caminho até ele: com alvo 70 e satisfação 40, fica 50, depois 57 e depois 61. O governo bom sobe até o alvo e para ali; o ruim desce até o alvo e para. Cada fator é simétrico em torno de um ponto neutro (o governo ganha tanto quanto perde), o que corrige a aprovação que só caía. (2) **Aprovação** é a média das satisfações, pesada pelo tamanho de cada grupo. (3) **Medidas:** o efeito de uma medida no alvo dos grupos é cheio quando ela passa a valer e cai pela metade em 6 meses, para quem gostou e para quem odiou; o rastro duradouro fica no radar do partido (F107). Substitui o corte que somava sem decair e o `FADE_DAYS` de 180 dias. (4) **Posse:** cada grupo começa satisfeito na proporção em que votou no presidente no turno que decidiu a eleição; quem ganhou com 54% começa perto de 54%. (5) **Memória:** todo mês, grupo com satisfação acima de 50 conta como mês aprovado (sobe o apoio ao partido do presidente e do vice e repara a rejeição, F107), e abaixo de 50 como mês reprovado (tira apoio e soma rejeição). O protótipo pode abrir uma faixa neutra no meio. (6) **Impeachment automático,** até o Congresso de bancadas (F153) passar a votá-lo: nenhum impeachment nos primeiros 12 meses do mandato; depois, cai quem fechar 6 meses seguidos abaixo de 25% (hoje são 3 meses, sem carência, em `approval.py` e `government_book.py:614`). **Protótipo:** o ponto neutro e a força de cada fator por grupo, o efeito de cada medida, o terço de passo, o piso de 25% e o quanto cada mês aprovado ou reprovado mexe em apoio e rejeição. **Gatilho:** depois da F107. **Canvas:** aprovação por grupo no card de aprovação, com o gráfico ao longo do mandato; alvo e direção de cada grupo (subindo ou caindo); aviso de risco de impeachment com a contagem de meses abaixo do piso e o fim da carência. **Decidido no canvas em 27 e 28/out:** (a) **Quem vê o quê:** a satisfação e o alvo de cada grupo são públicos e exatos para todos, porque decidem o impeachment; a contagem dos meses abaixo do piso também é pública no card, e o alerta vermelho e a pendência só aparecem para o presidente. (b) **Carência:** os meses abaixo do piso no 1º ano não contam; a contagem começa no 13º mês, então o impeachment mais cedo é no 18º. (c) **Faixa neutra de 45 a 55** no item 5: satisfação acima de 55 conta mês aprovado, abaixo de 45 conta mês reprovado, e entre as duas o mês não mexe em apoio nem em rejeição (com satisfação 52, o mês passa em branco). (d) **Tela:** aprovação por grupo no card de hoje, com a linha Geral no topo e o grupo selecionável: clicar num grupo troca o gráfico para a aprovação dele.

<a id="f130"></a>
**F130 — Ações de campanha: a eleição deixa de ser só dinheiro.** Serve N34; a campanha passa a ter escolhas e sorte, sobre o modelo de grupos (D19, F107). (1) **Verba mensal de base:** a contribuição de cada filiado continua sendo cobrada no 1º dia útil de cada mês da campanha e vira apoio espalhado por todos os grupos pelo peso de cada um, com retorno decrescente (hoje é a raiz quadrada ÷ 64 num eleitorado de 100). A divisão da verba entre a campanha presidencial e a do Congresso chega com a F153. (2) **Ações avulsas:** qualquer filiado dispara uma ação e paga na hora, do caixa da própria carteira, como na doação; o partido não tem caixa. O preço de cada ação é fixo em reais e segue a chave "corrigir pela inflação" da partida: ligada, sobe pelo IPCA a cada aniversário, como o salário e a meta (o fator sai de `life_budget.py` para um lugar compartilhado). (3) **As quatro ações e o dado:** cada ação rola um d20, sorteado pela semente da partida e mostrado na tela. A tabela base: 1, desastre, perde o dobro do ganho normal; 2 a 6, fraco, metade; 7 a 14, normal; 15 a 19, bom, 1,5 vez; 20, viralizou, 3 vezes. **TV** (cara, todos os grupos pelo peso) rola com vantagem: dois dados, vale o maior, então o desastre sai 1 vez em 400. **Evento com um grupo** (preço médio) rola um d20 normal e também repara um pouco da rejeição do partido naquele grupo, até um limite por campanha (F107). **Comício** (barato, um grupo) rola normal com os extremos dobrados: o desastre perde 4 vezes o ganho e o viral rende 6. **Ataque ao rival** (preço médio, um grupo e um partido rival): na faixa normal, tira do rival o ganho normal naquele grupo; no 1, o tiro sai pela culatra: o grupo passa a rejeitar quem atacou, em 2 vezes o ganho normal (+10 de rejeição no exemplo de ganho normal 5, confirmado em 28/out), e o apoio de quem atacou e o do rival não mudam. Nas outras ações o desastre só tira apoio, sem somar rejeição. (4) **Retorno decrescente:** a mesma ação no mesmo grupo rende metade a cada repetição no mês (100%, 50%, 25%) e zera no mês seguinte; espalhar entre grupos rende mais do que insistir num só. (5) **Duração:** todo apoio de campanha, da verba e das ações, cai pela metade em 3 meses; no dia da eleição pesam sobretudo os últimos meses, o que abre espaço para a virada. Afinidade e promessas não caem com isso. (6) **Partidos do computador:** a verba segue a média dos partidos de jogadores vezes 0,5, 1 ou 1,5 pela dificuldade, gasta por regra: eventos nos grupos de maior afinidade e TV quando a verba cobre o preço; atacam só na dificuldade difícil. (7) **Notícia:** desastre e viral saem no jornal com uma manchete ("Candidato se envolve em polêmica no comício com aposentados"), assim como a abertura da campanha e o fechamento das chapas, quando o jornal (F161) existir. **Protótipo:** o preço de cada ação, o ganho normal de cada uma, a curva da verba de base e se o dado mexe o bastante para virar uma eleição sem decidir sozinho. **Gatilho:** depois da F107. Depois, ações por região com o mapa (F164). **Canvas:** painel de ações da campanha (ação, grupo, rival, preço e quantas vezes já foi feita no mês); rolagem do d20 com o resultado e o efeito no grupo; histórico de ações do partido na campanha; manchete de desastre e de viral no jornal. **Decidido no canvas em 27 e 28/out:** (a) **Quem vê o quê:** só o próprio partido vê as suas ações, o dado e o efeito; os outros percebem pela pesquisa e pelo jornal. Todo ataque sai no jornal, e não só o desastre e o viral; o atacado vê o efeito no histórico, sem o dado. (b) **Retorno decrescente por partido:** o 2º evento com aposentados no mês rende 50%, seja de qual filiado for. (c) **Sem limite de ações:** o preço e o retorno decrescente bastam. As ações valem até a véspera do 1º turno; entre os turnos, valem as regras do 2º turno (F151). (d) **Reparação:** o desastre não repara rejeição; as outras faixas reparam. (e) **Ataque:** fraco, normal, bom e viral tiram do rival 0,5, 1, 1,5 e 3 vezes o ganho normal (2,5, 5, 7,5 e 15 no exemplo de ganho normal 5); os valores em pontos seguem exemplos até o protótipo. (f) **Tela:** as ações moram na aba Campanha do partido da página Eleição, em passos que mudam com a ação (TV 1 etapa, comício 2, ataque 3), com o resumo do dado sempre à vista. O diálogo do dado mostra a tabela de faixas antes de pagar, sem a trilha de 1 a 20, e o número tirado aparece dentro do hexágono.

<a id="f152"></a>
**F152 — Promessas de campanha cobradas no mandato.** Serve N34; substitui a régua de promessa por faixas, pelo modelo de grupos (D19, F107). (1) **O que se promete:** a chapa promete até 3 medidas da lista das que o governo pode propor: as de imposto, que já existem, e as de gasto quando a F106 chegar, na 3.2. Medida com valor leva um alvo ("day trade a 10%", hoje em 20%); medida de setor é sim ou não ("isentar o setor elétrico"). A promessa aparece no jornal ("Fulano prometeu isentar o setor elétrico"), na pesquisa, no resultado e na tela do governo, e move o radar do partido nos valores da medida. (2) **Na campanha:** a promessa rende apoio nos grupos que querem a medida e tira dos que não querem, na medida da posição de cada grupo no valor; quanto maior o passo prometido, mais rende e mais pesa se falhar. Num grupo, ela rende multiplicada por (1 − rejeição ÷ 100): com 40 de rejeição entre os aposentados, a promessa feita a eles rende 60%. Quem traiu promete de novo e rende menos onde traiu. (3) **No mandato:** no fim do mandato vale o que estiver em vigor. Chegou ao alvo, cumprida; parte do caminho, cumprida na proporção (de 20% para 15% numa promessa de 10% é metade); nada, descumprida. Cumprida sobe a lealdade e repara a rejeição dos grupos que queriam a medida (F107); descumprida soma rejeição neles, na mesma proporção. A tela do governo mostra cada promessa como cumprida, em andamento (com a fração do caminho) ou descumprida. (4) **Impeachment:** o vice que assume herda as promessas da chapa e é cobrado no fim do mandato; sem vice, o mandato acaba no impeachment e o que não foi cumprido vira rejeição. A cobrança fica sempre com o partido da chapa. (5) Os partidos do computador prometem por regra, com medidas dos próprios valores. **Protótipo:** quanto a promessa rende por grupo e por tamanho do passo, e quanto vale a lealdade e a rejeição de uma promessa cumprida ou quebrada. **Gatilho:** depois da F107. **Canvas:** escolha das promessas na chapa (medida, alvo e o rendimento esperado em cada grupo, já descontado pela rejeição); promessas da chapa na pesquisa e no resultado; promessas na tela do governo com o estado de cada uma; balanço do fim do mandato, com o que cada promessa deixou de lealdade e de rejeição em cada grupo. **Decidido no canvas em 27/out:** (a) **Desde o anúncio:** a promessa rende desde o anúncio. Depois dele, trocar, retirar ou baixar o alvo soma rejeição em quem queria; acrescentar até 3 e subir o alvo não custam. (b) **Cumprida soma afinidade,** a parte do apoio que não cai: é o que o item 3 chama de lealdade, sem nenhum número novo por grupo. (c) **Direção contrária pesa mais que não fazer nada:** de 20% para 25% numa promessa de 10% o governo andou meio caminho para trás (−50% do caminho), e a rejeição sai 1,5 vez a cheia. (d) **Reeleição:** com as chapas fechadas, metade do efeito do que estiver em vigor já pesa no voto; o balanço de 31 dez fecha a outra metade. (e) **Quem perdeu:** as promessas de quem perdeu ficam no histórico do partido, sem efeito. (f) **Tela:** a escolha é um diálogo, uma promessa por vez.

<a id="f151"></a>
**F151 — Segundo turno com disputa.** Serve N34. No playtest, o 2º turno repetiu o 1º sem chance de virada: entre os turnos não havia cobrança, os votos dos eliminados iam inteiros para o finalista de promessa mais próxima (`runoff` em `election.py`) e o único movimento era a doação de quem foi eliminado. (1) **Transferência grupo a grupo:** no dia seguinte ao 1º turno, os votos de cada eliminado se dividem, em cada grupo, pela afinidade do grupo com cada finalista (D19, F107). Uma parte fica indecisa, e essa parte cresce quando o grupo gosta pouco dos dois: aposentados com afinidade baixa com ambos deixam metade dos votos do eliminado indecisa, e investidores próximos de um finalista transferem 90%. (2) **Declaração de apoio:** o líder do partido eliminado declara apoio a um finalista ou neutralidade. Os grupos que confiam no eliminado (afinidade alta e rejeição baixa) seguem a indicação com parte dos votos indecisos. O partido do computador eliminado declara por regra, para o finalista de valores mais próximos. A declaração sai no jornal. A doação a um finalista continua. (3) **Campanha de 2º turno:** as ações avulsas (F130) valem entre os turnos, cada finalista pode fazer uma contribuição única de 2º turno, paga na hora e convertida como a verba mensal, e pode acrescentar 1 promessa (até 4 no total, F152); retirar promessa não é permitido. (4) **No dia do 2º turno,** os indecisos que sobraram se abstêm, e o vencedor sai dos votos válidos. A duração de 21 dias fica; volta à mesa se, jogando, ficar curta para a virada. O debate sorteado fica de fora. **Protótipo:** a curva da fração indecisa pela afinidade, quanto do apoio declarado os grupos seguem e se uma virada acontece numa fração razoável das eleições. **Gatilho:** depois da F130 e da F152. **Canvas:** resultado do 1º turno com a transferência por grupo (quanto foi para cada finalista e quanto ficou indeciso); painel do 2º turno com os indecisos por grupo, as ações, a contribuição única e a promessa extra; declaração de apoio do eliminado; resultado do 2º turno com a abstenção. **Decidido no canvas em 27 e 28/out:** (a) **Quem vê o quê:** a transferência grupo a grupo é pública como pesquisa, com a margem de cada grupo; o número exato só sai no resultado do 2º turno. (b) **Declaração:** o líder do eliminado declara uma vez, até a véspera, sem volta; sem declarar, conta como neutro. Quanto mais tarde, menos indecisos sobram para seguir. (c) **Contribuição de 2º turno:** uma por filiado do finalista; a soma vira apoio pela raiz, como a verba mensal (dobrar o dinheiro não dobra o apoio). (d) **Ações no 2º turno:** o ganho de uma ação sai primeiro dos indecisos do grupo; quando eles acabam, tira do rival. No ataque, o que o rival perde vira indeciso no grupo: os dois disputam, e quem sobrar no dia do 2º turno não vota. A repetição de ação no grupo zera no dia seguinte ao 1º turno, e tudo volta a render 100%. (e) **Pesquisa semanal entre os turnos,** porque a mensal só sairia depois da votação. (f) **Tela:** o 2º turno é um estado da página Eleição, nas abas Corrida e Campanha do partido, e não tem painel próprio (no lugar do painel do 2º turno da linha Canvas).

<a id="f128"></a>
**F128 — Orçamento do governo, dívida pública e prêmio de risco.** Serve N34. **O problema:** isentar imposto só soma aprovação e não custa nada, porque o governo não tem conta a fechar; nenhum partido tem motivo para ser austero ou gastador. (1) **Receita pela alíquota:** os impostos da partida só incidem sobre as operações dos jogadores, pequenas demais perto de um país, então a receita é modelada e o IR dos jogadores não entra nela. Cada imposto do jogo (ganho comum de ações, day trade e FII, isenção das vendas até o teto, tabela da renda fixa, LCI e LCA, regras de setor) tem uma base em % do PIB, e a receita dele varia com a alíquota vigente contra a padrão, com uma elasticidade: cortar o day trade pela metade tira um pouco menos que metade da receita dele, porque as pessoas passam a operar mais. O resto da arrecadação do país entra como receita fixa em % do PIB. A tela da proposta mostra a estimativa do efeito antes de propor ("−0,08% do PIB por ano"). (2) **Gasto e resultado:** o governo tem um gasto base em % do PIB, e as medidas de gasto (F106) somam a ele. Receita menos gasto é o resultado do mês; o déficit vira dívida, e a dívida paga juro pela SELIC mais o prêmio. (3) **Conta inicial, regra da sala** na aba da expansão no lobby: "jogável" (padrão), com a dívida bruta real do ano de início e receita igual ao gasto, ou "realista", com a dívida e o déficit reais do ano. As duas saem de tabelas anuais no molde de `INFLATION_TARGETS` em `approval.py`; fora da tabela vale o último ano. (4) **PIB e emprego:** o crescimento é uma tendência de 2% ao ano, menos um tanto por ponto de juro real (a SELIC menos a inflação: SELIC de 13% com inflação de 5% dá juro real de 8%) acima de um juro neutro, mais um tanto pela alta da bolsa em 12 meses. O desemprego segue o crescimento pela lei de Okun: cada ponto de crescimento acima da tendência baixa o desemprego em cerca de meio ponto. Funciona igual na história real e no futuro gerado, porque SELIC, IPCA e Ibovespa existem nos dois (D14). O emprego passa a ser um resultado que os grupos leem (F107): pesa mais em trabalhadores com carteira e quem depende de auxílio. (5) **Dívida ÷ PIB e prêmio de risco:** dívida de 80% do PIB quer dizer que o governo deve 80% de tudo o que o país produz num ano. Até 50%, nenhum prêmio; acima, a curva acelera: cerca de 1 ponto com 60%, 2 com 80% e 4 com 100%. O prêmio soma à taxa dos títulos novos do Tesouro na renda fixa (o spread do IPCA+, a taxa do prefixado e o spread do Selic em `tesouro_factory.py`). Os jogadores não financiam o governo de fato: as compras deles são pequenas demais perto da economia. (6) **Grupos:** a dívida alta e o título caro irritam investidores e quem tem o valor Estabilidade (D19), e o corte de gasto irrita quem depende dele, de modo que o austero e o gastador passam a ter eleitorado próprio. **Como funciona hoje:** a política de impostos padrão é a de antes da expansão (15% no ganho comum de ações, 20% no day trade e no FII, isenção das vendas de ações até R$ 20 mil no mês, tabela da renda fixa de 22,5% a 15% por prazo, LCI e LCA isentas); o presidente propõe medidas gerais e de setor, que valem 90 dias depois de aprovadas. **Protótipo:** as bases e as elasticidades de cada imposto, a receita fixa, os coeficientes do crescimento e da lei de Okun e os pontos da curva do prêmio. **Gatilho:** depois da F107. **Canvas:** orçamento do governo (receita, gasto, resultado do mês e dívida ÷ PIB, com descrição e dica em cada número); estimativa do efeito no orçamento na proposta da medida; prêmio de risco nos títulos do Tesouro na renda fixa, com a dica de por que a taxa subiu; regra da conta inicial na aba da expansão no lobby; PIB, crescimento e desemprego no painel da economia (F163).

<a id="f106"></a>
**F106 — Governo & Política: medidas de gasto público.** Serve N34; a segunda alavanca do governo, ao lado dos impostos. (1) **Quatro medidas com valor,** que sobem ou descem como os impostos (cortar gasto também é medida, a do governo austero), seguem a mesma fila, votação e prazo de 90 dias e entram como gasto no orçamento (F128): **auxílio** (em % do PIB; agrada quem depende dele e avança Justiça social), **reajuste dos servidores** (em %; agrada servidores e avança Serviço público), **reajuste das aposentadorias** acima da inflação (em %; agrada aposentados) e **obras** (em % do PIB; agrada empreendedores e carteira, avança Desenvolvimento e soma ao crescimento do PIB). Cada grupo passa a ter ao menos uma medida para pedir, e todas entram na lista das promessas (F152). (2) **Efeito na inflação:** cada medida soma pontos ao IPCA por cima da série; as obras somam menos. O efeito segue o mecanismo do impacto de preço das ordens grandes: o valor do dia é o da série vezes (1 + a soma dos efeitos ativos), cada efeito nasce de um evento, chega depois de um atraso, vale cheio e decai com o tempo, e tudo se reconstrói a partir dos eventos numa retomada. (3) **Reação da economia** pelos coeficientes da D14: a SELIC reage com 1,5 vez a inflação (com o Banco Central autônomo), e a bolsa cai 2,9% no trimestre por ponto de alta da SELIC, ativo a ativo pelo beta. (4) **Vale em toda a partida:** na história real e no futuro gerado, o IPCA e a SELIC ganham o efeito; a série guardada não muda, e a partida passa a ser "o que teria acontecido se". **Protótipo:** o custo de cada medida, quanto agrada ou irrita cada grupo, quantos pontos de IPCA soma, o atraso e a velocidade da queda do efeito. **Gatilho:** depois da F128. **Canvas:** proposta de medida de gasto (valor, efeito no orçamento, grupos que gostam e que odeiam, inflação esperada); efeitos ativos das medidas no painel da economia, com a parte de cada uma na inflação e na SELIC.

<a id="f153"></a>
**F153 — Congresso eleito, com bancadas orientadas pelo líder.** Serve N34. Hoje o Congresso é um sorteio: cada medida passa se um número de 0 a 100 sai abaixo da aprovação (`congress.py`). (1) **Casa de 101 cadeiras,** uma só (sem Senado), eleita junto com o presidente e mostrada como um hemiciclo de bolinhas na cor de cada partido. A medida passa com 51 votos Sim. (2) **Eleição própria:** os votos de Congresso saem do mesmo modelo de grupos (D19, F107), pesando mais a afinidade de longo prazo e o histórico do partido do que a campanha, e com a verba de Congresso que o partido separou da presidencial: a contribuição mensal ganha a divisão entre as duas campanhas (F130). Os votos viram cadeiras de forma proporcional, com barreira de 5% (quem fica abaixo não elege ninguém), pelo método D'Hondt: os votos de cada partido são divididos por 1, 2, 3 e assim por diante, e as maiores divisões levam as cadeiras; quem tem 30% dos votos leva cerca de 31 cadeiras. Um partido com histórico bom e pouco dinheiro elege bancada sem ganhar a presidência, e o presidente pode governar com a oposição em maioria. (3) **Partidos do computador permanentes:** os três existem sempre na casa, com perfil próprio por grupo e valores fixos, mesmo quando não lançam candidato; um deles faz o papel do "centrão", que vende apoio (F154). (4) **Líder orienta a bancada:** o líder é o fundador (se ele sair, o filiado mais antigo). Em cada medida, ele define o voto da bancada (Sim ou Não); uma orientação padrão por valor vale quando ele não escolhe, e a votação sem orientação vira pendência no jornal (F161). Quem perdeu a presidência continua jogando. Os partidos do computador orientam pelos próprios valores. (5) **Desobediência:** quanto mais a medida contraria os grupos que votaram no partido, mais deputados votam contra a orientação, até um terço da bancada, num sorteio pela semente da partida. (6) **Impeachment votado:** a régua da F129 (sem impeachment nos primeiros 12 meses, depois 6 meses seguidos abaixo de 25%) deixa de derrubar sozinha e passa a abrir o pedido; a casa vota, e o presidente cai com 68 das 101 cadeiras, dois terços como no Brasil. Depois do impeachment, assume o vice; sem vice, governa o partido do computador com mais cadeiras, propondo medidas pelos grupos dele. Filiados como deputados individuais, com salário e eleição por estado, ficam para depois, se a bancada se mostrar divertida. **Protótipo:** quanto a eleição de Congresso pesa histórico contra campanha, e a curva da desobediência. **Gatilho:** depois da F107 e da F130. **Canvas:** hemiciclo da casa, com a maioria e os dois terços marcados; resultado da eleição do Congresso (cadeiras de cada partido, ganhas e perdidas); votação de uma medida, com a orientação de cada bancada, o placar e quem desobedeceu; orientação padrão por valor na tela do partido; divisão da verba entre presidência e Congresso no diálogo de contribuição; votação do impeachment.

<a id="f154"></a>
**F154 — Negociar apoio com as bancadas, por emendas.** Serve N34. Com o Congresso de bancadas (F153), o governo monta maioria pagando emendas: verba do orçamento (F128) destinada à base do partido aliado, que entra como gasto e agrada os grupos desse partido (D19). (1) **Apoio por prazo:** o aliado entra na base por 6 meses, renováveis, e o líder dele orienta Sim em tudo o que o governo propuser, em troca de uma emenda mensal. A desobediência da bancada (F153) continua valendo. (2) **Preço por cadeira:** cada cadeira custa uma fração fixa do PIB por mês, e o centrão cobra 1,5 vez isso. O partido de jogador recebe a proposta num aviso de aceitar ou recusar, no mesmo molde do convite de vice (F145), com o valor e o prazo. O partido do computador responde pelo perfil: o centrão aceita quase sempre, e os outros só quando os valores do governo combinam com os deles. (3) **Quebra:** se o governo para de pagar, os grupos do aliado, que recebiam a emenda, somam rejeição ao partido do presidente; se o aliado orienta Não durante o prazo, os grupos do governo somam rejeição ao aliado. Nos dois casos o acordo acaba e sai no jornal (F161). Como a rejeição só cai com reparação (F107), trair a base cobra na eleição seguinte. **Protótipo:** o preço por cadeira e o tamanho da rejeição na quebra. **Gatilho:** depois da F153 e da F128. **Canvas:** proposta de acordo do governo (partido, prazo, preço e as cadeiras que somam à base, com a maioria marcada); aviso de proposta para o partido de jogador; a base do governo no hemiciclo e as emendas no orçamento; aviso e manchete de quebra de acordo.

<a id="f161"></a>
**F161 — Jornal da partida: notificações configuráveis por tipo.** Serve N31 e N32; retrabalho da F91. A caixa de entrada saiu como um e-mail (envelope com contagem de não lidas, painel lateral, marca de lida), e não é o que o jogo pede: com o tempo correndo, notícia é passageira. O modelo vem do OpenTTD (notícia grande em janela, pequena na faixa, e cada tipo configurável) e do Victoria 3 (cada tipo escolhe se aparece, fica só no registro ou some, e só o que é global pausa). Decidido no canvas em 27/out: (1) **Régua:** no jornal entra só o que pareceria notícia num jornal de verdade: economia, empresas, política (calendário da eleição, resultado, posse, medidas propostas, votadas e em vigor, vida dos partidos) e marcos históricos. O que é do jogador continua toast, com liga/desliga por tipo: ordens (manuais, a limite e do automático), jogador entrou ou saiu, parcelas pagas, empréstimo quitado, nota de risco, imprevisto, resposta do vice e resumo do mês. A resposta a um clique é toast e não se configura. O que pede ação é pendência, feature própria (F166). (2) **Como aparece**, escolha de cada jogador: o cartão do jornal num canto (embaixo à esquerda, o padrão; embaixo à direita; em cima à esquerda) ou a faixa de manchetes abaixo da topbar; os toasts ficam embaixo, no lado oposto (com a faixa, embaixo à direita). Em cima à direita fica de fora, porque divide a borda com a aba do tutorial. Várias manchetes no mesmo pregão: sobe a mais importante, com "+N neste pregão", sem fila. (3) **Configuração por tipo**, num registro único de tipos (categoria, texto, padrão): Janela, Jornal, Só no histórico ou Desligado. Janela abre a manchete no centro sem pausar e sem escurecer o fundo, fecha sozinha em 8 s, no máximo uma por pregão; no padrão fica para poucos tipos, e serve a quem quer ênfase numa categoria. Resultado de turno e impeachment ficam presos na janela com pausa. Em empresas, o filtro "só ativos da minha carteira". (4) **Histórico** da partida inteira, salvo com ela, por data, sem "lida" e sem contagem, com busca, filtro por seção e "só minha carteira". Ele mora numa página própria, com o item Jornal no menu lateral, sob Mercado; "Abrir o jornal" no cartão e o selo recolhido levam para ela. (5) **A caixa de entrada sai:** resumo do mês e retrospectiva viram toast com Abrir, e os passados ficam numa aba Resumos em Estatísticas. (6) **Multiplayer:** a configuração é de cada jogador e nunca pausa a sala. (7) **Ficam como estão,** fora do jornal e da configuração: aviso de que o host removeu o jogador, erro no servidor, conquista e aviso do backtest. O histórico em página própria foi escolhido no canvas em 28/out.

<a id="f166"></a>
**F166 — Pendências da partida.** Separada do jornal da partida (F161) em 27/out: notícia é passageira, e o que pede ação fica à vista até ser resolvido, como os alertas do Victoria 3. Tipos: parcela em atraso, caixa que não cobre a próxima parcela, caixa negativo, estratégia desligada por erro, risco de impeachment (só o presidente), convite de vice e campanha aberta sem filiação; a votação sem orientação do líder (F153) entra quando existir. Cada uma traz a ação que a resolve e some quando a condição acaba. Ao nascer, sobe um toast uma vez; depois ela fica no lugar dela. Campanha aberta e convite de vice deixam de abrir diálogo sozinhos: clicar na pendência abre o mesmo diálogo de hoje. Pendência não se desliga. Lugar na tela, escolhido no canvas em 28/out (janela ao lado): Pendências é uma linha no topo do menu lateral, com a contagem (vermelha se alguma é grave); clicar abre a lista numa janela ao lado, com a ação de cada pendência, que fecha fora dela ou no Esc, sem pausar o jogo. As graves vêm primeiro, e a janela rola por dentro se a lista passar da tela. A topbar fica fora, por falta de espaço no pior caso.

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F60** | Modo servidor dedicado (--headless) | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F81** | CORS restrito à mesma origem | — | — | [F6](#f6) | Baixo | Médio | Baixo | Médio | 💤 Registrado, sem prioridade |

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

<a id="f60"></a>
**F60 — Modo servidor dedicado (`--headless`).** O mesmo executável, sem o navegador: para rodar numa VPS ou num PC ligado direto, sem ninguém jogando nele. `--headless` na linha de comando, ou `[server] headless = true` no `config.toml`, pula o `webbrowser.open` do `main.py`, que hoje roda sempre que o app é o executável, e imprime no terminal os endereços para entrar (o da rede local e, com a F6, o do túnel). O administrador é quem entra com o apelido de `[host] nickname`, que é como o host é definido hoje (`routes/simulation.py`). Como a recuperação de login é por apelido, num servidor exposto à internet qualquer um que digite esse apelido viraria o host; por isso, no modo servidor, o `config.toml` ganha `[host] pin`, e o login com o apelido do host só passa com ele. Serve a quem quer deixar uma sala aberta para os amigos entrarem quando quiserem, sem depender de o host estar com o computador ligado jogando.

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
| **F44** | Expansão Gestoras: fundar a gestora e abrir capital | Serve N23; falta o protótipo do preço da cota com o formador sintético | M18 | [F101](#f101) | 🔍 Em avaliação |
| **F55** | Modo aquisição hostil | Serve N23; faltam parte mínima no mercado e o destino do incorporado | M18 | [F103](#f103) | 🔍 Em avaliação |
| **F90** | Cenários | Serve N22; um preset com objetivo | — | — | 🔍 Em avaliação |
| **F93** | Rumores antecipados | N31; opção da partida | M15 | [F92](#f92) | 🔍 Em avaliação |
| **F97** | SELIC nas mãos do governo | N34; opção, depois do rework do governo | — | [F106](#f106), [F128](#f128) | 🔍 Em avaliação |
| **F102** | Gestoras: emissão de novas cotas e recompra | Serve N23; falta o prazo da preferência e o preço da emissão | M18 | [F44](#f44) | 🔍 Em avaliação |
| **F103** | Gestoras: troca de gestor pela assembleia | Serve N23; falta como a assembleia escolhe o novo gestor | M18 | [F44](#f44) | 🔍 Em avaliação |
| **F104** | Gestoras: co-gestores | Serve N23; falta a divisão das taxas | M18 | [F44](#f44) | 🔍 Em avaliação |
| **F105** | Gestoras: rendimentos mensais | Serve N23; falta a parte do lucro distribuída | M18 | [F44](#f44), [F100](#f100) | 🔍 Em avaliação |
| **F123** | Redesenhar o aviso de conquista desbloqueada | Serve N22 e N15; falta escolher o desenho do aviso no canvas; liga à F122 | — | — | 🔍 Em avaliação |
| **F131** | Catálogo de padrões de vela | Serve N19; tópico do Como jogar com cada padrão animado | M11 | — | 🔍 Em avaliação |
| **F143** | Preparação de cada jogador no lobby | Serve N39 e N34; partido salvo no perfil escolhido; falta o resto | — | — | 🔍 Em avaliação |
| **F157** | Velocidade x100 que quase não acelera | Serve N40 e N24; falta medir o tick no x100 com o painel de desempenho | M16 | — | 🔍 Em avaliação |
| **F158** | Animações do Como jogar revistas | Serve N25; falta o visual numa rodada no canvas | M14 | — | 🔍 Em avaliação |
| **F164** | Mapa do Brasil por região na eleição | Serve N34; depois do rework; falta a mistura de grupos por região | — | [F107](#f107) | 🔍 Em avaliação |
| **F165** | Tela do Tesouro: títulos pelo risco do governo | Serve N34; depois do orçamento; falta o desenho | — | [F128](#f128) | 🔍 Em avaliação |

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
**F97 — SELIC nas mãos do governo.** Ligado à N34; uma opção da expansão "Governo & Política" (F95), no lugar do Banco Central autônomo, que continua sendo o padrão. (1) **Ritmo do Copom:** o governo decide a SELIC em reuniões a cada 45 dias, como o Copom, que se reúne 8 vezes por ano desde 2006; entre reuniões ela não muda. (2) **Teto por reunião, pelo que aconteceu de verdade.** Das 150 mudanças da meta da SELIC entre 2000 e outubro de 2026 (série do Banco Central): 34 foram de 0,25 ponto, 67 de 0,5, 19 de 0,75, 19 de 1, 7 de 1,5, uma de 2, uma de 2,5 (cortes de 2003) e duas de 3 (as altas da crise de 2002); desde 2006, nunca passou de 1,5. O teto acompanha isso: até 0,75 ponto por reunião em tempo normal (80% das mudanças reais), 1,5 com a inflação bem acima da meta, como em 2021 e 2022, e 3 só com a inflação explodindo, como em 2002. (3) **O preço vem do juro real,** a SELIC menos a inflação (SELIC de 10% com IPCA de 4% dá juro real de 6%). Juro real negativo ou perto de zero aquece a economia na hora e acelera a inflação meses depois, pelo mesmo mecanismo de efeito por cima das séries da F106: aposentados e quem vive de investimento perdem apoio (D19), e o prêmio de risco dos títulos sobe (F128). Juro real muito alto, acima de uns 7%, esfria o crescimento e derruba a bolsa pelo coeficiente da D14, e quem trabalha e empreende perde apoio. Falta definir: quanto a inflação reage à SELIC e com quanto atraso (medir no histórico, como a D14 mediu a reação da SELIC à inflação), os limites de juro real que começam a cobrar e os de inflação que liberam cada degrau do teto. Fica para depois do rework do governo da versão 3.1.

<a id="f102"></a>
**F102 — Gestoras: emissão de novas cotas e recompra.** Serve N23; amplia a expansão Gestoras (F44). (1) **Emissão:** depois da oferta pública, o gestor emite cotas novas com preferência para quem já é cotista, na proporção das cotas de cada um, para ninguém ser diluído sem escolher; o dinheiro entra na gestora. (2) **Recompra:** a gestora compra as próprias cotas no livro com o caixa dela; vale quando a cota está com deságio (pagar R$ 80 por R$ 100 de patrimônio valoriza a cota de quem fica) e é a defesa contra a troca de gestor (F103). Falta decidir: quanto tempo dura a preferência, e se o preço da emissão é o patrimônio por cota ou o preço de mercado (com ágio, emitir a mercado traz mais dinheiro por cota).

<a id="f103"></a>
**F103 — Gestoras: troca de gestor pela assembleia.** Serve N23; amplia a expansão Gestoras (F44). Quem juntar mais da metade das cotas troca o gestor pela assembleia de cotistas e passa a operar a carteira e a receber as taxas. É o custo de abrir capital, e a defesa é a recompra (F102) e comprar cotas com as taxas recebidas. O modo aquisição hostil (F55) se apoia nesta regra. Falta decidir: se a troca é automática ao passar de metade ou uma votação convocada; se o novo gestor é sempre quem juntou as cotas ou alguém que ele indica; e o que o gestor afastado mantém além das próprias cotas.

<a id="f104"></a>
**F104 — Gestoras: co-gestores.** Serve N23; amplia a expansão Gestoras (F44). A gestora pode ter mais de um gestor, por convite: eles operam a mesma carteira pelo modo na topbar e dividem as taxas, como sócios da mesma empresa. Com a expansão Governo & Política, o co-gestor é quem assume a gestora quando o gestor vira presidente (F95). Falta decidir: como as taxas se dividem (em partes iguais ou pelas cotas de cada um) e quem convida ou tira um co-gestor.

<a id="f105"></a>
**F105 — Gestoras: rendimentos mensais.** Serve N23; amplia a expansão Gestoras (F44) e espera os proventos (F100), porque hoje nem os FIIs importados pagam rendimento. Como um FII, a gestora distribui todo mês parte do lucro aos cotistas, em dinheiro no caixa de cada um, e a cota deixa de render só por valorização. Falta decidir: a parte do lucro distribuída (os FIIs reais distribuem pelo menos 95% do lucro do semestre), se ela é fixa ou escolha do gestor, e o que conta como lucro (só o realizado ou também a valorização da carteira).

<a id="f123"></a>
**F123 — Redesenhar o aviso de conquista desbloqueada.** Hoje o aviso (`achievement-toast.tsx`, aberto com `toast.custom` do sonner) é um cartão escuro de 380 px com uma faixa amarela de 3 px à esquerda, o ícone, o rótulo amarelo em maiúsculas ("Conquista desbloqueada"), o nome e a descrição; quando várias saem no mesmo dia, vira uma lista com "Ver todas". O incômodo existe, mas não está claro de onde vem: pode ser a faixa amarela do canto, o rótulo, o peso do cartão escuro, o tamanho ou a falta de movimento. Falta escolher o desenho depois de ver variantes lado a lado no canvas: (a) o cartão atual sem a faixa, com o ícone em destaque; (b) um cartão claro, no tema do app; (c) um formato compacto, com o ícone e o nome numa linha só e a descrição ao passar o mouse; (d) um formato de "selo" com a categoria e a cor dela. A rodada cobre os estados uma conquista, várias no mesmo dia, secreta revelada e conquista com barra de progresso completa, e decide a posição na tela e a entrada e saída. Sai daqui para Pendente com a variante escolhida.

<a id="f131"></a>
**F131 — Catálogo de padrões de vela.** Serve N19. Um tópico do "Como jogar" (F126) que lista todos os padrões que as dicas de análise técnica (F96) reconhecem, cada um com o ícone e o nome que aparecem no gráfico (o martelo com o símbolo dele, por exemplo). Navegar pelo catálogo mostra um padrão por vez, com a animação das velas se formando no molde dos roteiros do tutorial, o que o padrão costuma sugerir e o lembrete de que padrão não é garantia. Em aberto: se o catálogo é um tópico do tutorial ou uma tela própria, e se o card do padrão no gráfico ganha um "ver no catálogo". Gatilho: com as dicas de análise técnica e a janela "Como jogar" prontas.

<a id="f143"></a>
**F143 — Preparação de cada jogador no lobby.** Serve N39 e N34. Hoje o lobby prepara só a partida, pelas mãos do host; o que é de cada jogador só se faz depois do início, com o relógio andando, e os primeiros dias viram configuração. A ideia: um painel "Minha preparação" para cada jogador no lobby, salvo junto com o "Pronto" e aplicado no 1º dia da partida. **Escolhido:** o **partido** entra, com a expansão Governo & Política ligada: fundar (nome, sigla, cor e bandeiras da F107) ou pedir filiação ao partido de outro jogador, valendo na abertura da campanha, com o convite de vice (F145) no mesmo painel. O partido fica salvo no perfil do jogador como "Meu partido", no molde dos presets do host: nome, sigla, cor, bandeiras e os convites de sempre, aplicados no lobby sem refazer nada. A identidade é a única coisa salva; o histórico do partido (D19) recomeça a cada partida. Outros candidatos, do mais ao menos valioso: (2) **contribuição de campanha** do primeiro mês; (3) **modo automático:** a estratégia escolhida e ligada desde o 1º dia; (4) **ordens de abertura:** uma lista de compras executada no primeiro pregão; (5) **meta pessoal** no modo corrida à meta, se ela passar a ser de cada jogador. Falta definir: quais dos outros candidatos entram, e o que acontece numa partida salva com a preparação de quem não voltou.

<a id="f157"></a>
**F157 — Velocidade x100 que quase não acelera.** Serve N40 e N24. No playtest, o x100 andou quase como o x1, ou até mais lento. O loop dorme `1 / velocidade` segundos depois de cada tick (`simulation_loop.py:132` a `:156`): no x1 o dia leva o tick mais 1 s, no x100 o tick mais 10 ms. Quando o tick sozinho custa perto de 1 s (a medição da D4 deu de 0,6 a 0,95 s com carga), o x100 fica só umas duas vezes mais rápido que o x1. Falta medir, com o modo debug e o painel de desempenho, numa partida salva longa no x100: quanto custa o tick e em quê (snapshots, bots, eleição, emissão pelo Socket.IO), e se o navegador engasga com um evento por tick e redesenha a tela inteira. O resultado decide as otimizações (agrupar emissões, aliviar o trabalho de cada tick, redesenhar menos no front) e é o ponto de partida das otimizações gerais de desempenho.

<a id="f158"></a>
**F158 — Animações do Como jogar revistas.** Serve N25; retrabalho da F126. No playtest, o tutorial pareceu estranho: o estilo das animações ficou parecido com o do Create, e o número do passo que aparece no meio da animação, num círculo ao lado do alvo (`StepMarker` em `tutorial/stage/stage-kit.tsx:144`, número vindo de `topic-illustration.tsx:57`, usado em `buy-stock.tsx` e `order-types.tsx`), polui a cena. O salto para o trecho do passo ao clicar numa etapa funciona bem e fica como está. Falta escolher o visual numa rodada no canvas: comparar as animações atuais com as primeiras, feitas no canvas a partir das Dicas e truques do Factorio, decidir se o número sai da cena (o passo ativo já fica destacado na lista) e o que muda no cursor e no destaque.

<a id="f164"></a>
**F164 — Mapa do Brasil por região na eleição.** Serve N34. Um mapa pintado pela cor do partido que lidera cada região, e o resultado dito por região ("você ganhou mais eleitores no Sudeste"). Pelo modelo da D19, uma região é uma mistura de grupos de eleitores (o Sudeste com mais quem vive de investimento, o Nordeste com mais quem depende de auxílio), então o voto por região sai do voto por grupo sem mudar o modelo, e o mapa é uma camada visual por cima. O upgrade seguinte, se valer, são ações de campanha por região ("comício no Nordeste") na F130. Falta: a mistura de grupos de cada região e o desenho do mapa, que passa pelo canvas.

<a id="f165"></a>
**F165 — Tela do Tesouro: títulos pelo risco do governo.** Serve N34. Com o prêmio de risco (F128), a taxa dos títulos passa a contar a história do governo: sobe quando a dívida cresce. Uma tela própria do Tesouro mostra os títulos à venda, a taxa de cada um ao longo da partida e a dívida pública ÷ PIB ao lado, para quem investe ler o risco do governo antes de comprar. Falta: o que a tela mostra além da renda fixa de hoje e o desenho, que passa pelo canvas.
