# Decisões e necessidades — Simulador Financeiro

> Companion do [`ROADMAP.md`](ROADMAP.md). Aqui mora o **porquê**: as necessidades (`N#`) que motivam o trabalho e as decisões transversais (`D#`) que condicionam as features. O **o quê** — features (`F#`), marcos (`M#`) e o estado de cada uma — mora no `ROADMAP.md`, gerado por script.
>
> **IDs:** `N#` necessidade · `D#` decisão transversal · `F#` feature · `M#` marco.
> **Sincronização:** criar ou alterar um `N#`/`D#` aqui exige espelhar no `ROADMAP.md` (`upsert-ref`) na mesma mudança.
>
> **Última mudança:** registrada a N18 (correlação entre ativos); D9 decidida: o schema nasce dos models.

---

## Contexto

Simulador de investimentos do mercado brasileiro em formato de jogo (inspirado em Capitalism Lab / Victoria 3): o tempo avança em ticks diários sobre dados históricos reais, e o jogador opera renda variável (ações, FIIs, ETFs, via book de ordens com liquidez simulada) e renda fixa (CDB, LCI, LCA, Tesouro). Um jogador hospeda a partida e os outros entram pelo navegador; o ranking é pelo patrimônio.

**O que já existe** (as issues fechadas): backend FastAPI + Socket.IO servindo um SPA React; multiplayer com host/cliente e ranking; renda variável com matching engine e market maker; renda fixa com indexadores reais (CDI, IPCA); aporte mensal; controles de tempo; importação de ativos (yfinance/CSV) com atualização de defasados; histórico de simulações salvas; executável multiplataforma com release por CI; documentação Docusaurus.

**Filosofia do produto:** baixar o executável e jogar — *out-of-the-box*, sem instalar nem configurar nada. Hoje ela está quebrada num ponto: o executável exige PostgreSQL instalado (o suporte a SQLite foi removido no PR #82 porque manter os dois dialetos custava caro).

**Para que serve, no fundo:** testar estratégias *hands-off* e checar hipóteses de investimento antes de acreditar nelas. A inspiração é o [backtrader](https://www.backtrader.com/) — backtest por código — com a diferença de que aqui a simulação também se joga, por uma interface amigável.

**Escopo:** mercado brasileiro; o host roda tudo localmente, sem servidor central.

---

## Necessidades

**N1. Baixar o executável e jogar, sem instalar nem configurar nada ⭐**
É a promessa do projeto. Cada pré-requisito (instalar Postgres, criar senha, editar `.env`) é um ponto em que um amigo convidado desiste antes da primeira partida.

**N2. Jogar com amigos pela internet sem que cada um instale uma VPN**
Hoje o multiplayer fora da rede local depende de todos instalarem a mesma VPN (Radmin). O host deveria conseguir mandar um link e pronto.

**N3. Confiar que os números do simulador são exatos e reprodutíveis**
O valor mostrado na tela tem que ser o valor guardado, e uma simulação pausada e retomada outro dia tem que chegar ao mesmo resultado que rodada de uma vez. Num simulador, número que não bate invalida o resto.

**N4. Testar uma estratégia de investimento automática e ver como ela se sai**
Escrever a lógica de decisão (quando comprar, quando vender) e deixar o simulador executá-la enquanto o tempo passa, sem operar na mão.

**N5. Saber quanto risco foi corrido para chegar num resultado**
Retorno sozinho não diz se a estratégia foi boa: ganhar 20% passando por uma queda de 50% no meio do caminho é diferente de ganhar 20% de forma estável.

**N6. Comparar resultados de simulações diferentes**
Pôr lado a lado o desempenho de partidas distintas (a mesma pessoa em duas simulações, duas estratégias em períodos iguais).

**N7. Que o simulador cobre os custos de operar do mercado real**
Uma ordem enorme num ativo pouco negociado move o preço contra quem compra. Sem isso, a estratégia que ganha no simulador pode não valer nada fora dele.

**N8. Jogar contra oponentes controlados pelo computador**
Ter adversários na sala sem precisar de amigos online, escolhendo o "tipo" de cada um — como o seletor de IA de um jogo de estratégia, ou as IAs baixáveis do OpenTTD, em que cada IA é uma heurística diferente.

**N9. Saber num número só quem jogou melhor, pesando retorno e risco — e entender de onde vem esse número**
Ranking por patrimônio ignora o risco corrido. Uma nota geral resume, e a decomposição por dimensão (rentabilidade, risco...) mostra por que a nota é aquela, como a tela de fim de partida de um RTS.

**N10. Testar uma hipótese de estratégia num período inteiro sem esperar o tempo do jogo**
Rodar uma ou mais estratégias automáticas de ponta a ponta, sem interação, e ver o resultado comparado em minutos — o uso de backtest, com a interface do simulador.

**N11. Que o cenário econômico simulado seja o histórico real**
CDI, SELIC e IPCA de cada dia têm que ser os que de fato vigoravam. Com indicador constante, a renda fixa, o Sharpe e qualquer comparação contra o CDI medem um mundo que não existiu.

**N12. Continuar jogando depois do último dia com dado real**
Hoje, passado o último pregão importado, o preço congela no último fechamento. O mercado deveria continuar se mexendo de forma plausível, para a partida poder ir além do presente.

**N13. Saber que dados a base tem e mantê-los atualizados, fora da partida**
Ver de onde vem cada série (ativo, indicador), até quando ela é real e até quando é gerada, e atualizar uma ou todas — antes de jogar, sem que os dados de uma partida mudem por baixo dela.

**N14. Atualizar para uma versão nova sem perder as partidas salvas**
Hoje toda mudança no banco (F11, F13) obriga a começar de um banco novo: a release nova não abre o banco da anterior. Cada feature que mexe no schema custa os saves de quem já joga.

**N15. Usar uma interface agradável e coerente, à altura de um jogo**
A interface amigável é metade da proposta — é o que separa o simulador de um backtest por código. Cada tela nova (bots, backtest, fechamento, central de dados) precisa nascer no mesmo visual.

**N16. Ver a carteira e o mercado por setor e segmento**
Saber quanto está em bancos, em energia, em varejo; e poder escrever estratégias que decidem por setor.

**N17. Enxergar a estrutura do banco e esboçar mudanças nela**
Ter uma visão do schema atual — tabelas, colunas, relações — para entender o que existe e conversar sobre uma modelagem nova ("e se fosse 1-N aqui?") antes de virar código.

**N18. Saber quanto os ativos andam juntos antes de montar uma carteira ou estratégia**
Diversificar só funciona entre ativos que não caem juntos. Sem medir isso, duas posições "diferentes" podem ser a mesma aposta.

---

## Decisões

### D1 — Eventos são a fonte da verdade; snapshots são derivados
**Status:** ✅ Decidida

**Decisão:** Toda operação (compra, venda, resgate, aporte, rendimento) é gravada como evento imutável. O patrimônio por dia (snapshot) é calculado a partir dos eventos e pode ser reprocessado.
**Por quê:** é o modelo adotado na #50 e já implementado. Snapshot com bug se recalcula; evento perdido não se recupera. Mudar uma fórmula de cálculo não corrompe o histórico.
**Consequências:** qualquer estado que precise sobreviver a uma retomada (juros acumulados de renda fixa, por exemplo) tem que ser reconstruível a partir de eventos, nunca só existir em memória. Métricas e comparações leem snapshots.

### D2 — Cálculo financeiro acontece só no backend; o frontend exibe
**Status:** ✅ Decidida

**Decisão:** Montante, juros, projeções, retorno e métricas de risco são calculados no backend e entregues prontos. O frontend formata e exibe; não recalcula.
**Por quê:** a #85 descreve o sintoma de ter duas implementações: o JS do front projeta juros de um jeito e o backend credita de outro, e "cada um tem uma verdade sobre o dado". Uma fórmula só não diverge.
**Consequências:** toda tela nova que precisa de um número derivado ganha um campo no DTO em vez de uma função no front. O custo é um round-trip a mais em telas que poderiam calcular localmente.

### D3 — Dinheiro e quantidade trafegam como Decimal serializado em string
**Status:** ✅ Decidida

**Decisão:** Valores `Decimal` do backend chegam ao frontend como string e são formatados a partir da string, sem passar por `number`.
**Por quê:** o banco guarda `NUMERIC(20,6)`; converter para `float` no backend (ou `number` no JS) perde casas decimais e acumula erro (#86). Formatar a partir da string preserva exatamente o que foi persistido.
**Consequências:** formatadores do front (`formatMoney` e afins) passam a aceitar string; cálculo com esses valores no front deixa de existir (ver D2).

### D4 — Banco de dados embarcado no executável
**Status:** 🔍 Em aberto

**Decisão:** em aberto entre três finalistas, decidido pela F3:
1. **Só SQLite** — o executável cria um arquivo e funciona; o Postgres sai do projeto. Um dialeto só, mas troca JSONB por JSON.
2. **SQLite padrão + Postgres opcional** — o que existia antes do PR #82. Atende N1, mas devolve o custo de manter dois dialetos que motivou a remoção.
3. **Postgres embarcado** — binários do Postgres empacotados e iniciados pelo próprio executável. Um dialeto só, mas o executável engorda e o startup fica mais lento.

**Por quê está aberto:** a remoção do SQLite resolveu uma dor de manutenção e criou a quebra de N1. A escolha depende de números (tamanho do executável, tempo de startup, concorrência de escrita com vários jogadores) que ainda não foram medidos.

### D5 — Onde roda o código de estratégia escrito pelo usuário
**Status:** 🔍 Em aberto

**Decisão:** em aberto entre dois finalistas, decidido pela F7:
1. **Dentro do processo do host** — o simulador carrega o `.py` (de uma pasta ou salvo no banco) e chama `next()` a cada tick. Simples e determinístico; mas código Python não tem sandbox confiável, então só o host pode carregar estratégias — estratégia de jogador remoto seria execução de código arbitrário na máquina do host.
2. **Como cliente da API, na máquina do jogador** — a estratégia é um bot que roda localmente e opera pelas mesmas rotas que a interface usa. Funciona no multiplayer sem risco para o host; mas o tick não espera o bot, e a estratégia passa a depender de latência de rede.

**Por quê está aberto:** a ideia (#2, #12, #49) é a estratégia ser 100% código do usuário, e o multiplayer é parte central do jogo. As duas opções cobrem metade cada uma; o spike mede se dá pra ter as duas ou qual metade vale mais.

### D6 — A retomada continua no dia seguinte ao último evento
**Status:** ✅ Decidida

**Decisão:** Uma simulação retomada continua no dia útil seguinte à data mais recente entre os eventos e os snapshots dela. Os eventos pendentes são gravados ao parar a simulação.
**Por quê:** segue da D1 — um dia sem evento não mudou nada persistido, então reprocessar os dias depois do último registro chega ao mesmo estado em que o jogador parou, sem coluna nova no banco. A alternativa (gravar o último dia simulado numa coluna de `simulations`) exigiria `ALTER TABLE` nos bancos existentes, sem mecanismo de migração no executável.
**Consequências:** ao retomar, a data da simulação pode voltar alguns dias (até o último evento). Todo estado que precise sobreviver à retomada tem que ser reconstruível pelos eventos, e toda alteração de estado persistido tem que gerar evento.

### D7 — O simulador lê as séries sem saber a origem
**Status:** ✅ Decidida

**Decisão:** Dado real e dado gerado moram nas mesmas tabelas, no mesmo formato. A origem (canônica ou gerada) é um metadado da linha que só a gestão de dados lê; o motor da simulação consulta as séries como sempre e não distingue uma da outra.
**Por quê:** é o contrato comum entre quem produz série e quem a consome — a "interface" entre o gerador e o simulador. Cada gerador novo (outro método, outro indicador) entra sem tocar no motor, e a simulação continua sendo uma só.
**Consequências:** a origem precisa existir em toda tabela de série (preços e indicadores). Trocar dado gerado por canônico quando o real chega altera o passado de partidas salvas que jogaram sobre o gerado — como tratar isso é pergunta da F23.

### D8 — Bot, modo automático e backtest são o mesmo mecanismo
**Status:** ✅ Decidida

**Decisão:** Um jogador automático é um jogador cuja estratégia não é a `ManualStrategy`. O modo automático (F8) liga a estratégia num jogador humano; um bot (F16) é um jogador sem pessoa por trás, com a estratégia escolhida na criação; o backtest (F19) é uma partida só de bots, sem espera entre ticks.
**Por quê:** as três ideias são o mesmo "estratégia roda a cada tick" visto de lados diferentes. Um mecanismo só faz cada estratégia escrita valer nos três lugares e faz o resultado de qualquer um deles cair no mesmo relatório (estatísticas, comparação).
**Consequências:** o tick não pode depender de haver um cliente conectado por jogador. As telas de estatística, comparação e resultado de backtest são a mesma família de tela — o que importa para o redesign.

### D9 — De onde nasce uma mudança de schema
**Status:** ✅ Decidida

**Decisão:** em aberto entre dois ciclos, decidido no início da F25:
1. **Código primeiro** — `models.py` é a fonte; a mudança começa no model, e o `alembic revision --autogenerate` compara o model com o banco e escreve a migration, revisada antes de aplicar. O `sqlacodegen` sai do projeto. É o ciclo do Finance Manager.
2. **Banco primeiro** (o ciclo citado na F3) — a mudança começa no banco de desenvolvimento, o `sqlacodegen` regenera o `models.py`, e o autogenerate compara o model regenerado com uma cópia do banco na versão anterior. Mantém o hábito atual, mas exige guardar essa cópia a cada mudança.

**Por quê está aberto:** com o Alembic, o autogenerate parte dos models por construção; o ciclo atual parte do banco. Os dois funcionam, mas um vira o caminho natural e o outro um contorno.

**Atualização (2026-10-09):** decidido o ciclo 1, código primeiro. O `sqlacodegen` existia para editar o banco direto, sem passar pelo SQLAlchemy; com as migrations geradas dos models, esse caminho perde a razão de ser e sai junto. A visão do schema que o banco-primeiro dava passa a vir de um diagrama (F31).
