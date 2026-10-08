# Decisões e necessidades — Simulador Financeiro

> Companion do [`ROADMAP.md`](ROADMAP.md). Aqui mora o **porquê**: as necessidades (`N#`) que motivam o trabalho e as decisões transversais (`D#`) que condicionam as features. O **o quê** — features (`F#`), marcos (`M#`) e o estado de cada uma — mora no `ROADMAP.md`, gerado por script.
>
> **IDs:** `N#` necessidade · `D#` decisão transversal · `F#` feature · `M#` marco.
> **Sincronização:** criar ou alterar um `N#`/`D#` aqui exige espelhar no `ROADMAP.md` (`upsert-ref`) na mesma mudança.
>
> **Última mudança:** M1 concluído; registrada a D6 (de onde a retomada continua).

---

## Contexto

Simulador de investimentos do mercado brasileiro em formato de jogo (inspirado em Capitalism Lab / Victoria 3): o tempo avança em ticks diários sobre dados históricos reais, e o jogador opera renda variável (ações, FIIs, ETFs, via book de ordens com liquidez simulada) e renda fixa (CDB, LCI, LCA, Tesouro). Um jogador hospeda a partida e os outros entram pelo navegador; o ranking é pelo patrimônio.

**O que já existe** (as issues fechadas): backend FastAPI + Socket.IO servindo um SPA React; multiplayer com host/cliente e ranking; renda variável com matching engine e market maker; renda fixa com indexadores reais (CDI, IPCA); aporte mensal; controles de tempo; importação de ativos (yfinance/CSV) com atualização de defasados; histórico de simulações salvas; executável multiplataforma com release por CI; documentação Docusaurus.

**Filosofia do produto:** baixar o executável e jogar — *out-of-the-box*, sem instalar nem configurar nada. Hoje ela está quebrada num ponto: o executável exige PostgreSQL instalado (o suporte a SQLite foi removido no PR #82 porque manter os dois dialetos custava caro).

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
**Por quê:** a #85 descreve o sintoma de ter duas implementações: o JS do front projeta juros de um jeito e o backend credita de outro, e "cada um tem uma verdade sobre o dado". Hoje o ranking também é calculado no front (`build-ranking.ts`, com `parseFloat`). Uma fórmula só não diverge.
**Consequências:** toda tela nova que precisa de um número derivado ganha um campo no DTO em vez de uma função no front. O custo é um round-trip a mais em telas que poderiam calcular localmente.

### D3 — Dinheiro e quantidade trafegam como Decimal serializado em string
**Status:** ✅ Decidida

**Decisão:** Valores `Decimal` do backend chegam ao frontend como string e são formatados a partir da string, sem passar por `number`.
**Por quê:** o banco guarda `NUMERIC(20,6)`; converter para `float` no backend (ou `number` no JS) perde casas decimais e acumula erro (#86). Formatar a partir da string preserva exatamente o que foi persistido.
**Consequências:** formatadores do front (`formatMoney` e afins) passam a aceitar string; cálculo com esses valores no front deixa de existir (ver D2).

### D4 — Banco de dados embarcado no executável
**Status:** 🔍 Em aberto

**Decisão:** em aberto entre três finalistas, decidido pela F3:
1. **Só SQLite** — o executável cria um arquivo e funciona; o Postgres sai do projeto. Um dialeto só, mas troca JSONB por JSON e muda o ciclo database-first com `sqlacodegen`.
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
