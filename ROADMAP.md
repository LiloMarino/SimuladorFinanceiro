<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Arquivo morto:** [DECISIONS_ARCHIVE.md](DECISIONS_ARCHIVE.md) — itens encerrados saem dos dois documentos pra lá, inteiros. Consulta por ID.
>
> **Última mudança (2026-10-17):** Concluídas a sugestão de código ao digitar o ativo (F63) e o cache do perfil do ativo no yfinance (F64).

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | — | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | — | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F8](#f8), [F9](#f9), [F10](#f10), [F19](#f19), [F33](#f33) | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | — | — |
| **N6** | Comparar resultados de simulações diferentes | — | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | — | — |
| **N8** | Jogar contra oponentes controlados pelo computador | [F16](#f16) | — |
| **N9** | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | — | — |
| **N10** | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | [F19](#f19) | — |
| **N11** | Que o cenário econômico simulado seja o histórico real | — | — |
| **N12** | Continuar jogando depois do último dia com dado real | [F24](#f24) | — |
| **N13** | Saber que dados a base tem e mantê-los atualizados, fora da partida | — | — |
| **N14** | Atualizar para uma versão nova sem perder as partidas salvas | [F56](#f56) | — |
| **N15** | Usar uma interface agradável e coerente, à altura de um jogo | [F37](#f37) | — |
| **N16** | Ver a carteira e o mercado por setor e segmento | — | — |
| **N17** | Enxergar a estrutura do banco e esboçar mudanças nela | — | — |
| **N18** | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | — | — |
| **N19** | Analisar um ativo com as ferramentas de um trader | [F33](#f33) | — |
| **N20** | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | — | — |
| **N21** | Jogar "na unha", sem a interface apontar a melhor escolha | [F40](#f40) | — |
| **N22** | Ter objetivos para buscar além de vencer a partida | [F41](#f41) | — |
| **N23** | Jogar com os amigos de outras formas além de cada um por si | [F42](#f42), [F52](#f52), [F53](#f53) | — |
| **N24** | Saber onde está a lentidão durante uma partida | [F45](#f45), [F54](#f54) | — |
| **N25** | Entender o que é o simulador e como se joga, sem ler um manual | [F47](#f47), [F48](#f48) | — |
| **N26** | Achar a causa de um erro sem vasculhar o log inteiro | — | — |
| **N27** | Entrar numa partida que já começou | — | — |
| **N28** | Liberar uma vaga sem depender de o jogador sair | [F61](#f61) | — |
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
| [**F23**](#f23) | Spike: gerador de séries sintéticas | — | 🔍 |
| [**F24**](#f24) | Gerar dados futuros na Central de dados | — | ⏳ |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | — | 🔍 |
| [**F33**](#f33) | Indicadores técnicos | — | ⏳ |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | — | 🔍 |
| [**F37**](#f37) | Tema escuro | — | 💤 |
| [**F40**](#f40) | Modo Especialista | — | ⏳ |
| [**F41**](#f41) | Conquistas | — | ⏳ |
| [**F42**](#f42) | Modo em equipes | — | ⏳ |
| [**F44**](#f44) | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | — | 🔍 |
| [**F47**](#f47) | Gravação automática de demonstrações | — | ⏳ |
| [**F48**](#f48) | README e docs que mostram o produto | — | ⏳ |
| [**F49**](#f49) | Spike: tutorial animado | — | 🔍 |
| [**F52**](#f52) | Modo corrida à meta | — | ⏳ |
| [**F53**](#f53) | Modo viver de renda | — | ⏳ |
| [**F55**](#f55) | Modo aquisição hostil | — | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |

<details>
<summary><strong>Concluído / decidido / descartado (13 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | [F41](#f41) | ✅ |
| **D2** | Cálculo financeiro acontece só no backend; o frontend exibe | [F33](#f33), [F40](#f40) | ✅ |
| **D3** | Dinheiro e quantidade trafegam como Decimal serializado em string | — | ✅ |
| **D4** | Banco de dados embarcado no executável | — | ✅ |
| **D6** | A retomada continua no dia seguinte ao último evento | — | ✅ |
| **D7** | O simulador lê as séries sem saber a origem | [F24](#f24) | ✅ |
| **D8** | Bot, modo automático e backtest são o mesmo mecanismo | [F8](#f8), [F16](#f16), [F19](#f19) | ✅ |
| **D9** | De onde nasce uma mudança de schema | — | ✅ |
| **D10** | Como a nota geral é calculada | — | ✅ |
| **D11** | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | — | ✅ |
| **D12** | Como numerar as versões | — | ✅ |
| [**F45**](#f45) | Painel de desempenho | — | ✅ |
| [**F54**](#f54) | Modo debug | — | ✅ |

</details>

---

## 🚦 Livre pra pegar

> Derivado do grafo de dependências: as `F#` que podem ser pegas agora — toda dependência já ✅. "Destrava" é quantas `F#` em aberto esperam por ela, direta ou indiretamente; é por aí que a tabela está ordenada. 💤 (sem prioridade) e 🚫 não entram.

| ID | Resumo | Marco | Destrava | Status |
| --- | --- | --- | --- | --- |
| [**F7**](#f7) | Spike: estratégia Python escrita pelo usuário | M4 | 6 | 🔍 |
| [**F23**](#f23) | Spike: gerador de séries sintéticas | M9 | 2 | 🔍 |
| [**F5**](#f5) | Spike: provider de túnel pela internet | M3 | 1 | 🔍 |
| [**F33**](#f33) | Indicadores técnicos | M11 | 1 | ⏳ |
| [**F44**](#f44) | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | — | 1 | 🔍 |
| [**F47**](#f47) | Gravação automática de demonstrações | M14 | 1 | ⏳ |
| [**F52**](#f52) | Modo corrida à meta | M13 | 1 | ⏳ |
| [**F22**](#f22) | Preço ajustado e proventos | M8 | 0 | 🔍 |
| [**F40**](#f40) | Modo Especialista | M13 | 0 | ⏳ |
| [**F41**](#f41) | Conquistas | M13 | 0 | ⏳ |
| [**F42**](#f42) | Modo em equipes | M13 | 0 | ⏳ |
| [**F49**](#f49) | Spike: tutorial animado | M14 | 0 | 🔍 |
| [**F56**](#f56) | Novidades no app | — | 0 | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | 0 | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | 0 | ⏳ |

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
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F23**](#f23) | Spike: gerador de séries sintéticas | — | 🔍 |
| [**F24**](#f24) | Gerar dados futuros na Central de dados | [F23](#f23) | ⏳ |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | [F19](#f19), [F23](#f23) | 🔍 |

### M11 — Análise técnica

> **Objetivo:** Analisar um ativo com os indicadores e as ferramentas de desenho de uma plataforma de trader.
>
> **Serve:** N19
>
> **Progresso:** 0/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F33**](#f33) | Indicadores técnicos | — | ⏳ |
| [**F34**](#f34) | Gráfico de ações em tela cheia, com ferramentas de trader | [F33](#f33) | 🔍 |

### M13 — Mais jeitos de jogar

> **Objetivo:** Partidas com outras regras e objetivos: sem assistências, em equipes, com conquistas.
>
> **Serve:** N21, N22, N23
>
> **Progresso:** 0/5 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F40**](#f40) | Modo Especialista | — | ⏳ |
| [**F41**](#f41) | Conquistas | — | ⏳ |
| [**F42**](#f42) | Modo em equipes | — | ⏳ |
| [**F52**](#f52) | Modo corrida à meta | — | ⏳ |
| [**F53**](#f53) | Modo viver de renda | [F52](#f52) | ⏳ |

### M14 — Vitrine e primeiros passos

> **Objetivo:** Ver o jogo funcionando antes de baixar e aprender a jogar vendo, não lendo.
>
> **Serve:** N25
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F47**](#f47) | Gravação automática de demonstrações | — | ⏳ |
| [**F48**](#f48) | README e docs que mostram o produto | [F47](#f47) | ⏳ |
| [**F49**](#f49) | Spike: tutorial animado | — | 🔍 |

### Sem marco

> **Progresso:** 2/9 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F37**](#f37) | Tema escuro | — | 💤 |
| [**F44**](#f44) | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | — | 🔍 |
| [**F55**](#f55) | Modo aquisição hostil | [F44](#f44) | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |

<details><summary>Concluído (2 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F45**](#f45) | Painel de desempenho | [F54](#f54) | ✅ |
| [**F54**](#f54) | Modo debug | — | ✅ |

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
| **F24** | Gerar dados futuros na Central de dados | N12 | D7 | M9 | [F23](#f23) | Médio | Alto | Alto | Bom | ⏳ Pendente |
| **F19** | Modo backtest: partida só de estratégias, sem interação | N4, N10 | D8 | M6 | [F16](#f16) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F33** | Indicadores técnicos | N19, N4 | D2 | M11 | — | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F37** | Tema escuro | N15 | — | — | — | Médio | Baixo | Médio | Médio | 💤 Registrado, sem prioridade |
| **F40** | Modo Especialista | N21 | D2 | M13 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F41** | Conquistas | N22 | D1 | M13 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F42** | Modo em equipes | N23 | — | M13 | — | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F45** | Painel de desempenho | N24 | — | — | [F54](#f54) | Baixo | Baixo | Médio | Ótimo | ✅ Concluído |
| **F47** | Gravação automática de demonstrações | N25 | — | M14 | — | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F48** | README e docs que mostram o produto | N25 | — | M14 | [F47](#f47) | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F52** | Modo corrida à meta | N23 | — | M13 | — | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F53** | Modo viver de renda | N23 | — | M13 | [F52](#f52) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F54** | Modo debug | N24 | — | — | — | Baixo | Baixo | Médio | Ótimo | ✅ Concluído |
| **F56** | Novidades no app | N14 | — | — | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F61** | Host remove jogador da sala | N28 | — | — | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |

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
**F24 — Gerar dados futuros na Central de dados.** Serve N12; segue a D7. Na Central (F21), "Gerar dados": o usuário escolhe até quando gerar (o início é sempre o dia útil seguinte ao último dado real de cada série), a semente e a temperatura, vendo no preview como a geração fica antes de gravar; o gerador da F23 grava as linhas nas mesmas tabelas de preço e de indicadores, com origem "gerado", e a barra da linha do tempo mostra o trecho. "Atualizar" passa a trocar o trecho gerado pelo real à medida que o real fica disponível, seguindo a regra para partidas salvas que a F23 fechar. A simulação lê as séries como sempre. Gatilho: F21 e F23 concluídas.

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
**F41 — Conquistas.** Serve N22; segue a D1. Um catálogo no código (`backend/features/achievements/catalog.py`): cada conquista tem código, nome, descrição, ícone (do `lucide-react`), se é secreta, e uma condição avaliada sobre os eventos e snapshots do jogador no fim de cada tick. Exemplos: primeira compra de ação; primeiro R$ 1 milhão; bater o CDI 12 meses seguidos; atravessar uma queda de 30% do Ibovespa perdendo menos que ele; vencer uma sala cheia; vencer sem assistências (F40). A conquista desbloqueada vai para a tabela `achievements` (`user_id`, `code`, `simulation_id`, `unlocked_at`), por migration (D9), e chega ao jogador por um evento do Socket.IO que abre um toast rico, no estilo da Steam: ícone, nome e descrição, com `toast.custom` do sonner. Uma tela "Conquistas" mostra as do jogador: desbloqueadas com data e partida, bloqueadas em cinza, e as secretas sem descrição até sair. As conquistas ficam no banco do host, como o resto do histórico: sem conta online, o jogador que entra na sala de outro host começa lá do zero.

<a id="f42"></a>
**F42 — Modo em equipes.** Serve N23. Cada um opera a própria carteira, mas o placar é da equipe: quem vence é a equipe, não a pessoa. O host escolhe no lobby entre todos contra todos (o de hoje) e equipes; em equipes, cada jogador escolhe a equipe numa lista ao lado da cor, como no lobby de um RTS. A equipe é uma coluna `team` na `simulation_players` da F39, por migration (D9). O valor da equipe em cada critério de vitória (F27) é a média dos membros (média da nota, do retorno, do Sharpe), para que uma equipe de três não vença uma de dois só por somar mais patrimônio. Cada jogador mantém a própria cor; a equipe aparece como um selo ao lado do nome. As telas que mudam, a desenhar no Claude Design antes de implementar: o lobby (escolha de equipe e aviso de equipes desequilibradas); o ranking ao vivo, por equipe e com os membros abaixo; as estatísticas — na aba Geral, a classificação e a nota da equipe com os eixos da nota como média dos membros; nas abas com curva, a curva da equipe (média) com as dos membros mais apagadas; em Risco, Composição e Operações, os jogadores agrupados por equipe; e o fechamento (F27), com o pódio de equipes, os membros de cada uma e o destaque de quem mais contribuiu na equipe vencedora.

<a id="f45"></a>
**F45 — Painel de desempenho.** Serve N24. Mede onde o tempo vai durante uma partida, para depois investigar só o ponto caro, sem serviço externo (o Sentry faz essa medição por rota, mas manda os dados para fora da máquina e é pago). Só funciona com o modo debug (F54) ligado: fora dele o coletor fica desligado, o middleware nem é instalado e a rota `/api/debug/*` responde 404. Um coletor em memória (`backend/core/metrics.py`) guarda, por item, as últimas 1.000 medições e calcula chamadas, tempo total, médio, p95 e máximo: (1) **HTTP** — `MetricsMiddleware` (ASGI puro) mede cada requisição pela rota declarada (`/api/stocks/{ticker}`, não o ticker) e devolve o tempo no cabeçalho `Server-Timing`; fora da conta ficam `/api/stream` (resposta infinita) e o próprio `/api/debug`; (2) **Socket.IO** — o tempo de cada handler recebido (`connect`, `disconnect`, `subscribe`) e, para os enviados, mensagens e bytes por segundo por evento, contados por destinatário dentro do `SocketBroker` e do `SSEBroker` (`stock_update:PETR4` e os demais tickers viram `stock_update:*`); (3) **motor** — quanto leva `next_tick()` para processar um dia, contra o tempo que cabe na velocidade (`1000 / velocidade` ms). Chamadas acima de 500 ms vão para o `slow.log`, pelo logger `backend.metrics` (linha em `AREA_LOGGERS`, F57). `GET /api/debug/metrics` e `POST /api/debug/metrics/reset` são **só do host** (`verify_host`): as medições são do servidor dele. A tela "Desempenho" (`features/performance`, variante A do canvas) atualiza a cada 2 s, com Pausar e Zerar medições: quatro cartões (ritmo do motor com a velocidade real quando atrasa, HTTP com o p95 geral e as rotas lentas, volume enviado ao navegador, onde mais vai tempo), a tabela de tempo com filtro por origem, busca, ordenação e "Mostrar todas", marcando **lenta** (p95 acima de 500 ms) e **trava às vezes** (p95 de 10 vezes a média ou mais), o tráfego por evento e o cartão do py-spy com o comando e o PID. O item "Desempenho" (selo "Debug") em Ferramentas só aparece com o debug ligado e para o host; a URL direta mostra como ligar o debug ou que só o host vê. Achado o ponto, a investigação segue com o `py-spy record --pid`, que gera o gráfico de chamas sem mudar código; a página "Investigando lentidão" dos docs ensina o caminho. Limitações: as medições somem ao reiniciar o app, um 500 tratado pelo servidor entra na conta mas fica sem `Server-Timing`, e o "p95 geral" do cartão HTTP é calculado sobre as janelas atuais de todas as rotas.

<a id="f47"></a>
**F47 — Gravação automática de demonstrações.** Serve N25. Um roteiro em Playwright (`scripts/demo/`) sobe o app num banco de demonstração, importa um conjunto fixo de ativos pelo CSV (sem depender do yfinance, para sair igual toda vez), e percorre as telas: lobby, compra de ação, renda fixa, avanço do tempo, estatísticas e fechamento. Em cada passo tira screenshot, e a sessão inteira é gravada em vídeo (`recordVideo`). O `ffmpeg` corta os trechos em MP4 para os docs e o `gifski` faz GIFs curtos (até ~10 MB) para o README, que no GitHub só anima GIF. A saída vai para `docs/static/demo/`, e o comando `pnpm demo` refaz tudo a cada mudança visual, o que mantém as imagens em dia: as de hoje em `docs/static/img/` são de fevereiro, anteriores ao redesign.

<a id="f48"></a>
**F48 — README e docs que mostram o produto.** Serve N25. O README abre com um GIF do jogo rodando e, logo abaixo, o que ele faz, cada item com uma imagem ou um GIF curto da F47 (renda variável, renda fixa, estatísticas, multiplayer), o download e o link dos docs; a parte de desenvolvimento desce para o fim. Nos docs, uma página "Tour" com os vídeos, e as páginas de "Como usar" com as imagens novas. Junto, uma revisão do que está desatualizado em README e docs, página por página, contra o app de hoje. Feito com a skill de documentação (`engineering:documentation`).

<a id="f52"></a>
**F52 — Modo corrida à meta.** Serve N23. Vence quem chega primeiro a um patrimônio-alvo, como a vitória por Maravilha do Age of Empires. O host define a meta no lobby (por padrão, 10 vezes o capital inicial), guardada numa coluna `goal_net_worth` em `simulations`, e o critério de vitória da F27 ganha o valor "Primeiro a chegar à meta" (valor novo no `ENUM` nativo `victory_criterion`, com `ALTER TYPE ... ADD VALUE` à mão na migration, D9). No fim de cada dia, depois dos snapshots, o motor confere quem passou da meta; o primeiro encerra a partida e leva ao fechamento (F27). Dois no mesmo dia: vence o maior patrimônio. Se a data final chega sem ninguém na meta, vence quem estiver mais perto. A meta é em reais do dia, sem descontar inflação; numa partida de décadas, isso fica explicado ao lado do campo. A topbar mostra a barra de progresso de cada jogador até a meta. Em equipes (F42), a equipe chega à meta pela média do patrimônio dos membros.

<a id="f53"></a>
**F53 — Modo viver de renda.** Serve N23. Uma corrida à meta (F52) em que a meta é a independência financeira, e o caminho tem a vida real no meio. O host define no lobby o salário e a despesa mensal (o aporte de hoje vira a diferença entre os dois) e a frequência dos imprevistos. Imprevistos são despesas inesperadas (conserto, saúde, demissão de um mês sem salário), sorteadas com uma semente da partida, para que todos os jogadores recebam os mesmos imprevistos nos mesmos dias. Eles saem do caixa; caixa negativo paga juros de cheque especial até ser coberto, o que obriga a ter reserva de emergência em algo que se resgata rápido. Salário, despesa e imprevisto entram como valores novos do `ENUM` `cashflow_event_type` (à mão na migration, D9). Vence quem primeiro atinge o patrimônio da regra dos 4%: 25 vezes a despesa anual (com R$ 5 mil de despesa por mês, R$ 1,5 milhão), porque retirar 4% ao ano desse patrimônio cobre as despesas, e o estudo Trinity, com dados dos Estados Unidos, mostrou essa retirada, corrigida pela inflação, durando 30 anos na maior parte dos períodos históricos. A taxa de retirada é configurável, e a explicação fica ao lado do campo. Quando os proventos existirem (F22), a meta pode passar a ser a renda passiva real (dividendos e juros recebidos cobrindo a despesa).

<a id="f54"></a>
**F54 — Modo debug.** Serve N24. Um flag só, decidido ao subir o servidor: `[debug] enabled` no `config.toml` ou `--debug` na linha de comando (que liga mesmo com o arquivo desligado). **Vem desligado em todo lugar**, em desenvolvimento e no executável: "dev" e "executável" só dizem como o front é servido (Vite ou build), não são modos de debug, e não há botão na interface, mudar exige fechar e abrir o app. O backend o expõe em `GET /api/settings` (campo `debug`, somente leitura: o `PUT` não o grava e o valor do `config.toml` vale sobre qualquer coisa guardada). Ligado: (1) `TomlSettings.effective_logging_level()` força `DEBUG` no `app.log` e nos arquivos por área da F57, com `error.log` seguindo só em `ERROR`; `sqlalchemy`, `engineio`, `socketio`, `urllib3` e `asyncio` ficam em `INFO` (`NOISY_LOGGERS` em `logger.py`) para o DEBUG não afogar o arquivo; (2) o front carrega o TanStack Query Devtools pelo build de produção dele (`@tanstack/react-query-devtools/production`, em `lazy`), que funciona também no executável, e libera os `logger.debug`/`logger.log` do console. Desligado, o front é igual em dev e no executável: sem devtools e sem esses logs. O front lê o flag pelo hook `useDebugMode`, que a F45 usa para mostrar o painel e o item de menu; essas duas peças são da F45, não desta. Limitação: os logs do front anteriores à resposta de `/api/settings` se perdem; `warn` e `error` nunca são silenciados.

<a id="f56"></a>
**F56 — Novidades no app.** Serve N14. Como as notas de patch de um jogo: o `CHANGELOG.md` da F51 vai junto no executável, o backend o serve com a versão, e o lobby mostra as novidades da versão atual. Na primeira abertura depois de atualizar, o card ou o selo de novidades fica em destaque até ser aberto (o navegador guarda a última versão vista); aberto, mostra "O que há de novo na versão X" e dá acesso ao histórico inteiro. O lugar exato no lobby, que já está cheio, sai de uma iteração no Claude Design antes de implementar.

<a id="f61"></a>
**F61 — Host remove jogador da sala.** Serve N28. Hoje a vaga só abre quando o jogador sai por conta própria: com a sala cheia ou a partida salva recusada por causa de novatos (F58), o host tem de pedir pelo chat para alguém fechar a aba. O plano: um botão "Remover" no cartão de cada jogador do lobby, só para o host, que encerra a sessão do jogador pelo mesmo caminho do `player_logout`, com um aviso "o host te removeu da sala" na tela dele, e libera a cor e a vaga na hora. Fica em aberto se a remoção também vale para participante offline da partida em andamento; a leitura provável é que não, porque tirar a linha de `simulation_players` apaga o saldo e o histórico dele.

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F60** | Modo servidor dedicado (--headless) | — | — | — | Baixo | Baixo | Baixo | Bom | ⏳ Pendente |

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

<a id="f60"></a>
**F60 — Modo servidor dedicado (`--headless`).** O mesmo executável, sem o navegador: para rodar numa VPS ou num PC ligado direto, sem ninguém jogando nele. `--headless` na linha de comando, ou `[server] headless = true` no `config.toml`, pula o `webbrowser.open` do `main.py`, que hoje roda sempre que o app é o executável, e imprime no terminal os endereços para entrar (o da rede local e, com a F6, o do túnel). O administrador é quem entra com o apelido de `[host] nickname`, que é como o host é definido hoje (`routes/simulation.py`). Como a recuperação de login é por apelido, num servidor exposto à internet qualquer um que digite esse apelido viraria o host; por isso, no modo servidor, o `config.toml` ganha `[host] pin`, e o login com o apelido do host só passa com ele. Serve a quem quer deixar uma sala aberta para os amigos entrarem quando quiserem, sem depender de o host estar com o computador ligado jogando.

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
| **F23** | Spike: gerador de séries sintéticas | Serve N12; fecha o método e o contrato da F24 | M9 | — | 🔍 Em avaliação |
| **F28** | Muitos futuros (Monte Carlo) | Serve N10; revisa ou confirma a D7 | M9 | [F19](#f19), [F23](#f23) | 🔍 Em avaliação |
| **F34** | Gráfico de ações em tela cheia, com ferramentas de trader | Serve N19; escolhe a biblioteca de gráfico | M11 | [F33](#f33) | 🔍 Em avaliação |
| **F44** | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | Serve N23; faltam taxas padrão, rendimentos e protótipo do preço da cota | — | — | 🔍 Em avaliação |
| **F49** | Spike: tutorial animado | Serve N25; compara vídeo, framer-motion e Remotion | M14 | — | 🔍 Em avaliação |
| **F55** | Modo aquisição hostil | Serve N23; faltam parte mínima no mercado e o destino do incorporado | — | [F44](#f44) | 🔍 Em avaliação |

<a id="f5"></a>
**F5 — Spike: provider de túnel pela internet.** Origem: #77. Candidatos da issue: LocalTunnel, Playit, zrok (sugestão para entrar na comparação: Cloudflare Quick Tunnel, que não exige conta). Falta medir, para cada um: (1) **quanto o `.exe` cresce** — critério eliminatório da issue; (2) se exige conta ou cadastro (fere N1); (3) se baixa binário em runtime ou vai empacotado; (4) se passa o WebSocket do Socket.IO sem cair para polling. O cliente oficial do LocalTunnel é Node, o que provavelmente o elimina. Sai daqui com um provider escolhido para a F6.

<a id="f7"></a>
**F7 — Spike: estratégia Python escrita pelo usuário.** Origem: #2, #12. Decide a D5 e define a API da classe base. Falta responder: (1) carregar um `.py` externo via `importlib` funciona dentro do executável do PyInstaller, e quais bibliotecas a estratégia enxerga (só as empacotadas — pandas sim, outras não); (2) como proteger o tick de uma estratégia em loop infinito ou lenta (timeout por tick); (3) o que a estratégia vê e pode fazer — hoje `BaseStrategy` só recebe `matching_engine`/`market_data`, ou seja, renda variável, e faltam caixa, posição, renda fixa e o setor e segmento de cada ativo (já no banco pela F30, em `repository.stock.get_classification`); (4) onde o código fica guardado — numa pasta (fácil de editar no editor) ou no banco junto da simulação (retomar reusa exatamente a mesma versão do código); (5) a viabilidade da opção "bot cliente da API" no multiplayer.

<a id="f22"></a>
**F22 — Preço ajustado e proventos.** Serve N3 e N7. O importador usa `yf.download(auto_adjust=True)`: o preço vem ajustado por dividendos e desdobramentos *até o dia da importação*. A atualização incremental (`upsert_dataframe` só grava linhas depois da última data guardada) emenda duas séries ajustadas em dias diferentes, então um provento ou desdobramento ocorrido entre a importação e a atualização vira um degrau falso na emenda — num desdobramento 2:1, uma queda de 50% que não existiu. Além disso, o preço exibido não é o que se negociava na época, e dividendo nunca entra no caixa. Falta escolher: (1) **atualizar sempre baixando a série inteira** e sobrescrevendo — corrige o degrau com pouca mudança, mas reescreve o passado de partidas salvas a cada provento novo; (2) **preço bruto + proventos como evento** — `auto_adjust=False`; desdobramento ajusta a quantidade da posição e dividendo credita o caixa na data ex (o `yfinance` traz as duas listas); fiel e reprodutível, mas mexe no motor, na carteira e na F13. Sai daqui com a escolha e o plano de implementação.

<a id="f23"></a>
**F23 — Spike: gerador de séries sintéticas.** Serve N12. Gera um futuro plausível para depois do último dia real, gravado como dado comum (D7), sempre numa lacuna sem dado canônico e emendando no último valor real. Plausível quer dizer com a estrutura do mercado real: quedas bruscas, períodos agitados que duram, e ativos parecidos andando juntos (uma crise bancária derruba todos os bancos). Falta definir:

1. **O método** — recomendado: *bootstrap em blocos conjunto*, que sorteia trechos reais de algumas semanas do passado (o mesmo trecho para todos os ativos e indicadores ao mesmo tempo) e emenda os retornos diários desses trechos a partir do último preço real. Preserva as crises, a volatilidade e a correlação entre ativos e setores do histórico sem modelo para treinar, e com semente fixa a mesma geração sai igual (N3); o limite é não inventar um tipo de crise que nunca aconteceu. Alternativas: passeio aleatório com volatilidade constante (GBM — simples, mas sem crises nem correlação), GARCH (volatilidade que vem em ondas como no mercado real, mas um modelo por ativo e a correlação à parte) e rede neural treinada no histórico (MLP/LSTM — tende a prever a média e gerar uma curva lisa, porque o preço diário é quase imprevisível).
2. **A "temperatura"** — um controle só, como a temperatura de uma LLM: em 1 o sorteio dos trechos é uniforme (o histórico como foi); abaixo de 1 favorece trechos calmos; acima de 1 favorece trechos agitados (o peso de cada trecho cresce com a volatilidade dele). Com um preview: gerar sem gravar uma amostra de poucos ativos e mostrar o gráfico a cada mudança de parâmetro.
3. **Indicador é nível, não retorno** — a SELIC gerada a partir de variações sorteadas pode derivar para valores absurdos e precisa de limites, e o CDI anda colado na SELIC.
4. **Partida salva sobre dado gerado** quando o real chega e o substitui (D7) — congelar a geração para aquela partida, impedir a troca enquanto alguma partida usar o trecho, ou aceitar a mudança.

Sai daqui com o método e o contrato fechados para a F24.

<a id="f28"></a>
**F28 — Muitos futuros (Monte Carlo).** Serve N10. Em vez de testar a estratégia num futuro gerado só, testá-la em muitos (ex.: 100, cada um com uma semente) e mostrar o resultado como distribuição: "perdeu para o CDI em 23 de 100 futuros; no pior, −35%; no do meio, +40% em 5 anos". Lê-se pela fração de futuros ruins e pelo pior caso: poucos futuros perdendo para o CDI é bom; uma estratégia que só ganha no histórico real e perde na maioria dos futuros plausíveis teve sorte, não mérito. É o backtest da F19 repetido sobre gerações da F23. Falta definir: **onde vivem os 100 futuros.** A D7 guarda *um* futuro gerado nas tabelas de série, e Monte Carlo precisa de muitos ao mesmo tempo. Opções: (1) as tabelas de série ganham uma dimensão de cenário (o canônico é o cenário 0, e cada futuro de Monte Carlo é um cenário descartável); (2) o motor passa a ler as séries por um provedor, que pode ser o banco ou uma geração em memória — o que estende a D7 de "mesmas tabelas" para "mesma interface". Sai daqui com essa escolha, que revisa ou confirma a D7.

<a id="f34"></a>
**F34 — Gráfico de ações em tela cheia, com ferramentas de trader.** Serve N19; segue a D2. Um botão no card "Histórico de Preços" abre o gráfico em tela cheia, com os indicadores da F33 e o que uma plataforma de trader oferece: barra de ferramentas de desenho (linha de tendência, linha horizontal de suporte e resistência, canal, retângulo, retração de Fibonacci, texto), régua que mede variação % e pregões entre dois pontos, escala logarítmica, legenda com abertura, máxima, mínima, fechamento e volume do candle sob o cursor, comparação com outro ticker ou com o Ibovespa em %, e uma boleta compacta para comprar e vender sem sair da tela. Os desenhos ficam salvos por jogador e ticker numa tabela nova (`chart_drawings`, com os pontos em JSON), entrando por migration (D9). Falta escolher a biblioteca: (1) continuar no `lightweight-charts` e escrever as ferramentas de desenho como plugins (a API de primitives da versão 5; os exemplos oficiais trazem linha de tendência e retângulo); (2) trocar pelo KLineChart (Apache 2.0), que já vem com cerca de 15 ferramentas de desenho, mas calcula indicadores no navegador, e pela D2 eles viriam do backend como indicador customizado; (3) o Advanced Charts da TradingView tem tudo pronto, mas a licença pede cadastro e não permite publicar a biblioteca em repositório público, o que o deixa fora deste projeto. Sai daqui com um protótipo de linha de tendência e Fibonacci nas opções 1 e 2, e a escolha.

<a id="f44"></a>
**F44 — Expansão "Gestoras": abrir capital, cobrar taxa e disputar o controle.** Serve N23. Inspiração: o Capitalism Lab (oferta pública, emissão de novas ações, recompra, compra de ações dos concorrentes), o OpenTTD e o Software Inc. Lá cada jogador é uma empresa que fabrica ou transporta; aqui tudo é finanças, então a empresa de cada jogador é uma gestora, e o que ela vende é o próprio desempenho. **Como expansão:** ligável por partida no lobby, com nome, emblema e card próprios, como as DLCs dos jogos da Paradox; é enfeite visual, o sistema é o mesmo ligado ou não. **A gestora** tem nome e ticker de 4 letras mais 11, como cota de FII na B3 (o servidor recusa letras que já existam entre os ativos importados), e no livro de ofertas a linha leva a cor e a sigla do jogador, para não se confundir com ativo real. O jogador a funda levando parte da carteira em troca de cotas. **É um fundo fechado listado, como um FII, o que junta as duas ideias:** (1) **oferta pública** quando o gestor quiser — cotas novas ao preço do patrimônio por cota (patrimônio de R$ 100 mil em 1.000 cotas dá R$ 100), e o dinheiro de quem compra entra na gestora: é investir no amigo; (2) **mercado** — depois da oferta, as cotas são negociadas no livro de ofertas que a renda variável já tem, e o preço sai da oferta e da procura, acima do patrimônio por cota (ágio) quando a sala acredita no gestor e abaixo (deságio) quando não; (3) **emissão de novas cotas**, com preferência para quem já é cotista, e **recompra**, que vale quando a cota está com deságio (pagar R$ 80 por R$ 100 de patrimônio valoriza a cota de quem fica); (4) **taxas** — todo mês a gestora paga aos gestores taxa de administração sobre o patrimônio e taxa de performance sobre o que passar do CDI, como um fundo real; (5) **controle** — quem juntar mais da metade das cotas troca o gestor pela assembleia de cotistas e passa a operar a carteira e a receber as taxas. **Por que abrir capital, e quando:** as taxas são sobre o dinheiro dos outros, e com ágio as cotas do próprio gestor valem mais no ranking; o custo é ficar exposto, porque vender mais da metade abre a porta para perder o controle. Abrir cedo, sem histórico, tende a sair com pouca procura; abrir depois de um bom ano tende a sair com ágio. **Co-op:** a gestora pode ter mais de um gestor, por convite; eles operam a mesma carteira e dividem as taxas, como sócios da mesma empresa. **Regras para o cálculo fechar:** só pessoas compram cotas, nunca gestoras, o que impede a participação cruzada (A com cotas da B, que tem cotas da A); no ranking, cada jogador soma a carteira pessoal, as cotas que tem pelo preço de mercado e as taxas recebidas, e a carteira da gestora só conta através das cotas, sem contar o mesmo dinheiro duas vezes. **Estrutura:** hoje eventos e snapshots pertencem ao jogador (`user_id`); a gestora precisa de carteira própria, então entra uma tabela `portfolios` e eventos e snapshots passam a apontar para a carteira, com a carteira pessoal de cada jogador migrada uma a uma (D9); a cota é um ativo no livro de ofertas, com o patrimônio por cota publicado a cada dia. Falta: os valores padrão das taxas, se a gestora distribui rendimentos como um FII, e um protótipo do preço da cota no livro com bots (F16) comprando e vendendo.

<a id="f49"></a>
**F49 — Spike: tutorial animado.** Serve N25. O tutorial é um diálogo quase em tela cheia, em passos (avançar, voltar, pular), que aparece na primeira vez no lobby e fica num botão "Como jogar"; cada passo mostra uma animação do próprio app (entrar na sala, comprar uma ação, aplicar em renda fixa, avançar o tempo, ler as estatísticas) com um texto curto. O spike faz o mesmo passo — comprar uma ação — dos três jeitos e compara: (1) **vídeo gravado pelo Playwright**, o mesmo da F47; mais barato e sempre fiel ao app, mas não acompanha o tema escuro nem fica nítido em qualquer tamanho; (2) **animação em código com o `framer-motion`**, que o projeto já tem — os componentes reais com dados de exemplo e um cursor roteirizado; nítido e segue o tema, mas cada passo é código; (3) **Remotion**, que escreve vídeo em React e tem skills oficiais para agentes de código (`npx remotion skills add`); junta a precisão do código com a saída em vídeo, ao custo de uma ferramenta a mais (a licença é gratuita para uso individual). Critérios: fidelidade ao que o usuário imaginou, nitidez, custo de manter quando a tela muda, e tamanho no executável. Entrada necessária: o roteiro desse passo (o que aparece, o que se mexe, quanto dura, o texto). Sai daqui com o jeito escolhido e o plano dos passos restantes.

<a id="f55"></a>
**F55 — Modo aquisição hostil.** Serve N23. Um modo de jogo da expansão "Gestoras" (F44) em que perder o controle tira o jogador da partida. Todo o patrimônio de cada jogador está na própria gestora, e quem juntar mais da metade das cotas de outra a incorpora: o dono anterior sai da partida e a gestora dele passa a ser controlada pelo comprador. Vence quem sobrar, ou quem tiver o maior patrimônio na data final. **Carência:** nos primeiros meses (padrão 12) ninguém pode passar de metade de outra gestora, para que abrir capital cedo não seja suicídio. **Ninguém fica invulnerável:** sem oferta pública, a gestora seria impossível de comprar, então no fim da carência todas precisam ter uma parte mínima das cotas no mercado (padrão 50%); quem não abriu capital entra numa oferta automática pelo patrimônio por cota. **Defesa:** recompra de cotas com o caixa da gestora e compra com as taxas recebidas, como uma empresa que recompra ações para não ser comprada. Falta decidir: a parte mínima no mercado; se o incorporado sai da partida ou vira co-gestor do comprador (como numa fusão); e se há um preço mínimo por cota durante a tentativa de aquisição, como nas ofertas públicas de aquisição reais.
