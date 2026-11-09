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

A **abertura da campanha** também pausa a partida e aparece numa janela no centro da tela, que não dá para desligar nas notificações. As outras datas do calendário (chapas fecham, chapas fechadas, véspera do turno) são manchetes do Jornal e seguem o nível que você escolher.

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

### Federações

Dois partidos podem se unir numa **federação**: uma chapa só na eleição e uma lista só no Congresso. Serve para quem, sozinho, ficaria abaixo da **barreira** (a fatia mínima de votos que um partido precisa para ter cadeira). Ex.: dois partidos com 3% e 4% passam juntos de uma barreira de 5%; sozinhos, nenhum dos dois elege deputado.

**Propor e responder.** O fundador propõe a qualquer momento, inclusive no lobby, escolhendo o partido (de jogadores ou do computador), o **candidato da chapa** e o nome. A proposta vence em 7 dias, ou antes se o outro partido se federar com outro. Quem responde é o fundador do partido convidado, e os filiados veem o aviso. Não se propõe entre o 1º e o 2º turno. Cada partido tem no máximo uma federação por eleição e uma proposta aberta por vez.

**Quanto dura.** A federação nasce para uma eleição e vale no Congresso do dia em que se forma até a posse depois da eleição seguinte. Para a eleição depois dessa, os dois renovam ou cada um se federa com outro; a federação combinada de antemão concorre na eleição dela e entra no Congresso na posse. **Sair antes do prazo** desfaz a federação na hora para os dois, e quem saiu fica impedido de se federar na eleição seguinte.

**A chapa.** O partido do candidato é o **líder**: o fundador dele escolhe o vice e as promessas. As promessas do parceiro saem sem custo, e ele não define promessas enquanto a federação disputa.

**A eleição.** As intenções de voto dos dois somam na chapa. Cada partido continua com a própria verba e com as próprias ações de campanha; as ações do parceiro sobem o apoio dele, que entra na soma. Cada partido herda **metade da rejeição** que o parceiro tem em cada grupo de eleitores, calculada na hora da leitura.

**O Congresso.** A barreira e a divisão de cadeiras (método D'Hondt, que reparte as cadeiras pelas maiores médias de votos por cadeira) usam a **soma** dos votos da lista. Depois, as cadeiras se repartem entre os dois partidos pelo mesmo método, sem barreira. A **orientação** da bancada é a do partido com mais cadeiras, ou a do proponente em caso de empate ou se ninguém tem cadeira. O parceiro não orienta, e os deputados dele desobedecem pelo sorteio.

**Partidos do computador.** No fechamento do mês, o computador propõe se, sozinho, ficaria abaixo da barreira: escolhe o partido com mais bandeiras em comum e nenhuma oposta e, no empate, o de mais votos. Responde no dia seguinte e aceita se, sozinho, ficaria abaixo da barreira e tem ao menos uma bandeira em comum e nenhuma oposta. O computador nunca sai de uma federação.

Os avisos de proposta, resposta e saída chegam em tempo real, e o jornal noticia a formação e a saída.

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

## Por estado e por região

O **mapa do Brasil** (item **Mapa** do menu, com a expansão do governo ligada) mostra o mesmo eleitorado dividido em **27 estados** e **5 regiões**. Cada estado tem a sua **mistura** dos 6 grupos de eleitores: o Piauí tem mais gente que depende de auxílio, São Paulo tem mais investidores. A pesquisa e a apuração do mapa saem dessa mistura, e a soma dos estados fecha com o eleitorado do país.

### De onde vem a mistura

Cada grupo parte de um número real por estado, de fontes públicas: o eleitorado de cada estado vem do **TSE** (eleição de 2022); os beneficiários de auxílio, do **Bolsa Família** (abril de 2026, o último mês com recorte por estado); os aposentados, do **INSS** (benefícios emitidos do RGPS); os investidores, da **B3** (dezembro de 2025); e a ocupação das pessoas, do **IBGE** (PNAD Contínua). Como cada fonte tem a sua escala, os números não fecham entre si, e o jogo os ajusta.

### O ajuste proporcional iterativo

Duas somas precisam fechar ao mesmo tempo: **cada estado** soma a fatia dele no eleitorado do país, e **cada grupo** soma o peso dele no país. O ajuste reescala as linhas (estados) e as colunas (grupos), uma depois da outra, até a tabela parar de mudar. Exemplo com 2 estados e 2 grupos:

- O estado A tem 60% do eleitorado e o B tem 40%. O grupo X pesa 50% no país e o Y também.
- Os números brutos são A: X 30 e Y 10; B: X 10 e Y 10.
- **Linhas:** A soma 40 e precisa de 0,6, então vira X 0,45 e Y 0,15; B soma 20 e precisa de 0,4, então vira 0,20 e 0,20.
- **Colunas:** X soma 0,65 e precisa de 0,5, então encolhe para A 0,346 e B 0,154; Y soma 0,35 e precisa de 0,5, então cresce para A 0,214 e B 0,286.
- As linhas deixaram de fechar (A soma 0,56 em vez de 0,6), então a rodada repete. Depois de poucas rodadas a tabela para em A: X 0,364 e Y 0,236; B: X 0,136 e Y 0,264.
- Dividindo pela fatia do estado, a mistura de A é **61% X e 39% Y**, e a de B é **34% X e 66% Y**. A região é a média dos estados dela, pelo tamanho do eleitorado.

### A margem de erro de cada lugar

A pesquisa ouve **4.800 pessoas** no país, repartidas pelo tamanho de cada lugar. Lugar pequeno recebe poucas entrevistas e erra mais. A margem é

> margem = 98 ÷ √(entrevistas do lugar), arredondada e mantida entre ±3 e ±12 pontos

Exemplo: um estado com 4% do eleitorado recebe 192 entrevistas (4% de 4.800); 98 ÷ √192 ≈ 7, então a margem é **±7**. Um líder com 40% e margem ±7 pode ter de 33% a 47%.

### Empate técnico no mapa

O lugar fica **listrado** quando a diferença entre o 1º e o 2º é **menor ou igual à margem do lugar**: a pesquisa não consegue dizer quem lidera. Se o 3º também cabe na margem do 1º, o empate é entre três. Ex.: PTD com 36% e UPR com 33% num estado de margem ±4 têm diferença de 3, então o estado é listrado; com 41% contra 33%, a diferença é 8 e o PTD lidera. Na **apuração não existe margem**: vence quem tem mais voto, e a cor é cheia.

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

- **Imposto geral:** muda a alíquota do imposto sobre o lucro de ações, o teto de isenção de ações (R$ por mês), a tabela de imposto da renda fixa, a alíquota das LCI/LCA ou um dos quatro impostos que pagam o gasto do país: **consumo**, **IR das empresas**, **IR das pessoas** e **contribuição sobre a folha**. Alíquotas vão de 0% a 100%; cada medida anda até 2 pontos nos impostos de consumo, folha e pessoas, e até 5 no das empresas.
- **Por setor ou segmento:** soma pontos de imposto aos ativos de um setor (até 20 pontos) ou isenta o setor. Ex.: +5 pontos num setor com imposto de 15% passa a cobrar 20% sobre o lucro dos ativos dele. A **isenção** também move o preço: as ações do setor sobem 10% em 6 meses, em linha reta, e ficam nesse patamar enquanto a isenção durar. Ex.: uma ação de R$ 20 num setor isento passa a R$ 22 depois de 6 meses.

- **Gasto público:** muda o **auxílio**, as **obras** e o **custeio** (em % do PIB por ano) ou o **reajuste dos servidores** e o **das aposentadorias** (ganho real ao ano, acima da inflação). Cada medida anda um passo: até 0,5 ponto do PIB no auxílio, nas obras e no custeio, até 3 pontos nos reajustes, para cima ou para baixo. O custeio (a manutenção da máquina pública) parte de 2,0% do PIB e desce até zero; a saúde e a educação (3,5% do PIB) ficam fixas. O reajuste pode ficar **negativo**, uma perda real de poder de compra, até −10% ao ano. Todo janeiro a folha sobe a inflação mais o ganho real em vigor.

Gasto mexe em preço. O dinheiro a mais vira consumo, o **IPCA de 12 meses** sobe uns meses depois (o efeito enche em 6 meses e cai pela metade a cada 12), o Banco Central sobe a **SELIC** 1,5 vez o que as medidas somam à inflação (com a SELIC nas mãos do governo, quem decide é o presidente: veja [A SELIC no Copom](#a-selic-no-copom)), e cada ponto de SELIC a mais tira 2,9% da bolsa no trimestre, mais nas ações de beta alto (as que se mexem mais que o Ibovespa). O CDI sobe junto com a SELIC. Ex.: um auxílio que soma 0,5 ponto à inflação leva a SELIC a +0,75 ponto e derruba a bolsa uns 2,2%. Cortar gasto faz o caminho inverso. As obras também somam ao crescimento do PIB. O gasto chega ao IPCA por dois caminhos: o direto, que é o número de cada passo, e o indireto, que passa pelo PIB, pelo desemprego e pela curva de Phillips (veja [A economia interligada](#a-economia-interligada)). Medido sobre um passo de cada medida, o indireto soma de 1% a 9% do direto no mês em que o efeito enche, então o número do passo vale como o efeito total: é uma simplificação. O efeito vale para a partida inteira, na história e no futuro gerado, e a série guardada não muda: o painel da **Economia** mostra a série da história tracejada, o efeito de cada medida e de cada ligação e o Ibovespa com e sem o governo. Além das medidas, a economia responde ao estado do país: veja [A economia interligada](#a-economia-interligada).

O auxílio e as obras aceitam um **nome de programa** (até 30 caracteres, opcional) na hora de propor, como "Bolsa Família". O nome aparece no Jornal e no cartão de gasto público, e a medida sem nome segue como gasto comum. Um programa com nome tem memória:

- **Extinguir:** levar a verba do programa a zero soma rejeição ao seu partido nos grupos que recebiam o dinheiro (o auxílio atinge os beneficiários; as obras, empresários e trabalhadores formais). A rejeição é a lembrança da traição e demora para sumir. Reduzir a verba sem zerar não pesa.
- **Rebatizar:** propor o mesmo valor com outro nome. A medida passa pelo Congresso como as outras e vale depois da vigência; a verba e o apoio ficam, e a aprovação geral cai uma vez uns 2 pontos (some pela metade em 6 meses). O Jornal conta a troca.
- **Manter o nome:** uma medida de ajuste de verba com o campo do nome como veio mantém o programa em vigor.

Antes de enviar, o diálogo mostra a **prévia**: o que a medida faz na carteira de cada jogador e o efeito esperado na aprovação. Só pode haver uma medida igual na fila por vez, e o presidente pode retirar uma medida enquanto ela espera a votação.

### A economia interligada

Na partida com governo, a economia é a história real mais o que o governo mudou. O jogo calcula duas economias lado a lado: a da partida, com as medidas aprovadas, e a da história, com os impostos e o gasto padrão. A diferença entre as duas mexe nas séries por dez ligações. Sem nenhuma medida, as duas são iguais e a partida segue a história exata.

| Ligação | O que faz | Exemplo |
| --- | --- | --- |
| Desemprego baixo (curva de Phillips) | Com menos gente procurando emprego, os salários sobem e os preços vão junto: cada ponto de desemprego abaixo da história soma 0,35 ponto ao IPCA de 12 meses; acima, tira | Desemprego de 7,4% contra 9,4% na história soma 0,7 ponto ao IPCA |
| Risco fiscal | Cada ponto de prêmio de risco acima da história pesa na bolsa como um ponto de SELIC e encarece os empréstimos na mesma medida. O efeito na inflação vem pelo dólar (linha seguinte) | Prêmio 2 pontos acima da história tira uns 5,8% da bolsa no trimestre |
| Câmbio (dólar) | O **dólar da partida** é o da história (a PTAX) vezes o desvio que o governo causa: cada ponto de prêmio de risco acima da história soma 4% ao dólar (o investidor de fora foge) e cada ponto de juro real acima da história tira 2% (o dinheiro de fora vem atrás do juro). Cada 1% de alta do dólar em 12 meses, contra a alta que a história teve, soma 0,07 ponto ao IPCA de 12 meses, porque o importado e o combustível encarecem; o Banco Central reage a esse IPCA a mais subindo a SELIC. Dólar caro e parado deixa de pesar na inflação depois de um ano. Os ativos internacionais andam com ele (veja [Renda variável](investimentos/renda-variavel.md#ativos-nacionais-e-internacionais)) | Prêmio 5 pontos acima da história sobe o dólar uns 22% (de R$ 5,00 para uns R$ 6,10); em 12 meses isso soma uns 1,5 ponto ao IPCA (22 × 0,07) |
| PIB acima da história | Empresa que vende mais vale mais: cada 1% de PIB acima da história levanta a bolsa em 2,5%, e a arrecadação sobe 0,06 ponto do PIB | Um ano crescendo 1 ponto acima da história deixa a bolsa uns 2,5% mais alta |
| Juro real | O **juro real** é a SELIC menos a inflação de 12 meses: o quanto o dinheiro parado rende de verdade. Juro real mais alto que o da história esfria o consumo e traz a inflação para baixo; mais baixo, a empurra para cima. Cada ponto de diferença mantido por um ano mexe 0,3 ponto no IPCA de 12 meses, espalhado pelo ano seguinte, com o pico entre o 4º e o 9º mês | Juro real 3 pontos abaixo da história durante um ano soma uns 0,9 ponto ao IPCA no ano seguinte |
| Freio da inflação | Acima de 12% ao ano o IPCA de 12 meses deixa de ser só um número: os preços perdem a referência e as empresas investem menos. Cada ponto de IPCA acima de 12% tira 1,2 ponto do alvo do crescimento, e só conta o excesso que a partida tem a mais do que a história teve | IPCA de 17% numa história com 6% tem 5 pontos de excesso e tira 6 pontos do crescimento |
| Crédito encarecido | Quando a dívida sobe, o prêmio de risco sobe e o governo tira o crédito de empresas e famílias, o chamado efeito expulsão. Cada ponto de prêmio acima da história tira três quartos de ponto do alvo do crescimento; prêmio abaixo da história não empurra | Prêmio 4 pontos acima da história tira 3 pontos do crescimento |
| Ciclo fiscal | Cada ponto de desemprego acima da história custa 0,05% do PIB por ano de seguro-desemprego. O **impulso fiscal**: quando o resultado primário (o que o governo arrecada menos o que gasta, sem os juros) piora em 12 meses, sobra mais dinheiro para famílias e empresas, e cada ponto do PIB de piora soma meio ponto ao crescimento. Mantido o patamar por um ano, o empurrão acaba | Cortar imposto em 1% do PIB soma 0,5 ponto ao crescimento durante um ano |
| Imposto sobre o consumo | Alíquota mais alta encarece o que se compra: o jogo repassa aos preços metade da mudança da alíquota em 12 meses (a SELIC reage a esse IPCA a mais); o primário mais alto ainda freia o crescimento pelo impulso fiscal | Subir o consumo de 18% para 22% soma uns 2 pontos ao IPCA de 12 meses no pico e rende uns 1,6 ponto do PIB por ano |
| IR das empresas | Lucro menor vale menos na bolsa: cada ponto de alíquota acima do padrão (34%) tira 1,2% do nível da bolsa | Subir de 34% para 44% tira uns 12% da bolsa e rende uns 0,3 ponto do PIB por ano |
| Contribuição sobre a folha | Contratar fica mais caro: cada ponto de alíquota acima do padrão (20%) soma 0,06 ponto ao desemprego por ano, e o desemprego mais alto esfria os preços pela curva de Phillips | Subir de 20% para 26% soma uns 1 ponto ao desemprego em 3 anos e rende uns 1,1 ponto do PIB por ano |

**Os impostos que fecham a conta.** Os quatro impostos do país (consumo, IR das empresas, IR das pessoas e folha) pagam, juntos, 18,3% do PIB com as alíquotas padrão (18% no consumo, 34% nas empresas, 15% nas pessoas e 20% na folha), e os impostos do investimento pagam 0,7%: a soma é o gasto-base de 19% do PIB, então quem não mexe em nada arrecada e gasta o de sempre. Um imposto não rende em linha reta: a arrecadação sobe menos do que a alíquota (cada um tem uma elasticidade, a parte do aumento que a economia devolve em evasão e em atividade menor). Ex.: subir o consumo de 18% para 22% é 22% a mais de alíquota, mas só 18,6% a mais de arrecadação. Um presidente que sobe o consumo para 22%, a folha para 22% e as pessoas para 17%, e corta o custeio em 1 ponto do PIB e o reajuste dos servidores em 3 pontos, muda o resultado primário em uns 3,4 pontos do PIB em 4 anos, e paga por isso: IPCA de 12 meses até 1,6 ponto acima, desemprego mais de 1 ponto acima, PIB até 1,5 ponto abaixo e bolsa uns 13% abaixo no fim do mandato.

O Banco Central reage à inflação que as medidas e as ligações somam juntas: a SELIC sobe 1,5 vez o tanto, o juro real sobe junto e, pela ligação do juro real, puxa a inflação de volta nos meses seguintes. Com a SELIC nas mãos do governo, o Banco Central não reage: a SELIC é a que o presidente decidiu, e a bolsa reage a ela por dois caminhos: o que o mercado já esperava, que pesa 2,9% por ponto e se espalha pelo trimestre, e a surpresa do Copom, que pesa os mesmos 2,9% por ponto, inteira no dia em que a decisão passa a valer (veja [A SELIC no Copom](#a-selic-no-copom)). O crescimento da partida é o da história mais seis parcelas: o juro real e a bolsa contra os da história, as obras, o impulso fiscal, e as duas que tiram, a inflação acima de 12% e o crédito encarecido pelo prêmio de risco. Crescer menos aumenta a dívida ÷ PIB, o prêmio sobe e o crescimento cai de novo: o ciclo não tem teto, mas o crescimento da partida nunca passa de −15% ao ano, e para cima não há limite. O desemprego acompanha: cada ponto de crescimento acima da história baixa o desemprego em cerca de meio ponto em um ano. Sem novo empurrão, o desvio do desemprego contra a história volta devagar: cai pela metade a cada 3 anos, porque na economia real o desemprego volta à taxa normal da época. Ex.: um governo que deixa o desemprego 3 pontos acima da história (12% contra 9%) e depois para de piorar o vê 1,5 ponto acima depois de 3 anos e 0,75 depois de 6 se o PIB seguir a história. O que o governo fez fica na dívida, na folha, na credibilidade e na bolsa; só o desvio do desemprego se fecha sozinho. Cada ligação usa o último mês fechado e vale a partir do primeiro dia do mês seguinte.

**A taxa da dívida.** A dívida paga uma taxa mista: 45% dela segue a SELIC do dia e o resto paga o que os títulos travaram ao serem emitidos, na média dos últimos 36 meses, com o prêmio de risco da época. Ex.: SELIC de 10% e títulos que travaram 12% na média dão 0,45 × 10% + 0,55 × 12% = 11,1% ao ano. Uma alta da SELIC chega em parte na hora e o resto ao longo de 3 anos.

**O juro americano.** O Fed Funds, que a [conta em dólar](investimentos/renda-fixa.md#conta-em-dólar) rende, é o da história e depois volta a 3% ao ano: nenhuma medida do governo da partida o move.

**A espiral da dívida.** Acima de 50% do PIB de dívida, os títulos novos cobram um prêmio de risco que cresce cada vez mais rápido: com 80% do PIB, 1,6 ponto ao ano; com 100%, 3,4 pontos. Prêmio mais alto encarece a dívida, a dívida cresce, o prêmio sobe de novo, e o risco fiscal leva o dólar, a inflação e a SELIC junto. O modelo para a dívida em **300% do PIB**: acima disso ela deixa de crescer na conta, e o prêmio de risco também tem teto no efeito sobre o dólar (que ele leva a no máximo 4,5 vezes o da história). Quando o juro da dívida passa do que o crescimento e a inflação tiram dela, só um superávit primário segura a dívida.

**O primário que estabiliza a dívida.** É o superávit, em % do PIB, que mantém a dívida ÷ PIB no mesmo lugar: dívida × (taxa da dívida − crescimento nominal do PIB) ÷ (1 + crescimento nominal), com o crescimento nominal sendo o crescimento real da partida composto com o IPCA. Ex.: dívida de 80% do PIB, taxa de 12% e PIB nominal crescendo 8% pedem 0,8 × 4% ÷ 1,08 ≈ 3,0% do PIB de superávit; com um primário de 1%, a dívida sobe cerca de 2 pontos do PIB por ano. Primário acima do que estabiliza faz a dívida cair; abaixo, ela sobe, e com a taxa acima do crescimento nominal ela sobe sozinha, que é a espiral. Com a taxa abaixo do crescimento o número fica negativo: a dívida para até com déficit.

O painel da **Economia** abre tudo isso. O cartão de efeitos lista cada medida e cada ligação com o que somam ao IPCA, à SELIC e à bolsa. O do crescimento mostra a série do IBGE mais as seis parcelas, e o do desemprego, a história mais o que a partida somou. O do dólar mostra a PTAX, o que o prêmio de risco e o juro real somam a ela e quantos pontos de IPCA o dólar repassa hoje. O da dívida mostra a taxa média, o resultado primário ao lado do primário que estabiliza a dívida (o da partida e o da história) e de onde veio a variação dos últimos 12 meses: o juro a aumenta; o crescimento e a inflação a encolhem, porque aumentam o PIB que a divide; e o resultado primário a abate quando sobra e a aumenta quando falta. Ex.: juro +8,0 pontos, crescimento −1,3, inflação −3,0 e déficit primário +1,5 dão +5,2 pontos: a dívida foi de 70% para 75,2% do PIB.

### A SELIC no Copom

Na preparação da partida com governo, o campo **Juros** escolhe quem decide a SELIC:

- **Banco Central autônomo** (padrão): a SELIC é a da história mais a reação do Banco Central à inflação que o governo soma.
- **Nas mãos do governo:** o presidente decide a SELIC nas reuniões do **Copom**. Até o primeiro presidente de jogador tomar posse, o Banco Central segue decidindo como na história.

**As reuniões.** O Copom se reúne 8 vezes por ano, a cada 45 dias (no dia útil seguinte quando cai em fim de semana ou feriado). O jogo não pausa: o presidente marca a decisão antes, no cartão **SELIC no Copom** da aba de contas do **Governo**, e pode trocar ou desmarcar até o dia da reunião. A SELIC nova vale a partir do dia seguinte. Sem decisão marcada, a SELIC fica onde está; nos 7 dias antes de uma reunião sem decisão, o presidente recebe uma pendência. Um presidente do computador decide como o Banco Central autônomo decidiria.

**O teto por reunião.** A SELIC anda em passos de 0,25 ponto e cada reunião a move no máximo **3 pontos**, para cima ou para baixo, com qualquer IPCA. O presidente decide a estratégia: pode copiar a história, segurar o juro ou pisar fundo, e o custo vem do mercado, não da regra (a credibilidade, logo abaixo, cobra de quem segura o juro real abaixo da história).

A janela sempre alcança a **SELIC da história no dia**, por mais que ela tenha andado desde a reunião anterior: a regra dos 3 pontos nunca impede o presidente de copiar a história.

Ex.: SELIC de 10,75%: a próxima reunião decide entre 7,75% e 13,75%. Com a SELIC em 21% e a história em 25% no dia, a reunião pode levá-la até 25%. Uma decisão marcada fora dessa janela anda só até a borda.

**O piso.** A SELIC não desce de **0%**. Com o IPCA de 12 meses negativo (a deflação, possível num [futuro gerado](futuro-gerado.md) com inflação baixa), o piso desce a **−0,5%**, o do Banco Central Europeu. Ex.: com a SELIC em 1% e o IPCA em −0,8%, a reunião pode levá-la a −0,5%; com o IPCA de volta a 0% ou mais, a reunião seguinte volta a ter piso 0%, e uma decisão marcada abaixo disso anda só até 0%. Com a SELIC negativa, a renda fixa pós-fixada perde valor dia a dia, sem IR sobre a perda, e o dinheiro parado no caixa, que rende 0%, passa a render mais que ela: é a lição real do piso perto de zero, em que os bancos centrais não descem muito porque as pessoas sacam o dinheiro.

**O que o mercado espera e a surpresa.** O mercado espera que o presidente decida como o Banco Central autônomo decidiria (a SELIC da história mais 1,5 vez a inflação que o governo soma) e que repita o afastamento que mostrou na última reunião. A bolsa já tem esse esperado no preço, e ele pesa 2,9% por ponto de SELIC acima da história, espalhado pelo trimestre. O que a bolsa não tinha é a **surpresa**: a decisão menos o esperado, que pesa os mesmos 2,9% por ponto, inteira no dia em que a decisão passa a valer. Ex.: o mercado espera 13,25% e o Copom decide 12,25%: 1 ponto abaixo do esperado, e a bolsa sobe uns 3% (2,9%) no dia seguinte à reunião. Decidir o que o mercado espera não mexe na bolsa nesse dia. Quem copia a história a segue sem sustos; quem se afasta dela tem a surpresa cobrada na reunião e, depois, o afastamento vira o esperado e se dilui. O cartão **SELIC no Copom** mostra o **Mercado espera**: a mediana do **Focus**, a pesquisa semanal em que o Banco Central pergunta a bancos e consultorias a SELIC que eles esperam para a próxima reunião, desde que a última pesquisa tenha até 30 dias; sem ela (antes de nov/2004, no futuro gerado), a base é a SELIC de hoje. Sobre a base soma-se o que o mercado espera do presidente. O que move a bolsa é a surpresa, a decisão contra o esperado, e o cartão mostra esse esperado para o presidente decidir com ele à vista.

**O juro real.** O efeito da SELIC na inflação vem pelo juro real (SELIC menos IPCA de 12 meses), pela [ligação do juro real](#a-economia-interligada). Um juro real perto de **5%** é o **neutro**: nem esquenta nem esfria a economia. Ex.: SELIC de 10,75% com IPCA de 4,5% dão juro real de 6,25%, um pouco acima do neutro; cortar a SELIC para 8,75% com a história parada em 10,75% deixa o juro real em 4,25%, 2 pontos abaixo da história, e, mantido por um ano, soma uns 0,6 ponto ao IPCA no ano seguinte.

**A credibilidade.** A credibilidade do Banco Central vai de 0 a 100 e começa em 100. Ela mede o quanto o mercado acredita que a inflação vai voltar para a meta, e a régua é a história: quem marca a SELIC que a história teve no dia mantém os 100.

- Cada reunião em que o juro real da partida fica abaixo do da história (por mais de meio passo de 0,25, que é a folga do arredondamento) e o IPCA em 12 meses passa da **meta mais a tolerância** tira **4 pontos por ponto** abaixo da história, até 20 por reunião. Ex.: com a história em 5% de juro real, um juro real de 3,5% e o IPCA acima da faixa tiram 6 pontos. Com o IPCA dentro da faixa, o corte não custa credibilidade.
- Cada alta da SELIC, ou reunião com o juro real igual ou acima do da história, devolve **3 pontos**.
- Credibilidade baixa custa de três jeitos: a dívida paga até **2 pontos de prêmio de risco** a mais (com 80 de credibilidade, 0,4 ponto); o efeito do juro real na inflação cresce até **2 vezes** (com 80, 1,2 vez); e chega mais cedo, porque o mercado reajusta preço antes.

Credibilidade acima de 80 é boa; abaixo de 50, a dívida e a inflação já sentem.

**Os grupos de eleitores.** Em toda partida com governo, os grupos reagem ao juro real com uma faixa de **2% a 7%**. Abaixo de 2%, aposentados e investidores, que vivem de renda, reclamam; acima de 7%, trabalhadores com carteira e empreendedores, que tomam crédito, reclamam. Cada ponto fora da faixa tira de 1,5 a 2 pontos de aprovação do grupo, até 6 pontos fora.

**As fontes.** O calendário de 8 reuniões e os passos de 0,25 ponto seguem o Copom; o teto de 3 pontos por reunião é a maior alta que o Copom deu desde 1999 (out/2002, com o IPCA perto de 8%). O efeito de 0,3 ponto de IPCA por ponto de juro real, com defasagem de 6 a 9 meses, é a ordem de grandeza do modelo Samba, o modelo de projeção do Banco Central. Os números se calibram no playtest.

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

---

## Referências

- Khan, M. S.; Senhadji, A. S. (2001). *Threshold effects in the relationship between inflation and growth*. IMF Staff Papers, 48(1), 1–21. Inflação acima de um limiar tira crescimento.
- Bruno, M.; Easterly, W. (1998). *Inflation crises and long-run growth*. Journal of Monetary Economics, 41(1), 3–26. Crises de inflação alta e o crescimento.
