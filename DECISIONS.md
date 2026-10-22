# Decisões e necessidades — Simulador Financeiro

> Companion do [`ROADMAP.md`](ROADMAP.md). Aqui mora o **porquê**: as necessidades (`N#`) que motivam o trabalho e as decisões transversais (`D#`) que condicionam as features. O **o quê** — features (`F#`), marcos (`M#`) e o estado de cada uma — mora no `ROADMAP.md`, gerado por script.
>
> **IDs:** `N#` necessidade · `D#` decisão transversal · `F#` feature · `M#` marco.
> **Sincronização:** criar ou alterar um `N#`/`D#` aqui exige espelhar no `ROADMAP.md` (`upsert-ref`) na mesma mudança.
>
> **Última mudança:** registradas as necessidades de noticiário, resumo do mês, crédito e governo (N31–N34).

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

**N19. Analisar um ativo com as ferramentas de um trader**
Quem decide pelo gráfico precisa dos indicadores (MACD, IFR, médias móveis, Bandas de Bollinger) e das ferramentas de desenho (linha de tendência, suporte e resistência, Fibonacci) que sites como o Investing.com oferecem. Sem eles, quem usa análise técnica joga em desvantagem — e a estratégia automática não tem com o que decidir.

**N20. Reconhecer cada jogador, de relance, pela mesma cor e sigla em todo lugar**
Numa sala com vários jogadores, a cor é o que separa as linhas do gráfico e os nomes do ranking. Para valer como identidade, é do jogador: ele a escolhe, nenhum outro a tem na mesma partida, e é a mesma, junto com uma sigla de duas letras, no lobby, no ranking e nos gráficos.

**N21. Jogar "na unha", sem a interface apontar a melhor escolha**
Ordenar a renda fixa pela taxa equivalente e mostrar quanto o dinheiro vira no vencimento ensina, mas também decide pelo jogador: ele tende a pegar sempre o primeiro da lista. Quem já entende quer provar o próprio julgamento, fazendo as contas por conta própria.

**N22. Ter objetivos para buscar além de vencer a partida**
Conquistas dão o que perseguir numa partida perdida ou jogada sozinho, e marcam o que já se aprendeu a fazer, como atravessar uma crise ou bater o CDI um ano inteiro.

**N23. Jogar com os amigos de outras formas além de cada um por si**
Hoje toda partida é todos contra todos. Equipes, objetivos diferentes e laços econômicos entre os jogadores, como investir no amigo ou disputar o controle da empresa dele, mudam a conversa da sala.

**N24. Saber onde está a lentidão durante uma partida**
Quando a partida trava, saber qual rota ou evento está custando caro, para depois investigar só aquele ponto.

**N25. Entender o que é o simulador e como se joga, sem ler um manual**
Quem chega pelo GitHub decide em segundos se baixa, e decide pelo que vê funcionando. Quem abre o jogo pela primeira vez precisa aprender os passos básicos vendo, não lendo.

**N26. Achar a causa de um erro sem vasculhar o log inteiro**
Quando algo dá errado, na máquina de quem hospeda ou na de um amigo, o erro precisa estar num lugar curto para ler e para mandar, em vez de perdido entre as linhas de uma partida inteira.

**N27. Entrar numa partida que já começou**
Quem chega depois do início, ou volta a uma partida salva sem ter jogado nela, precisa poder participar sem estragar a conta de quem já está jogando: com depósito inicial, cor própria e o mesmo ranking.

**N28. Liberar uma vaga sem depender de o jogador sair**
Com a sala cheia, ou com uma partida salva que não comporta quem está nela, o host precisa poder abrir a vaga sozinho, em vez de pedir pelo chat para alguém fechar a aba.

**N29. Saber o que cada jogador está fazendo enquanto a partida não começa**
Na espera do lobby, "Online" diz só que a pessoa está lá. Saber que ela está na Central de dados ou olhando o resultado da última partida dá vida à sala e explica a demora de quem ainda não está pronto, como o "Navegando nos menus" dos jogos online.

**N30. Repetir uma configuração de partida sem montá-la de novo**
A cada feature nova a partida ganha mais o que configurar (período, capital, regras, modo de jogo, o futuro gerado). O host quer salvar a combinação que gosta e voltar a ela num clique, em vez de refazer tudo a cada partida.

**N31. Saber o que está movendo o mercado da partida, como quem lê o noticiário**
Hoje o preço só se mexe: a SELIC sobe, uma ação despenca, e nada na tela diz que aconteceu algo. Quem investe de verdade decide lendo o que acontece no mundo, e um mercado que conta a própria história também ensina a ligar o fato ao preço.

**N32. Saber como foi o mês sem montar a conta**
Com o tempo correndo, um mês passa em segundos. Quanto o patrimônio andou, se bateu o CDI, o que rendeu e o que afundou, quanto entrou de provento e saiu de imposto: tudo isso existe espalhado pelas telas, e ninguém para a partida para juntar.

**N33. Investir com dinheiro emprestado, pagando o juro do momento**
Pegar crédito para aproveitar uma oportunidade é uma decisão real de quem investe, e a mais perigosa: com a SELIC alta, o juro come o ganho; com a carteira caindo, a dívida continua lá. Sem crédito, o jogo não deixa errar (nem acertar) nessa decisão.

**N34. Disputar o poder de mudar as regras da economia da partida**
Em vez de só reagir aos impostos e ao cenário, chegar ao governo e mexer neles, como nos jogos em que o empresário vira prefeito. É outro jeito de ganhar e de atrapalhar os amigos, e precisa custar caro o bastante para o governo não virar o jogador mais forte da sala.

**N35. Tirar da lista as partidas que não interessam mais**
Partidas de teste, abandonadas no começo ou repetidas se acumulam em "Simulações salvas" e na comparação de partidas, e hoje não há como apagar nenhuma: a lista só cresce, e achar a partida que importa fica cada vez mais difícil.

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
**Status:** ✅ Decidida

**Decisão:** Postgres oficial embarcado no executável do Windows, sem trocar de motor e sem fork. O release baixa o zip de binários oficiais (versão e hash fixados no CI) e leva só `postgres`, `initdb`, `pg_ctl`, as DLLs, `lib`, `share` e os textos de licença que acompanham o zip. O banco vazio é gerado uma vez no CI e vai no executável como template: o `initdb` não roda no computador do jogador. Na abertura o app copia o template para a pasta de dados do usuário, sobe o servidor com `pg_ctl` numa porta livre, só em `127.0.0.1`, e o derruba ao fechar. `POSTGRES_DATABASE_URL` continua valendo: definida, usa o Postgres externo e não sobe nada. Linux e macOS seguem com Postgres externo; a EDB publica o zip oficial para Windows e macOS, e o macOS pode entrar depois pelo mesmo caminho.

**Por quê:** o spike (F3) mediu o app real, com 10 jogadores e threads gravando em paralelo.
- **Velocidade não decide.** Na carga realista (≈35 pedidos/s em paralelo, 3 ações, 250 ticks, 3 repetições), o tick levou 898 a 952 ms no Postgres e 599 a 634 ms no SQLite com a mesma garantia de durabilidade; com 100 ações (664 mil preços, 1 repetição), 1.640 contra 653 ms. Desligar a espera de disco no Postgres (`synchronous_commit=off`) não mudou o tick. Sob sobrecarga extrema (16 threads, ≈450 pedidos/s) o SQLite perdeu gravações (`database is locked`, 4 erros e um tick perdido com 3 ações) e o Postgres não deu erro. O laço da simulação dorme `1/velocidade` depois de cada tick, então com ~0,5 s por tick as velocidades ×10 e ×100 entregam cerca de 2 dias por segundo em qualquer motor: o gargalo é o custo do tick, não o banco.
- **Fidelidade dos dados decide.** O SQLite guarda `Numeric` como número aproximado (`12345678901.123456` volta como `12345678901.123455`), devolve datas sem fuso, não checa `ENUM` e recusa `NaN` (2 das 19.919 linhas de preço importadas hoje). O Postgres preserva tudo isso.
- **SQLite como reserva inverte o público.** Quem baixa o executável não tem Postgres, então rodaria no motor de menor fidelidade, diferente do de desenvolvimento, com dois conjuntos de migrations e testes. Foi esse custo que motivou a remoção do SQLite no PR #82.
- **Binários oficiais, não o pacote que os embala.** O pacote `pixeltable-pgserver` (único com Python 3.13) é mantido por uma empresa para uso próprio, traz o Postgres 18.4 enquanto o oficial está no 18.6 e não deixa escolher a versão. O zip oficial da EDB, que o [postgresql.org indica](https://www.postgresql.org/download/windows/) "para quem quer incluir o Postgres como parte do instalador de outra aplicação", entrega a versão que o projeto fixar. A [licença do PostgreSQL](https://www.postgresql.org/about/licence/) permite redistribuir para qualquer fim, desde que o aviso de copyright e o texto da licença acompanhem as cópias. O Karaoke Mugen, aplicativo desktop de código aberto, também embarca o Postgres por padrão e aceita um externo por configuração.
- **Custo medido no app completo.** O executável do Windows passa de 60,4 para 112,1 MB. A primeira abertura numa máquina limpa leva cerca de 10 s até o lobby responder, porque extrai os binários e o banco; as seguintes levam 6,8 s, o mesmo tempo do mesmo executável com banco externo, porque o servidor sobe em cerca de 0,4 s. O subconjunto mínimo de binários tem 140 MB descompactado e 49 MB comprimido, e o template do banco vazio tem 5 MB comprimido.

**Consequências:** o executável do Windows engorda cerca de 52 MB, e o formato de arquivo único extrai tudo a cada abertura (a maior parte dos ~7 s de abertura, com ou sem banco embarcado). Os binários oficiais exigem o runtime do Visual C++ da Microsoft, que um Windows limpo não traz (verificado no Windows Sandbox): a release publica o `vc_redist.x64.exe` oficial, com versão e hash fixados no workflow, e o app avisa com o link quando o servidor não abre por DLL ausente. O Postgres recusa rodar com permissão de administrador, então o executável precisa abrir sem "Executar como administrador"; o config.toml, o .env e os logs ficam na pasta do usuário. O servidor roda de pastas com caracteres fora do ASCII (testado com binários e dados em pasta acentuada); só o `initdb`, que roda no CI, falha nesses caminhos. O servidor é filho do app dentro de um Job Object do Windows, que o encerra junto com o app em qualquer queda; o encerramento limpo roda no fim normal e nos eventos do console que matam o processo sem `atexit`. O binário embutido não gera alerta de segurança automático: a versão fica fixada em `scripts/build_postgres.py` e o workflow `postgres-version.yml` a compara toda semana com a mais recente. Reabre a decisão se o servidor embarcado se mostrar instável em máquinas limpas.

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

**Decisão:** Dado real e dado gerado moram nas mesmas tabelas, no mesmo formato. A origem (canônica ou gerada) é um metadado da linha que só a gestão de dados lê; o motor da simulação lê as séries da partida e não distingue uma origem da outra. Partida salva que jogou sobre dado gerado congela esse trecho por **cópia na troca**: antes de o gerado ser trocado (pelo real que chegou ou por uma nova geração), as linhas geradas que cada partida salva cobre, de `start_date` até o último dia simulado, são copiadas para uma versão das séries daquela partida. A partida lê a própria versão onde ela existe e a comum no resto.
**Por quê:** é o contrato comum entre quem produz série e quem a consome — a "interface" entre o gerador e o simulador. Cada gerador novo (outro método, outro indicador) entra sem tocar no motor, e a simulação continua sendo uma só. O congelamento segue a N13: os dados de uma partida não mudam por baixo dela. A cópia na troca não custa nada a quem joga só sobre dado real nem sobre um gerado que nunca é trocado; copiar ao criar a partida pagaria umas 50 mil linhas por partida (37 ativos × 5 anos) mesmo quando o real nunca chega.
**Consequências:** a origem existe em toda tabela de série (preços e indicadores), e as tabelas de série ganham uma dimensão de versão: a comum e a de cada partida que congelou um trecho. A leitura do motor passa a ser "a versão da partida, senão a comum", implementada pela F24. A F28 encontra essa dimensão pronta e decide se os futuros de Monte Carlo moram nela ou em memória.

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

### D10 — Como a nota geral é calculada
**Status:** ✅ Decidida

**Decisão:** a nota é a soma de quatro eixos de peso igual — Retorno, Risco, Consistência e Eficiência —, cada um a média dos pontos das suas métricas. Cada métrica vira pontos por uma reta com dois níveis fixos (o que vale 0 e o que vale 100), com chão 0 e sem teto. As métricas: retorno anual acima do CDI e do Ibovespa; queda máxima, volatilidade, maior tempo abaixo do pico e pior mês; meses acima do CDI e meses no positivo; Sharpe e Sortino. A nota só existe a partir de 63 pregões.
**Por quê:** a avaliação olha cada dimensão por vários ângulos (o risco não é só a queda máxima), e o eixo, e não a métrica, é a unidade de peso: com quatro métricas de risco e duas de retorno, o risco não vale o dobro. As faixas são absolutas, iguais em toda partida, para que a nota compare partidas diferentes e funcione jogando sozinho, o que uma nota relativa à sala não permite. Sem teto, como placar de jogo, mas decomponível eixo a eixo e métrica a métrica, para mostrar o que puxou a nota. Abaixo de ~3 meses, anualizar engana (10 dias com +2% viram ~64% ao ano).
**Consequências:** risco e consistência têm máximo natural perto de 100 e retorno e eficiência não, então retorno muito alto compensa risco; uma carteira parada em caixa fica com ~100, quase tudo do eixo Risco. Mudar uma faixa muda a nota de todas as partidas salvas, porque a nota é recalculada dos snapshots a cada leitura.

### D11 — Sobre qual base o shadcn monta os componentes: Radix ou Base UI
**Status:** 🔍 Em aberto

**Decisão:** em aberto entre as duas bases que o shadcn oferece, decidido no começo da F36:
1. **Radix** — o que o projeto usa hoje (estilo `new-york`). Maduro e com muitos componentes; a troca de estilo é só recriar os componentes. Compõe com `asChild`.
2. **Base UI** — a biblioteca feita por parte de quem criou o Radix e o Material UI, estável desde a v1 e num pacote só. Compõe com a prop `render`. É a base do Finance Manager e do EconomicStatistics (preset `base-nova`), então componentes e padrões passam de um projeto ao outro sem adaptação.

**Por quê está aberto:** a padronização (F36) recria todos os componentes de qualquer forma, então trocar de base custa quase o mesmo que ficar — sobra a conversão dos 13 `asChild` fora de `ui/`. A recomendação é o Base UI, pela coerência com os projetos irmãos de finanças; falta conferir, recriando dois ou três componentes nos dois presets, que nada do que o app usa hoje fica sem equivalente.

**Atualização (2026-10-14):** decidida pelo **Base UI**, preset `base-nova`, na F36. Todos os componentes que o app usava têm equivalente, e os `asChild` viraram a prop `render`.
**Status:** ✅ Decidida

### D12 — Como numerar as versões
**Status:** ✅ Decidida

**Decisão:** SemVer daqui em diante, com a próxima release em 2.0.0. O número diz compatibilidade, não maturidade: maior quando partidas salvas ou o `config.toml` deixam de valer, menor para feature nova, correção no último. A maturidade vai num rótulo à parte, "Acesso antecipado", no README e no título da release.
**Por quê:** a v1.0.0 saiu em fevereiro de 2026 com uma fração das features de hoje, e o número passa a impressão de produto acabado. Os bancos da v1.0.0 não migram (a F25 partiu do schema atual), então pelo próprio SemVer a próxima já é maior. Recomeçar em 0.x inverteria a ordem (0.2.0 depois de 1.0.0) e prometeria instabilidade justo quando as migrations passaram a garantir que as partidas salvas sobrevivem; versão por data (2026.10.0) deixaria de avisar quando uma atualização quebra algo.
**Consequências:** a release que não mantém as partidas salvas é sempre maior, e o changelog de cada versão diz se elas continuam valendo (F51). Sair do "Acesso antecipado" é uma decisão de produto, separada do número.

**Atualização (2026-10-16): quando sobe cada número.** O número responde a uma pergunta sobre quem já tem o app instalado:

| Sobe | Quando | Exemplo |
| --- | --- | --- |
| **Correção** (2.0.1) | corrige bug, sem feature nova | uma tela que errava um número |
| **Menor** (2.1.0) | feature nova e nada quebra: as partidas salvas abrem e o `config.toml` antigo funciona | bots, modo Especialista, indicadores técnicos |
| **Maior** (3.0.0) | algo deixa de funcionar para quem atualiza: partida salva que não abre, chave do `config.toml` removida ou renomeada, troca de banco sem migrar os dados | trocar o Postgres pelo SQLite sem importar os dados |

Migration que acrescenta tabela ou coluna não é maior, porque a F25 a aplica sozinha nas partidas salvas. Ritmo: um marco concluído vira uma versão menor, correção solta vira correção, e a maior só com quebra de compatibilidade.

O número sai dos commits, que seguem o Conventional Commits: `feat:` pede a menor, `fix:`, `docs:`, `refactor:` e os demais pedem a correção, e um `!` depois do tipo (`feat!: Removido o campo X do config.toml`) pede a maior. O `!` é a única marca de quebra de compatibilidade, e quem faz o commit que quebra é quem o coloca. Commit sem tipo não conta. O escopo (`feat(lobby):`) é opcional e não entra na conta, então o projeto segue sem ele. A conta é do `git-cliff --bumped-version` (F51), conferida antes de cada release.

### D13 — Um canal de tempo real só: Socket.IO, com fallback de polling
**Status:** ✅ Decidida

**Decisão:** o app mantém só o Socket.IO. O SSE foi removido (broker, rota `/api/stream`, `/api/update-subscription`, cliente do front e `use_sse` do `config.toml`), e o cliente do Socket.IO passou a usar `transports: ["websocket", "polling"]`: tenta o WebSocket primeiro e cai no polling HTTP quando um proxy ou túnel barra o upgrade.
**Por quê:** o spike (F66) leu o código e achou o SSE sem uso e sem conserto. O front fixava o modo WebSocket e nenhuma tela, config ou detecção escolhia o SSE; ligar `use_sse = true` desmontava o Socket.IO do servidor e o front seguia falando Socket.IO, então o tempo real parava. O broker não tinha teste e tinha defeitos: a fila sem limite, o gerador síncrono que ocupa uma thread por conexão, e o fechamento de uma aba que apagava a inscrição da outra do mesmo cliente. O único argumento a favor, atravessar o que barra WebSocket, não se sustenta: o Quick Tunnel da Cloudflare, candidato da F5, não suporta SSE, e o polling do Socket.IO cobre o proxy que barra o upgrade sem um segundo canal para manter.
**Consequências:** a interface `RealtimeBroker` fica com uma implementação só (`SocketBroker`), e a escolha de modo some do `main.py`. A chave `use_sse` que sobrar num `config.toml` antigo é ignorada, então não quebra a atualização. A F5 passa a verificar, para cada túnel candidato, se ao menos o polling do Socket.IO atravessa; se algum não passar nem isso, a decisão se revê e o SSE volta pelo histórico do git.

### D14 — Como o futuro é gerado: bootstrap em blocos conjunto, com biomas e encaixe de nível
**Status:** ✅ Decidida

**Decisão:** o gerador (`backend/features/import_data/synthetic.py`) monta o futuro com trechos reais de 60 pregões do histórico desde 2000, e o mesmo trecho vale para todos os ativos e indicadores no mesmo dia. A escolha de cada trecho tem três camadas:
- **Biomas.** Os trechos se encadeiam por bioma (calmo, normal e agitado, pelo tercil da volatilidade do Ibovespa no trecho), com as transições medidas no histórico: depois de um trimestre agitado, 61% das vezes vem outro agitado. A cadeia começa no bioma do mercado de hoje ou no que o usuário escolher.
- **Encaixe de nível.** Entre os trechos do bioma, o sorteio favorece os que começam com SELIC, IPCA de 12 meses e tendência do IPCA (variação em 3 meses) parecidos com os do momento gerado. É uma média pesada pela distância nesse estado, com largura de meio desvio-padrão.
- **Temperatura**, de 0 a 3, padrão 1: o peso de cada trecho é (volatilidade dele ÷ volatilidade mediana) elevado a 2·(T − 1), e o mesmo peso inclina a troca de bioma.

Os indicadores saem do caminho: a SELIC soma as variações dos trechos ao último valor real, presa ao mínimo e ao máximo desde 2000; o CDI segue a SELIC com o spread do último dia real; o IPCA de cada mês é o do mês sorteado. O **choque de inflação**, de −5 a +20 pontos e desligado por padrão, é uma camada por cima dos mesmos trechos: sobe em seis meses, decai pela metade a cada ano, soma X pontos à inflação anual, 1,5·X à SELIC (princípio de Taylor: o Banco Central sobe o juro mais do que a inflação subiu) e, à bolsa, a reação histórica do Ibovespa à SELIC: −2,9% no trimestre por ponto de alta, medido em trimestres desde 2000, aplicado a cada ativo pelo beta dele. Ativo sem pregão no dia sorteado (abriu capital depois) usa o movimento dos pares do segmento, depois do setor, depois do Ibovespa, com o beta e um resíduo sorteado do próprio ativo. Dia com alta acima de 100% ou queda abaixo de 50% é erro da fonte e conta como dia sem pregão. O trecho de cada data depende só da semente, da temperatura, do bioma inicial e da data, então gerar um ativo sozinho dá as mesmas linhas que gerá-lo com todos, e o choque muda os níveis sem mudar os trechos.
**Por quê:** medido nos spikes (F23 e F88) com 37 ativos de 10 setores, gerando 100 futuros por variante e comparando com o histórico:
- **Dias bruscos** (curtose: 0 numa curva sem dias extremos, maior com mais quedas e altas bruscas): real 53, gerado 23, passeio aleatório com volatilidade constante 0.
- **Memória da agitação** (correlação entre o tamanho do movimento de hoje e o de daqui a 20 pregões; 0 é sem memória): real 0,08, gerado 0,07, trechos de 20 dias 0,00, passeio aleatório 0.
- **Setores andando juntos** (correlação média dos retornos diários; 1 é idêntico, 0 é sem relação): real 0,38 dentro do setor e 0,25 entre setores; gerado 0,35 e 0,20; passeio aleatório 0 e 0.
- **Queda máxima anual do Ibovespa** (do pico ao fundo dentro do ano): real com mediana −20%, pior −60% e queda acima de 30% em 6 de 26 anos (23%); gerado −20%, −71% e 28% de 500 anos.
- **Indicadores reagindo uns aos outros** (correlações por trimestre, real em 309 meses desde 2001, gerado em 100 futuros de 10 anos): o IPCA acelerar e a SELIC subir no trimestre seguinte, real 0,37, gerado 0,33 (sem o encaixe, 0,01; com uma regra fixa do Copom, 0,57, reação mais robótica que a real); a SELIC subir e o Ibovespa cair no mesmo trimestre, real −0,31, gerado −0,24 (com a regra do Copom, −0,07, porque a SELIC deixa de vir do mesmo trecho que a bolsa). O juro real (SELIC menos IPCA de 12 meses) fica negativo em 4% dos meses, contra 6% no real e 11% sem o encaixe, e nunca com a regra do Copom.
- **Choque** (50 futuros de 3 anos por nível): com +20 pontos, IPCA de 12 meses no pico de 22%, SELIC de 43% e queda do Ibovespa de 57% em dois anos; com +10, 14%, 28% e −36%; sem choque, 7%, 15% e −26%; com −5, a SELIC cai a 6%. Choque maior é sempre bolsa pior. Sem a camada, o encaixe não acha trechos com inflação de 30% e sorteia ao acaso, e a bolsa sofria menos nos choques maiores.
- **Biomas:** no realismo medido empatam com o sorteio sem regra de vizinhança, porque um trecho de 60 dias já carrega a transição dentro dele. Entram pelo jogo: começar o futuro numa crise dá 30% de volatilidade no primeiro ano, contra 22% começando normal e 18% calmo.
- **Temperatura:** anos com queda acima de 30% em 5% dos casos com T = 0, 28% com T = 1, 64% com T = 2 (volatilidade mediana de 43%, perto do pior ano real, 52%) e 96% com T = 3, o "apocalipse", acima de qualquer ano real por escolha.
- **Alternativas:** o passeio aleatório não tem dia brusco, memória nem correlação; o GARCH não foi medido, porque o bootstrap passou nos critérios; a rede neural tende a prever a média e gerar uma curva lisa; os geradores de ruído suave dos jogos (Perlin, seno) têm o mesmo defeito do passeio aleatório.
**Consequências:** o futuro sem choque nunca traz um tipo de crise que não aconteceu desde 2000. No teste fora da amostra (2020–2024 gerado só com o histórico até 2019), o que aconteceu caiu dentro da faixa do 5º ao 95º futuro em 23 de 36 séries no retorno e 26 de 36 na queda máxima: o encaixe deixa os futuros coerentes com o momento de partida e também mais estreitos, e o ciclo de 2020–2022 (SELIC a 2% e depois a alta mais rápida desde o Plano Real) ficou fora de todos os futuros em qualquer variante. Futuro fora do que já aconteceu é escolha explícita, pela temperatura ou pelo choque. Gerar 37 ativos × 5 anos leva cerca de 1 s e o preview de poucos ativos cerca de 0,1 s, então o preview pode refazer a geração a cada mudança de parâmetro. A F24 usa o `SeriesGenerator` como está. A metodologia para quem joga está na página "Como o futuro é gerado" dos docs.

### D15 — Lint com oxlint e o TypeScript 7 com a API do 6 ao lado
**Status:** ✅ Decidida

**Decisão:** o frontend checa tipos com o TypeScript 7, o `tsc` reescrito em Go, e faz lint com o oxlint (`frontend/.oxlintrc.json`): as regras do React Compiler nativas dele, as que olham os tipos pelo `oxlint-tsgolint` e o `@shadcn/lint` como `jsPlugin`. O `openapi-typescript` recebe a API do TypeScript 6 (`@typescript/typescript6`, publicado pela Microsoft para isso) por um hook do pnpm em `frontend/.pnpmfile.cjs`.
**Por quê:** o pacote `typescript` 7 não exporta mais a API de compilador, e duas ferramentas dependiam dela: o `typescript-eslint`, que até a 8.72 aceita só TypeScript abaixo de 6.1, e o `openapi-typescript`, que monta os tipos gerados com `ts.factory`. O oxlint não usa o pacote `typescript`, e o tsgolint é construído sobre o próprio TypeScript 7. Medido no projeto: o `tsc` caiu de 30,7 s para 6,5 s, e o lint de 15 s (ESLint) para 9 s, já com `no-floating-promises`, `no-misused-promises` e `await-thenable`, que o ESLint não rodava. Das 16 regras do `eslint-plugin-react-hooks` 7, o oxlint tem 14 nativas; ficam de fora `config` e `gating`, que validam a configuração do React Compiler, que o projeto não usa. O pnpm resolve peer dependency pelo `typescript` da raiz e ignora `overrides` e `packageExtensions` nela, por isso o hook reescreve o manifesto do `openapi-typescript` na instalação.
**Consequências:** o `.pnpmfile.cjs` sai quando o `openapi-typescript` aceitar o TypeScript 7 (hoje declara `typescript ^5.x`). Promise sem `await` é erro de lint: `navigate` do react-router e `invalidateQueries` disparados sem esperar levam `void`.
