<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/atualizar/concluir/descartar/remover um item, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban do projeto, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que ordem e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-10-31):** Concluída a conferência visual; cadastrados o retrato das telas no canvas e as rodadas de redesenho das regras visuais, da Eleição e do Como jogar.

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Tipo | Resumo | Marco | Condiciona (F#) | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **N1** | — | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — | — | — | — |
| **N2** | — | Jogar com amigos pela internet sem que cada um instale uma VPN | — | [F5](#f5), [F6](#f6) | — | — | — |
| **N3** | — | Confiar que os números do simulador são exatos e reprodutíveis | — | [F22](#f22), [F100](#f100) | — | — | — |
| **N4** | — | Testar uma estratégia de investimento automática e ver como ela se sai | — | [F110](#f110), [F111](#f111) | — | — | — |
| **N5** | — | Saber quanto risco foi corrido para chegar num resultado | — | — | — | — | — |
| **N6** | — | Comparar resultados de simulações diferentes | — | — | — | — | — |
| **N7** | — | Que o simulador cobre os custos de operar do mercado real | — | [F22](#f22), [F100](#f100) | — | — | — |
| **N8** | — | Jogar contra oponentes controlados pelo computador | — | — | — | — | — |
| **N9** | — | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — | — | — | — |
| **N10** | — | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | — | [F28](#f28) | — | — | — |
| **N11** | — | Que o cenário econômico simulado seja o histórico real | — | — | — | — | — |
| **N12** | — | Continuar jogando depois do último dia com dado real | — | — | — | — | — |
| **N13** | — | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | — | — | — | — |
| **N14** | — | Atualizar para uma versão nova sem perder as partidas salvas | — | [F56](#f56) | — | — | — |
| **N15** | — | Usar uma interface agradável e coerente, à altura de um jogo | — | [F37](#f37), [F72](#f72), [F123](#f123), [F179](#f179), [F180](#f180), [F181](#f181), [F182](#f182), [F183](#f183) | — | — | — |
| **N16** | — | Ver a carteira e o mercado por setor e segmento | — | — | — | — | — |
| **N17** | — | Enxergar a estrutura do banco e esboçar mudanças nela | — | — | — | — | — |
| **N18** | — | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — | — | — | — |
| **N19** | — | Analisar um ativo com as ferramentas de um trader | — | [F34](#f34), [F131](#f131) | — | — | — |
| **N20** | — | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | — | — | — | — |
| **N21** | — | Jogar "na unha", sem a interface apontar a melhor escolha | — | — | — | — | — |
| **N22** | — | Ter objetivos para buscar além de vencer a partida | — | [F90](#f90), [F123](#f123), [F159](#f159) | — | — | — |
| **N23** | — | Jogar com os amigos de outras formas além de cada um por si | — | [F44](#f44), [F55](#f55), [F69](#f69), [F101](#f101), [F102](#f102), [F103](#f103), [F104](#f104), [F105](#f105) | — | — | — |
| **N24** | — | Saber onde está a lentidão durante uma partida | — | [F157](#f157) | — | — | — |
| **N25** | — | Entender o que é o simulador e como se joga, sem ler um manual | — | [F132](#f132), [F133](#f133), [F139](#f139), [F140](#f140), [F141](#f141), [F158](#f158), [F183](#f183) | — | — | — |
| **N26** | — | Achar a causa de um erro sem vasculhar o log inteiro | — | — | — | — | — |
| **N27** | — | Entrar numa partida que já começou | — | — | — | — | — |
| **N28** | — | Liberar uma vaga sem depender de o jogador sair | — | — | — | — | — |
| **N29** | — | Saber o que cada jogador está fazendo enquanto a partida não começa | — | — | — | — | — |
| **N30** | — | Repetir uma configuração de partida sem montá-la de novo | — | — | — | — | — |
| **N31** | — | Saber o que está movendo o mercado da partida, como quem lê o noticiário | — | [F93](#f93) | — | — | — |
| **N32** | — | Saber como foi o mês sem montar a conta | — | — | — | — | — |
| **N33** | — | Investir com dinheiro emprestado, pagando o juro do momento | — | [F111](#f111) | — | — | — |
| **N34** | — | Disputar o poder de mudar as regras da economia da partida | — | [F97](#f97), [F164](#f164), [F165](#f165), [F169](#f169), [F173](#f173), [F174](#f174), [F175](#f175), [F176](#f176), [F177](#f177), [F182](#f182) | — | — | — |
| **N35** | — | Tirar da lista as partidas que não interessam mais | — | — | — | — | — |
| **N36** | — | Encontrar rapidamente os menores e maiores valores nos dados do jogo | — | — | — | — | — |
| **N37** | — | Comprar bitcoin do jeito que dá na vida real, em frações | — | — | — | — | — |
| **N38** | — | Saber quando as estatísticas vão mudar, sem achar que travaram | — | — | — | — | — |
| **N39** | — | Chegar ao primeiro dia da partida com as próprias escolhas já feitas | — | [F169](#f169), [F170](#f170), [F173](#f173), [F174](#f174) | — | — | — |
| **N40** | — | Jogar partidas longas e na velocidade máxima sem a tela travar | — | [F157](#f157) | — | — | — |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | — | — | — | — | 🔍 |
| [**F6**](#f6) | Feature | Link de convite pela internet no lobby | — | — | Médio | Bom | ⏳ |
| [**F14**](#f14) | Feature | Janela desktop nativa | — | — | Baixo | Bom | 💤 |
| [**F22**](#f22) | Feature | Preço ajustado e proventos | — | — | Alto | Bom | ⏳ |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | — | — | — | — | 🔍 |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | — | — | — | — | 🔍 |
| [**F37**](#f37) | Feature | Tema escuro | — | — | Médio | Médio | 💤 |
| [**F44**](#f44) | Feature | Expansão Gestoras: fundar a gestora e abrir capital | M18 · 4.0 | — | — | — | 🔍 |
| [**F55**](#f55) | Feature | Modo aquisição hostil | M18 · 4.0 | — | — | — | 🔍 |
| [**F56**](#f56) | Feature | Novidades no app | — | — | Baixo | Bom | ⏳ |
| [**F60**](#f60) | Feature | Modo servidor dedicado (--headless) | — | — | Baixo | Bom | 💤 |
| [**F69**](#f69) | Feature | Imprevistos configuráveis e tipos novos | — | — | Médio | Bom | 💤 |
| [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | — | — | Médio | Bom | 💤 |
| [**F81**](#f81) | Manutenção | CORS restrito à mesma origem | — | — | Baixo | Médio | 💤 |
| [**F90**](#f90) | Feature | Cenários | — | — | — | — | 🔍 |
| [**F93**](#f93) | Feature | Rumores antecipados | — | — | — | — | 🔍 |
| [**F97**](#f97) | Feature | SELIC nas mãos do governo | M21 · 3.4 | — | Alto | Bom | ⏳ |
| [**F100**](#f100) | Feature | Proventos na carteira e nas telas | — | — | Médio | Bom | ⏳ |
| [**F101**](#f101) | Feature | Carteira separada do jogador | M18 · 4.0 | — | Alto | Médio | 💤 |
| [**F102**](#f102) | Feature | Gestoras: emissão de novas cotas e recompra | M18 · 4.0 | — | — | — | 🔍 |
| [**F103**](#f103) | Feature | Gestoras: troca de gestor pela assembleia | M18 · 4.0 | — | — | — | 🔍 |
| [**F104**](#f104) | Feature | Gestoras: co-gestores | M18 · 4.0 | — | — | — | 🔍 |
| [**F105**](#f105) | Feature | Gestoras: rendimentos mensais | M18 · 4.0 | — | — | — | 🔍 |
| [**F110**](#f110) | Feature | Combinar estratégias | — | — | Médio | Bom | 💤 |
| [**F111**](#f111) | Feature | Crédito para estratégias e bots | — | — | Baixo | Bom | 💤 |
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | — | — | — | — | 🔍 |
| [**F131**](#f131) | Feature | Catálogo de padrões de vela | — | — | — | — | 🔍 |
| [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | — | — | Médio | Bom | ⏳ |
| [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | — | — | Baixo | Bom | ⏳ |
| [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | — | — | Médio | Bom | ⏳ |
| [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | — | — | Alto | Bom | ⏳ |
| [**F141**](#f141) | Docs | README com as features de hoje | — | — | Baixo | Excelente | ⏳ |
| [**F157**](#f157) | Correção | Velocidade x100 que quase não acelera | M20 · 3.3 | — | Médio | Excelente | ⏳ |
| [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | — | — | — | — | 🔍 |
| [**F159**](#f159) | Feature | Conquista "Ordem com paciência" | — | — | Baixo | Bom | ⏳ |
| [**F164**](#f164) | Feature | Mapa do Brasil por região na eleição | M21 · 3.4 | — | Médio | Bom | ⏳ |
| [**F165**](#f165) | Feature | Tela do Tesouro: títulos pelo risco do governo | M21 · 3.4 | — | Médio | Bom | ⏳ |
| [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | — | — | Baixo | Bom | 💤 |
| [**F169**](#f169) | Feature | Contribuição de campanha salva no perfil | M21 · 3.4 | — | Baixo | Bom | ⏳ |
| [**F170**](#f170) | Feature | Parâmetros das estratégias salvos no perfil | M21 · 3.4 | — | Médio | Excelente | ⏳ |
| [**F173**](#f173) | Feature | Partido desde o 1º dia | M21 · 3.4 | — | Médio | Bom | ⏳ |
| [**F174**](#f174) | Melhoria | Preparação do lobby redesenhada | M20 · 3.3 | — | — | — | 🔍 |
| [**F175**](#f175) | Feature | Federações partidárias | — | — | Alto | Bom | ⏳ |
| [**F176**](#f176) | Feature | Cadeiras do Congresso por região | — | — | Médio | Médio | 💤 |
| [**F177**](#f177) | Feature | Marcação a mercado do Tesouro | — | — | Médio | Bom | 💤 |
| [**F179**](#f179) | Melhoria | Topbar que cabe com a corrida e o governo | M20 · 3.3 | — | — | — | 🔍 |
| [**F180**](#f180) | Manutenção | Retrato no canvas das telas que mudaram desde a 3.0 | M20 · 3.3 | — | Alto | Bom | ⏳ |
| [**F181**](#f181) | Melhoria | Regras visuais do conjunto: texto, tabelas, grade e eixos | M20 · 3.3 | — | — | — | 🔍 |
| [**F182**](#f182) | Melhoria | Eleição redesenhada como um conjunto | M20 · 3.3 | — | — | — | 🔍 |
| [**F183**](#f183) | Melhoria | Como jogar sem cobrir a tela | M20 · 3.3 | — | — | — | 🔍 |
| [**F184**](#f184) | Correção | Correções da 3.3 | M20 · 3.3 | — | Médio | Bom | ⏳ |

<details>
<summary><strong>Concluído / decidido / descartado (18 itens — clique pra expandir)</strong></summary>

| ID | Tipo | Resumo | Marco | Condiciona (F#) | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **D1** | — | Eventos são a fonte da verdade; snapshots são derivados | — | [F22](#f22), [F100](#f100), [F159](#f159) | — | — | ✅ |
| **D2** | — | Cálculo financeiro acontece só no backend; o frontend exibe | — | — | — | — | ✅ |
| **D3** | — | Dinheiro e quantidade trafegam como Decimal serializado em string | — | [F22](#f22), [F100](#f100) | — | — | ✅ |
| **D4** | — | Banco de dados embarcado no executável | — | — | — | — | ✅ |
| **D6** | — | A retomada continua no dia seguinte ao último evento | — | — | — | — | ✅ |
| **D7** | — | O simulador lê as séries sem saber a origem | — | [F22](#f22), [F100](#f100) | — | — | ✅ |
| **D8** | — | Bot, modo automático e backtest são o mesmo mecanismo | — | [F110](#f110), [F111](#f111) | — | — | ✅ |
| **D9** | — | De onde nasce uma mudança de schema | — | [F101](#f101) | — | — | ✅ |
| **D10** | — | Como a nota geral é calculada | — | — | — | — | ✅ |
| **D11** | — | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | — | — | — | ✅ |
| **D12** | — | Como numerar as versões | — | — | — | — | ✅ |
| **D13** | — | Um canal de tempo real só: Socket.IO, com fallback de polling | — | — | — | — | ✅ |
| **D14** | — | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | — | [F97](#f97) | — | — | ✅ |
| **D15** | — | Lint com oxlint, formatação com oxfmt e o TypeScript 7 com a API do 6 ao lado | — | — | — | — | ✅ |
| **D16** | — | Estratégias do app no host, personalização pela API | — | — | — | — | ✅ |
| **D17** | — | Os tópicos do tutorial se animam em código, com o motion | — | — | — | — | ✅ |
| **D18** | — | Uma migration por versão; caminho antigo só cai numa major | — | — | — | — | ✅ |
| **D19** | — | O eleitorado são grupos, cada um com apoio e rejeição por partido | — | [F97](#f97), [F164](#f164), [F173](#f173), [F175](#f175), [F176](#f176) | — | — | ✅ |

</details>

---

## 🚀 Próximas versões

> O que entra em cada versão, na ordem de trabalho. Item arquivado conta como concluído.

### 3.3 — Preparação no lobby (M20)

> **Objetivo:** Cada jogador chega à partida já preparado no lobby, e as telas que mudaram desde a 3.0 voltam a formar um conjunto.
>
> **Serve:** N39, N15, N40
>
> **Progresso:** 3/11 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | **F143** | Feature | Preparação de cada jogador no lobby | — | 📦 Arquivado |
| 2 | **F168** | Feature | Desafio da vela no lobby | — | 📦 Arquivado |
| 3 | **F178** | Feature | Conferência visual de tudo o que mudou desde a 3.0 | — | 📦 Arquivado |
| 4 | [**F184**](#f184) | Correção | Correções da 3.3 | — | ⏳ Pendente |
| 5 | [**F180**](#f180) | Manutenção | Retrato no canvas das telas que mudaram desde a 3.0 | — | ⏳ Pendente |
| 6 | [**F181**](#f181) | Melhoria | Regras visuais do conjunto: texto, tabelas, grade e eixos | [F180](#f180) | 🔍 Em avaliação |
| 7 | [**F179**](#f179) | Melhoria | Topbar que cabe com a corrida e o governo | [F180](#f180) | 🔍 Em avaliação |
| 8 | [**F182**](#f182) | Melhoria | Eleição redesenhada como um conjunto | [F180](#f180) | 🔍 Em avaliação |
| 9 | [**F183**](#f183) | Melhoria | Como jogar sem cobrir a tela | [F180](#f180) | 🔍 Em avaliação |
| 10 | [**F174**](#f174) | Melhoria | Preparação do lobby redesenhada | — | 🔍 Em avaliação |
| 11 | [**F157**](#f157) | Correção | Velocidade x100 que quase não acelera | — | ⏳ Pendente |

### 3.4 — Juros e Tesouro (M21)

> **Objetivo:** O governo decide a SELIC, e os títulos do Tesouro rendem pelo risco que ele cria.
>
> **Serve:** N34, N39
>
> **Progresso:** 0/6 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F173**](#f173) | Feature | Partido desde o 1º dia | — | ⏳ Pendente |
| 2 | [**F169**](#f169) | Feature | Contribuição de campanha salva no perfil | [F173](#f173), [F174](#f174) | ⏳ Pendente |
| 3 | [**F170**](#f170) | Feature | Parâmetros das estratégias salvos no perfil | [F174](#f174) | ⏳ Pendente |
| 4 | [**F97**](#f97) | Feature | SELIC nas mãos do governo | — | ⏳ Pendente |
| 5 | [**F164**](#f164) | Feature | Mapa do Brasil por região na eleição | — | ⏳ Pendente |
| 6 | [**F165**](#f165) | Feature | Tela do Tesouro: títulos pelo risco do governo | — | ⏳ Pendente |

### 4.0 — Expansão Gestoras (M18)

> **Objetivo:** Fundar a própria gestora, abrir capital e disputar as cotas na sala.
>
> **Serve:** N23
>
> **Progresso:** 0/7 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F101**](#f101) | Feature | Carteira separada do jogador | — | 💤 Sem prioridade |
| 2 | [**F44**](#f44) | Feature | Expansão Gestoras: fundar a gestora e abrir capital | [F101](#f101) | 🔍 Em avaliação |
| 3 | [**F102**](#f102) | Feature | Gestoras: emissão de novas cotas e recompra | [F44](#f44) | 🔍 Em avaliação |
| 4 | [**F103**](#f103) | Feature | Gestoras: troca de gestor pela assembleia | [F44](#f44) | 🔍 Em avaliação |
| 5 | [**F55**](#f55) | Feature | Modo aquisição hostil | [F103](#f103) | 🔍 Em avaliação |
| 6 | [**F104**](#f104) | Feature | Gestoras: co-gestores | [F44](#f44) | 🔍 Em avaliação |
| 7 | [**F105**](#f105) | Feature | Gestoras: rendimentos mensais | [F44](#f44), [F100](#f100) | 🔍 Em avaliação |

### Sem versão

> Os itens ⏳ e 🔍 que ainda não entraram em nenhuma versão, do que mais destrava trabalho para o que menos ("Destrava" é quantos itens em aberto esperam por aquele). É daqui que sai a próxima versão; os 💤 ficam só no kanban.

| ID | Tipo | Resumo | Serve | Depende de | Destrava | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | N2 | — | 2 | 🔍 Em avaliação |
| [**F22**](#f22) | Feature | Preço ajustado e proventos | N3, N7 | — | 2 | ⏳ Pendente |
| [**F6**](#f6) | Feature | Link de convite pela internet no lobby | N2 | [F5](#f5) | 1 | ⏳ Pendente |
| [**F100**](#f100) | Feature | Proventos na carteira e nas telas | N3, N7 | [F22](#f22) | 1 | ⏳ Pendente |
| [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | N25 | [F44](#f44) | 1 | ⏳ Pendente |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | N10 | — | 0 | 🔍 Em avaliação |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | N19 | — | 0 | 🔍 Em avaliação |
| [**F56**](#f56) | Feature | Novidades no app | N14 | — | 0 | ⏳ Pendente |
| [**F90**](#f90) | Feature | Cenários | N22 | — | 0 | 🔍 Em avaliação |
| [**F93**](#f93) | Feature | Rumores antecipados | N31 | — | 0 | 🔍 Em avaliação |
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | N22, N15 | — | 0 | 🔍 Em avaliação |
| [**F131**](#f131) | Feature | Catálogo de padrões de vela | N19 | — | 0 | 🔍 Em avaliação |
| [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | N25 | — | 0 | ⏳ Pendente |
| [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | N25 | — | 0 | ⏳ Pendente |
| [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | N25 | [F44](#f44) | 0 | ⏳ Pendente |
| [**F141**](#f141) | Docs | README com as features de hoje | N25 | [F139](#f139) | 0 | ⏳ Pendente |
| [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | N25 | — | 0 | 🔍 Em avaliação |
| [**F159**](#f159) | Feature | Conquista "Ordem com paciência" | N22 | [F44](#f44) | 0 | ⏳ Pendente |
| [**F175**](#f175) | Feature | Federações partidárias | N34 | [F173](#f173) | 0 | ⏳ Pendente |

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: os itens que podem ser pegos agora, com toda dependência já ✅. A ordem segue o plano: primeiro os itens de cada versão (ou marco) na ordem dele, depois o resto pelo "Destrava", que é quantos itens em aberto esperam por aquele, direta ou indiretamente. 💤 (sem prioridade) e 🚫 não entram.

| ID | Tipo | Resumo | Marco | Destrava | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [**F184**](#f184) | Correção | Correções da 3.3 | M20 · 3.3 · 4º | 0 | Médio | Bom | ⏳ |
| [**F180**](#f180) | Manutenção | Retrato no canvas das telas que mudaram desde a 3.0 | M20 · 3.3 · 5º | 4 | Alto | Bom | ⏳ |
| [**F174**](#f174) | Melhoria | Preparação do lobby redesenhada | M20 · 3.3 · 10º | 2 | — | — | 🔍 |
| [**F157**](#f157) | Correção | Velocidade x100 que quase não acelera | M20 · 3.3 · 11º | 0 | Médio | Excelente | ⏳ |
| [**F173**](#f173) | Feature | Partido desde o 1º dia | M21 · 3.4 · 1º | 2 | Médio | Bom | ⏳ |
| [**F97**](#f97) | Feature | SELIC nas mãos do governo | M21 · 3.4 · 4º | 0 | Alto | Bom | ⏳ |
| [**F164**](#f164) | Feature | Mapa do Brasil por região na eleição | M21 · 3.4 · 5º | 1 | Médio | Bom | ⏳ |
| [**F165**](#f165) | Feature | Tela do Tesouro: títulos pelo risco do governo | M21 · 3.4 · 6º | 1 | Médio | Bom | ⏳ |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | — | 2 | — | — | 🔍 |
| [**F22**](#f22) | Feature | Preço ajustado e proventos | — | 2 | Alto | Bom | ⏳ |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | — | 0 | — | — | 🔍 |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | — | 0 | — | — | 🔍 |
| [**F56**](#f56) | Feature | Novidades no app | — | 0 | Baixo | Bom | ⏳ |
| [**F90**](#f90) | Feature | Cenários | — | 0 | — | — | 🔍 |
| [**F93**](#f93) | Feature | Rumores antecipados | — | 0 | — | — | 🔍 |
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | — | 0 | — | — | 🔍 |
| [**F131**](#f131) | Feature | Catálogo de padrões de vela | — | 0 | — | — | 🔍 |
| [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | — | 0 | Médio | Bom | ⏳ |
| [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | — | 0 | Baixo | Bom | ⏳ |
| [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | — | 0 | — | — | 🔍 |

---

## ⏳ Pendente

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F6** | Feature | Link de convite pela internet no lobby | N2 | — | — | [F5](#f5) | Médio | Médio | Alto | Bom |
| **F22** | Feature | Preço ajustado e proventos | N3, N7 | D1, D3, D7 | — | — | Alto | Alto | Alto | Bom |
| **F56** | Feature | Novidades no app | N14 | — | — | — | Baixo | Baixo | Médio | Bom |
| **F97** | Feature | SELIC nas mãos do governo | N34 | D19, D14 | M21 · 3.4 | — | Alto | Alto | Alto | Bom |
| **F100** | Feature | Proventos na carteira e nas telas | N3, N7 | D1, D3, D7 | — | [F22](#f22) | Médio | Médio | Médio | Bom |
| **F132** | Feature | Tópicos de "como se joga" do Como jogar | N25 | — | — | — | Médio | Baixo | Alto | Bom |
| **F133** | Feature | Tópicos de conceitos do Como jogar | N25 | — | — | — | Baixo | Baixo | Médio | Bom |
| **F139** | Docs | Demonstração regravada com o jogo de hoje | N25 | — | — | [F44](#f44) | Médio | Baixo | Alto | Bom |
| **F140** | Docs | Docs reorganizada por tipo de leitor | N25 | — | — | [F44](#f44) | Alto | Baixo | Alto | Bom |
| **F141** | Docs | README com as features de hoje | N25 | — | — | [F139](#f139) | Baixo | Baixo | Alto | Excelente |
| **F157** | Correção | Velocidade x100 que quase não acelera | N40, N24 | — | M20 · 3.3 | — | Médio | Médio | Alto | Excelente |
| **F159** | Feature | Conquista "Ordem com paciência" | N22 | D1 | — | [F44](#f44) | Baixo | Baixo | Baixo | Bom |
| **F164** | Feature | Mapa do Brasil por região na eleição | N34 | D19 | M21 · 3.4 | — | Médio | Baixo | Médio | Bom |
| **F165** | Feature | Tela do Tesouro: títulos pelo risco do governo | N34 | — | M21 · 3.4 | — | Médio | Baixo | Médio | Bom |
| **F169** | Feature | Contribuição de campanha salva no perfil | N34, N39 | — | M21 · 3.4 | [F173](#f173), [F174](#f174) | Baixo | Baixo | Médio | Bom |
| **F170** | Feature | Parâmetros das estratégias salvos no perfil | N39 | — | M21 · 3.4 | [F174](#f174) | Médio | Baixo | Alto | Excelente |
| **F173** | Feature | Partido desde o 1º dia | N39, N34 | D19 | M21 · 3.4 | — | Médio | Médio | Alto | Bom |
| **F175** | Feature | Federações partidárias | N34 | D19 | — | [F173](#f173) | Alto | Médio | Médio | Bom |
| **F180** | Manutenção | Retrato no canvas das telas que mudaram desde a 3.0 | N15 | — | M20 · 3.3 | — | Alto | Baixo | Alto | Bom |
| **F184** | Correção | Correções da 3.3 | — | — | M20 · 3.3 | — | Médio | Baixo | Alto | Bom |

<a id="f6"></a>
**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Abrir para a internet exige fechar antes a tomada do host: hoje ser host é ter o nickname do `config.toml`, e com o host desconectado qualquer jogador assume esse nickname por `/api/user/claim` e passa a poder parar a partida e apagar partidas salvas. O app gera um segredo a cada abertura e abre o navegador do host com ele; o servidor reconhece como host só a sessão que apresentou o segredo, e `/api/user/claim` recusa o nickname do host. O endereço de origem não distingue o host, porque num túnel o tráfego de fora costuma chegar ao servidor pela própria máquina. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada; com o host desconectado, nenhum outro jogador consegue virar host.

<a id="f22"></a>
**F22 — Preço ajustado e proventos.** Serve N3 e N7; segue a D1, a D3 e a D7. O importador usa `yf.download(auto_adjust=True)`: o preço vem ajustado por dividendos e desdobramentos até o dia da importação, e a atualização incremental (`upsert_dataframe` só grava linhas depois da última data guardada) emenda duas séries ajustadas em dias diferentes. Um desdobramento 2:1 entre a importação e a atualização vira um degrau falso, uma queda de 50% que não existiu; além disso, o preço exibido não é o que se negociava na época. Escolhido: preço bruto mais proventos como evento. Plano: (1) **Importação:** `auto_adjust=False` guarda o fechamento bruto, e as listas de dividendos e de desdobramentos que o `yfinance` traz entram numa tabela de eventos corporativos por ativo (data ex, tipo, valor ou razão), por migration. A série bruta não muda quando sai um provento novo, então a atualização incremental passa a emendar séries do mesmo tipo e o degrau some. (2) **Desdobramento e grupamento:** na data ex, a quantidade de cada posição é multiplicada pela razão e o preço médio dividido por ela, como evento da partida reconstruível (D1), com a quantidade em Decimal (D3). (3) **Dividendo:** na data ex, o valor por cota vezes a quantidade entra no caixa, como evento; sem esse crédito o retorno de quem paga dividendo cairia, porque o preço bruto cai na data ex e o ajuste que antes embutia o provento deixa de existir. Telas, rendimento por posição, IR e provento sintético ficam na F100. (4) **Números que mudam:** o retorno e a nota geral (D10) mudam de valor, então os testes de números fixos são regerados e conferidos contra uma conta à mão antes de aceitar. (5) **Partidas salvas:** jogaram sobre o preço ajustado; o primeiro passo é verificar se o congelamento por versão da D7 (hoje usado só para trecho gerado) cobre também o trecho real, ou se as partidas salvas são recalculadas. Gatilho: livre; a F100 espera esta.
**Aceite:** num desdobramento 2:1 ocorrido depois da importação, a atualização incremental não produz queda de 50% no preço, e a posição de quem tinha o ativo dobra de quantidade sem mudar de valor.

<a id="f56"></a>
**F56 — Novidades no app.** Serve N14. Como as notas de patch de um jogo: o `CHANGELOG.md` da F51 vai junto no executável, o backend o serve com a versão, e o lobby mostra as novidades da versão atual. Na primeira abertura depois de atualizar, o card ou o selo de novidades fica em destaque até ser aberto (o navegador guarda a última versão vista); aberto, mostra "O que há de novo na versão X" e dá acesso ao histórico inteiro. O lugar exato no lobby, que já está cheio, sai de uma iteração no Claude Design antes de implementar.

<a id="f97"></a>
**F97 — SELIC nas mãos do governo.** Ligado à N34; uma opção da expansão "Governo & Política" (F95), no lugar do Banco Central autônomo, que continua sendo o padrão. (1) **Ritmo do Copom:** o governo decide a SELIC em reuniões a cada 45 dias, como o Copom, que se reúne 8 vezes por ano desde 2006; entre reuniões ela não muda. (2) **Teto por reunião, pelo que aconteceu de verdade.** Das 150 mudanças da meta da SELIC entre 2000 e outubro de 2026 (série do Banco Central): 34 foram de 0,25 ponto, 67 de 0,5, 19 de 0,75, 19 de 1, 7 de 1,5, uma de 2, uma de 2,5 e duas de 3; desde 2006, nunca passou de 1,5. O teto vem do IPCA de 12 meses: 0,75 ponto em tempo normal (80% das mudanças reais), 1,5 com o IPCA acima do teto da meta (a meta mais a tolerância de 1,5 ponto), como em 2021 e 2022, e 3 com o IPCA acima de 15%, o que só aconteceu em 2002 e 2003. (3) **O efeito vem do juro real, contínuo e sem faixa morta.** Juro real é a SELIC menos o IPCA de 12 meses; o juro neutro, que nem aquece nem esfria, é 5%, perto da estimativa do Banco Central. A distância até o neutro age pelo mecanismo de efeito por cima das séries da F106: cada ponto abaixo do neutro, mantido por um ano, sobe o IPCA em uns 0,3 ponto ao longo dos 4 trimestres seguintes, com o pico no 2º e no 3º (o modelo Samba do Banco Central), e cada ponto acima o derruba na mesma medida. Abaixo do neutro o crescimento aquece na hora; acima, esfria e a bolsa cai pelo coeficiente da D14. Como o efeito é contínuo, nenhuma faixa de juro sai de graça. Os limites de 2% e 7% de juro real servem só para os avisos e para a reação dos grupos (D19): abaixo de 2%, aposentados e quem vive de investimento perdem apoio; acima de 7%, quem trabalha e empreende. (4) **Credibilidade.** Cada reunião que deixa o juro real abaixo do neutro com o IPCA acima da meta gasta credibilidade; cada reunião que aperta devolve um pouco, devagar. Com pouca credibilidade a inflação reage mais rápido ao juro baixo, porque o mercado já espera que ela suba, e o prêmio de risco dos títulos (F128) sobe: o governo que usou a SELIC para ganhar a eleição herda uma inflação que não cede. A tela mostra a credibilidade com uma dica do que ela mede e do que a move. O 0,3 é ordem de grandeza dos modelos semiestruturais e se calibra no playtest; não se mede no histórico do banco, porque a SELIC reage à inflação e a regressão direta sai com o sinal trocado. Fontes: [Relatório de Inflação de junho de 2013, box do Samba](https://www.bcb.gov.br/content/ri/relatorioinflacao/201306/RELINF201306-ri201306b6p.pdf); [um modelo semiestrutural simples](https://coolassessor.substack.com/p/um-modelo-semiestrutural-simples); [Blog do IBRE sobre o efeito da SELIC](https://blogdoibre.fgv.br/posts/deve-o-bc-reduzir-selic-replica-jose-julio-senna).

**Aceite:** com o resto parado, o juro real 3 pontos abaixo do neutro por um ano sobe o IPCA de 12 meses em 0,6 a 1,2 ponto no ano seguinte, e a mesma decisão com credibilidade baixa sobe mais.

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

<a id="f157"></a>
**F157 — Velocidade x100 que quase não acelera.** Serve N40 e N24. No playtest, o x100 andou quase como o x1, ou até mais lento. O loop dorme `1 / velocidade` segundos depois de cada tick (`simulation_loop.py:132` a `:156`): no x1 o dia leva o tick mais 1 s, no x100 o tick mais 10 ms, e com o tick perto de 1 s (a medição da D4 deu de 0,6 a 0,95 s com carga) o x100 fica só umas duas vezes mais rápido que o x1. A correção: (1) **medir por dentro do tick**, com uma medida do modo debug para cada etapa (snapshots, bots, eleição, emissão pelo Socket.IO), lida no painel de desempenho numa partida salva longa no x100, junto de se o navegador engasga com um evento por tick; (2) **dormir pela cadência**, `1 / velocidade` menos o que o tick já gastou, nunca abaixo de zero; (3) **agrupar as emissões em velocidade alta**, os dias do mesmo intervalo num evento só, com o front redesenhando uma vez por lote; (4) corrigir o gargalo que a medição apontar. É o ponto de partida das otimizações gerais de desempenho.

**Aceite:** numa partida salva longa, com bots e a expansão "Governo & Política" ligada, um dia no x100 custa no máximo 100 ms (uns 10 dias por segundo).

<a id="f159"></a>
**F159 — Conquista "Ordem com paciência".** Serve N22; segue a D1. A 9ª conquista da leva de novas conquistas ficou de fora porque o evento de ordem de ações (`event_equity`) não guarda o tipo da ordem que gerou a execução. Plano: coluna `order_type` em `event_equity` (mercado ou limitada), por migration, com as linhas antigas como mercado; o `Broker` grava o tipo na execução; uma `@metric` em `metrics.py` conta as execuções de ordem limitada do jogador, e a conquista entra no `catalog.py`. Vale qualquer ordem limitada executada, inclusive a que executa na hora porque o preço já estava bom. Fica para a rodada de conquistas feita com o usuário depois da Gestoras, junto com a docs, quando dá para ver todas as features que pedem conquista.

<a id="f164"></a>
**F164 — Mapa do Brasil por região na eleição.** Serve N34. Um mapa pintado pela cor do partido que lidera cada região, e o resultado dito por região ("você ganhou mais eleitores no Sudeste"). Pelo modelo da D19, uma região é uma mistura de grupos de eleitores, então o voto por região sai do voto por grupo sem mudar o modelo, e o mapa é uma camada visual por cima; o Congresso continua nacional. O peso de cada região é o eleitorado do TSE de 2022: Sudeste 42,6%, Nordeste 27,1%, Sul 14,7%, Norte 8,1%, Centro-Oeste 7,5%. A mistura de grupos de cada região vem de dados públicos: beneficiários do Bolsa Família (quem depende de auxílio), benefícios do INSS (aposentados), PNAD Contínua do IBGE (trabalhadores formais e servidores) e investidores da B3 por região (quem vive de investimento), com a fonte de quem empreende escolhida na implementação e citada no código. As misturas moram ao lado de `voters.WEIGHTS`, e a soma delas pesada pelo eleitorado fecha os pesos nacionais. O desenho começa registrando no canvas as telas e os estados: antes da eleição, apuração, 2º turno e expansão desligada. O upgrade seguinte são as cadeiras por região (F176) e, se valer, ações de campanha por região ("comício no Nordeste") na F130.

**Aceite:** a soma das misturas regionais pesada pelo eleitorado bate com os pesos nacionais com erro de até 0,005 por grupo, num teste.

<a id="f165"></a>
**F165 — Tela do Tesouro: títulos pelo risco do governo.** Serve N34. Com o prêmio de risco (F128), a taxa dos títulos conta a história do governo: sobe quando a dívida cresce. Hoje o Tesouro sai misturado na vitrine mensal da renda fixa, com o prêmio somado à taxa (`fixed_income/factory/__init__.py`). Uma tela própria do Tesouro mostra: (1) **os títulos à venda** (Selic, Prefixado e IPCA+), com a taxa aberta em "taxa base + prêmio de risco do país" e a compra dali mesmo; (2) **a taxa de cada tipo ao longo da partida**, com a dívida pública ÷ PIB no mesmo eixo de tempo, para ver a taxa subir junto com a dívida; (3) **o termômetro do risco**: o prêmio atual, a dívida ÷ PIB e quanto falta para o próximo degrau do prêmio. Cada métrica tem uma descrição curta e uma dica com a definição e como ler. Para o gráfico, o backend guarda a taxa de cada tipo e o prêmio em cada vitrine mensal. O desenho começa registrando no canvas as telas e os estados: expansão desligada, dívida abaixo de 50% do PIB sem prêmio e prêmio alto. A marcação a mercado é o card seguinte (F177).

<a id="f169"></a>
**F169 — Contribuição de campanha salva no perfil.** Serve N34 e N39. A contribuição mensal de cada filiado fica salva no perfil do jogador (`Users.settings`, chave própria, ao lado do Meu partido), e vale para quem funda e para quem se filia: o partido em que ele entra começa a cobrá-la quando a campanha abre, em vez de começar com zero. Quem nunca salvou continua com zero. A cobrança mensal já pula quem não tem caixa (`government_book.py`, coleta do 1º dia útil); o que muda é que **o mês pulado abre uma pendência** ("sua contribuição de R$ X não foi paga em março, por falta de caixa"), resolvida quando a contribuição seguinte é paga ou quando o jogador muda o valor. Mudar a contribuição dentro da partida também grava o valor no perfil. O campo da preparação mora na tela redesenhada (F174).

<a id="f170"></a>
**F170 — Parâmetros das estratégias salvos no perfil.** Serve N39. Quem ajusta uma estratégia do modo automático (os dias das médias, o ativo, a divisão do rebalanceamento) precisa lembrar e redigitar os valores a cada partida. Os parâmetros passam a ficar no perfil, por estratégia (`Users.settings`, chave `strategy_params`: `{chave_da_estratégia: {parâmetro: valor}}`), por dois caminhos: (1) **o último valor usado**: ao ligar o automático numa partida, os parâmetros escolhidos se gravam no perfil daquela estratégia; (2) **a preparação**: a aba Estratégias da tela redesenhada (F174) lista as estratégias com os parâmetros de cada uma, para ajustar antes de jogar. Ao ligar o automático, o formulário nasce com os valores do perfil, ou com o padrão da estratégia onde o jogador não salvou nada. A validação é a mesma dos bots do lobby (`validate` da estratégia: tipo, mínimo e máximo); o ticker salvo que não existe na partida cai no padrão da estratégia, com aviso no formulário. O automático continua sendo ligado pelo jogador dentro da partida, que nasce pausada no 1º dia.

<a id="f173"></a>
**F173 — Partido desde o 1º dia.** Serve N39 e N34; condicionada pela D19. Hoje fundar e filiar-se só abrem com a campanha, um ano antes do 1º turno (`_ensure_campaign_open` em `government_book.py`), e a preparação do lobby espera a abertura para virar partido. Como no Brasil, onde o partido existe o tempo todo e o que tem prazo é a filiação de quem concorre, a regra passa a ser: **fundar, filiar-se e sair ficam livres desde o 1º dia**; a **filiação para concorrer** fecha 6 meses antes do 1º turno (Lei 9.504/97, art. 9): quem entra depois disso é filiado, mas não pode ser candidato nem vice naquela eleição; a **chapa, as ações de campanha e a cobrança da contribuição** continuam só na janela da campanha (a cobrança mensal pula os meses antes da abertura). **A preparação do lobby é aplicada no 1º dia da partida**, e não mais na abertura da campanha: os partidos preparados nascem com os filiados, e a chapa e o vice preparados ficam guardados no partido até a campanha abrir. Entre os turnos, filiação e saída continuam travadas. Partido de jogador fundado no meio do mandato não tem cadeira até a eleição seguinte. A preparação ainda não saiu em versão, então não há partida salva com o evento antigo para manter. Gatilho: antes do redesenho da preparação (F174), que mostra os partidos já existentes.

<a id="f175"></a>
**F175 — Federações partidárias.** Serve N34. Na regra real (Lei 14.208/2021), dois ou mais partidos se unem e agem como um só por no mínimo 4 anos; a federação é diferente da chapa com vice de outro partido, que já existe e vale só para a eleição. Aqui: (1) **Formação:** um partido propõe a outro, no molde do convite de vice (`election.vice_blocker`, `government_book.answer_vice`), inclusive ao partido do computador; a proposta vale até 6 meses antes do 1º turno, o mesmo prazo da filiação para concorrer (F173). (2) **Um partido só, por um mandato:** a federação dura até o fim do mandato que vem depois da eleição em que se formou. Nela há uma chapa presidencial, com o candidato que a proposta nomeia e o vice de qualquer partido federado; uma lista no Congresso, com os votos somados para a barreira de 5% e para o D'Hondt de `house.distribute`, e as cadeiras da federação repartidas entre os partidos dela pelo D'Hondt sobre o voto de cada um; e uma orientação, a do partido com mais cadeiras (sem cadeira ou com empate, a do partido que propôs). O parceiro pode desobedecer, com o custo normal da desobediência. (3) **O preço:** o partido pequeno escapa da barreira, mas perde o próprio candidato, fica preso pelo mandato e herda, enquanto durar a federação, metade da rejeição que cada grupo de eleitores (D19) tem pelo parceiro. Sair antes do prazo desfaz a federação e impede quem saiu de se federar na eleição seguinte. (4) **Tela:** a federação aparece no cartão dos partidos da Eleição, no hemiciclo do Congresso e no jornal (formada, desfeita); o desenho começa registrando as telas e os estados no canvas: proposta pendente, federação formada, federação desfeita antes do prazo e expansão desligada.

<a id="f180"></a>
**F180 — Retrato no canvas das telas que mudaram desde a 3.0.** Serve N15. Da 3.1 à 3.3, cada tela foi desenhada sozinha no canvas e implementada sem conferência na tela. Juntas, elas quebram a topbar, fazem tabelas rolarem de lado e desalinham cartões (conferência visual, F178). Os boards do governo e da eleição mostram o desenho aprovado de cada feature isolada, não o app de hoje. Esta feature põe no canvas o app como ele está, para as rodadas de redesenho (F179, F181, F182, F183) comentarem sobre o conjunto e para comparar o que foi aprovado com o que foi implementado.

(1) **Limpeza.** As linhas das features implementadas até a 3.0 vão para uma página nova do Arquivo, mudando só a página do board. Ficam no canvas:
- as linhas das features ainda não implementadas, inclusive as variantes à espera de escolha;
- as linhas do governo e da eleição, até o retrato substituí-las;
- um board de identidade visual, de onde a skill `design-canvas` copia o `<helmet>` (fonte, cores e classes) para os boards novos.

(2) **Retrato.** Uma captura em 1366×768 de cada tela e estado que mudou desde a 3.0, seguindo o roteiro da conferência visual (199 linhas de tela × estado). As capturas são tiradas depois dos consertos do hotfix, no banco de teste, com o governo e a corrida ligados. Cada captura vira um board de imagem do lado do antes, com uma linha por área: lobby, mercado e carteira, crédito, estatísticas, eleição, governo, jornal, Como jogar e configurações. É imagem, e não réplica em HTML: a réplica seria uma terceira versão da tela, cara de fazer e com as próprias divergências.

(3) **Post-its.**
- Ao lado da captura, os achados da conferência que ficaram para o canvas.
- Onde a tela difere do board aprovado da feature, o post-it "implementado diferente do aprovado", com a diferença. A comparação é texto contra texto: a spec do board (`extract_spec.py`) contra a árvore da tela no devtools, por um Haiku por área, com a captura para o layout.

(4) **Notas.** O canvas comporta 200 notas, e a limpeza libera as das linhas arquivadas.

**Como roda:** sessão Sonnet, sem decisão de design: o que pede escolha vira post-it para as rodadas de redesenho. Pede, na mesma sessão, o app rodando com o `chrome-devtools` e escrita no canvas original. Sem escrita no original, a sessão para e avisa.

**Aceite:** toda tela do roteiro que mudou desde a 3.0 tem captura no canvas, e o canvas fica com até 185 notas.

<a id="f184"></a>
**F184 — Correções da 3.3.** Lote dos consertos achados desde a 3.2. Já em main, em 37 commits `fix:`:
- **Eleição e Governo:** a leitura dos eventos do 2º turno, que quebrava o resumo do mês, as estatísticas e as conquistas; a pesquisa do 1º turno ao lado da do 2º; a tabela de transferência do 2º turno (estimativa chamada de exata, partes que não somavam o total); a cor dos partidos do computador; a chapa do fundador sem vice; os diálogos de promessas e da votação; a data da posse; os cartões de pesquisa, eleitorado e promessas.
- **Economia e crédito:** o crescimento do PIB, que derrubava partidas longas; a nota de crédito, que ignorava parcela vencida; a alavancagem sem patrimônio; os pontos da nota de risco; o tooltip das séries da Economia.
- **Estados de erro e carregamento:** a tela de resultado, o jornal e o cartão do desafio da vela, que ficavam no esqueleto ou sumiam; a mensagem de erro das páginas de Governo, Eleição, Economia e Crédito; o ranking velho das Estatísticas; o diálogo do resultado do turno depois de recarregar.
- **Textos e corte:** plurais e concordâncias (compras e vendas, promessas, pontos, prêmio de risco); nomes cortados sem dica no lobby, nos partidos e nas estatísticas; a faixa do dia da renda variável; a janela do desafio da vela acima de 768 px; o painel final do desafio, que comemorava com 0 acertos; o relatório final; a coluna Quando das ordens abertas; a janela de notícias com a partida pausada.

Falta a triagem das notas da próxima partida de playtest: cada nota vira conserto neste lote, ou card próprio quando pede desenho. Vai a ✅ quando a triagem fechar.

---

## 🔍 Em avaliação

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Falta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **F5** | Spike | Spike: provider de túnel pela internet | N2 | — | — | — | Escolhe o provider da F6 |
| **F28** | Feature | Muitos futuros (Monte Carlo) | N10 | — | — | — | Revisa ou confirma a D7 |
| **F34** | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | N19 | — | — | — | Escolhe a biblioteca de gráfico |
| **F44** | Feature | Expansão Gestoras: fundar a gestora e abrir capital | N23 | — | M18 · 4.0 | [F101](#f101) | O protótipo do preço da cota com o formador sintético |
| **F55** | Feature | Modo aquisição hostil | N23 | — | M18 · 4.0 | [F103](#f103) | Parte mínima no mercado e o destino do incorporado |
| **F90** | Feature | Cenários | N22 | — | — | — | Um preset com objetivo |
| **F93** | Feature | Rumores antecipados | N31 | — | — | — | Opção da partida |
| **F102** | Feature | Gestoras: emissão de novas cotas e recompra | N23 | — | M18 · 4.0 | [F44](#f44) | O prazo da preferência e o preço da emissão |
| **F103** | Feature | Gestoras: troca de gestor pela assembleia | N23 | — | M18 · 4.0 | [F44](#f44) | Como a assembleia escolhe o novo gestor |
| **F104** | Feature | Gestoras: co-gestores | N23 | — | M18 · 4.0 | [F44](#f44) | A divisão das taxas |
| **F105** | Feature | Gestoras: rendimentos mensais | N23 | — | M18 · 4.0 | [F44](#f44), [F100](#f100) | A parte do lucro distribuída |
| **F123** | Melhoria | Redesenhar o aviso de conquista desbloqueada | N22, N15 | — | — | — | Escolher o desenho do aviso no canvas; liga à F122 |
| **F131** | Feature | Catálogo de padrões de vela | N19 | — | — | — | Tópico do Como jogar com cada padrão animado |
| **F158** | Melhoria | Animações do Como jogar revistas | N25 | — | — | — | O visual numa rodada no canvas |
| **F174** | Melhoria | Preparação do lobby redesenhada | N39, N34 | — | M20 · 3.3 | — | Retrabalho da F143; falta a rodada no canvas |
| **F179** | Melhoria | Topbar que cabe com a corrida e o governo | N15 | — | M20 · 3.3 | [F180](#f180) | Escolher o desenho no canvas |
| **F181** | Melhoria | Regras visuais do conjunto: texto, tabelas, grade e eixos | N15 | — | M20 · 3.3 | [F180](#f180) | A rodada no canvas sobre os retratos |
| **F182** | Melhoria | Eleição redesenhada como um conjunto | N15, N34 | — | M20 · 3.3 | [F180](#f180) | A rodada no canvas sobre os retratos |
| **F183** | Melhoria | Como jogar sem cobrir a tela | N15, N25 | — | M20 · 3.3 | [F180](#f180) | A rodada no canvas sobre os retratos |

<a id="f5"></a>
**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO; se não passar, se ao menos o polling atravessa (o SSE saiu na D13, então o polling é o único fallback). O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

<a id="f28"></a>
**F28 — Muitos futuros (Monte Carlo).** Serve N10. Em vez de testar a estratégia num futuro gerado só, testá-la em muitos (ex.: 100, cada um com uma semente) e mostrar o resultado como distribuição: "perdeu para o CDI em 23 de 100 futuros; no pior, −35%; no do meio, +40% em 5 anos". Lê-se pela fração de futuros ruins e pelo pior caso: poucos futuros perdendo para o CDI é bom; uma estratégia que só ganha no histórico real e perde na maioria dos futuros plausíveis teve sorte, não mérito. É o backtest da F19 repetido sobre gerações do gerador da D14. Falta definir: **onde vivem os 100 futuros.** A D7 dá às tabelas de série uma dimensão de versão, que a F24 implementa para congelar partidas salvas. Opções: (1) cada futuro de Monte Carlo é uma versão descartável nessa dimensão, gravando 100 vezes as linhas geradas (cerca de 5 milhões para 37 ativos × 5 anos); (2) o motor lê as séries por um provedor que pode ser o banco ou uma geração em memória (o `SeriesGenerator` gera 37 ativos × 5 anos em cerca de 1 s), o que estende a D7 de "mesmas tabelas" para "mesma interface". Sai daqui com essa escolha, que revisa ou confirma a D7.

<a id="f34"></a>
**F34 — Gráfico de ações em tela cheia, com ferramentas de trader.** Serve N19; segue a D2. Um botão no card "Histórico de Preços" abre o gráfico em tela cheia, com os indicadores da F33 e o que uma plataforma de trader oferece: barra de ferramentas de desenho (linha de tendência, linha horizontal de suporte e resistência, canal, retângulo, retração de Fibonacci, texto), régua que mede variação % e pregões entre dois pontos, escala logarítmica, legenda com abertura, máxima, mínima, fechamento e volume do candle sob o cursor, comparação com outro ticker ou com o Ibovespa em %, e uma boleta compacta para comprar e vender sem sair da tela. Os desenhos ficam salvos por jogador e ticker numa tabela nova (`chart_drawings`, com os pontos em JSON), entrando por migration (D9). Falta escolher a biblioteca: (1) continuar no `lightweight-charts` e escrever as ferramentas de desenho como plugins (a API de primitives da versão 5; os exemplos oficiais trazem linha de tendência e retângulo); (2) trocar pelo KLineChart (Apache 2.0), que já vem com cerca de 15 ferramentas de desenho, mas calcula indicadores no navegador, e pela D2 eles viriam do backend como indicador customizado; (3) o Advanced Charts da TradingView tem tudo pronto, mas a licença pede cadastro e não permite publicar a biblioteca em repositório público, o que o deixa fora deste projeto. Sai daqui com um protótipo de linha de tendência e Fibonacci nas opções 1 e 2, e a escolha.

<a id="f44"></a>
**F44 — Expansão "Gestoras": fundar a gestora e abrir capital.** Serve N23. Inspiração: o Capitalism Lab (oferta pública, emissão de novas ações, recompra, compra de ações dos concorrentes), o OpenTTD e o Software Inc. Lá cada jogador é uma empresa que fabrica ou transporta; aqui tudo é finanças, então a empresa de cada jogador é uma gestora, e o que ela vende é o próprio desempenho. **Como expansão:** ligável por partida numa **aba própria "Expansões"** no lobby, com banner, emblema e "o que muda", como a loja de DLC dos jogos da Paradox; é enfeite visual, o sistema é o mesmo ligado ou não. **A gestora** tem nome e ticker de 4 letras mais 11, como cota de FII na B3 (o servidor recusa letras que já existam entre os ativos importados), e no livro de ofertas a linha leva a cor e a sigla do jogador, para não se confundir com ativo real. O jogador a funda levando **caixa, ações e títulos** da carteira em troca de cotas, e a opera por um **modo na topbar** ("Operando: Aurora Gestão"), que troca a conta de todas as telas de mercado, com uma faixa verde-petróleo e o caixa da gestora dizendo qual conta está ativa. **É um fundo fechado listado, como um FII:** (1) **oferta pública** quando o gestor quiser — cotas novas ao preço do patrimônio por cota (patrimônio de R$ 100 mil em 1.000 cotas dá R$ 100), e o dinheiro de quem compra entra na gestora: é investir no amigo; (2) **mercado** — depois da oferta, as cotas são negociadas no livro de ofertas que a renda variável já tem, e o preço sai da oferta e da procura, acima do patrimônio por cota (ágio) quando a sala acredita no gestor e abaixo (deságio) quando não; (3) **liquidez** — a liquidez de fundo do livro nasce dos candles de cada ativo, e a cota não tem candle, então um formador de mercado sintético põe ordens de compra e venda em volta do patrimônio por cota, numa faixa de 20% para cima e para baixo recalculada todo dia; dentro da faixa, o preço sai dos jogadores, e o livro tem contraparte até numa sala de 2; (4) **taxas** — a gestora paga aos gestores taxa de administração todo mês sobre o patrimônio e taxa de performance a cada 6 meses sobre o que passar do CDI, com teto na partida de **2% ao ano de administração e 20% de performance**, e cada gestor escolhe até o teto. A performance respeita a **marca d'água**, o maior patrimônio por cota sobre o qual a taxa já foi cobrada: se a cota cai de R$ 100 para 80 e volta a 100, a recuperação não paga performance. **O lucro fica dentro da gestora** e valoriza a cota. **Por que abrir capital, e quando:** as taxas são sobre o dinheiro dos outros, e com ágio as cotas do próprio gestor valem mais no ranking; o custo é ficar exposto, porque vender mais da metade abre a porta para perder o controle (F103). Abrir cedo, sem histórico, tende a sair com pouca procura; abrir depois de um bom ano tende a sair com ágio. **O gestor e a própria gestora:** o gestor negocia com a gestora pelo livro como qualquer jogador; a linha leva a sigla dele, então a negociação fica à vista, e quem cobra é a sala, vendendo a cota (deságio) ou trocando o gestor (F103). **Regras para o cálculo fechar:** só pessoas compram cotas, nunca gestoras, o que impede a participação cruzada (A com cotas da B, que tem cotas da A). No ranking, cada jogador soma a carteira pessoal, as taxas recebidas e as cotas que tem pelo **preço de ranking**: a média dos negócios dos últimos 20 pregões, ponderada pelo volume e limitada a 30% acima ou abaixo do patrimônio por cota; sem negócio no período, vale o patrimônio por cota. Um ágio de até 30% conta, e um negócio forçado a R$ 1.000 numa cota de R$ 100 conta no máximo como R$ 130. A carteira da gestora só conta através das cotas, sem contar o mesmo dinheiro duas vezes. **Estrutura:** a carteira própria da gestora é a F101; a cota é um ativo no livro de ofertas, com o patrimônio por cota publicado a cada dia. **Com a expansão Governo & Política (F95):** quando o gestor vence a eleição, na posse ele deixa de operar a gestora e de receber as taxas, porque a carteira do presidente fica congelada; um co-gestor (F104) assume e, sem co-gestor, a gestora congela até o fim do mandato; as cotas que ele tem continuam dele. A F95 sai antes, então a carteira congelada do presidente já existe quando a gestora for implementada: cabe a esta feature estender o congelamento à gestora. **Nas features seguintes:** emissão de novas cotas e recompra (F102), troca de gestor pela assembleia (F103), co-gestores (F104) e rendimentos mensais (F105). Falta: um protótipo do preço da cota no livro, com o formador sintético e jogadores comprando e vendendo, para calibrar a faixa de 20%.
 **Na preparação do lobby:** a identidade da gestora (nome e ticker) fica salva no perfil, no molde do Meu partido, e entra numa aba própria da preparação (F174); a gestora preparada é fundada no 1º dia, vazia, e o jogador leva para ela o que quiser da carteira.

<a id="f55"></a>
**F55 — Modo aquisição hostil.** Serve N23. Um modo de jogo da expansão "Gestoras" (F44) em que perder o controle tira o jogador da partida. Todo o patrimônio de cada jogador está na própria gestora, e quem juntar mais da metade das cotas de outra a incorpora: o dono anterior sai da partida e a gestora dele passa a ser controlada pelo comprador. Vence quem sobrar, ou quem tiver o maior patrimônio na data final. **Carência:** nos primeiros meses (padrão 12) ninguém pode passar de metade de outra gestora, para que abrir capital cedo não seja suicídio. **Ninguém fica invulnerável:** sem oferta pública, a gestora seria impossível de comprar, então no fim da carência todas precisam ter uma parte mínima das cotas no mercado (padrão 50%); quem não abriu capital entra numa oferta automática pelo patrimônio por cota. **Defesa:** recompra de cotas com o caixa da gestora e compra com as taxas recebidas, como uma empresa que recompra ações para não ser comprada. Falta decidir: a parte mínima no mercado; se o incorporado sai da partida ou vira co-gestor do comprador (como numa fusão); e se há um preço mínimo por cota durante a tentativa de aquisição, como nas ofertas públicas de aquisição reais.

<a id="f90"></a>
**F90 — Cenários.** Serve N22. Como nos jogos de estratégia: uma partida montada com intenção, um preset (F89) com objetivo e texto de abertura. Exemplos: "Crise de 2008" (começa em setembro de 2008 com R$ 100 mil, meta de não perder mais de 20%), "Década perdida" (futuro gerado com choque de inflação de +15 pontos) e "Plano Real". O objetivo usa os modos de jogo que já existem (corrida à meta, viver de renda) e o ranking. Falta definir: quais cenários entram primeiro e o objetivo de cada um; se o objetivo pode ser algo que os modos não cobrem (perda máxima, bater o CDI); se há campanha, com um cenário liberando o seguinte; e se o usuário cria os próprios cenários ou só joga os que vêm com o app.

<a id="f93"></a>
**F93 — Rumores antecipados.** Ligado à N31; uma opção da partida, desligada por padrão. O simulador já sabe o futuro: as séries até a data final estão no banco antes de a partida começar, sejam reais ou geradas. O rumor usa isso e chega antes do fato, ao contrário do noticiário (F92): dias antes de um movimento grande (queda forte de um setor, mudança da SELIC), aparece na caixa de entrada algo como "analistas veem risco no varejo". O valor do rumor é obrigar o jogador a pensar: pode acontecer ou não, e a frase pede interpretação. Por isso só uma parte dos rumores se confirma, outra parte é alarme falso sorteado onde nada vai acontecer, e alguns não dizem a direção ("mudanças na diretoria da X"). Falta definir: a taxa de acerto e a antecedência; quão vago o rumor é (setor ou ativo, com ou sem direção); se é da sala inteira ou informação de um jogador só (comprada, como um informante); e se vale no modo Especialista.

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

<a id="f158"></a>
**F158 — Animações do Como jogar revistas.** Serve N25; retrabalho da F126. No playtest, o tutorial pareceu estranho: o estilo das animações ficou parecido com o do Create, e o número do passo que aparece no meio da animação, num círculo ao lado do alvo (`StepMarker` em `tutorial/stage/stage-kit.tsx:144`, número vindo de `topic-illustration.tsx:57`, usado em `buy-stock.tsx` e `order-types.tsx`), polui a cena. O salto para o trecho do passo ao clicar numa etapa funciona bem e fica como está. Falta escolher o visual numa rodada no canvas: comparar as animações atuais com as primeiras, feitas no canvas a partir das Dicas e truques do Factorio, decidir se o número sai da cena (o passo ativo já fica destacado na lista) e o que muda no cursor e no destaque.

<a id="f174"></a>
**F174 — Preparação do lobby redesenhada.** Serve N39 e N34; retrabalho da F143. O card "Minha preparação" ficou ruim na tela, e a preparação vai crescer (partido, parâmetros das estratégias, gestora), o que um card no lobby não comporta. A preparação existe para tirar do jogador o que ele refaz igual a cada partida. Falta escolher o desenho numa rodada no canvas, com três variantes: (a) um botão "Minha preparação" no lobby que abre um dialog largo com abas (Partido, Estratégias e, com a expansão, Gestora), no molde do Como jogar e do gerador de futuro; (b) um botão fixo no canto, como o do Como jogar dentro da partida; (c) uma **visão geral dos partidos à vista no lobby**, para todos: sigla, cor, filiados, chapa e vice de outro partido, que é onde a sala negocia quem entra com quem. A rodada cobre os estados expansão desligada, partida salva selecionada (travado), conflito de sigla ou cor e convite de vice pendente. Sai daqui para Pendente com a variante escolhida.

<a id="f179"></a>
**F179 — Topbar que cabe com a corrida e o governo.** Serve N15. O controle de velocidade (`layouts/partial/topbar.tsx`) é largo: o selo de pausa leva o motivo inteiro ("Pausado: resultado do 1º turno"), depois vêm a data, o play e os cinco botões de velocidade (1×, 2×, 4×, 10× e 100×). Com a corrida pela meta, o governo, o Como jogar e o caixa na mesma linha, a topbar quebra. Falta escolher o desenho no canvas, comparando: (a) a velocidade num botão só ("10×") que abre as opções; (b) o selo só com "Pausado" e o motivo numa dica ou na faixa abaixo da topbar, onde já mora o aviso do presidente; (c) a corrida e o governo como selos compactos, com o detalhe ao passar o mouse; (d) a topbar em duas linhas abaixo de uma largura. O pior caso é o estado de referência: 1366 px, corrida e governo ligados, pausa com o motivo mais longo e o x100 destacado. Sai daqui para Pendente com a variante escolhida.

<a id="f181"></a>
**F181 — Regras visuais do conjunto: texto, tabelas, grade e eixos.** Serve N15. A conferência visual (F178) achou problemas que se repetem pelo app inteiro:
- 125 usos de texto abaixo de 12 px;
- rótulos com contraste de 3,4 a 3,6:1, abaixo dos 4,5:1 que a recomendação de acessibilidade (WCAG AA) pede para texto comum;
- tabelas que rolam de lado dentro do cartão: Renda fixa, Contas, votação, Comparar, Central de dados e Rentabilidade;
- página sem largura máxima em 1920;
- cartões do mesmo nível com alturas diferentes: Crédito, Carteira, Estatísticas e Comparar;
- vazios grandes ao lado de colunas altas: Governo neutro, Eleição, Configurações e Detalhe da renda variável;
- eixos de gráfico com rótulos repetidos ou arredondados com erro: Economia, dívida e prêmio, Mandato.

São regras, desenhadas uma vez e aplicadas em todo lugar. Uma rodada no canvas, sobre os retratos da F180, decide:
- a escala de texto e a cor dos rótulos no design system;
- o que a tabela larga faz em 1366: esconder colunas, virar cartão por linha ou fixar a primeira coluna;
- a largura máxima da página;
- a regra de altura dos cartões irmãos e o que preenche o vazio;
- o formato dos eixos.

Cada regra aparece num antes e depois de uma tela real. A implementação aplica as regras nos componentes do design system, como variantes e tokens, e nas telas listadas.

**Como roda:** rodada de design em Opus, com o usuário, numa sessão. Se não couber numa sessão, divide-se em cards. A implementação é Sonnet.

**Aceite:** as telas do roteiro da conferência, em 1366×768, sem rolagem lateral, sem elemento passando da borda e sem texto abaixo de 12 px.

<a id="f182"></a>
**F182 — Eleição redesenhada como um conjunto.** Serve N15 e N34. A página da Eleição empilha telas de features desenhadas separadamente (F107, F130, F151, F152). Na conferência visual:
- o Ranking sobrepõe outro cartão;
- o "Partidos na disputa" sobra sozinho na linha;
- o radar sai do painel;
- entre os turnos, três faixas se empilham;
- no "Partidos na disputa" em três colunas:
  - o selo "Computador" passa da borda;
  - o nome do partido corta;
  - as promessas passam da largura;
  - os rótulos do radar cortam;
  - o radar muda de tamanho entre cartões;
  - a legenda mostra "Na fundação" mesmo quando o perfil não mudou.

Uma rodada no canvas, sobre os retratos da Eleição (F180), redesenha a página como um conjunto, em três momentos: na campanha, entre os turnos e no resultado.

**Como roda:** rodada de design em Opus, com o usuário, numa sessão. A implementação é Sonnet.

<a id="f183"></a>
**F183 — Como jogar sem cobrir a tela.** Serve N15 e N25. A aba "Como jogar" sobrepõe os cantos dos cartões em várias telas, e o balão "Tópico sobre esta tela" cobre a boleta e campos de formulário. Uma rodada no canvas, sobre os retratos (F180), decide onde a aba e o balão moram. Algumas saídas possíveis: dentro da topbar, junto da F179; um canto que nenhuma tela usa; o balão só ao passar o mouse.

**Como roda:** rodada de design em Opus, com o usuário, que pode ir junto da F179 se a aba for para a topbar. A implementação é Sonnet.

---

## 💤 Sem prioridade

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Feature | Janela desktop nativa | — | — | — | — | Baixo | Baixo | Baixo | Bom |
| **F37** | Feature | Tema escuro | N15 | — | — | — | Médio | Baixo | Médio | Médio |
| **F60** | Feature | Modo servidor dedicado (--headless) | — | — | — | — | Baixo | Baixo | Baixo | Bom |
| **F69** | Feature | Imprevistos configuráveis e tipos novos | N23 | — | — | — | Médio | Baixo | Médio | Bom |
| **F72** | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | N15 | — | — | — | Médio | Baixo | Médio | Bom |
| **F81** | Manutenção | CORS restrito à mesma origem | — | — | — | [F6](#f6) | Baixo | Médio | Baixo | Médio |
| **F101** | Feature | Carteira separada do jogador | N23 | D9 | M18 · 4.0 | — | Alto | Alto | Médio | Médio |
| **F110** | Feature | Combinar estratégias | N4 | D8 | — | — | Médio | Médio | Médio | Bom |
| **F111** | Feature | Crédito para estratégias e bots | N4, N33 | D8 | — | — | Baixo | Baixo | Médio | Bom |
| **F167** | Feature | Notícias do ativo como marcadores no gráfico de preço | — | — | — | — | Baixo | Baixo | Médio | Bom |
| **F176** | Feature | Cadeiras do Congresso por região | N34 | D19 | — | [F164](#f164) | Médio | Médio | Médio | Médio |
| **F177** | Feature | Marcação a mercado do Tesouro | N34 | — | — | [F165](#f165) | Médio | Médio | Médio | Bom |

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

<a id="f37"></a>
**F37 — Tema escuro.** Serve N15. Hoje só existe o tema claro (F26): o `:root` de `frontend/index.css` é a única fonte dos tokens, e o `@custom-variant dark` ficou inerte.

**Plano.**
1. Desenhar o tema escuro no canvas do Claude Design, sobre as mesmas telas da F26.
2. Reescrever os mesmos tokens num bloco `.dark`, com passos próprios das mesmas rampas, sem inverter as cores claras.
3. Validar as oito cores de gráfico contra a superfície escura com o validador de paleta da skill de dataviz.
4. Fazer o `lightweight-charts` ler as cores do token (`getComputedStyle`) em vez de fixá-las, para o gráfico de velas acompanhar.
5. Criar um card "Aparência" nas Configurações, com claro, escuro ou "seguir o sistema". A escolha fica no `localStorage`, por ser preferência deste navegador; o padrão é seguir o sistema (`prefers-color-scheme`).

**Gatilho:** quando o design escuro estiver fechado no canvas.

<a id="f60"></a>
**F60 — Modo servidor dedicado (`--headless`).** O mesmo executável, sem o navegador: para rodar numa VPS ou num PC ligado direto, sem ninguém jogando nele. `--headless` na linha de comando, ou `[server] headless = true` no `config.toml`, pula o `webbrowser.open` do `main.py`, que hoje roda sempre que o app é o executável, e imprime no terminal os endereços para entrar (o da rede local e, com a F6, o do túnel). O administrador é quem entra com o apelido de `[host] nickname`, que é como o host é definido hoje (`routes/simulation.py`). Como a recuperação de login é por apelido, num servidor exposto à internet qualquer um que digite esse apelido viraria o host; por isso, no modo servidor, o `config.toml` ganha `[host] pin`, e o login com o apelido do host só passa com ele. Serve a quem quer deixar uma sala aberta para os amigos entrarem quando quiserem, sem depender de o host estar com o computador ligado jogando.

<a id="f69"></a>
**F69 — Imprevistos configuráveis e tipos novos.** Serve N23. O modo viver de renda (F53) já nasce com os tipos de imprevisto num registro, em que cada tipo é uma entrada com nome, múltiplo da despesa mensal, efeito (sai do caixa ou corta o salário do mês seguinte) e peso no sorteio; adicionar um tipo é acrescentar uma entrada, sem mexer no motor, no log nem nas telas. Esta feature expõe esse registro ao host: no lobby, o host edita o valor de cada tipo (por exemplo, o conserto passa de 1 para 2 despesas mensais), liga e desliga tipos e cria tipos próprios com nome, valor e efeito. O sorteio continua saindo da semente da partida, então todos os jogadores seguem recebendo os mesmos imprevistos nos mesmos dias, e a configuração vale para a partida salva.

<a id="f72"></a>
**F72 — Gráficos padronizados sobre o `ChartContainer` do shadcn.** Serve N15; continua a padronização da interface no shadcn, que deixou o `shared/components/ui/chart.tsx` sem nenhum consumidor. Hoje cada gráfico Recharts repete o `ResponsiveContainer`, a cor da grade e um array `{ key, label, color }` de séries (que é o `ChartConfig`), e uns cinco cards de tooltip feitos à mão reimplementam o `ChartTooltipContent`. Plano: (1) antes|depois no canvas de `player-line-chart` e `networth-chart` com `ChartContainer` + `ChartTooltipContent`, para aprovar o visual do tooltip (texto menor, indicador) e decidir se o `ui/chart.tsx` ganha variante; (2) convenção de pasta por gráfico: `<nome>-chart/` com `<nome>-chart.tsx` (componente puro, recebe o dado da API por prop), `chart-data.ts` (`ChartConfig`, tipos de linha e `build*`), `chart-legend.tsx` opcional (a legenda clicável que liga e desliga série continua própria) e `index.ts` exportando só o componente; gráfico sem legenda nem transformação fica arquivo solto `<nome>-chart.tsx`; (3) migrar `player-line-chart/` (`utils.ts` + `series.ts` → `chart-data.ts`, sai o tooltip próprio), `networth-chart`, `allocation-donut` e os gráficos embutidos em `composition-tab.tsx` (`AreaChart`) e `risk-tab.tsx` (`ScatterChart`), extraídos para pastas próprias; o `stock-chart` (lightweight-charts, imperativo) fica fora do `ChartContainer`; (4) a seção Gráficos entra em `docs/docs/desenvolvimento/convencoes-frontend.md`. Gatilho: a próxima rodada de design no canvas, ou o próximo gráfico novo.

<a id="f81"></a>
**F81 — CORS restrito à mesma origem.** O backend libera CORS para qualquer origem com credenciais (`allow_origins=["*"]` e `allow_credentials=True` no FastAPI, `cors_allowed_origins="*"` no Socket.IO). Não é necessário: o front é servido pelo próprio backend e, no `pnpm dev`, chega pelo proxy do Vite. Hoje o que protege o jogador de um site malicioso aberto durante a partida é o cookie `client_id` com `SameSite=Lax`, que o navegador não manda em requisição de outro site; o CORS liberado só deixa outro site ler as rotas que não pedem identidade. (1) Sai o `CORSMiddleware` de `main.py`. (2) O Socket.IO fica com `cors_allowed_origins` na mesma origem, mais `http://localhost:5173` quando o modo debug estiver ligado: o proxy do Vite troca o `Host` (`changeOrigin: true`) mas mantém o `Origin` do Vite, e o Socket.IO recusaria a conexão em dev sem essa exceção. (3) Teste manual antes de fechar: jogo pelo `localhost`, por outro computador da LAN pelo IP e pelo `pnpm dev`. Gatilho: junto com o link de convite pela internet, quando o servidor passa a ficar exposto fora da LAN.

<a id="f101"></a>
**F101 — Carteira separada do jogador.** Serve N23; segue a D9. A base da expansão Gestoras (F44): hoje eventos e snapshots pertencem ao jogador (`user_id`), e a gestora precisa de carteira própria. Entra uma tabela `portfolios`, e eventos e snapshots passam a apontar para a carteira; a carteira pessoal de cada jogador é migrada uma a uma, inclusive nas partidas salvas. Nada muda na tela: cada jogador segue com uma carteira só até a F44 existir. Gatilho: a F44 sair da avaliação.

<a id="f110"></a>
**F110 — Combinar estratégias.** Serve N4; segue a D8. O jogador liga mais de uma estratégia ao mesmo tempo, cada uma com uma fatia do patrimônio (ex.: 30% em 100% no CDI e 70% no cruzamento de médias). O motor guarda, por jogador, a lista de estratégias com a fatia de cada uma e a origem de cada posição; cada estratégia recebe um contexto restrito à fatia dela (caixa e posições que ela comprou) e só opera dentro dele. A página de Estratégias passa de um interruptor para uma lista de fatias que somam 100%, e o log de ordens ganha o filtro por estratégia. Gatilho: F8 concluída e o uso pedir mais de uma estratégia.

<a id="f111"></a>
**F111 — Crédito para estratégias e bots.** Serve N4 e N33; segue a D8. O contexto da estratégia ganha a dívida, a nota de risco e a oferta do dia, e as ações ganham pegar empréstimo, amortizar e quitar, que chamam o mesmo serviço da tela de Crédito em nome do jogador. Uma estratégia de exemplo alavancada (ex.: rebalanceamento por meta com 20% emprestado) mostra o uso e entra na lista dos bots. O log da estratégia registra cada contratação e pagamento com o motivo. Gatilho: F8 e F94 concluídas.

<a id="f167"></a>
**F167 — Notícias do ativo como marcadores no gráfico de preço.** Serve N31. As manchetes de empresas do noticiário (F92) aparecem também na tela do ativo, como marcadores no gráfico de preço, com a manchete ao passar o mouse. Separada da F92 em 29/out: o noticiário sai na 3.1 só com as manchetes, e os marcadores pedem desenho no canvas antes do código. Gatilho: F92 concluída.

<a id="f176"></a>
**F176 — Cadeiras do Congresso por região.** Serve N34; upgrade do mapa por região (F164). Na Câmara real nenhum estado tem menos de 8 nem mais de 70 deputados, e o Norte e o Centro-Oeste valem mais em cadeiras do que em eleitores: o Norte tem 65 de 513 cadeiras (12,7%) com 8,1% do eleitorado, e o Sudeste 179 (34,9%) com 42,6%. As 101 cadeiras se repartem na proporção das 513: Sudeste 35, Nordeste 30, Sul 15, Norte 13, Centro-Oeste 8. Cada região reparte as dela pelo D'Hondt de `house.distribute` com o voto da região; a barreira continua nacional. Ganhar o Norte passa a valer mais no Congresso do que na urna, uma decisão de campanha real. Fica depois do mapa porque mexe no modelo das cadeiras.

<a id="f177"></a>
**F177 — Marcação a mercado do Tesouro.** Serve N34; upgrade da tela do Tesouro (F165). Na vida real, quem compra um Prefixado e vê as taxas subirem perde dinheiro se vender antes do vencimento: um título de 12% ao ano vale menos quando o mercado paga 15%, porque ninguém paga o mesmo preço por 12% podendo ter 15%. Os títulos do Tesouro ganham resgate antes do vencimento: o Selic pelo valor acumulado, o Prefixado e o IPCA+ pelo preço unitário de hoje, o valor no vencimento trazido a valor presente pela taxa atual do mesmo tipo (taxa base mais o prêmio de risco de hoje). A carteira mostra o ganho ou a perda da marcação ao lado do rendimento. O risco do governo fica palpável para quem investe, e o presidente com Prefixado na carteira perde com a própria gastança. Fica separado porque mexe na renda fixa toda (`liquidity.py`, `fixed_broker.redeem`), que hoje só resgata antes do vencimento o que tem liquidez diária.

---

## ✅ Concluído

> Nenhum item neste status.

---

## 🚫 Descartado

> Nenhum item neste status.
