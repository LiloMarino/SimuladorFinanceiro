<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-10-26):** Registrados os achados do playtest: correções no marco Partida sem tropeços, a eleição e o Congresso no marco Eleição e Congresso disputados, e a preparação de cada jogador no lobby.

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | [F22](#f22), [F100](#f100) | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F10](#f10), [F110](#f110), [F111](#f111), [F127](#f127), [F149](#f149) | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | — | — |
| **N6** | Comparar resultados de simulações diferentes | — | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | [F22](#f22), [F100](#f100) | — |
| **N8** | Jogar contra oponentes controlados pelo computador | [F146](#f146) | — |
| **N9** | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — |
| **N10** | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | — | — |
| **N11** | Que o cenário econômico simulado seja o histórico real | — | — |
| **N12** | Continuar jogando depois do último dia com dado real | — | — |
| **N13** | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | — |
| **N14** | Atualizar para uma versão nova sem perder as partidas salvas | [F56](#f56) | — |
| **N15** | Usar uma interface agradável e coerente, à altura de um jogo | [F37](#f37), [F72](#f72), [F134](#f134), [F144](#f144), [F149](#f149), [F155](#f155) | — |
| **N16** | Ver a carteira e o mercado por setor e segmento | — | — |
| **N17** | Enxergar a estrutura do banco e esboçar mudanças nela | — | — |
| **N18** | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — |
| **N19** | Analisar um ativo com as ferramentas de um trader | [F96](#f96) | — |
| **N20** | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | — |
| **N21** | Jogar "na unha", sem a interface apontar a melhor escolha | — | — |
| **N22** | Ter objetivos para buscar além de vencer a partida | [F122](#f122) | — |
| **N23** | Jogar com os amigos de outras formas além de cada um por si | [F69](#f69), [F101](#f101) | — |
| **N24** | Saber onde está a lentidão durante uma partida | — | — |
| **N25** | Entender o que é o simulador e como se joga, sem ler um manual | [F126](#f126), [F132](#f132), [F133](#f133), [F139](#f139), [F140](#f140), [F141](#f141) | — |
| **N26** | Achar a causa de um erro sem vasculhar o log inteiro | — | — |
| **N27** | Entrar numa partida que já começou | — | — |
| **N28** | Liberar uma vaga sem depender de o jogador sair | [F61](#f61) | — |
| **N29** | Saber o que cada jogador está fazendo enquanto a partida não começa | — | — |
| **N30** | Repetir uma configuração de partida sem montá-la de novo | — | — |
| **N31** | Saber o que está movendo o mercado da partida, como quem lê o noticiário | [F92](#f92) | — |
| **N32** | Saber como foi o mês sem montar a conta | [F91](#f91) | — |
| **N33** | Investir com dinheiro emprestado, pagando o juro do momento | [F111](#f111), [F148](#f148) | — |
| **N34** | Disputar o poder de mudar as regras da economia da partida | [F144](#f144), [F145](#f145), [F147](#f147), [F150](#f150) | — |
| **N35** | Tirar da lista as partidas que não interessam mais | — | — |
| **N36** | Encontrar rapidamente os menores e maiores valores nos dados do jogo | — | — |
| **N37** | Comprar bitcoin do jeito que dá na vida real, em frações | [F127](#f127) | — |
| **N38** | Saber quando as estatísticas vão mudar, sem achar que travaram | [F156](#f156) | — |
| **N39** | Chegar ao primeiro dia da partida com as próprias escolhas já feitas | — | — |
| **N40** | Jogar partidas longas e na velocidade máxima sem a tela travar | [F156](#f156) | — |
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
| [**F127**](#f127) | Estratégias e bots operam cripto em fração | — | 💤 |
| [**F128**](#f128) | Governo & Política: rever os impostos por setor | — | 🔍 |
| [**F129**](#f129) | Governo & Política: rever a aprovação do governo | — | 🔍 |
| [**F130**](#f130) | Governo & Política: rever os votos e a eleição | — | 🔍 |
| [**F131**](#f131) | Catálogo de padrões de vela | — | 🔍 |
| [**F132**](#f132) | Tópicos de "como se joga" do Como jogar | — | ⏳ |
| [**F133**](#f133) | Tópicos de conceitos do Como jogar | — | ⏳ |
| [**F134**](#f134) | Acabamentos das telas | — | ⏳ |
| [**F135**](#f135) | Tipos mais rígidos no frontend | — | ⏳ |
| [**F136**](#f136) | Código e dependências sem uso | — | ⏳ |
| [**F137**](#f137) | Acessibilidade das telas | — | ⏳ |
| [**F138**](#f138) | Piloto do modo strict do pyright | — | ⏳ |
| [**F139**](#f139) | Demonstração regravada com o jogo de hoje | — | ⏳ |
| [**F140**](#f140) | Docs reorganizada por tipo de leitor | — | ⏳ |
| [**F141**](#f141) | README com as features de hoje | — | ⏳ |
| [**F143**](#f143) | Preparação de cada jogador no lobby | — | 🔍 |
| [**F144**](#f144) | Ajustes de layout do playtest | — | ⏳ |
| [**F145**](#f145) | Convite de vice para qualquer jogador | — | ⏳ |
| [**F146**](#f146) | Bots "saindo" ao iniciar a partida | — | ⏳ |
| [**F147**](#f147) | Nome do presidente eleito aparecendo como null | — | ⏳ |
| [**F148**](#f148) | Empréstimo que não se deixa pagar com o jogador negativado | — | ⏳ |
| [**F149**](#f149) | Desligar o automático na própria boleta | — | ⏳ |
| [**F150**](#f150) | Aviso de abertura da campanha | — | ⏳ |
| [**F151**](#f151) | Segundo turno com disputa | — | 🔍 |
| [**F152**](#f152) | Promessas de campanha em texto | — | 🔍 |
| [**F153**](#f153) | Congresso eleito, com bancadas | — | 🔍 |
| [**F154**](#f154) | Negociar apoio com as bancadas | — | 🔍 |
| [**F155**](#f155) | Filtro "Na carteira" na renda fixa | — | ⏳ |
| [**F156**](#f156) | Estatísticas rápidas em partida longa | — | ⏳ |
| [**F157**](#f157) | Velocidade x100 que quase não acelera | — | 🔍 |
| [**F158**](#f158) | Animações do Como jogar revistas | — | 🔍 |

<details>
<summary><strong>Concluído / decidido / descartado (22 itens — clique pra expandir)</strong></summary>

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
| **D15** | Lint com oxlint, formatação com oxfmt e o TypeScript 7 com a API do 6 ao lado | — | ✅ |
| **D16** | Estratégias do app no host, personalização pela API | — | ✅ |
| **D17** | Os tópicos do tutorial se animam em código, com o motion | [F126](#f126) | ✅ |
| **D18** | Uma migration por versão; caminho antigo só cai numa major | [F142](#f142) | ✅ |
| [**F10**](#f10) | Guia de como escrever uma estratégia | — | ✅ |
| [**F96**](#f96) | Dicas de análise técnica | — | ✅ |
| [**F125**](#f125) | Revisão das regras de lint e da checagem de tipos | — | ✅ |
| [**F126**](#f126) | Janela "Como jogar" | — | ✅ |
| [**F142**](#f142) | Banco da 3.0: regras em JSON, conquistas preservadas e migrations por versão | — | ✅ |

</details>

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: as `F#` que podem ser pegas agora — toda dependência já ✅. "Destrava" é quantas `F#` em aberto esperam por ela, direta ou indiretamente; é por aí que a tabela está ordenada. 💤 (sem prioridade) e 🚫 não entram.

| ID | Resumo | Marco | Destrava | Status |
| --- | --- | --- | --- | --- |
| [**F5**](#f5) | Spike: provider de túnel pela internet | M3 | 2 | 🔍 |
| [**F22**](#f22) | Preço ajustado e proventos | M8 | 2 | ⏳ |
| [**F91**](#f91) | Caixa de entrada e resumo do mês | M15 | 2 | ⏳ |
| [**F106**](#f106) | Governo & Política: gasto público e inflação | — | 1 | 🔍 |
| [**F139**](#f139) | Demonstração regravada com o jogo de hoje | M14 | 1 | ⏳ |
| [**F153**](#f153) | Congresso eleito, com bancadas | M17 | 1 | 🔍 |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | M9 | 0 | 🔍 |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | M11 | 0 | 🔍 |
| [**F56**](#f56) | Novidades no app | — | 0 | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | 0 | ⏳ |
| [**F67**](#f67) | Abrir a pasta de configurações | — | 0 | ⏳ |
| [**F90**](#f90) | Cenários | — | 0 | 🔍 |
| [**F107**](#f107) | Perfis de público na eleição | M17 | 0 | 🔍 |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | 0 | 🔍 |
| [**F122**](#f122) | Novas conquistas para as features recentes e antigas | — | 0 | ⏳ |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 0 | 🔍 |
| [**F128**](#f128) | Governo & Política: rever os impostos por setor | — | 0 | 🔍 |
| [**F129**](#f129) | Governo & Política: rever a aprovação do governo | M17 | 0 | 🔍 |
| [**F130**](#f130) | Governo & Política: rever os votos e a eleição | M17 | 0 | 🔍 |
| [**F131**](#f131) | Catálogo de padrões de vela | M11 | 0 | 🔍 |
| [**F132**](#f132) | Tópicos de "como se joga" do Como jogar | M14 | 0 | ⏳ |
| [**F133**](#f133) | Tópicos de conceitos do Como jogar | M14 | 0 | ⏳ |
| [**F134**](#f134) | Acabamentos das telas | — | 0 | ⏳ |
| [**F135**](#f135) | Tipos mais rígidos no frontend | — | 0 | ⏳ |
| [**F136**](#f136) | Código e dependências sem uso | — | 0 | ⏳ |
| [**F137**](#f137) | Acessibilidade das telas | — | 0 | ⏳ |
| [**F138**](#f138) | Piloto do modo strict do pyright | — | 0 | ⏳ |
| [**F140**](#f140) | Docs reorganizada por tipo de leitor | M14 | 0 | ⏳ |
| [**F143**](#f143) | Preparação de cada jogador no lobby | — | 0 | 🔍 |
| [**F144**](#f144) | Ajustes de layout do playtest | M16 | 0 | ⏳ |
| [**F145**](#f145) | Convite de vice para qualquer jogador | M17 | 0 | ⏳ |
| [**F146**](#f146) | Bots "saindo" ao iniciar a partida | M16 | 0 | ⏳ |
| [**F147**](#f147) | Nome do presidente eleito aparecendo como null | M16 | 0 | ⏳ |
| [**F148**](#f148) | Empréstimo que não se deixa pagar com o jogador negativado | M16 | 0 | ⏳ |
| [**F149**](#f149) | Desligar o automático na própria boleta | M16 | 0 | ⏳ |
| [**F150**](#f150) | Aviso de abertura da campanha | M17 | 0 | ⏳ |
| [**F151**](#f151) | Segundo turno com disputa | M17 | 0 | 🔍 |
| [**F152**](#f152) | Promessas de campanha em texto | M17 | 0 | 🔍 |
| [**F155**](#f155) | Filtro "Na carteira" na renda fixa | M16 | 0 | ⏳ |
| [**F156**](#f156) | Estatísticas rápidas em partida longa | M16 | 0 | ⏳ |
| [**F157**](#f157) | Velocidade x100 que quase não acelera | M16 | 0 | 🔍 |
| [**F158**](#f158) | Animações do Como jogar revistas | M14 | 0 | 🔍 |

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
> **Progresso:** 1/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 |
| [**F131**](#f131) | Catálogo de padrões de vela | [F96](#f96), [F126](#f126) | 🔍 |

<details><summary>Concluído (1 item)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F96**](#f96) | Dicas de análise técnica | [F126](#f126) | ✅ |

</details>

### M14 — Vitrine e primeiros passos

> **Objetivo:** Ver o jogo funcionando antes de baixar e aprender a jogar vendo, não lendo.
>
> **Serve:** N25
>
> **Progresso:** 1/7 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F132**](#f132) | Tópicos de "como se joga" do Como jogar | [F126](#f126) | ⏳ |
| [**F133**](#f133) | Tópicos de conceitos do Como jogar | [F126](#f126) | ⏳ |
| [**F139**](#f139) | Demonstração regravada com o jogo de hoje | — | ⏳ |
| [**F140**](#f140) | Docs reorganizada por tipo de leitor | — | ⏳ |
| [**F141**](#f141) | README com as features de hoje | [F139](#f139) | ⏳ |
| [**F158**](#f158) | Animações do Como jogar revistas | [F126](#f126) | 🔍 |

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

### M16 — Partida sem tropeços

> **Objetivo:** Repetir uma partida com amigos, do lobby ao fim, sem os erros e as travas que o playtest mostrou.
>
> **Serve:** N4, N8, N15, N33, N34, N40
>
> **Progresso:** 0/8 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F144**](#f144) | Ajustes de layout do playtest | — | ⏳ |
| [**F146**](#f146) | Bots "saindo" ao iniciar a partida | — | ⏳ |
| [**F147**](#f147) | Nome do presidente eleito aparecendo como null | — | ⏳ |
| [**F148**](#f148) | Empréstimo que não se deixa pagar com o jogador negativado | — | ⏳ |
| [**F149**](#f149) | Desligar o automático na própria boleta | — | ⏳ |
| [**F155**](#f155) | Filtro "Na carteira" na renda fixa | — | ⏳ |
| [**F156**](#f156) | Estatísticas rápidas em partida longa | — | ⏳ |
| [**F157**](#f157) | Velocidade x100 que quase não acelera | — | 🔍 |

### M17 — Eleição e Congresso disputados

> **Objetivo:** Uma eleição que todos percebem começar, com 2º turno disputado, promessas visíveis e um Congresso eleito que pesa em cada votação.
>
> **Serve:** N34
>
> **Progresso:** 0/9 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F107**](#f107) | Perfis de público na eleição | — | 🔍 |
| [**F129**](#f129) | Governo & Política: rever a aprovação do governo | — | 🔍 |
| [**F130**](#f130) | Governo & Política: rever os votos e a eleição | — | 🔍 |
| [**F145**](#f145) | Convite de vice para qualquer jogador | — | ⏳ |
| [**F150**](#f150) | Aviso de abertura da campanha | — | ⏳ |
| [**F151**](#f151) | Segundo turno com disputa | — | 🔍 |
| [**F152**](#f152) | Promessas de campanha em texto | — | 🔍 |
| [**F153**](#f153) | Congresso eleito, com bancadas | — | 🔍 |
| [**F154**](#f154) | Negociar apoio com as bancadas | [F153](#f153) | 🔍 |

### Sem marco

> **Progresso:** 2/34 concluídas

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
| [**F110**](#f110) | Combinar estratégias | — | 💤 |
| [**F111**](#f111) | Crédito para estratégias e bots | — | 💤 |
| [**F120**](#f120) | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | — | 🔍 |
| [**F122**](#f122) | Novas conquistas para as features recentes e antigas | — | ⏳ |
| [**F123**](#f123) | Redesenhar o aviso de conquista desbloqueada | — | 🔍 |
| [**F127**](#f127) | Estratégias e bots operam cripto em fração | — | 💤 |
| [**F128**](#f128) | Governo & Política: rever os impostos por setor | — | 🔍 |
| [**F134**](#f134) | Acabamentos das telas | — | ⏳ |
| [**F135**](#f135) | Tipos mais rígidos no frontend | — | ⏳ |
| [**F136**](#f136) | Código e dependências sem uso | — | ⏳ |
| [**F137**](#f137) | Acessibilidade das telas | — | ⏳ |
| [**F138**](#f138) | Piloto do modo strict do pyright | — | ⏳ |
| [**F143**](#f143) | Preparação de cada jogador no lobby | — | 🔍 |

<details><summary>Concluído (2 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F125**](#f125) | Revisão das regras de lint e da checagem de tipos | — | ✅ |
| [**F142**](#f142) | Banco da 3.0: regras em JSON, conquistas preservadas e migrations por versão | — | ✅ |

</details>

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
| **F96** | Dicas de análise técnica | N19 | — | M11 | [F126](#f126) | Médio | Baixo | Médio | Bom | ✅ Concluído |
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
| **F134** | Acabamentos das telas | N15 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F139** | Demonstração regravada com o jogo de hoje | N25 | — | M14 | — | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F140** | Docs reorganizada por tipo de leitor | N25 | — | M14 | — | Alto | Baixo | Alto | Bom | ⏳ Pendente |
| **F141** | README com as features de hoje | N25 | — | M14 | [F139](#f139) | Baixo | Baixo | Alto | Excelente | ⏳ Pendente |
| **F144** | Ajustes de layout do playtest | N15, N34 | — | M16 | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F145** | Convite de vice para qualquer jogador | N34 | — | M17 | — | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F146** | Bots "saindo" ao iniciar a partida | N8 | — | M16 | — | Baixo | Baixo | Baixo | Bom | ⏳ Pendente |
| **F147** | Nome do presidente eleito aparecendo como null | N34 | — | M16 | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F148** | Empréstimo que não se deixa pagar com o jogador negativado | N33 | — | M16 | — | Médio | Médio | Alto | Excelente | ⏳ Pendente |
| **F149** | Desligar o automático na própria boleta | N4, N15 | — | M16 | — | Baixo | Baixo | Médio | Excelente | ⏳ Pendente |
| **F150** | Aviso de abertura da campanha | N34 | — | M17 | — | Baixo | Baixo | Alto | Excelente | ⏳ Pendente |
| **F155** | Filtro "Na carteira" na renda fixa | N15 | — | M16 | — | Baixo | Baixo | Médio | Excelente | ⏳ Pendente |
| **F156** | Estatísticas rápidas em partida longa | N40, N38 | — | M16 | — | Médio | Médio | Alto | Bom | ⏳ Pendente |

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
**F96 — Dicas de análise técnica.** Serve N19. Aprender análise técnica jogando: o gráfico de velas aponta e explica o que um trader enxergaria. É ajuda, então o modo Especialista (F40) a desliga, como as outras, com um interruptor próprio (Esconder dicas de análise técnica). (1) Padrões de vela: 11 padrões clássicos detectados por regras fixas (martelo, martelo invertido, enforcado, estrela cadente, doji, engolfo de alta e de baixa, estrela da manhã e da tarde, três soldados brancos e três corvos negros). Marcador com o nome sobre a vela, faixa atrás dos padrões de várias velas, interruptor "Padrões de vela" no topo do gráfico, lista recolhível dos padrões do período e card "E se ele acertou?" ao passar o mouse, com o desenho animado do padrão, o contorno dos 5 pregões seguintes e a taxa de acerto (só com 10 ocorrências ou mais). (2) Indicadores (F33): legendas "Sobrecomprado"/"Sobrevendido" no IFR e círculo com frase nos cruzamentos do MACD e das médias móveis. (3) Desafio da vela: quando surge um padrão com lado, o jogo pergunta "sobe ou desce?" e confere no fechamento do 5º pregão, com placar, cartão no fim da partida e as conquistas Primeira leitura e Leitor de velas. O preset Realista passou a esconder as dicas, para o rótulo Especialista continuar valendo.

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

<a id="f134"></a>
**F134 — Acabamentos das telas.** Serve N15. Ajustes pequenos que as telas implementadas deixaram de fora do desenho aprovado e que hoje só existem como post-its azuis no canvas, conferidos no código em 25/out. Cada item é uma troca local, sem rota nem modelo novos, e a referência visual é o board da linha no canvas. **Estatísticas:** o melhor da sala em verde na aba Geral, como em Rentabilidade e Risco (`statistics-report/overview-tab.tsx`, padrão em `risk-tab.tsx`); o caixa com cor própria no resumo "caixa · RV · RF" da Composição (`composition-tab.tsx`). **Fim de partida:** texto próprio para a partida só com você e, no viver de renda, a frase "passou por N imprevistos" (`match-result/match-hero.tsx`). **Página Meta:** rodapé "Juros pagos na partida" no histórico. **Lobby:** título "Continuar · nome da partida" e selo do tipo de partida na tela de entrada em equipes (`lobby-match.tsx`); a linha "Expansões" no diálogo de salvar preset (`preset-bar.tsx`, com o rótulo que `lobby/lib/preset.ts` já tem); legenda "dias sem dado" no calendário das datas (`ui/calendar.tsx`). **Modo Especialista:** erro ao salvar com "Tentar de novo" e o interruptor voltando ao valor anterior, esqueleto nas Assistências enquanto carregam e a contagem "N de M ligadas" no card da sala também fora do Personalizado (`rules-sheet.tsx`, `assistance-fields.tsx`); o clique no interruptor com Personalizado ligado segue o board, que pede a confirmação na sessão antes do código. **Correlação:** a linha que lê o par fixado no painel, o erro sem a linha técnica e a célula sem dado listrada com a causa (`correlation-side-panel.tsx`, `correlation-tool.tsx`). **Configurações:** duas colunas em qualquer largura e o erro ao salvar em vermelho suave (`settings.tsx`, `notifications-card.tsx`). **Sistema:** a nota de 12 px abaixo dos botões no 404 (`pages/error.tsx`). **Central de dados:** "buscando…" na sugestão enquanto o yFinance responde (`ticker-combobox.tsx`) e a mensagem de arquivo que não é CSV citando vírgula ou ponto e vírgula (`csv-file.ts`). **Governo:** a coluna "Hoje" do card de impostos alinhada à direita (`taxes-card.tsx`). **Backtest:** "Bateram o CDI" com o percentual ao lado da amostra e o selo Backtest no seletor de Comparar simulações (`compare/simulation-picker.tsx`). **Crédito:** o aviso "O automático está ligado" no Revisar e assinar, com o `TradeLockNotice` das boletas. **Indicadores técnicos:** a régua de 0 a 100 na dica ⓘ dos indicadores de escala fixa (IFR, Estocástico), marcando onde está o valor de hoje (`indicator-selector.tsx`, dica em `metric-hint`). **Dicas de análise técnica:** o cartão do minigame no fim da partida em cinza (`candle-challenge-card.tsx`). Ao terminar, os post-its azuis desses itens saem do canvas na sincronização.

<a id="f139"></a>
**F139 — Demonstração regravada com o jogo de hoje.** Serve N25; retrabalho da F47 e da F48. A última publicação do branch `demo` é de 2026-10-21, e de lá para cá entraram dezenas de features que a demonstração não mostra: modo automático com estratégias e bots na sala, backtest, crédito, governo e eleição, cripto, indicadores técnicos e dicas de análise técnica, presets e linha do tempo do período no lobby, compra a mercado por valor na boleta, a janela "Como jogar". Plano: (1) **Inventário:** cruzar o `git log` de `frontend/src` desde a última publicação com as cenas de `scripts/demo/script.py` (lobby, ações, renda fixa, tempo, estatísticas, fechamento) e as screenshots de `docs/static/demo/screens/`, listando cena por cena o que mudou na tela e o que não tem imagem. (2) **Cenas que mudaram:** o lobby passa pelo preset e pela linha do tempo; a cena de ações usa a compra por valor e mostra o gráfico com um indicador ligado. (3) **Cenas novas:** uma do modo automático (escolher a estratégia e ver o bot negociar) e screenshots de crédito, governo, análise técnica, backtest e "Como jogar"; o banco-base da demo ganha o que essas telas precisarem (um ativo cripto, os indicadores do governo). (4) **Página das imagens:** cada screenshot nova ganha o nome que a página dos docs vai usar, e a lista de screenshots esperadas fica no próprio roteiro, para a reorganização da docs (F140) pedir imagem acrescentando uma linha. (5) `pnpm demo` e `pnpm demo publish`. Gatilho: agora; destrava o README (F141).

<a id="f140"></a>
**F140 — Docs reorganizada por tipo de leitor.** Serve N25; retrabalho da F48. As páginas cresceram junto com as features e misturam três leituras: o passo a passo de quem joga, a referência campo a campo e a explicação de como o simulador calcula (o lobby tem 3 mil palavras e uma seção "Como funciona internamente"; estatísticas e futuro gerado carregam a metodologia inteira no meio do guia). "Novidades" mora dentro de "Como Usar", o "Desenvolvimento" põe o setup lado a lado com notas internas (async × sync, investigação de lentidão, cotações em lote, ordenação de tabelas), e há features sem página para quem joga (modo automático e backtest só aparecem em `desenvolvimento/estrategias.md`; a janela "Como jogar" não aparece em lugar nenhum); a intro e o README ainda dizem "Estratégias automáticas: em breve". Guia de escrita: o Diátaxis (https://diataxis.fr), que separa tutorial (aprender fazendo), guia prático (resolver uma tarefa), referência (consultar) e explicação (entender o porquê). Plano: (1) **Auditoria** página por página contra o app de hoje: o que está desatualizado, o que falta e de qual dos quatro tipos é cada seção, numa tabela entregue ao usuário com a barra lateral proposta antes de mover arquivo. (2) **Barra lateral nova:** "Primeiros passos" (instalação e uma primeira partida curta, apoiada no tour), "Como usar" com uma página curta por tela dizendo o que dá para fazer nela, "Referência" (os campos do lobby, as regras de imposto, os tipos de ordem) e "Como funciona" (a nota da partida, o futuro gerado, o governo, a correlação), para onde a metodologia sai do meio dos guias. "Novidades" vai para a barra superior, ao lado da API. (3) **Desenvolvimento:** o caminho de quem contribui (setup, estrutura de pastas, convenções, contribuindo, versionamento) separado das notas internas, num subgrupo próprio. (4) **Páginas novas:** modo automático e bots na sala, backtest, e a menção à janela "Como jogar" na primeira partida. (5) **Tom:** caixa-alta, negrito em sequência, avisos em excesso e seções "Próximos passos" saem; cada página abre dizendo para que serve a tela, e toda métrica ganha a definição curta e um exemplo numérico. (6) Os links do README, do app (link de ajuda da sala) e entre páginas são conferidos depois de mover, com o build do Docusaurus, que já falha em link quebrado entre páginas (`onBrokenLinks`); os links de fora (README e app) são conferidos à mão. As imagens que faltarem entram no roteiro da demonstração (F139). Gatilho: agora; a auditoria do passo 1 não depende da regravação.

<a id="f141"></a>
**F141 — README com as features de hoje.** Serve N25; retrabalho da F48. O README lista o que o jogo fazia em 2026-10-21 e termina em "Estratégias automáticas: em breve", que já existe. Plano: (1) "O que ele faz" ganha modo automático com estratégias e bots, crédito, governo e eleição, cripto e análise técnica, cada um com uma frase e a imagem da demonstração regravada (F139); as seções com GIF ficam nas quatro ou cinco mais fortes, e o resto vai para "E também", que deixa de ter item "em breve". (2) O parágrafo de abertura e os tipos de partida conferidos contra o lobby de hoje (presets, período). (3) Os links para os docs apontam para as páginas da reorganização (F140) quando ela tiver mudado os caminhos. (4) A intro dos docs repete a mesma lista, e as duas mudam juntas. Gatilho: F139 publicada.

<a id="f144"></a>
**F144 — Ajustes de layout do playtest.** Serve N15 e N34. Três trocas locais, sem rota nem modelo novos. (1) **Aba Expansões do lobby:** os cards ficam estreitos porque o grid divide a aba em duas colunas a partir do `sm` e o card de dentro divide de novo (`expansion-fields.tsx:53` e `:111`); o card passa a ocupar a largura da aba, com as opções internas em duas colunas só em telas largas. (2) **Sigla do partido:** hoje vai de 2 a 5 letras maiúsculas, no DTO (`core/dto/government.py:20` e `:33`), no `government_book.py:211` e no formulário (`found-party-dialog.tsx:28`, `:32` e `:108`); o teto sobe para 8 letras nos três lugares, e os lugares que mostram a sigla (selo do partido, pesquisa, resultado do turno, topbar do governo) são conferidos com uma sigla de 8. (3) **Rentabilidade por jogador:** em partida longa, a aba (`statistics-report/returns-tab.tsx`, título em `:339`) estoura a largura da tela; o conteúdo largo ganha rolagem própria dentro do card e a página fica sem rolagem horizontal.

<a id="f145"></a>
**F145 — Convite de vice para qualquer jogador.** Serve N34. Hoje o vice sai de um `Select` com os filiados do partido (`ticket-dialog.tsx:81`), e o backend recusa quem não é filiado (`government_book.py:311`); o convite e o aceite já existem (`government_book.py:343`, `vice-invite-dialog.tsx`). Plano: (1) **Regra:** o vice pode ser qualquer jogador humano da sala, de outro partido ou sem partido, como numa coligação, e continua filiado ao próprio partido. Fica bloqueado quem já é vice de outra chapa, quem é candidato de alguma chapa e os bots. (2) **Quem convida:** o `Select` vira uma lista de todos os jogadores, com o partido de cada um, e os bloqueados aparecem desabilitados com o motivo ("já é vice do ABC", "candidato pelo XYZ"). (3) **Quem é convidado:** um aviso que se abre na tela dele, pelo Socket.IO, com aceitar e recusar, reaproveitando o `vice-invite-dialog.tsx`; quem convida vê o convite como pendente até a resposta. (4) **Efeitos:** no impeachment, assume o vice enquanto ele estiver na partida, sem exigir filiação; na vitória política, o vice soma para o próprio partido. Esse aviso de aceitar ou recusar é o mecanismo que a negociação com as bancadas (F154) reaproveita.

<a id="f146"></a>
**F146 — Bots "saindo" ao iniciar a partida.** Serve N8. Ao começar a partida, o log mostrou "Tio Patinhas saiu da sala". O início chama `release_bots` (`simulation_loader.py:58` e `:132`), que tira os bots da sala com `_take_out_bots(park=False)` (`user_manager.py:848`) e emite a saída de cada um pelo mesmo `_emit_player_exit` da saída de verdade; o front transforma isso no aviso de saída (`GlobalNotifications.tsx:54`). Plano: separar a liberação do lobby, que acontece no início, da remoção do bot, e emitir a saída só na remoção (`remove_bot`, `user_manager.py:789`), para o bot passar do lobby à partida sem aviso. Teste: iniciar uma partida com bot na sala e conferir que nenhum evento de saída é emitido.

<a id="f147"></a>
**F147 — Nome do presidente eleito aparecendo como null.** Serve N34. No playtest, o anúncio do resultado mostrou "null" no lugar do jogador eleito. Os pontos que montam o nome: o resultado do turno usa o nome do candidato, com o nome do partido como reserva (`round-result-dialog.tsx:79`), a posse mostra só a sigla (`government-notifications.tsx:101`) e o evento de tempo real tem `party_abbr` e `winner_abbr` opcionais, sem o nome do jogador (`realtime/schemas.py:199`). Plano: reproduzir na partida salva do playtest até o resultado; achar qual campo chega nulo (o caso provável é o candidato que saiu da sala, sem apelido no `user_manager`); levar o nome do eleito no próprio evento, gravado no momento da apuração, para o texto não depender de o jogador estar online; e mostrar "o candidato do ABC" quando a chapa não tiver candidato.

<a id="f148"></a>
**F148 — Empréstimo que não se deixa pagar com o jogador negativado.** Serve N33. No playtest, um jogador negativado com R$ 20 mil em caixa não conseguiu pagar um empréstimo que a tela mostrava como "Pagar R$ 13 mil", e o console falava em empréstimo infinito. O `logs/error.log` de 25/out tem a pista: a simulação de empréstimo (`routes/credit.py:41`, `features/credit/overview.py:355`) quebra com `leverage_after = Infinity`, porque a alavancagem (dívida ÷ patrimônio) divide por um patrimônio líquido zero ou negativo. O resumo da tela já trata esse caso (`overview.py:296`, nulo quando o patrimônio não é positivo); a simulação e as linhas `:193` e `:375` não. Plano: (1) alavancagem com patrimônio ≤ 0 vira "sem limite" (nulo no DTO e "—" na tela) em todo lugar que a calcula, com teste para patrimônio zero e negativo; (2) abrir a partida salva do playtest e refazer o pagamento, para confirmar se a recusa vinha desse erro (a tela de Crédito quebrando por causa dele) ou do `_require_cash` (`credit_book.py:681`), que compara o valor com o caixa; (3) se for o caixa, conferir de onde sai o valor do botão e o caixa usado na conferência, que precisam ser o mesmo número. **Aceite:** na partida salva, o jogador negativado paga a parcela com o caixa que tem.

<a id="f149"></a>
**F149 — Desligar o automático na própria boleta.** Serve N4 e N15. Com o automático ligado, a boleta fica travada (`order-ticket.tsx:72`, `inert` em `:156`) e o aviso manda o jogador para Estratégias (`trade-lock-notice.tsx`, link "Ir para Estratégias"); para comprar uma ação na mão, ele sai da tela, desliga lá e volta. Plano: o aviso ganha o botão "Desligar o automático", que chama a mesma mutation da página de Estratégias e, com sucesso, destrava a boleta ali mesmo, mantendo ativo, lado, quantidade e preço preenchidos; o link para Estratégias continua para quem quer trocar a estratégia. A troca vale para todo lugar que usa o `useTradeLock`, como a renda fixa.

<a id="f150"></a>
**F150 — Aviso de abertura da campanha.** Serve N34. A campanha abre sem aviso (1 ano antes do 1º turno, ou no início da partida), e no playtest ninguém percebeu a tempo de fundar partido, se filiar ou mudar a contribuição. Plano: no dia da abertura, um evento `campaign_opened` pausa a partida, como já fazem o resultado de turno e o impeachment, e abre para todos um aviso com a data do 1º turno, o dia em que as chapas fecham e atalhos para Fundar partido, Filiar-se e Contribuição. Dois lembretes sem pausa, como toast: alguns dias antes de as chapas fecharem e na véspera do 1º turno. Quando a caixa de entrada (F91) existir, cada aviso também vira uma entrada da sala; o aviso não espera por ela.

<a id="f155"></a>
**F155 — Filtro "Na carteira" na renda fixa.** Serve N15. A renda variável já tem o filtro "Na carteira · N" (`variable-income.tsx:16`, `:51` e `:126`); a renda fixa não (`fixed-income.tsx`, filtros de índice, tipo, isentos e liquidez em `:74` a `:87` e `:320` a `:334`), e para ver os títulos que tem o jogador desce até o fim da Carteira. Plano: o mesmo filtro, com a contagem, na barra de filtros da renda fixa, cruzando os títulos da lista com as posições de renda fixa da carteira; com o filtro ligado, cada linha mostra também o valor aplicado. O filtro da renda variável existe e passou despercebido no playtest: vale conferir se ele está à vista.

<a id="f156"></a>
**F156 — Estatísticas rápidas em partida longa.** Serve N40 e N38. A tela demora a abrir em partida longa, e o backend explica: as rotas de `/api/statistics/*` (`routes/statistics.py:39` a `:155`) leem todos os snapshots diários de todos os jogadores, sem recorte de data (`core/repository/statistics.py:32` e `:54`), e recalculam tudo a cada pedido. Como as estatísticas só mudam na virada do mês, o plano é: (1) medir com o painel de desempenho, numa partida salva longa, quanto vai na leitura e quanto no cálculo; (2) guardar o relatório do mês fechado em memória, por simulação, e devolver o guardado até a próxima virada; (3) nos gráficos de série, mandar um ponto por semana ou por mês quando o período passa de um ano, em vez de um por dia útil. **Aceite:** numa partida de 10 anos com 4 jogadores, a aba Geral abre em menos de 1 segundo.

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F60** | Modo servidor dedicado (--headless) | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F67** | Abrir a pasta de configurações | — | — | — | Baixo | Baixo | Médio | Excelente | ⏳ Pendente |
| **F81** | CORS restrito à mesma origem | — | — | [F6](#f6) | Baixo | Médio | Baixo | Médio | 💤 Registrado, sem prioridade |
| **F125** | Revisão das regras de lint e da checagem de tipos | — | — | — | Médio | Baixo | Médio | Bom | ✅ Concluído |
| **F135** | Tipos mais rígidos no frontend | — | — | — | Alto | Médio | Médio | Médio | ⏳ Pendente |
| **F136** | Código e dependências sem uso | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F137** | Acessibilidade das telas | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F138** | Piloto do modo strict do pyright | — | — | — | Médio | Baixo | Baixo | Médio | ⏳ Pendente |
| **F142** | Banco da 3.0: regras em JSON, conquistas preservadas e migrations por versão | D18 | — | — | Alto | Médio | Alto | Bom | ✅ Concluído |

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

<a id="f60"></a>
**F60 — Modo servidor dedicado (`--headless`).** O mesmo executável, sem o navegador: para rodar numa VPS ou num PC ligado direto, sem ninguém jogando nele. `--headless` na linha de comando, ou `[server] headless = true` no `config.toml`, pula o `webbrowser.open` do `main.py`, que hoje roda sempre que o app é o executável, e imprime no terminal os endereços para entrar (o da rede local e, com a F6, o do túnel). O administrador é quem entra com o apelido de `[host] nickname`, que é como o host é definido hoje (`routes/simulation.py`). Como a recuperação de login é por apelido, num servidor exposto à internet qualquer um que digite esse apelido viraria o host; por isso, no modo servidor, o `config.toml` ganha `[host] pin`, e o login com o apelido do host só passa com ele. Serve a quem quer deixar uma sala aberta para os amigos entrarem quando quiserem, sem depender de o host estar com o computador ligado jogando.

<a id="f67"></a>
**F67 — Abrir a pasta de configurações.** O executável guarda `config.toml`, `.env` e `logs` na pasta de dados do usuário (`%LOCALAPPDATA%\SimuladorFinanceiro` no Windows), que o Windows esconde. Em vez de mudar os arquivos de lugar, a tela de configurações ganha o botão "Abrir pasta de configurações", como o "abrir pasta de mods" de vários jogos. (1) **Rota** `POST /api/settings/open-folder` em `routes/settings.py`, protegida por `verify_host` e que só aceita requisição vinda do próprio computador (`request.client.host` em `127.0.0.1` ou `::1`): o servidor também atende a rede local, e um convidado não pode abrir janelas na máquina do host. (2) **Abertura** da pasta de `app_files_dir()` com `os.startfile` no Windows, `open` no macOS e `xdg-open` no Linux, por `subprocess` sem shell. (3) **Sem interface gráfica** (servidor dedicado, Linux sem `xdg-open`) ou pedido fora do computador do host: a rota responde 409 com o caminho, e o front o mostra num campo com botão "Copiar". O caminho aparece sempre ao lado do botão, então o jogador também o encontra sem abrir nada. (4) Um segundo botão, "Abrir pasta de logs", usa a mesma rota com `target=logs`. Um aviso junto aos botões diz que `db` e `postgres` são do banco e não devem ser editados. Teste: a rota recusa quem não é o host e quem vem de outro IP, e chama o abridor do sistema (substituído por um dublê) com a pasta certa. Não serve nenhuma necessidade listada: o ganho é achar o `config.toml` sem caçar uma pasta oculta.

**Aceite:** no executável do Windows aberto por duplo clique, o botão abre o Explorer na pasta que contém o `config.toml`; um convidado da rede local que chama a rota recebe 403.

<a id="f81"></a>
**F81 — CORS restrito à mesma origem.** O backend libera CORS para qualquer origem com credenciais (`allow_origins=["*"]` e `allow_credentials=True` no FastAPI, `cors_allowed_origins="*"` no Socket.IO). Não é necessário: o front é servido pelo próprio backend e, no `pnpm dev`, chega pelo proxy do Vite. Hoje o que protege o jogador de um site malicioso aberto durante a partida é o cookie `client_id` com `SameSite=Lax`, que o navegador não manda em requisição de outro site; o CORS liberado só deixa outro site ler as rotas que não pedem identidade. (1) Sai o `CORSMiddleware` de `main.py`. (2) O Socket.IO fica com `cors_allowed_origins` na mesma origem, mais `http://localhost:5173` quando o modo debug estiver ligado: o proxy do Vite troca o `Host` (`changeOrigin: true`) mas mantém o `Origin` do Vite, e o Socket.IO recusaria a conexão em dev sem essa exceção. (3) Teste manual antes de fechar: jogo pelo `localhost`, por outro computador da LAN pelo IP e pelo `pnpm dev`. Gatilho: junto com o link de convite pela internet, quando o servidor passa a ficar exposto fora da LAN.

<a id="f125"></a>
**F125 — Revisão das regras de lint e da checagem de tipos.** Cada candidata foi medida rodando a ferramenta no código atual e julgada regra a regra, não pela categoria inteira: fica o que aponta bug, código morto ou risco de segurança; saem reescrita de estilo e falso positivo. Toda regra ligada é erro, porque o pyright e o oxlint saem com código 0 em aviso e o aviso se acumularia.

**Ruff.** `ERA` (código comentado, 0 achados). `DTZ` (data sem fuso): o app grava `datetime.now(UTC)` e o banco usa `DateTime(timezone=True)`, então misturar data com e sem fuso é bug; os 5 `noqa` são de data local do app. `PLE` (erros que o Python só mostra ao executar, 0). `PLW` menos `PLW0603` (os `global` são caches de módulo) e `PLW0108` (o lambda do `monkeypatch` adia a busca do nome): pegou 2 `subprocess.run` sem `check` e uma variável de `for` reescrita. `S` (segurança) menos `S311` (o `random` é do jogo, não de criptografia), `S603` e `S607` (os `subprocess` chamam comandos fixos): os 15 achados eram de propósito (SQL montado nas migrations, `urlopen` do BCB, bind em `0.0.0.0` para a rede local) e levam `noqa` com o motivo. `LOG` (2 `logger.exception` fora de `except`, que podem sair sem traceback). `PGH` (11 `# type: ignore` sem código, que escondem erro novo na mesma linha). `FAST` (6: `Annotated` nas dependências e `response_model` redundante). `BLE` (4 `except Exception`, todos de propósito: erro de estratégia de terceiro devolve o jogador ao manual). Do `PT`, só a `PT011` (2 `pytest.raises` sem `match`, que passam pelo motivo errado). O lint também roda `ruff format --check` (os recortes de código dos guias em Markdown ficam fora).

**Asserts.** O executável é empacotado com `optimize=2`, que apaga docstrings e `assert`. Os 45 `assert` do backend viraram `required()` (`backend/core/utils`), que levanta erro também no executável, ou `if`/`raise` explícito onde a checagem não é de `None` (tipo de parâmetro de estratégia, quantidade zero numa ordem). A `S101` vale no backend e libera `tests/` e `scripts/`.

**pyright.** Modo `standard`. `reportUnusedFunction` e `reportUnnecessaryComparison` são erro. `reportUnnecessaryTypeIgnoreComment` (9 dos 11 `# type: ignore` sem código e 19 dos com código estavam mortos) e `reportDeprecated` (`Iterator` trocado por `Generator` nos `@contextmanager`) estão ligados. Ficam fora `reportUnnecessaryIsInstance` (1 achado, validação de fronteira em `base_strategy.py`) e `reportUnnecessaryCast` (3, casts do pandas, cuja inferência muda com a ordem em que o pyright avalia os arquivos).

**oxlint e tsc.** A categoria `correctness` inteira e o `exhaustive-deps` são erro, e `only-export-components`, `incompatible-library` e `unsupported-syntax` também. Ligadas: as `no-unsafe-assignment`, `-argument`, `-member-access`, `-return` e `-call` (`any` vazando de `JSON.parse` e do zod; os componentes do shadcn em `shared/components/ui` e o `.pnpmfile.cjs` ficam fora); `no-deprecated` (o `Cell` do Recharts virou o `fill` da fatia); `no-unnecessary-type-assertion`, `-type-arguments`, `-type-conversion` e `-template-expression` (código morto, com autofix); `switch-exhaustiveness-check` com `considerDefaultExhaustiveForUnions` (`switch` sem `default` que esquece um caso da união é erro). No `tsc`, `noImplicitReturns` garante que todo caminho de uma função com retorno retorna.

**Medidas e deixadas de fora.** Ruff `C4`, `RET`, `PIE`, `FBT`, `FURB157`, `SLF`, `INP` e `PLR` são estilo e refatoração. `ARG` (18 no backend) é quase toda assinatura exigida (handler do FastAPI, método base de estratégia, `lifespan`); os dois parâmetros mortos de verdade, em funções privadas do governo, saíram. No oxlint: `pedantic` (`prefer-readonly-parameter-types` 2.332, `no-confusing-void-expression` 490, `strict-boolean-expressions` 428), `no-unsafe-type-assertion` (141), `eqeqeq` (o `== null` é idioma), `no-unstable-nested-components` (17, funções de render do Recharts e do `toast`), `prefer-nullish-coalescing` (11, todos `||` de propósito), `no-unmodified-loop-condition` (o `setDate` muda a data dentro do laço), `style-prop-object` (o `style` textual do aviso do tutorial), `exhaustive-effect-dependencies` (o `id` no array é de propósito), `no-accumulating-spread` (listas de rótulos pequenas) e `jsx-no-constructed-context-values` (os providers ficam na raiz e o valor muda com o dado de todo jeito).

**Formatação.** O frontend é formatado pelo oxfmt (`frontend/.oxfmtrc.json`, 120 colunas: é a largura que menos mexe no código existente, 214 arquivos contra 470 com 100 e 317 com 140). O `check` do frontend roda `oxfmt --check` e o `pnpm format` da raiz formata backend e frontend. O `frontend/.gitattributes` fixa LF na cópia local, porque o oxfmt não aceita fim de linha automático e o Windows faz checkout em CRLF.

O que ficou para depois tem card próprio: tipos mais rígidos no frontend ([F135](#f135)), código e dependências sem uso ([F136](#f136)), acessibilidade ([F137](#f137)) e o piloto do strict do pyright ([F138](#f138)).

<a id="f135"></a>
**F135 — Tipos mais rígidos no frontend.** Liga três checagens que o TypeScript e o oxlint têm e o projeto não usa. `noUncheckedIndexedAccess` (237 erros hoje): ler `lista[i]` ou `registro[chave]` passa a dar `T | undefined`, e o código precisa tratar o item que não existe. `exactOptionalPropertyTypes` (222): um campo opcional deixa de aceitar `undefined` escrito explicitamente, o que separa "campo ausente" de "campo presente e vazio". `typescript/no-unnecessary-condition` (66): condição que o tipo diz ser sempre verdadeira ou sempre falsa. As três só valem se o tipo gerado da API (`types/openapi.generated.ts`) for fiel ao que o backend manda: um campo que sempre vem, mas sai opcional no OpenAPI, faz a regra pedir checagem à toa. Plano: conferir quais DTOs do backend saem com campo opcional sem precisar (o FastAPI marca como opcional todo campo com valor padrão) e corrigir no schema; depois ligar uma flag por vez, corrigir e commitar separado. Gatilho: um bug de item ausente ou de campo opcional chegar ao jogador, ou uma rodada de qualidade.

<a id="f136"></a>
**F136 — Código e dependências sem uso.** O Knip no frontend acha arquivo, export e tipo que ninguém importa (hoje 2 arquivos, 72 exports e 37 tipos), e o deptry no backend acha pacote declarado e não importado, ou importado e não declarado (hoje 11, cerca de metade falso positivo). Plano: `knip.json` ignorando `shared/components/ui` (os componentes do shadcn exportam peças que o projeto ainda não usa) e o arquivo gerado da API; configuração do deptry no `pyproject.toml` com as exceções que a triagem dos 11 confirmar; apagar o que for morto de verdade e pôr os dois no `check`. Gatilho: livre, é limpeza sem dependência.

<a id="f137"></a>
**F137 — Acessibilidade das telas.** Liga o plugin `jsx-a11y` do oxlint, que confere no JSX o que leitor de tela e teclado precisam: botão só com ícone sem rótulo, clique em elemento que não recebe foco, imagem sem texto alternativo. Hoje são 49 achados. Plano: ligar o plugin, triar os 49 regra a regra como na revisão das regras de lint (fica o que impede alguém de usar a tela, sai o falso positivo), corrigir e deixar como erro. Gatilho: livre.

<a id="f138"></a>
**F138 — Piloto do modo strict do pyright.** O `strict` no projeto inteiro dá 3.352 achados; `backend/config`, `backend/routes` e `main.py` ficam quase limpos. Plano: listar essas pastas em `strict` no `pyrightconfig.json`, corrigir os achados e medir quanto cada achado custou; se o custo por achado valer, ampliar pasta por pasta, começando pelas que não tocam o pandas. Gatilho: livre.

<a id="f142"></a>
**F142 — Banco da 3.0: regras em JSON, conquistas preservadas e migrations por versão.** Entregue com a D18. **Regras da partida:** as 24 colunas de regra de `simulations` viraram um campo JSON `rules`, no mesmo formato do preset e das últimas regras; a leitura é estrita e passa por um decodificador só, que serve a lista de salvas, as estatísticas e a troca das séries geradas. Regra nova é um campo do DTO com valor padrão, sem migration. **Conquistas:** sobrevivem à exclusão da partida em que saíram (a chave vira `SET NULL`), e a tela mostra "Partida excluída". **Migrations:** a inicial é o banco da 2.3 e a da 3.0 junta tudo o que veio depois; quem está na 2.3 atualiza sem perder nada, e da 2.0 à 2.2 o app recusa e manda abrir uma vez na 2.3. **Trava de dado perdido:** conta cada valor do primeiro nível de um JSONB como uma célula. Conferido com o `pg_dump --schema-only` da cadeia antiga contra o da nova, nos dois pontos (2.3 e 3.0), e com uma partida criada pela 2.3 aberta na 3.0.

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
| **F107** | Perfis de público na eleição | Serve N34; eleitores com perfil sobre a eleição da F95 | M17 | — | 🔍 Em avaliação |
| **F120** | Repensar a evolução do patrimônio e a distribuição dos investimentos na carteira | Serve N15; falta escolher o desenho dos dois cards no canvas; liga à F72 | — | — | 🔍 Em avaliação |
| **F123** | Redesenhar o aviso de conquista desbloqueada | Serve N22 e N15; falta escolher o desenho do aviso no canvas; liga à F122 | — | — | 🔍 Em avaliação |
| **F128** | Governo & Política: rever os impostos por setor | Serve N34; revisão da versão jogável | — | — | 🔍 Em avaliação |
| **F129** | Governo & Política: rever a aprovação do governo | Serve N34; inclui a aprovação pesar na reeleição | M17 | — | 🔍 Em avaliação |
| **F130** | Governo & Política: rever os votos e a eleição | Serve N34; revisão da versão jogável | M17 | — | 🔍 Em avaliação |
| **F131** | Catálogo de padrões de vela | Serve N19; tópico do Como jogar com cada padrão animado | M11 | [F96](#f96), [F126](#f126) | 🔍 Em avaliação |
| **F143** | Preparação de cada jogador no lobby | Serve N39 e N34; falta escolher o que cada jogador prepara | — | — | 🔍 Em avaliação |
| **F151** | Segundo turno com disputa | Serve N34; falta escolher o que mexe nos votos entre os turnos | M17 | — | 🔍 Em avaliação |
| **F152** | Promessas de campanha em texto | Serve N34; falta escolher entre texto livre e medida da lista | M17 | — | 🔍 Em avaliação |
| **F153** | Congresso eleito, com bancadas | Serve N34; falta o tamanho da casa e a fórmula do voto | M17 | — | 🔍 Em avaliação |
| **F154** | Negociar apoio com as bancadas | Serve N34; falta a moeda da troca | M17 | [F153](#f153) | 🔍 Em avaliação |
| **F157** | Velocidade x100 que quase não acelera | Serve N40 e N24; falta medir o tick no x100 com o painel de desempenho | M16 | — | 🔍 Em avaliação |
| **F158** | Animações do Como jogar revistas | Serve N25; falta o visual numa rodada no canvas | M14 | [F126](#f126) | 🔍 Em avaliação |

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

<a id="f128"></a>
**F128 — Governo & Política: rever os impostos por setor.** Serve N34; revisão da versão jogável que a F95 entregou. **Como funciona hoje:** a política de impostos padrão é a de antes da expansão (15% no ganho comum de ações, 20% no day trade e no FII, isenção das vendas de ações até R$ 20 mil no mês, tabela da renda fixa de 22,5% a 15% por prazo, LCI e LCA isentas). O presidente propõe medidas gerais (alíquota do ganho comum, alíquota do day trade, teto da isenção de ações, uma alíquota única no lugar da tabela da renda fixa e a alíquota de LCI e LCA, de 0 a 100% e diferente da vigente) e medidas de setor ou segmento (isentar, ou taxar de mais de 0 até 20 pontos por medida, que se empilham sem teto acumulado). No IR do mês, vale a regra do dia de cada venda; segmento vence setor e, entre iguais, vale a mais nova. A venda de setor isento conta no volume dos R$ 20 mil, mas o ganho e o prejuízo dela saem do cálculo; a venda de setor taxado soma os pontos extras ao resultado positivo. A medida aprovada vale 90 dias depois. Na régua da promessa, corte geral é 1, isenção de setor 2, taxar setor 4 e imposto geral novo 5; na aprovação, isentar setor soma 2, taxar setor tira de 1 a 5 (pontos ÷ 2), corte geral soma de 1 a 3 e imposto geral novo tira de 1 a 5. Falta definir: o que muda nessa mecânica, a partir das ideias de refazer o sistema.

<a id="f129"></a>
**F129 — Governo & Política: rever a aprovação do governo.** Serve N34; revisão da versão jogável que a F95 entregou. **Como funciona hoje:** a aprovação começa em 50% na posse e é recalculada no último dia útil de cada mês, só com um jogador na presidência, limitada entre 0 e 100%. Fatores: inflação de 12 meses contra a meta do CMN do ano (tabela de 2000 a 2024; fora dela, 3%), +4 dentro ou abaixo da meta e −3 por ponto acima, sem teto; Ibovespa de 12 meses, 1 ponto a cada 5% de alta ou queda, até ±6; medidas aprovadas e já vigentes, em que o corte de imposto soma e não decai, e o imposto novo e a taxação de setor tiram pontos que somem em linha reta em 180 dias; e a promessa, que tira 3 pontos por faixa de distância entre a marca do governo (a média das faixas das medidas aprovadas) e a promessa da campanha. O Congresso vota a fila no mesmo dia: cada medida passa se um sorteio de 0 a 100, feito a partir da semente da partida, da data e do número da medida, sair abaixo da aprovação. A fila não aceita duas medidas iguais; a retirada vale só antes do voto, e a rejeitada pode voltar. Impeachment com aprovação abaixo de 25% em 3 fechamentos de mês seguidos, com aviso no 2º; o vice assume se ainda for filiado, senão entra um governo neutro do computador, sem medidas. Na troca, a fila some, o histórico de aprovação zera, as medidas aprovadas seguem valendo e a carteira de quem saiu volta a operar. **Ainda não existe:** a aprovação não pesa na eleição; a única trava da reeleição é o limite de 2 mandatos seguidos, e por isso "aprovação baixa perde a reeleição" ainda não vale. Falta definir: o que muda nos fatores e nos pesos, e quanto a aprovação do mandato pesa no voto da eleição seguinte. **O que o playtest mostrou:** a aprovação quase não sobe e o impeachment chega cedo demais; numa partida, ele veio 3 meses depois da posse, com a aprovação perto de 10%. A regra explica: os fatores tiram com folga (−3 por ponto de inflação acima da meta, sem teto) e somam pouco (+4 dentro da meta, Ibovespa até +6), e 3 fechamentos abaixo de 25% cabem no primeiro trimestre (`approval.py:17` a `:27`, gatilho em `government_book.py:614`). Candidatos para a revisão: uma carência depois da posse sem impeachment, um teto na perda pela inflação, fatores que deixem subir o governo que vai bem e mais fechamentos seguidos abaixo do piso.

<a id="f130"></a>
**F130 — Governo & Política: rever os votos e a eleição.** Serve N34; revisão da versão jogável que a F95 entregou. **Como funciona hoje:** a primeira eleição é escolhida no lobby e precisa cair dentro da partida; o mandato é de 4 anos, com até 2 seguidos. A campanha abre 1 ano antes do 1º turno (ou no início da partida), as chapas fecham no último dia do mês anterior, o 1º turno é em 7 de outubro e o 2º, 21 dias depois, no próximo dia útil quando a data cai em fim de semana; a posse é em 1º de janeiro. No 1º dia útil de cada mês da campanha, cada filiado paga a contribuição que escolheu, se tiver caixa, e o gasto vira pontos pela raiz quadrada ÷ 64 (R$ 8 mil dão 1,4 ponto) num eleitorado de 100; o que sobra são os indecisos, e a pesquisa guarda uma foto por mês. No 1º turno, vence quem tiver mais de 50% dos votos válidos; senão, vão os dois mais votados, e o empate fica com o partido mais antigo. No 2º turno, os votos de quem ficou de fora vão inteiros para o finalista com a promessa mais próxima. Entre os turnos, até a véspera do 2º, quem está num partido eliminado pode doar a um finalista; a doação rende pela mesma raiz e entra na hora. Os partidos do computador (União do Progresso, Movimento Novo Vigor e Aliança Cidadã) completam até 3 chapas, com a verba da média dos partidos de jogadores vezes 0,5, 1 ou 1,5 pela dificuldade, e a promessa na faixa mais longe dos partidos que já existem. Cada resultado de turno e o impeachment pausam a partida. Só jogadores fundam e se filiam, durante a campanha e fora do 2º turno; bots ficam fora. Na vitória política, vence o partido com a maior soma de patrimônio dos filiados, sem os do computador. Falta definir: o que muda no voto e na eleição, a partir das ideias de refazer o sistema; a F107 (perfis de público), a F151 (segundo turno com disputa), a F152 (promessas em texto) e a F153 (Congresso eleito) já são mudanças dessas.

<a id="f131"></a>
**F131 — Catálogo de padrões de vela.** Serve N19. Um tópico do "Como jogar" (F126) que lista todos os padrões que as dicas de análise técnica (F96) reconhecem, cada um com o ícone e o nome que aparecem no gráfico (o martelo com o símbolo dele, por exemplo). Navegar pelo catálogo mostra um padrão por vez, com a animação das velas se formando no molde dos roteiros do tutorial, o que o padrão costuma sugerir e o lembrete de que padrão não é garantia. Em aberto: se o catálogo é um tópico do tutorial ou uma tela própria, e se o card do padrão no gráfico ganha um "ver no catálogo". Gatilho: com as dicas de análise técnica e a janela "Como jogar" prontas.

<a id="f143"></a>
**F143 — Preparação de cada jogador no lobby.** Serve N39 e N34. Hoje o lobby prepara só a partida, pelas mãos do host; o que é de cada jogador só se faz depois do início, com o relógio andando, e os primeiros dias viram configuração. A ideia: um painel "Minha preparação" para cada jogador no lobby, salvo junto com o "Pronto" e aplicado no 1º dia da partida. Candidatos, do mais ao menos valioso: (1) **Partido**, com a expansão Governo & Política ligada: fundar (nome, sigla, cor e promessa) ou pedir filiação ao partido de outro jogador, valendo na abertura da campanha; o convite de vice (F145) também caberia aqui; (2) **contribuição de campanha** do primeiro mês; (3) **modo automático:** a estratégia escolhida e ligada desde o 1º dia; (4) **ordens de abertura:** uma lista de compras executada no primeiro pregão, para ninguém largar atrás por demorar a clicar; (5) **meta pessoal** no modo corrida à meta, se ela passar a ser de cada jogador. Falta definir: quais desses entram, o que deixa de ser regra da sala para virar escolha do jogador, e o que acontece numa partida salva com a preparação de quem não voltou.

<a id="f151"></a>
**F151 — Segundo turno com disputa.** Serve N34. No playtest, o 2º turno repetiu o 1º sem chance de virada, e a regra explica: ele cai 21 dias depois do 1º, a contribuição só é cobrada no 1º dia útil do mês (entre os turnos não há cobrança nenhuma), os votos dos eliminados vão inteiros para o finalista de promessa mais próxima e o único movimento possível é a doação de quem foi eliminado. Caminhos candidatos: (1) **campanha de 2º turno:** no dia seguinte ao 1º turno, cada finalista define uma contribuição única de 2º turno, paga na hora, que rende pela mesma raiz; (2) **transferência parcial:** os votos de quem ficou de fora se dividem pela distância das promessas em vez de ir inteiros, e uma parte vira indecisa, disputada pela verba; (3) **um evento de campanha** (debate) com resultado sorteado pela semente da partida. Falta escolher quais entram e com que peso, para a virada ficar possível sem virar sorteio. Conversa com a F107, que também mexe na transferência de votos.

<a id="f152"></a>
**F152 — Promessas de campanha em texto.** Serve N34. Hoje a promessa da chapa é só uma posição na régua de faixas, e ninguém sabe o que o candidato prometeu de fato. A ideia: a chapa registra até 3 promessas curtas ("Isentar o setor elétrico", "Baixar o IR do day trade"), que aparecem na pesquisa, no resultado da eleição e na tela do governo como "Prometeu: …". Falta decidir entre dois desenhos: **texto livre**, só para dar cara à campanha, ou **medida escolhida da lista** das que o governo pode propor, quando a tela marca a promessa como cumprida ou descumprida e a aprovação (F129) passa a pesar isso no lugar da distância de faixas. Com a caixa de entrada (F91), a promessa vira entrada na campanha e a cobrança aparece durante o mandato.

<a id="f153"></a>
**F153 — Congresso eleito, com bancadas.** Serve N34. Hoje o Congresso é um sorteio: cada medida passa se um número de 0 a 100, tirado da semente da partida, sai abaixo da aprovação. A ideia, que é quase um rework da eleição: (1) **Casa de cadeiras** eleita junto com o presidente e mostrada como um hemiciclo de bolinhas na cor de cada partido, os do computador incluídos. (2) **Eleição própria:** as cadeiras partem das intenções do 1º turno, mas não as copiam: a verba para o Congresso é separada da presidencial, os partidos do computador têm voto de legenda próprio e uma parte das cadeiras sai de um sorteio local pela semente, para o presidente poder ganhar com a oposição maioria na casa, como acontece na vida real. (3) **Votação cadeira a cadeira:** a bancada do governo vota a favor com chance alta, a oposição contra, e a chance de cada partido depende da aprovação e da distância entre a medida e a promessa dele; a tela mostra, antes da votação, a chance de a medida passar. Falta definir: o tamanho da casa, a regra que transforma votos em cadeiras, a fórmula do voto de cada cadeira e como a aprovação (F129) entra nela.

<a id="f154"></a>
**F154 — Negociar apoio com as bancadas.** Serve N34. Com o Congresso de bancadas (F153), o governo passa a negociar votos: oferece algo em troca de um partido votar com ele por um tempo, o que sobe a chance de aprovação das medidas. Partido de jogador recebe a proposta num aviso de aceitar ou recusar, no mesmo molde do convite de vice (F145); partido do computador responde por regra, pela distância entre as promessas. Falta definir: a moeda da troca (caixa do governo, uma medida do interesse do partido, a vice ou um cargo), quanto tempo o apoio vale e o custo de quebrar o acordo.

<a id="f157"></a>
**F157 — Velocidade x100 que quase não acelera.** Serve N40 e N24. No playtest, o x100 andou quase como o x1, ou até mais lento. O loop dorme `1 / velocidade` segundos depois de cada tick (`simulation_loop.py:132` a `:156`): no x1 o dia leva o tick mais 1 s, no x100 o tick mais 10 ms. Quando o tick sozinho custa perto de 1 s (a medição da D4 deu de 0,6 a 0,95 s com carga), o x100 fica só umas duas vezes mais rápido que o x1. Falta medir, com o modo debug e o painel de desempenho, numa partida salva longa no x100: quanto custa o tick e em quê (snapshots, bots, eleição, emissão pelo Socket.IO), e se o navegador engasga com um evento por tick e redesenha a tela inteira. O resultado decide as otimizações (agrupar emissões, aliviar o trabalho de cada tick, redesenhar menos no front) e é o ponto de partida das otimizações gerais de desempenho.

<a id="f158"></a>
**F158 — Animações do Como jogar revistas.** Serve N25; retrabalho da F126. No playtest, o tutorial pareceu estranho: o estilo das animações ficou parecido com o do Create, e o número do passo que aparece no meio da animação, num círculo ao lado do alvo (`StepMarker` em `tutorial/stage/stage-kit.tsx:144`, número vindo de `topic-illustration.tsx:57`, usado em `buy-stock.tsx` e `order-types.tsx`), polui a cena. O salto para o trecho do passo ao clicar numa etapa funciona bem e fica como está. Falta escolher o visual numa rodada no canvas: comparar as animações atuais com as primeiras, feitas no canvas a partir das Dicas e truques do Factorio, decidir se o número sai da cena (o passo ativo já fica destacado na lista) e o que muda no cursor e no destaque.
