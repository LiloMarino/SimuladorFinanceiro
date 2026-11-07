<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/atualizar/concluir/descartar/remover um item, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban do projeto, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que ordem e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-11-07):** Dividido o card de ações de campanha em arquivos por parte

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Tipo | Resumo | Marco | Condiciona (F#) | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **N1** | — | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — | — | — | — |
| **N2** | — | Jogar com amigos pela internet sem que cada um instale uma VPN | — | [F5](#f5), [F6](#f6) | — | — | — |
| **N3** | — | Confiar que os números do simulador são exatos e reprodutíveis | — | [F22](#f22), [F100](#f100) | — | — | — |
| **N4** | — | Testar uma estratégia de investimento automática e ver como ela se sai | — | [F110](#f110), [F111](#f111), [F197](#f197) | — | — | — |
| **N5** | — | Saber quanto risco foi corrido para chegar num resultado | — | — | — | — | — |
| **N6** | — | Comparar resultados de simulações diferentes | — | — | — | — | — |
| **N7** | — | Que o simulador cobre os custos de operar do mercado real | — | [F22](#f22), [F100](#f100) | — | — | — |
| **N8** | — | Jogar contra oponentes controlados pelo computador | — | — | — | — | — |
| **N9** | — | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — | — | — | — |
| **N10** | — | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | — | [F28](#f28), [F202](#f202) | — | — | — |
| **N11** | — | Que o cenário econômico simulado seja o histórico real | — | [F194](#f194) | — | — | — |
| **N12** | — | Continuar jogando depois do último dia com dado real | — | — | — | — | — |
| **N13** | — | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | — | — | — | — |
| **N14** | — | Atualizar para uma versão nova sem perder as partidas salvas | — | [F56](#f56) | — | — | — |
| **N15** | — | Usar uma interface agradável e coerente, à altura de um jogo | — | [F37](#f37), [F72](#f72), [F123](#f123), [F179](#f179), [F211](#f211), [F220](#f220) | — | — | — |
| **N16** | — | Ver a carteira e o mercado por setor e segmento | — | — | — | — | — |
| **N17** | — | Enxergar a estrutura do banco e esboçar mudanças nela | — | — | — | — | — |
| **N18** | — | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — | — | — | — |
| **N19** | — | Analisar um ativo com as ferramentas de um trader | — | [F34](#f34), [F131](#f131), [F193](#f193) | — | — | — |
| **N20** | — | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | — | — | — | — |
| **N21** | — | Jogar "na unha", sem a interface apontar a melhor escolha | — | — | — | — | — |
| **N22** | — | Ter objetivos para buscar além de vencer a partida | — | [F90](#f90), [F123](#f123), [F159](#f159) | — | — | — |
| **N23** | — | Jogar com os amigos de outras formas além de cada um por si | — | [F44](#f44), [F55](#f55), [F69](#f69), [F101](#f101), [F102](#f102), [F103](#f103), [F104](#f104), [F105](#f105) | — | — | — |
| **N24** | — | Saber onde está a lentidão durante uma partida | — | — | — | — | — |
| **N25** | — | Entender o que é o simulador e como se joga, sem ler um manual | — | [F132](#f132), [F133](#f133), [F139](#f139), [F140](#f140), [F141](#f141), [F158](#f158), [F193](#f193), [F225](#f225) | — | — | — |
| **N26** | — | Achar a causa de um erro sem vasculhar o log inteiro | — | — | — | — | — |
| **N27** | — | Entrar numa partida que já começou | — | — | — | — | — |
| **N28** | — | Liberar uma vaga sem depender de o jogador sair | — | — | — | — | — |
| **N29** | — | Saber o que cada jogador está fazendo enquanto a partida não começa | — | — | — | — | — |
| **N30** | — | Repetir uma configuração de partida sem montá-la de novo | — | — | — | — | — |
| **N31** | — | Saber o que está movendo o mercado da partida, como quem lê o noticiário | — | [F93](#f93), [F226](#f226) | — | — | — |
| **N32** | — | Saber como foi o mês sem montar a conta | — | — | — | — | — |
| **N33** | — | Investir com dinheiro emprestado, pagando o juro do momento | — | [F111](#f111) | — | — | — |
| **N34** | — | Disputar o poder de mudar as regras da economia da partida | — | [F176](#f176), [F194](#f194), [F226](#f226), [F227](#f227), [F232](#f232) | — | — | — |
| **N35** | — | Tirar da lista as partidas que não interessam mais | — | — | — | — | — |
| **N36** | — | Encontrar rapidamente os menores e maiores valores nos dados do jogo | — | — | — | — | — |
| **N37** | — | Comprar bitcoin do jeito que dá na vida real, em frações | — | — | — | — | — |
| **N38** | — | Saber quando as estatísticas vão mudar, sem achar que travaram | — | — | — | — | — |
| **N39** | — | Chegar ao primeiro dia da partida com as próprias escolhas já feitas | — | — | — | — | — |
| **N40** | — | Jogar partidas longas e na velocidade máxima sem a tela travar | — | [F221](#f221) | — | — | — |
| **N41** | — | Aprender como a economia real funciona, jogando | — | [F225](#f225), [F226](#f226), [F227](#f227) | — | — | — |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | M27 · 4.5 | — | — | — | 🔍 |
| [**F6**](#f6) | Feature | Link de convite pela internet no lobby | M27 · 4.5 | — | Médio | Bom | ⏳ |
| [**F14**](#f14) | Feature | Janela desktop nativa | — | — | Baixo | Bom | 💤 |
| [**F22**](#f22) | Feature | Preço bruto, desdobramentos e dividendos na partida | M22 · 4.0 | — | Alto | Bom | ⏳ |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | M25 · 4.3 | — | — | — | 🔍 |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | M24 · 4.2 | — | — | — | 🔍 |
| [**F37**](#f37) | Feature | Tema escuro | — | — | Médio | Médio | 💤 |
| [**F44**](#f44) | Feature | Expansão Gestoras: fundar a gestora e abrir capital | M18 · 4.1 | — | — | — | 🔍 |
| [**F55**](#f55) | Feature | Modo aquisição hostil | M18 · 4.1 | — | — | — | 🔍 |
| [**F56**](#f56) | Feature | Novidades no app | M27 · 4.5 | — | Baixo | Bom | ⏳ |
| [**F60**](#f60) | Feature | Modo servidor dedicado (--headless) | — | — | Baixo | Bom | 💤 |
| [**F69**](#f69) | Feature | Imprevistos configuráveis e tipos novos | — | — | Médio | Bom | 💤 |
| [**F72**](#f72) | Manutenção | Gráficos padronizados sobre o ChartContainer do shadcn | — | — | Médio | Bom | 💤 |
| [**F81**](#f81) | Manutenção | CORS restrito à mesma origem | — | — | Baixo | Médio | 💤 |
| [**F90**](#f90) | Feature | Cenários | M25 · 4.3 | — | — | — | 🔍 |
| [**F93**](#f93) | Feature | Rumores antecipados | M25 · 4.3 | — | — | — | 🔍 |
| [**F100**](#f100) | Feature | Proventos na carteira e nas telas | M22 · 4.0 | — | Médio | Bom | ⏳ |
| [**F101**](#f101) | Feature | Carteira separada do jogador | M18 · 4.1 | — | Alto | Médio | 💤 |
| [**F102**](#f102) | Feature | Gestoras: emissão de novas cotas e recompra | M18 · 4.1 | — | — | — | 🔍 |
| [**F103**](#f103) | Feature | Gestoras: troca de gestor pela assembleia | M18 · 4.1 | — | — | — | 🔍 |
| [**F104**](#f104) | Feature | Gestoras: co-gestores | M18 · 4.1 | — | — | — | 🔍 |
| [**F105**](#f105) | Feature | Gestoras: rendimentos mensais | M18 · 4.1 | — | — | — | 🔍 |
| [**F110**](#f110) | Feature | Combinar estratégias | — | — | Médio | Bom | 💤 |
| [**F111**](#f111) | Feature | Crédito para estratégias e bots | — | — | Baixo | Bom | 💤 |
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | M28 · 4.6 | — | — | — | 🔍 |
| [**F131**](#f131) | Feature | Catálogo de padrões de vela | M28 · 4.6 | — | — | — | 🔍 |
| [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | M28 · 4.6 | — | Médio | Bom | ⏳ |
| [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | M28 · 4.6 | — | Baixo | Bom | ⏳ |
| [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | M28 · 4.6 | — | Médio | Bom | ⏳ |
| [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | M28 · 4.6 | — | Alto | Bom | ⏳ |
| [**F141**](#f141) | Docs | README com as features de hoje | M28 · 4.6 | — | Baixo | Excelente | ⏳ |
| [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | M28 · 4.6 | — | — | — | 🔍 |
| [**F159**](#f159) | Feature | Conquista "Ordem com paciência" | M18 · 4.1 | — | Baixo | Bom | ⏳ |
| [**F167**](#f167) | Feature | Notícias do ativo como marcadores no gráfico de preço | — | — | Baixo | Bom | 💤 |
| [**F176**](#f176) | Feature | Cadeiras do Congresso por região | — | — | Médio | Médio | 💤 |
| [**F179**](#f179) | Melhoria | Topbar que cabe com a corrida e o governo | M18 · 4.1 | — | — | — | 🔍 |
| [**F193**](#f193) | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | M28 · 4.6 | — | — | — | 🔍 |
| [**F194**](#f194) | Feature | Dólar e ativos internacionais | M26 · 4.4 | — | — | — | 🔍 |
| [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | M24 · 4.2 | — | Médio | Bom | ⏳ |
| [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | M25 · 4.3 | — | — | — | 🔍 |
| [**F211**](#f211) | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | M24 · 4.2 | — | — | — | 🔍 |
| [**F220**](#f220) | Melhoria | Jornal: voltar para hoje e edição destacada no arquivo | — | — | Médio | Bom | ⏳ |
| [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | — | — | Médio | Bom | ⏳ |
| [**F225**](#f225) | Docs | Conceitos de economia real na docs e nomeados na tela | M28 · 4.6 | — | Alto | Bom | ⏳ |
| [**F226**](#f226) | Feature | Mercado reage à surpresa: o Focus da partida | M25 · 4.3 | — | — | — | 🔍 |
| [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | M28 · 4.6 | — | — | — | 🔍 |
| [**F232**](#f232) | Correção | Crescimento que sente o rombo do governo | — | — | — | — | 🔍 |
| [**F242**](#f242) | Manutenção | Partida do lobby em arquivos por parte | M22 · 4.0 | — | Alto | Bom | ⏳ |
| [**F243**](#f243) | Manutenção | Folha de regras do lobby em arquivos por parte | M22 · 4.0 | — | Alto | Bom | ⏳ |
| [**F244**](#f244) | Manutenção | Gráfico de ações em arquivos por parte e um hook | M22 · 4.0 | — | Alto | Médio | ⏳ |
| [**F249**](#f249) | Manutenção | Núcleo do backend sem import de features | — | — | Alto | Médio | 💤 |

<details>
<summary><strong>Concluído / decidido / descartado (30 itens — clique pra expandir)</strong></summary>

| ID | Tipo | Resumo | Marco | Condiciona (F#) | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **D1** | — | Eventos são a fonte da verdade; snapshots são derivados | — | [F22](#f22), [F159](#f159) | — | — | ✅ |
| **D2** | — | Cálculo financeiro acontece só no backend; o frontend exibe | — | — | — | — | ✅ |
| **D3** | — | Dinheiro e quantidade trafegam como Decimal serializado em string | — | [F22](#f22), [F100](#f100) | — | — | ✅ |
| **D4** | — | Banco de dados embarcado no executável | — | — | — | — | ✅ |
| **D6** | — | A retomada continua no dia seguinte ao último evento | — | — | — | — | ✅ |
| **D7** | — | O simulador lê as séries sem saber a origem | — | [F22](#f22) | — | — | ✅ |
| **D8** | — | Bot, modo automático e backtest são o mesmo mecanismo | — | [F110](#f110), [F111](#f111), [F202](#f202) | — | — | ✅ |
| **D9** | — | De onde nasce uma mudança de schema | — | [F101](#f101) | — | — | ✅ |
| **D10** | — | Como a nota geral é calculada | — | — | — | — | ✅ |
| **D11** | — | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | — | — | — | ✅ |
| **D12** | — | Como numerar as versões | — | [F22](#f22) | — | — | ✅ |
| **D13** | — | Um canal de tempo real só: Socket.IO, com fallback de polling | — | — | — | — | ✅ |
| **D14** | — | Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível | — | — | — | — | ✅ |
| **D15** | — | Lint com oxlint, formatação com oxfmt e o TypeScript 7 com a API do 6 ao lado | — | — | — | — | ✅ |
| **D16** | — | Estratégias do app no host, personalização pela API | — | — | — | — | ✅ |
| **D17** | — | Os tópicos do tutorial se animam em código, com o motion | — | — | — | — | ✅ |
| **D18** | — | Uma migration por versão; caminho antigo só cai numa major | — | — | — | — | ✅ |
| **D19** | — | O eleitorado são grupos, cada um com apoio e rejeição por partido | — | [F176](#f176) | — | — | ✅ |
| **D20** | — | A economia da partida é a história mais o desvio que o governo causa | — | [F194](#f194), [F226](#f226), [F227](#f227), [F232](#f232) | — | — | ✅ |
| **D21** | — | O jogo ensina a jogar, a docs explica o modelo | — | [F132](#f132), [F133](#f133), [F140](#f140), [F193](#f193), [F225](#f225), [F227](#f227) | — | — | ✅ |
| [**F233**](#f233) | Manutenção | Constantes de calendário unificadas no core | M22 · 4.0 | — | — | — | ✅ |
| [**F234**](#f234) | Manutenção | Juros compostos num módulo só | M22 · 4.0 | — | — | — | ✅ |
| [**F235**](#f235) | Manutenção | Tipo Percent no indicador do BCB | M22 · 4.0 | — | — | — | ✅ |
| [**F236**](#f236) | Manutenção | Prévia do impacto de preço fora da rota | M22 · 4.0 | — | — | — | ✅ |
| [**F237**](#f237) | Manutenção | Componentes do mercado na pasta da renda variável | M22 · 4.0 | — | — | — | ✅ |
| [**F238**](#f238) | Manutenção | Features do front sem import atravessado | M22 · 4.0 | — | — | — | ✅ |
| [**F239**](#f239) | Manutenção | Formatadores de percentual unificados | M22 · 4.0 | — | — | — | ✅ |
| [**F240**](#f240) | Manutenção | Badge de passo como variante do design system | M22 · 4.0 | — | — | — | ✅ |
| [**F241**](#f241) | Manutenção | Card de ações de campanha em arquivos por parte | M22 · 4.0 | — | — | — | ✅ |
| [**F245**](#f245) | Manutenção | Limpeza de scripts e docs | M22 · 4.0 | — | — | — | ✅ |

</details>

---

## 🚀 Próximas versões

> O que entra em cada versão, na ordem de trabalho. Item arquivado conta como concluído.

### 4.0 — Dividendos (M22)

> **Objetivo:** O preço é o negociado na época, e o ativo desdobra e paga dividendo na partida, no real e no futuro gerado.
>
> **Serve:** N3, N7
>
> **Progresso:** 10/15 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F22**](#f22) | Feature | Preço bruto, desdobramentos e dividendos na partida | — | ⏳ Pendente |
| 2 | [**F100**](#f100) | Feature | Proventos na carteira e nas telas | [F22](#f22) | ⏳ Pendente |
| 3 | [**F233**](#f233) | Manutenção | Constantes de calendário unificadas no core | — | ✅ Concluído |
| 4 | [**F234**](#f234) | Manutenção | Juros compostos num módulo só | — | ✅ Concluído |
| 5 | [**F235**](#f235) | Manutenção | Tipo Percent no indicador do BCB | — | ✅ Concluído |
| 6 | [**F236**](#f236) | Manutenção | Prévia do impacto de preço fora da rota | — | ✅ Concluído |
| 7 | [**F237**](#f237) | Manutenção | Componentes do mercado na pasta da renda variável | — | ✅ Concluído |
| 8 | [**F238**](#f238) | Manutenção | Features do front sem import atravessado | — | ✅ Concluído |
| 9 | [**F239**](#f239) | Manutenção | Formatadores de percentual unificados | — | ✅ Concluído |
| 10 | [**F240**](#f240) | Manutenção | Badge de passo como variante do design system | — | ✅ Concluído |
| 11 | [**F241**](#f241) | Manutenção | Card de ações de campanha em arquivos por parte | — | ✅ Concluído |
| 12 | [**F242**](#f242) | Manutenção | Partida do lobby em arquivos por parte | — | ⏳ Pendente |
| 13 | [**F243**](#f243) | Manutenção | Folha de regras do lobby em arquivos por parte | — | ⏳ Pendente |
| 14 | [**F244**](#f244) | Manutenção | Gráfico de ações em arquivos por parte e um hook | — | ⏳ Pendente |
| 15 | [**F245**](#f245) | Manutenção | Limpeza de scripts e docs | — | ✅ Concluído |

### 4.1 — Expansão Gestoras (M18)

> **Objetivo:** Fundar a própria gestora, abrir capital e disputar as cotas na sala.
>
> **Serve:** N23
>
> **Progresso:** 0/9 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F101**](#f101) | Feature | Carteira separada do jogador | — | 💤 Sem prioridade |
| 2 | [**F44**](#f44) | Feature | Expansão Gestoras: fundar a gestora e abrir capital | [F101](#f101) | 🔍 Em avaliação |
| 3 | [**F102**](#f102) | Feature | Gestoras: emissão de novas cotas e recompra | [F44](#f44) | 🔍 Em avaliação |
| 4 | [**F103**](#f103) | Feature | Gestoras: troca de gestor pela assembleia | [F44](#f44) | 🔍 Em avaliação |
| 5 | [**F55**](#f55) | Feature | Modo aquisição hostil | [F103](#f103) | 🔍 Em avaliação |
| 6 | [**F104**](#f104) | Feature | Gestoras: co-gestores | [F44](#f44) | 🔍 Em avaliação |
| 7 | [**F105**](#f105) | Feature | Gestoras: rendimentos mensais | [F44](#f44), [F100](#f100) | 🔍 Em avaliação |
| 8 | [**F179**](#f179) | Melhoria | Topbar que cabe com a corrida e o governo | [F44](#f44) | 🔍 Em avaliação |
| 9 | [**F159**](#f159) | Feature | Conquista "Ordem com paciência" | [F44](#f44) | ⏳ Pendente |

### 4.2 — Mesa do trader (M24)

> **Objetivo:** O detalhe do ativo vira mesa de operação: gráfico em tela cheia, livro de ofertas e rebalanceamento por meta.
>
> **Serve:** N19, N15, N4
>
> **Progresso:** 0/3 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 Em avaliação |
| 2 | [**F211**](#f211) | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | — | 🔍 Em avaliação |
| 3 | [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | — | ⏳ Pendente |

### 4.3 — Futuros e cenários (M25)

> **Objetivo:** A partida testa a carteira em muitos futuros e em cenários com objetivo, e o backtest corre rápido.
>
> **Serve:** N10, N12, N22, N31
>
> **Progresso:** 0/5 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | — | 🔍 Em avaliação |
| 2 | [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | — | 🔍 Em avaliação |
| 3 | [**F90**](#f90) | Feature | Cenários | — | 🔍 Em avaliação |
| 4 | [**F93**](#f93) | Feature | Rumores antecipados | — | 🔍 Em avaliação |
| 5 | [**F226**](#f226) | Feature | Mercado reage à surpresa: o Focus da partida | — | 🔍 Em avaliação |

### 4.4 — Dólar (M26)

> **Objetivo:** O dólar reage à economia do jogo, e a carteira compra ativos de fora.
>
> **Serve:** N34, N11
>
> **Progresso:** 0/1 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F194**](#f194) | Feature | Dólar e ativos internacionais | — | 🔍 Em avaliação |

### 4.5 — Jogo pela internet (M27)

> **Objetivo:** Amigos de longe entram na sala por um link de convite, e o app conta o que há de novo.
>
> **Serve:** N2, N14
>
> **Progresso:** 0/3 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | — | 🔍 Em avaliação |
| 2 | [**F6**](#f6) | Feature | Link de convite pela internet no lobby | [F5](#f5) | ⏳ Pendente |
| 3 | [**F56**](#f56) | Feature | Novidades no app | — | ⏳ Pendente |

### 4.6 — Ensino (M28)

> **Objetivo:** O Como jogar ensina o jogo e os conceitos sobre as telas mais recentes, e a docs, a demonstração e o README mostram o jogo com tudo que entrou.
>
> **Serve:** N25, N19, N22, N15, N41
>
> **Progresso:** 0/11 concluídos

| # | ID | Tipo | Resumo | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | — | 🔍 Em avaliação |
| 2 | [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | — | ⏳ Pendente |
| 3 | [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | — | ⏳ Pendente |
| 4 | [**F131**](#f131) | Feature | Catálogo de padrões de vela | — | 🔍 Em avaliação |
| 5 | [**F193**](#f193) | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | [F158](#f158) | 🔍 Em avaliação |
| 6 | [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | — | 🔍 Em avaliação |
| 7 | [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | — | 🔍 Em avaliação |
| 8 | [**F140**](#f140) | Docs | Docs reorganizada por tipo de leitor | [F44](#f44) | ⏳ Pendente |
| 9 | [**F225**](#f225) | Docs | Conceitos de economia real na docs e nomeados na tela | [F140](#f140) | ⏳ Pendente |
| 10 | [**F139**](#f139) | Docs | Demonstração regravada com o jogo de hoje | [F44](#f44) | ⏳ Pendente |
| 11 | [**F141**](#f141) | Docs | README com as features de hoje | [F139](#f139) | ⏳ Pendente |

### Sem versão

> Os itens ⏳ e 🔍 que ainda não entraram em nenhuma versão, do que mais destrava trabalho para o que menos ("Destrava" é quantos itens em aberto esperam por aquele). É daqui que sai a próxima versão; os 💤 ficam só no kanban.

| ID | Tipo | Resumo | Serve | Depende de | Destrava | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [**F220**](#f220) | Melhoria | Jornal: voltar para hoje e edição destacada no arquivo | N15 | — | 0 | ⏳ Pendente |
| [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | N40 | — | 0 | ⏳ Pendente |
| [**F232**](#f232) | Correção | Crescimento que sente o rombo do governo | N34 | — | 0 | 🔍 Em avaliação |

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: os itens que podem ser pegos agora, com toda dependência já ✅. A ordem segue o plano: primeiro os itens de cada versão (ou marco) na ordem dele, depois o resto pelo "Destrava", que é quantos itens em aberto esperam por aquele, direta ou indiretamente. 💤 (sem prioridade) e 🚫 não entram.

| ID | Tipo | Resumo | Marco | Destrava | Esforço | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [**F22**](#f22) | Feature | Preço bruto, desdobramentos e dividendos na partida | M22 · 4.0 · 1º | 2 | Alto | Bom | ⏳ |
| [**F242**](#f242) | Manutenção | Partida do lobby em arquivos por parte | M22 · 4.0 · 12º | 0 | Alto | Bom | ⏳ |
| [**F243**](#f243) | Manutenção | Folha de regras do lobby em arquivos por parte | M22 · 4.0 · 13º | 0 | Alto | Bom | ⏳ |
| [**F244**](#f244) | Manutenção | Gráfico de ações em arquivos por parte e um hook | M22 · 4.0 · 14º | 0 | Alto | Médio | ⏳ |
| [**F34**](#f34) | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | M24 · 4.2 · 1º | 0 | — | — | 🔍 |
| [**F211**](#f211) | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | M24 · 4.2 · 2º | 0 | — | — | 🔍 |
| [**F197**](#f197) | Melhoria | Rebalanceamento por meta com várias classes | M24 · 4.2 · 3º | 0 | Médio | Bom | ⏳ |
| [**F202**](#f202) | Performance | Backtest que corre mais rápido que a partida comum | M25 · 4.3 · 1º | 0 | — | — | 🔍 |
| [**F28**](#f28) | Feature | Muitos futuros (Monte Carlo) | M25 · 4.3 · 2º | 0 | — | — | 🔍 |
| [**F90**](#f90) | Feature | Cenários | M25 · 4.3 · 3º | 0 | — | — | 🔍 |
| [**F93**](#f93) | Feature | Rumores antecipados | M25 · 4.3 · 4º | 0 | — | — | 🔍 |
| [**F226**](#f226) | Feature | Mercado reage à surpresa: o Focus da partida | M25 · 4.3 · 5º | 0 | — | — | 🔍 |
| [**F194**](#f194) | Feature | Dólar e ativos internacionais | M26 · 4.4 · 1º | 0 | — | — | 🔍 |
| [**F5**](#f5) | Spike | Spike: provider de túnel pela internet | M27 · 4.5 · 1º | 2 | — | — | 🔍 |
| [**F56**](#f56) | Feature | Novidades no app | M27 · 4.5 · 3º | 0 | Baixo | Bom | ⏳ |
| [**F158**](#f158) | Melhoria | Animações do Como jogar revistas | M28 · 4.6 · 1º | 1 | — | — | 🔍 |
| [**F132**](#f132) | Feature | Tópicos de "como se joga" do Como jogar | M28 · 4.6 · 2º | 0 | Médio | Bom | ⏳ |
| [**F133**](#f133) | Feature | Tópicos de conceitos do Como jogar | M28 · 4.6 · 3º | 0 | Baixo | Bom | ⏳ |
| [**F131**](#f131) | Feature | Catálogo de padrões de vela | M28 · 4.6 · 4º | 0 | — | — | 🔍 |
| [**F123**](#f123) | Melhoria | Redesenhar o aviso de conquista desbloqueada | M28 · 4.6 · 6º | 0 | — | — | 🔍 |
| [**F227**](#f227) | Feature | Intensidade das ligações e laboratório da economia | M28 · 4.6 · 7º | 0 | — | — | 🔍 |
| [**F220**](#f220) | Melhoria | Jornal: voltar para hoje e edição destacada no arquivo | — | 0 | Médio | Bom | ⏳ |
| [**F221**](#f221) | Performance | Lista de ações que aguenta muitas ações | — | 0 | Médio | Bom | ⏳ |
| [**F232**](#f232) | Correção | Crescimento que sente o rombo do governo | — | 0 | — | — | 🔍 |

---

## ⏳ Pendente

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F6** | Feature | Link de convite pela internet no lobby | N2 | — | M27 · 4.5 | [F5](#f5) | Médio | Médio | Alto | Bom |
| **F22** | Feature | Preço bruto, desdobramentos e dividendos na partida | N3, N7 | D1, D3, D7, D12 | M22 · 4.0 | — | Alto | Alto | Alto | Bom |
| **F56** | Feature | Novidades no app | N14 | — | M27 · 4.5 | — | Baixo | Baixo | Médio | Bom |
| **F100** | Feature | Proventos na carteira e nas telas | N3, N7 | D3 | M22 · 4.0 | [F22](#f22) | Médio | Médio | Médio | Bom |
| **F132** | Feature | Tópicos de "como se joga" do Como jogar | N25 | D21 | M28 · 4.6 | — | Médio | Baixo | Alto | Bom |
| **F133** | Feature | Tópicos de conceitos do Como jogar | N25 | D21 | M28 · 4.6 | — | Baixo | Baixo | Médio | Bom |
| **F139** | Docs | Demonstração regravada com o jogo de hoje | N25 | — | M28 · 4.6 | [F44](#f44) | Médio | Baixo | Alto | Bom |
| **F140** | Docs | Docs reorganizada por tipo de leitor | N25 | D21 | M28 · 4.6 | [F44](#f44) | Alto | Baixo | Alto | Bom |
| **F141** | Docs | README com as features de hoje | N25 | — | M28 · 4.6 | [F139](#f139) | Baixo | Baixo | Alto | Excelente |
| **F159** | Feature | Conquista "Ordem com paciência" | N22 | D1 | M18 · 4.1 | [F44](#f44) | Baixo | Baixo | Baixo | Bom |
| **F197** | Melhoria | Rebalanceamento por meta com várias classes | N4 | — | M24 · 4.2 | — | Médio | Médio | Médio | Bom |
| **F220** | Melhoria | Jornal: voltar para hoje e edição destacada no arquivo | N15 | — | — | — | Médio | Baixo | Médio | Bom |
| **F221** | Performance | Lista de ações que aguenta muitas ações | N40 | — | — | — | Médio | Médio | Médio | Bom |
| **F225** | Docs | Conceitos de economia real na docs e nomeados na tela | N41, N25 | D21 | M28 · 4.6 | [F140](#f140) | Alto | Baixo | Alto | Bom |
| **F242** | Manutenção | Partida do lobby em arquivos por parte | — | — | M22 · 4.0 | — | Alto | Médio | Médio | Bom |
| **F243** | Manutenção | Folha de regras do lobby em arquivos por parte | — | — | M22 · 4.0 | — | Alto | Médio | Médio | Bom |
| **F244** | Manutenção | Gráfico de ações em arquivos por parte e um hook | — | — | M22 · 4.0 | — | Alto | Alto | Médio | Médio |

<a id="f6"></a>
**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Abrir para a internet exige fechar antes a tomada do host: hoje ser host é ter o nickname do `config.toml`, e com o host desconectado qualquer jogador assume esse nickname por `/api/user/claim` e passa a poder parar a partida e apagar partidas salvas. O app gera um segredo a cada abertura e abre o navegador do host com ele; o servidor reconhece como host só a sessão que apresentou o segredo, e `/api/user/claim` recusa o nickname do host. O endereço de origem não distingue o host, porque num túnel o tráfego de fora costuma chegar ao servidor pela própria máquina. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada; com o host desconectado, nenhum outro jogador consegue virar host.

<a id="f22"></a>
**F22 — Preço bruto, desdobramentos e dividendos na partida.** Serve N3 e N7; segue a D1, a D3, a D7 e a D12. O importador usa `yf.download(auto_adjust=True)`: o preço vem ajustado por dividendos e desdobramentos até o dia da importação, e a atualização incremental (`upsert_dataframe` só grava linhas depois do último pregão real) emenda duas séries ajustadas em dias diferentes. Um desdobramento 2:1 entre a importação e a atualização vira um degrau falso, uma queda de 50% que não existiu; além disso, o preço exibido não é o que se negociava na época. Com `auto_adjust=False` o problema não some: o `Close` do Yahoo continua ajustado por desdobramento (só deixa de descontar o dividendo), e a lista de dividendos também vem ajustada por desdobramento. Por isso o preço bruto é reconstruído: cada pregão e cada dividendo são multiplicados pelas razões dos desdobramentos com data ex posterior a eles. Esta feature faz o motor inteiro dos proventos, no histórico real e no futuro gerado; as telas ficam na F100, e as duas saem juntas na 4.0. Plano: (1) **Importação bruta:** `auto_adjust=False, actions=True` e a reconstrução acima. Como toda atualização baixa o histórico inteiro, a lista de desdobramentos está sempre completa e o bruto de um dia antigo nunca muda. Desdobramentos e dividendos entram numa tabela de eventos corporativos por ativo (data ex, tipo, razão ou valor por cota, origem e versão, no formato das séries por causa da D7). (2) **Desdobramento, grupamento e bonificação:** na data ex, a quantidade de cada posição muda pela razão como evento da partida (D1, quantidade em Decimal pela D3), e o custo total fica igual, então o preço médio se ajusta sozinho. A fração que sobra numa classe que não negocia fração é truncada e vendida no fechamento do dia, e o valor vai para o caixa como venda comum. (3) **Dividendo:** na data ex, o valor por cota vezes a quantidade da abertura do dia entra no caixa, com o ativo de origem guardado no evento: quem vende na data ex recebe, e quem compra não recebe. O valor é bruto; JCP e IR ficam na F100. (4) **Gerador do futuro:** a calibração passa a usar o preço corrigido por desdobramento, sem descontar dividendo, e o preço gerado não cai na data ex, porque as quedas reais de data ex já estão na média aprendida. O gerador escreve o dividendo sintético na mesma tabela, com origem gerada e pela mesma semente: o rendimento anual é a média dos últimos anos reais do ativo (até 5), com variação sorteada; os meses de pagamento são os do histórico; o ativo com histórico curto usa a média do segmento na base, com pagamento trimestral; quem passou 2 anos ou mais sem pagar continua sem pagar; cripto não paga. O trecho gerado congela com a partida salva, como as séries (D7). (5) **Migration:** a tabela de eventos, o tipo de evento de desdobramento na partida, o ativo de origem no evento de caixa e uma marca de série bruta por ativo; apaga as partidas salvas e o futuro gerado, que jogaram e foram calibrados sobre o preço ajustado, e a próxima atualização de cada ativo sem a marca reimporta a série inteira. É um `feat!` e abre a 4.0 (D12). Os testes de números fixos (retorno, nota geral da D10) são regerados e conferidos contra uma conta à mão antes de aceitar. Gatilho: a 3.4 fechada; a F100 espera esta.
**Aceite:** num desdobramento 2:1 ocorrido depois da importação, a atualização incremental não produz queda de 50% no preço, e a posição de quem tinha o ativo dobra de quantidade sem mudar de valor; a mesma semente gera os mesmos dividendos.

<a id="f56"></a>
**F56 — Novidades no app.** Serve N14. Como as notas de patch de um jogo: o `CHANGELOG.md` da F51 vai junto no executável, o backend o serve com a versão, e o lobby mostra as novidades da versão atual. Na primeira abertura depois de atualizar, o card ou o selo de novidades fica em destaque até ser aberto (o navegador guarda a última versão vista); aberto, mostra "O que há de novo na versão X" e dá acesso ao histórico inteiro. O lugar exato no lobby, que já está cheio, sai de uma iteração no Claude Design antes de implementar.

<a id="f100"></a>
**F100 — Proventos na carteira e nas telas.** Serve N3 e N7; segue a D3. Continua a F22, que guarda os dividendos de cada ativo, reais e gerados, e os credita no caixa na data ex com o ativo de origem; aqui o provento passa a aparecer no jogo. O provento cai no caixa e nunca reinveste sozinho: o que fazer com o dinheiro é do jogador. As telas passam antes pelo canvas. Plano: (1) **Carteira:** o total de proventos recebidos aparece no resumo e, em cada posição, o rendimento (proventos dos últimos 12 meses sobre o valor da posição hoje), em Decimal (D3), com a dica do que ele mede e de como ler. (2) **Detalhe do ativo:** a tela do ativo ganha o histórico de proventos (data ex, valor por cota, total recebido pelo jogador). (3) **Estatísticas e fechamento:** o que entrou como provento soma ao relatório da partida e à decomposição do retorno. (4) **IR:** dividendo e rendimento de FII são isentos para pessoa física, e a regra do simulador trata todo provento como isento; o `yfinance` não separa o JCP (juros sobre capital próprio, com 15% retidos na fonte) do dividendo, e essa simplificação entra escrita na página de impostos dos docs. Gatilho: F22 concluída; sai com ela na 4.0 e destrava os rendimentos mensais da gestora (F105).
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

<a id="f197"></a>
**F197 — Rebalanceamento por meta com várias classes.** Serve N4. Hoje o `TargetRebalance` (`backend/features/strategy/rebalance.py:55`) divide só entre um ativo de ações (BOVA11 por padrão) e a renda fixa de liquidez diária: a meta em ações vai de 10% a 90% (padrão 60%), e o desvio máximo, de 1 a 20 pontos (padrão 5). O playtest de 31/out pediu configurar a meta de cada classe.

**O que muda:** os parâmetros viram uma lista de alvos (um ativo ou uma classe e a porcentagem), que soma 100%, com a faixa de desvio de cada alvo; a estratégia vende o que passou da faixa antes de comprar o que ficou abaixo, como hoje. O formulário da estratégia mostra a lista com o total e recusa o que não soma 100%. O padrão continua 60% em BOVA11 e 40% em renda fixa com 5 pontos, então partidas salvas e backtests antigos dão o mesmo resultado; um teste compara os dois. Os parâmetros salvos no perfil (F170) passam a guardar a lista.

<a id="f220"></a>
**F220 — Jornal: voltar para hoje.** Serve N15. Com a rolagem infinita do Jornal (a lista rola a página inteira, e o "Arquivo da partida" fica fixo na lateral), quem desceu muito pelas edições antigas só volta a hoje rolando de volta até o topo. O pedido do playtest de 05/11: um botão "Voltar para hoje" que aparece assim que a página desce da primeira edição, e um scroll spy que marca na lateral a edição que está na tela. A decisão em aberto é o desenho: onde o botão fica, o que o destaque do arquivo mostra e como os dois convivem com o carregamento de mais edições ao rolar. É tela nova, então vai ao canvas.

<a id="f221"></a>
**F221 — Lista de ações que aguenta muitas ações.** Serve N40. A tela de ações (`variable-income.tsx`) busca todas as cotações de uma vez (`useVariableIncomeStocks`), filtra e ordena no navegador e desenha um mini gráfico por linha. A cada pregão chega um `stocks_update` com todas as ações, e a tabela inteira renderiza de novo. Com poucas ações não pesa; com muitas (uma base importada grande) o navegador trava. O playtest de 05/11 sugeriu paginar com carregamento por rolagem (como no Jornal) e só atualizar o que está na tela. O primeiro passo é medir: o custo do render por pregão com 100, 1.000 e 5.000 ações, para escolher entre paginar a busca, virtualizar as linhas (só as visíveis existem no DOM) ou assinar a atualização só das linhas visíveis. O filtro e a ordenação hoje são do navegador; paginar do lado do servidor leva os dois junto.

<a id="f225"></a>
**F225 — Conceitos de economia real na docs e nomeados na tela.** Serve N41 e N25; condicionado por D21. **Para quem:** quem joga e quer entender por que a economia da partida reagiu como reagiu, e quem lê a docs sem jogar. **O que cobre:** uma página por conceito na categoria de explicação que a reorganização da docs cria: juro real e juro real neutro, curva IS, lei de Okun, curva de Phillips, princípio de Taylor e a reação do Banco Central, defasagem da política monetária, meta de inflação e tolerância, credibilidade e expectativas, prêmio de risco, dinâmica da dívida (r − g) e espiral da dívida, primário que estabiliza a dívida e dominância fiscal. Cada página diz o que o conceito mede, um exemplo numérico, o que é valor bom e ruim, a fonte (relatório do Banco Central, artigo ou livro-texto) e como o jogo o implementa, com a fórmula e os coeficientes: é o lugar único dos números do modelo (D21), e a seção de economia interligada de `docs/docs/como-usar/governo.md` passa a apontar para as páginas. Cada página fecha com o que o jogo simplifica em relação à economia real, e uma página própria reúne as simplificações do modelo inteiro: as defasagens comprimidas, os coeficientes fixos em todas as épocas, o Banco Central que reage só à inflação (e não ao hiato do PIB) e o câmbio representado pelo prêmio de risco enquanto o dólar não entra na partida. O conteúdo parte dos conceitos e das explicações do [EconomicStatistics](https://github.com/LiloMarino/EconomicStatistics) (`frontend/shared/concepts/concepts.tsx` e `frontend/features/explainers/`), adaptado ao que o jogo faz, e as fórmulas entram com KaTeX no Docusaurus (`remark-math` e `rehype-katex`). **Na tela:** onde um texto do jogo cita um conceito ("segue o princípio de Taylor"), o nome dele vem com o sublinhado pontilhado do app e o cursor de interrogação, o mesmo `HoverCardTrigger term` de `frontend/shared/components/ui/hover-card.tsx` que o nome do padrão de candle usa no desafio. Passar o mouse ou focar abre um cartão no molde de `pattern-hint.tsx`, com três blocos. Primeiro, o nome e uma frase do que o conceito é, sem fórmula. Depois, "Na partida agora": o conceito aplicado ao estado da partida, como "IPCA 6,2% contra meta de 3,0%: o Copom tende a subir a SELIC na próxima reunião". Por fim, o "Saiba mais" para a página da docs. Os dois primeiros funcionam sem rede, e só o link depende dela. **Mecanismo:** um componente `ConceptTerm` em `frontend/shared/components/` e um catálogo dos conceitos em `frontend/shared/lib/` (chave, nome, frase e caminho da página da docs). Cada tela que cita o conceito passa o trecho da partida que o cartão lê, já resolvido pela tela, e o "Na partida agora" é montado a partir desse trecho. No mesmo bloco de texto, só a primeira menção ao conceito leva o sublinhado. Um teste confere que o caminho de cada conceito do catálogo existe em `docs/docs/`. Os pontos de partida são o painel da Economia (cada parcela leva o nome do conceito), a decisão do Copom, o prêmio de risco do Tesouro e o card da dívida. **Onde mora:** `docs/docs/`, na categoria de explicação. **Gatilho:** depois da reorganização da docs.

<a id="f242"></a>
**F242 — Partida do lobby em arquivos por parte.** `lobby/components/lobby-match.tsx` mistura o schema do formulário, o resumo da partida e os blocos de novos jogadores, equipes e início.

`dateField`, `simulationFormSchema` e o tipo `SimulationFormValues` vão para `lobby/lib/simulation-form.ts`, que já é dono de `toFormValues`/`toSettingsBody`; os 9 importadores do tipo são ajustados por script. Os blocos de novos jogadores, equipes e início e o resumo `typeRows`/`rows` viram componentes que recebem props, numa pasta `lobby-match/` com `index.tsx`.

Por fora nada muda. Confere-se com `pnpm --dir frontend run check`, `vitest` e o lobby aberto no app de teste, com a folha de regras e o resumo iguais ao de antes.

<a id="f243"></a>
**F243 — Folha de regras do lobby em arquivos por parte.** `lobby/components/rules-sheet.tsx` tem o hook `useNow`, o `SaveStatus` e as seções do formulário (Básico, Modo de jogo, Tipo de partida, Meta, Quem vence, Impacto de preço) no mesmo arquivo.

`useNow` vai para `shared/hooks` e `SaveStatus` para arquivo próprio. Cada `FieldSet` vira um componente que recebe `form`, `readOnly` e os valores observados, numa pasta `rules-sheet/` com `index.tsx`; `selectGameType` e o `useWatch` ficam no principal.

Por fora nada muda. Confere-se com `pnpm --dir frontend run check`, `vitest` e a folha de regras aberta no app de teste, nas abas e salvando.

<a id="f244"></a>
**F244 — Gráfico de ações em arquivos por parte e um hook.** `variable-income/components/stock-chart.tsx` tem constantes, helpers puros, três subcomponentes (`PopRow`, `LegendItem`, `PaneLabel`) e um efeito de criação do gráfico com dois `oxlint-disable` de exhaustive-deps, sem teste de componente. É o mais delicado dos quatro e o último da fila.

Constantes e helpers puros, `PopRow`, `LegendItem` e `PaneLabel` vão para arquivos em `stock-chart/`. O par `fill` + efeito de criação vira o hook `useStockChartInstance`, que recebe `chartType`, `selectedScale`, `layout` e `height` e devolve as refs. Os dois `oxlint-disable` vão junto, com o contrato escrito no hook como afirmação: `layout` resume tudo o que o efeito lê.

Por fora nada muda. Sem teste de componente, a conferência é no app de teste: trocar período, tipo e indicadores, com a mira e o zoom mantidos quando chega dado novo.

---

## 🔍 Em avaliação

| ID | Tipo | Resumo | Serve | D# | Marco | Depende de | Falta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **F5** | Spike | Spike: provider de túnel pela internet | N2 | — | M27 · 4.5 | — | Escolhe o provider da F6 |
| **F28** | Feature | Muitos futuros (Monte Carlo) | N10 | — | M25 · 4.3 | — | Revisa ou confirma a D7 |
| **F34** | Feature | Gráfico de ações em tela cheia, com ferramentas de trader | N19 | — | M24 · 4.2 | — | Escolhe a biblioteca de gráfico |
| **F44** | Feature | Expansão Gestoras: fundar a gestora e abrir capital | N23 | — | M18 · 4.1 | [F101](#f101) | O protótipo do preço da cota com o formador sintético |
| **F55** | Feature | Modo aquisição hostil | N23 | — | M18 · 4.1 | [F103](#f103) | Parte mínima no mercado e o destino do incorporado |
| **F90** | Feature | Cenários | N22 | — | M25 · 4.3 | — | Um preset com objetivo |
| **F93** | Feature | Rumores antecipados | N31 | — | M25 · 4.3 | — | Opção da partida |
| **F102** | Feature | Gestoras: emissão de novas cotas e recompra | N23 | — | M18 · 4.1 | [F44](#f44) | O prazo da preferência e o preço da emissão |
| **F103** | Feature | Gestoras: troca de gestor pela assembleia | N23 | — | M18 · 4.1 | [F44](#f44) | Como a assembleia escolhe o novo gestor |
| **F104** | Feature | Gestoras: co-gestores | N23 | — | M18 · 4.1 | [F44](#f44) | A divisão das taxas |
| **F105** | Feature | Gestoras: rendimentos mensais | N23 | — | M18 · 4.1 | [F44](#f44), [F100](#f100) | A parte do lucro distribuída |
| **F123** | Melhoria | Redesenhar o aviso de conquista desbloqueada | N22, N15 | — | M28 · 4.6 | — | Escolher o desenho do aviso no canvas; liga à F122 |
| **F131** | Feature | Catálogo de padrões de vela | N19 | — | M28 · 4.6 | — | Tópico do Como jogar com cada padrão animado |
| **F158** | Melhoria | Animações do Como jogar revistas | N25 | — | M28 · 4.6 | — | O visual numa rodada no canvas dedicada: animações atuais contra as primeiras, número do passo fora da cena, cursor e destaque, e o palco em tamanho real mostrando só o trecho do passo |
| **F179** | Melhoria | Topbar que cabe com a corrida e o governo | N15 | — | M18 · 4.1 | [F44](#f44) | Escolher a variante entre as do canvas, já com o layout das Gestoras |
| **F193** | Feature | Indicadores técnicos e padrões de vela explicados no Como jogar | N25, N19 | D21 | M28 · 4.6 | [F158](#f158) | O molde do tópico em fases, quais indicadores entram primeiro e onde o 'i' abre o tópico sem cobrir a tela (F183). |
| **F194** | Feature | Dólar e ativos internacionais | N34, N11 | D20 | M26 · 4.4 | — | Como o dólar do jogo reage (desconfiança, juro real), a camada pelo desvio sobre BDR e IVVB11 e onde o seletor de origem aparece. |
| **F202** | Performance | Backtest que corre mais rápido que a partida comum | N10 | D8 | M25 · 4.3 | — | Medir o dia do backtest por etapa e escolher quais custos saem do caminho dele (eventos em memória gravados em lote, leituras do que o motor acabou de gravar, trava por pregão, imposto por dia) |
| **F211** | Melhoria | Livro de ofertas e ordens abertas do detalhe do ativo | N15 | — | M24 · 4.2 | — | o desenho do livro (variantes e estados no canvas) e se a ordenação por preço vem do backend |
| **F226** | Feature | Mercado reage à surpresa: o Focus da partida | N34, N31, N41 | D20 | M25 · 4.3 | — | Como a expectativa se forma, se o governo pode sinalizar, se o Focus entra na Central de dados e o que fica do efeito por tamanho do desvio |
| **F227** | Feature | Intensidade das ligações e laboratório da economia | N41, N34 | D20, D21 | M28 · 4.6 | — | Quais das três regras entram, se contam no placar e nas conquistas, se o laboratório mostra o coeficiente e o valor da credibilidade inicial desacreditada |
| **F232** | Correção | Crescimento que sente o rombo do governo | N34 | D20 | — | — | O que freia o crescimento (prêmio, inflação ou os dois), em que forma e de que tamanho |

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
**F158 — Animações do Como jogar revistas.** Serve N25; retrabalho da F126. No playtest, o tutorial pareceu estranho: o estilo das animações ficou parecido com o do Create, e o número do passo que aparece no meio da animação, num círculo ao lado do alvo (`StepMarker` em `tutorial/stage/stage-kit.tsx:144`, número vindo de `topic-illustration.tsx:57`, usado em `buy-stock.tsx` e `order-types.tsx`), polui a cena. O salto para o trecho do passo ao clicar numa etapa funciona bem e fica como está. Falta escolher o visual numa rodada no canvas: comparar as animações atuais com as primeiras, feitas no canvas a partir das Dicas e truques do Factorio, decidir se o número sai da cena (o passo ativo já fica destacado na lista) e o que muda no cursor e no destaque. **Palco do tutorial (avaliado em 03/11):** a captura mostra o palco com a tela inteira encolhida a uns 70%, então o texto de 12 px do livro de ofertas chega a uns 8 px, e o marcador do passo cobre o texto que aponta. O desenho do retrato (palco em tamanho real mostrando só o trecho que o passo explica, o marcador numa margem à esquerda com uma linha até o alvo e os passos numa fileira abaixo) é coerente e o usuário o reconhece como a direção, mas não vai ser implementado a partir desse board: entra na rodada de canvas dedicada desta F, com o método completo (variantes e estados).

<a id="f179"></a>
**F179 — Topbar que cabe com a corrida e o governo.** Serve N15. O controle de velocidade (`layouts/partial/topbar.tsx`) é largo: depois do selo de pausa vêm a data, o play e os cinco botões de velocidade (1×, 2×, 4×, 10× e 100×). Com a corrida pela meta, o governo, o Como jogar e o caixa na mesma linha, a topbar quebra. Hoje isso é um caso extremo; com as Gestoras, governo, gestora e corrida pela meta ligados juntos passam a ser o caso comum, e é lá que o desenho se decide. O desenho no canvas já inclui o layout com as Gestoras, então a topbar é resolvida na 4.1, depois da F44, e entra no app já certa para o conjunto. A topbar não quebra linha, então a variante em duas linhas fica fora. Das outras, o canvas compara: (a) a velocidade num botão só ("10×") que abre as opções; (b) a corrida e o governo como selos compactos, com o detalhe ao passar o mouse. A referência é 1920 de largura, e em 1366 nada pode quebrar; o estado de teste é corrida, governo e gestora ligados, pausa com o motivo mais longo e o x100 destacado. O selo de pausa já sai só com "Pausado" e o motivo numa dica no lote de correções da 3.4 (F217), pedido dos playtests de 31/out e 04/11. Sai daqui para Pendente com a variante escolhida.

<a id="f193"></a>
**F193 — Indicadores técnicos e padrões de vela explicados no Como jogar.** Serve N25 e N19. Hoje cada indicador técnico diz Compra, Venda ou Neutro, com um "i" de texto curto que não ensina a ler, e o "i" dos padrões de vela nem abre. A ideia do playtest de 31/out: um tópico por indicador no Como jogar, em fases: o que é e como se calcula; por que ele aponta compra ou venda; um caso em que acerta; as ressalvas, quando ele engana. O "i" do indicador abre o tópico na aba dele. O mesmo molde serve aos padrões de vela, junto do catálogo (F131). As ordens a mercado e limitada já têm o tópico "Ordem a mercado e limitada" (`tutorial/topics/order-types.tsx`), que mostra a limitada esperando o preço chegar ao limite, e ficam como estão.

<a id="f194"></a>
**F194 — Dólar e ativos internacionais.** Serve N34 e N11. Ideia do playtest de 31/out: a cotação do dólar no jogo, subindo com a desconfiança na moeda e caindo com o juro real alto, e os ativos internacionais andando junto. Na Central de dados, cada ativo ganha a origem, Nacional ou Internacional, num seletor de dois com bandeirinha, que aparece também na listagem.

Ponto de realismo: BDR e ETF de índice de fora (IVVB11) já carregam o dólar no preço histórico. O câmbio do jogo só pode entrar como camada por cima, a diferença entre o dólar da partida e o dólar real daquele dia, senão o câmbio conta duas vezes. A série real é a PTAX do Banco Central (série 1 do SGS), desde 1994.

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

<a id="f226"></a>
**F226 — Mercado reage à surpresa: o Focus da partida.** Serve N34, N31 e N41; condicionado por D20. Hoje a bolsa e o prêmio de risco reagem ao tamanho do desvio: cada ponto de SELIC acima da história tira 2,9% da bolsa, anunciado ou não. No mercado real o preço já carrega o esperado, e o que move é a surpresa: uma alta que todo mundo esperava mexe pouco, uma que ninguém esperava mexe muito. A ideia é a partida ter a própria pesquisa Focus (a do Banco Central reúne as projeções do mercado para IPCA, SELIC, PIB e câmbio): a da história é a série real, publicada desde 2001, e a da partida é ela mais o desvio que o governo causa. A bolsa e o prêmio passam a reagir à diferença entre o decidido e o esperado, e o jogador vê antes da reunião o que o mercado espera, como quem lê o noticiário. Conversa com os rumores antecipados, que também falam do que vai acontecer. **Falta definir:** (1) como a expectativa da partida se forma: o Focus real mais o desvio, uma regra adaptativa (segue o realizado com atraso) ou a projeção do próprio modelo; (2) se o governo pode sinalizar, com um comunicado do Copom que mexe na expectativa e cobra credibilidade se não for cumprido; (3) se a série do Focus entra na Central de dados como as outras; (4) o que acontece com o efeito por tamanho do desvio, já calibrado.

<a id="f227"></a>
**F227 — Intensidade das ligações e laboratório da economia.** Serve N41 e N34; condicionado por D20 e D21. Três regras da partida, no lobby, para quem quer aprender vendo o mecanismo. **Intensidade:** Suave, Real e Exagerada multiplicam o desvio de todas as ligações por 0,5, 1 e 2. Como o multiplicador age sobre "partida menos história", sem governo a partida continua sendo a história; a Exagerada serve para ver o efeito com clareza num mandato curto. **Laboratório:** cada ligação (curva de Phillips, reação do Banco Central, risco fiscal, juro real na inflação, PIB na bolsa, ciclo fiscal) liga e desliga, para ver o que cada uma faz sozinha, e o painel da Economia mostra quais estão desligadas. **Credibilidade inicial:** a partida começa com o Banco Central acreditado (100, o padrão) ou desacreditado, como o Brasil de 2002 ou de 2015. Desacreditado, ele já paga prêmio de risco no primeiro dia e precisa manter o juro real acima do da história para recuperar a confiança. A regra vale porque a credibilidade é medida contra a história: um banco desacreditado que só copia a história recupera a confiança devagar. **Falta definir:** (1) quais das três regras entram; (2) se a partida Exagerada, de laboratório ou com banco desacreditado conta no placar e nas conquistas; (3) se o laboratório só liga e desliga ou também mostra o coeficiente, que a D21 deixa na docs; (4) o valor da credibilidade inicial desacreditada e se ela vem de um ano real escolhido no lobby.

<a id="f232"></a>
**F232 — Crescimento que sente o rombo do governo.** Serve N34; condicionado por D20. Na calibragem de 10 anos, o presidente que dá reajuste real de 15% ao ano por 10 anos chega a um primário de −22,7% do PIB e mesmo assim cresce 8% ao ano, o teto do jogo (`MAX_GROWTH` em `backend/features/economy/growth.py`), em 78 de 120 meses, com o desemprego no piso de 4% em 81. O impulso fiscal (`IMPULSE` em `backend/features/economy/links.py`) empurra o PIB a cada piora do primário, e nada do outro lado segura o crescimento. Na economia real, um rombo desse tamanho sufoca o crescimento: o prêmio de risco e a inflação altos encarecem o crédito, as empresas param de investir e o governo tira espaço do setor privado, o chamado efeito expulsão. Só aparece em quem gasta sem limite por anos; as estratégias comuns fecharam plausíveis. **Falta definir:** (1) o que freia o crescimento: o prêmio de risco acima da história, a inflação acima da meta ou os dois; (2) se o freio é uma parcela nova do crescimento, ao lado do juro real, da bolsa, das obras e do impulso, ou um impulso que perde força com o prêmio alto; (3) o tamanho, calibrado por CLI com o roteiro do gastador que nunca para em `.claude/trabalho/economia/calibrate10.py`, sem mexer nos cenários que já fecharam.

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
| **F101** | Feature | Carteira separada do jogador | N23 | D9 | M18 · 4.1 | — | Alto | Alto | Médio | Médio |
| **F110** | Feature | Combinar estratégias | N4 | D8 | — | — | Médio | Médio | Médio | Bom |
| **F111** | Feature | Crédito para estratégias e bots | N4, N33 | D8 | — | — | Baixo | Baixo | Médio | Bom |
| **F167** | Feature | Notícias do ativo como marcadores no gráfico de preço | — | — | — | — | Baixo | Baixo | Médio | Bom |
| **F176** | Feature | Cadeiras do Congresso por região | N34 | D19 | — | — | Médio | Médio | Médio | Médio |
| **F249** | Manutenção | Núcleo do backend sem import de features | — | — | — | — | Alto | Médio | Médio | Médio |

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

<a id="f249"></a>
**F249 — Núcleo do backend sem import de features.** `core/` importa de `features/` em `user_manager`, `room_preparation`, `dependencies` e `tunnel_manager`, o inverso do que a pasta promete.

Cada um desses módulos é movido para a feature que o consome ou passa a receber a dependência por injeção (o `core` define o protocolo, a feature implementa). Por fora nada muda; confere-se com `uv run pyright`, `uv run pytest -n 4` e um `grep "features" backend/core` vazio. Sem decisão de fazer agora.

---

## ✅ Concluído

| ID | Tipo | Resumo | Serve | D# | Marco |
| --- | --- | --- | --- | --- | --- |
| **F233** | Manutenção | Constantes de calendário unificadas no core | — | — | M22 · 4.0 |
| **F234** | Manutenção | Juros compostos num módulo só | — | — | M22 · 4.0 |
| **F235** | Manutenção | Tipo Percent no indicador do BCB | — | — | M22 · 4.0 |
| **F236** | Manutenção | Prévia do impacto de preço fora da rota | — | — | M22 · 4.0 |
| **F237** | Manutenção | Componentes do mercado na pasta da renda variável | — | — | M22 · 4.0 |
| **F238** | Manutenção | Features do front sem import atravessado | — | — | M22 · 4.0 |
| **F239** | Manutenção | Formatadores de percentual unificados | — | — | M22 · 4.0 |
| **F240** | Manutenção | Badge de passo como variante do design system | — | — | M22 · 4.0 |
| **F241** | Manutenção | Card de ações de campanha em arquivos por parte | — | — | M22 · 4.0 |
| **F245** | Manutenção | Limpeza de scripts e docs | — | — | M22 · 4.0 |

<a id="f233"></a>
**F233 — Constantes de calendário unificadas no core.** Nasceu `backend/core/periods.py` com `BUSINESS_DAYS_PER_YEAR = 252` (movido de `core/indicators.py`), `CALENDAR_DAYS_PER_YEAR = Decimal("365.25")`, `MONTHS_PER_YEAR = 12` e `DAYS_PER_MONTH`, e a docstring afirma que dia útil é sessão da B3 e dia corrido é dia de calendário. O tesouro, as estatísticas (`risk`, `returns`, `score`), o gerador sintético, o futuro gerado, o orçamento de vida, os efeitos do governo e o crédito importam de lá; os cinco `MONTHS_PER_YEAR` e os dois `DAYS_PER_MONTH` locais saíram, e o literal `12` virou a constante. As janelas de "um ano de pregões" (`achievements/metrics.py`, `newsroom/companies.py` e `newsroom/newsroom.py`) usam `BUSINESS_DAYS_PER_YEAR`. O `synthetic.py` renomeou a régua de dias sem feriado para `WEEKDAYS_PER_YEAR` e a manteve local. `economy/layer.py` ganhou `months_to_days`, que converte meses em dias corridos no mês médio, e `statistics/risk.py` ganhou `VOLATILITY_ANNUALIZER` (√252) em Decimal. Ficaram como estavam as janelas ajustáveis que só coincidem com 252 (`strategy/momentum.py`, `base_strategy.py`) e o `MONTH_DAYS = 30` do crédito, que é outra convenção.

As regras da corrida à meta e de viver de renda, antes escritas duas vezes (no DTO e na requisição da rota), viraram `validate_goal` e `validate_independence` em `core/dto/simulation.py`, no padrão de `validate_government`; a requisição continua validando na entrada (422) e chama as mesmas funções do DTO.

Por fora nada mudou: os números exibidos são os mesmos, `pyright` e `pytest` passam sem nenhum valor esperado alterado.

<a id="f234"></a>
**F234 — Juros compostos num módulo só.** Nasceu `backend/core/rates.py`, só em Decimal, com `compound(rate, periods)` = (1+r)^n − 1, `period_rate(rate, periods)` = (1+r)^(1/n) − 1 e `compose(*rates)` = ∏(1+r) − 1, com teste próprio. Passam a chamá-las `credit/price.py` (taxa mensal e saldo do ciclo), `fixed_income/accrual.py` (`annual_to_daily_factor` virou `1 + period_rate(...)` e manteve o `lru_cache`; o spread composto virou `compose`), `economy/debt.py`, `government/budget.py` (a dívida e o PIB do mês), `simulation/life_events.py` (juro do cheque especial), `core/indicators.py` (`daily_rate` e `annualize_daily`) e `summaries/summary.py` (o composto dos meses, que tinha o seu `_compound`).

`annualize_growth` mudou de `statistics/returns.py` para `statistics/risk.py`, porque o `returns` já importa do `risk` e o `risk` precisava dela; o `returns` importa de lá e o `score.py` a chama como `risk.annualize_growth`. Com isso `risk.annual_return` e a nota anual do `score.py` deixaram de repetir a conta e o guarda de acumulado ≤ −100%. Os caminhos em float/numpy (`economy/layer.annual_to_daily` e os helpers do `synthetic.py`) ficaram com os helpers próprios; `to_annual` e `to_daily` do `synthetic.py` passaram a públicos e o `future.py` chama `to_annual` em vez de repetir a conta.

Por fora nada mudou: o resultado em Decimal é idêntico e nenhum valor esperado dos testes foi alterado.

<a id="f235"></a>
**F235 — Tipo Percent no indicador do BCB.** `Percent = NewType("Percent", Decimal)` e `from_percent(value: Percent) -> Decimal` moram em `core/rates.py`, com a afirmação de que o valor é como o BCB publica (0,0551 = 0,0551%). `index_value_on` devolve `Percent`; `daily_rate` e `annualize_daily` só aceitam `Percent`, e os `/ 100` de `core/indicators.py` e das tabelas de meta, tolerância, dívida bruta e resultado primário viraram `from_percent`. Como `last_known_value` também lê o IBOV, que é nível de índice em pontos, a leitura das taxas ganhou `last_known_rate` (CDI/SELIC/IPCA, devolve `Percent`) e `last_known_value` ficou só para as séries de nível; `accrual.py`, `economy/panel.py` e a checagem de cobertura migraram para `last_known_rate`. Onde a história é lida direto (`economy/panel.py`, `economy/layer.py`, `newsroom/macro.py`) o `Percent(...)` nasce na leitura, e os testes de `economy_layer` e `economy_panel` passam `Percent`. A chamada de prova com um `Decimal` cru em `annualize_daily` falhou no pyright e foi removida.

Por fora nada mudou: os valores são os mesmos; `pyright` e `pytest` passam sem nenhum valor esperado alterado.

<a id="f236"></a>
**F236 — Prévia do impacto de preço fora da rota.** A conta da curva saiu de `routes/simulation.py` e virou `preview_curve(k, decay_days)` em `features/variable_income/price_impact.py`, junto de `impact()` e `decay()`, levando `PREVIEW_VOLUME_SHARE` e o volume médio fixo do exemplo (`PREVIEW_AVERAGE_VOLUME`, 1 milhão). A função devolve o impacto de cada pregão afetado, e a rota só chama `preview_curve` e monta o `PriceImpactPreviewDTO`. Um teste novo confere `preview_curve` contra `impact()` e `decay()`.

Por fora nada mudou: a resposta da rota é a mesma e o `docs/openapi.json` não mudou.

<a id="f237"></a>
**F237 — Componentes do mercado na pasta da renda variável.** `market-mark.tsx` e `scale-ruler.tsx` saíram de `shared/components/` e foram para `features/variable-income/components/`, a única feature que os usa (`order-book-card.tsx` e `indicator-selector.tsx`). `chart-scale.ts` e `tutorial-topic-ids.ts` ficam em `shared/`, porque também têm consumidores lá.

Por fora nada mudou: só os caminhos de import.

<a id="f238"></a>
**F238 — Features do front sem import atravessado.** Os padrões de vela passaram a ser compartilhados: `candle-patterns.ts`, `pattern-geometry.ts`, `pattern-view.ts` (com o seu teste) foram para `shared/lib/`, e `pattern-drawing.tsx` com o `pattern-drawing-animated.tsx` que ele carrega foram para `shared/components/candle-patterns/`. A geometria e o desenho animado subiram junto porque o desenho depende deles e nenhum outro código os usa; assim `shared/` não importa de feature. O resto de `candle-patterns/` (cartão, lista, controles) ficou em variable-income.

O minigame de candles desceu para dentro do lobby, o único que o usa: `features/candle-challenge/` virou `features/lobby/candle-challenge/`, com `components/`, `hooks/` e `lib/` preservados. O `lobby-button.tsx` do tutorial desceu para `lobby/components/`.

Dentro de `features/`, a única aresta entre features que sobra é a do tutorial para variable-income, aceita como exceção.

<a id="f239"></a>
**F239 — Formatadores de percentual unificados.** `displayPercent` ganhou a opção `{ trim: true }`, que mostra casas só quando há (0,4 → "40%", 0,0025 → "0,25%"). O `chancePercent` do governo saiu e seus 4 usos viraram `displayPercent(x, 2, { trim: true })`; os três `formatPercent(Number(x) * 100, 1)` dos cards do mapa viraram `displayPercent(x, 1)`. O `formatPercent` ficou, porque é o formatador de pontos (52 = "52%"), unidade só do governo, e a docstring dele agora afirma isso.

Uma varredura das formatações à mão trocou mais cinco pontos por `displayPercent`: `percentLabel` (governo), o toast do 2º turno, `percentOf` do tesouro, as três linhas da ilustração de alavancagem do tutorial e `cashShare` do lobby. O texto exibido é o mesmo de antes.

Ficaram de fora, por não terem equivalente exato: `yearShare` (mínimo de 2 e máximo de 3 casas) e os formatadores de valores que já chegam na escala 0–100, ou sem o "%" (`pointsOf`, `signedPointsOf`, `pollPercent`, os de pontos percentuais do mapa).

<a id="f240"></a>
**F240 — Badge de passo como variante do design system.** O círculo numerado do `Step` em `pyspy-card.tsx` era um `Badge` reimplementado com classes inline. O `Badge` ganhou `size="step"` (`size-5.5 px-0 font-semibold`) em `badgeVariants.ts`, e o `Step` passou a `<Badge variant="secondary" size="step">`.

O círculo de `measure-steps.tsx` ficou de fora: é outro selo, maior (`size-7`), em tom de informação e com fonte mono, e não o mesmo círculo do py-spy.

<a id="f241"></a>
**F241 — Card de ações de campanha em arquivos por parte.** `campaign-actions-card.tsx` virou a pasta `campaign-actions-card/`, com `index.tsx` (o card e o subtítulo do dado) e um arquivo por parte: `action-body.tsx`, `tv-reach.tsx`, `action-choice.tsx`, `group-choices.tsx`, `group-poll-cell.tsx`, `summary-body.tsx`, `summary-row.tsx` e `summary-title.ts`, no padrão de `statistics-report/`. Quem importa o card continua com o mesmo caminho.

O rival antes era resolvido duas vezes, no card e no corpo da ação. Agora o `index.tsx` resolve uma vez e passa o `rival` pronto ao `ActionBody`, com o tipo tirado do `CampaignPanel`.

Por fora nada mudou.

<a id="f245"></a>
**F245 — Limpeza de scripts e docs.** Saíram `scripts/plot_beta_distribution.py`, `scripts/tree.py` e `scripts/tree_descriptions.yaml`, junto com a seção "Atualização da Árvore de Estrutura" de `docs/docs/desenvolvimento/estrutura-pastas.md`, que ensinava a rodá-los. Os scripts `profile:line` e `profile:line:view` saíram do `package.json`, e com eles `line-profiler` (`pyproject.toml`, exclude do `.spec`) e `cross-env`; os dois lockfiles foram regenerados e o deptry confirma. O padrão `*.lprof` saiu do script `clean`. Na docs de estrutura de pastas, o exemplo `base-card.tsx`, que não existe, passou a `shared/components/kpi.tsx`. O `matplotlib`, que só o `plot_beta_distribution.py` usava, continua no grupo `dev` do `pyproject.toml`.

---

## 🚫 Descartado

> Nenhum item neste status.
