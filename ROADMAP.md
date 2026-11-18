<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/atualizar/concluir/descartar/remover um item, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban do projeto, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que ordem e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-11-18):** Decididas as regras pendentes dos cards da 4.2 e criados os cards da assembleia de cotistas e da cor da conta que opera

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Tipo | Resumo | Marco | Condiciona (F#) | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **N1** | — | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — | — | — | — |
| **N2** | — | Jogar com amigos pela internet sem que cada um instale uma VPN | — | [F5](#f5), [F6](#f6) | — | — | — |
| **N3** | — | Confiar que os números do simulador são exatos e reprodutíveis | — | [F308](#f308) | — | — | — |
| **N4** | — | Testar uma estratégia de investimento automática e ver como ela se sai | — | [F110](#f110), [F111](#f111), [F197](#f197), [F279](#f279), [F306](#f306) | — | — | — |
| **N7** | — | Que o simulador cobre os custos de operar do mercado real | — | — | — | — | — |
| **N8** | — | Jogar contra oponentes controlados pelo computador | — | [F279](#f279), [F294](#f294), [F298](#f298) | — | — | — |
| **N9** | — | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — | — | — | — |
| **N10** | — | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | — | [F28](#f28), [F202](#f202), [F308](#f308) | — | — | — |
| **N11** | — | Que o cenário econômico simulado seja o histórico real | — | — | — | — | — |
| **N12** | — | Continuar jogando depois do último dia com dado real | — | — | — | — | — |
| **N13** | — | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | — | — | — | — |
| **N14** | — | Atualizar para uma versão nova sem perder as partidas salvas | — | [F56](#f56) | — | — | — |
| **N15** | — | Usar uma interface agradável e coerente, à altura de um jogo | — | [F37](#f37), [F72](#f72), [F123](#f123), [F179](#f179), [F211](#f211), [F287](#f287), [F288](#f288), [F295](#f295), [F300](#f300), [F312](#f312) | — | — | — |
| **N19** | — | Analisar um ativo com as ferramentas de um trader | — | [F34](#f34), [F131](#f131), [F193](#f193) | — | — | — |
| **N20** | — | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | [F285](#f285), [F287](#f287), [F288](#f288) | — | — | — |
| **N21** | — | Jogar "na unha", sem a interface apontar a melhor escolha | — | — | — | — | — |
| **N22** | — | Ter objetivos para buscar além de vencer a partida | — | [F90](#f90), [F123](#f123), [F159](#f159) | — | — | — |
| **N23** | — | Jogar com os amigos de outras formas além de cada um por si | — | [F44](#f44), [F55](#f55), [F101](#f101), [F102](#f102), [F103](#f103), [F104](#f104), [F105](#f105), [F290](#f290), [F293](#f293), [F296](#f296), [F299](#f299), [F300](#f300), [F301](#f301), [F302](#f302), [F303](#f303), [F304](#f304), [F305](#f305), [F306](#f306), [F310](#f310), [F311](#f311), [F312](#f312), [F313](#f313) | — | — | — |
| **N24** | — | Saber onde está a lentidão durante uma partida | — | — | — | — | — |
| **N25** | — | Entender o que é o simulador e como se joga, sem ler um manual | — | [F132](#f132), [F133](#f133), [F139](#f139), [F140](#f140), [F141](#f141), [F158](#f158), [F193](#f193), [F225](#f225), [F289](#f289) | — | — | — |
| **N26** | — | Achar a causa de um erro sem vasculhar o log inteiro | — | — | — | — | — |
| **N31** | — | Saber o que está movendo o mercado da partida, como quem lê o noticiário | — | [F93](#f93) | — | — | — |
| **N33** | — | Investir com dinheiro emprestado, pagando o juro do momento | — | [F111](#f111) | — | — | — |
| **N34** | — | Disputar o poder de mudar as regras da economia da partida | — | [F176](#f176), [F227](#f227), [F255](#f255), [F284](#f284), [F290](#f290), [F292](#f292), [F293](#f293), [F297](#f297), [F307](#f307) | — | — | — |
| **N39** | — | Chegar ao primeiro dia da partida com as próprias escolhas já feitas | — | [F289](#f289), [F291](#f291), [F298](#f298), [F309](#f309) | — | — | — |
| **N40** | — | Jogar partidas longas e na velocidade máxima sem a tela travar | — | [F221](#f221) | — | — | — |
| **N41** | — | Aprender como a economia real funciona, jogando | — | [F225](#f225), [F227](#f227), [F255](#f255), [F292](#f292) | — | — | — |
| **N42** | — | Chegar a um estado da partida sem jogar até ele | — | [F286](#f286) | — | — | — |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | M27 · 4.5 | — | — | — | 🔍 |
| [**F6**](#f6) | Feature | Link de convite pela internet no lobby | M27 · 4.5 | — | Médio | Bom | ⏳ |
| [**F14**](#f14) | Feature | Janela desktop nativa | M27 · 4.5 | — | Baixo | Bom | ⏳ |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | M25 · 4.4 | — | Alto | Bom | ⏳ |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | M24 · 4.3 | — | — | — | 🔍 |
| [**F37**](#f37) | Feature | Tema escuro | M28 · 4.6 | — | Médio | Médio | ⏳ |
| [**F56**](#f56) | Feature | Novidades no app | M27 · 4.5 | — | Baixo | Bom | ⏳ |
| [**F60**](#f60) | Feature | Modo servidor dedicado (--headless) | M27 · 4.5 | — | Baixo | Bom | ⏳ |
| [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | M24 · 4.3 | — | Médio | Bom | ⏳ |
| [**F81**](#f81) | Manutenção | CORS restrito à mesma origem | M27 · 4.5 | — | Baixo | Médio | ⏳ |
| [**F90**](#f90) | Feature | Cenários | M25 · 4.4 | — | Alto | Bom | ⏳ |
| [**F93**](#f93) | Feature | Rumores antecipados | M25 · 4.4 | — | Médio | Médio | ⏳ |
| [**F110**](#f110) | Feature | Combinar estratégias | M25 · 4.4 | — | Médio | Bom | ⏳ |
| [**F111**](#f111) | Feature | Crédito para estratégias e bots | M25 · 4.4 | — | Baixo | Bom | ⏳ |
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | M28 · 4.6 | — | — | — | 🔍 |
| [**F131**](#f131) | Feature | Catálogo de padrões de vela | M28 · 4.6 | — | — | — | 🔍 |
| [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | M28 · 4.6 | — | Médio | Bom | ⏳ |
| [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | M28 · 4.6 | — | Baixo | Bom | ⏳ |
| [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | M28 · 4.6 | — | Médio | Bom | ⏳ |
| [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | M28 · 4.6 | — | Alto | Bom | ⏳ |
| [**F141**](#f141) | Docs | README com as features de hoje | M28 · 4.6 | — | Baixo | Excelente | ⏳ |
| [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | M28 · 4.6 | — | — | — | 🔍 |
| [**F159**](#f159) | Feature | Rodada de novas conquistas e revisão das existentes | M28 · 4.6 | — | — | — | 🔍 |
| [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | M24 · 4.3 | — | Baixo | Bom | ⏳ |
| [**F176**](#f176) | Feature | Cadeiras do Congresso por região | — | — | Médio | Médio | 💤 |
| [**F193**](#f193) | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | M28 · 4.6 | — | — | — | 🔍 |
| [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | M24 · 4.3 | — | Médio | Bom | ⏳ |
| [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | M25 · 4.4 | — | — | — | 🔍 |
| [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | M24 · 4.3 | — | Médio | Bom | ⏳ |
| [**F225**](#f225) | Docs | Conceitos de economia real na docs e nomeados na tela | M28 · 4.6 | — | Alto | Bom | ⏳ |
| [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | M28 · 4.6 | — | Alto | Médio | ⏳ |
| [**F279**](#f279) | Feature | Estratégias automáticas novas e revisão das atuais | M24 · 4.3 | — | — | — | 🔍 |
| [**F284**](#f284) | Feature | Ministério para o partido da base | — | — | Alto | Médio | ⏳ |
| [**F285**](#f285) | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | — | — | — | — | 🔍 |
| [**F286**](#f286) | Feature | Comandos de trapaça no modo debug | — | — | Médio | Bom | ⏳ |
| [**F300**](#f300) | Melhoria | Tela da gestora em abas, como a do governo | M18 · 4.2 | — | Alto | Bom | ⏳ |
| [**F301**](#f301) | Correção | Gestor que vira presidente e mais de uma gestora por jogador | M18 · 4.2 | — | Alto | Bom | ⏳ |
| [**F302**](#f302) | Correção | Caixa da gestora sem ficar negativo | M18 · 4.2 | — | Médio | Bom | ⏳ |
| [**F303**](#f303) | Feature | Dinheiro novo na gestora depois da oferta pública | M18 · 4.2 | — | Alto | Bom | ⏳ |
| [**F304**](#f304) | Feature | Co-gestão combinada no lobby | M18 · 4.2 | — | Médio | Bom | ⏳ |
| [**F305**](#f305) | Melhoria | Aquisição hostil como modo de vitória | M18 · 4.2 | — | Médio | Bom | ⏳ |
| [**F306**](#f306) | Feature | Automático só na carteira da gestora | M18 · 4.2 | — | Médio | Bom | ⏳ |
| [**F307**](#f307) | Correção | Estatais com preço vivo e lucro à vista | M18 · 4.2 | — | Alto | Bom | ⏳ |
| [**F308**](#f308) | Spike | Spike: impacto do jogador no preço, teto do k e oscilação no pregão | M18 · 4.2 | — | Médio | Bom | ⏳ |
| [**F309**](#f309) | Melhoria | Balanceamento das profissões | M18 · 4.2 | — | Médio | Bom | ⏳ |
| [**F310**](#f310) | Feature | Página Ofertas públicas | M18 · 4.2 | — | Médio | Bom | ⏳ |
| [**F311**](#f311) | Feature | Fusão de gestoras | M18 · 4.2 | — | Alto | Médio | ⏳ |
| [**F312**](#f312) | Melhoria | Cor da expansão na conta que opera | M18 · 4.2 | — | Baixo | Bom | ⏳ |
| [**F313**](#f313) | Feature | Assembleia de cotistas com aba própria e aumento de taxa | M18 · 4.2 | — | Alto | Bom | ⏳ |

<details>
<summary><strong>Concluído / decidido / descartado (44 itens — clique pra expandir)</strong></summary>

| ID | Tipo | Resumo | Marco | Condiciona (F#) | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **D1** | — | Eventos são a fonte da verdade; snapshots são derivados | — | [F159](#f159) | — | — | ✅ |
| **D2** | — | Cálculo financeiro acontece só no backend; o frontend exibe | — | — | — | — | ✅ |
| **D3** | — | Dinheiro e quantidade trafegam como Decimal serializado em string | — | — | — | — | ✅ |
| **D4** | — | Banco de dados embarcado no executável | — | — | — | — | ✅ |
| **D6** | — | A retomada continua no dia seguinte ao último evento | — | — | — | — | ✅ |
| **D7** | — | O simulador lê as séries sem saber a origem | — | [F28](#f28) | — | — | ✅ |
| **D8** | — | Bot, modo automático e backtest são o mesmo mecanismo | — | [F110](#f110), [F111](#f111), [F202](#f202) | — | — | ✅ |
| **D9** | — | De onde nasce uma mudança de schema | — | [F101](#f101) | — | — | ✅ |
| **D10** | — | Como a nota geral é calculada | — | — | — | — | ✅ |
| **D11** | — | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | — | — | — | ✅ |
| **D12** | — | Como numerar as versões | — | — | — | — | ✅ |
| **D13** | — | Um canal de tempo real só: Socket.IO, com fallback de polling | — | — | — | — | ✅ |
| **D14** | — | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | — | — | — | — | ✅ |
| **D15** | — | Lint com oxlint, formatação com oxfmt e o TypeScript 7 com a API do 6 ao lado | — | — | — | — | ✅ |
| **D16** | — | Estratégias do app no host, personalização pela API | — | — | — | — | ✅ |
| **D17** | — | Os tópicos do tutorial se animam em código, com o motion | — | — | — | — | ✅ |
| **D18** | — | Uma migration por versão; caminho antigo só cai numa major | — | [F90](#f90), [F93](#f93) | — | — | ✅ |
| **D19** | — | O eleitorado são grupos, cada um com apoio e rejeição por partido | — | [F176](#f176), [F290](#f290), [F293](#f293) | — | — | ✅ |
| **D20** | — | A economia da partida é a história mais o desvio que o governo causa | — | [F227](#f227), [F255](#f255) | — | — | ✅ |
| **D21** | — | O jogo ensina a jogar, a docs explica o modelo | — | [F132](#f132), [F133](#f133), [F140](#f140), [F193](#f193), [F225](#f225), [F227](#f227) | — | — | ✅ |
| [**F44**](#f44) | Feature | Expansão Gestoras: fundar a gestora e abrir capital | M18 · 4.2 | — | — | — | ✅ |
| [**F55**](#f55) | Feature | Modo aquisição hostil | M18 · 4.2 | — | — | — | ✅ |
| [**F101**](#f101) | Feature | Carteira separada do jogador | M18 · 4.2 | — | — | — | ✅ |
| [**F102**](#f102) | Feature | Gestoras: emissão de novas cotas e recompra | M18 · 4.2 | — | — | — | ✅ |
| [**F103**](#f103) | Feature | Gestoras: troca de gestor pela assembleia | M18 · 4.2 | — | — | — | ✅ |
| [**F104**](#f104) | Feature | Gestoras: co-gestores | M18 · 4.2 | — | — | — | ✅ |
| [**F105**](#f105) | Feature | Gestoras: rendimentos mensais | M18 · 4.2 | — | — | — | ✅ |
| [**F179**](#f179) | Melhoria | Topbar que cabe com a corrida e o governo | M18 · 4.2 | — | — | — | ✅ |
| [**F211**](#f211) | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | M18 · 4.2 | — | — | — | ✅ |
| [**F249**](#f249) | Manutenção | Núcleo do backend sem import de features | M18 · 4.2 | — | — | — | ✅ |
| [**F255**](#f255) | Feature | Estatais | M18 · 4.2 | — | — | — | ✅ |
| [**F287**](#f287) | Melhoria | Slots dos jogadores do lobby no desenho anterior | M18 · 4.2 | — | — | — | ✅ |
| [**F288**](#f288) | Melhoria | Badge de profissão legível no lobby e na Minha preparação | M18 · 4.2 | — | — | — | ✅ |
| [**F289**](#f289) | Melhoria | Cards de profissão com vantagens e desvantagens | M18 · 4.2 | — | — | — | ✅ |
| [**F290**](#f290) | Feature | Profissões novas | M18 · 4.2 | — | — | — | ✅ |
| [**F291**](#f291) | Melhoria | Locador com aluguel de 1,1× o salário | M18 · 4.2 | — | — | — | ✅ |
| [**F292**](#f292) | Feature | Fundo Soberano: o governo compra ações e cotas | M18 · 4.2 | — | — | — | ✅ |
| [**F293**](#f293) | Feature | Profissões das expansões: Comissionado e Banqueiro de ofertas | M18 · 4.2 | — | — | — | ✅ |
| [**F294**](#f294) | Melhoria | Adicionar vários bots de uma vez | M18 · 4.2 | — | — | — | ✅ |
| [**F295**](#f295) | Manutenção | Orçamento, painel econômico e base do governo por tempo real | M18 · 4.2 | — | — | — | ✅ |
| [**F296**](#f296) | Correção | Correções do playtest: gestoras e renda variável | M18 · 4.2 | — | — | — | ✅ |
| [**F297**](#f297) | Correção | Correções do playtest: governo e eleição | M18 · 4.2 | — | — | — | ✅ |
| [**F298**](#f298) | Correção | Correções do playtest: lobby, bots e profissões | M18 · 4.2 | — | — | — | ✅ |
| [**F299**](#f299) | Feature | Cota de gestora negociada na renda variável | M18 · 4.2 | — | — | — | ✅ |

</details>

---

## 🚀 Próximas versões

> O que entra em cada versão, na ordem de trabalho. Item arquivado conta como concluído.

### 4.2 — Expansão Gestoras (M18)

> **Objetivo:** Fundar a própria gestora, abrir capital e disputar as cotas na sala; o governo também funda estatais, segura o preço, privatiza e investe pelo Fundo Soberano; a preparação ganha profissões novas.
>
> **Serve:** N23, N34, N41
>
> **Progresso:** 24/38 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F249**](#f249) | Manutenção | Núcleo do backend sem import de features | — | ✅ Concluído |
| 2 | [**F101**](#f101) | Feature | Carteira separada do jogador | — | ✅ Concluído |
| 3 | [**F211**](#f211) | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | — | ✅ Concluído |
| 4 | [**F44**](#f44) | Feature | Expansão Gestoras: fundar a gestora e abrir capital | — | ✅ Concluído |
| 5 | [**F179**](#f179) | Melhoria | Topbar que cabe com a corrida e o governo | — | ✅ Concluído |
| 6 | [**F102**](#f102) | Feature | Gestoras: emissão de novas cotas e recompra | — | ✅ Concluído |
| 7 | [**F103**](#f103) | Feature | Gestoras: troca de gestor pela assembleia | — | ✅ Concluído |
| 8 | [**F55**](#f55) | Feature | Modo aquisição hostil | — | ✅ Concluído |
| 9 | [**F104**](#f104) | Feature | Gestoras: co-gestores | — | ✅ Concluído |
| 10 | [**F105**](#f105) | Feature | Gestoras: rendimentos mensais | — | ✅ Concluído |
| 11 | [**F255**](#f255) | Feature | Estatais | — | ✅ Concluído |
| 12 | [**F292**](#f292) | Feature | Fundo Soberano: o governo compra ações e cotas | — | ✅ Concluído |
| 13 | [**F287**](#f287) | Melhoria | Slots dos jogadores do lobby no desenho anterior | — | ✅ Concluído |
| 14 | [**F288**](#f288) | Melhoria | Badge de profissão legível no lobby e na Minha preparação | — | ✅ Concluído |
| 15 | [**F289**](#f289) | Melhoria | Cards de profissão com vantagens e desvantagens | — | ✅ Concluído |
| 16 | [**F290**](#f290) | Feature | Profissões novas | — | ✅ Concluído |
| 17 | [**F293**](#f293) | Feature | Profissões das expansões: Comissionado e Banqueiro de ofertas | — | ✅ Concluído |
| 18 | [**F291**](#f291) | Melhoria | Locador com aluguel de 1,1× o salário | — | ✅ Concluído |
| 19 | [**F294**](#f294) | Melhoria | Adicionar vários bots de uma vez | — | ✅ Concluído |
| 20 | [**F295**](#f295) | Manutenção | Orçamento, painel econômico e base do governo por tempo real | — | ✅ Concluído |
| 21 | [**F296**](#f296) | Correção | Correções do playtest: gestoras e renda variável | — | ✅ Concluído |
| 22 | [**F297**](#f297) | Correção | Correções do playtest: governo e eleição | — | ✅ Concluído |
| 23 | [**F298**](#f298) | Correção | Correções do playtest: lobby, bots e profissões | — | ✅ Concluído |
| 24 | [**F299**](#f299) | Feature | Cota de gestora negociada na renda variável | — | ✅ Concluído |
| 25 | [**F310**](#f310) | Feature | Página Ofertas públicas | [F299](#f299) | ⏳ Pendente |
| 26 | [**F300**](#f300) | Melhoria | Tela da gestora em abas, como a do governo | — | ⏳ Pendente |
| 27 | [**F312**](#f312) | Melhoria | Cor da expansão na conta que opera | — | ⏳ Pendente |
| 28 | [**F301**](#f301) | Correção | Gestor que vira presidente e mais de uma gestora por jogador | — | ⏳ Pendente |
| 29 | [**F302**](#f302) | Correção | Caixa da gestora sem ficar negativo | — | ⏳ Pendente |
| 30 | [**F304**](#f304) | Feature | Co-gestão combinada no lobby | — | ⏳ Pendente |
| 31 | [**F306**](#f306) | Feature | Automático só na carteira da gestora | — | ⏳ Pendente |
| 32 | [**F307**](#f307) | Correção | Estatais com preço vivo e lucro à vista | — | ⏳ Pendente |
| 33 | [**F308**](#f308) | Spike | Spike: impacto do jogador no preço, teto do k e oscilação no pregão | — | ⏳ Pendente |
| 34 | [**F309**](#f309) | Melhoria | Balanceamento das profissões | — | ⏳ Pendente |
| 35 | [**F303**](#f303) | Feature | Dinheiro novo na gestora depois da oferta pública | — | ⏳ Pendente |
| 36 | [**F305**](#f305) | Melhoria | Aquisição hostil como modo de vitória | — | ⏳ Pendente |
| 37 | [**F313**](#f313) | Feature | Assembleia de cotistas com aba própria e aumento de taxa | [F300](#f300) | ⏳ Pendente |
| 38 | [**F311**](#f311) | Feature | Fusão de gestoras | [F301](#f301), [F313](#f313) | ⏳ Pendente |

### 4.3 — Mesa do trader (M24)

> **Objetivo:** O detalhe do ativo vira mesa de operação: a lista de ações aguenta muitas ações, o gráfico abre em tela cheia com as notícias marcadas, o livro de ofertas e o rebalanceamento por meta chegam, e os gráficos seguem um molde só.
>
> **Serve:** N19, N15, N4
>
> **Progresso:** 0/6 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | — | ⏳ Pendente |
| 2 | [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 Em avaliação |
| 3 | [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | — | ⏳ Pendente |
| 4 | [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | — | ⏳ Pendente |
| 5 | [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | — | ⏳ Pendente |
| 6 | [**F279**](#f279) | Feature | Estratégias automáticas novas e revisão das atuais | — | 🔍 Em avaliação |

### 4.4 — Futuros, cenários e estratégias (M25)

> **Objetivo:** A partida testa a carteira em muitos futuros e em cenários com objetivo, com bots que combinam estratégias e tomam crédito, e o backtest corre rápido.
>
> **Serve:** N10, N12, N22, N31
>
> **Progresso:** 0/6 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | — | 🔍 Em avaliação |
| 2 | [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | — | ⏳ Pendente |
| 3 | [**F90**](#f90) | Feature | Cenários | — | ⏳ Pendente |
| 4 | [**F93**](#f93) | Feature | Rumores antecipados | — | ⏳ Pendente |
| 5 | [**F110**](#f110) | Feature | Combinar estratégias | — | ⏳ Pendente |
| 6 | [**F111**](#f111) | Feature | Crédito para estratégias e bots | — | ⏳ Pendente |

### 4.5 — Jogo pela internet e servidor (M27)

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

### 4.6 — Ensino (M28)

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
| 7 | [**F159**](#f159) | Feature | Rodada de novas conquistas e revisão das existentes | [F44](#f44), [F123](#f123) | 🔍 Em avaliação |
| 8 | [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | — | ⏳ Pendente |
| 9 | [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | [F44](#f44) | ⏳ Pendente |
| 10 | [**F225**](#f225) | Docs | Conceitos de economia real na docs e nomeados na tela | [F140](#f140) | ⏳ Pendente |
| 11 | [**F37**](#f37) | Feature | Tema escuro | — | ⏳ Pendente |
| 12 | [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | [F44](#f44) | ⏳ Pendente |
| 13 | [**F141**](#f141) | Docs | README com as features de hoje | [F139](#f139) | ⏳ Pendente |

### Sem versão

> Os itens ⏳ e 🔍 que ainda não entraram em nenhuma versão, do que mais destrava trabalho para o que menos ("Destrava" é quantos itens em aberto esperam por aquele). É daqui que sai a próxima versão; os 💤 ficam só no kanban.

| ID | Tipo | Resumo | Serve | Depende de | Destrava | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [**F284**](#f284) | Feature | Ministério para o partido da base | N34 | — | 0 | ⏳ Pendente |
| [**F285**](#f285) | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | N20 | — | 0 | 🔍 Em avaliação |
| [**F286**](#f286) | Feature | Comandos de trapaça no modo debug | N42 | [F54](#f54) | 0 | ⏳ Pendente |

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: os itens que podem ser pegos agora, com toda dependência já ✅. A ordem segue o plano: primeiro os itens de cada versão (ou marco) na ordem dele, depois o resto pelo "Destrava", que é quantos itens em aberto esperam por aquele, direta ou indiretamente. 💤 (sem prioridade) e 🚫 não entram.

| ID | Tipo | Resumo | Marco | Destrava | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [**F310**](#f310) | Feature | Página Ofertas públicas | M18 · 4.2 · 25º | 0 | Médio | Bom | ⏳ |
| [**F300**](#f300) | Melhoria | Tela da gestora em abas, como a do governo | M18 · 4.2 · 26º | 2 | Alto | Bom | ⏳ |
| [**F312**](#f312) | Melhoria | Cor da expansão na conta que opera | M18 · 4.2 · 27º | 0 | Baixo | Bom | ⏳ |
| [**F301**](#f301) | Correção | Gestor que vira presidente e mais de uma gestora por jogador | M18 · 4.2 · 28º | 1 | Alto | Bom | ⏳ |
| [**F302**](#f302) | Correção | Caixa da gestora sem ficar negativo | M18 · 4.2 · 29º | 0 | Médio | Bom | ⏳ |
| [**F304**](#f304) | Feature | Co-gestão combinada no lobby | M18 · 4.2 · 30º | 0 | Médio | Bom | ⏳ |
| [**F306**](#f306) | Feature | Automático só na carteira da gestora | M18 · 4.2 · 31º | 0 | Médio | Bom | ⏳ |
| [**F307**](#f307) | Correção | Estatais com preço vivo e lucro à vista | M18 · 4.2 · 32º | 0 | Alto | Bom | ⏳ |
| [**F308**](#f308) | Spike | Spike: impacto do jogador no preço, teto do k e oscilação no pregão | M18 · 4.2 · 33º | 0 | Médio | Bom | ⏳ |
| [**F309**](#f309) | Melhoria | Balanceamento das profissões | M18 · 4.2 · 34º | 0 | Médio | Bom | ⏳ |
| [**F303**](#f303) | Feature | Dinheiro novo na gestora depois da oferta pública | M18 · 4.2 · 35º | 0 | Alto | Bom | ⏳ |
| [**F305**](#f305) | Melhoria | Aquisição hostil como modo de vitória | M18 · 4.2 · 36º | 0 | Médio | Bom | ⏳ |
| [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | M24 · 4.3 · 1º | 0 | Médio | Bom | ⏳ |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | M24 · 4.3 · 2º | 0 | — | — | 🔍 |
| [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | M24 · 4.3 · 3º | 0 | Médio | Bom | ⏳ |
| [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | M24 · 4.3 · 4º | 0 | Baixo | Bom | ⏳ |
| [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | M24 · 4.3 · 5º | 0 | Médio | Bom | ⏳ |
| [**F279**](#f279) | Feature | Estratégias automáticas novas e revisão das atuais | M24 · 4.3 · 6º | 0 | — | — | 🔍 |
| [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | M25 · 4.4 · 1º | 0 | — | — | 🔍 |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | M25 · 4.4 · 2º | 0 | Alto | Bom | ⏳ |
| [**F90**](#f90) | Feature | Cenários | M25 · 4.4 · 3º | 0 | Alto | Bom | ⏳ |
| [**F93**](#f93) | Feature | Rumores antecipados | M25 · 4.4 · 4º | 0 | Médio | Médio | ⏳ |
| [**F110**](#f110) | Feature | Combinar estratégias | M25 · 4.4 · 5º | 0 | Médio | Bom | ⏳ |
| [**F111**](#f111) | Feature | Crédito para estratégias e bots | M25 · 4.4 · 6º | 0 | Baixo | Bom | ⏳ |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | M27 · 4.5 · 1º | 2 | — | — | 🔍 |
| [**F60**](#f60) | Feature | Modo servidor dedicado (--headless) | M27 · 4.5 · 4º | 0 | Baixo | Bom | ⏳ |
| [**F14**](#f14) | Feature | Janela desktop nativa | M27 · 4.5 · 5º | 0 | Baixo | Bom | ⏳ |
| [**F56**](#f56) | Feature | Novidades no app | M27 · 4.5 · 6º | 0 | Baixo | Bom | ⏳ |
| [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | M28 · 4.6 · 1º | 1 | — | — | 🔍 |
| [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | M28 · 4.6 · 2º | 0 | Médio | Bom | ⏳ |
| [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | M28 · 4.6 · 3º | 0 | Baixo | Bom | ⏳ |
| [**F131**](#f131) | Feature | Catálogo de padrões de vela | M28 · 4.6 · 4º | 0 | — | — | 🔍 |
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | M28 · 4.6 · 6º | 1 | — | — | 🔍 |
| [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | M28 · 4.6 · 8º | 0 | Alto | Médio | ⏳ |
| [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | M28 · 4.6 · 9º | 1 | Alto | Bom | ⏳ |
| [**F37**](#f37) | Feature | Tema escuro | M28 · 4.6 · 11º | 0 | Médio | Médio | ⏳ |
| [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | M28 · 4.6 · 12º | 1 | Médio | Bom | ⏳ |
| [**F284**](#f284) | Feature | Ministério para o partido da base | — | 0 | Alto | Médio | ⏳ |
| [**F285**](#f285) | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | — | 0 | — | — | 🔍 |
| [**F286**](#f286) | Feature | Comandos de trapaça no modo debug | — | 0 | Médio | Bom | ⏳ |

---

## ⏳ Pendente

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F6** | Feature | Link de convite pela internet no lobby | N2 | — | M27 · 4.5 | [F5](#f5) | Médio | Médio | Alto | Bom |
| **F14** | Feature | Janela desktop nativa | — | — | M27 · 4.5 | — | Baixo | Baixo | Baixo | Bom |
| **F28** | Feature | Muitos futuros (Monte Carlo) | N10 | D7 | M25 · 4.4 | — | Alto | Alto | Alto | Bom |
| **F37** | Feature | Tema escuro | N15 | — | M28 · 4.6 | — | Médio | Baixo | Médio | Médio |
| **F56** | Feature | Novidades no app | N14 | — | M27 · 4.5 | — | Baixo | Baixo | Médio | Bom |
| **F60** | Feature | Modo servidor dedicado (--headless) | — | — | M27 · 4.5 | — | Baixo | Baixo | Baixo | Bom |
| **F72** | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | N15 | — | M24 · 4.3 | — | Médio | Baixo | Médio | Bom |
| **F81** | Manutenção | CORS restrito à mesma origem | — | — | M27 · 4.5 | [F6](#f6) | Baixo | Médio | Baixo | Médio |
| **F90** | Feature | Cenários | N22 | D18 | M25 · 4.4 | — | Alto | Médio | Alto | Bom |
| **F93** | Feature | Rumores antecipados | N31 | D18 | M25 · 4.4 | — | Médio | Médio | Médio | Médio |
| **F110** | Feature | Combinar estratégias | N4 | D8 | M25 · 4.4 | — | Médio | Médio | Médio | Bom |
| **F111** | Feature | Crédito para estratégias e bots | N4, N33 | D8 | M25 · 4.4 | — | Baixo | Baixo | Médio | Bom |
| **F132** | Feature | Tópicos de "como se joga" do Como jogar | N25 | D21 | M28 · 4.6 | — | Médio | Baixo | Alto | Bom |
| **F133** | Feature | Tópicos de conceitos do Como jogar | N25 | D21 | M28 · 4.6 | — | Baixo | Baixo | Médio | Bom |
| **F139** | Docs | Demonstração regravada com o jogo de hoje | N25 | — | M28 · 4.6 | [F44](#f44) | Médio | Baixo | Alto | Bom |
| **F140** | Docs | Docs reorganizada por tipo de leitor | N25 | D21 | M28 · 4.6 | [F44](#f44) | Alto | Baixo | Alto | Bom |
| **F141** | Docs | README com as features de hoje | N25 | — | M28 · 4.6 | [F139](#f139) | Baixo | Baixo | Alto | Excelente |
| **F167** | Feature | Notícias do ativo como marcadores no gráfico de preço | — | — | M24 · 4.3 | — | Baixo | Baixo | Médio | Bom |
| **F197** | Melhoria | Rebalanceamento por meta com várias classes | N4 | — | M24 · 4.3 | — | Médio | Médio | Médio | Bom |
| **F221** | Performance | Lista de ações que aguenta muitas ações | N40 | — | M24 · 4.3 | — | Médio | Médio | Médio | Bom |
| **F225** | Docs | Conceitos de economia real na docs e nomeados na tela | N41, N25 | D21 | M28 · 4.6 | [F140](#f140) | Alto | Baixo | Alto | Bom |
| **F227** | Feature | Intensidade das ligações e laboratório da economia | N41, N34 | D20, D21 | M28 · 4.6 | — | Alto | Médio | Médio | Médio |
| **F284** | Feature | Ministério para o partido da base | N34 | — | — | — | Alto | Médio | Médio | Médio |
| **F286** | Feature | Comandos de trapaça no modo debug | N42 | — | — | [F54](#f54) | Médio | Baixo | Alto | Bom |
| **F300** | Melhoria | Tela da gestora em abas, como a do governo | N23, N15 | — | M18 · 4.2 | — | Alto | Médio | Alto | Bom |
| **F301** | Correção | Gestor que vira presidente e mais de uma gestora por jogador | N23 | — | M18 · 4.2 | — | Alto | Médio | Alto | Bom |
| **F302** | Correção | Caixa da gestora sem ficar negativo | N23 | — | M18 · 4.2 | — | Médio | Médio | Alto | Bom |
| **F303** | Feature | Dinheiro novo na gestora depois da oferta pública | N23 | — | M18 · 4.2 | — | Alto | Médio | Alto | Bom |
| **F304** | Feature | Co-gestão combinada no lobby | N23 | — | M18 · 4.2 | — | Médio | Baixo | Médio | Bom |
| **F305** | Melhoria | Aquisição hostil como modo de vitória | N23 | — | M18 · 4.2 | — | Médio | Baixo | Médio | Bom |
| **F306** | Feature | Automático só na carteira da gestora | N23, N4 | — | M18 · 4.2 | — | Médio | Médio | Médio | Bom |
| **F307** | Correção | Estatais com preço vivo e lucro à vista | N34 | — | M18 · 4.2 | — | Alto | Médio | Alto | Bom |
| **F308** | Spike | Spike: impacto do jogador no preço, teto do k e oscilação no pregão | N3, N10 | — | M18 · 4.2 | — | Médio | Baixo | Alto | Bom |
| **F309** | Melhoria | Balanceamento das profissões | N39 | — | M18 · 4.2 | — | Médio | Baixo | Médio | Bom |
| **F310** | Feature | Página Ofertas públicas | N23 | — | M18 · 4.2 | [F299](#f299) | Médio | Baixo | Médio | Bom |
| **F311** | Feature | Fusão de gestoras | N23 | — | M18 · 4.2 | [F301](#f301), [F313](#f313) | Alto | Alto | Médio | Médio |
| **F312** | Melhoria | Cor da expansão na conta que opera | N15, N23 | — | M18 · 4.2 | — | Baixo | Baixo | Médio | Bom |
| **F313** | Feature | Assembleia de cotistas com aba própria e aumento de taxa | N23 | — | M18 · 4.2 | [F300](#f300) | Alto | Médio | Alto | Bom |

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

<a id="f300"></a>
**F300 — Tela da gestora em abas, como a do governo.** Serve N23 e N15. Do playtest de 17/11. A tela da gestora mistura tudo numa página: a oferta pública encerrada fica sempre à vista, os botões de ação ficam soltos no topo, a tabela de rendimentos cresce sem paginar (`fund-distributions-card.tsx`) e empurra os cards para baixo, o relatório mensal fica escondido num botão da composição (`fund-composition.tsx:42-62`), e a recompra tem dois jeitos no diálogo (`buyback-dialog.tsx:70-101`). **Decidido em 18/11.** **Topo fixo acima das abas, em todas elas:** identidade (marca, nome, ticker, etapa), os quatro números comuns com ⓘ (patrimônio, patrimônio por cota, preço no mercado, ágio) e o aviso da fase; o patrimônio por cota começa em R$ 100, como `FIRST_NAV`. **Primeira aba "Suas ações", no molde da aba de mesmo nome do governo** (`actions-tab.tsx`, `action-row.tsx`, `action-card.tsx`): um cartão por papel (Como gestor, Como cotista), cada ação numa linha com ícone, explicação, o motivo quando está travada e um botão; botão cheio só na ação principal, os outros contornados; o bloco "Decida agora" no topo para o que tem prazo (votação aberta, preferência da emissão, convite de co-gestão). Quem não gere também vê a aba, com as ações de cotista: comprar na emissão com preferência, votar ou convocar a assembleia, negociar a cota na renda variável, responder convite; sem cota, só a oferta aberta e o atalho para negociar. Os componentes de linha e de grupo do governo sobem para `shared/` (dois consumidores). **Gestora fechada:** os passos (levar da carteira, conferir as taxas, abrir a oferta pública) moram em Suas ações, e a Visão geral vira um estado vazio que explica que preço e histórico chegam com a bolsa. **Abas do gestor:** Suas ações, Visão geral, Carteira, Cotas (cotistas, emissões e a oferta encerrada como histórico), Rendimentos (paginada), Assembleia (F313), Relatório e Configurações (taxas, parte do lucro distribuída e o automático da F306). Quem não gere vê Suas ações, Visão geral, Cotas, Rendimentos, Assembleia e Relatório. **Visão geral:** o gráfico do preço contra o patrimônio por cota ganha a terceira linha, o preço de ranking, com a faixa de ±30% e o número com ⓘ. **Rendimentos:** "parte do lucro distribuída" é a fração do lucro realizado do mês que vai aos cotistas (padrão 95%, vale no mês seguinte), e o controle mostra a prévia em reais por cota com o lucro do mês; o dividend yield é consequência, não controle. **Relatório:** aberto a qualquer cotista, com a rosca da alocação da carteira. **Recompra:** um caminho só, explicado no próprio diálogo. Desenho na rodada de canvas da linha da gestora, com todas as telas da 4.2 juntas.

<a id="f301"></a>
**F301 — Gestor que vira presidente e mais de uma gestora por jogador.** Serve N23. Do playtest de 17/11. O gestor de uma gestora fechada virou presidente; na posse, `on_office` (`fund_book.py:1163-1179`) passou a gestão ao co-gestor (outro jogador, que já tinha a própria gestora), embora o gestor tivesse 100% das cotas. Daí: a lista de gestoras diz "gerida por" quem tem fatia mínima ou nenhuma; o co-gestor promovido não alcança a tela de gestão da segunda gestora (o front supõe uma gestora por jogador: `funds.tsx:33-34`, `sidebar.tsx:72-73`); o dono-presidente perde o acesso à própria gestora e vê "Funde a sua gestora". **A posse segue a regra de hoje:** o co-gestor de maior participação assume e, sem co-gestor, a gestora congela com a carteira do presidente ou segue no automático (F306). **No fim do mandato sem reeleição, o ex-presidente retoma a gestão:** a gestora congelada volta para a mão dele, e a que passou a um co-gestor volta a tê-lo como gestor principal; hoje nada desfaz a troca da posse. **Gerir mais de uma gestora é um caso normal do jogo,** porque a aquisição hostil (F305) termina nele. **O menu Gestoras vira a lista da sala (decidido em 18/11):** três blocos, as que você gere, as em que você tem cotas e as outras, cada linha com ticker, gestor, patrimônio e a sua parte, abrindo a gestora; "Funde a sua gestora" vira um botão no topo, só para quem não tem gestora. O seletor de conta lista todas as geridas, e a tela distingue gestor, co-gestor e cotista. **Fundar exige não ter gestora:** quem perdeu a sua (a assembleia trocou o gestor, alguém comprou o controle) funda outra; quem tem uma, inclusive congelada pela presidência, não. O backend recusa em `found_fund` (`simulation.py:1305-1330`), que hoje só tem o redirecionamento do front (`fund-found.tsx:20`). **O Fundo Soberano não é gestora:** ele só reaproveita o seletor do caixa, e o menu lateral e a lista de gestoras nunca o tratam como uma. As cotas de quem não gere chegam pela renda variável (F299). Desenho da lista na rodada de canvas da linha da gestora.

<a id="f302"></a>
**F302 — Caixa da gestora sem ficar negativo.** Serve N23. Do playtest de 17/11. A gestora ficou com caixa negativo em 106 dias, o pior em −239 mil: a taxa de performance de 225,6 mil foi cobrada logo depois de uma distribuição de 1,14 milhão ter esvaziado o caixa. `charge_fund_fee` cobra sem olhar o caixa, e a distribuição não reserva as taxas. **Decidido em 18/11: taxa a pagar.** A parte da taxa que o caixa não cobre vira "taxa a pagar", uma dívida da gestora com o gestor: ela desconta do patrimônio pelo termo de dívida que `nav_per_quota` já tem, e o próximo dinheiro que entra (dividendo, juro, venda de ativo) quita a taxa a pagar antes de qualquer outra coisa. A distribuição paga só o caixa que sobra depois da taxa a pagar. O gestor recebe quando a gestora paga, e os co-gestores pela divisão de hoje (`split_fee`). A Carteira e o Relatório mostram a taxa a pagar em aberto.

<a id="f303"></a>
**F303 — Dinheiro novo na gestora depois da oferta pública.** Serve N23. Do playtest de 17/11. Depois da oferta pública não há como pôr dinheiro novo na gestora: o aporte existe só antes da listagem (`contribute`, `fund_book.py:450`), a emissão vai a público, o co-gestor não aporta e o crédito pega sempre a conta pessoal (`routes/credit.py:25-104` usa o ClientID; `credit_book` não conhece gestora). Desde a cota negociada na renda variável, os bots compram a sobra da emissão no último pregão quando o preço fica abaixo do que acham que a cota vale, e a emissão pública deve passar a vender. **Decidido em 18/11.** **Emissão dirigida ao gestor e aos co-gestores:** o gestor emite cotas novas para si ou para um co-gestor, que aceita na pendência; elas são liquidadas no mesmo pregão e pagas pelo caixa pessoal de quem compra. **Preço: o maior entre o patrimônio por cota e o preço de ranking.** Com deságio, a cota sai ao patrimônio por cota e ninguém é diluído; com ágio, sai ao preço de ranking e o ganho fica na gestora (patrimônio por cota de R$ 100 e ranking de R$ 120: sai a R$ 120). No modo aquisição hostil, a emissão respeita o teto do gestor (1 − participação mínima do mercado). **Empréstimo em nome da gestora:** o crédito passa a atender a conta ativa, e a gestora toma empréstimo pelas mesmas regras da conta pessoal (`credit/rules.py`): a nota sai da alavancagem, da volatilidade e do histórico de pagamento sobre o patrimônio da gestora, as parcelas saem do caixa dela e a dívida desconta do patrimônio por cota. Só o gestor toma, sem assembleia. A emissão dirigida a um cotista qualquer fica fora (abriria o aliado que fura o teto da aquisição hostil). Desenho do diálogo da emissão dirigida na rodada de canvas da linha da gestora.

<a id="f304"></a>
**F304 — Co-gestão combinada no lobby.** Serve N23. Do playtest de 17/11. A co-gestão só se combina dentro da partida (convite com validade de 7 dias). No lobby, o jogador escolhe começar como co-gestor da gestora de outro jogador, no mesmo molde do convite de vice dos partidos: quem funda convida, o convidado aceita na própria preparação e a partida começa com a co-gestão de pé. Respeita o teto de 3 co-gestores. Desenho do convite no lobby na rodada de canvas da linha da gestora.

<a id="f305"></a>
**F305 — Aquisição hostil como modo de vitória.** Serve N23. Do playtest de 17/11. O modo aquisição hostil é um interruptor no card da expansão de gestoras (`funds-card.tsx:152-186`), e isso dá a entender que ele combina com qualquer tipo de partida, quando ele mesmo define como se vence. **Decidido em 18/11.** A aquisição hostil vira um tipo de partida (`GameType`, `game-types.ts`), ao lado de Clássica, Corrida pela meta, Independência financeira e Política, e sai do card da expansão. Escolher o tipo liga a expansão Gestoras e a mantém ligada; a carência e a participação mínima do mercado aparecem embaixo do tipo, como a meta nos tipos de meta. **Vitória: o último de pé,** como o código já conta: quem perde para a assembleia a gestora que fundou é eliminado e vira espectador, e a partida acaba quando sobra um jogador ativo (`simulation.py:2262`). Se a data final chega com mais de um de pé, vence o maior patrimônio do ranking. A dica do lobby diz "sobra um jogador", e não "sobra uma gestora". Quem conquista gestoras passa a gerir várias (F301) e as junta pela fusão (F311). Desenho do tipo no lobby na rodada de canvas da linha da gestora.

<a id="f306"></a>
**F306 — Automático só na carteira da gestora.** Serve N23 e N4. Do playtest de 17/11. O automático (a estratégia que opera pelo jogador, `useMyStrategy`) vale só para a conta pessoal e trava as boletas dela. O gestor liga uma estratégia só na carteira da gestora, na aba Configurações da gestora, e segue operando à mão a conta pessoal; o lock das boletas (`useTradeLock.ts`) passa a olhar a conta ativa. **Na presidência:** o gestor que toma posse sem co-gestor deixa a gestora no automático em vez de congelada, e ela segue operando durante o mandato pela estratégia escolhida; no fim do mandato sem reeleição ele retoma o controle e desliga o automático (a regra da posse está na F301). O menu do automático na aba Configurações se redesenha na rodada de canvas da linha da gestora (o desenho de 17/11 ficou fraco).

<a id="f307"></a>
**F307 — Estatais com preço vivo e lucro à vista.** Serve N34. Do playtest de 17/11. A estatal fundada ficou em linha reta: o valor justo sorteia um retorno por ano (`fair_value.py`, média abaixo do juro real, desvio de 10%) e o divide em fatores iguais por dia, então dentro do ano é uma reta, e num ano de sorteio negativo é uma reta descendo; sem negócio, o fechamento repete o último preço; o impacto da compra do jogador decai e parece "só cair"; e num mês de lucro negativo não há dividendo. O volume 0 com milhões no livro é a escada do formador de mercado esperando: volume conta só negócio fechado. A política de dividendos do governo já vale (Reinvestir paga 25% do lucro e cresce o porte 1% ao mês; Normal 50%; Apertar 80% e encolhe o porte, `payout.py`, `gdp.py`). **Decidido em 18/11.** **Preço de referência diário em três camadas:** a tendência do ano ligada ao PIB (ano de PIB acima da média dá retorno maior, e o que o presidente faz no PIB mexe na estatal), a sensibilidade à bolsa do dia (0,8 para começar: a bolsa cai 2% e a estatal cai 1,6%) e um ruído próprio que puxa de volta para o valor justo. Sem negócio, o fechamento é essa referência, e a escada do formador se monta em volta dela. A fonte do retorno da bolsa e a calibração se fecham no plano. **Os bots negociam estatais** como qualquer ação ou cota. **Tela da estatal:** gráfico mensal de lucro, dividendo e valor justo, com o que o jogo já guarda (`state_company_months`), sem receita, que o modelo não tem; o mês sem dividendo diz por quê; a fatia do governo aparece na composição. A estatal importada segue a história. Desenho da tela na rodada de canvas da linha da gestora.

<a id="f308"></a>
**F308 — Spike: impacto do jogador no preço, teto do k e oscilação no pregão.** Serve N3 e N10. Do playtest de 17/11. A partida das estatais rodou com intensidade do impacto (k) 3,0, contra 0,05 das outras; houve negócios a preços absurdos (uma ação foi de 1.837 a 237.871) e o gráfico da estatal saltou e voltou ao pausar. O impacto (`k·√(qtd/volume médio)` com decaimento) entra nas leituras e não nos candles salvos, por isso o preço volta ao pausar. **Decidido em 18/11: o campo do k fica sem teto, com aviso.** Acima de 0,10, o lobby avisa que o preço salta, com o exemplo da compra de 4 vezes o volume médio (k 0,10 sobe 20%; k 1 sobe 200%). O spike mede contra o histórico real a faixa realista de k, o texto do aviso com esses números e se o impacto dentro do pregão pode ser opção da sala sem mexer no modelo realista que o backtest usa.

<a id="f309"></a>
**F309 — Balanceamento das profissões.** Serve N39. Do playtest de 17/11. Na partida de Independência financeira, o bot Herdeiro venceu no primeiro dia: a meta era 1,2 milhão (12 × 5.000 ÷ 5%) e o capital inicial dele foi de 1,58 milhão, porque a validação da meta (`dto/simulation.py:66-95`) compara com o caixa da sala, e não com o capital do Herdeiro (caixa mais o valor presente dos salários). **Decidido em 18/11: meta acima do capital de todos.** A meta precisa passar do maior capital inicial entre as profissões da sala, bots incluídos (Corrida pela meta: a meta; Independência financeira: 12 × despesa ÷ taxa de saque); com um Herdeiro na sala a meta mínima sobe e o lobby explica "meta mínima de R$ X por causa do Herdeiro", e a partida não começa com a meta abaixo dela. **Profissões fracas:** o script de calibração da sessão de 18/11 mediu o Freelancer em 0,38× o CLT em 26 anos com IPCA e o Recém-formado em 0,47× em 5 anos. O ajuste leva cada profissão para a faixa de 0,8× a 1,25× o patrimônio final do CLT nos horizontes de 5, 10 e 26 anos, por número ou por mecânica própria.

<a id="f310"></a>
**F310 — Página Ofertas públicas.** Serve N23. Da rodada de canvas da tela da gestora em abas, em 17/11. A compra na oferta pública e na sobra da emissão já sai pelo livro do detalhe da cota na renda variável, que mostra a venda em aberto (preço fixo, quanto sobra e até quando); a tela da gestora leva até lá. Falta quem não tem gestora achar as ofertas da sala: como no app das corretoras, uma página própria no menu lateral, "Ofertas públicas", com as ofertas e emissões abertas da sala, cada uma com o preço fixo, os pregões que faltam e a preferência do cotista na emissão, o atalho para o detalhe da cota e o histórico das encerradas. A emissão segue no card da gestora. A abertura da oferta pública passa a chegar em janela (o nível WINDOW do jornal, no centro da tela, sem pausar), com o botão que leva à compra; a emissão segue no cartão do canto. Desenho na rodada de canvas da linha da gestora.

<a id="f311"></a>
**F311 — Fusão de gestoras.** Serve N23. Da conversa sobre posse de gestoras, em 18/11. No modo aquisição hostil (F305) o jogador acaba gerindo várias gestoras (F301), e controlar dez ao mesmo tempo é inviável. A fusão junta duas: a gestora mãe incorpora a filha, o ticker que fica é o da mãe, e tudo o que a filha tem (caixa, ações, títulos e cotas de outros ativos) passa para a mãe; a filha deixa de existir e sai da renda variável. **Decidido em 18/11: as assembleias das duas aprovam.** Quem gere as duas propõe a fusão, e ela vira pauta na assembleia de cada uma, com 5 pregões de votação; sai se a maioria de quem votou aprovar nas duas. Cada cotista da filha recebe cotas da mãe pela relação entre os patrimônios por cota do dia da aprovação (filha a R$ 50 e mãe a R$ 100: duas cotas da filha viram uma da mãe), e quem votou contra pode sair recebendo o patrimônio por cota, pago pela filha antes da incorporação. O plano fecha de onde sai esse pagamento quando o caixa da filha não cobre. Depende da assembleia com aba própria (F313). Desenho na rodada de canvas da linha da gestora.

<a id="f312"></a>
**F312 — Cor da expansão na conta que opera.** Serve N15 e N23. Do comentário no canvas da tela da gestora, em 18/11. Os desenhos perderam a cor da expansão, e no app nada lembra o jogador de que a ordem sai pela gestora. Quando a conta ativa no topo é uma gestora, a boleta e o botão de comprar e vender ficam na cor da expansão Gestoras (a variante `fund` do botão já existe); com a conta do Fundo Soberano, na cor da expansão do governo. O que muda de cor (só o botão, a boleta inteira ou também o seletor de conta) se escolhe por variantes na rodada de canvas da linha da gestora.

<a id="f313"></a>
**F313 — Assembleia de cotistas com aba própria e aumento de taxa.** Serve N23. Do comentário no canvas da tela da gestora, em 18/11. A assembleia de cotistas existe em toda partida com Gestoras (`fund_assembly.py`): quem tem 10% das cotas convoca, a votação dura 5 pregões, vence a maioria de quem votou (bots e formador de mercado não votam) e a única pauta é trocar o gestor. Ela mora num bloco da página da gestora (`fund-assembly.tsx`) e não chega às pendências, que só levam o convite de candidato (`FUND_ASSEMBLY_INVITE`). **Decidido em 18/11.** **Aba Assembleia na tela da gestora, no nível da aba Congresso do governo:** a votação aberta com placar, pauta, prazo e o voto; a convocação; o histórico das encerradas. **Pautas:** trocar o gestor (a de hoje), a fusão de gestoras (F311) e o aumento de taxa: subir a taxa de administração ou a de performance passa a depender de aprovação e vale no mês seguinte ao resultado; baixar continua livre. Cada pauta tem a própria votação; o intervalo de 3 meses entre convocações segue valendo para a troca de gestor. **Pendência:** a votação aberta vira pendência para quem tem cota e ainda não votou, com o prazo, e entra no "Decida agora" da aba Suas ações. Desenho na rodada de canvas da linha da gestora.

---

## 🔍 Em avaliação

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Falta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **F5** | Spike | Spike: provider de túnel pela internet | N2 | — | M27 · 4.5 | — | Escolhe o provider da F6 |
| **F34** | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | N19 | — | M24 · 4.3 | — | Escolhe a biblioteca de gráfico |
| **F123** | Melhoria | Redesenhar o aviso de conquista desbloqueada | N22, N15 | — | M28 · 4.6 | — | Escolher o desenho do aviso no canvas; liga à F122 |
| **F131** | Feature | Catálogo de padrões de vela | N19 | — | M28 · 4.6 | — | Tópico do Como jogar com cada padrão animado |
| **F158** | Melhoria | Animações do Como jogar revistas | N25 | — | M28 · 4.6 | — | O visual numa rodada no canvas dedicada: animações atuais contra as primeiras, número do passo fora da cena, cursor e destaque, e o palco em tamanho real mostrando só o trecho do passo |
| **F159** | Feature | Rodada de novas conquistas e revisão das existentes | N22 | D1 | M28 · 4.6 | [F44](#f44), [F123](#f123) | Quais conquistas novas entram e o que muda nas existentes; decidido com o usuário numa rodada de ideias |
| **F193** | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | N25, N19 | D21 | M28 · 4.6 | [F158](#f158) | O molde do tópico em fases, quais indicadores entram primeiro e onde o 'i' abre o tópico sem cobrir a tela (F183). |
| **F202** | Performance | Backtest que corre mais rápido que a partida comum | N10 | D8 | M25 · 4.4 | — | Medir o dia do backtest por etapa e escolher quais custos saem do caminho dele (eventos em memória gravados em lote, leituras do que o motor acabou de gravar, trava por pregão, imposto por dia) |
| **F279** | Feature | Estratégias automáticas novas e revisão das atuais | N4, N8 | — | M24 · 4.3 | — | Medir as estratégias atuais em várias bases com governo, dólar e crédito; calibrar os níveis de dificuldade; escolher as estratégias novas |
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
| **F44** | Feature | Expansão Gestoras: fundar a gestora e abrir capital | N23 | — | M18 · 4.2 |
| **F55** | Feature | Modo aquisição hostil | N23 | — | M18 · 4.2 |
| **F101** | Feature | Carteira separada do jogador | N23 | D9 | M18 · 4.2 |
| **F102** | Feature | Gestoras: emissão de novas cotas e recompra | N23 | — | M18 · 4.2 |
| **F103** | Feature | Gestoras: troca de gestor pela assembleia | N23 | — | M18 · 4.2 |
| **F104** | Feature | Gestoras: co-gestores | N23 | — | M18 · 4.2 |
| **F105** | Feature | Gestoras: rendimentos mensais | N23 | — | M18 · 4.2 |
| **F179** | Melhoria | Topbar que cabe com a corrida e o governo | N15 | — | M18 · 4.2 |
| **F211** | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | N15 | — | M18 · 4.2 |
| **F249** | Manutenção | Núcleo do backend sem import de features | — | — | M18 · 4.2 |
| **F255** | Feature | Estatais | N34, N41 | D20 | M18 · 4.2 |
| **F287** | Melhoria | Slots dos jogadores do lobby no desenho anterior | N15, N20 | — | M18 · 4.2 |
| **F288** | Melhoria | Badge de profissão legível no lobby e na Minha preparação | N15, N20 | — | M18 · 4.2 |
| **F289** | Melhoria | Cards de profissão com vantagens e desvantagens | N39, N25 | — | M18 · 4.2 |
| **F290** | Feature | Profissões novas | N23, N34 | D19 | M18 · 4.2 |
| **F291** | Melhoria | Locador com aluguel de 1,1× o salário | N39 | — | M18 · 4.2 |
| **F292** | Feature | Fundo Soberano: o governo compra ações e cotas | N34, N41 | — | M18 · 4.2 |
| **F293** | Feature | Profissões das expansões: Comissionado e Banqueiro de ofertas | N23, N34 | D19 | M18 · 4.2 |
| **F294** | Melhoria | Adicionar vários bots de uma vez | N8 | — | M18 · 4.2 |
| **F295** | Manutenção | Orçamento, painel econômico e base do governo por tempo real | N15 | — | M18 · 4.2 |
| **F296** | Correção | Correções do playtest: gestoras e renda variável | N23 | — | M18 · 4.2 |
| **F297** | Correção | Correções do playtest: governo e eleição | N34 | — | M18 · 4.2 |
| **F298** | Correção | Correções do playtest: lobby, bots e profissões | N39, N8 | — | M18 · 4.2 |
| **F299** | Feature | Cota de gestora negociada na renda variável | N23 | — | M18 · 4.2 |

<a id="f44"></a>
**F44 — Expansão "Gestoras": fundar a gestora e abrir capital.** Serve N23. Inspiração: o Capitalism Lab (oferta pública, emissão de novas ações, recompra, compra de ações dos concorrentes), o OpenTTD e o Software Inc. Lá cada jogador é uma empresa que fabrica ou transporta; aqui tudo é finanças, então a empresa de cada jogador é uma gestora, e o que ela vende é o próprio desempenho. **Como expansão:** ligável por partida numa **aba própria "Expansões"** no lobby, com banner, emblema e "o que muda", como a loja de DLC dos jogos da Paradox; é enfeite visual, o sistema é o mesmo ligado ou não. **A gestora** tem nome e ticker de 4 letras mais 11, como cota de FII na B3 (o servidor recusa letras que já existam entre os ativos importados), e no livro de ofertas redesenhado (F211) cada linha leva a cor e a sigla de quem pôs a ordem, jogador ou bot, para não se confundir com ativo real. O jogador a funda levando **caixa, ações e títulos** da carteira em troca de cotas, e a opera **pelo rótulo do caixa na topbar** ("Caixa · Aurora Gestão ▾"): o rótulo abre a lista das contas, a pessoal e as gestoras que ele gere, e a escolhida vale para todas as telas de mercado, com uma faixa verde-petróleo dizendo qual conta está ativa. O botão "Operando" do desenho de 22/out sai, porque disputava a linha com a corrida e o governo (F179). **É um fundo fechado listado, como um FII:** (1) **oferta pública** quando o gestor quiser — cotas novas ao preço do patrimônio por cota (patrimônio de R$ 100 mil em 1.000 cotas dá R$ 100), e o dinheiro de quem compra entra na gestora: é investir no amigo; (2) **mercado** — depois da oferta, as cotas são negociadas no livro de ofertas que a renda variável já tem, e o preço sai da oferta e da procura, acima do patrimônio por cota (ágio) quando a sala acredita no gestor e abaixo (deságio) quando não; (3) **liquidez** — a liquidez de fundo do livro nasce dos candles de cada ativo, e a cota não tem candle, então um formador de mercado sintético põe ordens de compra e venda em volta do patrimônio por cota, numa faixa de 20% para cima e para baixo recalculada todo dia; dentro da faixa, o preço sai dos jogadores, e o livro tem contraparte até numa sala de 2; (4) **taxas** — a gestora paga aos gestores taxa de administração todo mês sobre o patrimônio e taxa de performance a cada 6 meses sobre o que passar do CDI, com teto na partida de **2% ao ano de administração e 20% de performance**, e cada gestor escolhe até o teto. Uma taxa nova passa a valer no mês seguinte, com aviso no jornal para a sala. A performance respeita a **marca d'água**, o maior patrimônio por cota sobre o qual a taxa já foi cobrada: se a cota cai de R$ 100 para 80 e volta a 100, a recuperação não paga performance. **O lucro fica dentro da gestora** e valoriza a cota. **Por que abrir capital, e quando:** as taxas são sobre o dinheiro dos outros, e com ágio as cotas do próprio gestor valem mais no ranking; o custo é ficar exposto, porque vender mais da metade abre a porta para perder o controle (F103). Abrir cedo, sem histórico, tende a sair com pouca procura; abrir depois de um bom ano tende a sair com ágio. **O gestor e a própria gestora:** o gestor negocia com a gestora pelo livro como qualquer jogador; a linha leva a sigla dele, então a negociação fica à vista, e quem cobra é a sala, vendendo a cota (deságio) ou trocando o gestor (F103). **Quem compra cotas:** pessoas, jogadores e bots, e o Fundo Soberano do governo; nunca gestoras, o que impede a participação cruzada (A com cotas da B, que tem cotas da A). **Os bots** não fundam gestora: compram e vendem cotas pelas estratégias que já têm, com a cota como mais um ativo do livro, e cada bot fica com no máximo 20% das cotas de uma gestora, para não decidir a assembleia; na assembleia (F103) eles se abstêm. **Regras para o cálculo fechar:** No ranking, cada jogador soma a carteira pessoal, as taxas recebidas e as cotas que tem pelo **preço de ranking**: a média dos negócios dos últimos 20 pregões, ponderada pelo volume e limitada a 30% acima ou abaixo do patrimônio por cota; sem negócio no período, vale o patrimônio por cota. Um ágio de até 30% conta, e um negócio forçado a R$ 1.000 numa cota de R$ 100 conta no máximo como R$ 130. A carteira da gestora só conta através das cotas, sem contar o mesmo dinheiro duas vezes. **Estrutura:** a carteira própria da gestora é a F101; a cota é um ativo no livro de ofertas, com o patrimônio por cota publicado a cada dia. **Com a expansão Governo & Política (F95):** quando o gestor vence a eleição, na posse ele deixa de operar a gestora e de receber as taxas, porque a carteira do presidente fica congelada; um co-gestor (F104) assume e, sem co-gestor, a gestora congela até o fim do mandato; as cotas que ele tem continuam dele. A F95 sai antes, então a carteira congelada do presidente já existe quando a gestora for implementada: cabe a esta feature estender o congelamento à gestora. **Nas features seguintes:** emissão de novas cotas e recompra (F102), troca de gestor pela assembleia (F103), co-gestores (F104) e rendimentos mensais (F105).
 **Na preparação do lobby:** a identidade da gestora (nome e ticker) fica salva no perfil, no molde do Meu partido, e entra numa aba própria da preparação (F174); a gestora preparada é fundada no 1º dia, vazia, e o jogador leva para ela o que quiser da carteira.

**Plano.**

1. **Protótipo pelo CLI**, antes de qualquer tela: uma partida com bots e duas gestoras, o formador sintético na faixa de 20% e jogadores simulados comprando e vendendo cotas, para calibrar a faixa e o preço de ranking.
2. **Redesenho no canvas** das telas das Gestoras na largura de referência de 1920, dentro do layout base, na mesma sessão da topbar (F179): página da gestora, fundar, ações do gestor, a troca de conta pelo caixa, a cota vista pelos outros e os estados. Os desenhos de 22/out são de 1440 e anteriores ao layout atual.
3. **Backend:** a gestora como conta sobre a carteira separada (F101), a cota como ativo do livro com o patrimônio por cota publicado a cada dia, o formador sintético, as taxas com marca d'água, o preço de ranking e o teto de 20% por bot.
4. **Frontend:** a aba Expansões, a aba da gestora na preparação, as telas desenhadas e a troca de conta pelo caixa.
5. **Gestora do presidente:** o congelamento da carteira do presidente passa a valer para a gestora dele.

**Aceite:** no protótipo, sem procura a cota negocia perto do patrimônio por cota; com compra contínua, o preço sobe dentro da faixa e aparece ágio; o formador nunca negocia fora da faixa de 20%; um negócio forçado não leva o preço de ranking além de 30% do patrimônio por cota.

<a id="f55"></a>
**F55 — Modo aquisição hostil.** Todo jogador funda a gestora no 1º dia; no fim da carência o gestor acima do limite entra em oferta automática ao patrimônio líquido e o formador compra a sobra; perder a assembleia da própria gestora elimina o jogador, e a partida acaba quando resta um só ativo.

<a id="f101"></a>
**F101 — Carteira separada do jogador.** Serve N23; segue a D9. A base da expansão Gestoras (F44): hoje eventos e snapshots pertencem ao jogador (`user_id`), e a gestora precisa de carteira própria. Entra uma tabela `portfolios`, e eventos e snapshots passam a apontar para a carteira; a carteira pessoal de cada jogador é migrada uma a uma, inclusive nas partidas salvas. Nada muda na tela: cada jogador segue com uma carteira só até a F44 existir. Gatilho: a F44 sair da avaliação.

<a id="f102"></a>
**F102 — Gestoras: emissão de novas cotas e recompra.** Emissão com preço fixo, preferência de 10 pregões e sobra de 5, recompra pelo livro com queima das cotas e prévias calculadas no backend; página das gestoras na documentação.

<a id="f103"></a>
**F103 — Gestoras: troca de gestor pela assembleia.** Serve N23; amplia a expansão Gestoras (F44). É o custo de abrir capital; a defesa é a recompra (F102) e comprar cotas com as taxas recebidas. O modo aquisição hostil (F55) se apoia nesta regra.

**Regras.**

1. **Convocar:** quem tem pelo menos 10% das cotas convoca a assembleia e já indica o novo gestor: ele mesmo ou um aliado que aceite o convite.
2. **Votação:** dura 5 pregões. Cada cotista vota a favor ou contra, e o voto conta as cotas que ele tem no fim da janela, então comprar cotas durante a votação vira uma corrida entre quem quer trocar e quem defende. O gestor vota com as cotas dele; os bots se abstêm.
3. **Resultado:** vence a maioria das cotas que votaram; empate mantém o gestor.
4. **O gestor afastado** vira cotista comum: mantém as cotas e as taxas já recebidas, perde a operação e as taxas futuras, e só funda outra gestora depois de 6 meses de jogo.
5. **Intervalo:** cada gestora tem no máximo uma assembleia a cada 3 meses, para a convocação não virar assédio permanente.

**Plano.** Backend da assembleia: convocação, votos, apuração no fim do 5º pregão e a troca do gestor, que leva junto o acesso à conta da gestora. Aviso a todos os cotistas e manchete no jornal na convocação e no resultado. A tela de votação entra na sessão de canvas das Gestoras.

**Aceite:** comprar cotas no último pregão da votação muda o resultado; empate mantém o gestor; o afastado não funda gestora antes de 6 meses.

<a id="f104"></a>
**F104 — Gestoras: co-gestores.** Serve N23; amplia a expansão Gestoras (F44). A gestora pode ter mais de um gestor: eles operam a mesma carteira pela troca de conta no caixa da topbar e dividem as taxas, como sócios.

**Quem manda:** o gestor principal convida, escolhe a parte das taxas de cada co-gestor (por exemplo, 30% para o co-gestor e 70% para ele) e pode tirá-lo a qualquer momento. O co-gestor aceita o convite e pode sair quando quiser. A parte das taxas não depende das cotas: quem tem cotas ganha pela cota, e o controle continua seguindo as cotas pela assembleia (F103).

**Com Governo & Política:** o co-gestor assume a gestora quando o gestor vira presidente (F95); com mais de um, assume o que tem a maior parte das taxas.

**Plano.** Convite e aceite por aviso; a lista de co-gestores na página da gestora, com a parte de cada um; a divisão no pagamento mensal da administração e no semestral da performance; a saída e a remoção. O acesso à conta da gestora pelo caixa vale para todos os gestores. As telas entram na sessão de canvas das Gestoras.

**Aceite:** a soma das partes dá 100% da taxa; remover um co-gestor tira o acesso no mesmo pregão.

<a id="f105"></a>
**F105 — Gestoras: rendimentos mensais.** A gestora distribui parte do lucro realizado do mês (padrão 95%, de 0 a 100%, escolhida pelo gestor); a performance e a marca d'água seguem o retorno total.

<a id="f179"></a>
**F179 — Topbar que cabe com a corrida e o governo.** Serve N15. O controle de velocidade (`layouts/partial/topbar.tsx`) é largo: depois do selo de pausa vêm a data, o play e os cinco botões de velocidade (1×, 2×, 4×, 10× e 100×). Com a corrida pela meta, o governo, o Como jogar e o caixa na mesma linha, a topbar quebra. Com as Gestoras, governo, gestora e corrida ligados juntos passam a ser o caso comum, então a topbar é resolvida na 4.2, no mesmo desenho das Gestoras (F44). A referência é 1920 de largura, e em 1366 nada pode quebrar; o estado de teste é corrida, governo e gestora ligados, pausa com o motivo mais longo e o 100× destacado.

**Desenho aprovado em 14/nov** (board "Topbar recombinada" e os estados dela, no canvas). O que muda:

- a velocidade vira tracinhos com o número ao lado, um clique por tracinho, e a dica mostra a tecla (1 a 5); Espaço pausa e retoma, sem agir quando o foco está num campo de texto;
- o selo "Pausado" sai: a data ganha o fundo âmbar e o texto "Pausado · data", e o motivo da pausa fica na dica;
- o caixa vira o seletor de conta: "Caixa · Aurora Gestão ▾" abre a lista (carteira pessoal e gestoras), e com a gestora escolhida uma faixa verde-petróleo aparece sob a topbar; o botão "Operando" das Gestoras não existe;
- o selo "Carteira congelada" do presidente sai: o cadeado entra no rótulo do caixa e nas contas do menu, com a dica "Congelada até <data>".

**Meta e governo ficam como no app de hoje.** O board desenha os dois de forma aproximada, e o código segue os componentes reais (`topbar-goal.tsx`, `topbar-government.tsx`), sem mudar o estilo deles. O que o board não mostra e o app tem: a trilha da meta com 240 px de largura (o board usa 150) e um marcador por jogador ou equipe; a linha sob a meta com o reajuste pelo IPCA, o aviso "quase lá" e a "média da sua equipe"; o governo com presidente no cargo (emblema, nome, aprovação com a seta e a dica ao passar o mouse), que o board só desenha como a pílula "Governo do computador até a posse"; e o botão Como jogar.

**Plano.**

1. **Medir antes de mexer:** o bloco da direita com os componentes de hoje (meta com trilha de 240 px, governo com presidente, Como jogar, tempo e caixa) a 1366 e a 1920, com a velocidade em tracinhos e a pausa dobrada na data. Se a meta e o governo reais não couberem a 1366, o ponto de decisão é aberto e vai para o usuário: encolher a trilha (o board usa 150 px) ou compactar o governo, que o card já previa.
2. **Tempo:** os tracinhos no lugar do `ToggleGroup`, a data âmbar no lugar do selo, o motivo da pausa na dica e os atalhos Espaço e 1 a 5.
3. **Caixa:** o rótulo com o seletor de conta, o menu, a faixa verde-petróleo e o cadeado da carteira congelada (fica para quando a gestora existir, na F44; sem ela o rótulo é "Caixa" como hoje).
4. **Estados:** conferir com a receita do canvas (tudo ligado a 1920 e a 1366, pausado, dica do teclado, menu aberto, governando, cheque especial, nome longo, partida clássica sem expansões, carregando).

**Aceite:** a 1366 a topbar com corrida, governo e gestora ligados cabe numa linha, sem quebra; o 100× e a pausa com o motivo mais longo continuam legíveis; Espaço pausa e 1 a 5 trocam a velocidade, e digitar num campo não aciona nada.

<a id="f211"></a>
**F211 — Livro de ofertas e ordens abertas do detalhe do ativo.** Serve N15. O livro (`features/variable-income/components/order-book-card.tsx`) simula a profundidade de mercado a partir do candle do dia, e a ordem do jogador se perde no meio dele. O que o código faz hoje:
- **O livro vem do candle do dia corrente**, o pregão que o jogo acabou de avançar (`market_liquidity.py`: compra abaixo do preço típico `(máxima + mínima + fechamento) / 3`, venda acima, com a distribuição de volume do candle). Não é o candle do dia seguinte.
- **A ordem do jogador entra no livro com a data do dia em que foi enviada** (`operation.py:185`) e só executa quando o candle do dia seguinte injeta liquidez do outro lado; ela executa no preço dela (`matching_engine.py:197`).
- **O livro não vem ordenado por preço**: `order_book.py:93-107` devolve o heap na ordem interna e a tela não define ordenação inicial (`order-book-card.tsx:69`), por isso a ordem do jogador aparece no meio.

**Falta** desenhar, numa rodada no canvas em Opus com variantes e estados (como numa feature nova), a tela do livro. O desenho de 03/11 parte de: a ordem aberta do jogador numa faixa no topo com Cancelar à mão; o livro em duas colunas, Compra (maior preço no topo) e Venda (menor preço no topo), com a melhor compra e a melhor venda em destaque, ligadas à boleta; uma barra de quantidade; a coluna Situação sai (repetia "Aberta"); o balão "Tópico" some. O usuário gostou do rumo e pediu o refinamento pelo método completo. A rodada decide também o que o livro diz sobre si mesmo (que é a pressão ao redor do preço do candle de hoje) e se a ordenação por preço passa a vir do backend. Entra na 4.2, antes das Gestoras: a cota da gestora é negociada nesse livro, e cada linha leva a sigla e a cor de quem pôs a ordem (jogador ou bot), então o livro já é desenhado com essas linhas.

<a id="f249"></a>
**F249 — Núcleo do backend sem import de features.** `core/` importava de `features/` em `user_manager`, `room_preparation`, `dependencies` e `tunnel_manager`, o inverso do que a pasta promete.

O túnel foi para `features/tunnel/`, a preparação da sala para `features/government/` e as dependências do FastAPI, que só as rotas usam, para `routes/dependencies/`. A interface `RealtimeBroker` e os eventos de presença do jogador subiram para o core, e o `UserManager` publica pelo `RealtimeBrokerManager`. A resolução e a validação da estratégia dos bots foram para `features/strategy/bots.py`: `add_bot` e `update_bot` recebem o `BotConfig` pronto, que já leva o nome da estratégia.

**Aceite:** nenhum import de `backend.features` em tempo de execução no core; ficam o import só de anotação do `SimulationManager` e os prefixos de logger em `core/logger.py`, que são texto de configuração. `uv run pyright` e `uv run pytest -n 4` limpos.

<a id="f255"></a>
**F255 — Estatais.** O presidente funda estatais em três portes (medida votada, paga com dívida, 51% do governo e 49% no formador), comanda o controle de preço em degraus de 5 a 20% com teto de 1,5 ponto de inflação represada que volta ao soltar, escolhe a política de dividendos (Reinvestir, Normal, Espremer) e privatiza por oferta de 5 pregões com reserva e rateio; a importação marca a estatal histórica, e sem ordem a partida segue a história. O Fundo Soberano fica na F292, e a conferência da tela contra o canvas ficou pendente.

<a id="f287"></a>
**F287 — Slots dos jogadores do lobby no desenho anterior.** Serve N15 e N20. O redesenho do topo do lobby também refez o card de cada jogador (`lobby-player-list.tsx`): o nome ficou sozinho na primeira linha, a profissão e os papéis desceram para uma segunda linha, a presença e o partido preparado viraram uma terceira, e as vagas livres viraram uma faixa só ("N vagas livres · a sala aceita até 12"), com "Adicionar bot" numa faixa à parte. O usuário preferiu o desenho anterior e pediu a volta.

**O que voltou** (o estado do arquivo antes do commit "Redesenhado o topo do lobby e movida a profissão para a Minha preparação"): o nome com os badges ao lado na mesma linha (Host, Novo e profissão); embaixo, a presença do jogador ou a estratégia do bot; o partido preparado à direita do card ("candidato" ou "sem partido"); cada vaga livre como um card próprio, na altura do card de jogador, e "Adicionar bot" ocupando a primeira vaga.

**O que ficou:** o topo do lobby redesenhado e a escolha da profissão dentro da Minha preparação. Na linha do nome volta só o badge de profissão (leitura), sem o seletor.

**Onde o desenho mudou em relação ao anterior:** com 2 colunas de 264 px, o badge de profissão e o "Bot" deixavam o nome do bot cortado (6 de 11 nomes, com a sala cheia). O badge "Bot" saiu, porque o avatar de robô e a estratégia já dizem que é bot, e os cards ficaram em uma coluna só, na largura do card do próprio jogador: nenhum nome corta a 1366 e a 1920. O custo é a altura: o card Jogadores tem cerca de 1013 px em qualquer sala (as 12 posições ficam à vista), contra cerca de 680 px em 2 colunas. O card do bot não mostra mais "robô não prepara" (bot nunca tem partido, o lado direito fica vazio) e a estratégia trunca com a dica do nome inteiro.

**Conferência feita:** sala com 12 jogadores, bots com nomes e estratégias longas e o próprio jogador com partido de candidato, a 1366 e a 1920: nenhum texto sobreposto nem cortado, vaga e card de jogador com 66 px.

<a id="f288"></a>
**F288 — Badge de profissão legível no lobby e na Minha preparação.** Serve N15 e N20. Dois problemas vistos no lobby:

- **Contraste.** O `ProfessionBadge` (`frontend/shared/components/profession-badge.tsx`) usa a variante `secondary` do Badge (`bg-muted`, texto `secondary-foreground`, sem borda). Sobre o card do jogador (`bg-card`, e o do próprio jogador em `bg-info-soft`) o fundo do badge quase some e não se vê onde ele começa. Os badges "Bot" e "Novo" do mesmo card usam a mesma variante e sofrem igual.
- **Botão Minha preparação.** O botão do topo (`preparation-button.tsx`) mostra a profissão como texto solto ("CLT" cinza, sem ícone), quando o desenho aprovado no canvas tinha o badge com ícone, e antes do redesenho a profissão aparecia como badge no card do jogador.

**Plano:** a variante do badge de etiqueta ganha contraste no próprio design system (`badgeVariants.ts`): borda `border-input` e fundo que se destaca do card nos dois temas, seja ajustando a `secondary` (se todos os usos dela ganham com isso) ou criando uma variante nova de etiqueta usada pelo badge de profissão, pelo "Bot" e pelo "Novo". Sem `className` por cima da variante. O botão Minha preparação passa a renderizar o `ProfessionBadge` no lugar do texto.

**Aceite:** a borda ou o fundo do badge tem contraste de pelo menos 3:1 contra o fundo do card, no tema claro e no escuro, no card comum e no card do próprio jogador.

<a id="f289"></a>
**F289 — Cards de profissão com vantagens e desvantagens.** Serve N39 e N25. A aba Profissão da Minha preparação (`ProfessionCards` em `frontend/shared/components/profession-grid.tsx`) mostra, em cada card, o ícone, o nome, o "N× o salário" e um parágrafo (`feels` em `frontend/shared/lib/professions.ts`) que mistura demissão, reajuste e imposto. O usuário achou denso demais: ninguém lê prosa para escolher. Na escolha, o que importa é o que cada profissão ganha e o que ela perde.

**Proposta:** o parágrafo vira duas partes. **Vantagens** (✓) e **desvantagens** (✗) em lista curta respondem "vale a pena?". **Afetado por** responde "o que eu acompanho durante a partida": as variáveis que movem a renda (da economia ou do governo), como etiquetas curtas, sem dizer se é bom ou ruim. As etiquetas e as frases saem das regras da profissão (`ProfessionRule`: imposto, reajuste, PIB, auxílio, sorteio de demissão), e as listas moram em `PROFESSIONS` no lugar do `feels`, como fonte única do texto.

**Decidido em 13/11:**

- **Renda em R$ e em múltiplo:** cada card mostra o valor do mês com o salário que o host definiu ("R$ 6.000 por mês") e, embaixo, o "1,2× o salário". A nota de rodapé que explicava o "× o salário" sai.
- **Auxílio:** mostra o total, 0,9× (R$ 4.500), com a divisão "0,5× do bico + 0,4× do auxílio" embaixo.
- **Regras da sala:** o card mostra só o que vale na sala. Sem o Governo, saem as etiquetas e as vantagens que dependem dele (aumento dos servidores e dos aposentados, gasto com auxílio, impostos); sem a correção pela inflação, sai o aumento. Card sem nenhuma etiqueta diz "Nada que mude na partida".
- **Dica das etiquetas:** hovercard com o que a variável é e uma tabela curta do efeito em R$ (PIB do empreendedor, desemprego com a frequência do sorteio, imposto, gasto com auxílio, aumento do governo). Sem dica de texto corrido: etiqueta sem tabela fica só com o nome.
- **Locador:** passa a 1,1× o salário, no card próprio dele no roadmap; os cards já o mostram com R$ 5.500.

**Falta:** o usuário escolher no canvas a variante do card (A: três colunas com lista única; B: duas colunas com Ganha e Perde lado a lado; C: tabela comparativa) e revisar as frases de cada profissão.

<a id="f290"></a>
**F290 — Profissões novas.** Serve N23 e N34; condicionado por D19. As seis profissões de hoje (`backend/core/professions.py`, `frontend/shared/lib/professions.ts`) ligam a renda ao desemprego, ao PIB, ao reajuste do governo e a um dos três impostos. Cada profissão nova aposta numa variável que a partida já simula e que nenhuma das seis usa, para a escolha ser uma leitura da economia, e cada uma tem um preço. Os múltiplos abaixo são o ponto de partida; os números finais saem da calibragem.

- **Exportador:** a renda segue o dólar; ganha quando o real se desvaloriza e perde quando ele se valoriza. Imposto de empresa. Grupo dos empreendedores; o governo chega por câmbio e imposto de empresa.
- **Bancário:** a renda segue a Selic; ganha com juro alto e perde quando o Banco Central corta. Tem sorteio de demissão e imposto de renda. Grupo dos trabalhadores formais; o governo chega pela Selic.
- **Autônomo:** cerca de 1,4× o salário, sem reajuste nem correção pela inflação, então a inflação come a renda ao longo da partida; o sorteio de demissão vira "mês sem cliente", um mês sem renda. Imposto de renda. Grupo dos empreendedores.
- **Corretor:** a renda segue o Ibovespa dos últimos 12 meses. Imposto de renda. Grupo dos investidores.
- **Herdeiro:** sem renda nenhuma; começa com um patrimônio calibrado para empatar com o CLT aplicado no CDI na duração padrão da partida. É trocar a renda pelo capital de partida: ganha de quem investe mal e perde para quem investe bem o salário. Grupo dos investidores; o governo chega pela Selic, que decide quanto o patrimônio rende.
- **Recém-formado:** começa com patrimônio zero e cerca de 0,6× o salário, que sobe até cerca de 1,5× em 10 anos; o risco de demissão é maior no começo. Imposto de renda. Grupo dos trabalhadores formais.

Os bots recebem uma profissão sorteada entre todas, e o host pode fixá-la no slot do bot. Os cards usam o formato Ganha | Perde dos cards de profissão.

**Plano.**

1. **Calibragem pelo CLI:** cada profissão nova contra o CLT em várias bases e sorteios, ajustando os múltiplos e o patrimônio do Herdeiro.
2. **Backend:** os campos novos do `ProfessionRule` (renda que segue dólar, Selic ou bolsa; sem reajuste; patrimônio inicial; a curva de renda do Recém-formado; a demissão como mês sem cliente) e a profissão sorteada dos bots.
3. **Frontend:** os seis cards Ganha | Perde e o seletor de profissão no slot do bot.

**Aceite:** na calibragem, cada profissão nova termina acima do CLT em algum cenário e abaixo em outro; o Herdeiro que deixa tudo no CDI termina perto do CLT que investe o salário no CDI.

<a id="f291"></a>
**F291 — Locador com aluguel de 1,1× o salário.** Serve N39. Hoje o Locador (`backend/core/professions.py`) rende 1× o salário, paga o imposto de renda das pessoas e corre o sorteio de demissão como vacância, igual ao CLT, mas sem o aumento acima da inflação que o CLT ganha quando o PIB cresce. Ele sai igual ou pior que o CLT em tudo, e com as vantagens e desvantagens escritas no card da profissão isso fica à vista: ninguém escolhe o Locador.

**Decidido em 13/11:** o aluguel passa a 1,1× o salário (R$ 5.500 com salário de R$ 5.000), 10% mais que o CLT, e segue só com a inflação. A escolha vira uma troca: mais renda agora contra o CLT, que cresce. Com PIB de 2% ao ano o CLT ganha 1% ao ano acima da inflação e alcança o Locador em uns 10 anos de partida. Muda o `income_multiple` do Locador no backend e no `frontend/shared/lib/professions.ts`, e os testes de profissão que fixam o 1×.

<a id="f292"></a>
**F292 — Fundo Soberano: o governo compra ações e cotas.** Serve N34 e N41. O governo investe em empresas com uma carteira própria. A referência é o Fundo Soberano do Brasil (2008 a 2019): criado com dinheiro do Tesouro, comprou ações da Petrobras e do Banco do Brasil e foi extinto em 2019, com o saldo usado para pagar dívida.

**Regras.**

1. **É um destino do gasto público**, como o auxílio e as obras: o aporte é uma medida que passa pelo Congresso. A medida sempre existe, sem chave nas configurações do governo.
2. **O presidente escolhe as compras**, ativo por ativo, fora da fila do Congresso, porque o dinheiro já foi aprovado. Toda compra e toda venda sai no jornal.
3. **Como compra:** o presidente troca o caixa da topbar para o Fundo Soberano, como faz com uma gestora, e compra na Renda Variável de sempre, com gráfico, livro de ofertas e busca; uma faixa avisa que a ordem é do fundo. A compra passa pelo livro e mexe no preço, como a de qualquer jogador grande.
4. **O que o fundo compra:** ações importadas, inclusive as das estatais, e até 20% das cotas de cada gestora (F44). Comprar a gestora de um aliado, do partido do presidente ou da base, dá manchete de favorecimento e rejeição nos grupos do eleitorado.
5. **Sem impulso no PIB:** comprar ação na bolsa não constrói nada, o dinheiro só troca de mão. Venda e dividendos voltam ao Tesouro e abatem a dívida.
6. **A carteira do fundo** é uma carteira separada (F101). As telas estão desenhadas no canvas, na linha das Estatais (F255), com a compra pelo caixa da topbar.

**Plano.** A medida de aporte entre os gastos públicos; a carteira do governo; as ações de compra e venda do presidente; as manchetes de compra, de venda e de favorecimento; o teto de 20% por gestora; o retorno de venda e dividendos ao Tesouro.

**Riscos.** O presidente pode usar o fundo para inflar a cota de um aliado; o teto de 20%, a manchete e a rejeição são o preço. Comprar antes de uma medida que valoriza o ativo é informação privilegiada, aceita como nas estatais, porque o aporte passa pelo Congresso à vista de todos.

**Aceite:** sem aporte aprovado o fundo não compra nada; vender devolve o dinheiro ao Tesouro e abate a dívida; o fundo nunca passa de 20% das cotas de uma gestora; comprar ação não move o PIB.

<a id="f293"></a>
**F293 — Profissões das expansões.** Serve N23 e N34; condicionado por D19. Duas profissões que só aparecem com a expansão delas ligada, no formato Ganha | Perde dos cards de profissão. Os múltiplos são o ponto de partida; os números finais saem da calibragem.

- **Comissionado**, com Governo & Política: cerca de 1,5× o salário enquanto o partido escolhido na preparação, de um jogador ou do computador, ocupa a presidência ou está na base do governo, e cerca de 0,5× fora dela. A eleição decide a renda. Grupo dos servidores públicos.
- **Banqueiro de ofertas**, com Gestoras: cerca de 0,7× o salário mais 1% de toda oferta pública e emissão de cotas da sala (F102), descontado do valor captado pela gestora, como a comissão dos bancos nas ofertas reais. Ganha quando a sala abre capital. Grupo dos investidores.

**Plano.** A profissão com requisito de expansão, que só aparece com ela ligada; a escolha do partido na aba Profissão da preparação; a renda do Comissionado lida da presidência e da base a cada mês; a comissão do Banqueiro paga a cada oferta e emissão; os dois cards Ganha | Perde.

**Aceite:** com a expansão desligada a profissão não aparece; o Comissionado muda de renda no mês seguinte à troca de governo; uma oferta de R$ 100 mil paga R$ 1 mil ao Banqueiro.

<a id="f294"></a>
**F294 — Adicionar vários bots de uma vez.** Serve N8. O diálogo de adicionar bot (`frontend/features/lobby/components/lobby-bot-dialog.tsx`) ganhou o campo de quantidade, de 1 até as vagas livres da sala, e, com quantidade maior que 1, o item "Sortear para cada bot" na lista de estratégias. No lote, o nome sai da lista da estratégia e a cor, a profissão e o time são automáticos; cada bot continua editável no slot depois. Com quantidade 1 o diálogo é o de sempre. Os bots entram pela rota `POST /api/simulation/bots/batch`, sob um único lock: se faltar vaga ou algum nome se repetir, nenhum entra. O desenho é registrado no canvas depois de implementado.

<a id="f295"></a>
**F295 — Orçamento, painel econômico e base do governo por tempo real.** O orçamento do país (`useBudget`), o painel econômico (`useEconomyPanel`) e a base do governo (`features/government/hooks/queries/useBase.ts`) buscam os dados de novo a cada 10 s por `refetchInterval`. O resto do app atualiza por tempo real: o backend emite um evento pelo websocket quando o dado muda e o hook invalida a query.

**Aceite:** os três hooks sem `refetchInterval`; um evento do backend para cada dado, emitido quando ele muda (no tick ou na ação que o altera), e o hook invalidando a query ao receber. Molde: `useFixedIncomeAssets` com `fixed_assets_update`, e as páginas da gestora com `funds_update`. O painel de desempenho do modo debug segue buscando de tempo em tempo, porque mede o servidor.

<a id="f296"></a>
**F296 — Correções do playtest: gestoras e renda variável.**

Os sete itens do playtest saíram: Levar da carteira sem cotas de gestora, botão de oferta pública só antes da oferta, total vendido na oferta encerrada, menu e tela do presidente com Fundo Soberano, selo de estatal na lista, nome Mercado nas duas pontas do livro e filtros da renda variável em duas linhas a 1366 px.

<a id="f297"></a>
**F297 — Correções do playtest: governo e eleição.** Serve N34. Lote do playtest de 17/11. (1) Linha do tempo do segundo turno fora de ordem (04 jan, 02 jan, 09 jan, 2º turno) e marcadores de aliança entre os pontos errados: `map_timeline.py:141-226` monta os pontos sem ordenar e o front (`map-timeline.ts:14-34`) dispõe por índice, com o marcador na média dos vizinhos (`map-timeline-ruler.tsx:243-256`); os pontos saem ordenados por data. (2) Convidar vice dentro da partida inscreve a chapa e o convite não chega: `government_book.py:2024-2056` emite VICE_INVITED e deixa o vice pendente, mas a pendência do convidado não aparece; reproduzir no app de teste e corrigir. (3) "Prometido" mostra o valor prometido no hover do selo e no diálogo de mudar (`taxes-card.tsx:196-212`, `spending-card.tsx:151-155`, `measure-action.tsx`): o DTO passa a mandar o valor além do `promised: bool` (`dto/government.py:969, 996`). (4) O selo "Novo" das Estatais é fixo (`government.tsx:93-96`) e sai. (5) Privatizar não chegou ao Congresso: na partida, nenhuma medida de privatização foi registrada; o botão só aparece com `isPresident && company.can_command` (`state-companies-table.tsx:242-247`); reproduzir e corrigir o caminho até a medida. (6) O Fundo Soberano não teve nenhum aporte nem compra na partida (zero fluxos e zero eventos na conta 0); reproduzir o aporte e a compra e corrigir.

<a id="f298"></a>
**F298 — Correções do playtest: lobby, bots e profissões.** Serve N39 e N8. Lote do playtest de 17/11. (1) Adicionar 4 bots dá 422 "O nome do bot precisa ter de 1 a 20 caracteres, sem # nem /": esgotados os 3 nomes da estratégia, `bot-names.ts:12-15` gera "<nome> #N" e `user_manager.py:1211-1221` recusa o "#", derrubando o lote inteiro; o nome numerado passa a usar um formato aceito. (2) O diálogo de bots ganha duas abas, como a preparação: "Em lote" (quantidade e sorteio) e "Individual" (o diálogo de um bot, sem o campo de quantidade). (3) Fim de partida dessincronizado: um jogador viu derrota e o outro vitória até recarregar; o caminho é `simulation_ended` → invalidação das estatísticas → `/match-result`; reproduzir com dois navegadores e garantir que o resultado só aparece com o placar final. (4) Cards de profissão: o Herdeiro mostra o capital inicial (o valor que importa, já que o salário é zero) e um selo de "difícil"; as profissões das expansões levam o selo da expansão (`profession-cards.tsx`). (5) O Comissionado e o Banqueiro de ofertas não deixam selecionar (`profession-tab.tsx:47-56` exige o partido do Comissionado): reproduzir e corrigir. (6) A profissão escolhida não volta ao lobby depois de uma partida: na partida jogada, `simulation_players.profession` ficou nulo para todos, embora `users.settings` guardasse a profissão (`settings.py:103-116`, carga em `user_manager.py:199-206`).

<a id="f299"></a>
**F299 — Cota de gestora negociada na renda variável.** Serve N23. Do playtest de 17/11: quem abria a oferta pública não achava a cota em lugar nenhum, porque a lista da renda variável e o catálogo dos bots excluíam a classe FUND, e sem negócio o preço de ranking descolou do patrimônio por cota (330,20 contra 552,20). Feito: a cota listada (desde a abertura da oferta) entra na lista da renda variável com o selo de gestora; a gestora fechada fica fora. O detalhe do ativo serve a cota com livro, gráfico e análise técnica, mais os cards da gestora (patrimônio por cota, ágio e P/VP com dica, taxas, rendimentos, gestor e link), o card da oferta ou da sobra da emissão em aberto, e na boleta o ágio pago, a posição depois da ordem e o aviso de perder o controle com "Vender só N". O painel de compra e venda saiu da tela da gestora, que agora leva ao detalhe ("Comprar na oferta", "Vender cotas", "Negociar cotas"). Toda compra automática de cota tem teto de P/VP 1,2. Estratégia nova dos bots, "Cotas de gestoras", só nas salas com a expansão: dá à cota o patrimônio por cota mais um prêmio de 2× o desempenho sobre o CDI em 126 pregões (limitado a ±20%) e uma opinião do dia de ±5% por bot; compra abaixo desse valor, vende acima, e na oferta ou na sobra só compra no último pregão, se o preço fixo couber. O backtest lista as estratégias sem gestoras.

---

## 🚫 Descartado

> Nenhum item neste status.
