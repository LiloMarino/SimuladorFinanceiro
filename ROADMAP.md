<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/atualizar/concluir/descartar/remover um item, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban do projeto, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que ordem e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-11-20):** Triado o playtest de 20/11: consertos das gestoras e do lobby, voto dos bots na taxa, Estratégias na conta ativa e ações sem espera em velocidade alta, no começo da 4.3

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Tipo | Resumo | Marco | Condiciona (F#) | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **N1** | — | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — | — | — | — |
| **N2** | — | Jogar com amigos pela internet sem que cada um instale uma VPN | — | [F5](#f5), [F6](#f6) | — | — | — |
| **N3** | — | Confiar que os números do simulador são exatos e reprodutíveis | — | — | — | — | — |
| **N4** | — | Testar uma estratégia de investimento automática e ver como ela se sai | — | [F110](#f110), [F111](#f111), [F197](#f197), [F279](#f279), [F319](#f319) | — | — | — |
| **N7** | — | Que o simulador cobre os custos de operar do mercado real | — | — | — | — | — |
| **N8** | — | Jogar contra oponentes controlados pelo computador | — | [F279](#f279) | — | — | — |
| **N9** | — | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — | — | — | — |
| **N10** | — | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | — | [F28](#f28), [F202](#f202) | — | — | — |
| **N11** | — | Que o cenário econômico simulado seja o histórico real | — | — | — | — | — |
| **N12** | — | Continuar jogando depois do último dia com dado real | — | — | — | — | — |
| **N13** | — | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | — | — | — | — |
| **N14** | — | Atualizar para uma versão nova sem perder as partidas salvas | — | [F56](#f56) | — | — | — |
| **N15** | — | Usar uma interface agradável e coerente, à altura de um jogo | — | [F37](#f37), [F72](#f72), [F123](#f123), [F316](#f316), [F317](#f317) | — | — | — |
| **N19** | — | Analisar um ativo com as ferramentas de um trader | — | [F34](#f34), [F131](#f131), [F193](#f193) | — | — | — |
| **N20** | — | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | [F285](#f285) | — | — | — |
| **N21** | — | Jogar "na unha", sem a interface apontar a melhor escolha | — | — | — | — | — |
| **N22** | — | Ter objetivos para buscar além de vencer a partida | — | [F90](#f90), [F123](#f123), [F159](#f159) | — | — | — |
| **N23** | — | Jogar com os amigos de outras formas além de cada um por si | — | [F316](#f316), [F317](#f317), [F318](#f318), [F319](#f319), [F337](#f337) | — | — | — |
| **N24** | — | Saber onde está a lentidão durante uma partida | — | — | — | — | — |
| **N25** | — | Entender o que é o simulador e como se joga, sem ler um manual | — | [F132](#f132), [F133](#f133), [F139](#f139), [F140](#f140), [F141](#f141), [F158](#f158), [F193](#f193), [F225](#f225) | — | — | — |
| **N26** | — | Achar a causa de um erro sem vasculhar o log inteiro | — | — | — | — | — |
| **N31** | — | Saber o que está movendo o mercado da partida, como quem lê o noticiário | — | [F93](#f93) | — | — | — |
| **N33** | — | Investir com dinheiro emprestado, pagando o juro do momento | — | [F111](#f111) | — | — | — |
| **N34** | — | Disputar o poder de mudar as regras da economia da partida | — | [F176](#f176), [F227](#f227), [F284](#f284), [F317](#f317) | — | — | — |
| **N39** | — | Chegar ao primeiro dia da partida com as próprias escolhas já feitas | — | [F315](#f315), [F321](#f321), [F322](#f322), [F323](#f323), [F324](#f324), [F325](#f325), [F326](#f326), [F327](#f327), [F328](#f328), [F329](#f329), [F330](#f330), [F331](#f331), [F332](#f332), [F333](#f333), [F334](#f334) | — | — | — |
| **N40** | — | Jogar partidas longas e na velocidade máxima sem a tela travar | — | [F221](#f221), [F320](#f320) | — | — | — |
| **N41** | — | Aprender como a economia real funciona, jogando | — | [F225](#f225), [F227](#f227) | — | — | — |
| **N42** | — | Chegar a um estado da partida sem jogar até ele | — | [F286](#f286) | — | — | — |
| **N43** | — | Operar como numa corretora de verdade: proteger a posição e ganhar também na queda | — | [F335](#f335), [F336](#f336) | — | — | — |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | M27 · 4.6 | — | — | — | 🔍 |
| [**F6**](#f6) | Feature | Link de convite pela internet no lobby | M27 · 4.6 | — | Médio | Bom | ⏳ |
| [**F14**](#f14) | Feature | Janela desktop nativa | M27 · 4.6 | — | Baixo | Bom | ⏳ |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | M25 · 4.5 | — | Alto | Bom | ⏳ |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | M24 · 4.4 | — | — | — | 🔍 |
| [**F37**](#f37) | Feature | Tema escuro | M28 · 4.7 | — | Médio | Médio | ⏳ |
| [**F56**](#f56) | Feature | Novidades no app | M27 · 4.6 | — | Baixo | Bom | ⏳ |
| [**F60**](#f60) | Feature | Modo servidor dedicado (--headless) | M27 · 4.6 | — | Baixo | Bom | ⏳ |
| [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | M24 · 4.4 | — | Médio | Bom | ⏳ |
| [**F81**](#f81) | Manutenção | CORS restrito à mesma origem | M27 · 4.6 | — | Baixo | Médio | ⏳ |
| [**F90**](#f90) | Feature | Cenários | M25 · 4.5 | — | Alto | Bom | ⏳ |
| [**F93**](#f93) | Feature | Rumores antecipados | M25 · 4.5 | — | Médio | Médio | ⏳ |
| [**F110**](#f110) | Feature | Combinar estratégias | M25 · 4.5 | — | Médio | Bom | ⏳ |
| [**F111**](#f111) | Feature | Crédito para estratégias e bots | M29 · 4.3 | — | Baixo | Bom | ⏳ |
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | M28 · 4.7 | — | — | — | 🔍 |
| [**F131**](#f131) | Feature | Catálogo de padrões de vela | M28 · 4.7 | — | — | — | 🔍 |
| [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | M28 · 4.7 | — | Médio | Bom | ⏳ |
| [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | M28 · 4.7 | — | Baixo | Bom | ⏳ |
| [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | M28 · 4.7 | — | Médio | Bom | ⏳ |
| [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | M28 · 4.7 | — | Alto | Bom | ⏳ |
| [**F141**](#f141) | Docs | README com as features de hoje | M28 · 4.7 | — | Baixo | Excelente | ⏳ |
| [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | M28 · 4.7 | — | — | — | 🔍 |
| [**F159**](#f159) | Feature | Rodada de novas conquistas e revisão das existentes | M28 · 4.7 | — | — | — | 🔍 |
| [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | M24 · 4.4 | — | Baixo | Bom | ⏳ |
| [**F176**](#f176) | Feature | Cadeiras do Congresso por região | — | — | Médio | Médio | 💤 |
| [**F193**](#f193) | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | M28 · 4.7 | — | — | — | 🔍 |
| [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | M24 · 4.4 | — | Médio | Bom | ⏳ |
| [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | M25 · 4.5 | — | — | — | 🔍 |
| [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | M24 · 4.4 | — | Médio | Bom | ⏳ |
| [**F225**](#f225) | Docs | Conceitos de economia real na docs e nomeados na tela | M28 · 4.7 | — | Alto | Bom | ⏳ |
| [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | M28 · 4.7 | — | Alto | Médio | ⏳ |
| [**F279**](#f279) | Feature | Estratégias automáticas novas e revisão das atuais | M24 · 4.4 | — | — | — | 🔍 |
| [**F284**](#f284) | Feature | Ministério para o partido da base | — | — | Alto | Médio | ⏳ |
| [**F285**](#f285) | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | — | — | — | — | 🔍 |
| [**F286**](#f286) | Feature | Comandos de trapaça no modo debug | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F315**](#f315) | Feature | Base das mecânicas de profissão: página Profissão, política razoável e troca no meio da partida | M29 · 4.3 | — | Alto | Bom | ⏳ |
| [**F320**](#f320) | Performance | Ações do jogador sem espera em velocidade alta | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F321**](#f321) | Feature | Séries do preço de imóvel, do IGP-M e da TR | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F322**](#f322) | Feature | FGTS e hora extra do CLT | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F323**](#f323) | Feature | Consignado do Servidor | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F324**](#f324) | Feature | CDB da casa do Bancário | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F325**](#f325) | Feature | Trava de câmbio e mix de exportação do Exportador | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F326**](#f326) | Feature | Tabela de preços do Autônomo | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F327**](#f327) | Feature | Reinvestimento do Empreendedor | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F328**](#f328) | Feature | Previdência do Aposentado | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F329**](#f329) | Feature | Pé-de-Meia, tarifa social e curso técnico do Auxílio | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F330**](#f330) | Feature | Relatório da casa do Corretor | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F331**](#f331) | Feature | Escada acadêmica do Recém-formado | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F332**](#f332) | Feature | Imóveis do Locador | M29 · 4.3 | — | Alto | Bom | ⏳ |
| [**F333**](#f333) | Feature | Administrador, a profissão que troca de setor | M29 · 4.3 | — | Alto | Bom | ⏳ |
| [**F334**](#f334) | Feature | Calibração das profissões pelos três alarmes | M29 · 4.3 | — | Médio | Bom | ⏳ |
| [**F335**](#f335) | Feature | Venda a descoberto e aluguel de ações | M24 · 4.4 | — | Alto | Médio | ⏳ |
| [**F336**](#f336) | Feature | Ordem stop e validade na boleta | M24 · 4.4 | — | Médio | Bom | ⏳ |

<details>
<summary><strong>Concluído / decidido / descartado (27 itens — clique pra expandir)</strong></summary>

| ID | Tipo | Resumo | Marco | Condiciona (F#) | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **D1** | — | Eventos são a fonte da verdade; snapshots são derivados | — | [F159](#f159) | — | — | ✅ |
| **D2** | — | Cálculo financeiro acontece só no backend; o frontend exibe | — | — | — | — | ✅ |
| **D3** | — | Dinheiro e quantidade trafegam como Decimal serializado em string | — | — | — | — | ✅ |
| **D4** | — | Banco de dados embarcado no executável | — | — | — | — | ✅ |
| **D6** | — | A retomada continua no dia seguinte ao último evento | — | — | — | — | ✅ |
| **D7** | — | O simulador lê as séries sem saber a origem | — | [F28](#f28) | — | — | ✅ |
| **D8** | — | Bot, modo automático e backtest são o mesmo mecanismo | — | [F110](#f110), [F111](#f111), [F202](#f202) | — | — | ✅ |
| **D9** | — | De onde nasce uma mudança de schema | — | — | — | — | ✅ |
| **D10** | — | Como a nota geral é calculada | — | — | — | — | ✅ |
| **D11** | — | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | — | — | — | ✅ |
| **D12** | — | Como numerar as versões | — | — | — | — | ✅ |
| **D13** | — | Um canal de tempo real só: Socket.IO, com fallback de polling | — | — | — | — | ✅ |
| **D14** | — | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | — | — | — | — | ✅ |
| **D15** | — | Lint com oxlint, formatação com oxfmt e o TypeScript 7 com a API do 6 ao lado | — | — | — | — | ✅ |
| **D16** | — | Estratégias do app no host, personalização pela API | — | — | — | — | ✅ |
| **D17** | — | Os tópicos do tutorial se animam em código, com o motion | — | — | — | — | ✅ |
| **D18** | — | Uma migration por versão; caminho antigo só cai numa major | — | [F90](#f90), [F93](#f93) | — | — | ✅ |
| **D19** | — | O eleitorado são grupos, cada um com apoio e rejeição por partido | — | [F176](#f176) | — | — | ✅ |
| **D20** | — | A economia da partida é a história mais o desvio que o governo causa | — | [F227](#f227) | — | — | ✅ |
| **D21** | — | O jogo ensina a jogar, a docs explica o modelo | — | [F132](#f132), [F133](#f133), [F140](#f140), [F193](#f193), [F225](#f225), [F227](#f227) | — | — | ✅ |
| **D22** | — | O k do impacto de preço fica sem teto, avisa acima de 0,10, e o impacto vale só do pregão seguinte | — | — | — | — | ✅ |
| **D23** | — | A profissão é uma classe: cada uma tem uma ação própria ligada à macroeconomia | — | [F315](#f315), [F321](#f321), [F322](#f322), [F323](#f323), [F324](#f324), [F325](#f325), [F326](#f326), [F327](#f327), [F328](#f328), [F329](#f329), [F330](#f330), [F331](#f331), [F332](#f332), [F333](#f333), [F334](#f334) | — | — | ✅ |
| [**F316**](#f316) | Correção | Correções do playtest: gestoras e cotas | M29 · 4.3 | — | — | — | ✅ |
| [**F317**](#f317) | Correção | Correções do playtest: lobby, aporte no Fundo Soberano, dicas ⓘ e fim da aquisição hostil | M29 · 4.3 | — | — | — | ✅ |
| [**F318**](#f318) | Feature | Bots cotistas e o Mercado votam o aumento de taxa pelo desempenho | M29 · 4.3 | — | — | — | ✅ |
| [**F319**](#f319) | Melhoria | Página Estratégias segue a conta ativa | M29 · 4.3 | — | — | — | ✅ |
| [**F337**](#f337) | Feature | Mercado e bots cotistas compram a emissão pelo desempenho e pelo ágio | M29 · 4.3 | — | — | — | ✅ |

</details>

---

## 🚀 Próximas versões

> O que entra em cada versão, na ordem de trabalho. Item arquivado conta como concluído.

### 4.3 — Profissões (M29)

> **Objetivo:** Cada profissão ganha uma mecânica própria ligada à macroeconomia, como uma classe de RPG: nenhuma é ruim e cada uma tem como sair na frente se bem jogada; chega o Administrador, que troca de setor, os bots usam as mecânicas e tomam crédito, o modo debug ganha comandos para testar, e a calibração confere três alarmes contra o poupador da sala.
>
> **Serve:** N39, N23, N4, N40, N15, N34
>
> **Progresso:** 5/23 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F316**](#f316) | Correção | Correções do playtest: gestoras e cotas | — | ✅ Concluído |
| 2 | [**F317**](#f317) | Correção | Correções do playtest: lobby, aporte no Fundo Soberano, dicas ⓘ e fim da aquisição hostil | — | ✅ Concluído |
| 3 | [**F318**](#f318) | Feature | Bots cotistas e o Mercado votam o aumento de taxa pelo desempenho | — | ✅ Concluído |
| 4 | [**F337**](#f337) | Feature | Mercado e bots cotistas compram a emissão pelo desempenho e pelo ágio | — | ✅ Concluído |
| 5 | [**F319**](#f319) | Melhoria | Página Estratégias segue a conta ativa | — | ✅ Concluído |
| 6 | [**F320**](#f320) | Performance | Ações do jogador sem espera em velocidade alta | — | ⏳ Pendente |
| 7 | [**F315**](#f315) | Feature | Base das mecânicas de profissão: página Profissão, política razoável e troca no meio da partida | — | ⏳ Pendente |
| 8 | [**F321**](#f321) | Feature | Séries do preço de imóvel, do IGP-M e da TR | — | ⏳ Pendente |
| 9 | [**F322**](#f322) | Feature | FGTS e hora extra do CLT | [F315](#f315), [F321](#f321) | ⏳ Pendente |
| 10 | [**F323**](#f323) | Feature | Consignado do Servidor | [F315](#f315) | ⏳ Pendente |
| 11 | [**F324**](#f324) | Feature | CDB da casa do Bancário | [F315](#f315) | ⏳ Pendente |
| 12 | [**F325**](#f325) | Feature | Trava de câmbio e mix de exportação do Exportador | [F315](#f315) | ⏳ Pendente |
| 13 | [**F326**](#f326) | Feature | Tabela de preços do Autônomo | [F315](#f315) | ⏳ Pendente |
| 14 | [**F327**](#f327) | Feature | Reinvestimento do Empreendedor | [F315](#f315) | ⏳ Pendente |
| 15 | [**F328**](#f328) | Feature | Previdência do Aposentado | [F315](#f315) | ⏳ Pendente |
| 16 | [**F329**](#f329) | Feature | Pé-de-Meia, tarifa social e curso técnico do Auxílio | [F315](#f315) | ⏳ Pendente |
| 17 | [**F330**](#f330) | Feature | Relatório da casa do Corretor | [F315](#f315) | ⏳ Pendente |
| 18 | [**F331**](#f331) | Feature | Escada acadêmica do Recém-formado | [F315](#f315) | ⏳ Pendente |
| 19 | [**F332**](#f332) | Feature | Imóveis do Locador | [F315](#f315), [F321](#f321) | ⏳ Pendente |
| 20 | [**F333**](#f333) | Feature | Administrador, a profissão que troca de setor | [F315](#f315) | ⏳ Pendente |
| 21 | [**F111**](#f111) | Feature | Crédito para estratégias e bots | — | ⏳ Pendente |
| 22 | [**F286**](#f286) | Feature | Comandos de trapaça no modo debug | [F54](#f54) | ⏳ Pendente |
| 23 | [**F334**](#f334) | Feature | Calibração das profissões pelos três alarmes | [F322](#f322), [F323](#f323), [F324](#f324), [F325](#f325), [F326](#f326), [F327](#f327), [F328](#f328), [F329](#f329), [F330](#f330), [F331](#f331), [F332](#f332), [F333](#f333) | ⏳ Pendente |

### 4.4 — Mesa do trader (M24)

> **Objetivo:** O detalhe do ativo vira mesa de operação: a lista de ações aguenta muitas ações, o gráfico abre em tela cheia com as notícias marcadas, o livro de ofertas e o rebalanceamento por meta chegam, e os gráficos seguem um molde só.
>
> **Serve:** N19, N15, N4
>
> **Progresso:** 0/8 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | — | ⏳ Pendente |
| 2 | [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 Em avaliação |
| 3 | [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | — | ⏳ Pendente |
| 4 | [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | — | ⏳ Pendente |
| 5 | [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | — | ⏳ Pendente |
| 6 | [**F279**](#f279) | Feature | Estratégias automáticas novas e revisão das atuais | — | 🔍 Em avaliação |
| 7 | [**F335**](#f335) | Feature | Venda a descoberto e aluguel de ações | — | ⏳ Pendente |
| 8 | [**F336**](#f336) | Feature | Ordem stop e validade na boleta | — | ⏳ Pendente |

### 4.5 — Futuros, cenários e estratégias (M25)

> **Objetivo:** A partida testa a carteira em muitos futuros e em cenários com objetivo, com bots que combinam estratégias e tomam crédito, e o backtest corre rápido.
>
> **Serve:** N10, N12, N22, N31
>
> **Progresso:** 0/5 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | — | 🔍 Em avaliação |
| 2 | [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | — | ⏳ Pendente |
| 3 | [**F90**](#f90) | Feature | Cenários | — | ⏳ Pendente |
| 4 | [**F93**](#f93) | Feature | Rumores antecipados | — | ⏳ Pendente |
| 5 | [**F110**](#f110) | Feature | Combinar estratégias | — | ⏳ Pendente |

### 4.6 — Jogo pela internet e servidor (M27)

> **Objetivo:** Amigos de longe entram na sala por um link de convite, o servidor roda sem tela e com CORS certo, o jogo abre numa janela própria e o app conta o que há de novo.
>
> **Serve:** N2, N14
>
> **Progresso:** 0/6 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | — | 🔍 Em avaliação |
| 2 | [**F6**](#f6) | Feature | Link de convite pela internet no lobby | [F5](#f5) | ⏳ Pendente |
| 3 | [**F81**](#f81) | Manutenção | CORS restrito à mesma origem | [F6](#f6) | ⏳ Pendente |
| 4 | [**F60**](#f60) | Feature | Modo servidor dedicado (--headless) | — | ⏳ Pendente |
| 5 | [**F14**](#f14) | Feature | Janela desktop nativa | — | ⏳ Pendente |
| 6 | [**F56**](#f56) | Feature | Novidades no app | — | ⏳ Pendente |

### 4.7 — Ensino (M28)

> **Objetivo:** O Como jogar ensina o jogo e os conceitos sobre as telas mais recentes, o jogo ganha o tema escuro, e a docs, a demonstração e o README mostram o jogo com tudo que entrou.
>
> **Serve:** N25, N19, N22, N15, N41
>
> **Progresso:** 0/13 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | — | 🔍 Em avaliação |
| 2 | [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | — | ⏳ Pendente |
| 3 | [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | — | ⏳ Pendente |
| 4 | [**F131**](#f131) | Feature | Catálogo de padrões de vela | — | 🔍 Em avaliação |
| 5 | [**F193**](#f193) | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | [F158](#f158) | 🔍 Em avaliação |
| 6 | [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | — | 🔍 Em avaliação |
| 7 | [**F159**](#f159) | Feature | Rodada de novas conquistas e revisão das existentes | [F123](#f123) | 🔍 Em avaliação |
| 8 | [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | — | ⏳ Pendente |
| 9 | [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | — | ⏳ Pendente |
| 10 | [**F225**](#f225) | Docs | Conceitos de economia real na docs e nomeados na tela | [F140](#f140) | ⏳ Pendente |
| 11 | [**F37**](#f37) | Feature | Tema escuro | — | ⏳ Pendente |
| 12 | [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | — | ⏳ Pendente |
| 13 | [**F141**](#f141) | Docs | README com as features de hoje | [F139](#f139) | ⏳ Pendente |

### Sem versão

> Os itens ⏳ e 🔍 que ainda não entraram em nenhuma versão, do que mais destrava trabalho para o que menos ("Destrava" é quantos itens em aberto esperam por aquele). É daqui que sai a próxima versão; os 💤 ficam só no kanban.

| ID | Tipo | Resumo | Serve | Depende de | Destrava | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [**F284**](#f284) | Feature | Ministério para o partido da base | N34 | — | 0 | ⏳ Pendente |
| [**F285**](#f285) | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | N20 | — | 0 | 🔍 Em avaliação |

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: os itens que podem ser pegos agora, com toda dependência já ✅. A ordem segue o plano: primeiro os itens de cada versão (ou marco) na ordem dele, depois o resto pelo "Destrava", que é quantos itens em aberto esperam por aquele, direta ou indiretamente. 💤 (sem prioridade) e 🚫 não entram.

| ID | Tipo | Resumo | Marco | Destrava | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [**F320**](#f320) | Performance | Ações do jogador sem espera em velocidade alta | M29 · 4.3 · 6º | 0 | Médio | Bom | ⏳ |
| [**F315**](#f315) | Feature | Base das mecânicas de profissão: página Profissão, política razoável e troca no meio da partida | M29 · 4.3 · 7º | 13 | Alto | Bom | ⏳ |
| [**F321**](#f321) | Feature | Séries do preço de imóvel, do IGP-M e da TR | M29 · 4.3 · 8º | 3 | Médio | Bom | ⏳ |
| [**F111**](#f111) | Feature | Crédito para estratégias e bots | M29 · 4.3 · 21º | 0 | Baixo | Bom | ⏳ |
| [**F286**](#f286) | Feature | Comandos de trapaça no modo debug | M29 · 4.3 · 22º | 0 | Médio | Bom | ⏳ |
| [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | M24 · 4.4 · 1º | 0 | Médio | Bom | ⏳ |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | M24 · 4.4 · 2º | 0 | — | — | 🔍 |
| [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | M24 · 4.4 · 3º | 0 | Médio | Bom | ⏳ |
| [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | M24 · 4.4 · 4º | 0 | Baixo | Bom | ⏳ |
| [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | M24 · 4.4 · 5º | 0 | Médio | Bom | ⏳ |
| [**F279**](#f279) | Feature | Estratégias automáticas novas e revisão das atuais | M24 · 4.4 · 6º | 0 | — | — | 🔍 |
| [**F335**](#f335) | Feature | Venda a descoberto e aluguel de ações | M24 · 4.4 · 7º | 0 | Alto | Médio | ⏳ |
| [**F336**](#f336) | Feature | Ordem stop e validade na boleta | M24 · 4.4 · 8º | 0 | Médio | Bom | ⏳ |
| [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | M25 · 4.5 · 1º | 0 | — | — | 🔍 |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | M25 · 4.5 · 2º | 0 | Alto | Bom | ⏳ |
| [**F90**](#f90) | Feature | Cenários | M25 · 4.5 · 3º | 0 | Alto | Bom | ⏳ |
| [**F93**](#f93) | Feature | Rumores antecipados | M25 · 4.5 · 4º | 0 | Médio | Médio | ⏳ |
| [**F110**](#f110) | Feature | Combinar estratégias | M25 · 4.5 · 5º | 0 | Médio | Bom | ⏳ |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | M27 · 4.6 · 1º | 2 | — | — | 🔍 |
| [**F60**](#f60) | Feature | Modo servidor dedicado (--headless) | M27 · 4.6 · 4º | 0 | Baixo | Bom | ⏳ |
| [**F14**](#f14) | Feature | Janela desktop nativa | M27 · 4.6 · 5º | 0 | Baixo | Bom | ⏳ |
| [**F56**](#f56) | Feature | Novidades no app | M27 · 4.6 · 6º | 0 | Baixo | Bom | ⏳ |
| [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | M28 · 4.7 · 1º | 1 | — | — | 🔍 |
| [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | M28 · 4.7 · 2º | 0 | Médio | Bom | ⏳ |
| [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | M28 · 4.7 · 3º | 0 | Baixo | Bom | ⏳ |
| [**F131**](#f131) | Feature | Catálogo de padrões de vela | M28 · 4.7 · 4º | 0 | — | — | 🔍 |
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | M28 · 4.7 · 6º | 1 | — | — | 🔍 |
| [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | M28 · 4.7 · 8º | 0 | Alto | Médio | ⏳ |
| [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | M28 · 4.7 · 9º | 1 | Alto | Bom | ⏳ |
| [**F37**](#f37) | Feature | Tema escuro | M28 · 4.7 · 11º | 0 | Médio | Médio | ⏳ |
| [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | M28 · 4.7 · 12º | 1 | Médio | Bom | ⏳ |
| [**F284**](#f284) | Feature | Ministério para o partido da base | — | 0 | Alto | Médio | ⏳ |
| [**F285**](#f285) | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | — | 0 | — | — | 🔍 |

---

## ⏳ Pendente

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F6** | Feature | Link de convite pela internet no lobby | N2 | — | M27 · 4.6 | [F5](#f5) | Médio | Médio | Alto | Bom |
| **F14** | Feature | Janela desktop nativa | — | — | M27 · 4.6 | — | Baixo | Baixo | Baixo | Bom |
| **F28** | Feature | Muitos futuros (Monte Carlo) | N10 | D7 | M25 · 4.5 | — | Alto | Alto | Alto | Bom |
| **F37** | Feature | Tema escuro | N15 | — | M28 · 4.7 | — | Médio | Baixo | Médio | Médio |
| **F56** | Feature | Novidades no app | N14 | — | M27 · 4.6 | — | Baixo | Baixo | Médio | Bom |
| **F60** | Feature | Modo servidor dedicado (--headless) | — | — | M27 · 4.6 | — | Baixo | Baixo | Baixo | Bom |
| **F72** | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | N15 | — | M24 · 4.4 | — | Médio | Baixo | Médio | Bom |
| **F81** | Manutenção | CORS restrito à mesma origem | — | — | M27 · 4.6 | [F6](#f6) | Baixo | Médio | Baixo | Médio |
| **F90** | Feature | Cenários | N22 | D18 | M25 · 4.5 | — | Alto | Médio | Alto | Bom |
| **F93** | Feature | Rumores antecipados | N31 | D18 | M25 · 4.5 | — | Médio | Médio | Médio | Médio |
| **F110** | Feature | Combinar estratégias | N4 | D8 | M25 · 4.5 | — | Médio | Médio | Médio | Bom |
| **F111** | Feature | Crédito para estratégias e bots | N4, N33 | D8 | M29 · 4.3 | — | Baixo | Baixo | Médio | Bom |
| **F132** | Feature | Tópicos de "como se joga" do Como jogar | N25 | D21 | M28 · 4.7 | — | Médio | Baixo | Alto | Bom |
| **F133** | Feature | Tópicos de conceitos do Como jogar | N25 | D21 | M28 · 4.7 | — | Baixo | Baixo | Médio | Bom |
| **F139** | Docs | Demonstração regravada com o jogo de hoje | N25 | — | M28 · 4.7 | — | Médio | Baixo | Alto | Bom |
| **F140** | Docs | Docs reorganizada por tipo de leitor | N25 | D21 | M28 · 4.7 | — | Alto | Baixo | Alto | Bom |
| **F141** | Docs | README com as features de hoje | N25 | — | M28 · 4.7 | [F139](#f139) | Baixo | Baixo | Alto | Excelente |
| **F167** | Feature | Notícias do ativo como marcadores no gráfico de preço | — | — | M24 · 4.4 | — | Baixo | Baixo | Médio | Bom |
| **F197** | Melhoria | Rebalanceamento por meta com várias classes | N4 | — | M24 · 4.4 | — | Médio | Médio | Médio | Bom |
| **F221** | Performance | Lista de ações que aguenta muitas ações | N40 | — | M24 · 4.4 | — | Médio | Médio | Médio | Bom |
| **F225** | Docs | Conceitos de economia real na docs e nomeados na tela | N41, N25 | D21 | M28 · 4.7 | [F140](#f140) | Alto | Baixo | Alto | Bom |
| **F227** | Feature | Intensidade das ligações e laboratório da economia | N41, N34 | D20, D21 | M28 · 4.7 | — | Alto | Médio | Médio | Médio |
| **F284** | Feature | Ministério para o partido da base | N34 | — | — | — | Alto | Médio | Médio | Médio |
| **F286** | Feature | Comandos de trapaça no modo debug | N42 | — | M29 · 4.3 | [F54](#f54) | Médio | Baixo | Alto | Bom |
| **F315** | Feature | Base das mecânicas de profissão: página Profissão, política razoável e troca no meio da partida | N39 | D23 | M29 · 4.3 | — | Alto | Médio | Alto | Bom |
| **F320** | Performance | Ações do jogador sem espera em velocidade alta | N40 | — | M29 · 4.3 | — | Médio | Médio | Alto | Bom |
| **F321** | Feature | Séries do preço de imóvel, do IGP-M e da TR | N39 | D23 | M29 · 4.3 | — | Médio | Baixo | Médio | Bom |
| **F322** | Feature | FGTS e hora extra do CLT | N39 | D23 | M29 · 4.3 | [F315](#f315), [F321](#f321) | Médio | Baixo | Alto | Bom |
| **F323** | Feature | Consignado do Servidor | N39 | D23 | M29 · 4.3 | [F315](#f315) | Médio | Baixo | Alto | Bom |
| **F324** | Feature | CDB da casa do Bancário | N39 | D23 | M29 · 4.3 | [F315](#f315) | Médio | Baixo | Alto | Bom |
| **F325** | Feature | Trava de câmbio e mix de exportação do Exportador | N39 | D23 | M29 · 4.3 | [F315](#f315) | Médio | Médio | Alto | Bom |
| **F326** | Feature | Tabela de preços do Autônomo | N39 | D23 | M29 · 4.3 | [F315](#f315) | Médio | Baixo | Alto | Bom |
| **F327** | Feature | Reinvestimento do Empreendedor | N39 | D23 | M29 · 4.3 | [F315](#f315) | Médio | Médio | Alto | Bom |
| **F328** | Feature | Previdência do Aposentado | N39 | D23 | M29 · 4.3 | [F315](#f315) | Médio | Médio | Alto | Bom |
| **F329** | Feature | Pé-de-Meia, tarifa social e curso técnico do Auxílio | N39 | D23 | M29 · 4.3 | [F315](#f315) | Médio | Baixo | Alto | Bom |
| **F330** | Feature | Relatório da casa do Corretor | N39 | D23 | M29 · 4.3 | [F315](#f315) | Médio | Baixo | Alto | Bom |
| **F331** | Feature | Escada acadêmica do Recém-formado | N39 | D23 | M29 · 4.3 | [F315](#f315) | Médio | Médio | Alto | Bom |
| **F332** | Feature | Imóveis do Locador | N39 | D23 | M29 · 4.3 | [F315](#f315), [F321](#f321) | Alto | Alto | Alto | Bom |
| **F333** | Feature | Administrador, a profissão que troca de setor | N39 | D23 | M29 · 4.3 | [F315](#f315) | Alto | Alto | Alto | Bom |
| **F334** | Feature | Calibração das profissões pelos três alarmes | N39 | D23 | M29 · 4.3 | [F322](#f322), [F323](#f323), [F324](#f324), [F325](#f325), [F326](#f326), [F327](#f327), [F328](#f328), [F329](#f329), [F330](#f330), [F331](#f331), [F332](#f332), [F333](#f333) | Médio | Médio | Alto | Bom |
| **F335** | Feature | Venda a descoberto e aluguel de ações | N43 | — | M24 · 4.4 | — | Alto | Alto | Alto | Médio |
| **F336** | Feature | Ordem stop e validade na boleta | N43 | — | M24 · 4.4 | — | Médio | Baixo | Médio | Bom |

<a id="f6"></a>
**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Abrir para a internet exige fechar antes a tomada do host: hoje ser host é ter o nickname do `config.toml`, e com o host desconectado qualquer jogador assume esse nickname por `/api/user/claim` e passa a poder parar a partida e apagar partidas salvas. O app gera um segredo a cada abertura e abre o navegador do host com ele; o servidor reconhece como host só a sessão que apresentou o segredo, e `/api/user/claim` recusa o nickname do host. O endereço de origem não distingue o host, porque num túnel o tráfego de fora costuma chegar ao servidor pela própria máquina. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada; com o host desconectado, nenhum outro jogador consegue virar host.

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

<a id="f28"></a>
**F28 — Muitos futuros (Monte Carlo).** Serve N10; condicionado por D7. Pede um plano de implementação em Opus antes do Sonnet: a orquestração de 100 partidas, a partida ativa única e a limpeza.

**O que o jogador passa a poder fazer.** Em vez de testar a estratégia num futuro gerado só, testá-la em muitos (ex.: 100, cada um com uma semente) e ver o resultado como distribuição: "perdeu para o CDI em 23 de 100 futuros; no pior, −35%; no do meio, +40% em 5 anos". Monte Carlo é a técnica de repetir a simulação com sorteios diferentes para ver a faixa de resultados possíveis, e não um só; a semente é o número que fixa o sorteio, então a mesma semente gera o mesmo futuro. Lê-se pela fração de futuros ruins e pelo pior caso: poucos futuros perdendo para o CDI é bom; uma estratégia que só ganha no histórico real e perde na maioria dos futuros plausíveis teve sorte, não mérito. É o backtest da F19 repetido sobre gerações do gerador da D14.

**Decisão.** Cada futuro é uma versão descartável na dimensão de versão da D7, um futuro por vez. Para cada semente: gerar o futuro, gravar as séries na versão da partida de backtest daquele futuro, rodar o backtest, guardar só o resultado e a semente e apagar as linhas. O pico fica em cerca de 50 mil linhas (37 ativos × 5 anos) em vez dos 5 milhões de 100 futuros gravados juntos. O motor não muda, e a D7 fica confirmada, sem virar "mesma interface".

**Por quê.** A dimensão de versão já existe: a versão 0 é a série comum e a versão N é a da partida de id N (`backend/core/repository/series_version.py`, com `reading_version` e `seen_by`). O backtest já cria uma partida gravada com id (`start`, com `is_backtest=True`, em `backend/features/backtest/service.py`). O motor chama o repositório direto, em cerca de 12 funções SQL de `backend/core/repository/stock.py`, `economic.py` e `corporate_event.py`, então um provedor em memória criaria uma segunda leitura da mesma série. E o gerador é determinístico pela semente (`SeriesGenerator.generate(seed)`, em `backend/features/import_data/synthetic.py`, devolve um `GeneratedSeries` em memória): o futuro se recria igual e não precisa ficar guardado.

**Plano.**

1. **Geração.** Em `synthetic.py` e `future.py`, onde `_rows` converte a série gerada em linhas para gravar.
2. **Gravação por versão.** Hoje a gravação só escreve na versão 0, por `replace()` em `backend/core/repository/generated_future.py`, e a tabela `GeneratedFuture` tem uma linha só (id = 1). Os futuros de Monte Carlo precisam de um caminho de gravação por versão que não passe por essa linha.
3. **Orquestração.** A rodada mora ao lado do backtest, em `backend/features/backtest/`, com as rotas em `backend/routes/backtest.py`: para cada semente, em fila, gerar, gravar na versão da partida de backtest, rodar o backtest, guardar o resultado e a semente e apagar as linhas e a partida de rascunho.
4. **Limpeza.** O cache de `EconomicRepository` é por (série, versão) e é limpo ao apagar cada versão.
5. **Resultado.** O que a tela mostra: a fração de futuros que perdem para o CDI, o pior caso e o do meio (a mediana: metade dos futuros fica abaixo, metade acima), com a nota de que 100 futuros têm margem de erro de cerca de 8 pontos para cada lado ("23 de 100" significa algo entre 15% e 31%). Mudou DTO e rota: `pnpm openapi`.

**Tempo da rodada.** Com o motor de hoje, 100 futuros de 5 anos em fila passam de 3 horas, o que é tempo demais para quem só quer testar uma estratégia. A feature inclui deixar a partida de backtest mais rápida, nesta ordem: (1) medir para onde vai o tempo de uma partida (`pnpm profile:match`), separando o que é banco do que é cálculo em Python; (2) cortar o que o backtest de Monte Carlo não precisa, como gravar no banco a cada dia o que só o resultado final usa; (3) avaliar reescrever em Cython os laços de cálculo que sobrarem no topo da medição. O Cython compila um trecho de Python para C: num laço de contas, o ganho costuma ser de 10 a 100 vezes; em tempo gasto no banco, o ganho é nenhum, e por isso a medição vem antes. O custo do Cython é o executável passar a depender de um compilador de C na hora de ser montado. O plano fixa a meta de tempo da rodada e, se ela não for alcançada, escolhe entre menos futuros, período menor ou rodar em segundo plano com barra de progresso.

**Pendências para o plano.** (a) Medir quanto dura um backtest de 5 anos (`pnpm profile:match`), porque o gargalo provável é a partida repetida 100 vezes e não as séries: pela F202, 10 anos com 7 bots levam perto de 4 minutos, então 5 anos levam perto de 2 e 100 futuros em fila passam de 3 horas. (b) A leitura cai na "partida ativa" quando não recebe id, o que supõe uma partida por vez, então a rodada é sequencial. (c) Gravar e apagar 5 milhões de linhas ao longo da rodada deixa espaço morto no Postgres (o espaço que o banco só devolve numa limpeza), e a limpeza precisa ser prevista. (d) O desenho do que a tela mostra, como descrito no passo 5.

**Aceite:** a mesma semente reproduz o mesmo resultado; ao fim da rodada não sobra linha das versões descartáveis nem partida de rascunho; a série comum (versão 0) e as partidas salvas ficam intactas; o resultado sai como distribuição, com o tamanho da amostra; a rodada de 100 futuros de 5 anos termina dentro da meta de tempo fixada no plano, com a medição de antes e de depois registrada.

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

<a id="f60"></a>
**F60 — Modo servidor dedicado (`--headless`).** O mesmo executável, sem o navegador: para rodar numa VPS ou num PC ligado direto, sem ninguém jogando nele. `--headless` na linha de comando, ou `[server] headless = true` no `config.toml`, pula o `webbrowser.open` do `main.py`, que hoje roda sempre que o app é o executável, e imprime no terminal os endereços para entrar (o da rede local e, com a F6, o do túnel). O administrador é quem entra com o apelido de `[host] nickname`, que é como o host é definido hoje (`routes/simulation.py`). Como a recuperação de login é por apelido, num servidor exposto à internet qualquer um que digite esse apelido viraria o host; por isso, no modo servidor, o `config.toml` ganha `[host] pin`, e o login com o apelido do host só passa com ele. Serve a quem quer deixar uma sala aberta para os amigos entrarem quando quiserem, sem depender de o host estar com o computador ligado jogando.

<a id="f72"></a>
**F72 — Gráficos padronizados sobre o `ChartContainer` do shadcn.** Serve N15; continua a padronização da interface no shadcn, que deixou o `shared/components/ui/chart.tsx` sem nenhum consumidor. Hoje cada gráfico Recharts repete o `ResponsiveContainer`, a cor da grade e um array `{ key, label, color }` de séries (que é o `ChartConfig`), e uns cinco cards de tooltip feitos à mão reimplementam o `ChartTooltipContent`. Plano: (1) antes|depois no canvas de `player-line-chart` e `networth-chart` com `ChartContainer` + `ChartTooltipContent`, para aprovar o visual do tooltip (texto menor, indicador) e decidir se o `ui/chart.tsx` ganha variante; (2) convenção de pasta por gráfico: `<nome>-chart/` com `<nome>-chart.tsx` (componente puro, recebe o dado da API por prop), `chart-data.ts` (`ChartConfig`, tipos de linha e `build*`), `chart-legend.tsx` opcional (a legenda clicável que liga e desliga série continua própria) e `index.ts` exportando só o componente; gráfico sem legenda nem transformação fica arquivo solto `<nome>-chart.tsx`; (3) migrar `player-line-chart/` (`utils.ts` + `series.ts` → `chart-data.ts`, sai o tooltip próprio), `networth-chart`, `allocation-donut` e os gráficos embutidos em `composition-tab.tsx` (`AreaChart`) e `risk-tab.tsx` (`ScatterChart`), extraídos para pastas próprias; o `stock-chart` (lightweight-charts, imperativo) fica fora do `ChartContainer`; (4) a seção Gráficos entra em `docs/docs/desenvolvimento/convencoes-frontend.md`. Gatilho: a próxima rodada de design no canvas, ou o próximo gráfico novo.

<a id="f81"></a>
**F81 — CORS restrito à mesma origem.** O backend libera CORS para qualquer origem com credenciais (`allow_origins=["*"]` e `allow_credentials=True` no FastAPI, `cors_allowed_origins="*"` no Socket.IO). Não é necessário: o front é servido pelo próprio backend e, no `pnpm dev`, chega pelo proxy do Vite. Hoje o que protege o jogador de um site malicioso aberto durante a partida é o cookie `client_id` com `SameSite=Lax`, que o navegador não manda em requisição de outro site; o CORS liberado só deixa outro site ler as rotas que não pedem identidade. (1) Sai o `CORSMiddleware` de `main.py`. (2) O Socket.IO fica com `cors_allowed_origins` na mesma origem, mais `http://localhost:5173` quando o modo debug estiver ligado: o proxy do Vite troca o `Host` (`changeOrigin: true`) mas mantém o `Origin` do Vite, e o Socket.IO recusaria a conexão em dev sem essa exceção. (3) Teste manual antes de fechar: jogo pelo `localhost`, por outro computador da LAN pelo IP e pelo `pnpm dev`. Gatilho: junto com o link de convite pela internet, quando o servidor passa a ficar exposto fora da LAN.

<a id="f90"></a>
**F90 — Cenários.** Serve N22; condicionado por D18.

**O que o jogador passa a poder fazer.** Escolher, na criação da sala, um cenário histórico: uma partida montada com intenção, com texto de abertura, regras fixas e medalhas de bronze, prata e ouro. A partida continua vencida pelo modo de jogo e pelo ranking; as medalhas são um desafio por cima, que cada jogador cumpre ou não, individualmente. Todos os cenários ficam liberados, listados em ordem sugerida de dificuldade, cada um mostrando a melhor medalha que o jogador já conquistou. Não há campanha.

**O que existe.** O preset guarda só regras (`RULE_GROUP_FIELDS` em `backend/core/dto/preset.py`), sem texto de abertura, objetivo nem medalha, e os prontos nascem na migration inicial (`BUILT_IN_PRESETS`). A meta da corrida é avaliada em `backend/features/statistics/goal.py` e o ranking em `ranking.py` (`build_overview`); a queda máxima, a cota e o CDI do dia já saem de `risk.py`. As conquistas são gravadas por jogador na tabela `achievements`.

**Plano.**

1. **Medalhas.** Cada cenário tem três degraus, e cada degrau é uma lista de condições que o jogador precisa cumprir todas. O catálogo é pequeno e combinável: patrimônio final acima de um valor, retorno da cota acima do CDI acumulado no período e perda máxima (a maior queda do patrimônio desde o pico, `max_drawdown`). A perda máxima nunca vem sozinha, porque ficar parado no caixa a cumpriria: o degrau que a usa exige também uma condição de ganho, e a validação do cenário recusa o degrau que não a tem. Exemplo, Crise de 2008 com R$ 100 mil: bronze, terminar acima de R$ 100 mil; prata, terminar acima do CDI; ouro, terminar acima do CDI sem nunca cair mais de 20%. A avaliação é uma função pura, num módulo novo de `backend/features/statistics/`, que recebe o histórico do jogador e as medalhas do cenário e devolve o maior degrau cumprido. Os bots entram no ranking como sempre e não gravam medalha.
2. **Dado do cenário.** Tabela `scenario` por migration (D18), no molde do `preset`: nome, ordem de dificuldade, regras no mesmo formato do `config` do preset, texto de abertura e medalhas em JSON. As três linhas da primeira entrega entram na própria migration, como `BUILT_IN_PRESETS`, e por isso existem em instalação nova. Só há cenários que vêm com o app, sem editor.
3. **Trava.** O cenário escolhido grava `scenario_id` na partida (campo novo de `SimulationSettingsDTO`, nulo por padrão, no JSON de regras e sem migration, por D18). Ao criar a sala, o servidor confere que as regras enviadas são as do cenário: período, caixa inicial, aporte, modo de jogo, vida e imprevistos, impacto de preço, expansões e rumores (F93, sempre desligados) vêm fixos. Ficam livres o nome da sala e as ajudas de tela (modo Especialista); o número de jogadores e de bots não é travado. O lobby mostra os campos fixos desabilitados, com o seletor de cenário junto dos presets.
4. **Abertura.** A partida abre com o texto de abertura e as medalhas à vista.
5. **Fim da partida.** O relatório do ranking (`build_overview`) ganha, por jogador, a medalha obtida, mostrada ao lado da posição. A melhor medalha de cada jogador em cada cenário fica gravada na tabela nova `scenario_medal` (jogador, cenário, degrau, partida e data; chave jogador mais cenário), no molde de `achievements`; a gravação só troca o degrau por um maior.
6. **Lista de cenários.** Uma rota nova devolve os cenários na ordem de dificuldade com a melhor medalha do jogador, e o seletor do lobby a mostra.
7. **Primeira entrega.** Três cenários históricos, só com dados reais: Crise de 2008 (set/2008 a dez/2010, R$ 100 mil), Pandemia (jan/2020 a dez/2021) e Juros nas alturas (2015 a 2016, SELIC a 14,25% ao ano). Os valores das medalhas são calibrados na implementação, simulando em cada período três carteiras simples (100% CDI, 100% Ibovespa e meio a meio): o bronze é alcançável por quem não errou feio, e o ouro pede decisão boa. O caixa inicial, o aporte e o modo de jogo da Pandemia e dos Juros nas alturas saem junto da calibragem.
8. Mudou DTO e rota: `pnpm openapi`; tabelas novas: `pnpm db:revision`. `docs/docs/como-usar/lobby.md` descreve os cenários e as medalhas.

**Testes.** `tests/test_presets.py` ou um `tests/test_scenarios.py` novo: cada condição do catálogo; degrau com perda máxima sem condição de ganho recusado; histórico parado no caixa sem ouro nos três cenários; criação de sala recusada quando uma regra fixa difere do cenário e aceita com outro nome e outras ajudas; medalha gravada que só sobe de degrau; os três cenários presentes em banco novo.

**Fora deste card, como ideias futuras:** cenários criados pelo usuário; "Década perdida", que depende de o preset carregar um futuro gerado com choque (hoje não existe); e "Plano Real", que depende de haver dados de 1994.

**Aceite:** escolher um cenário trava as regras e mostra a abertura e as medalhas; ao fim da partida cada jogador vê a medalha obtida ao lado do ranking; a medalha fica gravada e aparece na lista de cenários; os três cenários existem em instalação nova; ficar 100% no caixa não dá ouro em nenhum deles.

<a id="f93"></a>
**F93 — Rumores antecipados.** Serve N31; condicionado por D18.

**O que o jogador passa a poder fazer.** Ligar, na criação da partida, uma opção de mercado desligada por padrão: o jornal da sala passa a publicar rumores, marcados como Rumor, de 3 a 10 pregões antes de um fato. O simulador já sabe o futuro, porque as séries até a data final estão no banco antes de a partida começar, reais ou geradas, e o rumor usa isso. Ao contrário do noticiário (F92), que conta o que já aconteceu, o rumor pede interpretação: pode se confirmar, ser alarme falso ou ser seguido de um movimento forte no sentido contrário. Rumor de queda seria quase de graça de obedecer (vender, ficar no CDI, recomprar); o alarme falso, o movimento contrário e a antecedência variável dão custo a obedecer sempre.

**O que existe.** As manchetes são da sala (`backend/features/notifications/news.py`, tabela `News`). As regras do jornal moram em `backend/features/newsroom/newsroom.py`: `strong_moves` e `copom_decision`, com os limiares em `companies.py` (variação mínima de 5%, 4 vezes a oscilação normal do ativo) e `macro.py`. As opções da partida estão em `SimulationSettingsDTO` (`backend/core/dto/simulation.py`).

**Plano.**

1. **Opção.** Campo `rumors_enabled: bool = False` em `SimulationSettingsDTO`, guardado no JSON de regras da partida, sem migration (D18), e listado em `RULE_GROUP_FIELDS` para o preset guardá-lo. No lobby é opção do mercado, fora do grupo das ajudas de tela: independe do modo Especialista (`expert_mode` só olha as ajudas) e liga-se com ou sem elas. Nos cenários (F90) a opção fica desligada e travada.
2. **Gerador.** Módulo novo `backend/features/newsroom/rumors.py`, chamado pelo `Newsroom` a cada pregão D com a opção ligada. Ele olha os 3 a 10 pregões seguintes nas séries guardadas e acha os fatos que os critérios de `strong_moves` e de `copom_decision` reconheceriam, olhando para a frente em vez de para trás. Para cada fato, a semente da partida (a mesma `random_seed` dos imprevistos, que o `Newsroom` passa a receber) e a chave do fato sorteiam se há rumor, a antecedência e o desfecho; o rumor sai no pregão D igual ao do fato menos a antecedência. O sorteio é determinístico: a mesma semente e o mesmo fato dão o mesmo rumor.
3. **Dado que falta.** A criação da partida não confere que as séries cobrem até a data final. Sem dado à frente, o fato não existe e não sai rumor; o alarme falso só sai quando a janela inteira de 10 pregões tem dado. O rumor lê a série guardada: com a expansão Governo & Política ligada, o preço da partida se afasta dela pelas ações dos jogadores, e o rumor acerta menos que os 60%. Isso é aceito como ruído a mais, e `docs/docs/como-usar/jornal.md` avisa.
4. **Desfecho.** De cada 100 rumores, 60 se confirmam, 25 são alarme falso e 15 são seguidos de movimento forte no sentido contrário. Os confirmados e os contrários nascem de fatos reais (75 de 100, na razão de 4 para 1), e só cerca de metade dos movimentos grandes ganha rumor, para que a ausência de rumor não garanta calmaria. O alarme falso é sorteado num alvo e numa data em que nenhum critério de movimento forte dispara nos 10 pregões seguintes, à razão de um para cada três rumores de fato real. Os falsos dependem da semente, então partidas do mesmo período com sementes diferentes têm alarmes falsos diferentes.
5. **Formatos.** Três, sorteados, pela regra "ou diz onde, ou diz para onde": setor com direção ("analistas veem risco no varejo", confirmado por movimento forte de um ativo do setor naquela direção), ativo sem direção ("mudanças na diretoria da X", confirmado por movimento forte do ativo) e macro sem direção (reunião do Copom fora do esperado, confirmada por mudança da SELIC). Nunca ativo e direção juntos. O desfecho contrário só cabe no formato com direção, porque só dá para contrariar uma direção dita: sorteia-se o desfecho e depois o formato entre os que cabem nele. As frases têm variações escolhidas por `pick`, de `newsroom/text.py`.
6. **Alcance.** A sala toda recebe o mesmo rumor, no jornal que já existe, sem caixa de entrada privada e sem pagamento. A manchete sai por `publish` com o tipo novo `NewsType.RUMOR` (enum e registro de tipos de manchete, com seção e nível padrão), e o jornal e o cartão de notícia (`frontend/features/news`) mostram a marca Rumor para distinguir do fato.
7. Mudou DTO: `pnpm openapi`. `docs/docs/como-usar/lobby.md` descreve a opção e `docs/docs/como-usar/jornal.md`, o rumor e as três saídas possíveis.

**Testes.** `tests/test_newsroom.py` ou um `tests/test_rumors.py` novo: opção desligada sem rumor; antecedência sempre entre 3 e 10 pregões; em muitas partidas sorteadas, as proporções ficam perto de 60/25/15; nenhum rumor com ativo e direção juntos; série sem dado à frente sem rumor e sem erro; duas sementes sobre o mesmo período dão alarmes falsos diferentes.

**Fora deste card, como ideia futura:** rumor privado sorteado para um ou dois jogadores, que depende de uma caixa de entrada por jogador.

**Aceite:** com a opção desligada nenhum rumor aparece; ligada, os rumores aparecem no jornal marcados como Rumor, de 3 a 10 pregões antes do fato; num teste com muitas partidas sorteadas as proporções ficam perto de 60/25/15; nenhum rumor traz ativo e direção juntos; duas partidas do mesmo período com sementes diferentes têm rumores falsos diferentes.

<a id="f110"></a>
**F110 — Combinar estratégias.** Serve N4; segue a D8. O jogador liga mais de uma estratégia ao mesmo tempo, cada uma com uma fatia do patrimônio (ex.: 30% em 100% no CDI e 70% no cruzamento de médias). O motor guarda, por jogador, a lista de estratégias com a fatia de cada uma e a origem de cada posição; cada estratégia recebe um contexto restrito à fatia dela (caixa e posições que ela comprou) e só opera dentro dele. A página de Estratégias passa de um interruptor para uma lista de fatias que somam 100%, e o log de ordens ganha o filtro por estratégia. Gatilho: F8 concluída e o uso pedir mais de uma estratégia.

<a id="f111"></a>
**F111 — Crédito para estratégias e bots.** Serve N4 e N33; segue a D8. O contexto da estratégia ganha a dívida, a nota de risco e a oferta do dia, e as ações ganham pegar empréstimo, amortizar e quitar, que chamam o mesmo serviço da tela de Crédito em nome do jogador. Uma estratégia de exemplo alavancada (ex.: rebalanceamento por meta com 20% emprestado) mostra o uso e entra na lista dos bots. O log da estratégia registra cada contratação e pagamento com o motivo. Gatilho: F8 e F94 concluídas.

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

<a id="f167"></a>
**F167 — Notícias do ativo como marcadores no gráfico de preço.** Serve N31. As manchetes de empresas do noticiário (F92) aparecem também na tela do ativo, como marcadores no gráfico de preço, com a manchete ao passar o mouse. Separada da F92 em 29/out: o noticiário sai na 3.1 só com as manchetes, e os marcadores pedem desenho no canvas antes do código. Gatilho: F92 concluída.

<a id="f197"></a>
**F197 — Rebalanceamento por meta com várias classes.** Serve N4. Hoje o `TargetRebalance` (`backend/features/strategy/rebalance.py:55`) divide só entre um ativo de ações (BOVA11 por padrão) e a renda fixa de liquidez diária: a meta em ações vai de 10% a 90% (padrão 60%), e o desvio máximo, de 1 a 20 pontos (padrão 5). O playtest de 31/out pediu configurar a meta de cada classe.

**O que muda:** os parâmetros viram uma lista de alvos (um ativo ou uma classe e a porcentagem), que soma 100%, com a faixa de desvio de cada alvo; a estratégia vende o que passou da faixa antes de comprar o que ficou abaixo, como hoje. O formulário da estratégia mostra a lista com o total e recusa o que não soma 100%. O padrão continua 60% em BOVA11 e 40% em renda fixa com 5 pontos, então partidas salvas e backtests antigos dão o mesmo resultado; um teste compara os dois. Os parâmetros salvos no perfil (F170) passam a guardar a lista. O modelo é o rebalanceamento por meta do Finance Manager: a mesma lista de alvos com faixa e a mesma regra de vender o que passou antes de comprar o que faltou.

<a id="f221"></a>
**F221 — Lista de ações que aguenta muitas ações.** Serve N40. A tela de ações (`variable-income.tsx`) busca todas as cotações de uma vez (`useVariableIncomeStocks`), filtra e ordena no navegador e desenha um mini gráfico por linha. A cada pregão chega um `stocks_update` com todas as ações, e a tabela inteira renderiza de novo. Com poucas ações não pesa; com muitas (uma base importada grande) o navegador trava. O playtest de 05/11 sugeriu paginar com carregamento por rolagem (como no Jornal) e só atualizar o que está na tela. O primeiro passo é medir: o custo do render por pregão com 100, 1.000 e 5.000 ações, para escolher entre paginar a busca, virtualizar as linhas (só as visíveis existem no DOM) ou assinar a atualização só das linhas visíveis. O filtro e a ordenação hoje são do navegador; paginar do lado do servidor leva os dois junto.

<a id="f225"></a>
**F225 — Conceitos de economia real na docs e nomeados na tela.** Serve N41 e N25; condicionado por D21. **Para quem:** quem joga e quer entender por que a economia da partida reagiu como reagiu, e quem lê a docs sem jogar. **O que cobre:** uma página por conceito na categoria de explicação que a reorganização da docs cria: juro real e juro real neutro, curva IS, lei de Okun, curva de Phillips, princípio de Taylor e a reação do Banco Central, defasagem da política monetária, meta de inflação e tolerância, credibilidade e expectativas, prêmio de risco, dinâmica da dívida (r − g) e espiral da dívida, primário que estabiliza a dívida e dominância fiscal. Cada página diz o que o conceito mede, um exemplo numérico, o que é valor bom e ruim, a fonte (relatório do Banco Central, artigo ou livro-texto) e como o jogo o implementa, com a fórmula e os coeficientes: é o lugar único dos números do modelo (D21), e a seção de economia interligada de `docs/docs/como-usar/governo.md` passa a apontar para as páginas. Cada página fecha com o que o jogo simplifica em relação à economia real, e uma página própria reúne as simplificações do modelo inteiro: as defasagens comprimidas, os coeficientes fixos em todas as épocas, o Banco Central que reage só à inflação (e não ao hiato do PIB) e o câmbio representado pelo prêmio de risco enquanto o dólar não entra na partida. O conteúdo parte dos conceitos e das explicações do [EconomicStatistics](https://github.com/LiloMarino/EconomicStatistics) (`frontend/shared/concepts/concepts.tsx` e `frontend/features/explainers/`), adaptado ao que o jogo faz, e as fórmulas entram com KaTeX no Docusaurus (`remark-math` e `rehype-katex`). **Na tela:** onde um texto do jogo cita um conceito ("segue o princípio de Taylor"), o nome dele vem com o sublinhado pontilhado do app e o cursor de interrogação, o mesmo `HoverCardTrigger term` de `frontend/shared/components/ui/hover-card.tsx` que o nome do padrão de candle usa no desafio. Passar o mouse ou focar abre um cartão no molde de `pattern-hint.tsx`, com três blocos. Primeiro, o nome e uma frase do que o conceito é, sem fórmula. Depois, "Na partida agora": o conceito aplicado ao estado da partida, como "IPCA 6,2% contra meta de 3,0%: o Copom tende a subir a SELIC na próxima reunião". Por fim, o "Saiba mais" para a página da docs. Os dois primeiros funcionam sem rede, e só o link depende dela. **Mecanismo:** um componente `ConceptTerm` em `frontend/shared/components/` e um catálogo dos conceitos em `frontend/shared/lib/` (chave, nome, frase e caminho da página da docs). Cada tela que cita o conceito passa o trecho da partida que o cartão lê, já resolvido pela tela, e o "Na partida agora" é montado a partir desse trecho. No mesmo bloco de texto, só a primeira menção ao conceito leva o sublinhado. Um teste confere que o caminho de cada conceito do catálogo existe em `docs/docs/`. Os pontos de partida são o painel da Economia (cada parcela leva o nome do conceito), a decisão do Copom, o prêmio de risco do Tesouro e o card da dívida. **Onde mora:** `docs/docs/`, na categoria de explicação. **Gatilho:** depois da reorganização da docs.

<a id="f227"></a>
**F227 — Intensidade das ligações e laboratório da economia.** Serve N41 e N34; condicionado por D20 e D21. Pede um plano de implementação em Opus antes do Sonnet, porque toca o núcleo da economia, as conquistas e o lobby.

**O que o jogador passa a poder fazer.** Ajustar no lobby três regras da partida, para quem quer aprender vendo o mecanismo. Quem não mexe em nada joga a partida padrão, que não muda: sem governo ela segue sendo a história.

**As três regras (as três entram).**

- **Intensidade.** Suave, Real e Exagerada multiplicam o desvio de todas as ligações por 0,5, 1 e 2. O desvio é a diferença entre a economia da partida e a da história (D20). Exemplo: se as medidas do governo deixam a inflação 1 ponto acima da história, a Suave a leva a 0,5 ponto acima, a Real mantém 1 e a Exagerada a leva a 2. Como o multiplicador age sobre "partida menos história", sem governo o desvio é zero e a partida continua sendo a história. A Exagerada serve para ver o efeito com clareza num mandato curto.
- **Laboratório.** Cada ligação liga e desliga, para ver o que cada uma faz sozinha. São seis: curva de Phillips (desemprego abaixo do normal empurra a inflação), reação do Banco Central (o juro sobe quando a inflação sobe), risco fiscal (dívida crescendo encarece o crédito), juro real na inflação (juro bem acima da inflação freia os preços), PIB na bolsa (economia mais fraca derruba as ações) e ciclo fiscal (a arrecadação acompanha o PIB). Com as estatais (F255), que saem antes, entra a sétima, o PIB da estatal, e ela ganha a chave aqui. O laboratório só liga e desliga: cada chave traz uma frase do mecanismo e um "Saiba mais" para a docs, sem coeficiente na tela (D21 deixa os números na docs). O número que o jogador vê é a parcela de cada ligação no painel da Economia, que também mostra quais ligações estão desligadas.
- **Credibilidade inicial.** Credibilidade, de 0 a 100, é a confiança do mercado de que o Banco Central segura a inflação. A partida começa com o Banco Central acreditado (100, o padrão) ou desacreditado. Desacreditado, começa em 40, valor fixo e ajustável na calibragem, e já paga prêmio de risco no primeiro dia (o prêmio é o juro extra que a dívida do governo paga por desconfiança: vale 2 pontos com credibilidade zero e cai na proporção, então 40 de 100 paga 60% de 2 pontos, ou 1,2 ponto). Para recuperar a confiança ele precisa manter o juro real na história ou subir a SELIC: cada reunião do Copom (a reunião em que o Banco Central decide a SELIC) que cumpre isso devolve 3 pontos, e com 8 reuniões por ano são 24 pontos por ano, o que dá no mínimo 2 anos e meio para voltar a 100. A regra vale porque a credibilidade é medida contra a história: um banco desacreditado que só copia a história recupera a confiança devagar. O 40 não vem de um ano real escolhido: 2002 e 2015 aparecem só como exemplo no texto da opção. A opção só aparece em partida com a expansão de governo, porque com Banco Central autônomo a credibilidade é sempre cheia (`AutonomousCentralBank`, em `backend/features/economy/monetary.py`).

**Placar e conquistas.** O placar da partida vale sempre. As conquistas só destravam com intensidade Real e todas as ligações ligadas. O Banco Central desacreditado conta normalmente para as conquistas, porque só dificulta. O motivo: ligação desligada e intensidade Suave facilitam, e a Exagerada dobra também o ganho (bolsa 10% acima da história vira cerca de 21%), o que permitiria farmar conquistas de retorno (repetir a partida fácil até acumular). A partida fora do padrão mostra o aviso "partida de laboratório: não destrava conquistas" no lobby e no painel da Economia. Ideia registrada, sem card: uma conquista própria para quem recuperar a credibilidade de 40 até 100.

**Plano.**

1. **Configuração.** As três regras são configuração da partida, escolhida no lobby; o padrão é Real, todas as ligações ligadas e Banco Central acreditado.
2. **Intensidade e laboratório.** As ligações e o desvio moram em `backend/features/government/linked_economy.py`, com as fórmulas em `backend/features/economy/links.py`. O desvio de cada ligação passa a sair multiplicado pelo fator de intensidade e zerado quando a ligação está desligada. O painel da Economia mostra a parcela de cada ligação e quais estão desligadas.
3. **Credibilidade.** As constantes e funções moram em `backend/features/economy/monetary.py` (`FULL_CREDIBILITY`, `CREDIBILITY_PREMIUM`, `next_credibility`). O ponto de partida da credibilidade, hoje sempre cheio, passa a ser o valor da regra; o prêmio e a recuperação seguem as funções que já existem.
4. **Conquistas.** Em `backend/features/achievements/` (`evaluator.py`, `catalog.py`, `service.py`) hoje nenhuma partida é excluída, então nasce aqui a marca de partida fora do padrão: intensidade diferente de Real ou alguma ligação desligada. Com a marca, nenhuma conquista da partida destrava; o Banco Central desacreditado não entra na marca.
5. **Telas e docs.** Aviso no lobby e no painel da Economia; cada chave do laboratório com a frase do mecanismo e o "Saiba mais" (D21), e a página da docs com os coeficientes. Mudou DTO e rota: `pnpm openapi`.

**Pendências para o plano.** (a) Confirmar se as seis ligações já são parcelas separadas do desvio, o que torna o liga e desliga barato. (b) Calibrar a Exagerada: a calibragem de 10 anos foi só em ×1, a bolsa segue a exponencial das forças (dobrar o desvio mais que dobra o efeito) e a espiral da dívida não tem teto (D20).

**Aceite:** a partida padrão sem governo continua idêntica à história; cada ligação desligada zera só a própria parcela no painel; a intensidade ×0,5 e ×2 multiplicam o desvio e ×1 não muda nada; a partida fora do padrão não destrava conquista e a com Banco Central desacreditado destrava; o desacreditado começa em 40 com prêmio de 1,2 ponto; a rodada de calibragem da Exagerada fica registrada.

<a id="f284"></a>
**F284 — Ministério para o partido da base.** Serve N34.

**Como é hoje.** Só o presidente propõe medidas (`_ensure_president` em `government_book.py`). O partido que entra na base entrega as cadeiras e recebe a emenda, com o setor que escolheu e cerca de 1 ponto de apoio por mês nos grupos dele (`deals.py`, `MONTHLY_SUPPORT`), e não ganha capital político por estar na base (`capital.py`): quem governa é só o presidente. Saiu do desenho da presidência e da base que valem a pena (F274) por ser grande o bastante para pedir desenho próprio.

**O que o jogador passa a poder fazer.** O acordo de base pode incluir um ministério, de uma lista fixa de 4 pastas. O líder do partido aliado vira o ministro e propõe as medidas da pasta, com os mesmos passos e limites de hoje, passando pelo Congresso. Em troca, o presidente perde a caneta daquela pasta e uma parte dos pontos de presidência do mês passa do partido dele para o do ministro. Estar na base deixa de ser só receber emenda e passa a ser também governar, com risco: o presidente demite quando quiser, e o ministro que favorece o próprio setor derruba a aprovação do governo.

As pastas e o que cada uma propõe:

- Infraestrutura: obras (`PUBLIC_WORKS`), com o valor e o endereço de setor ou segmento;
- Desenvolvimento Social: auxílio (`WELFARE_SPENDING`) e o nome do programa;
- Gestão: custeio (`OPERATING_COST`) e reajuste dos servidores (`SERVANT_RAISE`);
- Previdência: reajuste das aposentadorias (`RETIREE_RAISE`).

Impostos, medidas por setor e SELIC seguem só com o presidente.

**Plano.**

1. **Pasta no acordo.** Enum novo `Ministry` em `backend/core/enum/__init__.py`, com as 4 pastas e, em cada uma, os `MeasureKind` acima. `Deal` (`deals.py`) ganha `ministry: Ministry | None`; `propose_deal` recebe a pasta opcional e a grava em `DEAL_PROPOSED`. O aliado aceita ou recusa o acordo inteiro, com a pasta. Só partido de jogador recebe ministério: `propose_deal` recusa pasta para a bancada do computador (422), que segue aceitando o acordo pelas bandeiras, sem pasta. O ministério acaba junto com o acordo (rompimento, corte ou fim do mandato).
2. **Quem propõe.** `_ensure_president` vira uma checagem por tipo de medida (`_ensure_proposer`): numa pasta cedida só o ministro propõe, e o presidente leva 403 enquanto ela estiver cedida; nas demais medidas segue só o presidente. O ministro é o líder do partido aliado (`ally_leader`). `propose`, `repropose`, `withdraw` e `preview` valem para ele nas medidas da pasta, com `_draft`, os limites, a fila e a votação do Congresso iguais aos de hoje; o autor fica gravado em `proposer_id`.
3. **Capital político.** O `APPROVAL_MEASURED` passa a gravar os partidos que tinham ministério no mês, e `GovernedMonth` (`state.py`) guarda essa lista. Em `capital.py` (`party_capital`), cada ministério leva 15% dos pontos de presidência do mês (`MINISTRY_SHARE = Decimal("0.15")`, calibrável), tirados do partido do presidente e somados ao do ministro. Exemplo, com aprovação 60 e dois ministérios: o presidente soma 42 por mês (60 menos 18), ou 2.016 em 48 meses contra 2.880 sem ministério, e cada partido ministro soma 9 por mês, ou 432 em 48 meses, além das cadeiras. O total dos pontos do mês é o mesmo com e sem ministério (42 + 9 + 9 = 60). No impeachment o aliado perde metade do que o ministério rendeu a ele naquele mandato, na mesma regra que hoje tira metade da presidência.
4. **Freios.**
   - Uma pasta por partido e no máximo duas cedidas no governo: `propose_deal` (ou `deal_blocker`) recusa a terceira e a segunda pasta do mesmo partido.
   - O presidente demite o ministro a qualquer momento (`dismiss_minister`): a pasta volta a ele, o acordo de base continua, e o partido do presidente soma 4 pontos de rejeição nos grupos do aliado (`DISMISSAL_REJECTION = BREAK_REJECTION / 2`, metade dos 8 de romper o acordo, nos mesmos grupos que a quebra atinge). O ministro também pode entregar o cargo sem sair da base (`resign_ministry`), sem essa rejeição. Eventos novos `MINISTER_DISMISSED` e `MINISTER_RESIGNED`.
   - O favorecimento conta o ministro. A obra com endereço cobra aprovação pela maior fatia entre a carteira do presidente e a do ministro que a propôs: 6 pontos de aprovação vezes a fatia (`FAVORITISM_POINTS` em `sector_boost.py`). A carteira do presidente é congelada e a fatia dele fica gravada na medida (`stake`); a do ministro não é, então a fatia dele é lida de novo da carteira a cada fechamento de mês (`_close_month`), e `favoritism_factor` (`approval.py`) passa a receber essas fatias. Exemplo: ministro com 50% em Energia aponta obra para Energia, e o governo perde 3 pontos de aprovação por mês enquanto a fatia continuar. A carteira do ministro é pública enquanto ele estiver no cargo, no painel do governo, como a do presidente (`governance.py`, `_portfolio`).
   - Não há veto do presidente sobre a medida do ministro: o freio é orientar a bancada contra (`guide`) e demitir.
5. **Telas.** O `deal-proposal-dialog` ganha a escolha da pasta (ou nenhuma); o `base-card` mostra o ministro de cada pasta, com demitir para o presidente e entregar o cargo para o ministro; o `new-measure-dialog` e o painel de medidas mostram ao ministro as medidas da pasta e tiram do presidente as da pasta cedida; o `negotiate-dialog` e o `break-deal-dialog` avisam da pasta. Mudou DTO e rota: `pnpm openapi`.
6. **Partidas salvas.** `ministry` e a lista de partidos com ministério são campos novos nos eventos: o evento antigo, sem eles, é lido como acordo sem pasta, e a partida salva não muda.
7. `docs/docs/como-usar/governo.md` descreve as 4 pastas, a divisão dos pontos com o exemplo de aprovação 60, os freios e o favorecimento do ministro.

**Testes.** `tests/test_deals_book.py` e `tests/test_deals.py`: acordo com pasta aceito e gravado; pasta recusada para o computador; segunda pasta do mesmo partido e terceira pasta do governo recusadas; demissão devolve a pasta, mantém o acordo e soma 4 pontos de rejeição; entrega do cargo sem rejeição. `tests/test_government_book.py`: o ministro propõe na pasta e o presidente leva 403 nela; o ministro leva 403 em imposto, medida por setor e SELIC; a medida do ministro passa pelo Congresso. `tests/test_political_capital.py`: aprovação 60 com dois ministérios soma 42 ao presidente e 9 a cada ministro, e o total é o do mês sem ministério; impeachment tira metade do que o ministério rendeu ao aliado. Aprovação: o favorecimento do ministro com 50% no setor da obra cobra 3 pontos e acompanha a fatia a cada fechamento.

**Para observar no playtest (limite conhecido).** O favorecimento custa pouco ao ministro: dos 3 pontos, só 0,45 de capital cai nele (15%) e 2,55 caem no presidente. A demissão logo depois de o ministro aprovar o que o presidente queria. A Previdência tem um botão só e pode ser fundida com Desenvolvimento Social. A fatia de 15% é um valor de partida: abaixo de 10% o ministério não compensa o aliado, e acima de 25% a presidência deixa de valer a pena com dois aliados.

**Aceite:** o acordo de base com ministério grava a pasta; o ministro propõe as medidas da pasta e o presidente não, enquanto ela estiver cedida; a terceira pasta cedida e a segunda do mesmo partido são recusadas; o computador aceita o acordo sem pasta; com aprovação 60 e dois ministérios, o presidente soma 42 por mês e cada ministro 9, e o total dos pontos do mês é o mesmo com e sem ministério; a demissão devolve a pasta ao presidente, mantém o acordo e soma 4 pontos de rejeição nos grupos do aliado; a obra do ministro com 50% no setor tira 3 pontos de aprovação por mês enquanto a fatia continuar; `docs/docs/como-usar/governo.md` atualizada.

<a id="f286"></a>
**F286 — Comandos de trapaça no modo debug.** Com o modo debug ligado, o host ganha comandos que levam a partida a um estado sem jogar até ele, como os consoles de jogo de estratégia: virar presidente (ou outro cargo do governo), pôr ou tirar dinheiro do caixa de um jogador, pular para uma data, forçar um imprevisto ou um evento de vida, dar um título ou uma ação na carteira. Servem para conferir telas, montar o antes de um redesenho no canvas e testar regras no app de teste. Com o modo debug desligado, os comandos não existem no front nem respondem no backend. A forma (console de texto, painel com botões ou os dois) se decide quando o card for aberto.

<a id="f315"></a>
**F315 — Base das mecânicas de profissão.** Serve N39; segue a D23. A fundação onde cada profissão pendura a mecânica dela.
- **Página Profissão** no grupo Você, ao lado de Meta, só no modo profissões (`frontend/features/profession/pages/profession.tsx`, item em `App.tsx`), desenhada antes no canvas: o card da profissão (o `ProfessionBadge` e as `ProfessionTags` que hoje moram no card de vida da Meta), o bloco da mecânica, as séries que movem a renda (gráfico curto do indicador da profissão) e o histórico de uso. Cada mecânica entra como um bloco da página, seguindo o molde, sem canvas próprio.
- **Selo "da sua profissão"**, variante nova do `Badge` do design system, para o produto exclusivo que aparece na tela onde mora (consignado na Crédito, CDB da casa na Renda fixa).
- **Estado da mecânica por jogador** em `backend/features/profession/`: tabela com o estado tipado de cada profissão (migração própria), rota de leitura e uma rota de ação por mecânica; o `LifeBudget` lê o estado ao calcular a renda; cada uso vira evento no histórico de vida.
- **Política razoável**: uma função pura por mecânica que, dado o estado, o dia e a macro, devolve a ação de um jogador razoável. O motor a chama todo mês para os bots (junto do pagamento em `_live`, em `simulation.py`), e o `calibrate.py` importa a mesma função.
- **Troca de profissão no meio da partida**: a troca que hoje só vale no lobby ganha uma via interna, chamada pelas mecânicas (curso técnico do Auxílio, Administrador), que registra a data no histórico e mantém o capital inicial do jogador; o histórico de renda e as conquistas leem a profissão por período.
- **Calibração** (`calibrate.py`, fora do git): o poupador da sala como régua e a coluna "sem a mecânica".

**Aceite:** a página mostra card e séries para toda profissão; a troca no meio da partida tem teste; `pnpm run check` verde.

<a id="f320"></a>
**F320 — Ações do jogador sem espera em velocidade alta.** Do playtest de 20/11: em velocidade alta, diálogos e ações ficam carregando sem fim ou demoram muito. O loop (`simulation_loop.py`) segura o lock da partida durante o dia inteiro e só solta no intervalo entre dias (5 a 10 ms a 100x). O lock não é justo e volta direto para o loop, e as rotas de ordem, diálogo, pausa e velocidade esperam por ele sem prazo. A partida da triagem rodou sem o modo debug, então os logs não têm tempos. Medir pela CLI com o modo debug (tempo de espera das rotas e duração do dia a 100x) e fazer a rota esperar no máximo um dia: o loop cede a vez a quem está esperando antes de começar o dia seguinte.

<a id="f321"></a>
**F321 — Séries do preço de imóvel, do IGP-M e da TR.** Serve N39; segue a D23. Três séries novas em `IndicatorSeries`, do cliente do Banco Central que o jogo já usa (`bcb_sgs.py`, entradas em `INDICATOR_SOURCES` de `indicators.py`): o IVG-R (índice de valores de garantia dos imóveis residenciais financiados, mensal desde março de 2001), o IGP-M (o índice que reajusta os contratos de aluguel) e a TR (a Taxa Referencial, que rende o FGTS); os códigos SGS se conferem na importação. O futuro se gera em `synthetic.py`/`future.py` como nas outras séries mensais, e o IVG-R antes de março de 2001 recebe preenchimento sintético pelo IPCA. As três entram na Central como séries da economia, com uma linha dizendo o que medem. Testes do importador com resposta gravada.

<a id="f322"></a>
**F322 — FGTS e hora extra do CLT.** Serve N39; segue a D23. **FGTS** (passivo): todo mês 8% do salário bruto entram numa conta travada do jogador, sem sair do salário, rendendo 3% ao ano mais a TR; na demissão sorteada o saldo e a multa de 40% sobre ele caem no caixa e a conta recomeça. O saldo conta no patrimônio e aparece na carteira e na página Profissão. É o que separa o CLT do Autônomo na demissão. **Hora extra** (ativa): o jogador liga ou desliga na página Profissão; ligada, a renda sobe 25% e o imprevisto de saúde pesa o dobro; a oferta de hora extra segue o PIB de 12 meses (na recessão não há). Campos novos na `ProfessionRule`, aplicados pelo `LifeBudget`; só no modo profissões. Política razoável: liga a hora extra com o PIB acima do neutro e reserva que cubra um imprevisto.

<a id="f323"></a>
**F323 — Consignado do Servidor.** Serve N39; segue a D23. Na tela Crédito, um produto Consignado com o selo da profissão, só para o Servidor: juro de SELIC + 2% ao ano (abaixo da nota AAA), prazo até 60 meses e parcela descontada do salário antes de entrar no caixa, sem atraso possível. O limite é a margem consignável (soma das parcelas até 35% do salário líquido), independente da nota e do patrimônio: dá crédito no começo da partida, quando o patrimônio é pequeno. Reaproveita `credit_book.py` e a tabela Price de `loan.py`, com a regra nova em `rules.py`; o consignado conta como dívida na nota de risco. Aparece também no bloco da página Profissão. Política razoável: toma metade da margem quando o Ibovespa está 20% abaixo do topo de 12 meses, compra ações e quita quando o índice recupera.

<a id="f324"></a>
**F324 — CDB da casa do Bancário.** Serve N39; segue a D23. Todo primeiro dia do mês o banco oferece ao Bancário um CDB prefixado de 1, 2 ou 3 anos, com taxa igual à SELIC esperada pelo Focus para o prazo mais 1 ponto e teto de aplicação de 1 salário por mês, sem resgate antes do vencimento. Como o salário dele cai quando a SELIC cai, travar com juro alto protege a renda. Aparece na Renda fixa com o selo da profissão e no bloco da página Profissão. Reaproveita o `fixed_broker` (cria a taxa prefixada se o CDB hoje só for pós-fixado), com a oferta criada por jogador em vez da fábrica de ofertas raras. Política razoável: aplica o teto quando a SELIC está acima da média de 24 meses.

<a id="f325"></a>
**F325 — Trava de câmbio e mix de exportação do Exportador.** Serve N39; segue a D23. **Trava:** na página Profissão o Exportador contrata um câmbio futuro para até 100% da receita de 6 ou 12 meses, ao dólar do dia corrigido pela diferença de juros (dólar x (1 + CDI) / (1 + Fed Funds) no prazo, com as séries que já existem); enquanto vale, a parte travada da renda usa o dólar travado no lugar do fator do dólar. Uma trava por vez. **Mix:** escolhe a fração exportada (0 a 100%, mudança no máximo uma vez por trimestre); a parte exportada segue o dólar e a vendida no Brasil segue o PIB, pelas curvas que já existem em `DRIVER_CURVES`, somadas pelo peso. Política razoável: trava 50% por 12 meses com o dólar acima da média de 12 meses; mix 50/50, puxado para o lado cujo indicador está acima do neutro.

<a id="f326"></a>
**F326 — Tabela de preços do Autônomo.** Serve N39; segue a D23. O Autônomo define o preço em reais, uma vez por mês, contra uma referência de mercado que sobe com o IPCA. A renda é preço x clientes: cobrar acima da referência rende mais por cliente e perde clientes, e a perda cresce com o desemprego acima do neutro; a chance do mês sem clientes também sobe com o preço. Sem reajuste, o preço fica para trás da referência e a inflação corrói a renda, como hoje: a identidade dele fica, e quem reajusta bem resolve o tombo das partidas longas. O mecanismo substitui o `inflation_indexed=False` da regra. Política razoável: repassa o IPCA de 12 meses uma vez por ano, mais 5% com o desemprego abaixo do neutro e nada acima.

<a id="f327"></a>
**F327 — Reinvestimento do Empreendedor.** Serve N39; segue a D23. Todo mês o Empreendedor escolhe a fração do lucro (a renda do mês) que volta para a empresa. O capital da empresa rende uma renda extra ligada ao PIB de 12 meses (alta no crescimento, negativa na recessão), conta no patrimônio como uma linha da carteira e só vira caixa vendendo uma parte da empresa com desconto de 20%. Estado na tabela da base; controles no bloco da página Profissão. Política razoável: reinveste 30% com o PIB acima do neutro e nada abaixo, e vende 25% quando o PIB fica negativo por dois trimestres.

<a id="f328"></a>
**F328 — Previdência do Aposentado.** Serve N39; segue a D23. O Aposentado entra com um saldo de previdência privada além do capital da sala, travado e rendendo o CDI menos 1% ao ano de taxa. Na página Profissão ele pode converter parte ou todo o saldo em renda vitalícia, com a renda do mês calculada pelo juro real do dia (SELIC menos o IPCA esperado pelo Focus) e fixada daí em diante (corrigida pelo IPCA na sala com correção): converter com juro alto dá renda maior para sempre. Ou pode resgatar pagando IR regressivo pelo tempo do saldo no plano (35% até 2 anos, caindo 5 pontos a cada 2 anos, até 10% depois de 10). O saldo conta no patrimônio; o convertido vira renda. A saúde em dobro continua. Política razoável: converte metade quando o juro real passa de 6% ao ano e resgata o resto depois de 10 anos.

<a id="f329"></a>
**F329 — Pé-de-Meia, tarifa social e curso técnico do Auxílio.** Serve N39; segue a D23. **Tarifa social** (passivo): a despesa do Auxílio é 15% menor, por um campo novo na `ProfessionRule`. **Pé-de-Meia:** todo mês em que o caixa termina maior do que começou, o governo deposita 20% dessa sobra (teto de 10% do salário) numa conta travada, liberada a cada 2 anos se o caixa não ficou negativo no período; o bônus escala com o gasto com auxílio das alavancas do governo. **Curso técnico:** o jogador se matricula (12 meses com a renda do bico pela metade) e, ao concluir, vira CLT pela troca de profissão da base, perdendo o benefício e mantendo o saldo do Pé-de-Meia. Política razoável: poupa todo mês e faz o curso no começo quando a partida tem 10 anos ou mais.

<a id="f330"></a>
**F330 — Relatório da casa do Corretor.** Serve N39; segue a D23. Todo mês o Corretor recebe, no bloco da página Profissão, o relatório da corretora: de 3 a 5 ações com recomendação de compra ou venda e preço-alvo, calculados pelos fundamentos, pelo noticiário agendado e pela macro que o jogo já tem, dias antes de as notícias saírem, com acerto acima do acaso mas não garantido (ruído calibrado). A vantagem é informação: bem jogado é saber quando seguir e quando ignorar. Passivo: a renda troca o vínculo com o Ibovespa por salário fixo mais comissão sobre o volume negociado na sala no mês, paga pela casa e dividida entre os Corretores, como a comissão do Banqueiro de ofertas (`simulation_engine.py`). Política razoável: compra as recomendações de compra com 20% do patrimônio e vende no prazo do preço-alvo.

<a id="f331"></a>
**F331 — Escada acadêmica do Recém-formado.** Serve N39; segue a D23. A classe de maior escala da partida, fraca no começo e com o maior salário numa partida longa. Degraus em ordem: especialização (1 ano, mensalidade, trabalha junto), mestrado (2 anos, renda da bolsa no lugar do salário) e doutorado (4 anos, bolsa). Cada degrau concluído sobe o múltiplo final da carreira (ex.: 1,3x, depois 1,6x, 2,2x e 3,0x) e estica a curva (`CareerCurve` por degrau). Matricular com o desemprego acima do neutro dá desconto na mensalidade e bolsa maior. **Mora com os pais:** despesa 40% menor nos 3 primeiros anos, ou até sair de casa por um botão na página. Sem teto de calibração: os alarmes só conferem que ele não é o primeiro em todos os horizontes. Política razoável: sobe um degrau só quando os anos que faltam pagam o degrau (valor presente simples) e sai de casa no prazo.

<a id="f332"></a>
**F332 — Imóveis do Locador.** Serve N39; segue a D23. A renda do Locador passa a ser o aluguel dos imóveis dele: começa com imóveis cujo aluguel soma o múltiplo de hoje, no lugar do 1,1x do salário. Cada imóvel tem preço pelo IVG-R e aluguel de 0,5% do preço ao mês na assinatura, reajustado pelo IGP-M a cada 12 meses do contrato. A vacância é sorteada por imóvel todo mês, com chance que sobe com o desemprego e a queda do PIB, e substitui a vacância de hoje; vago, o imóvel volta ao mercado com aluguel pelo preço do dia. Compra e venda no bloco Imóveis da página Profissão, com custo de transação de cerca de 5% (ITBI e corretagem) e venda concluída em até 1 mês. O valor dos imóveis conta no patrimônio e aparece na carteira. Tabela nova de imóveis por jogador, com migração. Política razoável: compra quando o aluguel do dia rende mais que o CDI menos 2 pontos e vende quando rende menos que o CDI menos 5.

<a id="f333"></a>
**F333 — Administrador, a profissão que troca de setor.** Serve N39; segue a D23. Profissão nova (enum, regra, card e textos em `professions.ts`, elegível para bots). Setores: CLT, Empreendedor, Exportador, Bancário, Autônomo e Corretor; ele leva só a renda do setor (múltiplo, indicador e demissão), não a mecânica. **Experiência por setor:** entra júnior (0,85x a renda do setor) e chega a sênior (1,0x) em 12 meses no setor; sair não apaga a experiência, e voltar retoma o nível. Trocar toda hora o deixa júnior em tudo; trocar de vez em quando o deixa sênior nos setores onde mais ficou. A troca leva 1 mês, com a renda do mês pela metade, pela troca de profissão da base. **Servidor por concurso:** edital aberto algumas vezes por ano (mais com o gasto do governo alto), inscrição com meses de estudo e renda menor, e chance de aprovação; aprovado, vira Servidor com estabilidade e a perde se sair. A página Profissão mostra a experiência em cada setor e a renda que cada um daria hoje. Política razoável: troca para o setor de maior renda esperada quando a diferença passa de 20% e o setor atual já está sênior.

<a id="f334"></a>
**F334 — Calibração das profissões pelos três alarmes.** Serve N39; segue a D23. Com o `calibrate.py` importando as políticas razoáveis, roda as salas com e sem correção pelo IPCA em 5, 10, 20 e 26 anos contra o poupador da sala e confere os três alarmes da D23: mecânica que não vale a pena, profissão primeira em todos os horizontes, profissão última em todos. Ajusta os números das regras até nenhum alarme soar, Comissionado e Banqueiro de ofertas incluídos; a taxa da herança do Herdeiro só muda se soar alarme para ele. A docs das profissões e os cards de `professions.ts` passam a descrever a mecânica e o formato da curva de cada uma (começo forte, constante, fim de jogo), com a dica explicando cada número. A tabela final fica registrada no card ao concluir.

<a id="f335"></a>
**F335 — Venda a descoberto e aluguel de ações.** Serve N43. Qualquer jogador pode vender uma ação que não tem: a venda abre uma posição negativa, que paga o aluguel da ação (taxa ao ano cobrada por dia) e trava uma garantia em caixa ou títulos (ex.: 150% do valor vendido). Se a perda come a garantia além de um limite, vem a chamada de margem: o jogador repõe em 1 dia ou a posição é zerada a mercado. O outro lado, o comum no varejo: o jogador marca na carteira que empresta as próprias ações e recebe a taxa do aluguel. Motor: posição negativa no `broker`/`matching_engine`, aluguel e garantia num livro novo, eventos no histórico e aviso da chamada. Na boleta, vender sem ter a ação abre a confirmação de venda a descoberto com o custo e o risco (perda sem teto). Jogo base, sem expansão; nenhuma estratégia dos bots usa por enquanto.

<a id="f336"></a>
**F336 — Ordem stop e validade na boleta.** Serve N43. A boleta ganha um "Avançado" recolhido, fechado por padrão, com o stop (vira ordem a mercado ou limitada quando o preço cruza o gatilho: o stop loss limita a perda, o stop gain realiza o lucro) e a validade (vale hoje ou até cancelar). `OrderType` ganha o stop e o stop limitado, o `order_book` dispara o gatilho a cada pregão e a lista de ordens pendentes mostra o gatilho. A boleta padrão continua com a ordem a mercado e a limitada. Fica fora a OCO e as outras ordens de nicho.

---

## 🔍 Em avaliação

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Falta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **F5** | Spike | Spike: provider de túnel pela internet | N2 | — | M27 · 4.6 | — | Escolhe o provider da F6 |
| **F34** | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | N19 | — | M24 · 4.4 | — | Escolhe a biblioteca de gráfico |
| **F123** | Melhoria | Redesenhar o aviso de conquista desbloqueada | N22, N15 | — | M28 · 4.7 | — | Escolher o desenho do aviso no canvas; liga à F122 |
| **F131** | Feature | Catálogo de padrões de vela | N19 | — | M28 · 4.7 | — | Tópico do Como jogar com cada padrão animado |
| **F158** | Melhoria | Animações do Como jogar revistas | N25 | — | M28 · 4.7 | — | O visual numa rodada no canvas dedicada: animações atuais contra as primeiras, número do passo fora da cena, cursor e destaque, e o palco em tamanho real mostrando só o trecho do passo |
| **F159** | Feature | Rodada de novas conquistas e revisão das existentes | N22 | D1 | M28 · 4.7 | [F123](#f123) | Quais conquistas novas entram e o que muda nas existentes; decidido com o usuário numa rodada de ideias |
| **F193** | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | N25, N19 | D21 | M28 · 4.7 | [F158](#f158) | O molde do tópico em fases, quais indicadores entram primeiro e onde o 'i' abre o tópico sem cobrir a tela (F183). |
| **F202** | Performance | Backtest que corre mais rápido que a partida comum | N10 | D8 | M25 · 4.5 | — | Medir o dia do backtest por etapa e escolher quais custos saem do caminho dele (eventos em memória gravados em lote, leituras do que o motor acabou de gravar, trava por pregão, imposto por dia) |
| **F279** | Feature | Estratégias automáticas novas e revisão das atuais | N4, N8 | — | M24 · 4.4 | — | Medir as estratégias atuais em várias bases com governo, dólar e crédito; calibrar os níveis de dificuldade; escolher as estratégias novas |
| **F285** | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | N20 | — | — | — | Escolher o mecanismo (filtrar o seletor, recolorir na tela de quem liga ou reforçar além da cor) e medir o tamanho do conjunto distinguível sob as três simulações |

<a id="f5"></a>
**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO; se não passar, se ao menos o polling atravessa (o SSE saiu na D13, então o polling é o único fallback). O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

<a id="f34"></a>
**F34 — Gráfico de ações em tela cheia, com ferramentas de trader.** Serve N19; segue a D2. Um botão no card "Histórico de Preços" abre o gráfico em tela cheia, com os indicadores da F33 e o que uma plataforma de trader oferece: barra de ferramentas de desenho (linha de tendência, linha horizontal de suporte e resistência, canal, retângulo, retração de Fibonacci, texto), régua que mede variação % e pregões entre dois pontos, escala logarítmica, legenda com abertura, máxima, mínima, fechamento e volume do candle sob o cursor, comparação com outro ticker ou com o Ibovespa em %, e uma boleta compacta para comprar e vender sem sair da tela. Os desenhos ficam salvos por jogador e ticker numa tabela nova (`chart_drawings`, com os pontos em JSON), entrando por migration (D9). Falta escolher a biblioteca: (1) continuar no `lightweight-charts` e escrever as ferramentas de desenho como plugins (a API de primitives da versão 5; os exemplos oficiais trazem linha de tendência e retângulo); (2) trocar pelo KLineChart (Apache 2.0), que já vem com cerca de 15 ferramentas de desenho, mas calcula indicadores no navegador, e pela D2 eles viriam do backend como indicador customizado; (3) o Advanced Charts da TradingView tem tudo pronto, mas a licença pede cadastro e não permite publicar a biblioteca em repositório público, o que o deixa fora deste projeto. Sai daqui com um protótipo de linha de tendência e Fibonacci nas opções 1 e 2, e a escolha.

<a id="f123"></a>
**F123 — Redesenhar o aviso de conquista desbloqueada.** Hoje o aviso (`achievement-toast.tsx`, aberto com `toast.custom` do sonner) é um cartão escuro de 380 px com uma faixa amarela de 3 px à esquerda, o ícone, o rótulo amarelo em maiúsculas ("Conquista desbloqueada"), o nome e a descrição; quando várias saem no mesmo dia, vira uma lista com "Ver todas". O incômodo existe, mas não está claro de onde vem: pode ser a faixa amarela do canto, o rótulo, o peso do cartão escuro, o tamanho ou a falta de movimento. Falta escolher o desenho depois de ver variantes lado a lado no canvas: (a) o cartão atual sem a faixa, com o ícone em destaque; (b) um cartão claro, no tema do app; (c) um formato compacto, com o ícone e o nome numa linha só e a descrição ao passar o mouse; (d) um formato de "selo" com a categoria e a cor dela. A rodada cobre os estados uma conquista, várias no mesmo dia, secreta revelada e conquista com barra de progresso completa, e decide a posição na tela e a entrada e saída. Sai daqui para Pendente com a variante escolhida.

<a id="f131"></a>
**F131 — Catálogo de padrões de vela.** Serve N19. Um tópico do "Como jogar" (F126) que lista todos os padrões que as dicas de análise técnica (F96) reconhecem, cada um com o ícone e o nome que aparecem no gráfico (o martelo com o símbolo dele, por exemplo). Navegar pelo catálogo mostra um padrão por vez, com a animação das velas se formando no molde dos roteiros do tutorial, o que o padrão costuma sugerir e o lembrete de que padrão não é garantia. Em aberto: se o catálogo é um tópico do tutorial ou uma tela própria, e se o card do padrão no gráfico ganha um "ver no catálogo". Gatilho: com as dicas de análise técnica e a janela "Como jogar" prontas.

<a id="f158"></a>
**F158 — Animações do Como jogar revistas.** Serve N25; retrabalho da F126. No playtest, o tutorial pareceu estranho: o estilo das animações ficou parecido com o do Create, e o número do passo que aparece no meio da animação, num círculo ao lado do alvo (`StepMarker` em `tutorial/stage/stage-kit.tsx:144`, número vindo de `topic-illustration.tsx:57`, usado em `buy-stock.tsx` e `order-types.tsx`), polui a cena. O salto para o trecho do passo ao clicar numa etapa funciona bem e fica como está. Falta escolher o visual numa rodada no canvas: comparar as animações atuais com as primeiras, feitas no canvas a partir das Dicas e truques do Factorio, decidir se o número sai da cena (o passo ativo já fica destacado na lista) e o que muda no cursor e no destaque. **Palco do tutorial (avaliado em 03/11):** a captura mostra o palco com a tela inteira encolhida a uns 70%, então o texto de 12 px do livro de ofertas chega a uns 8 px, e o marcador do passo cobre o texto que aponta. O desenho do retrato (palco em tamanho real mostrando só o trecho que o passo explica, o marcador numa margem à esquerda com uma linha até o alvo e os passos numa fileira abaixo) é coerente e o usuário o reconhece como a direção, mas não vai ser implementado a partir desse board: entra na rodada de canvas dedicada desta F, com o método completo (variantes e estados).

<a id="f159"></a>
**F159 — Rodada de novas conquistas e revisão das existentes.** Serve N22; segue a D1. Sessão de iteração com o usuário: ele dá as ideias, o Claude ajuda a pensar, critica e propõe, e a mesma rodada revê o catálogo atual (`backend/features/achievements/catalog.py`): quais conquistas ficam, quais mudam de condição ou de texto e quais saem. Vem depois da Gestoras, quando dá para ver todas as features que pedem conquista, e depois da redesenhada do aviso, para as conquistas novas já nascerem no desenho novo. Entra nela a conquista "Ordem com paciência", já planejada: coluna `order_type` em `event_equity` (mercado ou limitada), por migration, com as linhas antigas como mercado; o `Broker` grava o tipo na execução; uma `@metric` em `metrics.py` conta as execuções de ordem limitada do jogador, e a conquista entra no `catalog.py`. Vale qualquer ordem limitada executada, inclusive a que executa na hora porque o preço já estava bom. Sai daqui para Pendente com a lista aprovada e o plano de cada conquista nova.

<a id="f193"></a>
**F193 — Indicadores técnicos e padrões de vela explicados no Como jogar.** Serve N25 e N19. Hoje cada indicador técnico diz Compra, Venda ou Neutro, com um "i" de texto curto que não ensina a ler, e o "i" dos padrões de vela nem abre. A ideia do playtest de 31/out: um tópico por indicador no Como jogar, em fases: o que é e como se calcula; por que ele aponta compra ou venda; um caso em que acerta; as ressalvas, quando ele engana. O "i" do indicador abre o tópico na aba dele. O mesmo molde serve aos padrões de vela, junto do catálogo (F131). As ordens a mercado e limitada já têm o tópico "Ordem a mercado e limitada" (`tutorial/topics/order-types.tsx`), que mostra a limitada esperando o preço chegar ao limite, e ficam como estão.

<a id="f202"></a>
**F202 — Backtest que corre mais rápido que a partida comum.** Serve N10; segue a D8. Depois da correção do dia que crescia, o backtest de 10 anos com 5 bots já fica mais rápido a cada pregão, mas ainda corre no ritmo de uma partida comum na velocidade máxima. Pelo `profile:match`, com 7 bots o dia custa ~90 ms: os ~2.500 pregões de 10 anos levam perto de 4 minutos. Um backtest não tem ninguém olhando cada pregão, então tudo o que o dia faz para a tela e para retomar a partida no meio é custo sem retorno.

O backtest já pula os avisos por pregão e o governo e grava os snapshots em lote (`_record_backtest_day`, `flush_backtest`). O que continua igual à partida comum, e é candidato a sair do caminho do dia: gravar no banco os eventos de cada pregão no `flush` em vez de acumular em memória e gravar em lote, ler do banco o que o próprio motor acabou de escrever (fluxos de ordens no fator de impacto, preços do dia), a trava do motor tomada a cada pregão, e o cálculo do imposto e do caixa por dia. Pela D8 o executor rápido é o mesmo motor com as mesmas estratégias e as mesmas regras do dia: muda só onde o dado mora enquanto o backtest corre e quando ele vai para o banco.

**Como medir:** o tempo total do backtest de 10 anos com 5 bots, três rodadas no banco de teste, junto da medida por etapa do dia do modo debug e de um perfil do motor (yappi) de 200 pregões, antes e depois. Para conferir que o resultado não mudou, o mesmo backtest com a mesma semente dá o mesmo patrimônio final de cada bot, centavo por centavo.

**Aceite:** o backtest de 10 anos com 5 bots leva no máximo metade do tempo de 2.500 dias de partida comum com os mesmos bots, e o patrimônio final de cada bot sai igual ao de antes da mudança com a mesma semente.

<a id="f279"></a>
**F279 — Estratégias automáticas novas e revisão das atuais.** Serve N4 e N8. As estratégias automáticas e os bots foram desenhados antes do governo, do dólar, do crédito e das expansões. Precisa conferir se continuam competitivas e se faltam estratégias que usem o que entrou. O rebalanceamento por meta com várias classes já é a F197, na Mesa do trader. **Dificuldade:** os bots da partida ganham os níveis Fácil, Médio e Difícil, como os bots da eleição. O Difícil diversifica entre classes e rebalanceia; o Fácil gira muito a carteira e paga corretagem e imposto. A medida são backtests em várias bases e vários sorteios, para o ativo sorteado não decidir o resultado: na base atual o buy and hold vence porque compra bitcoin. **Estratégias novas** incluem as de renda fixa e de alocação, no molde da 100% CDI, além das de gráfico.

<a id="f285"></a>
**F285 — Modo daltonismo: limitar as cores às que um daltônico distingue.** Serve N20.

**O que o jogador passa a poder fazer.** Ligar uma opção "modo daltonismo", como os jogos têm, e ver jogadores e partidos só em cores que ele distingue. Com o modo desligado, as cores seguem escolhidas só pelo contraste e pela distância ΔE normal, sem a restrição de daltonismo.

**O que existe.** As 12 cores dos jogadores e as 20 dos partidos foram escolhidas para visão normal: contraste de 3 para 1 contra o fundo e ΔE (CIEDE2000, o quanto duas cores parecem diferentes; perto de 10 dá para distinguir lado a lado) de pelo menos 12. Simulando daltonismo (modelo de Machado, 2009: protanopia é a falta dos cones do vermelho, deuteranopia a dos cones do verde e tritanopia a dos cones do azul), vários pares colapsam. Na paleta de 16 cores medida, 19 pares ficam abaixo de ΔE 12 na protanopia, 25 na deuteranopia e 20 na tritanopia. Os piores: Caramelo e MNV (0,8 na protanopia), Vermelho e Caramelo (2,8 na deuteranopia) e Verde-água e o cinza do partido sem cor (2,4 na deuteranopia). Mesma ordem de grandeza da paleta das tintas do Minecraft, que a avaliação comparou.

**Falta decidir o mecanismo.**

1. Filtrar o seletor: com o modo ligado, o seletor oferece só um subconjunto de cores distinguíveis nas três simulações. É o mais simples, mas só vale para a cor que a pessoa escolhe; as cores que os outros escolheram ficam como estão e duas delas ainda podem se confundir.
2. Recolorir na tela de quem liga: o navegador troca a cor mostrada de cada jogador e de cada partido por uma de um conjunto distinguível, sem mexer no que o servidor guarda (a cor é só de exibição). Cobre as cores dos outros. O preço: a tela de quem liga o modo não bate com a dos demais.
3. Reforço além da cor: sigla, listra ou forma junto da cor, no mapa e nos gráficos. Vale para qualquer tipo de daltonismo, mas cada gráfico precisa de desenho próprio.

Recomendação: começar pelo 2, porque cobre as cores dos outros sem tocar no servidor, e deixar o 3 para onde só a cor carrega a informação (o mapa). O tamanho do conjunto distinguível sai de medir o ΔE sob as três simulações.

---

## 💤 Sem prioridade

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F176** | Feature | Cadeiras do Congresso por região | N34 | D19 | — | — | Médio | Médio | Médio | Médio |

<a id="f176"></a>
**F176 — Cadeiras do Congresso por região.** Serve N34; upgrade do mapa por região (F164). Na Câmara real nenhum estado tem menos de 8 nem mais de 70 deputados, e o Norte e o Centro-Oeste valem mais em cadeiras do que em eleitores: o Norte tem 65 de 513 cadeiras (12,7%) com 8,1% do eleitorado, e o Sudeste 179 (34,9%) com 42,6%. As 101 cadeiras se repartem na proporção das 513: Sudeste 35, Nordeste 30, Sul 15, Norte 13, Centro-Oeste 8. Cada região reparte as dela pelo D'Hondt de `house.distribute` com o voto da região; a barreira continua nacional. Ganhar o Norte passa a valer mais no Congresso do que na urna, uma decisão de campanha real. Fica depois do mapa porque mexe no modelo das cadeiras.

---

## ✅ Concluído

| ID | Tipo | Resumo | Serve | D# | Marco |
| --- | --- | --- | --- | --- | --- |
| **F316** | Correção | Correções do playtest: gestoras e cotas | N23, N15 | — | M29 · 4.3 |
| **F317** | Correção | Correções do playtest: lobby, aporte no Fundo Soberano, dicas ⓘ e fim da aquisição hostil | N23, N34, N15 | — | M29 · 4.3 |
| **F318** | Feature | Bots cotistas e o Mercado votam o aumento de taxa pelo desempenho | N23 | — | M29 · 4.3 |
| **F319** | Melhoria | Página Estratégias segue a conta ativa | N4, N23 | — | M29 · 4.3 |
| **F337** | Feature | Mercado e bots cotistas compram a emissão pelo desempenho e pelo ágio | N23 | — | M29 · 4.3 |

<a id="f316"></a>
**F316 — Correções do playtest: gestoras e cotas.** Do playtest de 20/11 (partida de aquisição hostil). Sete consertos nas telas e regras da gestora:

- **Comprar com preferência para o gestor:** o atalho de Suas ações leva à aba Cotas, mas o formulário de compra da emissão aparece só para quem não é o gestor (`viewer = fund.my_role !== "manager"` em `quotas-tab.tsx`, condição em `fund-issuance-card.tsx`). O backend aceita a compra do gestor; o formulário passa a aparecer para todo cotista com direito, gestor incluído.
- **Meses do Relatório:** com muitos meses, o seletor de mês (ToggleGroup em `report-tab.tsx`) passa da largura da tela. Segue o molde do mapa das eleições (`map-timeline-years.tsx`): os meses mais recentes à vista e um botão "Anteriores · N" que abre a grade com todos. Com dois consumidores, o seletor sobe para `shared/components`.
- **Emissão que não capta:** o cartão da emissão explica quem compra e quando: cotistas na fase de preferência (10 pregões); na sobra (5 pregões), qualquer um, e os bots só no último pregão, se o preço da emissão couber no valor que dão à cota (patrimônio por cota mais um prêmio de até ±20% pelo desempenho acima do CDI). Encerrada sem venda, o cartão diz por quê.
- **Gestora paga com a liquidez diária:** parcela, taxa a pagar e as outras saídas da gestora resgatam primeiro a renda fixa de liquidez diária dela, como a conta pessoal já faz (`cover_before_debit` em `simulation_engine.py`, que hoje pula a gestora).
- **Rendimentos na renda variável:** o cartão de rendimentos da cota no detalhe da renda variável (`fund-distributions-card.tsx`) lista todos os meses. Ganha a paginação da aba Rendimentos da gestora (`HistoryCard` em `income-tab.tsx`), que sobe para `shared` com os dois consumidores.
- **Comprar a própria cota na emissão:** teste que reproduz o gestor comprando na preferência e na sobra pública e confere que a participação dele depois fica acima da que teria sem comprar. O cartão mostra quantas cotas mantêm a participação de hoje.
- **Gestora comprando cota de outra gestora:** o backend recusa ("A gestora não compra cota de gestora.", em `create_order`), mas a boleta não diz nada antes. Com uma gestora ativa no topo, a boleta de uma cota fica desabilitada com o motivo.

<a id="f317"></a>
**F317 — Correções do playtest: lobby, aporte no Fundo Soberano, dicas ⓘ e fim da aquisição hostil.** Do playtest de 20/11 (partida de aquisição hostil). Sete consertos fora das telas da gestora:

- **Tipo de partida sem trava de expansão no lobby:** o tipo Aquisição hostil deixa de travar a expansão Gestoras, e o tipo Político deixa de travar a expansão Governo, pela mesma regra. Sai o selo "expansão ligada e travada" e a nota `ExpansionLockNote`. Desligar a expansão com o tipo que depende dela escolhido volta o tipo para o clássico. Com a expansão desligada, o cartão do tipo fica só com a cara de desabilitado, mais escuro, sem o selo "Ligue a expansão" (`game-type-fields.tsx`, `funds-card.tsx`, `expansion-fields.tsx`).
- **Fundar gestora mais enxuto na preparação:** comparada a criar partido, a aba tem blocos que não pedem decisão. Sai "Como a sala vai ver" (repete o nome três vezes); a linha do tempo "Como ela nasce" vira uma frase curta sob a identidade. Ficam Identidade, Co-gestores, Taxas e Nesta sala (`fund-found-tab.tsx`).
- **Aporte no Fundo Soberano recusado:** o aporte de 100 bi volta "O campo value é inválido.". O `value` de `ProposeMeasureRequest` (`core/dto/government.py`) tem `max_digits=14, decimal_places=4`, então não passa de R$ 9.999.999.999,9999, e os quatro atalhos do diálogo (10, 25, 50 e 100 bi) passam desse teto. O campo passa a aceitar o maior valor que uma medida pode ter (conferir obras e estatal fundada), e o erro `decimal_max_digits` ganha frase própria em `validation_messages.py`. Sem aporte o caixa do Fundo é zero, e por isso ele não comprava nada: confirmar na salva que, com o aporte aprovado, a compra pela conta do Fundo sai. A boleta na conta do Fundo mostra o caixa e, sem caixa, o caminho do aporte.
- **Dicas ⓘ que não abrem:** as dicas de "Faixa de hoje", "Preço de ranking" e de outras telas não abrem. O app não monta `TooltipProvider` desde a troca do Radix pelo Base UI (`App.tsx`), e o `InfoHint` só abre por hover. Toda ⓘ abre no hover e no clique, conferido no navegador. Dentro de boleta travada (`inert`), a dica continua acessível.
- **Estatísticas da aquisição hostil:** o layout das estatísticas do fim de partida em aquisição hostil quebra. Sem print: reproduzir na salva da partida e consertar o que passar da borda ou desalinhar.
- **Vencedor da aquisição hostil:** o título diz "Thales venceu: restou uma gestora", enquanto o pódio e o "Você venceu." põem em 1º quem tem mais patrimônio, eliminado ou não (`match-hero.tsx` usa `survivor_nickname`; o pódio usa a `position` de `ranking.py`, que ignora eliminação). Na aquisição hostil, quem restou fica em 1º e os eliminados vêm depois, de quem caiu por último para quem caiu primeiro; título, pódio e "Você venceu." usam a mesma ordem.

<a id="f318"></a>
**F318 — Bots cotistas e o Mercado votam o aumento de taxa pelo desempenho.** Do playtest de 20/11. Hoje as cotas do gestor e dos co-gestores não votam o aumento de taxa, e bots e o formador de mercado também não. Com os outros cotistas todos bots, ninguém vota, e empate ou zero votos mantém a taxa: o gestor nunca sobe a taxa, mesmo com 90% das cotas. Decidido: o bot cotista vota, com o peso das cotas dele, a favor quando a gestora bateu o CDI nos últimos 6 meses (126 pregões, a janela de desempenho de `performance.py`, rendimentos incluídos, a mesma que dá o prêmio que o bot paga pela cota) e contra quando não bateu. O Mercado (formador de mercado), que junta cotas comprando de quem vende, vota com a mesma regra, para a taxa nunca travar com as cotas paradas nele. A aba Assembleia mostra no placar "Bots cotistas" e "Mercado" separados, e a regra numa dica.

<a id="f319"></a>
**F319 — Página Estratégias segue a conta ativa.** Do playtest de 20/11. O automático da gestora mora na aba Configurações e não tem o que a página Estratégias tem: gráfico de sinais, prévia antes de salvar, confirmação ao desligar ou trocar, registro completo, painel de resultado e parâmetros salvos no perfil. A página Estratégias opera só a conta pessoal (`useMyStrategy` busca `/api/strategies/me`) e não diz isso, e quem gere a gestora acha que ela mexe no automático da gestora. Decidido: a página Estratégias opera a conta escolhida no topo, como a boleta, e diz no cabeçalho qual conta é; a aba Configurações da gestora fica com um resumo do automático e o link para a página. O aviso de boleta travada (`trade-lock-notice.tsx`) desliga o automático de qualquer conta, não só da pessoal.

<a id="f337"></a>
**F337 — Mercado e bots cotistas compram a emissão pelo desempenho e pelo ágio.** Do playtest de 20/11. A sobra de uma emissão de cotas só tem dois compradores além dos jogadores: os bots da estratégia "Cotas de gestoras" (Cotista, Caçador de Ágio, Dona Cota), que compram só no último pregão da sobra e só se o preço couber no valor que dão à cota (patrimônio por cota mais um prêmio de até ±20% pelo desempenho acima do CDI, em `fund_quotas.py`); e mais ninguém, porque o Mercado (formador de mercado) nunca compra do emissor (`bid_ceiling` em `maker.py`). Numa sala com um bot cotista ou nenhum, a emissão não capta, o que não vendeu não nasce (`_close_issuance` em `fund_book.py`) e a cota fica sem liquidez. O ágio, que o jogador espera que ajude a captar, não entra em conta nenhuma.

Decidido:

- **Mercado compra a sobra:** no último pregão da sobra, depois dos jogadores e dos bots, o Mercado mede a atratividade da cota como o maior entre o prêmio do desempenho (o mesmo dos bots, sem a opinião do dia) e o ágio do livro (P/VP menos 1, com o P/VP sendo o preço da cota dividido pelo patrimônio por cota). Leva da sobra a fração atratividade ÷ 20%, até a sobra inteira, e revende essas cotas na escada dele. Atratividade zero ou negativa, não compra. Exemplos: gestora 3 pontos acima do CDI dá prêmio de 6% e o Mercado leva 30% da sobra; cota a P/VP 1,12 dá 12% e ele leva 60%. Só o ágio não basta porque a escada do Mercado se centra no patrimônio por cota, e numa sala com poucos compradores o P/VP fica perto de 1: o Mercado nunca compraria justo onde falta comprador. Só o desempenho ignora a demanda que o livro mostra.
- **Bots cotistas pesam o ágio na emissão:** na oferta e na sobra, o bot compara o preço com o maior entre o valor que dá à cota e o preço do livro, sem passar do teto de 1,2 vez o patrimônio por cota. Cota a P/VP 1,15 faz a emissão a R$ 100 sair 13% abaixo do que o livro paga (R$ 115), e o bot compra mesmo com a gestora um pouco abaixo do CDI. A descrição da estratégia diz isso.
- **Estimativa de captação:** o diálogo de anunciar e o cartão da emissão mostram uma faixa de quanto o mercado deve levar (a opinião diária dos bots varia ±5%), somando os bots da sala, pelo valor e pelo caixa de cada um, e o Mercado, pela fração acima. Quando a faixa é zero, o cartão diz o que falta: "a gestora rende 2 pontos abaixo do CDI e a cota não tem ágio". Diz também em que pregão bots e Mercado decidem.
- **% e quantidade nos formulários de cota:** anunciar emissão, comprar na preferência ou na sobra e emitir para si ou para um co-gestor ganham os atalhos de percentual e o campo de quantidade inteira da boleta de ações, sobre o teto de cada um (o teto da emissão, o direito de preferência, o caixa).

**Aceite:** testes da compra do Mercado (fração pela atratividade, zero sem atratividade, depois de jogadores e bots) e do bot cotista com ágio; a estimativa bate com a compra numa emissão de teste sem opinião do dia; `pnpm run check` verde.

---

## 🚫 Descartado

> Nenhum item neste status.
