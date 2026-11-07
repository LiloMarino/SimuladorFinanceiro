---
sidebar_position: 8.7
---

# Governo & Política

**Governo & Política** é uma expansão opcional: os jogadores se organizam em **partidos** e disputam uma **eleição presidencial** dentro da partida. Ela se liga no lobby, na aba **Expansões** das regras, e aparece como os itens **Eleição** e **Governo** no menu lateral.

Com a expansão ligada, você pode jogar a partida normalmente e usar a eleição como um extra, ou escolher o tipo de partida **Política**, em que o vencedor é o partido (veja [Vitória política](#vitória-política)).

## Calendário da eleição

O host escolhe, nas regras, a data do **1º turno da primeira eleição** (por padrão, 7 de outubro do ano seguinte ao início). Dali, uma eleição a cada 4 anos.

| Marco | Quando |
| --- | --- |
| Abertura da candidatura | 1 ano antes do 1º turno (ou no início da partida, se for depois) |
| Fim da inscrição de chapas | Último dia do mês anterior ao 1º turno |
| 1º turno | A data das regras (se não for dia útil, passa para o próximo) |
| 2º turno | 3 semanas depois do 1º |
| Posse | 1º de janeiro do ano seguinte; o mandato dura 4 anos |

Quem governa pode concorrer a **uma reeleição**; depois de dois mandatos seguidos, não concorre de novo.

Os dois turnos **pausam a partida** quando o resultado sai: todos veem o diálogo do resultado e retomam pelo controle de velocidade no topo.

## Partidos

Só se concorre por partido, e o partido existe desde o 1º dia da partida:

- **Fundar:** nome, sigla de 2 a 8 letras, cor, **promessa** na régua (veja abaixo) e a contribuição mensal. Nome, sigla e cor não podem repetir os de outro partido. Quem funda é o **fundador**.
- **Filiar-se:** escolhe um partido de jogadores e quanto contribui por mês. Cada jogador está em um partido só; para trocar, é preciso sair antes.
- **Contribuir:** cada filiado define a própria contribuição mensal, que pode ser **zero**. A **verba** do partido é a soma das contribuições. O valor fica salvo no perfil: ao fundar ou entrar num partido, inclusive pela preparação do lobby, o jogador começa com a última contribuição que escolheu.
- **Sair** e **expulsar:** quem sai para de contribuir na hora, e o que já saiu do caixa não volta. Só o fundador expulsa, e a expulsão é pública. Bots não entram em partido.

Fundar, filiar-se e sair valem desde o 1º dia da partida; entre os turnos só se doa. Três coisas esperam a campanha abrir:

- **A chapa** se inscreve só com a campanha aberta, até o fim da inscrição de chapas.
- **A contribuição** começa a ser cobrada no 1º dia do mês seguinte à abertura; antes disso, o valor fica marcado e nada sai do caixa.
- **As ações de campanha** (comício, evento, propaganda na TV) também.

Para concorrer, como candidato ou vice, é preciso estar filiado **6 meses antes do 1º turno**, como manda a lei eleitoral. Quem se filia depois do prazo é filiado normal, contribui e vota com o partido, mas só entra numa chapa na eleição seguinte. Numa partida que já começa depois do prazo, vale quem se filiou no 1º dia.

Um partido fundado no meio do mandato fica **sem cadeira** no Congresso até a eleição seguinte.

Quem joga sozinho fundou um partido de um filiado: vale igual.

### A chapa

A chapa é o **candidato** e o **vice**. Por padrão o candidato é o fundador e a chapa vai sem vice. O fundador pode escolher outro filiado como candidato e **convidar um vice** até o fim da inscrição de chapas. O vice pode ser qualquer jogador da sala, de outro partido ou sem partido, como numa coligação; ele continua filiado ao próprio partido e soma para ele no ranking. Não vale convidar quem já é vice ou candidato de outra chapa. O vice só conta depois de **aceitar** o convite, que aparece na tela dele; sem resposta, a chapa concorre sem vice.

### A promessa na régua

Cada partido assume uma posição de 1 a 5 numa régua entre **impostos baixos** e **gasto alto**:

| Faixa | Posição |
| --- | --- |
| 1 | Impostos bem baixos (corte geral de imposto) |
| 2 | Impostos baixos (isenção para um setor) |
| 3 | Meio-termo |
| 4 | Gasto alto (taxa um setor) |
| 5 | Gasto bem alto (imposto geral novo) |

A promessa decide para onde vão os votos de quem sai no 2º turno (veja abaixo) e pesa na aprovação de quem governa (veja [Governar](#governar)).

## Como a verba vira votos

O **apoio** de um partido cresce pela **raiz quadrada** do que ele gasta: dobrar a verba **não** dobra os votos. A conta de cada mês é

> pontos = √(verba do mês) ÷ 64

e o resultado é quantos eleitores, em cada 100, passam a votar no partido. Exemplos:

- **R$ 8.000** num mês: √8.000 ≈ 89,4; ÷ 64 = **1,4 ponto**.
- **R$ 16.000** no mês (o dobro): √16.000 ≈ 126,5; ÷ 64 = **2,0 pontos**, e não 2,8.

Os pontos de cada mês de campanha se somam. Por isso muitos contribuintes pequenos rendem mais votos por real do que um só doador grande.

A contribuição de cada filiado é debitada do caixa no **1º dia útil de cada mês** de campanha. Se faltar caixa naquele mês, a contribuição é **pulada** (não vira dívida) e vira uma pendência, "Sua contribuição de R$ 2.000,00 não foi paga em março, por falta de caixa", que some quando a contribuição seguinte é paga ou quando você muda o valor.

O que falta para 100 são os **indecisos**: eleitores que ainda não escolheram ninguém. A **pesquisa de intenção** mostra os pontos de cada partido e os indecisos de hoje.

## O 1º turno

A apuração usa os **votos válidos**: a fatia de cada partido entre os eleitores que escolheram alguém (os indecisos ficam de fora). Ex.: com os partidos A 20, B 10 e C 5 pontos, os válidos são 35, e A tem 20 ÷ 35 = **57%**.

- Passou de **50%** dos válidos: elege-se já no 1º turno, e o 2º turno não acontece.
- Senão, os **dois mais votados** vão ao 2º turno. Empate fica com o partido mais antigo.

## Entre os turnos: doações

Entre os dois turnos, os filiados de partidos que **ficaram de fora** podem **doar a um finalista**, a favor de quem lidera ou contra. A doação é pública, sai do patrimônio de quem doa e soma √valor ÷ 64 pontos ao finalista. O prazo vai até a véspera do 2º turno.

## O 2º turno

Os eleitores dos partidos eliminados vão para o **finalista de promessa mais próxima** na régua; em distância igual, para o que tinha mais votos. Quem somar mais votos vence. O painel mostra uma **simulação do 2º turno** entre os dois primeiros de hoje, que se atualiza com a pesquisa.

## Partidos do computador

O computador completa a disputa com **partidos próprios** (UPR, MNV e ACI) até haver três partidos na eleição. Cada um gasta, por mês, um múltiplo da **verba média dos partidos de jogadores**, definido pela **dificuldade do computador** nas regras: Fácil (0,5×), Normal (1×) ou Difícil (1,5×). Ex.: com os partidos de jogadores gastando em média R$ 10.000 por mês, cada partido do computador gasta R$ 5.000 no Fácil e R$ 15.000 no Difícil. Sem partidos de jogadores, o computador não gasta nada.

## Ranking

A página da eleição traz o **patrimônio de cada jogador** e o de cada **partido** (a soma dos filiados). Quem não é de partido fica fora do ranking de partidos.

## Vitória política

No tipo de partida **Política**, a partida acaba na data final e vence o **partido com a maior soma de patrimônio dos filiados**, e não o critério de vitória escolhido para as demais. Por isso o seletor do critério some quando a Política está marcada, e o modo de jogo fica **individual** (cada jogador compete por seu partido, e não em equipes). O ranking individual continua na tela de resultado, só para informação.

A Política só aparece quando a expansão **Governo & Política** está ligada. Desligar a expansão devolve o tipo para Clássica.

## Governar

Quem vence a eleição toma posse em 1º de janeiro e governa por 4 anos. A página **Governo** mostra a aprovação, os impostos e o gasto público em vigor, a fila do Congresso e a carteira do presidente. Até a primeira posse, um governo neutro do computador conduz o país e não muda impostos.

### Propor medidas

O presidente propõe medidas pelo botão **Nova medida**. Três tipos:

- **Imposto geral:** muda a alíquota do imposto sobre o lucro de ações, o teto de isenção de ações (R$ por mês), a tabela de imposto da renda fixa ou a alíquota das LCI/LCA. Alíquotas vão de 0% a 100%.
- **Por setor ou segmento:** soma pontos de imposto aos ativos de um setor (até 20 pontos) ou isenta o setor. Ex.: +5 pontos num setor com imposto de 15% passa a cobrar 20% sobre o lucro dos ativos dele.

- **Gasto público:** muda o **auxílio** e as **obras** (em % do PIB por ano) ou o **reajuste dos servidores** e o **das aposentadorias** (ganho real ao ano, acima da inflação). Cada medida anda um passo: até 0,5 ponto do PIB no auxílio e nas obras, até 3 pontos nos reajustes, para cima ou para baixo (o ganho real não fica abaixo de 0%). Todo janeiro a folha sobe a inflação mais o ganho real em vigor.

Gasto mexe em preço. O dinheiro a mais vira consumo, o **IPCA de 12 meses** sobe uns meses depois (o efeito enche em 6 meses e cai pela metade a cada 12), o Banco Central sobe a **SELIC** 1,5 vez o que as medidas somam à inflação (com a SELIC nas mãos do governo, quem decide é o presidente: veja [A SELIC no Copom](#a-selic-no-copom)), e cada ponto de SELIC a mais tira 2,9% da bolsa no trimestre, mais nas ações de beta alto (as que se mexem mais que o Ibovespa). O CDI sobe junto com a SELIC. Ex.: um auxílio que soma 0,5 ponto à inflação leva a SELIC a +0,75 ponto e derruba a bolsa uns 2,2%. Cortar gasto faz o caminho inverso. As obras também somam ao crescimento do PIB. O gasto chega ao IPCA por dois caminhos: o direto, que é o número de cada passo, e o indireto, que passa pelo PIB, pelo desemprego e pela curva de Phillips (veja [A economia interligada](#a-economia-interligada)). Medido sobre um passo de cada medida, o indireto soma de 1% a 9% do direto no mês em que o efeito enche, então o número do passo vale como o efeito total: é uma simplificação. O efeito vale para a partida inteira, na história e no futuro gerado, e a série guardada não muda: o painel da **Economia** mostra a série da história tracejada, o efeito de cada medida e de cada ligação e o Ibovespa com e sem o governo. Além das medidas, a economia responde ao estado do país: veja [A economia interligada](#a-economia-interligada).

Antes de enviar, o diálogo mostra a **prévia**: o que a medida faz na carteira de cada jogador e o efeito esperado na aprovação. Só pode haver uma medida igual na fila por vez, e o presidente pode retirar uma medida enquanto ela espera a votação.

### A economia interligada

Na partida com governo, a economia é a história real mais o que o governo mudou. O jogo calcula duas economias lado a lado: a da partida, com as medidas aprovadas, e a da história, com os impostos e o gasto padrão. A diferença entre as duas mexe nas séries por cinco ligações. Sem nenhuma medida, as duas são iguais e a partida segue a história exata.

| Ligação | O que faz | Exemplo |
| --- | --- | --- |
| Desemprego baixo (curva de Phillips) | Com menos gente procurando emprego, os salários sobem e os preços vão junto: cada ponto de desemprego abaixo da história soma 0,35 ponto ao IPCA de 12 meses; acima, tira | Desemprego de 7,4% contra 9,4% na história soma 0,7 ponto ao IPCA |
| Risco fiscal | Cada ponto de prêmio de risco acima da história soma meio ponto ao IPCA (o real perde valor e os importados encarecem), pesa na bolsa como um ponto de SELIC e encarece os empréstimos na mesma medida | Prêmio 2 pontos acima da história soma 1 ponto ao IPCA e tira uns 5,8% da bolsa no trimestre |
| PIB acima da história | Empresa que vende mais vale mais: cada 1% de PIB acima da história levanta a bolsa em 2,5%, e a arrecadação sobe 0,06 ponto do PIB | Um ano crescendo 1 ponto acima da história deixa a bolsa uns 2,5% mais alta |
| Juro real | O **juro real** é a SELIC menos a inflação de 12 meses: o quanto o dinheiro parado rende de verdade. Juro real mais alto que o da história esfria o consumo e traz a inflação para baixo; mais baixo, a empurra para cima. Cada ponto de diferença mantido por um ano mexe 0,3 ponto no IPCA de 12 meses, espalhado pelo ano seguinte, com o pico entre o 4º e o 9º mês | Juro real 3 pontos abaixo da história durante um ano soma uns 0,9 ponto ao IPCA no ano seguinte |
| Ciclo fiscal | Cada ponto de desemprego acima da história custa 0,05% do PIB por ano de seguro-desemprego. O **impulso fiscal**: quando o resultado primário (o que o governo arrecada menos o que gasta, sem os juros) piora em 12 meses, sobra mais dinheiro para famílias e empresas, e cada ponto do PIB de piora soma meio ponto ao crescimento. Mantido o patamar por um ano, o empurrão acaba | Cortar imposto em 1% do PIB soma 0,5 ponto ao crescimento durante um ano |

O Banco Central reage à inflação que as medidas e as ligações somam juntas: a SELIC sobe 1,5 vez o tanto, o juro real sobe junto e, pela ligação do juro real, puxa a inflação de volta nos meses seguintes. Com a SELIC nas mãos do governo, o Banco Central não reage: a SELIC é a que o presidente decidiu, e cada ponto dela acima da história tira 2,9% da bolsa no trimestre. O crescimento da partida é o da história mais quatro parcelas: o juro real e a bolsa contra os da história, as obras e o impulso fiscal. O desemprego acompanha: cada ponto de crescimento acima da história baixa o desemprego em cerca de meio ponto em um ano. Sem novo empurrão, o desvio do desemprego contra a história volta devagar: cai pela metade a cada 3 anos, porque na economia real o desemprego volta à taxa normal da época. Ex.: um governo que deixa o desemprego 3 pontos acima da história (12% contra 9%) e depois para de piorar o vê 1,5 ponto acima depois de 3 anos e 0,75 depois de 6 se o PIB seguir a história. O que o governo fez fica na dívida, na folha, na credibilidade e na bolsa; só o desvio do desemprego se fecha sozinho. Cada ligação usa o último mês fechado e vale a partir do primeiro dia do mês seguinte.

**A taxa da dívida.** A dívida paga uma taxa mista: 45% dela segue a SELIC do dia e o resto paga o que os títulos travaram ao serem emitidos, na média dos últimos 36 meses, com o prêmio de risco da época. Ex.: SELIC de 10% e títulos que travaram 12% na média dão 0,45 × 10% + 0,55 × 12% = 11,1% ao ano. Uma alta da SELIC chega em parte na hora e o resto ao longo de 3 anos.

**A espiral sem teto.** Acima de 50% do PIB de dívida, os títulos novos cobram um prêmio de risco que cresce cada vez mais rápido e não tem teto: com 80% do PIB, 1,6 ponto ao ano; com 100%, 3,4 pontos. Prêmio mais alto encarece a dívida, a dívida cresce, o prêmio sobe de novo, e o risco fiscal leva a inflação e a SELIC junto. Quando o juro da dívida passa do que o crescimento e a inflação tiram dela, só um superávit primário segura a dívida.

**O primário que estabiliza a dívida.** É o superávit, em % do PIB, que mantém a dívida ÷ PIB no mesmo lugar: dívida × (taxa da dívida − crescimento nominal do PIB) ÷ (1 + crescimento nominal), com o crescimento nominal sendo o crescimento real da partida composto com o IPCA. Ex.: dívida de 80% do PIB, taxa de 12% e PIB nominal crescendo 8% pedem 0,8 × 4% ÷ 1,08 ≈ 3,0% do PIB de superávit; com um primário de 1%, a dívida sobe cerca de 2 pontos do PIB por ano. Primário acima do que estabiliza faz a dívida cair; abaixo, ela sobe, e com a taxa acima do crescimento nominal ela sobe sozinha, que é a espiral. Com a taxa abaixo do crescimento o número fica negativo: a dívida para até com déficit.

O painel da **Economia** abre tudo isso. O cartão de efeitos lista cada medida e cada ligação com o que somam ao IPCA, à SELIC e à bolsa. O do crescimento mostra a série do IBGE mais as quatro parcelas, e o do desemprego, a história mais o que a partida somou. O da dívida mostra a taxa média, o resultado primário ao lado do primário que estabiliza a dívida (o da partida e o da história) e de onde veio a variação dos últimos 12 meses: o juro a aumenta; o crescimento e a inflação a encolhem, porque aumentam o PIB que a divide; e o resultado primário a abate quando sobra e a aumenta quando falta. Ex.: juro +8,0 pontos, crescimento −1,3, inflação −3,0 e déficit primário +1,5 dão +5,2 pontos: a dívida foi de 70% para 75,2% do PIB.

### A SELIC no Copom

Na preparação da partida com governo, o campo **Juros** escolhe quem decide a SELIC:

- **Banco Central autônomo** (padrão): a SELIC é a da história mais a reação do Banco Central à inflação que o governo soma.
- **Nas mãos do governo:** o presidente decide a SELIC nas reuniões do **Copom**. Até o primeiro presidente de jogador tomar posse, o Banco Central segue decidindo como na história.

**As reuniões.** O Copom se reúne 8 vezes por ano, a cada 45 dias (no dia útil seguinte quando cai em fim de semana ou feriado). O jogo não pausa: o presidente marca a decisão antes, no cartão **SELIC no Copom** da aba de contas do **Governo**, e pode trocar ou desmarcar até o dia da reunião. A SELIC nova vale a partir do dia seguinte. Sem decisão marcada, a SELIC fica onde está; nos 7 dias antes de uma reunião sem decisão, o presidente recebe uma pendência. Um presidente do computador decide como o Banco Central autônomo decidiria.

**O teto por reunião.** A SELIC anda em passos de 0,25 ponto e cada reunião a move no máximo:

| IPCA de 12 meses | Teto por reunião |
| --- | --- |
| Dentro da meta mais a tolerância | 0,75 ponto |
| Acima da meta mais a tolerância | 1,5 ponto |
| Acima de 15% | 3 pontos |

Ex.: SELIC de 10,75% com o IPCA dentro da meta: a próxima reunião decide entre 10% e 11,5%. Uma decisão marcada fora do teto do dia da reunião anda só até o teto.

**O juro real.** O efeito da SELIC na inflação vem pelo juro real (SELIC menos IPCA de 12 meses), pela [ligação do juro real](#a-economia-interligada). Um juro real perto de **5%** é o **neutro**: nem esquenta nem esfria a economia. Ex.: SELIC de 10,75% com IPCA de 4,5% dão juro real de 6,25%, um pouco acima do neutro; cortar a SELIC para 8,75% com a história parada em 10,75% deixa o juro real em 4,25%, 2 pontos abaixo da história, e, mantido por um ano, soma uns 0,6 ponto ao IPCA no ano seguinte.

**A credibilidade.** A credibilidade do Banco Central vai de 0 a 100 e começa em 100. Ela mede o quanto o mercado acredita que a inflação vai voltar para a meta, e a régua é a história: quem marca a SELIC que a história teve no dia mantém os 100.

- Cada reunião em que o juro real da partida fica abaixo do da história (por mais de meio passo de 0,25, que é a folga do arredondamento) e o IPCA em 12 meses passa da **meta mais a tolerância** tira **4 pontos por ponto** abaixo da história, até 20 por reunião. Ex.: com a história em 5% de juro real, um juro real de 3,5% e o IPCA acima da faixa tiram 6 pontos. Com o IPCA dentro da faixa, o corte não custa credibilidade.
- Cada alta da SELIC, ou reunião com o juro real igual ou acima do da história, devolve **3 pontos**.
- Credibilidade baixa custa de três jeitos: a dívida paga até **2 pontos de prêmio de risco** a mais (com 80 de credibilidade, 0,4 ponto); o efeito do juro real na inflação cresce até **2 vezes** (com 80, 1,2 vez); e chega mais cedo, porque o mercado reajusta preço antes.

Credibilidade acima de 80 é boa; abaixo de 50, a dívida e a inflação já sentem.

**Os grupos de eleitores.** Em toda partida com governo, os grupos reagem ao juro real com uma faixa de **2% a 7%**. Abaixo de 2%, aposentados e investidores, que vivem de renda, reclamam; acima de 7%, trabalhadores com carteira e empreendedores, que tomam crédito, reclamam. Cada ponto fora da faixa tira de 1,5 a 2 pontos de aprovação do grupo, até 6 pontos fora.

**As fontes.** O calendário de 8 reuniões e os passos de 0,25 ponto seguem o Copom; o teto de 1,5 ponto é o ritmo do Copom em 2021. O efeito de 0,3 ponto de IPCA por ponto de juro real, com defasagem de 6 a 9 meses, é a ordem de grandeza do modelo Samba, o modelo de projeção do Banco Central. Os números se calibram no playtest.

### O Congresso

O Congresso vota as medidas da fila no **último dia útil de cada mês**. A **chance** de a medida passar é igual à aprovação do governo naquele dia: com 60% de aprovação, cada medida tem 60% de chance (é um sorteio, então 60% não garante nada). Se for aprovada, a medida vale **90 dias depois** da votação; se for rejeitada, nada muda e o presidente pode propor de novo. Todos os jogadores recebem aviso da votação e de quando a medida passa a valer.

### A aprovação

A aprovação é quantos eleitores, em cada 100, aprovam o governo. Ela começa em **50%** na posse e é recalculada com os fatores abaixo, sempre entre 0 e 100:

| Fator | Efeito |
| --- | --- |
| Inflação em 12 meses | +4 pontos se estiver dentro da meta do ano; cada ponto percentual acima da meta tira 3 |
| Bolsa em 12 meses | +1 ponto a cada 5% de alta e −1 a cada 5% de queda, até 6 pontos para cada lado |
| Corte de imposto | Soma de 1 a 3 pontos enquanto o governo dura |
| Imposto novo | Tira de 1 a 5 pontos ao passar a valer, e o efeito some em 6 meses |
| Juro real | Por grupo: tira de 1,5 a 2 pontos por ponto de juro real fora da faixa de 2% a 7% (veja [A SELIC no Copom](#a-selic-no-copom)) |
| Promessa | Tira 3 pontos por faixa de distância entre a promessa do partido e a marca do governo na régua |

A **marca do governo** é a média das faixas das medidas aprovadas. Ex.: um partido que prometeu a faixa 2 (isenção para um setor) e aprovou só aumento geral de imposto (faixa 5) está 3 faixas à direita da promessa e perde 9 pontos. A aprovação é calculada só quando um jogador governa.

### Impeachment

Se a aprovação fechar **3 meses seguidos abaixo de 25%**, o presidente sofre impeachment. A partir do primeiro mês abaixo do piso o presidente recebe um aviso. Quem assume é o **vice**, se ainda estiver na partida, e governa até o fim do mandato; sem vice, assume o partido do computador com mais cadeiras na casa, que governa até o fim do mandato propondo medidas pelos grupos de eleitores dele. A carteira de quem saiu volta a operar.

### A carteira do presidente

Enquanto governa, o presidente **não compra nem vende**: a carteira fica congelada até o fim do mandato, e a boleta mostra o aviso. A carteira é **pública**: todos os jogadores veem os ativos que o presidente tem e a fatia de cada um, para que ninguém governe em causa própria sem a sala saber. A prévia de uma medida setorial também mostra quanto cada jogador tem naquele setor.

