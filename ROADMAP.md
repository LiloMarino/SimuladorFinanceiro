<!-- ARQUIVO GERADO POR scripts/roadmap.py (skill feature-roadmap) -- NÃO EDITAR À MÃO. -->

> ⚠️ **Este arquivo é gerado automaticamente — não edite manualmente.** Toda mudança (inserir/mover/concluir/descartar/remover um card, cadastrar ou atualizar uma necessidade/decisão/marco, o cabeçalho) passa por `scripts/roadmap.py` (ver `SKILL.md`); uma edição direta aqui é sobrescrita sem aviso na próxima regeneração.

# Roadmap do Simulador Financeiro

> Kanban de features, segue a metodologia da skill `feature-roadmap`. Companion: [DECISIONS.md](DECISIONS.md) — lá está o "porquê" (necessidades `N#` e decisões `D#`); aqui fica só o "o quê construir, em que marco e em que estado está".
>
> **Regra de sincronização:** os dois documentos usam os mesmos IDs (`N#`, `D#`) e devem sempre concordar sobre a decisão vigente de cada item.
>
> **Última mudança (2026-10-17):** F4 concluída: o executável do Windows leva o Postgres oficial e abre sem instalar nada; fecha o M2.

## Glossário

> Descrição completa de cada `N#`/`D#` em `DECISIONS.md`; `F#` é espelho do kanban abaixo. "Condiciona" é derivado dos cards: as `F#` que citam aquele `N#`/`D#`.

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **N1** | Baixar o executável e jogar, sem instalar nem configurar nada ⭐ | [F3](#f3), [F4](#f4), [F25](#f25) | — |
| **N2** | Jogar com amigos pela internet sem que cada um instale uma VPN | [F6](#f6) | — |
| **N3** | Confiar que os números do simulador são exatos e reprodutíveis | [F1](#f1), [F2](#f2), [F21](#f21) | — |
| **N4** | Testar uma estratégia de investimento automática e ver como ela se sai | [F8](#f8), [F9](#f9), [F10](#f10), [F19](#f19), [F33](#f33) | — |
| **N5** | Saber quanto risco foi corrido para chegar num resultado | [F11](#f11), [F17](#f17), [F27](#f27) | — |
| **N6** | Comparar resultados de simulações diferentes | [F12](#f12), [F17](#f17), [F27](#f27) | — |
| **N7** | Que o simulador cobre os custos de operar do mercado real | [F13](#f13), [F29](#f29) | — |
| **N8** | Jogar contra oponentes controlados pelo computador | [F16](#f16) | — |
| **N9** | Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número | [F18](#f18), [F27](#f27) | — |
| **N10** | Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo | [F19](#f19) | — |
| **N11** | Que o cenário econômico simulado seja o histórico real | [F20](#f20) | — |
| **N12** | Continuar jogando depois do último dia com dado real | [F24](#f24) | — |
| **N13** | Saber que dados a base tem e mantê-los atualizados, fora da partida | [F21](#f21), [F63](#f63), [F64](#f64) | — |
| **N14** | Atualizar para uma versão nova sem perder as partidas salvas | [F25](#f25), [F51](#f51), [F56](#f56), [F62](#f62) | — |
| **N15** | Usar uma interface agradável e coerente, à altura de um jogo | [F26](#f26), [F35](#f35), [F36](#f36), [F37](#f37), [F38](#f38) | — |
| **N16** | Ver a carteira e o mercado por setor e segmento | [F30](#f30), [F64](#f64) | — |
| **N17** | Enxergar a estrutura do banco e esboçar mudanças nela | [F31](#f31), [F50](#f50) | — |
| **N18** | Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia | [F32](#f32) | — |
| **N19** | Analisar um ativo com as ferramentas de um trader | [F33](#f33) | — |
| **N20** | Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar | [F39](#f39) | — |
| **N21** | Jogar "na unha", sem a interface apontar a melhor escolha | [F40](#f40) | — |
| **N22** | Ter objetivos para buscar além de vencer a partida | [F41](#f41) | — |
| **N23** | Jogar com os amigos de outras formas além de cada um por si | [F42](#f42), [F43](#f43), [F52](#f52), [F53](#f53) | — |
| **N24** | Saber onde está a lentidão durante uma partida | [F45](#f45), [F54](#f54) | — |
| **N25** | Entender o que é o simulador e como se joga, sem ler um manual | [F47](#f47), [F48](#f48) | — |
| **N26** | Achar a causa de um erro sem vasculhar o log inteiro | [F57](#f57) | — |
| **N27** | Entrar numa partida que já começou | [F58](#f58) | — |
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
| [**F45**](#f45) | Painel de desempenho | — | ⏳ |
| [**F47**](#f47) | Gravação automática de demonstrações | — | ⏳ |
| [**F48**](#f48) | README e docs que mostram o produto | — | ⏳ |
| [**F49**](#f49) | Spike: tutorial animado | — | 🔍 |
| [**F51**](#f51) | Versão única e changelog | — | ⏳ |
| [**F52**](#f52) | Modo corrida à meta | — | ⏳ |
| [**F53**](#f53) | Modo viver de renda | — | ⏳ |
| [**F54**](#f54) | Modo debug | — | ⏳ |
| [**F55**](#f55) | Modo aquisição hostil | — | 🔍 |
| [**F56**](#f56) | Novidades no app | — | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | ⏳ |
| [**F62**](#f62) | Uma migration inicial só para a 2.0.0 | — | ⏳ |
| [**F63**](#f63) | Sugestão de código ao digitar o ativo | — | ⏳ |
| [**F64**](#f64) | Cache do perfil do ativo no yfinance | — | ⏳ |

<details>
<summary><strong>Concluído / decidido / descartado (40 itens — clique pra expandir)</strong></summary>

| ID | Resumo | Condiciona (F#) | Status |
| --- | --- | --- | --- |
| **D1** | Eventos são a fonte da verdade; snapshots são derivados | [F2](#f2), [F11](#f11), [F13](#f13), [F29](#f29), [F41](#f41) | ✅ |
| **D2** | Cálculo financeiro acontece só no backend; o frontend exibe | [F2](#f2), [F11](#f11), [F12](#f12), [F17](#f17), [F32](#f32), [F33](#f33), [F40](#f40) | ✅ |
| **D3** | Dinheiro e quantidade trafegam como Decimal serializado em string | [F1](#f1) | ✅ |
| **D4** | Banco de dados embarcado no executável | [F3](#f3), [F4](#f4) | ✅ |
| **D6** | A retomada continua no dia seguinte ao último evento | [F2](#f2) | ✅ |
| **D7** | O simulador lê as séries sem saber a origem | [F20](#f20), [F21](#f21), [F24](#f24) | ✅ |
| **D8** | Bot, modo automático e backtest são o mesmo mecanismo | [F8](#f8), [F16](#f16), [F19](#f19), [F27](#f27) | ✅ |
| **D9** | De onde nasce uma mudança de schema | [F25](#f25), [F31](#f31), [F50](#f50), [F62](#f62), [F64](#f64) | ✅ |
| **D10** | Como a nota geral é calculada | [F18](#f18) | ✅ |
| **D11** | Sobre qual base o shadcn monta os componentes: Radix ou Base UI | [F36](#f36) | ✅ |
| **D12** | Como numerar as versões | [F51](#f51) | ✅ |
| [**F1**](#f1) | Decimal como string do backend ao frontend | — | ✅ |
| [**F2**](#f2) | Renda fixa com cálculo único no backend e retomada consistente | — | ✅ |
| [**F3**](#f3) | Spike: banco embarcado no executável | — | ✅ |
| [**F4**](#f4) | Executável sobe sem banco instalado | — | ✅ |
| [**F11**](#f11) | Métricas de risco do desempenho | — | ✅ |
| [**F12**](#f12) | Comparação entre simulações | — | ✅ |
| [**F13**](#f13) | Impacto de preço de ordens grandes | — | ✅ |
| [**F15**](#f15) | Cliente desktop em Tauri | — | 🚫 |
| [**F17**](#f17) | Estatísticas em abas, como o relatório de fim de partida de um RTS | — | ✅ |
| [**F18**](#f18) | Pontuação geral (overall) | — | ✅ |
| [**F20**](#f20) | Indicadores reais (CDI, SELIC, IPCA) do Banco Central | — | ✅ |
| [**F21**](#f21) | Central de dados, fora da partida | — | ✅ |
| [**F25**](#f25) | Migrations com Alembic | — | ✅ |
| [**F26**](#f26) | Redesign visual | — | ✅ |
| [**F27**](#f27) | Fechamento de partida: pódio e critério de vitória | — | ✅ |
| [**F29**](#f29) | IR na venda de renda variável | — | ✅ |
| [**F30**](#f30) | Setores e segmentos | — | ✅ |
| [**F31**](#f31) | Diagrama do banco sempre em dia | — | ✅ |
| [**F32**](#f32) | Ferramenta de correlação entre ativos | — | ✅ |
| [**F35**](#f35) | Dependências em dia | — | ✅ |
| [**F36**](#f36) | Interface padronizada no shadcn | — | ✅ |
| [**F38**](#f38) | Mensagens do backend em português | — | ✅ |
| [**F39**](#f39) | Cor exclusiva e sigla de duas letras por jogador | — | ✅ |
| [**F43**](#f43) | Spike: outros modos de jogo | — | ✅ |
| [**F46**](#f46) | Console do navegador no terminal do dev | — | ✅ |
| [**F50**](#f50) | Diagrama do banco navegável | — | ✅ |
| [**F57**](#f57) | Logs separados por assunto | — | ✅ |
| [**F58**](#f58) | Entrar no meio da partida (hot-join) | — | ✅ |
| [**F59**](#f59) | Separar em dois executáveis: cliente e servidor | — | 🚫 |

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
| [**F51**](#f51) | Versão única e changelog | — | 1 | ⏳ |
| [**F52**](#f52) | Modo corrida à meta | M13 | 1 | ⏳ |
| [**F54**](#f54) | Modo debug | — | 1 | ⏳ |
| [**F22**](#f22) | Preço ajustado e proventos | M8 | 0 | 🔍 |
| [**F40**](#f40) | Modo Especialista | M13 | 0 | ⏳ |
| [**F41**](#f41) | Conquistas | M13 | 0 | ⏳ |
| [**F42**](#f42) | Modo em equipes | M13 | 0 | ⏳ |
| [**F49**](#f49) | Spike: tutorial animado | M14 | 0 | 🔍 |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | 0 | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | — | 0 | ⏳ |
| [**F62**](#f62) | Uma migration inicial só para a 2.0.0 | — | 0 | ⏳ |
| [**F63**](#f63) | Sugestão de código ao digitar o ativo | M8 | 0 | ⏳ |
| [**F64**](#f64) | Cache do perfil do ativo no yfinance | M8 | 0 | ⏳ |

---

## 🧭 Marcos

### M1 — Números confiáveis

> **Objetivo:** O que aparece na tela é o que está no banco, e retomar uma simulação dá o mesmo resultado que rodar direto.
>
> **Serve:** N3
>
> **Progresso:** 2/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| — | *(nada em aberto)* | — | — |

<details><summary>Concluído (2 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F1**](#f1) | Decimal como string do backend ao frontend | — | ✅ |
| [**F2**](#f2) | Renda fixa com cálculo único no backend e retomada consistente | — | ✅ |

</details>

### M2 — Baixar e jogar

> **Objetivo:** Abrir o executável numa máquina limpa e chegar ao lobby sem instalar nada, e atualizar de versão sem perder os saves.
>
> **Serve:** N1, N14
>
> **Progresso:** 3/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| — | *(nada em aberto)* | — | — |

<details><summary>Concluído (3 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F3**](#f3) | Spike: banco embarcado no executável | — | ✅ |
| [**F4**](#f4) | Executável sobe sem banco instalado | [F3](#f3) | ✅ |
| [**F25**](#f25) | Migrations com Alembic | — | ✅ |

</details>

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

### M5 — Análise de desempenho

> **Objetivo:** Ver o risco por trás do retorno e comparar simulações lado a lado.
>
> **Serve:** N5, N6
>
> **Progresso:** 2/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| — | *(nada em aberto)* | — | — |

<details><summary>Concluído (2 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F11**](#f11) | Métricas de risco do desempenho | — | ✅ |
| [**F12**](#f12) | Comparação entre simulações | — | ✅ |

</details>

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

### M7 — Relatório de fim de partida

> **Objetivo:** Ver o desempenho por dimensão ao longo do tempo e numa nota geral, na partida e na comparação.
>
> **Serve:** N5, N6, N9
>
> **Progresso:** 3/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| — | *(nada em aberto)* | — | — |

<details><summary>Concluído (3 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F17**](#f17) | Estatísticas em abas, como o relatório de fim de partida de um RTS | — | ✅ |
| [**F18**](#f18) | Pontuação geral (overall) | — | ✅ |
| [**F27**](#f27) | Fechamento de partida: pódio e critério de vitória | [F17](#f17), [F18](#f18) | ✅ |

</details>

### M8 — Dados reais, cuidados fora da partida

> **Objetivo:** Indicadores e preços fiéis ao histórico, geridos numa central antes de jogar.
>
> **Serve:** N3, N11, N13
>
> **Progresso:** 2/5 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F22**](#f22) | Preço ajustado e proventos | — | 🔍 |
| [**F63**](#f63) | Sugestão de código ao digitar o ativo | — | ⏳ |
| [**F64**](#f64) | Cache do perfil do ativo no yfinance | — | ⏳ |

<details><summary>Concluído (2 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F20**](#f20) | Indicadores reais (CDI, SELIC, IPCA) do Banco Central | — | ✅ |
| [**F21**](#f21) | Central de dados, fora da partida | — | ✅ |

</details>

### M9 — Mercado sem fim

> **Objetivo:** Jogar além do último dia real sobre dados gerados que a simulação trata como reais.
>
> **Serve:** N12
>
> **Progresso:** 0/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F23**](#f23) | Spike: gerador de séries sintéticas | [F20](#f20) | 🔍 |
| [**F24**](#f24) | Gerar dados futuros na Central de dados | [F21](#f21), [F23](#f23) | ⏳ |
| [**F28**](#f28) | Muitos futuros (Monte Carlo) | [F19](#f19), [F23](#f23) | 🔍 |

### M10 — Custos do mercado real

> **Objetivo:** Operar paga o que pagaria fora do simulador: impacto de preço e imposto.
>
> **Serve:** N7
>
> **Progresso:** 2/2 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| — | *(nada em aberto)* | — | — |

<details><summary>Concluído (2 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F13**](#f13) | Impacto de preço de ordens grandes | — | ✅ |
| [**F29**](#f29) | IR na venda de renda variável | — | ✅ |

</details>

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

### M12 — Interface nova

> **Objetivo:** O app inteiro no visual novo, sobre componentes padronizados e dependências em dia.
>
> **Serve:** N15
>
> **Progresso:** 3/3 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| — | *(nada em aberto)* | — | — |

<details><summary>Concluído (3 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F26**](#f26) | Redesign visual | [F36](#f36) | ✅ |
| [**F35**](#f35) | Dependências em dia | — | ✅ |
| [**F36**](#f36) | Interface padronizada no shadcn | [F35](#f35) | ✅ |

</details>

### M13 — Mais jeitos de jogar

> **Objetivo:** Partidas com outras regras e objetivos: sem assistências, em equipes, com conquistas.
>
> **Serve:** N21, N22, N23
>
> **Progresso:** 1/6 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F40**](#f40) | Modo Especialista | — | ⏳ |
| [**F41**](#f41) | Conquistas | — | ⏳ |
| [**F42**](#f42) | Modo em equipes | [F39](#f39) | ⏳ |
| [**F52**](#f52) | Modo corrida à meta | — | ⏳ |
| [**F53**](#f53) | Modo viver de renda | [F52](#f52) | ⏳ |

<details><summary>Concluído (1 item)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F43**](#f43) | Spike: outros modos de jogo | — | ✅ |

</details>

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

> **Progresso:** 9/20 concluídas

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F14**](#f14) | Janela desktop nativa | — | 💤 |
| [**F37**](#f37) | Tema escuro | [F26](#f26) | 💤 |
| [**F44**](#f44) | Expansão Gestoras: abrir capital, cobrar taxa e disputar o controle | — | 🔍 |
| [**F45**](#f45) | Painel de desempenho | [F54](#f54) | ⏳ |
| [**F51**](#f51) | Versão única e changelog | — | ⏳ |
| [**F54**](#f54) | Modo debug | — | ⏳ |
| [**F55**](#f55) | Modo aquisição hostil | [F44](#f44) | 🔍 |
| [**F56**](#f56) | Novidades no app | [F51](#f51) | ⏳ |
| [**F60**](#f60) | Modo servidor dedicado (--headless) | — | ⏳ |
| [**F61**](#f61) | Host remove jogador da sala | [F58](#f58) | ⏳ |
| [**F62**](#f62) | Uma migration inicial só para a 2.0.0 | [F4](#f4) | ⏳ |

<details><summary>Concluído (9 itens)</summary>

| ID | Resumo | Depende de | Status |
| --- | --- | --- | --- |
| [**F30**](#f30) | Setores e segmentos | — | ✅ |
| [**F31**](#f31) | Diagrama do banco sempre em dia | — | ✅ |
| [**F32**](#f32) | Ferramenta de correlação entre ativos | — | ✅ |
| [**F38**](#f38) | Mensagens do backend em português | — | ✅ |
| [**F39**](#f39) | Cor exclusiva e sigla de duas letras por jogador | — | ✅ |
| [**F46**](#f46) | Console do navegador no terminal do dev | — | ✅ |
| [**F50**](#f50) | Diagrama do banco navegável | — | ✅ |
| [**F57**](#f57) | Logs separados por assunto | — | ✅ |
| [**F58**](#f58) | Entrar no meio da partida (hot-join) | [F39](#f39) | ✅ |

</details>

---

## 1. Atende necessidade

| ID | Resumo | Atende (N#) | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F1** | Decimal como string do backend ao frontend | N3 | D3 | M1 | — | Médio | Médio | Alto | Bom | ✅ Concluído |
| **F2** | Renda fixa com cálculo único no backend e retomada consistente | N3 | D1, D2, D6 | M1 | — | Alto | Alto | Alto | Bom | ✅ Concluído |
| **F4** | Executável sobe sem banco instalado | N1 | D4 | M2 | [F3](#f3) | Médio | Médio | Alto | Excelente | ✅ Concluído |
| **F6** | Link de convite pela internet no lobby | N2 | — | M3 | [F5](#f5) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F8** | Modo automático: estratégia do jogador roda a cada tick | N4 | D5, D8 | M4 | [F7](#f7) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F9** | Estratégias prontas de exemplo | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F10** | Guia de como escrever uma estratégia | N4 | — | M4 | [F8](#f8) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F11** | Métricas de risco do desempenho | N5 | D1, D2 | M5 | — | Médio | Baixo | Alto | Excelente | ✅ Concluído |
| **F12** | Comparação entre simulações | N6 | D2 | M5 | — | Médio | Baixo | Médio | Bom | ✅ Concluído |
| **F13** | Impacto de preço de ordens grandes | N7 | D1 | M10 | — | Alto | Alto | Médio | Médio | ✅ Concluído |
| **F16** | Bots na sala | N8 | D8 | M6 | [F8](#f8) | Médio | Baixo | Alto | Bom | ⏳ Pendente |
| **F17** | Estatísticas em abas, como o relatório de fim de partida de um RTS | N5, N6 | D2 | M7 | — | Médio | Baixo | Alto | Bom | ✅ Concluído |
| **F20** | Indicadores reais (CDI, SELIC, IPCA) do Banco Central | N11 | D7 | M8 | — | Médio | Médio | Alto | Excelente | ✅ Concluído |
| **F21** | Central de dados, fora da partida | N13, N3 | D7 | M8 | — | Médio | Baixo | Alto | Bom | ✅ Concluído |
| **F24** | Gerar dados futuros na Central de dados | N12 | D7 | M9 | [F21](#f21), [F23](#f23) | Médio | Alto | Alto | Bom | ⏳ Pendente |
| **F25** | Migrations com Alembic | N14, N1 | D9 | M2 | — | Médio | Médio | Alto | Excelente | ✅ Concluído |
| **F19** | Modo backtest: partida só de estratégias, sem interação | N4, N10 | D8 | M6 | [F16](#f16) | Alto | Alto | Alto | Bom | ⏳ Pendente |
| **F27** | Fechamento de partida: pódio e critério de vitória | N5, N6, N9 | D8 | M7 | [F17](#f17), [F18](#f18) | Médio | Baixo | Alto | Bom | ✅ Concluído |
| **F29** | IR na venda de renda variável | N7 | D1 | M10 | — | Médio | Médio | Alto | Bom | ✅ Concluído |
| **F30** | Setores e segmentos | N16 | — | — | — | Médio | Baixo | Médio | Bom | ✅ Concluído |
| **F31** | Diagrama do banco sempre em dia | N17 | D9 | — | — | Baixo | Baixo | Médio | Excelente | ✅ Concluído |
| **F32** | Ferramenta de correlação entre ativos | N18 | D2 | — | — | Médio | Baixo | Médio | Bom | ✅ Concluído |
| **F18** | Pontuação geral (overall) | N9 | D10 | M7 | — | Médio | Baixo | Alto | Bom | ✅ Concluído |
| **F33** | Indicadores técnicos | N19, N4 | D2 | M11 | — | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F35** | Dependências em dia | N15 | — | M12 | — | Médio | Médio | Baixo | Médio | ✅ Concluído |
| **F36** | Interface padronizada no shadcn | N15 | D11 | M12 | [F35](#f35) | Médio | Médio | Médio | Bom | ✅ Concluído |
| **F26** | Redesign visual | N15 | — | M12 | [F36](#f36) | Alto | Médio | Alto | Bom | ✅ Concluído |
| **F37** | Tema escuro | N15 | — | — | [F26](#f26) | Médio | Baixo | Médio | Médio | 💤 Registrado, sem prioridade |
| **F38** | Mensagens do backend em português | N15 | — | — | — | Baixo | Baixo | Médio | Bom | ✅ Concluído |
| **F39** | Cor exclusiva e sigla de duas letras por jogador | N20 | — | — | — | Médio | Baixo | Médio | Bom | ✅ Concluído |
| **F40** | Modo Especialista | N21 | D2 | M13 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F41** | Conquistas | N22 | D1 | M13 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F42** | Modo em equipes | N23 | — | M13 | [F39](#f39) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F45** | Painel de desempenho | N24 | — | — | [F54](#f54) | Baixo | Baixo | Médio | Ótimo | ⏳ Pendente |
| **F47** | Gravação automática de demonstrações | N25 | — | M14 | — | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F48** | README e docs que mostram o produto | N25 | — | M14 | [F47](#f47) | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F51** | Versão única e changelog | N14 | D12 | — | — | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F43** | Spike: outros modos de jogo | N23 | — | M13 | — | Baixo | Baixo | Médio | Bom | ✅ Concluído |
| **F52** | Modo corrida à meta | N23 | — | M13 | — | Médio | Baixo | Alto | Ótimo | ⏳ Pendente |
| **F53** | Modo viver de renda | N23 | — | M13 | [F52](#f52) | Médio | Médio | Alto | Bom | ⏳ Pendente |
| **F54** | Modo debug | N24 | — | — | — | Baixo | Baixo | Médio | Ótimo | ⏳ Pendente |
| **F56** | Novidades no app | N14 | — | — | [F51](#f51) | Baixo | Baixo | Médio | Bom | ⏳ Pendente |
| **F57** | Logs separados por assunto | N26 | — | — | — | Baixo | Baixo | Médio | Ótimo | ✅ Concluído |
| **F50** | Diagrama do banco navegável | N17 | D9 | — | — | Médio | Baixo | Médio | Bom | ✅ Concluído |
| **F58** | Entrar no meio da partida (hot-join) | N27 | — | — | [F39](#f39) | Médio | Médio | Médio | Bom | ✅ Concluído |
| **F61** | Host remove jogador da sala | N28 | — | — | [F58](#f58) | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F62** | Uma migration inicial só para a 2.0.0 | N14 | D9 | — | [F4](#f4) | Baixo | Médio | Médio | Bom | ⏳ Pendente |
| **F63** | Sugestão de código ao digitar o ativo | N13 | — | M8 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F64** | Cache do perfil do ativo no yfinance | N13, N16 | D9 | M8 | — | Médio | Baixo | Médio | Bom | ⏳ Pendente |
| **F3** | Spike: banco embarcado no executável | N1 | D4 | M2 | — | Médio | Baixo | Alto | Excelente | ✅ Concluído |

<a id="f1"></a>
**F1 — Decimal como string do backend ao frontend.** Origem: #86. O `BaseDTO` deixou de converter `Decimal` para `float`, e o Pydantic serializa como string; os DTOs de dinheiro, quantidade monetária e taxa (carteira, posições, renda fixa, simulação, indicadores, eventos realtime de caixa e execução) e os requests de valor passaram a `Decimal`. O motor guarda caixa e posições em `Decimal`; preço de ação continua `float` na origem (`StockPriceHistory` é `Double`) e vira `Decimal` pelo texto (`to_money`) onde entra no caixa ou num evento. No front, `displayMoney`/`displayPercent`/`displayMoneyCompact` formatam a string direto pelo `Intl` (lib `ES2023.Intl`), e os requests mandam a string digitada. A conta da tela de Carteira subiu para o backend: o `PortfolioDTO` traz totais, alocação e rentabilidade prontos, o histórico patrimonial virou `/api/portfolio/history`, e `portfolio_update` substitui a carteira a cada tick. Limitações: a pizza da carteira soma no front os itens visíveis (interação do gráfico); o compacto do eixo passou a usar o sufixo pt-BR ("mil", "mi").
**Aceite:** todo valor exibido bate com o `NUMERIC(20,6)` do banco em todas as casas que a tela mostra.

<a id="f2"></a>
**F2 — Renda fixa com cálculo único no backend e retomada consistente.** Origem: #85. `features/fixed_income/accrual.py` é a única fórmula: taxa efetiva (prefixado = taxa; CDI = CDI × percentual; IPCA+/SELIC+ composto, `(1 + índice) × (1 + spread) − 1`), fator diário `(1 + taxa)^(1/252)`, tabela regressiva de IR e resgate arredondado ao centavo. O tick ao vivo (`accrue`, idempotente por dia), a reconstrução e a projeção aplicam a mesma sequência de multiplicações em `Decimal`. Ao carregar, as posições são reconstruídas dos eventos BUY/REDEEM (D1), e as de ações também, repetindo compras e vendas com a mesma `Position`. A retomada segue a D6, sem reaplicar o aporte do mês, e o caixa reconstruído passou a somar os aportes. As posições de renda fixa são indexadas pelo `asset_uuid`, não pelo nome. `GET /api/fixed-income/{uuid}/projection` alimenta a tela de detalhe, e o front parou de projetar juros. Limitações: os indicadores (CDI, IPCA, SELIC) ainda são constantes em `EconomicRepository`, então a projeção do pós-fixado só coincide com o realizado enquanto continuarem constantes; o IR de vários aportes no mesmo título usa a data do primeiro.
**Aceite:** um prefixado comprado e levado ao vencimento credita o mesmo valor, ao centavo, rodando direto ou pausando e retomando no meio — e esse valor é igual à projeção mostrada no dia da compra (coberto em `tests/test_fixed_income_accrual.py` e verificado ponta a ponta: projeção R$ 12.778,14, resgate R$ 12.778,14 após parar e retomar).

<a id="f4"></a>
**F4 — Executável sobe sem banco instalado.** Serve N1; condicionada pela D4. No Windows o executável leva o Postgres oficial e abre sem nenhum passo extra. `scripts/build_postgres.py` (`pnpm build:postgres`, rodado pelo release só no job do Windows) baixa o zip oficial com versão e SHA-256 fixados, extrai `postgres`, `initdb`, `pg_ctl`, as DLLs, `lib`, `share` e as licenças, e roda o `initdb` uma vez (UTF8, localidade `C.UTF-8` embutida, fuso America/Sao_Paulo), gerando `postgres.zip` e `cluster.zip`, que o `.spec` empacota em `backend/postgres`. `backend/core/embedded_postgres.py` cuida do ciclo de vida: `resolve_database_url()` devolve o `POSTGRES_DATABASE_URL` quando definida (o `.env` deixa de ser obrigatório e o servidor não sobe) ou sobe o embarcado; extrai binários e banco uma vez em `%LOCALAPPDATA%/SimuladorFinanceiro`, sobe o `postgres.exe` numa porta livre só em 127.0.0.1, sorteia a senha do superusuário na primeira abertura e passa a exigir `scram-sha-256`. O servidor fica preso ao processo do app por um Job Object, que o Windows encerra em qualquer queda, e o encerramento limpo roda no `atexit` e nos eventos de console (Ctrl+Break, fechar a janela, logoff, desligamento). `database.py` e `main.py` passaram a usar `resolve_database_url()`; Linux e macOS não embarcam nada e seguem com `POSTGRES_DATABASE_URL`. A página de instalação e o README foram reescritos, e o workflow `postgres-version.yml` compara toda segunda a versão fixada com a mais recente. Referência de desenho: o Karaoke Mugen, aplicativo desktop de código aberto, embarca o Postgres por padrão, aceita um externo por configuração, confere o runtime do Visual C++ e limpa servidor órfão. Medido no app completo: 112,1 MB (eram 60,4); primeira abertura numa máquina limpa simulada em cerca de 10 s; reabertura em 6,8 s, igual à do mesmo executável com banco externo; fechar o app à força não deixa servidor para trás. Limitações: a verificação foi num Windows que já tem Postgres instalado (o executável não o usa) e com o runtime do Visual C++ presente, então a máquina realmente limpa continua por testar; o fechamento pelo X da janela não foi exercitado, só Ctrl+Break; o macOS não embarca (a EDB tem o zip oficial e entra pelo mesmo caminho); uma versão principal nova do Postgres exige exportar e importar o banco.

**Aceite:** numa máquina Windows sem Postgres e sem `.env`, baixar o release e abrir o executável leva ao lobby sem nenhum passo extra, e a segunda abertura chega ao lobby sem rodar o `initdb`.

<a id="f6"></a>
**F6 — Link de convite pela internet no lobby.** Origem: #77. Implementa o provider escolhido na F5 como subclasse de `TunnelProvider` (`start`/`stop`/`get_public_url`, a mesma interface do `lan_provider`), selecionável em `[server] provider` do TOML. O link copiável que o lobby já mostra para LAN passa a mostrar a URL pública quando o túnel está ativo. Gatilho: F5 concluída.
**Aceite:** um amigo fora da rede local entra na partida só abrindo o link, sem instalar nada.

<a id="f8"></a>
**F8 — Modo automático: estratégia do jogador roda a cada tick.** Origem: #2, #12, #14. Hoje `SimulationEngine.set_strategy` guarda uma estratégia só para o engine inteiro; ela passa a ser por jogador (`client_id` → estratégia), com `ManualStrategy` (já é no-op) como padrão. Cada tick chama `next()` da estratégia de cada jogador antes do flush de eventos. A página de Estratégias (hoje um mock que retorna 501) vira real: escolher a estratégia, ativar e desativar (a alternância manual ↔ automático da #14) e ver o log das ordens que ela emitiu. Onde a estratégia roda e quem pode carregá-la segue a D5. Gatilho: F7 concluída.

<a id="f9"></a>
**F9 — Estratégias prontas de exemplo.** Estratégias simples e conhecidas, implementadas como subclasses da classe base com parâmetros editáveis na UI. Duas famílias: **referências**, para responder se uma estratégia bate o "não fazer nada" — comprar e segurar um ETF de índice (BOVA11), 100% no CDI e rebalanceamento por meta (ex.: 60% ações / 40% renda fixa, voltando à meta todo mês, como o rebalanceamento do [Finance Manager](https://github.com/LiloMarino/Finance-Manager)); e **táticas**, as três do mock atual de `strategies.tsx` — cruzamento de médias móveis de 50 e 200 dias, RSI (compra abaixo de 30, vende acima de 70) e rompimento de máxima com volume — mais momentum (compra os ativos que mais subiram nos últimos 12 meses). Servem para jogar no automático e como bots (F16) sem escrever código, como exemplo comentado para o guia da F10 e como teste da própria classe base: o rebalanceamento e o 100% CDI só cabem se a estratégia enxergar caixa, posições e renda fixa, e cada estratégia que não couber limpa aponta o que falta na API da F7/F8.

<a id="f10"></a>
**F10 — Guia de como escrever uma estratégia.** Origem: #49. Página no Docusaurus (grupo "Como Usar"): a classe base, quais métodos o usuário implementa e quais já vêm prontos, o que acontece em cada tick, uma das estratégias da F9 comentada linha a linha, e as limitações (bibliotecas disponíveis no executável, tempo máximo por tick, regra de multiplayer da D5). Gatilho: F8 concluída — a API da classe base só fica estável depois dela.

<a id="f11"></a>
**F11 — Métricas de risco do desempenho.** Origem: #5. O snapshot passou a ser diário (um por jogador por dia útil); `statistics_snapshot_update` continua saindo só na virada do mês, para a tela de Estatísticas não buscar o histórico inteiro a cada tick, e `snapshot_update` (merge por data na Carteira) sai todo dia. O `total_fixed` do snapshot vem das posições em memória do motor, como o `total_equity`, e a tabela `fixed_income_position`, que só existia para alimentá-lo, saiu do modelo. Medido em 100× com 4 jogadores: o tick foi de ~49 ms para ~64 ms (~4,5 ms por jogador). `features/statistics/risk.py` calcula em `Decimal`, a partir dos snapshots (D1) e no backend (D2), o retorno de cada dia descontado o aporte do dia, e sobre ele:
- **Drawdown máximo:** a maior queda a partir de um pico numa cota que só os rendimentos movem (como a cota de um fundo), então o aporte não disfarça a queda. Ex.: o patrimônio sobe a R$ 15.000 e cai a R$ 12.000 → 20%. Quanto menor, melhor; acima de ~30% é uma queda que a maioria das pessoas não aguenta sem vender.
- **Volatilidade anual:** desvio-padrão amostral dos retornos diários × √252. Ex.: ~1% ao ano é renda fixa; ~25% é uma carteira só de ações.
- **Índice de Sharpe:** (retorno anual − CDI anual) ÷ volatilidade anual, com o retorno anual e o CDI anual como a média diária × 252; o CDI de cada dia sai do mesmo fator diário da renda fixa. Ex.: retorno de 18%, CDI de 10%, volatilidade de 16% → 0,5. Abaixo de 0 perdeu para o CDI; perto de 1 é bom; acima de 2 é raro.

`RiskMetricsDTO` vem aninhado em cada jogador de `/api/statistics` e `/api/statistics/compare`; cada métrica é `null` enquanto a série é curta demais (drawdown a partir do 2º dia, volatilidade e Sharpe a partir do 3º; Sharpe também sem oscilação). Na tela de Estatísticas, o card "Risco da sua carteira" mostra as três com o número de dias da amostra, uma descrição curta ao lado e um tooltip com definição, exemplo e faixa boa/ruim; o ranking (e a comparação) ganhou as três colunas com o mesmo tooltip. O `FieldHint` do lobby virou `shared/components/info-hint.tsx`. Limitações: o CDI ainda é constante em `EconomicRepository`; save anterior tem só os pontos mensais antes da retomada, que entram como um "dia" de variação maior; com volatilidade perto de zero (só renda fixa) o Sharpe fica grande em módulo.
**Aceite:** numa série sintética com pico de R$ 15.000 e vale de R$ 12.000, a API retorna drawdown de 20,00% (coberto em `tests/test_statistics_risk.py`, junto com aporte que não esconde queda e volatilidade/Sharpe conferidos à mão).

<a id="f12"></a>
**F12 — Comparação entre simulações.** Origem: #84. O ranking subiu para o backend (D2): `features/statistics/ranking.py` calcula em `Decimal`, a partir do último snapshot de cada jogador, o capital aportado (saldo inicial + aportes), o retorno em R$ e em % e a posição, além da média da sala. `GET /api/statistics` passou a devolver esse relatório pronto (`PerformanceReportDTO`). `GET /api/statistics/compare?simulation_ids=…` devolve o mesmo relatório para várias simulações salvas, sem exigir partida ativa; `StatisticsRepository.get_players_history` recebe os ids e traz o nome de cada simulação. No front saíram `build-ranking.ts` e `build-match-summary.ts`. A tela de Estatísticas refaz a busca a cada `statistics_snapshot_update`. O gráfico de desempenho guarda a string original para o tooltip, que agora mostra os valores em R$. A tela `/compare-simulations` abre pelo botão "Comparar Simulações" do lobby: uma sidebar com checkbox por simulação salva, e o gráfico e o ranking com séries `Nick#Simulação`. O registro recusa `#` no nickname. Patrimônio zero passou a valer −100% de retorno. Limitação: o eixo X é a data, então simulações de períodos diferentes aparecem em trechos diferentes do eixo, não sobrepostas.
**Aceite:** marcar duas simulações salvas mostra `Lilo#Teste M1 103121` (2,18%) e `Lilo#Simulação #4` (0,00%) no gráfico e no ranking, com tooltip em R$.

<a id="f13"></a>
**F13 — Impacto de preço de ordens grandes.** Origem: #59. Ligável por partida no lobby: `price_impact_enabled`, `price_impact_k` e `price_impact_decay_days` são colunas de `simulations` (padrões em `[simulation]` do TOML), então a partida retoma com a mesma configuração. `features/variable_income/price_impact.py` é a única fórmula: a quantidade líquida do dia por ativo (compras − vendas dos jogadores, de `event_equity`) gera impacto = k × √(quantidade ÷ volume médio dos últimos 20 pregões); o impacto vale cheio no pregão seguinte e decai por (1 − t/T)², com t = 0 nesse primeiro pregão, durando T pregões. O preço do dia é o OHLC histórico × (1 + soma dos impactos ativos), piso 0,01, no centavo. Agregar por dia faz o fatiamento de uma ordem em várias execuções não mudar nada, e compra e venda iguais entre jogadores se anulam. O impacto é derivado dos eventos (D1) a cada tick, depois de um flush que leva ao banco as ordens enviadas entre ticks, então retomar reconstrói os mesmos preços. Vale na lista de ativos, no detalhe e no histórico do gráfico (cada dia com o seu fator), no market maker e no matching, na carteira e no snapshot mensal, que passou a receber do motor o valor das ações. Padrões: k = 0,02 (próximo do mercado real), T = 20. Limitações: sem migração, banco anterior à F13 fica incompatível (nova release, novo save); o histórico do detalhe recalcula o fator de cada dia a cada abertura da tela.
**Aceite:** com k = 0,02, comprar 10% do volume médio desloca o preço do pregão seguinte em +0,63% e o desvio some depois de T pregões (coberto em `tests/test_price_impact.py`).

<a id="f16"></a>
**F16 — Bots na sala.** Serve N8; segue a D8. No lobby, o host clica "Adicionar bot" e escolhe a estratégia — as prontas da F9 ou as escritas pelo usuário na F8; cada estratégia é um "tipo de IA", como as IAs do OpenTTD — e um nome. O bot é um jogador sem socket: registro em `users` marcado como bot, carteira própria, e o motor chama o `next()` da estratégia dele a cada tick, como faz com a de um humano no automático. Aparece no ranking e nas estatísticas como qualquer jogador, com um ícone que o distingue. Quem escolhe o código do bot é o host, então ele roda no processo do host qualquer que seja a D5 — a restrição da D5 é sobre código vindo de jogador remoto. Com a F13 ligada, as ordens do bot movem preço como as de qualquer jogador. Gatilho: F8 concluída.

<a id="f17"></a>
**F17 — Estatísticas em abas, como o relatório de fim de partida de um RTS.** Serve N5 e N6. Inspiração: a tela de estatísticas do fim de partida do Age of Empires II. `GET /api/statistics` e `/api/statistics/compare` deram lugar a um endpoint por aba — `/api/statistics/{overview,returns,risk,composition,operations}?simulation_ids=…` —, todos sobre os snapshots diários da F11 e sem exigir partida ativa: a tela de Estatísticas passa o id da partida em andamento, a comparação passa os escolhidos, e o fechamento (F27) vai passar o da partida encerrada. O cálculo fica em `features/statistics/` (D2), montado por `report.py`: **Geral** (ranking e resumo da partida); **Rentabilidade** (patrimônio e retorno acumulado da cota dia a dia, com o CDI e o Ibovespa da F20 como linhas tracejadas, e uma tabela com capital aportado, retorno anual composto, meses acima do CDI e meses no positivo); **Risco** (curva de distância do pico, volatilidade em janela móvel de 63 pregões, dispersão risco × retorno e a tabela com drawdown, volatilidade, Sharpe, Sortino, maior tempo abaixo do pico, pior mês e a amostra); **Composição** (área empilhada de caixa, renda variável e renda fixa, e o recorte por setor da F30: exposição de cada jogador no último dia, número efetivo de setores — 1 ÷ Σ fração² — e lucro por setor, reconstruídos de `event_equity` a preço do dia com o fator de impacto); **Operações** (volume negociado por mês, compras, vendas, giro, o IR pago da F29 e o custo de impacto da F13 — executado menos histórico, com o sinal de quem paga —, para o qual `PriceImpact.factors_on` virou público). No front, `StatisticsReport` (`features/statistics/components/statistics-report/`) serve a partida e a comparação; cada aba busca os próprios dados quando abre, e cada métrica tem descrição curta e dica com definição, exemplo e leitura (`lib/metrics.ts`). O `PerformanceChart` virou o gráfico de linha genérico das abas. A aba Geral ganha a nota com a F18. Limitações: o Sortino de uma carteira parada em caixa fica muito negativo (perde para o CDI todo dia com oscilação quase nula); na comparação, simulações de períodos diferentes aparecem em trechos diferentes do eixo.
**Aceite:** numa partida de dois jogadores com impacto ligado, as cinco abas mostram as curvas por jogador com CDI e Ibovespa de referência, Lilo com 69,84% em Financeiro e número efetivo de 1,87, e a comparação abre o mesmo relatório com séries `Nick#Simulação` (cálculos cobertos em `tests/test_statistics_{risk,returns,sectors,operations}.py`).

<a id="f20"></a>
**F20 — Indicadores reais (CDI, SELIC, IPCA) do Banco Central.** Serve N11. As constantes do `EconomicRepository` saíram: as séries moram em `economic_indicator_history` (série, data, `NUMERIC`, origem — D7), com `fetch_log` registrando tentativa e sucesso, e as antigas `ipca_history`/`selic_history`, que nada lia, foram removidas na mesma migration; `stock_price_history` também ganhou a coluna de origem. A busca segue o desenho do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): SGS do Banco Central (séries 12, 11 e 433) em janelas de até 10 anos, valor lido do texto direto para `Decimal`, e IBOV pelo yfinance (`^BVSP`) na mesma tabela. A primeira carga traz a série inteira; as seguintes recomeçam no dia 1 do mês do último valor; a inicialização dispara a busca numa thread, respeitando o intervalo de 6 horas, e falha mantém o que está no banco. Na renda fixa, o tick rende com a taxa do dia útil anterior (a taxa de um dia paga a noite até o próximo): CDI e SELIC viram o fator do dia direto, dia sem valor publicado dentro da série é feriado e não rende, o IPCA do mês se distribui pelos dias úteis do mês, e depois do último dado real vale o último valor conhecido. A projeção na compra congela o último valor conhecido. A taxa anual mostrada no card e usada pelas fábricas de títulos é a do dia composta por 252 dias úteis (IPCA: acumulado de 12 meses), e o Sharpe desconta o CDI diário real. A partida só é criada (ou carregada) quando CDI, SELIC e IPCA têm dado no dia de início. Resolve a limitação de CDI constante da F2 e da F11.
**Aceite:** um CDB 100% do CDI de 02/01/2020 a 31/12/2020 rende, antes do IR, o índice 1,02750141 que a Calculadora do Cidadão do Banco Central dá para o mesmo período (teste com o CDI real de 2020).

<a id="f21"></a>
**F21 — Central de dados, fora da partida.** Serve N13 e N3. `/import-assets` virou a Central de dados, aberta pelo botão do lobby: além dos formulários de importação por yfinance e CSV, uma tabela com toda série da base — indicadores (F20) e ações — com início, fim do dado real, fim do dado gerado (D7, vazio até a F24) e uma barra de linha do tempo por série num eixo comum, com o trecho real e o gerado em cores diferentes. Cada série se atualiza pelo botão da linha (indicador ignora o intervalo de 6 horas) e "Atualizar todos" busca os indicadores e as ações desatualizadas. A cobertura vem de `GET /api/import-assets/coverage`, numa consulta agrupada no lugar do `/status` que fazia uma consulta por ação. A Central é só de fora da partida: o router de `/api/import-assets` responde 409 com partida ativa e o guard manda `/import-assets` para `/` durante o jogo. No lobby, o período é conferido contra a cobertura: indexador sem dado na data inicial bloqueia o botão de iniciar (o backend também recusa), e série cujo dado real termina antes da data final gera um aviso. Um `Alert` entrou no design system para os dois casos.

<a id="f24"></a>
**F24 — Gerar dados futuros na Central de dados.** Serve N12; segue a D7. Na Central (F21), "Gerar dados": o usuário escolhe até quando gerar (o início é sempre o dia útil seguinte ao último dado real de cada série), a semente e a temperatura, vendo no preview como a geração fica antes de gravar; o gerador da F23 grava as linhas nas mesmas tabelas de preço e de indicadores, com origem "gerado", e a barra da linha do tempo mostra o trecho. "Atualizar" passa a trocar o trecho gerado pelo real à medida que o real fica disponível, seguindo a regra para partidas salvas que a F23 fechar. A simulação lê as séries como sempre. Gatilho: F21 e F23 concluídas.

<a id="f25"></a>
**F25 — Migrations com Alembic.** Origem: as mudanças de schema da F11 e da F13, que deixaram os bancos anteriores incompatíveis. O `create_all` saiu de `get_engine()`, e o `main.py` chama `migrate()` (`backend/core/migration.py`) antes de subir o uvicorn; `MigrationError` encerra o app com a mensagem no console (no executável, esperando um Enter). O Alembic é configurado no `pyproject.toml` (`[tool.alembic]`, com `ruff` nos hooks de escrita), `pnpm db:revision "<descrição>"` gera a revisão por autogenerate a partir dos models (D9), e o `sqlacodegen` saiu das dependências e do `.spec`. A primeira revisão (`243ae671fdc0`) é o schema atual; a v1.0.0 e bancos de desenvolvimento entre releases não migram. O `migrate` decide pelo estado do banco: vazio recebe todas as migrations; no head, nada; sem `alembic_version` e igual aos models (um banco do `create_all` atual), é marcado no head; sem `alembic_version` e diferente, é recusado; numa revisão anterior, as migrations rodam antes numa cópia (`<banco>_dryrun`, `CREATE DATABASE ... TEMPLATE`), que recusa o upgrade se alguma tabela perder linha ou célula preenchida, e depois um backup `<banco>_bkp_AAAAMMDD_HHMMSS` (ficam os 3 mais recentes) antecede o upgrade real. O `resource_path` acha `backend/migrations` em dev e no executável, que a empacota como dado. `tests/test_migrations.py` (Postgres do `.env`, banco descartável por teste, pulado sem servidor) confere que as migrations chegam exatamente no schema dos models, que toda revisão desce e sobe, o `stamp` do banco do `create_all` e a recusa do banco antigo. A página "Ciclo de desenvolvimento com banco de dados" dos docs foi reescrita para o ciclo novo, com o que o autogenerate não cobre (valor novo em `ENUM` nativo, `ENUM` no downgrade, `NOT NULL` em tabela com dado, rename). O banco local de desenvolvimento ficou preservado como `simulador_financeiro_pre_alembic`. Limitações: a cópia exige o banco sem outras conexões abertas (pgAdmin, DBeaver); a contagem de células não pega dado alterado sem ser apagado.
**Aceite:** com uma revisão de teste que adiciona coluna, um banco com 6.721 preços migra com backup e sem perder linha; uma que remove coluna com dado é recusada no ensaio e o banco fica intacto.

<a id="f19"></a>
**F19 — Modo backtest: partida só de estratégias, sem interação.** Serve N4 e N10; segue a D8. No lobby, "Rodar backtest" escolhe período, capital inicial, aporte e as estratégias participantes; cada estratégia vira um bot (F16) e a partida roda sem `sleep` entre ticks e sem eventos de socket por tick, mandando o progresso a cada N dias para a tela animar o gráfico. Ao fim, a partida fica salva como qualquer outra e abre no relatório da F17, já comparando as estratégias.

**Mercado isolado (padrão) ou compartilhado.** O backtest existe para comparar estratégias da forma mais justa e realista possível, então por padrão cada bot opera num mercado só dele: o impacto de preço da F13 é calculado a partir das ordens daquele jogador, e não da soma da sala, e o livro de ordens e a liquidez do market maker são separados por jogador. Todos veem o mesmo histórico, e só as próprias ordens movem o preço que cada um vê. Uma opção no lobby troca para mercado compartilhado, em que um interfere no preço do outro — o comportamento normal de uma partida multiplayer, que continua compartilhada sempre.

Referência de custo: o tick leva hoje ~50–100 ms (medido na F11), então 10 anos (~2.520 pregões) levam de 2 a 4 minutos — daí a animação. Medir onde vai o tempo do tick e tirar do caminho do backtest o que só serve à tela ao vivo (broadcast, snapshot por tick) faz parte. Gatilho: F16 concluída.
**Aceite:** duas estratégias idênticas, em mercado isolado e com a F13 ligada, terminam com o mesmo patrimônio.

<a id="f27"></a>
**F27 — Fechamento de partida: pódio e critério de vitória.** Serve N5, N6 e N9; segue a D8. Quando a partida chega na data final ou o host encerra, o `simulation_ended` passou a levar o id da simulação, e o `SimulationProvider` leva todos para `/match-result/:id` no lugar do toast e do lobby: o título "Fim de partida", o pódio com os três primeiros e o valor que decidiu cada posição, o relatório da F17 sobre a partida inteira (com a classificação completa e a nota na aba Geral) e "Voltar ao lobby". A rota muda antes de o status da partida ser atualizado, porque o guard tira da tela de Estatísticas quem estiver lá com a partida inativa. O fim por data passou a fazer o mesmo que o `stop()`: o flush dos eventos do último dia e a liberação da simulação antes do aviso, então o fechamento lê a partida inteira. A mesma tela abre depois, para qualquer simulação salva, pelo "Ver resultado" da lista de simulações salvas do lobby, que agora abre para todos os jogadores (carregar continua só do host). **Critério de vitória:** como as condições de vitória do Civilization VI, o host escolhe no lobby entre nota geral (padrão, F18), rentabilidade, patrimônio final ou Sharpe; é a coluna `victory_criterion` de `simulations` (ENUM, migration com `server_default` para as partidas salvas) e ordena o ranking durante a partida e o pódio, com o retorno desempatando e quem ainda não tem o valor (a nota antes de 63 pregões, o Sharpe sem oscilação) no fim. Na comparação de simulações com critérios diferentes, vale a nota geral. É diferente da tela de comparação: a comparação põe resultados lado a lado, o pódio declara quem venceu. Limitação: quem entra pelo navegador com a partida já rodando cai no lobby até recarregar a página (comportamento anterior à F27).
**Aceite:** uma partida de quatro jogadores levada até a data final leva a aba aberta em Estatísticas para `/match-result/3`, com Lilo em 1º por 285 pts de nota; uma partida encerrada pelo host abre a mesma tela pelo "Ver resultado" (ranking por critério coberto em `tests/test_statistics_ranking.py`).

<a id="f29"></a>
**F29 — IR na venda de renda variável.** Serve N7. `features/variable_income/income_tax.py` é o motor fiscal do [Finance Manager](https://github.com/LiloMarino/Finance-Manager) portado para os eventos de `event_equity`, recalculado das operações a cada consulta (D1). Todo mês, por jogador, o lucro das vendas sobre o preço médio fiscal vai para três conjuntos de compensação: comum (ação, ETF e BDR, 15%), day trade (20%) e FII (20%). Compra e venda do mesmo ativo no mesmo dia se pareiam como day trade, a 1ª compra com a 1ª venda, e só as sobras movem o preço médio, que por isso tem replay próprio, separado da posição do `Broker`. O ganho comum com ações é isento quando as vendas de ações do mês somam até R$ 20.000. O prejuízo de cada conjunto abate o lucro dos meses seguintes, e o imposto abaixo de R$ 10 soma ao do mês seguinte. No último dia útil do mês, o tick debita o DARF do mês anterior como evento `TAX` de `event_cashflow`. A retomada começa no dia seguinte ao último evento, então nenhum DARF sai duas vezes. O caixa pode ficar negativo, como uma dívida com a Receita. `stock` ganhou `asset_class` (ação, FII, ETF, BDR): na importação a classe é inferida pelo sufixo do código (31 a 35 e 39 viram BDR, 11 vira FII, o resto vira ação), e na Central de dados um seletor a corrige, porque ETFs e units também terminam em 11. A migration aplica a mesma regra às ações já importadas. A carteira mostra o card "Imposto de Renda", com o IR pago, o valor a pagar (o já apurado que não venceu, mais o mês corrente) e a regra explicada na dica. A aba Operações da F17 lê o mesmo evento `TAX` quando for feita. Limitações: a regra fiscal atual vale para qualquer período histórico simulado; o IRRF de 0,005% fica fora, porque é antecipação do mesmo imposto; e uma partida que termina antes do vencimento não debita o último mês, que fica só como "a pagar".
**Aceite:** vender R$ 30.000 em ações com R$ 5.000 de lucro num mês debita R$ 750 no mês seguinte; vender R$ 15.000 com lucro no mês não debita nada.

<a id="f30"></a>
**F30 — Setores e segmentos.** Serve N16. Mesmo modelo do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): tabelas `sectors` (nome único) e `segments` (nome único dentro do setor), com `segment_id` anulável em `stock` (`ON DELETE SET NULL`). `StockRepository.classify` cria setor e segmento pelo nome na primeira vez e apaga o que fica sem nenhuma ação, então a lista de sugestões só tem o que está em uso. Na importação, enquanto a ação não tem classificação, o `sector` e a `industry` do `yf.Ticker().info` viram a sugestão: os 11 setores do yfinance chegam nos nomes da B3 (Financial Services → Financeiro), a indústria vira o segmento como veio; a classificação feita à mão não é trocada. Na Central de dados (F21), a coluna "Setor / Segmento" abre a janela Classificar, com as sugestões de `GET /api/import-assets/sectors` (`PUT`/`DELETE /stocks/{ticker}/segment`). A carteira ganhou o card "Renda Variável por Setor" (barras e tabela de valor e fração por setor e segmento, "Sem setor" para o que não foi classificado), calculado no backend em `backend/core/sectors.py` (`PortfolioDTO.sectors`); o motor lê a classificação uma vez por partida, porque a Central só abre com a partida parada. O recorte por setor das estatísticas entra na aba Composição da F17. "A estratégia enxerga o setor" ficou para a F7/F8: o dado está em `get_classification`, e o que a estratégia vê é decidido no spike. Limitação: o segmento sugerido vem em inglês (*Banks - Regional*) até ser editado.
**Aceite:** importar ITUB4 e VALE3 pelo yfinance as classifica em Financeiro · Banks - Regional e Materiais Básicos · Other Industrial Metals & Mining, e a PETR4 classificada à mão continua como estava (coberto em `tests/test_sectors.py`).

<a id="f31"></a>
**F31 — Diagrama do banco sempre em dia.** Serve N17; segue a D9. Primeira versão do diagrama: um `erDiagram` em Mermaid por domínio, gerado dos models por `scripts/erd.py` e conferido por `tests/test_erd.py`, que falhava enquanto a página estivesse defasada. Substituída pela [F50](#f50): um diagrama só, navegável, gerado dentro do build dos docs.

<a id="f32"></a>
**F32 — Ferramenta de correlação entre ativos.** Serve N18; segue a D2.

**Onde abre.** Uma rota só, `/correlation`: na partida é o item "Correlação" da sidebar, e no lobby o card "Correlação entre ativos" a abre em tela cheia (`layouts/simulation-mode-layout.tsx` escolhe o layout pelo modo).

**Escolha dos ativos.** Até 20 tickers, agrupados por setor (`GET /api/correlation/assets` traz o setor de cada um). Há dois atalhos: "Minha carteira", na partida, e "Um de cada setor". A janela é de 6 meses, 1, 3 ou 5 anos.

**Cálculo.** `GET /api/correlation` (`features/correlation/correlation.py`) calcula a correlação de Pearson dos retornos diários de cada par com `statistics.correlation`. Cada par usa só os pregões em que os dois lados têm retorno. A resposta traz:
- a matriz completa, com o IBOV como última linha e coluna;
- os destaques entre os ativos escolhidos: o par mais parecido, o de menor correlação (o melhor para diversificar) e, na partida, a média entre as ações da carteira de quem pede.

**Par sem número.** Um par com menos de 63 pregões em comum (~3 meses) vem `null`, com `reason: insufficient_days`; um par com um lado parado na janela vem `null` com `constant_series`. O motivo aparece ao clicar no par. Fechamento inválido (NaN, zero) conta como dia sem pregão.

**Data final.** Na partida, a janela termina sempre na data da simulação, que aparece como selo. Fora dela, a data final é livre e começa no último pregão.

**Tela.**
- A matriz mostra só a metade de baixo, com o Ibovespa numa linha à parte: vermelho para positiva, azul para negativa.
- Clicar numa célula fixa o par no painel lateral, com o número, a leitura e os pregões em comum.
- A leitura segue as faixas: ≥ 0,7 andam muito juntos; 0,3 a 0,7 em parte; −0,3 a 0,3 quase independentes; ≤ −0,3 opostos.
- Se o novo cálculo falha, a matriz anterior fica na tela com um aviso e "Tentar de novo".
- Uma base sem preços leva à Central de dados.

A página "Correlação entre Ativos" dos docs explica a leitura.

**Fora da tela.** O CDI ficou de fora como referência: a taxa diária só muda quando o Copom mexe na Selic, então a correlação com ela fica perto de 0 e, numa janela com a Selic parada, nem existe. Quando a F23 existir, a mesma tela confere o gerador: o mesmo par medido num período histórico e num gerado.

<a id="f18"></a>
**F18 — Pontuação geral (overall).** Serve N9; segue a D10. Uma nota por jogador, decomposta por eixo e por métrica, na aba Geral da F17 e no ranking, que passou a ordenar por ela (quem ainda não tem nota vem depois, e o retorno desempata). `features/statistics/score.py` guarda as faixas como tabela de dados: cada métrica vira pontos numa reta entre o valor que vale 0 e o que vale 100, com chão 0 e sem teto; cada eixo é a média das suas métricas medidas, e a nota é a soma dos quatro. **Retorno:** retorno anual acima do CDI (−10 p.p. → 0, +10 p.p. → 100) e acima do Ibovespa (−15 → 0, +15 → 100). **Risco:** queda máxima (50% → 0, 0% → 100), volatilidade (40% → 0), maior tempo abaixo do pico (252 pregões → 0) e pior mês (−20% → 0). **Consistência:** fração dos meses acima do CDI e no positivo. **Eficiência:** Sharpe (−1 → 0, 2 → 100) e Sortino (−1 → 0, 3 → 100). A nota só aparece a partir de 63 pregões; antes, a aba Geral mostra quantos faltam. `ScoreDTO` vem em cada jogador de `/api/statistics/overview`, com o valor e os pontos de cada métrica, e o card "Nota" mostra cada eixo com uma barra e cada métrica como "queda máxima 13,65% → 72,7 pts". A página de estatísticas dos docs tem a fórmula em LaTeX (`remark-math` + `rehype-katex`, com o `$` simples desligado por causa do "R$"), a tabela de faixas e um exemplo completo. Limitação: risco e consistência param perto de 100 e retorno e eficiência não, então uma carteira parada em caixa fica com ~100, quase tudo do eixo Risco.
**Aceite:** na partida de teste, Lilo tem Retorno 58,3 + Risco 71,8 + Consistência 41,7 + Eficiência 40,4 = 212 e lidera o ranking; a soma dos eixos bate com o total (coberto em `tests/test_statistics_score.py`).

<a id="f33"></a>
**F33 — Indicadores técnicos.** Serve N19 e N4; segue a D2. Hoje o gráfico de ações mostra só o preço (área ou velas); os indicadores que um site como o Investing.com mostra não existem. `backend/features/technical_analysis/indicators.py` calcula, sobre o histórico de preço e volume (`stock_price_history` já guarda o volume), funções puras em pandas com parâmetros editáveis: médias móveis simples e exponencial (MMS, MME), MACD (12, 26, 9: linha, sinal e histograma), IFR (14), Bandas de Bollinger (20 pregões, 2 desvios), estocástico (14, 3), ATR (14) e OBV. Implementação própria, sem TA-Lib, que exige uma biblioteca em C no executável; cada função tem teste contra uma série curta com valores calculados à mão. `GET /api/stocks/{ticker}/indicators` devolve as séries alinhadas às datas do preço; na partida, só até a data da simulação, como na correlação (F32). No gráfico, o que se desenha sobre o preço (médias, Bollinger) vira série no mesmo painel, e os osciladores (MACD, IFR, estocástico, volume) ganham painéis próprios embaixo, que o `lightweight-charts` 5 tem nativos. Um seletor "Indicadores" liga e desliga cada um e edita os parâmetros, e cada indicador traz a dica com o que mede e como ler (IFR acima de 70 costuma ser lido como sobrecomprado, abaixo de 30 como sobrevendido). Ao lado do gráfico, um "Resumo técnico" no formato do Investing.com: o valor de cada indicador no dia e a leitura (compra, neutro, venda). As mesmas funções entram no contexto da estratégia (F8), para que a estratégia decida pelo mesmo número que aparece na tela. Uma página "Análise Técnica" nos docs explica cada indicador.

<a id="f35"></a>
**F35 — Dependências em dia.** Serve N15. Feito em dois passos, cada um fechado com `pnpm check`. (1) Versões menores: `pnpm update` no frontend e `uv lock --upgrade` no backend. (2) Versões maiores, uma por commit: Vite 8 com o `@vitejs/plugin-react` no lugar do `-swc`; ESLint 10 com `eslint-plugin-react-hooks` 7, cujas regras do React Compiler pediram ajustes (`useEffectEvent` no `useRealtime`, sem `setState` dentro de efeito); `globals`, `eslint-plugin-react-refresh` e `@types/node` atualizados. O TypeScript parou no 6: o `typescript-eslint` ainda não aceita o 7. O `framer-motion` saiu do projeto, porque o único uso era a página 404, refeita sem animação na F26. O Recharts 3 entrou na F36. Limitação: subir para o TypeScript 7 quando o `typescript-eslint` suportar.

<a id="f36"></a>
**F36 — Interface padronizada no shadcn.** Serve N15; decidiu a D11 pelo Base UI. O `components.json` está no preset `base-nova` (`@base-ui/react`), com o pacote `shadcn` importado no CSS (`@import "shadcn/tailwind.css"`, que traz as variantes `data-*` dos componentes). Os componentes de `shared/components/ui` foram recriados pela CLI, e os que faltavam entraram conforme as telas pediram: toggle-group, empty, avatar, field, radio-group, popover, progress, switch, input-group, textarea, sheet, skeleton e separator; o `form.tsx` saiu, sem uso. A CLI do registro grava `import ... from "cn"` e adiciona um pacote `cn` falso: o import é corrigido para `@/shared/lib/utils` a cada componente novo. Os `asChild` fora de `ui/` viraram a prop `render`; o Recharts foi para a versão 3. Aparência nova é sempre variante no componente, e o `@shadcn/lint` garante isso: `no-restyle` (só classes de layout por fora) e `no-raw-colors` (só tokens), que entraram como aviso durante a migração e terminaram como erro. Os 14 elementos feitos à mão viraram o componente equivalente na tela da F26 que os redesenhou.

<a id="f26"></a>
**F26 — Redesign visual.** Serve N15. O app inteiro no visual iterado no Claude Design, sobre os componentes da F36.

**Base.** Tokens só do tema claro em `frontend/index.css`: superfícies, texto, primária azul, pares de estado com fundo suave (sucesso, aviso, perigo, info), sidebar escura, velas e oito cores de gráfico validadas para daltonismo. O tema escuro ficou para a F37. As fontes IBM Plex Sans e Mono vão empacotadas via `@fontsource`, porque o executável roda sem internet; números em mono `tabular-nums`. As variantes novas no DS são: Button `dark`, `inverse`, `success`, `warning` e tamanhos de `xs` a `xl`; Badge e Alert por estado; ToggleGroup `segmented`; Tabs em trilho; Card `sm`/`lg` e `destructive`; Table com linhas `current`/`warning` e coluna `numeric`; Input `numeric`; Avatar até `2xl`; Sheet `lg`. Os estados compartilhados são o `ErrorState` (título, saída e a linha "Erro 500 · …") e os skeletons. O `ApiError` traz a mensagem em português por status.

**Shell.** Sidebar fixa em grupos (Mercado, Você, Ferramentas) com rodapé do jogador; topbar com data, pausa, velocidade segmentada e caixa; o loading avisa depois de 10 s e oferece tentar de novo; a 404 oferece uma saída só, conforme o contexto; os toasts agregam execuções seguidas e respeitam a preferência de entrada e saída.

**Telas, com o que cada uma pediu do backend.**
- Login: o conflito de nickname aparece no card, com "Sou eu, entrar".
- Lobby: status da simulação salva derivado (pausada ou terminada, a mesma regra do `SimulationLoader`, sem coluna nova), jogadores e vencedor; regras em Sheet com prévia da curva de impacto (`GET /api/simulation/price-impact-preview`).
- Central de dados: a importação devolve a série importada; `GET .../suggestion` sugere o setor.
- Carteira: o `PortfolioDTO` ganhou IR do mês com régua da isenção, setores efetivos, aportado e as frações.
- Renda variável:
  - Lista: tabela de mercado com sparkline e setor.
  - Detalhe: livro da sala e execuções lidas dos eventos (`GET .../trades`), além da boleta com prévia (`POST .../order-preview`: total, caixa depois, máximo, IR estimado).
- Renda fixa: tabela comparável pela taxa equivalente de hoje e boleta com projeção (caixa antes e depois).
- Estatísticas: colocação e distância do líder, eixo mais fraco, quadradinhos de meses, dispersão risco × retorno, mapa de calor de volume por mês e estilo de giro.
- Fim de partida: vencedor, pódio e destaques da sala (`GET /api/statistics/highlights`).
- Comparar: letra e cor por partida, "Você contra você", ranking ordenável, "Só você" e o eixo "desde o início" pelo número do pregão.
- Correlação (F32 refeita): ativos por setor, meia matriz, par fixado e destaques.
- Configurações: switches que voltam e explicam ao falhar; a exclusão só libera com o nickname digitado.
- Estratégias: página "Em desenvolvimento" com as três prévias.

**Limitações.**
- A lista do Comparar mostra o vencedor de cada partida, mas não "você em Nº", que exigiria o ranking completo de cada simulação salva.
- A variação do dia na renda variável continua intradiária, por causa do impacto de preço.
- "Encerrar" antes do fim continua salvando e saindo.

<a id="f37"></a>
**F37 — Tema escuro.** Serve N15. Hoje só existe o tema claro (F26): o `:root` de `frontend/index.css` é a única fonte dos tokens, e o `@custom-variant dark` ficou inerte.

**Plano.**
1. Desenhar o tema escuro no canvas do Claude Design, sobre as mesmas telas da F26.
2. Reescrever os mesmos tokens num bloco `.dark`, com passos próprios das mesmas rampas, sem inverter as cores claras.
3. Validar as oito cores de gráfico contra a superfície escura com o validador de paleta da skill de dataviz.
4. Fazer o `lightweight-charts` ler as cores do token (`getComputedStyle`) em vez de fixá-las, para o gráfico de velas acompanhar.
5. Criar um card "Aparência" nas Configurações, com claro, escuro ou "seguir o sistema". A escolha fica no `localStorage`, por ser preferência deste navegador; o padrão é seguir o sistema (`prefers-color-scheme`).

**Gatilho:** quando o design escuro estiver fechado no canvas.

<a id="f38"></a>
**F38 — Mensagens do backend em português.** Serve N15. O frontend mostra na tela a mensagem que o backend devolve, e parte delas ainda chega em inglês. Exemplos:
- os textos padrão das exceções HTTP em `backend/core/exceptions/http_exceptions.py` ("An upstream service failed to answer the request.");
- os erros 422 de validação do Pydantic ("Field required", "Input should be a valid integer");
- mensagens soltas de rotas e serviços.

**Plano.**
1. Traduzir os `detail` padrão de `http_exceptions.py`.
2. Registrar em `backend/routes/__init__.py` um handler de `RequestValidationError` que monta uma frase em português por tipo de erro do Pydantic (`missing`, `int_parsing`, `greater_than`...), com o nome do campo. O formato de erro que o frontend já lê continua o mesmo.
3. Varrer as rotas e os serviços (`grep` por `detail=` e pelos `raise` com texto) atrás do que sobrou em inglês.
4. Criar um teste que percorre as exceções padrão e confere que nenhum `detail` sai em inglês.

O `ApiError` do frontend já cai numa mensagem em português por status quando o backend não manda texto.

**Gatilho:** qualquer momento; não depende de outra feature.

<a id="f39"></a>
**F39 — Cor exclusiva e sigla de duas letras por jogador.** Serve N20. Inspiração: o Age of Empires II, que dá uma cor própria a cada um dos 8 jogadores da partida; aqui a sala vai a 10. Antes, a cor do jogador nascia em dois lugares que não se falavam (um hash do apelido no lobby, no perfil, na sidebar e no livro de ofertas; a posição alfabética nas estatísticas) e a sigla era a primeira letra do apelido. Agora: (1) **a cor é do jogador na partida.** Enquanto está na sala ela vive na memória do servidor (`UserManager`); ao iniciar vira linha de `simulation_players` (`simulation_id`, `user_id`, `color`, chave composta, migration pela D9), que as Estatísticas e o fechamento leem, inclusive dias depois, sem partida ativa. As partidas salvas antes ganharam as linhas na própria migration. (2) **Dez jogadores, dez cores.** `--chart-9` (cinza) e `--chart-10` (marrom) entram na paleta do redesign. O teto da sala é o tamanho da paleta e o servidor recusa o 11º conectado (423, "a sala está cheia"). A conferência de daltonismo (lima × âmbar, verde-água × ciano) continua em aberto. (3) **Conflito é impedido, não detectado.** Ao entrar o jogador recebe a primeira cor livre; a troca é `PUT /api/simulation/players/me/color` e o servidor recusa com 409 se a cor já tem dono (vale o primeiro pedido, quem perdeu fica com a anterior); o evento `player_color` avisa a sala. No seletor "Sua cor" a cor ocupada aparece apagada com a sigla de quem a tem. (4) **A preferência mora no navegador** (`localStorage`): ao entrar o cliente pede a última cor escolhida e fica com a que recebeu se ela já tiver dono. (5) **Sigla sempre de duas letras**, calculada no front por `playerInitials` (acento e emoji contam inteiros) e desenhada pelo `PlayerAvatar` de `shared/`, que substituiu os sete `Avatar` com `charAt(0)`; a sigla sai do apelido, nunca do rótulo " · A". (6) **Uma fonte de cor só no front:** `stringToColor` e `playerColors` saíram; lobby, perfil, sidebar, livro de ofertas, ranking, pódio e gráficos leem a cor do payload. A comparação de simulações segue colorindo por partida (a letra e a cor da F17), com avatares neutros. (7) **Quem participa é quem está na sala ao iniciar**: só eles recebem o depósito inicial e snapshots (antes era toda conta do banco). Quem não participa de uma partida em andamento escolhe uma cor e entra pela F58. (8) **Continuar uma partida salva tem dois passos**: o host a seleciona (`PUT /api/simulation/selection`) e a sala inteira troca para as cores guardadas, travadas para quem já jogou e reservadas para os ausentes; depois clica em Continuar. Quem está na sala e nunca jogou a partida escolhe entre as cores que sobraram e entra com o depósito inicial na retomada. Os bots da F16 não existem ainda e contarão no mesmo teto.

<a id="f40"></a>
**F40 — Modo Especialista.** Serve N21; segue a D2. Uma opção da partida no lobby, ao lado do critério de vitória, que tira as ajudas que decidem pelo jogador e o obriga a fazer as próprias contas. A filosofia é a do realismo de batalha do Total War e do Hardcore de Kingdom Come: Deliverance, que tiram da tela o que entrega a resposta. O que sai, pelo inventário de hoje: na renda fixa, a coluna e o card "Equivale hoje" (a taxa anual equivalente com CDI e IPCA do dia) e a ordenação por ela, que passa a ser por vencimento; no detalhe do título, a projeção "Quanto R$ X viram no vencimento", com o IR já descontado; e, quando existir, o "Resumo técnico" da F33 com a leitura compra/neutro/venda (os indicadores ficam). A pausa e a visão dos outros jogadores continuam como no modo normal. Guardado em `simulations` como uma coluna por ajuda (com o padrão "ligado"), por migration (D9); o lobby oferece os atalhos Normal e Especialista e mostra a lista para ajuste fino. O servidor omite os campos escondidos do DTO em vez de o front só não desenhá-los, porque no multiplayer quem abrir o DevTools veria a resposta.

<a id="f41"></a>
**F41 — Conquistas.** Serve N22; segue a D1. Um catálogo no código (`backend/features/achievements/catalog.py`): cada conquista tem código, nome, descrição, ícone (do `lucide-react`), se é secreta, e uma condição avaliada sobre os eventos e snapshots do jogador no fim de cada tick. Exemplos: primeira compra de ação; primeiro R$ 1 milhão; bater o CDI 12 meses seguidos; atravessar uma queda de 30% do Ibovespa perdendo menos que ele; vencer uma sala cheia; vencer sem assistências (F40). A conquista desbloqueada vai para a tabela `achievements` (`user_id`, `code`, `simulation_id`, `unlocked_at`), por migration (D9), e chega ao jogador por um evento do Socket.IO que abre um toast rico, no estilo da Steam: ícone, nome e descrição, com `toast.custom` do sonner. Uma tela "Conquistas" mostra as do jogador: desbloqueadas com data e partida, bloqueadas em cinza, e as secretas sem descrição até sair. As conquistas ficam no banco do host, como o resto do histórico: sem conta online, o jogador que entra na sala de outro host começa lá do zero.

<a id="f42"></a>
**F42 — Modo em equipes.** Serve N23. Cada um opera a própria carteira, mas o placar é da equipe: quem vence é a equipe, não a pessoa. O host escolhe no lobby entre todos contra todos (o de hoje) e equipes; em equipes, cada jogador escolhe a equipe numa lista ao lado da cor, como no lobby de um RTS. A equipe é uma coluna `team` na `simulation_players` da F39, por migration (D9). O valor da equipe em cada critério de vitória (F27) é a média dos membros (média da nota, do retorno, do Sharpe), para que uma equipe de três não vença uma de dois só por somar mais patrimônio. Cada jogador mantém a própria cor; a equipe aparece como um selo ao lado do nome. As telas que mudam, a desenhar no Claude Design antes de implementar: o lobby (escolha de equipe e aviso de equipes desequilibradas); o ranking ao vivo, por equipe e com os membros abaixo; as estatísticas — na aba Geral, a classificação e a nota da equipe com os eixos da nota como média dos membros; nas abas com curva, a curva da equipe (média) com as dos membros mais apagadas; em Risco, Composição e Operações, os jogadores agrupados por equipe; e o fechamento (F27), com o pódio de equipes, os membros de cada uma e o destaque de quem mais contribuiu na equipe vencedora.

<a id="f45"></a>
**F45 — Painel de desempenho.** Serve N24. Mede onde o tempo vai durante uma partida, para depois investigar só o ponto caro. O app mede sozinho, sem serviço externo: o Sentry faz essa medição por rota, mas manda os dados para fora da máquina e é pago. Um coletor em memória (`backend/core/metrics.py`) recebe: (1) **HTTP** — um middleware ASGI mede cada requisição e agrupa pela rota declarada (`/api/stocks/{ticker}`, não o ticker); (2) **Socket.IO** — o tempo de cada handler de evento recebido e, para os emitidos, quantas mensagens e quantos bytes por segundo por nome de evento, que é o que pesa no navegador em velocidade alta; (3) **tick** — quanto o motor leva para processar um dia e quanto atrasa em relação à velocidade pedida. Para cada item: chamadas, tempo total, médio, p95 (95% das chamadas levam até esse tempo; média de 20 ms com p95 de 400 ms quer dizer que de vez em quando ela trava) e o máximo, sobre as últimas 1.000 medições. Com o modo debug ligado (F54), `GET /api/debug/metrics` alimenta uma tela "Desempenho" com a tabela ordenada pelo tempo total, e as requisições lentas vão para um `slow.log`, por um logger próprio (ex.: `backend.metrics`) e uma linha `"slow.log": ("backend.metrics",)` na tabela `AREA_LOGGERS` de `logger.py` (F57), sem handler novo; cada resposta HTTP ganha o cabeçalho `Server-Timing`, que a aba Rede do DevTools já mostra. Achado o ponto, a investigação segue com o `py-spy` (`py-spy record --pid`), que gera o gráfico de chamas do processo rodando sem mudar código; uma página dos docs ensina o caminho.

<a id="f47"></a>
**F47 — Gravação automática de demonstrações.** Serve N25. Um roteiro em Playwright (`scripts/demo/`) sobe o app num banco de demonstração, importa um conjunto fixo de ativos pelo CSV (sem depender do yfinance, para sair igual toda vez), e percorre as telas: lobby, compra de ação, renda fixa, avanço do tempo, estatísticas e fechamento. Em cada passo tira screenshot, e a sessão inteira é gravada em vídeo (`recordVideo`). O `ffmpeg` corta os trechos em MP4 para os docs e o `gifski` faz GIFs curtos (até ~10 MB) para o README, que no GitHub só anima GIF. A saída vai para `docs/static/demo/`, e o comando `pnpm demo` refaz tudo a cada mudança visual, o que mantém as imagens em dia: as de hoje em `docs/static/img/` são de fevereiro, anteriores ao redesign.

<a id="f48"></a>
**F48 — README e docs que mostram o produto.** Serve N25. O README abre com um GIF do jogo rodando e, logo abaixo, o que ele faz, cada item com uma imagem ou um GIF curto da F47 (renda variável, renda fixa, estatísticas, multiplayer), o download e o link dos docs; a parte de desenvolvimento desce para o fim. Nos docs, uma página "Tour" com os vídeos, e as páginas de "Como usar" com as imagens novas. Junto, uma revisão do que está desatualizado em README e docs, página por página, contra o app de hoje. Feito com a skill de documentação (`engineering:documentation`).

<a id="f51"></a>
**F51 — Versão única e changelog.** Serve N14; segue a D12. Hoje a versão está em três lugares que não se falam: digitada à mão no `workflow_dispatch` do `release.yml` (a última tag é v1.0.0), `0.1.0` no `pyproject.toml`, e `0.0.0` nos `package.json` do frontend e dos docs; o app não sabe a própria versão. E não existe changelog: as notas da v1.0.0 são a lista automática de PRs do GitHub, com atualização de dependência do Dependabot, ilegível para quem joga. O plano: (1) **uma fonte só** — a versão mora no `pyproject.toml`, e o workflow de release a lê de lá e cria a tag, em vez de recebê-la digitada; os `package.json` são de pacotes privados que não se publicam, e o campo `version` deles sai; o backend expõe a versão. A próxima é a 2.0.0, com "Acesso antecipado" no título da release e no README (D12). (2) **A próxima versão sai dos commits** — o `git-cliff --bumped-version` calcula, e o workflow de release a mostra antes de publicar; testado em repositório descartável: só `docs:`, `refactor:` ou `fix:` dão correção (2.0.1), um `feat:` dá a menor (2.1.0), e um `!` depois do tipo dá a maior (3.0.0), até em `fix!:`; commit sem tipo não move o número. Os 109 commits desde a v1.0.0 estão todos no formato (tipo, descrição em português, sem emoji, sem escopo); os 559 anteriores, com emoji, ficam antes da tag e não entram em conta nenhuma. A única regra nova é o `!` no commit que quebra compatibilidade, que o `docs/docs/desenvolvimento/contribuindo.md` passa a trazer, junto com a tabela da D12 numa página "Versionamento" nos docs. (3) **`CHANGELOG.md` automático, sem LLM** — o `git-cliff` gera cada seção a partir dos commits desde a tag anterior: `feat:` vira "Novidades", `fix:` vira "Correções", e `docs:`, `chore:`, `refactor:`, `build:` e `test:` ficam de fora. O assunto dos commits já é escrito para ser lido (pt-BR, particípio, sem escopo), então a seção sai legível sem edição. Só a seção da 2.0.0, que cobre tudo desde fevereiro, ganha um resumo à mão no topo. Cada seção diz se as partidas salvas continuam valendo. (4) **Onde aparece** — o `CHANGELOG.md` na raiz do repositório (o GitHub o lista entre os arquivos, mas não o mostra numa aba ao lado do README); a seção da versão vira a descrição da release no GitHub, gerada pelo workflow (`git-cliff --latest`); e uma página "Novidades" nos docs, gerada no build a partir do mesmo arquivo.

<a id="f43"></a>
**F43 — Spike: outros modos de jogo.** Serve N23. Decidido com o usuário: entram a corrida à meta (F52) e o viver de renda (F53), além das equipes (F42). Ficaram de fora, por ora: eliminação (a cada trimestre o último sai, até sobrar um), cenário com objetivo (começar numa crise histórica com uma meta, como uma campanha de RTS) e todos contra o índice (a sala inteira numa equipe contra o CDI e o Ibovespa).

<a id="f52"></a>
**F52 — Modo corrida à meta.** Serve N23. Vence quem chega primeiro a um patrimônio-alvo, como a vitória por Maravilha do Age of Empires. O host define a meta no lobby (por padrão, 10 vezes o capital inicial), guardada numa coluna `goal_net_worth` em `simulations`, e o critério de vitória da F27 ganha o valor "Primeiro a chegar à meta" (valor novo no `ENUM` nativo `victory_criterion`, com `ALTER TYPE ... ADD VALUE` à mão na migration, D9). No fim de cada dia, depois dos snapshots, o motor confere quem passou da meta; o primeiro encerra a partida e leva ao fechamento (F27). Dois no mesmo dia: vence o maior patrimônio. Se a data final chega sem ninguém na meta, vence quem estiver mais perto. A meta é em reais do dia, sem descontar inflação; numa partida de décadas, isso fica explicado ao lado do campo. A topbar mostra a barra de progresso de cada jogador até a meta. Em equipes (F42), a equipe chega à meta pela média do patrimônio dos membros.

<a id="f53"></a>
**F53 — Modo viver de renda.** Serve N23. Uma corrida à meta (F52) em que a meta é a independência financeira, e o caminho tem a vida real no meio. O host define no lobby o salário e a despesa mensal (o aporte de hoje vira a diferença entre os dois) e a frequência dos imprevistos. Imprevistos são despesas inesperadas (conserto, saúde, demissão de um mês sem salário), sorteadas com uma semente da partida, para que todos os jogadores recebam os mesmos imprevistos nos mesmos dias. Eles saem do caixa; caixa negativo paga juros de cheque especial até ser coberto, o que obriga a ter reserva de emergência em algo que se resgata rápido. Salário, despesa e imprevisto entram como valores novos do `ENUM` `cashflow_event_type` (à mão na migration, D9). Vence quem primeiro atinge o patrimônio da regra dos 4%: 25 vezes a despesa anual (com R$ 5 mil de despesa por mês, R$ 1,5 milhão), porque retirar 4% ao ano desse patrimônio cobre as despesas, e o estudo Trinity, com dados dos Estados Unidos, mostrou essa retirada, corrigida pela inflação, durando 30 anos na maior parte dos períodos históricos. A taxa de retirada é configurável, e a explicação fica ao lado do campo. Quando os proventos existirem (F22), a meta pode passar a ser a renda passiva real (dividendos e juros recebidos cobrindo a despesa).

<a id="f54"></a>
**F54 — Modo debug.** Serve N24. Hoje há dois modos implícitos: no `pnpm dev`, o Vite roda em desenvolvimento, as ferramentas do TanStack Query aparecem e o `logger.ts` loga tudo; no executável, o front é o build de produção, de onde o `ReactQueryDevtools` sai sozinho. Falta o meio: ligar as ferramentas no executável, para investigar lentidão na máquina de quem joga, e desligá-las no dev, para ver o app como no executável. Um modo só, independente de como o app roda: `[debug] enabled` no `config.toml` (e `--debug` na linha de comando), ligado por padrão fora do executável e desligado nele. O backend o expõe em `/api/settings`. Ligado, ele: carrega as ferramentas do TanStack Query também no build de produção, por import dinâmico do build de produção delas, como a documentação do TanStack ensina; liga o painel de desempenho (F45) e o item dela no menu; e sobe o nível do `app.log` e dos arquivos por área da F57 para `DEBUG` (o `setup_logging` já recebe o nível; o `config.toml` e o `--debug` o decidem no boot), com o `error.log` seguindo só com `ERROR`. Não há "staging": o projeto não tem servidor publicado, só quem roda o próprio executável.

<a id="f56"></a>
**F56 — Novidades no app.** Serve N14. Como as notas de patch de um jogo: o `CHANGELOG.md` da F51 vai junto no executável, o backend o serve com a versão, e o lobby mostra as novidades da versão atual. Na primeira abertura depois de atualizar, o card ou o selo de novidades fica em destaque até ser aberto (o navegador guarda a última versão vista); aberto, mostra "O que há de novo na versão X" e dá acesso ao histórico inteiro. O lugar exato no lobby, que já está cheio, sai de uma iteração no Claude Design antes de implementar.

<a id="f57"></a>
**F57 — Logs separados por assunto.** Serve N26. Hoje o `setup_logging` (`backend/core/logger.py`) manda tudo para o console e para um `app.log` só (rotativo, 10 MB por arquivo, 5 arquivos), então um erro fica no meio das linhas de uma partida inteira: o `app.log` de uma sessão de desenvolvimento tem 3.541 linhas, 12 delas de erro, e seis dessas são de uma única busca no yfinance por um ticker que não existe. Inspirado nos logs da Paradox, que guardam um arquivo por assunto e um `error.log` só com os erros. O plano: (1) **`error.log`** — só `ERROR` e `CRITICAL`, com o traceback completo que `logger.exception` já gera, rotativo como o `app.log`; ficam de fora dele as bibliotecas que tratam falha esperada como erro (o `yfinance` para ticker inexistente), por filtro de prefixo de logger; a linha continua no `app.log`, e o importador loga a própria mensagem de erro, que é a que entra no `error.log`. (2) **Um arquivo por área**, escolhido pelo prefixo do nome do logger e com o mesmo formato de linha: `simulation.log` (motor, ticks, ordens), `realtime.log` (Socket.IO e SSE), `import.log` (yfinance e BCB) e `database.log` (migrations e banco). Cada linha vai para o arquivo da área e para o `app.log`, que segue como o registro completo e cronológico. A tabela "arquivo → prefixos de logger" mora só em `logger.py`; área nova é uma linha. (3) **O uvicorn passa a escrever nos mesmos arquivos.** Hoje o `uvicorn.run` instala a configuração de log própria dele, com `propagate` desligado, então as mensagens do servidor (início, erro de protocolo do WebSocket) saem só no console e não existem no `app.log`. Com `log_config=None` os loggers dele sobem para o raiz e entram em `app.log` e `error.log`; o `uvicorn.access`, uma linha por requisição, fica em `WARNING` para não encher o arquivo. A F54 (modo debug) sobe o nível do `app.log` e dos arquivos por área para `DEBUG`, com o `error.log` seguindo só com erros, e a F45 manda as requisições lentas para um `slow.log` com uma linha a mais nessa tabela. **Aceite:** uma exceção provocada numa rota deixa o traceback no `error.log`, uma partida inteira sem falha o deixa vazio, e uma queda do WebSocket por erro de protocolo aparece no `app.log`.

<a id="f50"></a>
**F50 — Diagrama do banco navegável.** Serve N17; segue a D9. A página "Diagrama do Banco de Dados" tem um diagrama só, com zoom, arraste, busca e os ENUMs numa tabela abaixo, no [ERD Editor](https://github.com/dineug/erd-editor) (`@dineug/erd-editor` 4.0, MIT) embutido como componente do Docusaurus. **100% gerado, sem passo manual:** `scripts/erd.py` lê o `Base.metadata` e escreve o DDL do Postgres (`CreateTable` do SQLAlchemy) em `docs/src/generated/schema.json` e a tabela dos ENUM em `docs/docs/desenvolvimento/_enums.md`; os dois rodam no `prestart`, `prebuild` e `pretypecheck` dos docs (`pnpm db:erd`) e no `deploy-docs.yml`, que ganhou `uv sync` e passou a disparar também por mudança em `backend/core/models/**`. Os arquivos gerados não são versionados, e o `tests/test_erd.py` saiu. O componente `DatabaseDiagram` (`BrowserOnly`) cria o `<erd-editor>`, carrega o DDL com `setSchemaSQL(..., { placement: 'auto' })`, enquadra o diagrama inteiro no zoom inicial e segue o tema claro/escuro do Docusaurus. O editor abre editável e nada é salvo: arrastar tabelas, reorganizar e esboçar uma modelagem ("e se fosse 1-N aqui?") valem só até recarregar, quando o diagrama volta ao schema dos models. **A escolha:** os dois visualizadores foram prototipados sobre o schema de hoje. O React Flow desenhava a notação do MySQL Workbench, mas as linhas se embaraçavam perto das tabelas de evento e foco numa tabela, layout automático e busca teriam de ser construídos. O ERD Editor traz isso pronto (foco numa tabela e nas vizinhas com `Alt+F`, *Auto Layout* por Force, Flow ou árvore, só as colunas de chave, busca por tabela e coluna), e a notação do Workbench foi dispensada: as chaves vêm coloridas (PK amarela, FK vermelha, PK que também é FK azul) e a obrigatoriedade aparece em texto. O modo somente leitura do editor trava também o arrasto, por isso ele não é usado. Limitação: o layout inicial ainda embaraça as linhas perto das tabelas de evento; *Auto Layout* → *Force* (`Ctrl+K`) as separa. O pacote pesa cerca de 11 MB, carregados só na página do diagrama.
**Aceite:** alterar um model e subir `pnpm start` nos docs mostra a mudança no diagrama sem rodar nada à mão.

<a id="f58"></a>
**F58 — Entrar no meio da partida (hot-join).** Serve N27. Antes só participava quem estava na sala ao iniciar (F39): quem chegava depois, com conta nova ou antiga, era barrado com 423 "a partida já começou". Agora: (1) **A vaga é do participante, online ou não.** A partida em andamento tem no máximo 10 participantes (linhas de `simulation_players`, o teto da paleta); quem jogou e saiu continua dono da vaga e da cor, então uma partida de 10 com seis offline está cheia e o 11º leva 423 ("a partida já tem 10 jogadores, 6 deles offline"). (2) **Quem chega entra "pendente".** `register`, `claim` e `/session/me` deixam de barrar: a sessão volta com `pending_join` e o front manda para a tela `/join`, sem cor e fora de `UserManager._active_players`. (3) **`/join` mostra quem joga (online ou offline), as cores livres e o saldo inicial.** A lista vem de `GET /api/simulation/match-players`; a cor já marcada é a preferência do navegador, se estiver livre, senão a primeira livre. (4) **`POST /api/simulation/join` vale o primeiro pedido.** Sob o mesmo lock `UserManager.join_match` confere o teto e a cor (409 "X pegou essa cor antes") e grava a linha; `Simulation.add_player` deposita o `starting_cash` pelo `add_cash` do motor, datado do dia corrente, e cria o snapshot do dia. O jogador entra no ranking e nas estatísticas. O aporte mensal vale só dali em diante: o ranking por retorno é comparável, mas o por patrimônio absoluto reflete a data de chegada. (5) **Quem sai e volta mantém a cor da partida.** (6) **A mesma conta de vagas vale para a partida salva.** O lobby desenha os ausentes da partida selecionada (cartão tracejado com a cor reservada), marca "Novo" em quem nunca jogou, conta presentes mais ausentes no `N / 10` e mostra o aviso de quem entra com o saldo inicial. Partida que não comporta a sala (jogadores da partida mais novatos passando de 10) não é selecionável: o diálogo de partidas salvas desabilita o "Selecionar" e diz o motivo com os nomes (`room_overflow`), e o servidor recusa com 409 citando os mesmos nomes. Com espaço para os novatos, a seleção segue normal. Quem resolve o excesso hoje é o próprio jogador saindo da sala (F61).
**Aceite:** com a partida em andamento e vaga, um jogador novo escolhe uma cor livre, recebe o depósito inicial e aparece no ranking; com 10 participantes, online ou não, ele continua barrado; uma partida salva de 10 jogadores não é selecionável com um novato na sala, e uma de 8 é com dois.

<a id="f61"></a>
**F61 — Host remove jogador da sala.** Serve N28. Hoje a vaga só abre quando o jogador sai por conta própria: com a sala cheia ou a partida salva recusada por causa de novatos (F58), o host tem de pedir pelo chat para alguém fechar a aba. O plano: um botão "Remover" no cartão de cada jogador do lobby, só para o host, que encerra a sessão do jogador pelo mesmo caminho do `player_logout`, com um aviso "o host te removeu da sala" na tela dele, e libera a cor e a vaga na hora. Fica em aberto se a remoção também vale para participante offline da partida em andamento; a leitura provável é que não, porque tirar a linha de `simulation_players` apaga o saldo e o histórico dele.

<a id="f62"></a>
**F62 — Uma migration inicial só para a 2.0.0.** Serve N14; segue a D9. Hoje `backend/migrations/versions/` tem seis arquivos, todos de outubro de 2026 (a inicial, os indicadores econômicos, a classe do ativo e o IR, setores e segmentos, o critério de vitória e a cor por jogador), escritos durante o desenvolvimento. Nenhum executável publicado os conhece: a v1.0.0 criava as tabelas com `create_all` e não guarda `alembic_version`. Condensá-los agora é de graça, porque ninguém tem um banco em revisão intermediária; depois da 2.0.0 nenhum banco de jogador pode ficar sem caminho de upgrade, e a cadeia passa a só crescer. O plano: no último passo antes da release, depois de a F4 fechar o banco e de qualquer outra mudança de schema da 2.0.0, apagar os seis arquivos e gerar uma inicial só, por `pnpm db:revision "create initial schema"` contra um banco vazio, revista à mão: os `ENUM` nativos, o `server_default` do JSONB e, no `downgrade`, o drop explícito de cada `ENUM`, que o autogenerate não faz. O `tests/test_migrations.py` confere que a inicial chega no schema dos models e que sobe e desce. O banco de desenvolvimento aponta para uma revisão que deixa de existir: troca-se o `alembic_version` pela nova (ou recria-se o banco), e o mesmo vale para os bancos de teste de quem experimentou builds anteriores. **Aceite:** um banco novo chega ao schema dos models só com a inicial, e `tests/test_migrations.py` passa.

<a id="f63"></a>
**F63 — Sugestão de código ao digitar o ativo.** Serve N13. Mesma ideia do [Finance Manager](https://github.com/LiloMarino/Finance-Manager): no campo "Código do ativo" do painel Adicionar ativo (fonte yFinance), a pessoa digita e a lista já mostra os códigos válidos com o nome da empresa, em vez de descobrir o erro só depois de tentar importar. Backend: `GET /api/import-assets/tickers?q=` (no router da Central, que já responde 409 com partida ativa) chama `yf.Search(q, max_results=20, news_count=0, lists_count=0).quotes`; abaixo de 2 caracteres devolve `[]` sem consultar a fonte, e falha da fonte vira 503. O filtro é o da B3: bolsa `SAO`, símbolo terminado em `.SA` e nome no formato `[A-Z0-9]{4}\d{1,2}` (PETR4, KNRI11); o `.SA` sai, repetidos saem e a ordem do Yahoo fica. Frontend: o `Input` do painel vira um campo com `Popover` + `Command` do design system, com debounce de 300 ms, `useQuery` com `staleTime: Infinity` por texto buscado e setas/Enter/Escape. A sugestão não restringe: o texto digitado continua valendo, então `BTC-USD` e o código tirado do nome do CSV seguem funcionando. A lista só aparece com a fonte yFinance; no CSV o campo fica como hoje. Limitação: códigos de fora da B3 não aparecem na lista, só digitados à mão.
**Aceite:** digitar "petr" lista PETR3 e PETR4 com o nome da Petrobras; um provider falso cobre filtro, `.SA`, repetidos e o corte de menos de 2 caracteres em `tests/`.

<a id="f64"></a>
**F64 — Cache do perfil do ativo no yfinance.** Serve N13 e N16. Hoje cada importação de ativo ainda sem classificação chama `yf.Ticker(ticker).info` de novo (`fetch_info` em `importer_service.py`), inclusive no "Atualizar todos", e o ativo que o yfinance devolve sem setor (ETF, cripto) é reconsultado toda vez. O [Finance Manager](https://github.com/LiloMarino/Finance-Manager) guarda isso numa tabela `ticker_profiles` e só vai à fonte quando não há linha. Aqui: tabela `ticker_profile` (`ticker` como chave, `name`, `quote_type`, `sector`, `industry`, `fetched_at`), criada por migration do Alembic (D9) e lida por `fetch_info` antes da rede: com linha, usa a linha; sem linha, consulta o yfinance e grava a resposta, inclusive a vazia, para o ETF sem setor não ser reconsultado. `infer_asset_class`, `suggest_segment` e o nome do ativo passam a ler o perfil guardado. Sem expiração: setor e indústria quase não mudam, e a classificação feita à mão continua mandando sobre a sugestão. Se o yfinance falhar, nada é gravado e a importação segue sem sugestão, como hoje. Um botão "Atualizar perfil" na janela Classificar da Central refaz a consulta de um ativo. Se a F63 mostrar setor ao lado da sugestão, lê desta mesma tabela.
**Aceite:** importar o mesmo ativo duas vezes chama o yfinance para o perfil uma vez só, e "Atualizar todos" não consulta o perfil de ativo já guardado (coberto em `tests/` com `fetch_info` falso contando chamadas).

<a id="f3"></a>
**F3 — Spike: banco embarcado no executável.** Decidiu a D4: Postgres oficial embarcado no executável do Windows. A medição usou um harness descartável que roda a `Simulation` real com 10 jogadores e threads gravando em paralelo, como requisições HTTP, sobre o Postgres e o SQLite, com os preços do banco de desenvolvimento (19.919 linhas) e uma variante de 100 ações (664 mil linhas); mais um executável de teste com o servidor embarcado, o app completo empacotado com um pacote de Postgres embarcado e o zip oficial da EDB extraído, iniciado e parado sem instalação. Os números e os argumentos estão na D4. Limitações: sobrecarga e 100 ações têm uma repetição cada; o Postgres rodou com a configuração padrão; o tempo de abertura do app completo e a máquina limpa (runtime do Visual C++) não foram medidos e ficam para o aceite da F4.

---
## 2. Nice-to-have

| ID | Resumo | D# | Marco | Depende de | Esforço | Risco | Valor | Custo-benefício | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **F14** | Janela desktop nativa | — | — | — | Baixo | Baixo | Baixo | Bom | 💤 Registrado, sem prioridade |
| **F46** | Console do navegador no terminal do dev | — | — | — | Baixo | Baixo | Baixo | Bom | ✅ Concluído |
| **F60** | Modo servidor dedicado (--headless) | — | — | — | Baixo | Baixo | Baixo | Bom | ⏳ Pendente |

<a id="f14"></a>
**F14 — Janela desktop nativa.** Troca o `webbrowser.open` de `main.py` por uma janela própria via `pywebview`, que usa o WebView do sistema operacional (WebView2 no Windows 10/11, já instalado) e é Python puro — entra no mesmo executável do PyInstaller sem toolchain nova. O uvicorn sobe numa thread e a janela aponta para `localhost`; se o WebView do sistema faltar, cai para o navegador como hoje. Flag no TOML para escolher. Não serve nenhuma necessidade listada (o jogo já funciona no navegador); o ganho é parecer um app desktop. Os convidados do multiplayer continuam entrando pelo navegador.

<a id="f46"></a>
**F46 — Console do navegador no terminal do dev.** O Vite 8 tem `server.forwardConsole`; em `frontend/vite.config.ts` ele está ligado com `{ unhandledErrors: true, logLevels: ["error", "warn"] }`. No `pnpm dev`, `console.error`, `console.warn`, exceção não tratada e promessa rejeitada sem tratamento aparecem no terminal do Vite como `[vite] (client) [console.error] ...`, as duas últimas com o trecho do código de origem; `console.log` fica de fora. Vale para o desenvolvimento, não para o executável. O ganho principal é para o agente de código, que lê o terminal mas não o console do navegador.

<a id="f60"></a>
**F60 — Modo servidor dedicado (`--headless`).** O mesmo executável, sem o navegador: para rodar numa VPS ou num PC ligado direto, sem ninguém jogando nele. `--headless` na linha de comando, ou `[server] headless = true` no `config.toml`, pula o `webbrowser.open` do `main.py`, que hoje roda sempre que o app é o executável, e imprime no terminal os endereços para entrar (o da rede local e, com a F6, o do túnel). O administrador é quem entra com o apelido de `[host] nickname`, que é como o host é definido hoje (`routes/simulation.py`). Como a recuperação de login é por apelido, num servidor exposto à internet qualquer um que digite esse apelido viraria o host; por isso, no modo servidor, o `config.toml` ganha `[host] pin`, e o login com o apelido do host só passa com ele. Serve a quem quer deixar uma sala aberta para os amigos entrarem quando quiserem, sem depender de o host estar com o computador ligado jogando.

---
## 3. Descartada

| ID | Resumo | N# | Status |
| --- | --- | --- | --- |
| **F15** | Cliente desktop em Tauri | — | 🚫 Descartado |
| **F59** | Separar em dois executáveis: cliente e servidor | N2 | 🚫 Descartado |

<a id="f15"></a>
**F15 — Descartado.** 🚫 O núcleo do Tauri é Rust: o backend Python iria como sidecar (o executável do PyInstaller dentro do pacote Tauri), o que dá dois executáveis, toolchain Rust nas três plataformas da CI e um WebView diferente em cada SO. O ganho — janela própria em vez de aba do navegador — é o mesmo da F14, que faz isso em Python dentro do executável atual. Electron daria o mesmo resultado com ~150 MB de Chromium a mais. Em qualquer dos dois, os convidados do multiplayer continuam no navegador.

<a id="f59"></a>
**F59 — Descartado.** 🚫 Separar o app em dois executáveis, um cliente e um servidor. Hoje o app já é cliente e servidor: o executável é o servidor, e o navegador é o cliente, que o próprio servidor entrega pronto. Separar não traz nada que isso não dê, e custa três coisas: (1) os convidados do multiplayer teriam de baixar um programa em vez de abrir um link, o que fere a N2; (2) quem hospeda passaria a abrir dois programas, e a versão do cliente teria de combinar com a do servidor, coisa que hoje é garantida porque o front vai dentro do servidor; (3) a CI geraria o dobro de artefatos nos três sistemas. O Tauri não muda a conta: o Rust nas três plataformas e o motor web diferente em cada sistema continuam (F15), e o ganho de uma janela própria é o da F14, em Python, dentro do executável atual. O que a ideia buscava, um servidor sem jogador na frente, é a F60.

---
## 4. Incerta / exploratória

| ID | Resumo | Conexão | Marco | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| **F5** | Spike: provider de túnel pela internet | Serve N2; escolhe o provider da F6 | M3 | — | 🔍 Em avaliação |
| **F7** | Spike: estratégia Python escrita pelo usuário | Serve N4; decide D5 | M4 | — | 🔍 Em avaliação |
| **F22** | Preço ajustado e proventos | Serve N3, N7; degrau falso na atualização incremental | M8 | — | 🔍 Em avaliação |
| **F23** | Spike: gerador de séries sintéticas | Serve N12; fecha o método e o contrato da F24 | M9 | [F20](#f20) | 🔍 Em avaliação |
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
