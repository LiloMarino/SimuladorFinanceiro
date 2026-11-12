<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/atualizar/concluir/descartar/remover um item, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban do projeto, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que ordem e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-11-11):** Definidos o plano e o aceite de sete cards que saíram da avaliação: corrida eleitoral com bots (F280), ministério para o partido da base (F284), laboratório da economia (F227), estatais (F255), muitos futuros (F28), cenários (F90) e rumores antecipados (F93).

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Tipo | Resumo | Marco | Condiciona (F#) | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **N1** | — | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — | — | — | — |
| **N2** | — | Jogar com amigos pela internet sem que cada um instale uma VPN | — | [F5](#f5), [F6](#f6) | — | — | — |
| **N3** | — | Confiar que os números do simulador são exatos e reprodutíveis | — | [F263](#f263), [F264](#f264) | — | — | — |
| **N4** | — | Testar uma estratégia de investimento automática e ver como ela se sai | — | [F110](#f110), [F111](#f111), [F197](#f197), [F279](#f279) | — | — | — |
| **N5** | — | Saber quanto risco foi corrido para chegar num resultado | — | — | — | — | — |
| **N6** | — | Comparar resultados de simulações diferentes | — | — | — | — | — |
| **N7** | — | Que o simulador cobre os custos de operar do mercado real | — | — | — | — | — |
| **N8** | — | Jogar contra oponentes controlados pelo computador | — | [F279](#f279), [F280](#f280) | — | — | — |
| **N9** | — | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | [F264](#f264) | — | — | — |
| **N10** | — | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | — | [F28](#f28), [F202](#f202) | — | — | — |
| **N11** | — | Que o cenário econômico simulado seja o histórico real | — | [F194](#f194), [F259](#f259) | — | — | — |
| **N12** | — | Continuar jogando depois do último dia com dado real | — | — | — | — | — |
| **N13** | — | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | [F266](#f266) | — | — | — |
| **N14** | — | Atualizar para uma versão nova sem perder as partidas salvas | — | [F56](#f56) | — | — | — |
| **N15** | — | Usar uma interface agradável e coerente, à altura de um jogo | — | [F37](#f37), [F72](#f72), [F123](#f123), [F179](#f179), [F211](#f211), [F250](#f250), [F252](#f252), [F265](#f265), [F266](#f266), [F267](#f267), [F268](#f268), [F269](#f269), [F270](#f270), [F272](#f272), [F282](#f282), [F283](#f283) | — | — | — |
| **N16** | — | Ver a carteira e o mercado por setor e segmento | — | — | — | — | — |
| **N17** | — | Enxergar a estrutura do banco e esboçar mudanças nela | — | — | — | — | — |
| **N18** | — | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — | — | — | — |
| **N19** | — | Analisar um ativo com as ferramentas de um trader | — | [F34](#f34), [F131](#f131), [F193](#f193) | — | — | — |
| **N20** | — | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | [F271](#f271), [F285](#f285) | — | — | — |
| **N21** | — | Jogar "na unha", sem a interface apontar a melhor escolha | — | — | — | — | — |
| **N22** | — | Ter objetivos para buscar além de vencer a partida | — | [F90](#f90), [F123](#f123), [F159](#f159), [F275](#f275) | — | — | — |
| **N23** | — | Jogar com os amigos de outras formas além de cada um por si | — | [F44](#f44), [F55](#f55), [F69](#f69), [F101](#f101), [F102](#f102), [F103](#f103), [F104](#f104), [F105](#f105), [F257](#f257), [F261](#f261), [F273](#f273), [F278](#f278) | — | — | — |
| **N24** | — | Saber onde está a lentidão durante uma partida | — | — | — | — | — |
| **N25** | — | Entender o que é o simulador e como se joga, sem ler um manual | — | [F132](#f132), [F133](#f133), [F139](#f139), [F140](#f140), [F141](#f141), [F158](#f158), [F193](#f193), [F225](#f225) | — | — | — |
| **N26** | — | Achar a causa de um erro sem vasculhar o log inteiro | — | — | — | — | — |
| **N27** | — | Entrar numa partida que já começou | — | — | — | — | — |
| **N28** | — | Liberar uma vaga sem depender de o jogador sair | — | — | — | — | — |
| **N29** | — | Saber o que cada jogador está fazendo enquanto a partida não começa | — | — | — | — | — |
| **N30** | — | Repetir uma configuração de partida sem montá-la de novo | — | — | — | — | — |
| **N31** | — | Saber o que está movendo o mercado da partida, como quem lê o noticiário | — | [F93](#f93), [F226](#f226), [F254](#f254), [F277](#f277) | — | — | — |
| **N32** | — | Saber como foi o mês sem montar a conta | — | — | — | — | — |
| **N33** | — | Investir com dinheiro emprestado, pagando o juro do momento | — | [F111](#f111) | — | — | — |
| **N34** | — | Disputar o poder de mudar as regras da economia da partida | — | [F176](#f176), [F194](#f194), [F226](#f226), [F227](#f227), [F232](#f232), [F250](#f250), [F251](#f251), [F253](#f253), [F254](#f254), [F255](#f255), [F256](#f256), [F257](#f257), [F258](#f258), [F259](#f259), [F260](#f260), [F261](#f261), [F262](#f262), [F263](#f263), [F265](#f265), [F268](#f268), [F269](#f269), [F273](#f273), [F274](#f274), [F275](#f275), [F276](#f276), [F280](#f280), [F281](#f281), [F284](#f284) | — | — | — |
| **N35** | — | Tirar da lista as partidas que não interessam mais | — | — | — | — | — |
| **N36** | — | Encontrar rapidamente os menores e maiores valores nos dados do jogo | — | — | — | — | — |
| **N37** | — | Comprar bitcoin do jeito que dá na vida real, em frações | — | — | — | — | — |
| **N38** | — | Saber quando as estatísticas vão mudar, sem achar que travaram | — | — | — | — | — |
| **N39** | — | Chegar ao primeiro dia da partida com as próprias escolhas já feitas | — | [F267](#f267) | — | — | — |
| **N40** | — | Jogar partidas longas e na velocidade máxima sem a tela travar | — | [F221](#f221) | — | — | — |
| **N41** | — | Aprender como a economia real funciona, jogando | — | [F225](#f225), [F226](#f226), [F227](#f227), [F253](#f253), [F255](#f255), [F260](#f260), [F276](#f276) | — | — | — |
| **N42** | — | Chegar a um estado da partida sem jogar até ele | — | [F286](#f286) | — | — | — |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | M27 · 4.5 | — | — | — | 🔍 |
| [**F6**](#f6) | Feature | Link de convite pela internet no lobby | M27 · 4.5 | — | Médio | Bom | ⏳ |
| [**F14**](#f14) | Feature | Janela desktop nativa | M27 · 4.5 | — | Baixo | Bom | ⏳ |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | M25 · 4.4 | — | Alto | Bom | ⏳ |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | M24 · 4.3 | — | — | — | 🔍 |
| [**F37**](#f37) | Feature | Tema escuro | M28 · 4.6 | — | Médio | Médio | ⏳ |
| [**F44**](#f44) | Feature | Expansão Gestoras: fundar a gestora e abrir capital | M18 · 4.2 | — | — | — | 🔍 |
| [**F55**](#f55) | Feature | Modo aquisição hostil | M18 · 4.2 | — | — | — | 🔍 |
| [**F56**](#f56) | Feature | Novidades no app | M27 · 4.5 | — | Baixo | Bom | ⏳ |
| [**F60**](#f60) | Feature | Modo servidor dedicado (--headless) | M27 · 4.5 | — | Baixo | Bom | ⏳ |
| [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | M24 · 4.3 | — | Médio | Bom | ⏳ |
| [**F81**](#f81) | Manutenção | CORS restrito à mesma origem | M27 · 4.5 | — | Baixo | Médio | ⏳ |
| [**F90**](#f90) | Feature | Cenários | M25 · 4.4 | — | Alto | Bom | ⏳ |
| [**F93**](#f93) | Feature | Rumores antecipados | M25 · 4.4 | — | Médio | Médio | ⏳ |
| [**F101**](#f101) | Feature | Carteira separada do jogador | M18 · 4.2 | — | Alto | Médio | ⏳ |
| [**F102**](#f102) | Feature | Gestoras: emissão de novas cotas e recompra | M18 · 4.2 | — | — | — | 🔍 |
| [**F103**](#f103) | Feature | Gestoras: troca de gestor pela assembleia | M18 · 4.2 | — | — | — | 🔍 |
| [**F104**](#f104) | Feature | Gestoras: co-gestores | M18 · 4.2 | — | — | — | 🔍 |
| [**F105**](#f105) | Feature | Gestoras: rendimentos mensais | M18 · 4.2 | — | — | — | 🔍 |
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
| [**F159**](#f159) | Feature | Conquista "Ordem com paciência" | M18 · 4.2 | — | Baixo | Bom | ⏳ |
| [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | M24 · 4.3 | — | Baixo | Bom | ⏳ |
| [**F176**](#f176) | Feature | Cadeiras do Congresso por região | — | — | Médio | Médio | 💤 |
| [**F179**](#f179) | Melhoria | Topbar que cabe com a corrida e o governo | M18 · 4.2 | — | — | — | 🔍 |
| [**F193**](#f193) | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | M28 · 4.6 | — | — | — | 🔍 |
| [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | M24 · 4.3 | — | Médio | Bom | ⏳ |
| [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | M25 · 4.4 | — | — | — | 🔍 |
| [**F211**](#f211) | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | M24 · 4.3 | — | — | — | 🔍 |
| [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | M24 · 4.3 | — | Médio | Bom | ⏳ |
| [**F225**](#f225) | Docs | Conceitos de economia real na docs e nomeados na tela | M28 · 4.6 | — | Alto | Bom | ⏳ |
| [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | M28 · 4.6 | — | Alto | Médio | ⏳ |
| [**F249**](#f249) | Manutenção | Núcleo do backend sem import de features | M18 · 4.2 | — | Alto | Médio | ⏳ |
| [**F255**](#f255) | Feature | Estatais | M18 · 4.2 | — | Alto | Médio | ⏳ |
| [**F267**](#f267) | Melhoria | Lobby com topo enxuto e profissão na preparação | M26 · 4.1 | — | — | — | 🔍 |
| [**F268**](#f268) | Melhoria | Tela do Mapa repensada | M26 · 4.1 | — | — | — | 🔍 |
| [**F269**](#f269) | Melhoria | Governo e Eleição com as ações do jogador num lugar só | M26 · 4.1 | — | — | — | 🔍 |
| [**F270**](#f270) | Melhoria | Cards permanentes da Renda fixa integrados à tela | M26 · 4.1 | — | — | — | 🔍 |
| [**F279**](#f279) | Feature | Estratégias automáticas novas e revisão das atuais | M26 · 4.1 | — | — | — | 🔍 |
| [**F284**](#f284) | Feature | Ministério para o partido da base | — | — | Alto | Médio | ⏳ |
| [**F285**](#f285) | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | — | — | — | — | 🔍 |
| [**F286**](#f286) | Feature | Comandos de trapaça no modo debug | — | — | Médio | Bom | ⏳ |

<details>
<summary><strong>Concluído / decidido / descartado (52 itens — clique pra expandir)</strong></summary>

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
| **D10** | — | Como a nota geral é calculada | — | [F264](#f264) | — | — | ✅ |
| **D11** | — | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | — | — | — | ✅ |
| **D12** | — | Como numerar as versões | — | — | — | — | ✅ |
| **D13** | — | Um canal de tempo real só: Socket.IO, com fallback de polling | — | — | — | — | ✅ |
| **D14** | — | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | — | — | — | — | ✅ |
| **D15** | — | Lint com oxlint, formatação com oxfmt e o TypeScript 7 com a API do 6 ao lado | — | — | — | — | ✅ |
| **D16** | — | Estratégias do app no host, personalização pela API | — | — | — | — | ✅ |
| **D17** | — | Os tópicos do tutorial se animam em código, com o motion | — | — | — | — | ✅ |
| **D18** | — | Uma migration por versão; caminho antigo só cai numa major | — | [F90](#f90), [F93](#f93) | — | — | ✅ |
| **D19** | — | O eleitorado são grupos, cada um com apoio e rejeição por partido | — | [F176](#f176), [F254](#f254), [F261](#f261) | — | — | ✅ |
| **D20** | — | A economia da partida é a história mais o desvio que o governo causa | — | [F194](#f194), [F226](#f226), [F227](#f227), [F232](#f232), [F253](#f253), [F255](#f255), [F256](#f256), [F257](#f257), [F263](#f263), [F281](#f281) | — | — | ✅ |
| **D21** | — | O jogo ensina a jogar, a docs explica o modelo | — | [F132](#f132), [F133](#f133), [F140](#f140), [F193](#f193), [F225](#f225), [F227](#f227) | — | — | ✅ |
| [**F69**](#f69) | Feature | Imprevistos configuráveis e tipos novos | M26 · 4.1 | — | — | — | ✅ |
| [**F194**](#f194) | Feature | Dólar e ativos internacionais | M26 · 4.1 | — | — | — | ✅ |
| [**F226**](#f226) | Feature | Mercado reage à surpresa: o Focus da partida | M26 · 4.1 | — | — | — | ✅ |
| [**F232**](#f232) | Correção | Crescimento que sente o rombo do governo | M26 · 4.1 | — | — | — | ✅ |
| [**F250**](#f250) | Correção | Correções da 4.1 | M26 · 4.1 | — | — | — | ✅ |
| [**F251**](#f251) | Melhoria | Mapa da eleição ao longo do tempo | M26 · 4.1 | — | — | — | ✅ |
| [**F252**](#f252) | Melhoria | Atalhos de valor no Tesouro e varredura de qualidade de vida | M26 · 4.1 | — | — | — | ✅ |
| [**F253**](#f253) | Melhoria | Impostos e cortes que fecham a conta do governo | M26 · 4.1 | — | — | — | ✅ |
| [**F254**](#f254) | Feature | Programas de governo com nome | M26 · 4.1 | — | — | — | ✅ |
| [**F256**](#f256) | Melhoria | SELIC abaixo de zero em futuro com deflação | M26 · 4.1 | — | — | — | ✅ |
| [**F257**](#f257) | Feature | Viver de renda que sente a economia | M26 · 4.1 | — | — | — | ✅ |
| [**F258**](#f258) | Melhoria | Orientação da bancada que se explica | M26 · 4.1 | — | — | — | ✅ |
| [**F259**](#f259) | Correção | Preço dos ativos cotados em dólar convertido para real | M26 · 4.1 | — | — | — | ✅ |
| [**F260**](#f260) | Feature | Caixa em dólar com o juro americano | M26 · 4.1 | — | — | — | ✅ |
| [**F261**](#f261) | Feature | Profissão no viver de renda | M26 · 4.1 | — | — | — | ✅ |
| [**F262**](#f262) | Feature | Pedido de impeachment aberto por jogador | M26 · 4.1 | — | — | — | ✅ |
| [**F263**](#f263) | Correção | Bolsa com piso e dividendo que acompanha o preço da partida | M26 · 4.1 | — | — | — | ✅ |
| [**F264**](#f264) | Correção | Nota de desempenho que não explode com patrimônio quase zero | M26 · 4.1 | — | — | — | ✅ |
| [**F265**](#f265) | Correção | Acabamentos do mapa, do Tesouro e dos cards da economia | M26 · 4.1 | — | — | — | ✅ |
| [**F266**](#f266) | Melhoria | Central de dados redesenhada | M26 · 4.1 | — | — | — | ✅ |
| [**F271**](#f271) | Melhoria | Paleta de 20 cores para os partidos, sala de 12 jogadores e um seletor de cor único | M26 · 4.1 | — | — | — | ✅ |
| [**F272**](#f272) | Melhoria | Seletores e combobox novos | M26 · 4.1 | — | — | — | ✅ |
| [**F273**](#f273) | Melhoria | Convites que se escolhem e se acumulam | M26 · 4.1 | — | — | — | ✅ |
| [**F274**](#f274) | Feature | Presidência e base do governo que valem a pena | M26 · 4.1 | — | — | — | ✅ |
| [**F275**](#f275) | Feature | Vitória política separada do capital | M26 · 4.1 | — | — | — | ✅ |
| [**F276**](#f276) | Correção | Governo ruim perde aprovação | M26 · 4.1 | — | — | — | ✅ |
| [**F277**](#f277) | Melhoria | Jornal com eventos raros em destaque e manchetes variadas | M26 · 4.1 | — | — | — | ✅ |
| [**F278**](#f278) | Feature | Imprevistos e eventos de vida mais variados | M26 · 4.1 | — | — | — | ✅ |
| [**F280**](#f280) | Melhoria | Corrida eleitoral com bots sempre presentes e campanha que pesa | M26 · 4.1 | — | — | — | ✅ |
| [**F281**](#f281) | Correção | Banco Central autônomo que decide em reunião, em passos de 0,25, olhando através do imposto | M26 · 4.1 | — | — | — | ✅ |
| [**F282**](#f282) | Correção | Texto dos gráficos com no mínimo 12 px | M26 · 4.1 | — | — | — | ✅ |
| [**F283**](#f283) | Melhoria | Campos de valor com o mesmo controle de R$ e de porcentagem | M26 · 4.1 | — | — | — | ✅ |

</details>

---

## 🚀 Próximas versões

> O que entra em cada versão, na ordem de trabalho. Item arquivado conta como concluído.

### 4.1 — Economia: governo, Focus e dólar (M26)

> **Objetivo:** O governo ganha impostos de verdade, cortes com preço e programas com nome; o crescimento sente o rombo; o mapa da eleição percorre o tempo; o viver de renda sente a economia, ganha imprevistos novos e a profissão de cada jogador; a economia traz o Focus e o dólar reage, com os ativos de fora cotados em real, protegendo a carteira, e o caixa em dólar rendendo o juro americano. Abre com os consertos e os atalhos que o playtest de 08/11 pediu.
>
> **Serve:** N15, N34, N23, N11, N31, N41
>
> **Progresso:** 32/37 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F250**](#f250) | Correção | Correções da 4.1 | — | ✅ Concluído |
| 2 | [**F252**](#f252) | Melhoria | Atalhos de valor no Tesouro e varredura de qualidade de vida | — | ✅ Concluído |
| 3 | [**F253**](#f253) | Melhoria | Impostos e cortes que fecham a conta do governo | — | ✅ Concluído |
| 4 | [**F232**](#f232) | Correção | Crescimento que sente o rombo do governo | — | ✅ Concluído |
| 5 | [**F254**](#f254) | Feature | Programas de governo com nome | — | ✅ Concluído |
| 6 | [**F256**](#f256) | Melhoria | SELIC abaixo de zero em futuro com deflação | — | ✅ Concluído |
| 7 | [**F251**](#f251) | Melhoria | Mapa da eleição ao longo do tempo | — | ✅ Concluído |
| 8 | [**F69**](#f69) | Feature | Imprevistos configuráveis e tipos novos | — | ✅ Concluído |
| 9 | [**F257**](#f257) | Feature | Viver de renda que sente a economia | — | ✅ Concluído |
| 10 | [**F226**](#f226) | Feature | Mercado reage à surpresa: o Focus da partida | — | ✅ Concluído |
| 11 | [**F259**](#f259) | Correção | Preço dos ativos cotados em dólar convertido para real | — | ✅ Concluído |
| 12 | [**F194**](#f194) | Feature | Dólar e ativos internacionais | — | ✅ Concluído |
| 13 | [**F260**](#f260) | Feature | Caixa em dólar com o juro americano | — | ✅ Concluído |
| 14 | [**F261**](#f261) | Feature | Profissão no viver de renda | — | ✅ Concluído |
| 15 | [**F258**](#f258) | Melhoria | Orientação da bancada que se explica | — | ✅ Concluído |
| 16 | [**F262**](#f262) | Feature | Pedido de impeachment aberto por jogador | — | ✅ Concluído |
| 17 | [**F263**](#f263) | Correção | Bolsa com piso e dividendo que acompanha o preço da partida | — | ✅ Concluído |
| 18 | [**F264**](#f264) | Correção | Nota de desempenho que não explode com patrimônio quase zero | — | ✅ Concluído |
| 19 | [**F265**](#f265) | Correção | Acabamentos do mapa, do Tesouro e dos cards da economia | — | ✅ Concluído |
| 20 | [**F266**](#f266) | Melhoria | Central de dados redesenhada | — | ✅ Concluído |
| 21 | [**F267**](#f267) | Melhoria | Lobby com topo enxuto e profissão na preparação | — | 🔍 Em avaliação |
| 22 | [**F268**](#f268) | Melhoria | Tela do Mapa repensada | — | 🔍 Em avaliação |
| 23 | [**F269**](#f269) | Melhoria | Governo e Eleição com as ações do jogador num lugar só | — | 🔍 Em avaliação |
| 24 | [**F270**](#f270) | Melhoria | Cards permanentes da Renda fixa integrados à tela | — | 🔍 Em avaliação |
| 25 | [**F271**](#f271) | Melhoria | Paleta de 20 cores para os partidos, sala de 12 jogadores e um seletor de cor único | — | ✅ Concluído |
| 26 | [**F272**](#f272) | Melhoria | Seletores e combobox novos | — | ✅ Concluído |
| 27 | [**F273**](#f273) | Melhoria | Convites que se escolhem e se acumulam | — | ✅ Concluído |
| 28 | [**F274**](#f274) | Feature | Presidência e base do governo que valem a pena | — | ✅ Concluído |
| 29 | [**F275**](#f275) | Feature | Vitória política separada do capital | — | ✅ Concluído |
| 30 | [**F276**](#f276) | Correção | Governo ruim perde aprovação | — | ✅ Concluído |
| 31 | [**F277**](#f277) | Melhoria | Jornal com eventos raros em destaque e manchetes variadas | — | ✅ Concluído |
| 32 | [**F278**](#f278) | Feature | Imprevistos e eventos de vida mais variados | — | ✅ Concluído |
| 33 | [**F279**](#f279) | Feature | Estratégias automáticas novas e revisão das atuais | — | 🔍 Em avaliação |
| 34 | [**F280**](#f280) | Melhoria | Corrida eleitoral com bots sempre presentes e campanha que pesa | — | ✅ Concluído |
| 35 | [**F281**](#f281) | Correção | Banco Central autônomo que decide em reunião, em passos de 0,25, olhando através do imposto | — | ✅ Concluído |
| 36 | [**F282**](#f282) | Correção | Texto dos gráficos com no mínimo 12 px | — | ✅ Concluído |
| 37 | [**F283**](#f283) | Melhoria | Campos de valor com o mesmo controle de R$ e de porcentagem | — | ✅ Concluído |

### 4.2 — Expansão Gestoras (M18)

> **Objetivo:** Fundar a própria gestora, abrir capital e disputar as cotas na sala; o governo também funda, segura o preço e privatiza estatais com a mesma base.
>
> **Serve:** N23, N34, N41
>
> **Progresso:** 0/11 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F249**](#f249) | Manutenção | Núcleo do backend sem import de features | — | ⏳ Pendente |
| 2 | [**F101**](#f101) | Feature | Carteira separada do jogador | — | ⏳ Pendente |
| 3 | [**F44**](#f44) | Feature | Expansão Gestoras: fundar a gestora e abrir capital | [F101](#f101) | 🔍 Em avaliação |
| 4 | [**F102**](#f102) | Feature | Gestoras: emissão de novas cotas e recompra | [F44](#f44) | 🔍 Em avaliação |
| 5 | [**F103**](#f103) | Feature | Gestoras: troca de gestor pela assembleia | [F44](#f44) | 🔍 Em avaliação |
| 6 | [**F55**](#f55) | Feature | Modo aquisição hostil | [F103](#f103) | 🔍 Em avaliação |
| 7 | [**F104**](#f104) | Feature | Gestoras: co-gestores | [F44](#f44) | 🔍 Em avaliação |
| 8 | [**F105**](#f105) | Feature | Gestoras: rendimentos mensais | [F44](#f44) | 🔍 Em avaliação |
| 9 | [**F255**](#f255) | Feature | Estatais | [F44](#f44) | ⏳ Pendente |
| 10 | [**F179**](#f179) | Melhoria | Topbar que cabe com a corrida e o governo | [F44](#f44) | 🔍 Em avaliação |
| 11 | [**F159**](#f159) | Feature | Conquista "Ordem com paciência" | [F44](#f44) | ⏳ Pendente |

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
| 3 | [**F211**](#f211) | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | — | 🔍 Em avaliação |
| 4 | [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | — | ⏳ Pendente |
| 5 | [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | — | ⏳ Pendente |
| 6 | [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | — | ⏳ Pendente |

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
> **Progresso:** 0/12 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | — | 🔍 Em avaliação |
| 2 | [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | — | ⏳ Pendente |
| 3 | [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | — | ⏳ Pendente |
| 4 | [**F131**](#f131) | Feature | Catálogo de padrões de vela | — | 🔍 Em avaliação |
| 5 | [**F193**](#f193) | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | [F158](#f158) | 🔍 Em avaliação |
| 6 | [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | — | 🔍 Em avaliação |
| 7 | [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | — | ⏳ Pendente |
| 8 | [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | [F44](#f44) | ⏳ Pendente |
| 9 | [**F225**](#f225) | Docs | Conceitos de economia real na docs e nomeados na tela | [F140](#f140) | ⏳ Pendente |
| 10 | [**F37**](#f37) | Feature | Tema escuro | — | ⏳ Pendente |
| 11 | [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | [F44](#f44) | ⏳ Pendente |
| 12 | [**F141**](#f141) | Docs | README com as features de hoje | [F139](#f139) | ⏳ Pendente |

### Sem versão

> Os itens ⏳ e 🔍 que ainda não entraram em nenhuma versão, do que mais destrava trabalho para o que menos ("Destrava" é quantos itens em aberto esperam por aquele). É daqui que sai a próxima versão; os 💤 ficam só no kanban.

| ID | Tipo | Resumo | Serve | Depende de | Destrava | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [**F284**](#f284) | Feature | Ministério para o partido da base | N34 | — | 0 | ⏳ Pendente |
| [**F285**](#f285) | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | N20 | [F271](#f271) | 0 | 🔍 Em avaliação |
| [**F286**](#f286) | Feature | Comandos de trapaça no modo debug | N42 | [F54](#f54) | 0 | ⏳ Pendente |

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: os itens que podem ser pegos agora, com toda dependência já ✅. A ordem segue o plano: primeiro os itens de cada versão (ou marco) na ordem dele, depois o resto pelo "Destrava", que é quantos itens em aberto esperam por aquele, direta ou indiretamente. 💤 (sem prioridade) e 🚫 não entram.

| ID | Tipo | Resumo | Marco | Destrava | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [**F267**](#f267) | Melhoria | Lobby com topo enxuto e profissão na preparação | M26 · 4.1 · 21º | 0 | — | — | 🔍 |
| [**F268**](#f268) | Melhoria | Tela do Mapa repensada | M26 · 4.1 · 22º | 0 | — | — | 🔍 |
| [**F269**](#f269) | Melhoria | Governo e Eleição com as ações do jogador num lugar só | M26 · 4.1 · 23º | 0 | — | — | 🔍 |
| [**F270**](#f270) | Melhoria | Cards permanentes da Renda fixa integrados à tela | M26 · 4.1 · 24º | 0 | — | — | 🔍 |
| [**F279**](#f279) | Feature | Estratégias automáticas novas e revisão das atuais | M26 · 4.1 · 33º | 0 | — | — | 🔍 |
| [**F249**](#f249) | Manutenção | Núcleo do backend sem import de features | M18 · 4.2 · 1º | 0 | Alto | Médio | ⏳ |
| [**F101**](#f101) | Feature | Carteira separada do jogador | M18 · 4.2 · 2º | 13 | Alto | Médio | ⏳ |
| [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | M24 · 4.3 · 1º | 0 | Médio | Bom | ⏳ |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | M24 · 4.3 · 2º | 0 | — | — | 🔍 |
| [**F211**](#f211) | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | M24 · 4.3 · 3º | 0 | — | — | 🔍 |
| [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | M24 · 4.3 · 4º | 0 | Médio | Bom | ⏳ |
| [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | M24 · 4.3 · 5º | 0 | Baixo | Bom | ⏳ |
| [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | M24 · 4.3 · 6º | 0 | Médio | Bom | ⏳ |
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
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | M28 · 4.6 · 6º | 0 | — | — | 🔍 |
| [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | M28 · 4.6 · 7º | 0 | Alto | Médio | ⏳ |
| [**F37**](#f37) | Feature | Tema escuro | M28 · 4.6 · 10º | 0 | Médio | Médio | ⏳ |
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
| **F101** | Feature | Carteira separada do jogador | N23 | D9 | M18 · 4.2 | — | Alto | Alto | Médio | Médio |
| **F110** | Feature | Combinar estratégias | N4 | D8 | M25 · 4.4 | — | Médio | Médio | Médio | Bom |
| **F111** | Feature | Crédito para estratégias e bots | N4, N33 | D8 | M25 · 4.4 | — | Baixo | Baixo | Médio | Bom |
| **F132** | Feature | Tópicos de "como se joga" do Como jogar | N25 | D21 | M28 · 4.6 | — | Médio | Baixo | Alto | Bom |
| **F133** | Feature | Tópicos de conceitos do Como jogar | N25 | D21 | M28 · 4.6 | — | Baixo | Baixo | Médio | Bom |
| **F139** | Docs | Demonstração regravada com o jogo de hoje | N25 | — | M28 · 4.6 | [F44](#f44) | Médio | Baixo | Alto | Bom |
| **F140** | Docs | Docs reorganizada por tipo de leitor | N25 | D21 | M28 · 4.6 | [F44](#f44) | Alto | Baixo | Alto | Bom |
| **F141** | Docs | README com as features de hoje | N25 | — | M28 · 4.6 | [F139](#f139) | Baixo | Baixo | Alto | Excelente |
| **F159** | Feature | Conquista "Ordem com paciência" | N22 | D1 | M18 · 4.2 | [F44](#f44) | Baixo | Baixo | Baixo | Bom |
| **F167** | Feature | Notícias do ativo como marcadores no gráfico de preço | — | — | M24 · 4.3 | — | Baixo | Baixo | Médio | Bom |
| **F197** | Melhoria | Rebalanceamento por meta com várias classes | N4 | — | M24 · 4.3 | — | Médio | Médio | Médio | Bom |
| **F221** | Performance | Lista de ações que aguenta muitas ações | N40 | — | M24 · 4.3 | — | Médio | Médio | Médio | Bom |
| **F225** | Docs | Conceitos de economia real na docs e nomeados na tela | N41, N25 | D21 | M28 · 4.6 | [F140](#f140) | Alto | Baixo | Alto | Bom |
| **F227** | Feature | Intensidade das ligações e laboratório da economia | N41, N34 | D20, D21 | M28 · 4.6 | — | Alto | Médio | Médio | Médio |
| **F249** | Manutenção | Núcleo do backend sem import de features | — | — | M18 · 4.2 | — | Alto | Médio | Médio | Médio |
| **F255** | Feature | Estatais | N34, N41 | D20 | M18 · 4.2 | [F44](#f44) | Alto | Alto | Alto | Médio |
| **F284** | Feature | Ministério para o partido da base | N34 | — | — | — | Alto | Médio | Médio | Médio |
| **F286** | Feature | Comandos de trapaça no modo debug | N42 | — | — | [F54](#f54) | Médio | Baixo | Alto | Bom |

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

<a id="f101"></a>
**F101 — Carteira separada do jogador.** Serve N23; segue a D9. A base da expansão Gestoras (F44): hoje eventos e snapshots pertencem ao jogador (`user_id`), e a gestora precisa de carteira própria. Entra uma tabela `portfolios`, e eventos e snapshots passam a apontar para a carteira; a carteira pessoal de cada jogador é migrada uma a uma, inclusive nas partidas salvas. Nada muda na tela: cada jogador segue com uma carteira só até a F44 existir. Gatilho: a F44 sair da avaliação.

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

<a id="f159"></a>
**F159 — Conquista "Ordem com paciência".** Serve N22; segue a D1. A 9ª conquista da leva de novas conquistas ficou de fora porque o evento de ordem de ações (`event_equity`) não guarda o tipo da ordem que gerou a execução. Plano: coluna `order_type` em `event_equity` (mercado ou limitada), por migration, com as linhas antigas como mercado; o `Broker` grava o tipo na execução; uma `@metric` em `metrics.py` conta as execuções de ordem limitada do jogador, e a conquista entra no `catalog.py`. Vale qualquer ordem limitada executada, inclusive a que executa na hora porque o preço já estava bom. Fica para a rodada de conquistas feita com o usuário depois da Gestoras, junto com a docs, quando dá para ver todas as features que pedem conquista.

<a id="f167"></a>
**F167 — Notícias do ativo como marcadores no gráfico de preço.** Serve N31. As manchetes de empresas do noticiário (F92) aparecem também na tela do ativo, como marcadores no gráfico de preço, com a manchete ao passar o mouse. Separada da F92 em 29/out: o noticiário sai na 3.1 só com as manchetes, e os marcadores pedem desenho no canvas antes do código. Gatilho: F92 concluída.

<a id="f197"></a>
**F197 — Rebalanceamento por meta com várias classes.** Serve N4. Hoje o `TargetRebalance` (`backend/features/strategy/rebalance.py:55`) divide só entre um ativo de ações (BOVA11 por padrão) e a renda fixa de liquidez diária: a meta em ações vai de 10% a 90% (padrão 60%), e o desvio máximo, de 1 a 20 pontos (padrão 5). O playtest de 31/out pediu configurar a meta de cada classe.

**O que muda:** os parâmetros viram uma lista de alvos (um ativo ou uma classe e a porcentagem), que soma 100%, com a faixa de desvio de cada alvo; a estratégia vende o que passou da faixa antes de comprar o que ficou abaixo, como hoje. O formulário da estratégia mostra a lista com o total e recusa o que não soma 100%. O padrão continua 60% em BOVA11 e 40% em renda fixa com 5 pontos, então partidas salvas e backtests antigos dão o mesmo resultado; um teste compara os dois. Os parâmetros salvos no perfil (F170) passam a guardar a lista.

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

<a id="f249"></a>
**F249 — Núcleo do backend sem import de features.** `core/` importa de `features/` em `user_manager`, `room_preparation`, `dependencies` e `tunnel_manager`, o inverso do que a pasta promete.

Cada um desses módulos é movido para a feature que o consome ou passa a receber a dependência por injeção (o `core` define o protocolo, a feature implementa). Por fora nada muda; confere-se com `uv run pyright`, `uv run pytest -n 4` e um `grep "features" backend/core` vazio. Sem decisão de fazer agora.

<a id="f255"></a>
**F255 — Estatais.** Serve N34 e N41; condicionado por D20. Só se implementa depois da expansão Gestoras (F44). A ideia do playtest de 08/11: o governo cria estatais (empresas controladas pelo governo, com ações na bolsa) para gerar receita e PIB. No Brasil, as estatais listadas (Petrobras, Banco do Brasil) pagam dividendos ao Tesouro (dividendo é a parte do lucro que a empresa paga aos acionistas), e os proventos já existem na partida desde a 4.0. Entram quatro medidas, cada uma com o seu preço: fundar, usar o controle, privatizar e a política de dividendos.

**Por que depois das Gestoras.** A estatal é um ativo que os jogadores negociam, e fundar e privatizar reaproveitam o que a expansão Gestoras (F44) constrói: um ativo que nasce no meio da partida, com o preço feito por um formador de mercado sintético (um participante automático que sempre põe ordens de compra e venda em volta do valor justo), e a oferta pública, que é a privatização. Os dividendos ao Tesouro seguem o molde dos rendimentos da gestora (F105). O uso do controle age também nas estatais que já estão entre os ativos importados, como camada sobre o preço histórico, no molde do dólar sobre os ativos de fora (F194).

**Plano.**

1. **Capital.** A estatal fundada nasce listada, com 51% do governo (o controle, como na Petrobras e no Banco do Brasil) e 49% na bolsa. São dois estados: estatal ou privada. Privatizar vende os 51% de uma vez. Os 49% são absorvidos pelo formador de mercado sintético das Gestoras, e o governo arrecada pelo valor justo (o valor que a empresa tem pelo que rende) independentemente de haver gente comprando na sala. Exemplo: uma estatal de R$ 100 bi custa R$ 51 bi de dívida, a fatia que o governo mantém.
2. **Estatais importadas.** Quem monta a base marca, na importação, quais códigos são estatais; não há lista fixa no código. A tela de importação sugere a marca para os códigos conhecidos da União (PETR3, PETR4, BBAS3). A marcação traz a fatia do governo e o número de ações, necessários para transformar o dividendo por ação em reais. Nas importadas valem o uso do controle e a política de dividendos; fundar e privatizar são só das estatais criadas na partida.
3. **Usar o controle** (o antigo "segurar preço"). O governo manda a estatal vender abaixo do preço que o mercado pagaria. O efeito na economia depende do setor do ativo, que define a alavanca (o que o governo consegue mexer na economia pela estatal): combustíveis e energia elétrica baixam o IPCA (a gasolina pesa uns 5% do índice, então 10% de desconto nela tira cerca de 0,5 ponto da inflação; a conta de luz pesa uns 4%); banco baixa o juro do crédito e sobe o PIB, e a inflação sobe um pouco; os outros setores não têm alavanca, só o dividendo. O custo é sempre o mesmo: lucro menor, dividendo menor ao Tesouro e ação em queda. Casos reais: Petrobras de 2011 a 2014, Eletrobras em 2012, BB e Caixa em 2012. Fundar pede escolher o setor (combustíveis, energia ou banco), que define a alavanca.
4. **Inflação represada.** Ao soltar o preço, o que foi segurado volta ao IPCA nos meses seguintes, como em 2015 (a inflação represada é a que foi adiada, não a que sumiu). Sem essa volta, segurar preço evitaria para sempre a perda de credibilidade do Banco Central. Há um teto para a soma das alavancas de IPCA, que sai da calibragem. A alavanca do banco é pequena, para não virar um segundo botão de juro além da SELIC.
5. **Política de dividendos** (medida nova, em fundadas e importadas). O governo manda a estatal distribuir mais agora, o que rende receita extra, ao custo de ela investir menos, o que dá menos PIB e uma ação mais fraca depois. Exemplo: mandar distribuir 80% do lucro em vez de 50% enche o caixa do Tesouro este ano e deixa a estatal com menos para investir. É o jeito de a importada arrecadar mais, porque pela D20 o dividendo normal dela já está na história e não é desvio.
6. **Receita.** Os dividendos vão ao Tesouro na proporção da fatia do governo, sobre o lucro da estatal: com fatia de 51%, uma estatal que distribui R$ 10 bi manda R$ 5,1 bi ao Tesouro. A fundada tem valor justo com retorno sorteado por ano em volta de uma média, e pode valer menos que o investido.
7. **PIB.** Na fundação vem um impulso, pela ligação de ciclo fiscal que já existe; depois vem uma parcela permanente, proporcional ao tamanho (valor) da estatal enquanto ela opera: cresce se ela reinveste e encolhe se o governo a espreme. Cada estatal nova no mesmo setor soma menos. É a sétima ligação da economia e ganha chave no laboratório (F227).

O tamanho dos efeitos sai da calibragem pelo CLI.

**Riscos.**

- **Máquina de dinheiro.** Se o retorno médio da estatal fundada fica acima do juro da história, fundar vira dinheiro de graça (a dívida custa o juro e a estatal rende mais que ele). A média do retorno fica perto ou abaixo do juro real da história (o juro descontada a inflação).
- **Ciclo fundar e privatizar.** Fundar e vender em sequência não pode render de graça; a calibragem confere isso.
- **Informação privilegiada.** Colegas de partido sabem antes que uma medida vem e podem comprar ou vender a ação. É aceito porque a medida passa pela fila do Congresso, à vista de todos.

**Aceite:** sem medida de estatal a partida segue a história; a calibragem compara "fundar 10 estatais em 10 anos" com "não fundar nenhuma" e fundar não domina; segurar o preço e soltar devolve a inflação represada; banco estatal não baixa o IPCA; a soma das alavancas respeita o teto; dividendo extra hoje reduz PIB e valor depois.

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

---

## 🔍 Em avaliação

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Falta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **F5** | Spike | Spike: provider de túnel pela internet | N2 | — | M27 · 4.5 | — | Escolhe o provider da F6 |
| **F34** | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | N19 | — | M24 · 4.3 | — | Escolhe a biblioteca de gráfico |
| **F44** | Feature | Expansão Gestoras: fundar a gestora e abrir capital | N23 | — | M18 · 4.2 | [F101](#f101) | O protótipo do preço da cota com o formador sintético |
| **F55** | Feature | Modo aquisição hostil | N23 | — | M18 · 4.2 | [F103](#f103) | Parte mínima no mercado e o destino do incorporado |
| **F102** | Feature | Gestoras: emissão de novas cotas e recompra | N23 | — | M18 · 4.2 | [F44](#f44) | O prazo da preferência e o preço da emissão |
| **F103** | Feature | Gestoras: troca de gestor pela assembleia | N23 | — | M18 · 4.2 | [F44](#f44) | Como a assembleia escolhe o novo gestor |
| **F104** | Feature | Gestoras: co-gestores | N23 | — | M18 · 4.2 | [F44](#f44) | A divisão das taxas |
| **F105** | Feature | Gestoras: rendimentos mensais | N23 | — | M18 · 4.2 | [F44](#f44) | A parte do lucro distribuída |
| **F123** | Melhoria | Redesenhar o aviso de conquista desbloqueada | N22, N15 | — | M28 · 4.6 | — | Escolher o desenho do aviso no canvas; liga à F122 |
| **F131** | Feature | Catálogo de padrões de vela | N19 | — | M28 · 4.6 | — | Tópico do Como jogar com cada padrão animado |
| **F158** | Melhoria | Animações do Como jogar revistas | N25 | — | M28 · 4.6 | — | O visual numa rodada no canvas dedicada: animações atuais contra as primeiras, número do passo fora da cena, cursor e destaque, e o palco em tamanho real mostrando só o trecho do passo |
| **F179** | Melhoria | Topbar que cabe com a corrida e o governo | N15 | — | M18 · 4.2 | [F44](#f44) | Escolher a variante entre as do canvas, já com o layout das Gestoras |
| **F193** | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | N25, N19 | D21 | M28 · 4.6 | [F158](#f158) | O molde do tópico em fases, quais indicadores entram primeiro e onde o 'i' abre o tópico sem cobrir a tela (F183). |
| **F202** | Performance | Backtest que corre mais rápido que a partida comum | N10 | D8 | M25 · 4.4 | — | Medir o dia do backtest por etapa e escolher quais custos saem do caminho dele (eventos em memória gravados em lote, leituras do que o motor acabou de gravar, trava por pregão, imposto por dia) |
| **F211** | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | N15 | — | M24 · 4.3 | — | o desenho do livro (variantes e estados no canvas) e se a ordenação por preço vem do backend |
| **F267** | Melhoria | Lobby com topo enxuto e profissão na preparação | N15, N39 | — | M26 · 4.1 | — | Desenho no canvas: o topo do lobby, o card do jogador sem o seletor de profissão e a aba de profissão no Minha preparação. |
| **F268** | Melhoria | Tela do Mapa repensada | N34, N15 | — | M26 · 4.1 | — | Desenho no canvas: onde mora a lista de lugares, como o Ver mais expande sem rolagem horizontal e a coluna das lentes. |
| **F269** | Melhoria | Governo e Eleição com as ações do jogador num lugar só | N34, N15 | — | M26 · 4.1 | — | Análise de UX das duas páginas e das abas; depois o desenho no canvas de onde fica cada ação do presidente e do candidato. |
| **F270** | Melhoria | Cards permanentes da Renda fixa integrados à tela | N15 | — | M26 · 4.1 | — | Desenho no canvas: cor, layout e posição dos dois cards fixos. |
| **F279** | Feature | Estratégias automáticas novas e revisão das atuais | N4, N8 | — | M26 · 4.1 | — | Medir as estratégias atuais em partidas com governo, dólar e crédito; escolher as estratégias novas. |
| **F285** | Feature | Modo daltonismo: limitar as cores às que um daltônico distingue | N20 | — | — | [F271](#f271) | Escolher o mecanismo (filtrar o seletor, recolorir na tela de quem liga ou reforçar além da cor) e medir o tamanho do conjunto distinguível sob as três simulações |

<a id="f5"></a>
**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO; se não passar, se ao menos o polling atravessa (o SSE saiu na D13, então o polling é o único fallback). O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

<a id="f34"></a>
**F34 — Gráfico de ações em tela cheia, com ferramentas de trader.** Serve N19; segue a D2. Um botão no card "Histórico de Preços" abre o gráfico em tela cheia, com os indicadores da F33 e o que uma plataforma de trader oferece: barra de ferramentas de desenho (linha de tendência, linha horizontal de suporte e resistência, canal, retângulo, retração de Fibonacci, texto), régua que mede variação % e pregões entre dois pontos, escala logarítmica, legenda com abertura, máxima, mínima, fechamento e volume do candle sob o cursor, comparação com outro ticker ou com o Ibovespa em %, e uma boleta compacta para comprar e vender sem sair da tela. Os desenhos ficam salvos por jogador e ticker numa tabela nova (`chart_drawings`, com os pontos em JSON), entrando por migration (D9). Falta escolher a biblioteca: (1) continuar no `lightweight-charts` e escrever as ferramentas de desenho como plugins (a API de primitives da versão 5; os exemplos oficiais trazem linha de tendência e retângulo); (2) trocar pelo KLineChart (Apache 2.0), que já vem com cerca de 15 ferramentas de desenho, mas calcula indicadores no navegador, e pela D2 eles viriam do backend como indicador customizado; (3) o Advanced Charts da TradingView tem tudo pronto, mas a licença pede cadastro e não permite publicar a biblioteca em repositório público, o que o deixa fora deste projeto. Sai daqui com um protótipo de linha de tendência e Fibonacci nas opções 1 e 2, e a escolha.

<a id="f44"></a>
**F44 — Expansão "Gestoras": fundar a gestora e abrir capital.** Serve N23. Inspiração: o Capitalism Lab (oferta pública, emissão de novas ações, recompra, compra de ações dos concorrentes), o OpenTTD e o Software Inc. Lá cada jogador é uma empresa que fabrica ou transporta; aqui tudo é finanças, então a empresa de cada jogador é uma gestora, e o que ela vende é o próprio desempenho. **Como expansão:** ligável por partida numa **aba própria "Expansões"** no lobby, com banner, emblema e "o que muda", como a loja de DLC dos jogos da Paradox; é enfeite visual, o sistema é o mesmo ligado ou não. **A gestora** tem nome e ticker de 4 letras mais 11, como cota de FII na B3 (o servidor recusa letras que já existam entre os ativos importados), e no livro de ofertas a linha leva a cor e a sigla do jogador, para não se confundir com ativo real. O jogador a funda levando **caixa, ações e títulos** da carteira em troca de cotas, e a opera por um **modo na topbar** ("Operando: Aurora Gestão"), que troca a conta de todas as telas de mercado, com uma faixa verde-petróleo e o caixa da gestora dizendo qual conta está ativa. **É um fundo fechado listado, como um FII:** (1) **oferta pública** quando o gestor quiser — cotas novas ao preço do patrimônio por cota (patrimônio de R$ 100 mil em 1.000 cotas dá R$ 100), e o dinheiro de quem compra entra na gestora: é investir no amigo; (2) **mercado** — depois da oferta, as cotas são negociadas no livro de ofertas que a renda variável já tem, e o preço sai da oferta e da procura, acima do patrimônio por cota (ágio) quando a sala acredita no gestor e abaixo (deságio) quando não; (3) **liquidez** — a liquidez de fundo do livro nasce dos candles de cada ativo, e a cota não tem candle, então um formador de mercado sintético põe ordens de compra e venda em volta do patrimônio por cota, numa faixa de 20% para cima e para baixo recalculada todo dia; dentro da faixa, o preço sai dos jogadores, e o livro tem contraparte até numa sala de 2; (4) **taxas** — a gestora paga aos gestores taxa de administração todo mês sobre o patrimônio e taxa de performance a cada 6 meses sobre o que passar do CDI, com teto na partida de **2% ao ano de administração e 20% de performance**, e cada gestor escolhe até o teto. A performance respeita a **marca d'água**, o maior patrimônio por cota sobre o qual a taxa já foi cobrada: se a cota cai de R$ 100 para 80 e volta a 100, a recuperação não paga performance. **O lucro fica dentro da gestora** e valoriza a cota. **Por que abrir capital, e quando:** as taxas são sobre o dinheiro dos outros, e com ágio as cotas do próprio gestor valem mais no ranking; o custo é ficar exposto, porque vender mais da metade abre a porta para perder o controle (F103). Abrir cedo, sem histórico, tende a sair com pouca procura; abrir depois de um bom ano tende a sair com ágio. **O gestor e a própria gestora:** o gestor negocia com a gestora pelo livro como qualquer jogador; a linha leva a sigla dele, então a negociação fica à vista, e quem cobra é a sala, vendendo a cota (deságio) ou trocando o gestor (F103). **Regras para o cálculo fechar:** só pessoas compram cotas, nunca gestoras, o que impede a participação cruzada (A com cotas da B, que tem cotas da A). No ranking, cada jogador soma a carteira pessoal, as taxas recebidas e as cotas que tem pelo **preço de ranking**: a média dos negócios dos últimos 20 pregões, ponderada pelo volume e limitada a 30% acima ou abaixo do patrimônio por cota; sem negócio no período, vale o patrimônio por cota. Um ágio de até 30% conta, e um negócio forçado a R$ 1.000 numa cota de R$ 100 conta no máximo como R$ 130. A carteira da gestora só conta através das cotas, sem contar o mesmo dinheiro duas vezes. **Estrutura:** a carteira própria da gestora é a F101; a cota é um ativo no livro de ofertas, com o patrimônio por cota publicado a cada dia. **Com a expansão Governo & Política (F95):** quando o gestor vence a eleição, na posse ele deixa de operar a gestora e de receber as taxas, porque a carteira do presidente fica congelada; um co-gestor (F104) assume e, sem co-gestor, a gestora congela até o fim do mandato; as cotas que ele tem continuam dele. A F95 sai antes, então a carteira congelada do presidente já existe quando a gestora for implementada: cabe a esta feature estender o congelamento à gestora. **Nas features seguintes:** emissão de novas cotas e recompra (F102), troca de gestor pela assembleia (F103), co-gestores (F104) e rendimentos mensais (F105). Falta: um protótipo do preço da cota no livro, com o formador sintético e jogadores comprando e vendendo, para calibrar a faixa de 20%.
 **Na preparação do lobby:** a identidade da gestora (nome e ticker) fica salva no perfil, no molde do Meu partido, e entra numa aba própria da preparação (F174); a gestora preparada é fundada no 1º dia, vazia, e o jogador leva para ela o que quiser da carteira.

<a id="f55"></a>
**F55 — Modo aquisição hostil.** Serve N23. Um modo de jogo da expansão "Gestoras" (F44) em que perder o controle tira o jogador da partida. Todo o patrimônio de cada jogador está na própria gestora, e quem juntar mais da metade das cotas de outra a incorpora: o dono anterior sai da partida e a gestora dele passa a ser controlada pelo comprador. Vence quem sobrar, ou quem tiver o maior patrimônio na data final. **Carência:** nos primeiros meses (padrão 12) ninguém pode passar de metade de outra gestora, para que abrir capital cedo não seja suicídio. **Ninguém fica invulnerável:** sem oferta pública, a gestora seria impossível de comprar, então no fim da carência todas precisam ter uma parte mínima das cotas no mercado (padrão 50%); quem não abriu capital entra numa oferta automática pelo patrimônio por cota. **Defesa:** recompra de cotas com o caixa da gestora e compra com as taxas recebidas, como uma empresa que recompra ações para não ser comprada. Falta decidir: a parte mínima no mercado; se o incorporado sai da partida ou vira co-gestor do comprador (como numa fusão); e se há um preço mínimo por cota durante a tentativa de aquisição, como nas ofertas públicas de aquisição reais.

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
**F158 — Animações do Como jogar revistas.** Serve N25; retrabalho da F126. No playtest, o tutorial pareceu estranho: o estilo das animações ficou parecido com o do Create, e o número do passo que aparece no meio da animação, num círculo ao lado do alvo (`StepMarker` em `tutorial/stage/stage-kit.tsx:144`, número vindo de `topic-illustration.tsx:57`, usado em `buy-stock.tsx` e `order-types.tsx`), polui a cena. O salto para o trecho do passo ao clicar numa etapa funciona bem e fica como está. Falta escolher o visual numa rodada no canvas: comparar as animações atuais com as primeiras, feitas no canvas a partir das Dicas e truques do Factorio, decidir se o número sai da cena (o passo ativo já fica destacado na lista) e o que muda no cursor e no destaque. **Palco do tutorial (avaliado em 03/11):** a captura mostra o palco com a tela inteira encolhida a uns 70%, então o texto de 12 px do livro de ofertas chega a uns 8 px, e o marcador do passo cobre o texto que aponta. O desenho do retrato (palco em tamanho real mostrando só o trecho que o passo explica, o marcador numa margem à esquerda com uma linha até o alvo e os passos numa fileira abaixo) é coerente e o usuário o reconhece como a direção, mas não vai ser implementado a partir desse board: entra na rodada de canvas dedicada desta F, com o método completo (variantes e estados).

<a id="f179"></a>
**F179 — Topbar que cabe com a corrida e o governo.** Serve N15. O controle de velocidade (`layouts/partial/topbar.tsx`) é largo: depois do selo de pausa vêm a data, o play e os cinco botões de velocidade (1×, 2×, 4×, 10× e 100×). Com a corrida pela meta, o governo, o Como jogar e o caixa na mesma linha, a topbar quebra. Hoje isso é um caso extremo; com as Gestoras, governo, gestora e corrida pela meta ligados juntos passam a ser o caso comum, e é lá que o desenho se decide. O desenho no canvas já inclui o layout com as Gestoras, então a topbar é resolvida na 4.1, depois da F44, e entra no app já certa para o conjunto. A topbar não quebra linha, então a variante em duas linhas fica fora. Das outras, o canvas compara: (a) a velocidade num botão só ("10×") que abre as opções; (b) a corrida e o governo como selos compactos, com o detalhe ao passar o mouse. A referência é 1920 de largura, e em 1366 nada pode quebrar; o estado de teste é corrida, governo e gestora ligados, pausa com o motivo mais longo e o x100 destacado. O selo de pausa já sai só com "Pausado" e o motivo numa dica no lote de correções da 3.4 (F217), pedido dos playtests de 31/out e 04/11. Sai daqui para Pendente com a variante escolhida.

<a id="f193"></a>
**F193 — Indicadores técnicos e padrões de vela explicados no Como jogar.** Serve N25 e N19. Hoje cada indicador técnico diz Compra, Venda ou Neutro, com um "i" de texto curto que não ensina a ler, e o "i" dos padrões de vela nem abre. A ideia do playtest de 31/out: um tópico por indicador no Como jogar, em fases: o que é e como se calcula; por que ele aponta compra ou venda; um caso em que acerta; as ressalvas, quando ele engana. O "i" do indicador abre o tópico na aba dele. O mesmo molde serve aos padrões de vela, junto do catálogo (F131). As ordens a mercado e limitada já têm o tópico "Ordem a mercado e limitada" (`tutorial/topics/order-types.tsx`), que mostra a limitada esperando o preço chegar ao limite, e ficam como estão.

<a id="f202"></a>
**F202 — Backtest que corre mais rápido que a partida comum.** Serve N10; segue a D8. Depois da correção do dia que crescia, o backtest de 10 anos com 5 bots já fica mais rápido a cada pregão, mas ainda corre no ritmo de uma partida comum na velocidade máxima. Pelo `profile:match`, com 7 bots o dia custa ~90 ms: os ~2.500 pregões de 10 anos levam perto de 4 minutos. Um backtest não tem ninguém olhando cada pregão, então tudo o que o dia faz para a tela e para retomar a partida no meio é custo sem retorno.

O backtest já pula os avisos por pregão e o governo e grava os snapshots em lote (`_record_backtest_day`, `flush_backtest`). O que continua igual à partida comum, e é candidato a sair do caminho do dia: gravar no banco os eventos de cada pregão no `flush` em vez de acumular em memória e gravar em lote, ler do banco o que o próprio motor acabou de escrever (fluxos de ordens no fator de impacto, preços do dia), a trava do motor tomada a cada pregão, e o cálculo do imposto e do caixa por dia. Pela D8 o executor rápido é o mesmo motor com as mesmas estratégias e as mesmas regras do dia: muda só onde o dado mora enquanto o backtest corre e quando ele vai para o banco.

**Como medir:** o tempo total do backtest de 10 anos com 5 bots, três rodadas no banco de teste, junto da medida por etapa do dia do modo debug e de um perfil do motor (yappi) de 200 pregões, antes e depois. Para conferir que o resultado não mudou, o mesmo backtest com a mesma semente dá o mesmo patrimônio final de cada bot, centavo por centavo.

**Aceite:** o backtest de 10 anos com 5 bots leva no máximo metade do tempo de 2.500 dias de partida comum com os mesmos bots, e o patrimônio final de cada bot sai igual ao de antes da mudança com a mesma semente.

<a id="f211"></a>
**F211 — Livro de ofertas e ordens abertas do detalhe do ativo.** Serve N15. O livro (`features/variable-income/components/order-book-card.tsx`) simula a profundidade de mercado a partir do candle do dia, e a ordem do jogador se perde no meio dele. O que o código faz hoje:
- **O livro vem do candle do dia corrente**, o pregão que o jogo acabou de avançar (`market_liquidity.py`: compra abaixo do preço típico `(máxima + mínima + fechamento) / 3`, venda acima, com a distribuição de volume do candle). Não é o candle do dia seguinte.
- **A ordem do jogador entra no livro com a data do dia em que foi enviada** (`operation.py:185`) e só executa quando o candle do dia seguinte injeta liquidez do outro lado; ela executa no preço dela (`matching_engine.py:197`).
- **O livro não vem ordenado por preço**: `order_book.py:93-107` devolve o heap na ordem interna e a tela não define ordenação inicial (`order-book-card.tsx:69`), por isso a ordem do jogador aparece no meio.

**Falta** desenhar, numa rodada no canvas em Opus com variantes e estados (como numa feature nova), a tela do livro. O desenho de 03/11 parte de: a ordem aberta do jogador numa faixa no topo com Cancelar à mão; o livro em duas colunas, Compra (maior preço no topo) e Venda (menor preço no topo), com a melhor compra e a melhor venda em destaque, ligadas à boleta; uma barra de quantidade; a coluna Situação sai (repetia "Aberta"); o balão "Tópico" some. O usuário gostou do rumo e pediu o refinamento pelo método completo. A rodada decide também o que o livro diz sobre si mesmo (que é a pressão ao redor do preço do candle de hoje) e se a ordenação por preço passa a vir do backend. Fica fora de versão.

<a id="f267"></a>
**F267 — Lobby com topo enxuto e profissão na preparação.** Serve N15 e N39. O topo do lobby quebra linha e fica desarmônico: Conquistas, Minha preparação e Como jogar dividem a linha com o título, o link de convite e o Desafio da vela. No card do bot, "Bot", "CLT" e "robô não prepara" se sobrepõem e "Comp…" corta (`lobby-player-list.tsx:173`, `:192-198`). A profissão sai do seletor do card e vira uma aba do diálogo Minha preparação (`preparation-dialog.tsx:73`, que hoje tem as abas partido e estratégias).

<a id="f268"></a>
**F268 — Tela do Mapa repensada.** Serve N34 e N15. Em "Estados, do maior para o menor", o "Ver mais" abre um card pequeno numa coluna estreita à direita, com rolagem horizontal, e deixa a página vazia à esquerda. Os rótulos das lentes ocupam espaços desiguais.

<a id="f269"></a>
**F269 — Governo e Eleição com as ações do jogador num lugar só.** Serve N34 e N15. Quem é presidente ou está em campanha não acha onde agir: criar medida, prometer na campanha, orientar a bancada. As ações se espalham entre as telas Governo e Eleição e entre as abas de cada uma. O card começa por uma análise de UX das duas páginas inteiras. Entra na análise o valor do PIB do país, que hoje só aparece no card Dívida ÷ PIB, como "PIB em 12 meses", e a jogadora não achou.

<a id="f270"></a>
**F270 — Cards permanentes da Renda fixa integrados à tela.** Serve N15. Os cards fixos "CDB Nubank Liquidez Diária", em verde, e "Conta em dólar", em azul, destoam da tela: as cores, o layout e a posição não seguem o resto da Renda fixa.

<a id="f279"></a>
**F279 — Estratégias automáticas novas e revisão das atuais.** Serve N4 e N8. As estratégias automáticas e os bots foram desenhados antes do governo, do dólar, do crédito e das expansões. Precisa conferir se continuam competitivas e se faltam estratégias que usem o que entrou. O rebalanceamento por meta com várias classes já é a F197, na Mesa do trader.

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
| **F69** | Feature | Imprevistos configuráveis e tipos novos | N23 | — | M26 · 4.1 |
| **F194** | Feature | Dólar e ativos internacionais | N34, N11 | D20 | M26 · 4.1 |
| **F226** | Feature | Mercado reage à surpresa: o Focus da partida | N34, N31, N41 | D20 | M26 · 4.1 |
| **F232** | Correção | Crescimento que sente o rombo do governo | N34 | D20 | M26 · 4.1 |
| **F250** | Correção | Correções da 4.1 | N15, N34 | — | M26 · 4.1 |
| **F251** | Melhoria | Mapa da eleição ao longo do tempo | N34 | — | M26 · 4.1 |
| **F252** | Melhoria | Atalhos de valor no Tesouro e varredura de qualidade de vida | N15 | — | M26 · 4.1 |
| **F253** | Melhoria | Impostos e cortes que fecham a conta do governo | N34, N41 | D20 | M26 · 4.1 |
| **F254** | Feature | Programas de governo com nome | N34, N31 | D19 | M26 · 4.1 |
| **F256** | Melhoria | SELIC abaixo de zero em futuro com deflação | N34 | D20 | M26 · 4.1 |
| **F257** | Feature | Viver de renda que sente a economia | N23, N34 | D20 | M26 · 4.1 |
| **F258** | Melhoria | Orientação da bancada que se explica | N34 | — | M26 · 4.1 |
| **F259** | Correção | Preço dos ativos cotados em dólar convertido para real | N11, N34 | — | M26 · 4.1 |
| **F260** | Feature | Caixa em dólar com o juro americano | N41, N34 | — | M26 · 4.1 |
| **F261** | Feature | Profissão no viver de renda | N23, N34 | D19 | M26 · 4.1 |
| **F262** | Feature | Pedido de impeachment aberto por jogador | N34 | — | M26 · 4.1 |
| **F263** | Correção | Bolsa com piso e dividendo que acompanha o preço da partida | N3, N34 | D20 | M26 · 4.1 |
| **F264** | Correção | Nota de desempenho que não explode com patrimônio quase zero | N9, N3 | D10 | M26 · 4.1 |
| **F265** | Correção | Acabamentos do mapa, do Tesouro e dos cards da economia | N15, N34 | — | M26 · 4.1 |
| **F266** | Melhoria | Central de dados redesenhada | N13, N15 | — | M26 · 4.1 |
| **F271** | Melhoria | Paleta de 20 cores para os partidos, sala de 12 jogadores e um seletor de cor único | N20 | — | M26 · 4.1 |
| **F272** | Melhoria | Seletores e combobox novos | N15 | — | M26 · 4.1 |
| **F273** | Melhoria | Convites que se escolhem e se acumulam | N34, N23 | — | M26 · 4.1 |
| **F274** | Feature | Presidência e base do governo que valem a pena | N34 | — | M26 · 4.1 |
| **F275** | Feature | Vitória política separada do capital | N34, N22 | — | M26 · 4.1 |
| **F276** | Correção | Governo ruim perde aprovação | N34, N41 | — | M26 · 4.1 |
| **F277** | Melhoria | Jornal com eventos raros em destaque e manchetes variadas | N31 | — | M26 · 4.1 |
| **F278** | Feature | Imprevistos e eventos de vida mais variados | N23 | — | M26 · 4.1 |
| **F280** | Melhoria | Corrida eleitoral com bots sempre presentes e campanha que pesa | N34, N8 | — | M26 · 4.1 |
| **F281** | Correção | Banco Central autônomo que decide em reunião, em passos de 0,25, olhando através do imposto | N34 | D20 | M26 · 4.1 |
| **F282** | Correção | Texto dos gráficos com no mínimo 12 px | N15 | — | M26 · 4.1 |
| **F283** | Melhoria | Campos de valor com o mesmo controle de R$ e de porcentagem | N15 | — | M26 · 4.1 |

<a id="f69"></a>
**F69 — Imprevistos configuráveis e tipos novos.** Serve N23. O modo viver de renda (F53) já nasce com os tipos de imprevisto num registro, em que cada tipo é uma entrada com nome, múltiplo da despesa mensal, efeito (sai do caixa ou corta o salário do mês seguinte) e peso no sorteio; adicionar um tipo é acrescentar uma entrada, sem mexer no motor, no log nem nas telas. Esta feature expõe esse registro ao host: no lobby, o host edita o valor de cada tipo (por exemplo, o conserto passa de 1 para 2 despesas mensais), liga e desliga tipos e cria tipos próprios com nome, valor e efeito. O sorteio continua saindo da semente da partida, então todos os jogadores seguem recebendo os mesmos imprevistos nos mesmos dias, e a configuração vale para a partida salva.

<a id="f194"></a>
**F194 — Dólar e ativos internacionais.** Serve N34 e N11; condicionado por D20. Ideia do playtest de 31/out: a cotação do dólar no jogo, subindo com a desconfiança na moeda e caindo com o juro real alto, e os ativos internacionais andando junto. Antes tudo era em real: não existia a desvalorização da moeda, e investir fora não protegia de nada. Agora ter ativo dolarizado é estratégia de proteção, e o governo irresponsável pesa no câmbio e, pelo câmbio, na inflação.

**Feito.**
1. **O dólar da partida** é a PTAX da história vezes e elevado ao desvio: cada ponto de prêmio de risco acima da história soma 4% ao dólar e cada ponto de juro real acima da história tira 2%, cada causa com teto no expoente. Sem governo, o dólar da partida é a PTAX. Depois do último dado real a PTAX vira série macro e anda pela paridade do poder de compra.
2. **Repasse à inflação:** cada 1% de alta do dólar em 12 meses, contra a da história, soma 0,07 ponto ao IPCA em 12 meses. O prêmio de risco deixou de entrar direto no IPCA e chega a ele só pelo dólar. Para fechar o ciclo prêmio, dólar, inflação e juro com números finitos, a dívida do governo tem teto de 300% do PIB.
3. **Origem do ativo:** Nacional ou Internacional, inferida na importação (moeda USD ou classe BDR é Internacional), com troca manual na Central de dados que a reimportação preserva. O ativo Internacional anda só com o fator do dólar da partida (a razão entre o dólar da partida e a PTAX do dia, para o câmbio não contar duas vezes).
4. **Na tela:** card do dólar e KPI no painel da Economia, com o detalhe de cada ligação; seletor de origem com bandeirinha na Central de dados; filtro e bandeira na listagem de renda variável.

**Fica de fora.** O caixa em dólar com o juro americano é a F260. A calibragem dos pesos usa o CLI da economia (`.claude/trabalho/economia/calibrate10.py`); o teto de 300% do PIB deixa o cenário de gasto desenfreado com o BC cooperando derrubar a bolsa a perto de 5 mil pontos em 2010.

<a id="f226"></a>
**F226 — Mercado reage à surpresa: o Focus da partida.** Serve N34, N31 e N41; condicionado por D20. Antes a bolsa reagia ao tamanho do desvio da SELIC no mesmo dia da decisão, anunciada ou não. No mercado real o preço já carrega o esperado, e no dia só mexe a parte que ninguém esperava. Agora a bolsa separa o esperado da surpresa, e a pesquisa Focus do Banco Central entra na base.

**Feito.**
1. **A bolsa reage em duas partes.** O esperado é a regra do Banco Central e se dilui no trimestre; a surpresa é o afastamento que o presidente mostrou na última reunião e entra inteira no dia em que a decisão passa a valer (o dia seguinte à reunião). Os 2,9% por ponto valem para as duas, então um desvio mantido por um ano dá o mesmo efeito acumulado de antes: muda o momento, não o tamanho. O presidente que segue a regra move a bolsa antes da reunião; quem segura a SELIC com a inflação alta surpreende no dia.
2. **O Focus é importado:** a SELIC da próxima reunião, o IPCA dos próximos 12 meses, o PIB do ano e o câmbio do fim do ano, todos pela mediana da pesquisa inteira, a partir da API de expectativas do Banco Central. As quatro aparecem na Central de dados, num grupo próprio, com dica de como ler; não limitam o período da partida nem ganham futuro gerado.
3. **No cartão da SELIC,** o KPI "Mercado espera": a mediana do Focus quando a última pesquisa tem até 30 dias (senão, a SELIC de hoje) mais o que o mercado espera do presidente, com a dica do que é o Focus e de como a surpresa mexe na bolsa.

**Fica de fora.** Só a SELIC esperada entra na conta da bolsa; IPCA, PIB e câmbio do Focus ficam como informação. O comunicado do Copom, que move a expectativa e cobra credibilidade, segue fora.

<a id="f232"></a>
**F232 — Crescimento que sente o rombo do governo.** Serve N34; condicionado por D20. Na calibragem de 10 anos, o presidente que dá reajuste real de 15% ao ano por 10 anos chega a um primário de −22,7% do PIB e mesmo assim cresce 8% ao ano, o teto do jogo (`MAX_GROWTH` em `backend/features/economy/growth.py`), em 78 de 120 meses, com o desemprego no piso de 4% em 81. O crescimento do jogo já é o real, descontada a inflação, então o número é implausível de fato. O impulso fiscal (`IMPULSE` em `backend/features/economy/links.py`) empurra o PIB a cada piora do primário, e nada do outro lado segura o crescimento. Pior: o presidente que gasta e segura a SELIC baixa gera inflação alta e juro real muito negativo, e o modelo lê o juro real negativo como estímulo, então a inflação alta empurra o PIB para cima.

**Plano.** Duas ligações novas no alvo de crescimento (`GrowthAim`), cada uma sobre "partida menos história" (D20), uma linha própria no detalhe do PIB e uma entrada no `EconomyLink`, com a fonte na docs da economia:
1. **Inflação acima do limiar tira crescimento.** O IPCA de 12 meses acima de 12% ao ano tira crescimento a cada ponto acima do limiar; abaixo dele, nada. Base: Khan e Senhadji (FMI, 2001) acharam que, em países emergentes, a inflação acima de 11 a 12% ao ano passa a reduzir o crescimento, porque a incerteza trava o investimento; Bruno e Easterly (1998) mostram a queda forte do crescimento nas crises acima de 40% ao ano, como a dos anos 1980 no Brasil.
2. **O prêmio de risco encarece o crédito (efeito expulsão).** O prêmio acima da história tira crescimento mesmo com a SELIC baixa, porque o juro longo que as empresas pagam sobe com a desconfiança no governo, e elas investem menos. Foi o caminho do Brasil em 2002 e de 2014 a 2016.

**Sai a faixa do crescimento da partida:** o teto de 8% e o piso de −6% deixam de valer para o desvio (`next_month`), e quem segura o crescimento passa a ser o freio, com cada número explicado por uma ligação. Só sobra um piso de −15% ao ano (`COLLAPSE_GROWTH`), porque abaixo disso o ciclo dívida, prêmio e crescimento deixa de ser finito; para cima não há teto. Calibrado em 1,2 ponto por ponto de IPCA acima de 12% e 0,75 ponto por ponto de prêmio acima da história. A faixa do modelo da história onde a série não cobre (`step_growth`) fica, porque ali nenhuma medida do governo age.

**Calibragem** pelo CLI, com os cinco presidentes do roteiro em `.claude/trabalho/economia/calibrate10.py`, junto com a dos impostos e cortes (F253), que mexe na mesma conta.

**Aceite:** na calibragem de 10 anos, o gastador que nunca para cresce abaixo da história na média dos anos 6 a 10 e entra em recessão quando o prêmio dispara; os presidentes que não geram inflação acima de 12% (historiador, austero, austero com Banco Central autônomo) ficam a menos de 0,5 ponto do crescimento médio que já fecharam; nenhum mês de nenhum presidente passa de 15% ou de −15% ao ano. Quem gasta por 4 anos passa de 12% de IPCA e perde crescimento pelo freio, que é o efeito pedido.

<a id="f250"></a>
**F250 — Correções da 4.1.** Lote do playtest de 08/11. Serve N15 e N34.

1. **Nome do jogador com limite.** O apelido não tem tamanho máximo em lugar nenhum (`backend/routes/auth.py:16`, `frontend/features/auth/pages/login.tsx:17`; a coluna `users.nickname` é `Text`), e um apelido gigante quebrou os diálogos da partida. Entra o limite de 20 caracteres no DTO e no formulário do login. Na mesma varredura, o nome do bot (30 no front e sem limite no backend, `routes/simulation.py:198`), o nome da partida e o do backtest (sem limite nos dois lados) ganham o mesmo limite no DTO e no formulário, e a sigla do partido aceita o mesmo tamanho nos dois lados (o front aceita de 2 a 8 letras e o DTO recusa acima de 5, `core/dto/government.py:44`). Os diálogos que mostram o apelido inteiro cortam com reticências e mostram o nome completo numa dica: `lobby-player-menu.tsx:52`, `expel-dialog.tsx:30`, `danger-zone-card.tsx:60` e `frozen-portfolio-card.tsx:38`. Os apelidos longos das partidas salvas continuam valendo e aparecem cortados; confere-se abrindo uma partida salva com o apelido longo.
2. **"Ver como tabela" do Mapa e tabela da Economia.** No Mapa, o link (`map-view.tsx:80`) rola até a tabela de lugares, e com pouca página para rolar o clique parece não fazer nada: sai o link, e a tabela de lugares fica no fim da página. Na Economia sai a tabela que abre e fecha (`economy-table.tsx`, usada só em `economy.tsx:55`), porque os gráficos já mostram os números.
3. **Card da aprovação sem o mapa.** O mini mapa de `approval-regions.tsx` abre um vão grande no card da aprovação (`approval-card.tsx`). Sai o mapa, e ficam o gráfico e um botão "Ver no mapa", que abre o Mapa na lente de aprovação (`mapLink("approval", "region")` de `lib/map-url.ts`, que o Mapa já lê da URL).
4. **Sai o aviso "Novo: indicadores técnicos".** O aviso (`stock-chart/index.tsx:338`) aparece sempre que nenhum indicador está ligado e não tem botão de dispensar. Ele depende do estado, e não de um "já visto": volta toda vez que o jogador desliga o último indicador, e em toda conta nova. Os indicadores já não são novidade, então o aviso sai, e o botão de indicadores do gráfico continua.
5. **Abertura da campanha na janela central do Jornal.** O resultado de turno e o "vão ao 2º turno" saem na janela central, porque o tipo resultado de eleição tem o nível janela fixo (`features/notifications/registry.py:108`). A manchete da abertura da campanha é do tipo calendário eleitoral, que sai como cartão por padrão (`registry.py:130`, `government/headlines.py:73`). Ela passa a sair na janela central, com o nível fixo como o do resultado de turno, e o diálogo de campanha aberta que pausa a partida continua. A janela do Jornal e o diálogo da pausa aparecem um depois do outro, sem se cobrir.
6. **Triagem: orientar a bancada num governo do computador.** O backend respeita a orientação do líder da bancada num governo do computador (teste em `tests/test_congress.py`). O relato de que a orientação Sim por padrão não podia ser recusada tem três causas de desenho, sem bug de código: o acordo de apoio força Sim e o Não só pega depois de "Orientar Não e romper"; o controle aparece mesmo quando a federação tem outro partido como líder e o clique volta 403; e em velocidade alta o mês passa antes de a medida ser orientada, porque a janela vai até a véspera, o último dia útil do mês.

<a id="f251"></a>
**F251 — Mapa da eleição ao longo do tempo.** Serve N34; retrabalho do mapa por região (F164). O Mapa mostrava só o momento atual; agora uma linha do tempo percorre o ciclo inteiro de cada eleição da partida.

**Entregue:** o seletor escolhe o ano e a régua cobre o ciclo (pesquisas mensais do 1º turno, apuração do 1º turno, pesquisas semanais do 2º turno e apuração do 2º). A lente "Quem lidera" junta a pesquisa e o resultado: ponto de pesquisa mostra quem lidera (listras no empate técnico), ponto de resultado mostra quem venceu. Aprovação, Rejeição e Onde vive cada grupo não têm data e escondem a linha do tempo inteira. A Variação compara com o ponto anterior. Marcos entre as pesquisas (promessa, ações de campanha e aliança) aparecem na régua, no máximo dois por intervalo e o resto em "+N". O card do lugar ganha o gráfico "<Lugar> ao longo da campanha", e clicar num ponto leva a régua até ele. As setas ← e → andam a régua, "Reproduzir" anda um ponto por segundo até o hoje e "Voltar ao hoje" sai do ponto passado. Com cinco eleições ou mais, os anos antigos vão para a grade "Anteriores". Se o histórico falha, só a régua mostra o erro, com "Tentar de novo"; o mapa segue no hoje.

**Aceite:** a rota `/api/government/map/timeline` devolve anos, pontos e marcos; conferido no app de teste com duas eleições passadas, a 1920 e a 1366, e com a rota do histórico falhando.

<a id="f252"></a>
**F252 — Atalhos de valor no Tesouro e varredura de qualidade de vida.** Atalhos de 25%, 50% e Tudo na compra e na venda do Tesouro (a venda perdeu o seletor e ganhou o campo sempre visível). Varredura: Enter confirma, foco no primeiro campo e motivo do botão desabilitado (dica ao passar o mouse) nas telas de valor e de ação; atalhos de valor no pagamento antecipado do crédito.

<a id="f253"></a>
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

<a id="f254"></a>
**F254 — Programas de governo com nome.** Serve N34 e N31; condicionado por D19. Hoje o auxílio é uma medida de gasto sem nome (`WELFARE_SPENDING`, em passos de 0,5 ponto do PIB até 5%). A ideia do playtest de 08/11: o presidente cria o programa com nome ("Bolsa Família", "Auxílio Brasil"), e o nome aparece no Jornal ("Governo lança o Bolsa Família") e no card de gasto da aba Contas.

**Plano.** O nome é um campo da medida de hoje, sem medida nova:
1. O auxílio (`WELFARE_SPENDING`) e as obras (`PUBLIC_WORKS`) aceitam nome ao propor a medida, com até 30 caracteres no DTO e no formulário, no molde dos outros nomes da partida. O nome sai no Jornal e no card de gasto da aba Contas; sem nome, tudo fica como hoje.
2. **Extinguir custa mais:** levar a verba de um programa com nome a zero soma rejeição no grupo que a medida atende (a memória da D19), além da queda de apoio que o mesmo corte sem nome já dá. Reduzir sem zerar funciona como hoje.
3. **Rebatizar** (o "Auxílio Brasil" no lugar do "Bolsa Família", em 2021) mantém a verba e o apoio do programa e custa uma vez um pouco de aprovação geral, com a manchete no Jornal.
4. O tamanho do custo de extinguir e de rebatizar se calibra jogando, como os outros números da D19.

Plano econômico com nome ("Plano Real") fica fora: não existe medida de plano econômico.

<a id="f256"></a>
**F256 — SELIC abaixo de zero em futuro com deflação.** Serve N34; condicionado por D20. Hoje o piso da SELIC é 0%, no DTO (`SelicRequest`, `backend/core/dto/government.py:1098`) e na janela de cada reunião (`backend/features/economy/monetary.py:76` e `frontend/features/government/lib/monetary.ts:17`). No histórico do Brasil a inflação é sempre positiva, e com a SELIC a 0% o juro real já fica muito negativo. A SELIC negativa só faz sentido num futuro gerado com deflação (o regime de inflação do gerador vai até −5 pontos), como no Japão e na Europa dos anos 2010.

**Plano.**
1. Com o IPCA de 12 meses negativo, o piso da SELIC desce para −0,5%, o do Banco Central Europeu; com ele de volta acima de zero, a reunião seguinte volta a ter piso 0%. A regra vale no DTO, na janela da reunião e no formulário, e a dica da SELIC explica quando o piso abaixo de zero abre.
2. O caixa do jogador continua rendendo 0%. Com a SELIC negativa, o dinheiro foge da renda fixa pós-fixada para o caixa, que é a lição real do piso perto de zero: os bancos centrais não descem muito porque as pessoas sacam o dinheiro.
3. A renda fixa pós-fixada rende negativo e mostra isso como qualquer perda, e o IR sobre o rendimento negativo é zero; confere-se o cálculo do IR e do extrato com o rendimento abaixo de zero.

**Aceite:** num futuro gerado com deflação, o presidente leva a SELIC a −0,5%, o Tesouro Selic perde valor dia a dia e o caixa não; com o IPCA de volta acima de zero, a reunião seguinte recusa valor abaixo de 0%.

<a id="f257"></a>
**F257 — Viver de renda que sente a economia.** Serve N23 e N34; condicionado por D20. No modo viver de renda, o salário e a despesa são valores fixos da partida (`backend/core/life_budget.py:39`). Eles só se corrigem pelo IPCA de 12 meses em cada aniversário do começo da partida, e só com a correção pela inflação ligada (`life_budget.py:55`, `core/indicators.py:254`). O IPCA lido é o da camada da economia (`features/economy/layer.py:270`), então o gasto do governo, que sobe a inflação, chega ao salário e à despesa por esse caminho indireto. Nada mais chega. O IR é só sobre o investimento (`simulation.py:1645`), sem tocar no salário. O juro do cheque especial é fixo e não segue a SELIC (`simulation.py:225`). A demissão é sorteada da semente com a mesma chance por pregão, sem ler o desemprego nem o PIB (`features/simulation/life_events.py:76`).

**Plano.** Quatro ligações, cada uma lendo a série da partida, que sem governo é a história:
1. **A demissão segue o desemprego:** a chance por pregão passa a ser a de hoje vezes o desemprego da partida sobre o neutro de 9%. Com 18% de desemprego, demite o dobro; com 4%, menos da metade. O sorteio continua saindo da semente.
2. **Reajuste real pelo PIB:** no aniversário da partida, além da correção pelo IPCA, o salário ganha parte do crescimento real do PIB dos 12 meses quando ele é positivo; na recessão, não há reajuste real.
3. **O cheque especial segue a SELIC:** o juro passa a ser a SELIC mais um spread fixo, escolhido para que, na SELIC média da história, dê o juro fixo de hoje.
4. **O IR das pessoas desconta do salário:** o desvio da alíquota do IR das pessoas (F253) contra a referência desconta do salário. Sem governo, o salário líquido é o de hoje.

O registro do orçamento mostra cada mudança no salário, na despesa e no juro com a origem ("reajuste pelo PIB de 3,1%", "demissão com desemprego de 14%"). A profissão do jogador, que liga o salário a um grupo do eleitorado, é um card próprio que parte deste.

**Aceite:** com a mesma semente, uma partida sem governo e de desemprego alto sorteia mais demissões que uma de desemprego baixo, e o registro do orçamento mostra a origem de toda mudança de salário, despesa e juro.

<a id="f258"></a>
**F258 — Orientação da bancada que se explica.** Serve N34. O líder orienta a bancada até o fim do dia da votação, e a casa apura à noite, com a orientação que ele deu até lá. O acordo de apoio mostra o Não pendente, com o aviso do rompimento e o botão de confirmar; fechar sem confirmar mantém o Sim e avisa. Na federação em que outro partido orienta, o controle aparece travado, dizendo quem orienta.

<a id="f259"></a>
**F259 — Preço dos ativos cotados em dólar convertido para real.** Serve N11. O importador manda ao Yahoo Finance o ticker como está quando ele não é da B3 (`yfinance_symbol` em `backend/features/import_data/importer_service.py:44`), e o download (`from_yfinance`, linhas 55-85, e `from_yfinance_batch`) guarda o preço sem ler a moeda que o Yahoo devolve. A AAPL a US$ 200 entra como R$ 200, e o mesmo vale para a MSFT e para o BTC-USD; a tela formata tudo em real (`frontend/shared/lib/utils/format.ts:50`). Comprar uma ação americana sai cinco vezes mais barato do que na vida real, e a alta do dólar não mexe nela. Os BDRs (AAPL34) já vêm em reais e não mudam.

**Plano.**
1. A PTAX, a cotação oficial do dólar que o Banco Central publica todo dia (série 1 do SGS), entra como série nova, desde 1994, e aparece na Central de dados.
2. O importador lê a moeda do ativo no Yahoo e guarda numa coluna nova do ativo (migração pelo `pnpm db:revision`). O preço em dólar se converte para real pela PTAX de cada dia na importação e na atualização, e o histórico antes da PTAX fica de fora. Ativo em outra moeda é recusado na importação com o motivo.
3. Os ativos em dólar já importados ganham a moeda e o preço convertido pela atualização de ativos que já existe. As partidas salvas com esses ativos mudam de preço, então o commit leva `!`.
4. A docs da importação passa a dizer que o preço de fora vem convertido pela PTAX do dia.

**Aceite:** a AAPL e o BTC-USD importados mostram, num dia qualquer, o fechamento do Yahoo vezes a PTAX daquele dia, ao centavo; os ativos da B3 saem iguais aos de antes.

<a id="f260"></a>
**F260 — Caixa em dólar com o juro americano.** Serve N41 e N34; amplia o dólar e os ativos internacionais ([F194](#f194)). O carry trade é tomar dinheiro onde o juro é baixo e aplicar onde é alto, ganhando a diferença enquanto a moeda não vira contra. Exemplo: com o CDI a 13% e o juro americano a 5%, quem aplica em real ganha 8 pontos ao ano a mais, e uma alta de 10% do dólar come todo esse ganho. Antes o dólar já se movia e os ativos de fora já protegiam, mas não existia um ativo em dólar que só rendesse juro, e a escolha "CDI ou dólar com juro americano" não aparecia. Agora ela aparece, com o dólar que empata a conta à vista.

**Feito.**
1. **O juro americano da partida:** a série Fed Funds (taxa básica dos EUA, em % ao ano, baixada do FRED na Central de dados) entra como série macro com início em jul/1994, o da PTAX. Depois do último dado real ela volta a 3% pela metade do caminho a cada 2 anos.
2. **A conta em dólar (Nomad):** ativo de liquidez diária que rende 100% do juro americano, marcado pelo dólar da partida. A compra paga 1,1% de IOF de câmbio e vira dólares ao dólar do dia; o saldo em dólar cresce com o fator diário do Fed e o valor em reais acompanha o dólar. O resgate leva IR de 15% sobre o ganho em reais, sem IOF, e a cobertura automática do caixa vende a conta como vende o CDB de liquidez diária. A conta não entra no cálculo da melhor taxa de renda fixa do crédito.
3. **Na tela:** dois cards lado a lado no topo da Renda fixa (CDB de liquidez diária e conta em dólar, com o "empata se o dólar subir"), prévia em dólares e IOF na boleta de investir, "sai da conta" e IR de 15% na de resgatar, saldo em dólar nos detalhes e na carteira, e a série do Fed com dica na Central de dados.

**Fica de fora.** Empréstimo em dólar (o carry trade completo), título do Tesouro americano, apuração anual do IR sobre a variação cambial e alíquota de IR do câmbio definida pelo governo.

<a id="f261"></a>
**F261 — Profissão no viver de renda.** Serve N23 e N34; parte do viver de renda que sente a economia ([F257](#f257)). Hoje o salário e a despesa são os mesmos para todos os jogadores da partida (`SimulationSettingsDTO`, `backend/core/dto/simulation.py:108`; `_live` em `simulation.py:1340`). A ideia do playtest de 08/11: uma opção do modo, "salário igual para todos" (o de hoje) ou "cada um escolhe a profissão", como uma classe de RPG. Cada profissão pertence a um grupo do eleitorado (D19), então a medida que taxa os mais ricos, reforça o auxílio ou reajusta as aposentadorias chega direto na renda dos jogadores daquele grupo: o jogador que governa mexe na vida dos outros, e o servidor sente na pele o ajuste fiscal que o presidente aprova.

**Equilíbrio sem limitar a renda.** A renda muda de verdade entre as profissões e oscila com a economia; nenhuma é a melhor em tudo. As alavancas candidatas:
- **Com o que a renda oscila:** o CLT pela demissão que segue o desemprego; o servidor pelo reajuste do governo, que congela no ajuste fiscal, mas não é demitido; o aposentado pelo reajuste das aposentadorias, com renda menor e sem demissão; o empresário pelo PIB e pela bolsa, com renda alta nos anos bons e meses sem retirada, ou com aporte, na recessão; quem vive de auxílio pelo auxílio do governo, que é cortado quando a renda passa do limite.
- **Padrão de vida:** a despesa acompanha a profissão, e a meta do modo (o patrimônio que paga a despesa do ano, `goal_on` em `backend/features/statistics/goal.py:13`) passa a ser a de cada jogador. O empresário ganha mais e precisa de mais para viver de renda. Hoje a meta é uma só por partida: mudar isso muda o contrato do `goal_on`.
- **Alvo das medidas:** o IR das pessoas ([F253](#f253)) e as medidas por grupo pesam mais em quem ganha mais.
- **Vantagens próprias:** a estabilidade do servidor, o FGTS e o seguro-desemprego do CLT na demissão, o crédito do empresário.

**Falta:** a lista de profissões e os números de cada uma; se a meta passa a ser de cada jogador ou se o placar compensa a renda de outro jeito; qual profissão os bots escolhem; e como o imprevisto, que é um múltiplo da despesa mensal ([F69](#f69)), se comporta com a despesa de cada jogador: o dia do sorteio segue igual para todos, e o valor sai da despesa de cada um.

**Feito.**

<a id="f262"></a>
**F262 — Pedido de impeachment aberto por jogador.** Serve N34. O líder de um partido com pelo menos uma cadeira na casa, fora o do partido do presidente, abre o pedido enquanto a aprovação de um presidente jogador está abaixo do piso de 25% e fora da carência dos 12 primeiros meses. Há um pedido aberto por vez e cada partido pede uma vez por mandato. O pedido rejeitado soma 5 pontos de rejeição ao partido de quem pediu, nos grupos de eleitores que ainda aprovam o presidente. O pedido sai em manchete para a sala toda e em aviso ao presidente, com o partido que pediu; a tela do Congresso mostra o botão com o custo explicado antes de confirmar. A bancada na base orienta Não e protege o presidente, sem código novo. Os 5 pontos ficam para a calibragem pelo CLI.

<a id="f263"></a>
**F263 — Bolsa com piso e dividendo que acompanha o preço da partida.** Serve N3 e N34; condicionado por D20. Na Simulação #3, o nível da bolsa da partida (`level` em `backend/features/economy/layer.py:270`, a exponencial da soma das forças, sem limite para baixo) levou as ações a 1/400 da série guardada: a PETR4 foi de ~R$ 4,40 a R$ 0,01 no fim de 2031 e ficou assim até o fim. O provento continuou igual ao histórico por ação (`broker.py:142` paga `event.value` sem o fator da partida), e o rendimento passou de ~9% para milhares de por cento ao ano. Uma jogadora aplicou R$ 50 mi em PETR4 entre 2033 e 2035 e recebeu R$ 3,69 bi em dividendos. O arredondamento ao centavo (`_scale` em `variable_income/price_impact.py`) piora o quadro: a ação alterna entre R$ 0,00 e R$ 0,01, e a carteira de um bot foi de R$ 30 mil a R$ 0,01 num pregão e voltou a R$ 7,5 mil.

**Plano.**
1. **Provento na escala da partida.** O dividendo e o JCP por ação são multiplicados pelo `stock_factor` do dia do pagamento, o mesmo do preço. O histórico de proventos e o rendimento (`dividends.py`, `trailing_per_share`) leem o valor já escalado.
2. **Piso com amortecimento no nível da bolsa.** Abaixo de um limiar, a queda do nível se comprime em vez de seguir a exponencial. O limiar e o piso são calibrados na calibragem de 10 anos, com o pior governo que ela simula.
3. **Preço que não arredonda a zero.** O OHLC escalado tem piso de R$ 0,01.

**Aceite.** Teste com o fator da bolsa a 1/400: o provento sai a 1/400 do histórico. A calibragem de 10 anos com o pior governo não leva a bolsa abaixo do piso. Nenhum preço de ação sai R$ 0,00.

<a id="f264"></a>
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

<a id="f265"></a>
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

<a id="f266"></a>
**F266 — Central de dados redesenhada.** Serve N13 e N15. A tabela de séries ficou apertada: nomes cortados ("FOCUS_S…", "GDP_GRO…") e três colunas que só mostram "—". As séries do Focus são importadas e não ganham futuro gerado, por desenho (F226), mas a legenda genérica "repete o último valor" (`how-to-read.tsx:29`) não diz isso.

<a id="f271"></a>
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

<a id="f272"></a>
**F272 — Seletores e combobox novos.** Serve N15. Um componente só (`OptionSelect`, em cima do Combobox do base-ui) no lugar do `select.tsx` e dos quatro combobox de Command: busca a partir de 8 opções, grupo "Indisponíveis" com o motivo escrito, lista que abre embaixo e opções de 48 px. O campo "Ações que ela opera" ganhou a variante com a contagem no botão e as ações marcadas em etiquetas (limite de 30 vindo do backend, "Só as da carteira", "Voltar ao padrão" e "Limpar"), e `/api/simulation/bots/tickers` passou a devolver código e nome da empresa.

<a id="f273"></a>
**F273 — Convites que se escolhem e se acumulam.** Serve N34 e N23. Convidar o vice virou ação própria: escolher no seletor não envia nada, o botão Convidar envia e Retirar convite desfaz, na partida e no lobby. Inscrever a chapa e salvar a fundação deixam de convidar. Quem recebe acumula convites de vice e propostas de federação; aceitar um recusa os incompatíveis do mesmo tipo (vice e federação não se cruzam) e avisa quem convidou. O proponente envia uma proposta de federação por vez. O convite recusado aparece na tela da chapa e no card público do partido.

<a id="f274"></a>
**F274 — Presidência e base do governo que valem a pena.** Serve N34. Revisa duas escolhas antigas do arquivo morto (F95, "o ganho de governar chega só pela própria carteira", e F154, "o aliado ganha só o apoio dos grupos dele"). O presidente recebe 3 vezes o salário da partida no lugar da renda da profissão, sem perda por imprevisto, e acumula legado: 5% de um salário por ponto de aprovação acima de 40 a cada mês fechado, pago no fim normal do mandato e perdido no impeachment (`presidency.py`, `GovernmentBook._pay_legacy`). A medida de obras aceita setor e segmento: as ações do alvo sobem 2,5 vezes a fatia do PIB, até 7,5%, em rampa de 6 meses, e apontar para um setor em que o presidente tem ações tira 6 pontos de aprovação vezes a fatia dele, gravada na medida (`sector_boost.py`, `approval.favoritism_factor`). Ao aceitar o acordo, o líder aliado escolhe o setor da emenda: alta de 30 vezes a fatia do PIB por ano, até 6%, que cai quando o acordo acaba ou é rompido; o partido do computador escolhe um setor fixo, mostrado na prévia. Isenção, obra e emendas somam até 20% por setor. A proposta, a negociação e o card da base mostram o apoio mensal do acordo em verba de campanha (R$ 4.096 por mês, `voters.campaign_amount`). As regras estão em `docs/docs/como-usar/governo.md`. Ficam para o playtest: partida com salário zero não paga a presidência, salário alto pode dominar, e o presidente pode empurrar o próprio setor pela emenda de um aliado sem pagar favorecimento. O ministério para o aliado virou card próprio (F284).

<a id="f275"></a>
**F275 — Vitória política separada do capital.** Serve N34 e N22. A vitória política deixa de somar o patrimônio dos filiados: vence o partido com mais **capital político**, pontos acumulados a cada mês fechado (`backend/features/government/capital.py`, `party_capital`). Só partidos de jogador pontuam: 1 ponto por cadeira na casa em exercício; a aprovação do fechamento (0 a 100) para o partido do presidente (`governed_months` no `GovernmentState`, gravado no `APPROVAL_MEASURED`); `100 × fração cumprida` por promessa no balanço do mandato; e o impeachment tira metade do que a presidência rendeu naquele mandato. Desempate por cadeiras na casa atual. Decisões: medida aprovada não pontua por si (pesa pela aprovação); vence o partido e os filiados dividem a colocação; continua o tipo "Política", sem tipo novo nas regras (a vitória da Expansão Gestoras citada como molde ainda não existe); o ranking de partidos é por capital político em toda partida com a expansão, e a soma de patrimônio saiu de tela, diálogos e textos. O ranking individual segue em patrimônio, informativo. `PoliticalCapitalDTO` (total e as quatro parcelas) substitui `total_networth` no painel e no relatório; a página Eleição mostra total e parcelas, e a tela de resultado ganhou o pódio de partidos. Sem evento novo: partida salva recalcula pelo replay, e uma migration de dados zera o resultado guardado das partidas políticas. Limite conhecido, fora deste card: com o patrimônio fora do placar, gastar tudo em campanha deixa de ter custo na vitória política.

<a id="f276"></a>
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

<a id="f277"></a>
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

<a id="f278"></a>
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

<a id="f280"></a>
**F280 — Corrida eleitoral com bots sempre presentes e campanha que pesa.**

Disputa sempre com os três partidos do computador, fundo público mensal de R$ 8.000 por concorrente (metade igual, metade por cadeiras), teto de contribuição de R$ 8.000 por filiado, caixa único do partido e sobra virando propaganda com √sobra ÷ 128. Limite conhecido: os finalistas chegam ao 2º turno com o caixa zerado até o playtest decidir.

<a id="f281"></a>
**F281 — Banco Central autônomo que decide em reunião, olhando através do imposto.** O Banco Central autônomo decide só nos dias de reunião do Copom (`meeting_days`, hoje em `backend/core/copom.py`, com `SELIC_STEP` e `to_step`): em cada uma leva a regra do dia ao passo de 0,25 ponto, a até 1 ponto da decisão anterior (`autonomous_decision` e `AUTONOMOUS_CAP` em `monetary.py`), e mantém os pontos até a reunião seguinte. A SELIC da partida é a história do dia mais esses pontos segurados (`EconomyLayer.autonomous_points`, `layer.py`); sem efeito do governo nada muda, e entre `first_day` e a primeira reunião o desvio vale 0. A regra olha através do imposto: `reading_points` tira de `inflation_points` o degrau de preço do imposto sobre consumo (`consumption_points`), então um corte do imposto não derruba a SELIC; a regra também alimenta o presidente computador e o esperado do mercado, e a linha do imposto sobre consumo no painel da economia deixa de mostrar efeito na SELIC e na bolsa. No futuro gerado (`synthetic.py`, `_decided_in_meetings`), a SELIC inteira (trecho sorteado mais regime e surto) só muda no pregão seguinte a uma reunião, em múltiplos de 0,25, e o CDI anda colado; o gráfico "Juros e inflação" fica com no máximo 8 marcadores do Copom por ano no futuro. Limite conhecido: no trecho histórico da partida o marcador soma as mudanças reais da história e as reuniões do autônomo, e a SELIC absoluta segue a da história (o múltiplo de 0,25 vale para o desvio do autônomo).

<a id="f282"></a>
**F282 — Texto dos gráficos com no mínimo 12 px.** Serve N15. O texto de gráfico (eixos, legendas, rótulos e tooltips) usa um token só, de 12 px: `CHART_TICK` e `CHART_FONT_SIZE`, em `shared/lib/chart-text.ts`. O teste de tamanho mínimo passou a pegar também `fontSize` literal abaixo de 12, além das classes `text-[Npx]`.

<a id="f283"></a>
**F283 — Campos de valor com o mesmo controle de R$ e de porcentagem.**
Os campos de valor (comprar e vender Tesouro, amortizar, aplicar e resgatar renda fixa, doação) ganharam o mesmo controle R$ | % antes dos atalhos, com Shift para ver o outro modo, modo lembrado por tipo de campo e atalho em R$ que para no máximo. A contribuição mensal ficou só com a grade de quatro. Conferido no app em todos menos doação e contribuição mensal.

---

## 🚫 Descartado

> Nenhum item neste status.
