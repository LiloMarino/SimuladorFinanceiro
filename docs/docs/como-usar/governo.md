---
sidebar_position: 8.7
---

# Governo & Política

**Governo & Política** é uma expansão opcional: os jogadores se organizam em **partidos** e disputam uma **eleição presidencial** dentro da partida. Ela se liga no lobby, na aba **Expansões** das regras, e aparece como o item **Eleição** no menu lateral.

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

Só se concorre por partido, e todo partido nasce na candidatura:

- **Fundar:** nome, sigla de 2 a 5 letras, cor, **promessa** na régua (veja abaixo) e a contribuição mensal. Nome, sigla e cor não podem repetir os de outro partido. Quem funda é o **fundador**.
- **Filiar-se:** escolhe um partido de jogadores e quanto contribui por mês. Cada jogador está em um partido só; para trocar, é preciso sair antes.
- **Contribuir:** cada filiado define a própria contribuição mensal, que pode ser **zero**. A **verba** do partido é a soma das contribuições.
- **Sair** e **expulsar:** quem sai para de contribuir na hora, e o que já saiu do caixa não volta. Só o fundador expulsa, e a expulsão é pública. Bots não entram em partido.

Fundar e filiar-se só abrem durante a campanha, antes do 1º turno; entre os turnos só se doa.

Quem joga sozinho fundou um partido de um filiado: vale igual.

### A chapa

A chapa é o **candidato** e o **vice**. Por padrão o candidato é o fundador e a chapa vai sem vice. O fundador pode escolher outro filiado como candidato e **convidar um vice** até o fim da inscrição de chapas. O vice só conta depois de **aceitar** o convite; sem resposta, a chapa concorre sem vice.

### A promessa na régua

Cada partido assume uma posição de 1 a 5 numa régua entre **impostos baixos** e **gasto alto**:

| Faixa | Posição |
| --- | --- |
| 1 | Impostos bem baixos (corte geral de imposto) |
| 2 | Impostos baixos (isenção para um setor) |
| 3 | Meio-termo |
| 4 | Gasto alto (taxa um setor) |
| 5 | Gasto bem alto (imposto geral novo) |

A promessa decide para onde vão os votos de quem sai no 2º turno (veja abaixo). Governar a partir da promessa não faz parte desta versão da expansão.

## Como a verba vira votos

O **apoio** de um partido cresce pela **raiz quadrada** do que ele gasta: dobrar a verba **não** dobra os votos. A conta de cada mês é

> pontos = √(verba do mês) ÷ 64

e o resultado é quantos eleitores, em cada 100, passam a votar no partido. Exemplos:

- **R$ 8.000** num mês: √8.000 ≈ 89,4; ÷ 64 = **1,4 ponto**.
- **R$ 16.000** no mês (o dobro): √16.000 ≈ 126,5; ÷ 64 = **2,0 pontos**, e não 2,8.

Os pontos de cada mês de campanha se somam. Por isso muitos contribuintes pequenos rendem mais votos por real do que um só doador grande.

A contribuição de cada filiado é debitada do caixa no **1º dia útil de cada mês** de campanha. Se faltar caixa naquele mês, a contribuição é **pulada** (não vira dívida).

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
