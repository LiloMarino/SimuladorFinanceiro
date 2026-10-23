---
sidebar_position: 9
---

# Governo e eleições

O host pode ativar **Governo** em **Regras da partida → Expansões**, antes de começar.
A partida precisa durar ao menos cinco anos. A carreira política é voluntária:
quem não se filiar nem aceitar uma candidatura continua investindo normalmente.
Ser host não concede poderes de presidente.

## Partido e campanha

Na página **Eleição**, funde um partido com nome, sigla, cor e programa na régua de
1 a 5. Cada jogador pode pertencer a um partido; também pode sair livremente.
O fundador indica candidato e vice entre os filiados. A indicação de outra pessoa
precisa de aceite pessoal, e pode ser recusada mantendo a filiação. Inscrever a
própria candidatura já expressa o aceite.

Cada filiado escolhe sua contribuição mensal, inclusive zero. Durante a campanha,
o valor sai do caixa disponível no primeiro dia de cada mês; se faltar dinheiro,
é limitado ao saldo disponível. O gasto reduz patrimônio e retorno financeiro.
O partido não recebe patrimônio para distribuir: a verba é consumida na campanha.
Filiações, contribuições, doações e expulsões são públicas.

A campanha abre em 7 de outubro do ano anterior à eleição. A primeira eleição
ocorre no ano seguinte ao início da partida, e as seguintes a cada quatro anos.
O primeiro turno é em **7 de outubro**; é preciso superar 50% dos votos válidos.
Caso contrário, os dois melhores disputam o segundo turno em **28 de outubro**.
A posse é em **1º de janeiro**, com mandato de quatro anos e uma reeleição.
Datas de calendário que caem no fim de semana são processadas pelo próximo tick,
mantendo a data original no registro.

O computador completa as vagas até três chapas, com programas distribuídos pela
régua. Sua verba mensal corresponde a 0,5, 1 ou 1,5 vez a média das contribuições
humanas, conforme a dificuldade. Sem candidatos humanos, usa R$ 8 mil como média.
Entre turnos, jogadores não filiados e filiados de partidos eliminados podem doar
a um finalista; a doação é pública e descontada uma única vez.

A verba tem retorno decrescente: R$ 8 mil no mês acrescentam 1,4 de alcance;
R$ 16 mil acrescentam aproximadamente 2. A pesquisa combina alcance, programa,
aprovação do candidato que governa e preferências dos perfis de eleitores:

| Perfil | Peso inicial | Posição na régua |
| --- | ---: | ---: |
| Investidores | 25% | 1,5 |
| Empreendedores | 30% | 2,5 |
| Serviços públicos | 30% | 4,5 |
| Equilíbrio fiscal | 15% | 3 |

Os pesos ficam fixos na partida. No segundo turno, cada perfil compara os
finalistas novamente. As pesquisas são atualizadas no calendário da campanha.

## Governar

Só o presidente em exercício pode publicar e retirar propostas ou decidir a SELIC
quando essa opção está ligada. Todos podem consultar as propostas e **simular uma
medida**, sem gravá-la nem gastar dinheiro.

O Congresso vota a fila no fechamento do mês. A chance de cada proposta passar é
a aprovação do governo no momento do voto. Uma rejeitada pode ser reapresentada;
uma aprovada entra em vigor **90 dias corridos depois**. Até lá, permanece pública
para os demais jogadores ajustarem suas carteiras.

Os instrumentos disponíveis são IR comum, day trade e FIIs; limite da isenção
mensal de ações; ajuste da tabela regressiva da renda fixa; IR de LCI/LCA; ajuste
do IR por setor ou segmento; tarifa de importação por produto; e investimento
público. As regras em vigor aparecem no painel. IR altera a cobrança sobre ganhos;
as tarifas também afetam a cotação através do modelo empresarial.

A carteira do presidente é pública e fica congelada durante o exercício do cargo.
Ordens abertas são canceladas na posse. Compras e vendas discricionárias ficam
bloqueadas; rendimentos, impostos, aportes e vencimentos seguem automáticos.

A aprovação parte de 50%, é apurada mensalmente e considera inflação, bolsa em
12 meses, medidas tributárias recentes e distância do programa prometido.
O padrão é impeachment após **três meses consecutivos abaixo de 25%**. O vice
assume; sem vice, um governo neutro aguarda a próxima eleição. Propostas ainda
não votadas são retiradas; medidas já aprovadas mantêm sua vigência. O ex-presidente
volta a operar sua carteira.

## Produtos, gasto e juros

**Impactos e modelo** compara o preço com e sem os efeitos do governo, mantendo a
mesma série de referência. As exposições de aço, petróleo, alimentos e tecnologia
são hipóteses do cenário. Uma tarifa pode ajudar um produtor local e prejudicar
uma empresa que importa o insumo. Ativos sem perfil são identificados como
**cobertura insuficiente para produtos**; os efeitos monetários ainda podem valer.

O orçamento começa em R$ 1 bilhão e recebe o IR efetivamente recolhido dos
jogadores, inclusive retenções da renda fixa, nos fechamentos mensais. Cada programa
de investimento público custa de R$ 1 milhão a R$ 100 milhões e precisa caber no
orçamento livre. A aprovação reserva o valor; a execução na vigência o consome.
Cada R$ 100 milhões acrescentam **1 ponto percentual à inflação anual**, após
30 dias de execução, com meia-vida de 365 dias.

Com o Banco Central autônomo, a SELIC ganha 1,5 vez a inflação adicional. Com
controle presidencial, uma decisão estabelece a taxa usada por SELIC e CDI no
modelo. O intervalo mínimo é de 45 dias. A variação máxima por decisão é de 0,75
ponto percentual; sobe para 1,5 quando a inflação supera a meta em 2 pontos, e
para 3 quando supera em 10 pontos. A meta inicial de inflação do jogo é 3%.
Cada ponto de SELIC abaixo da referência acrescenta 0,25 ponto à inflação após
90 dias; acima da referência, o efeito tem sinal oposto.

Esses números são regras de jogo aprovadas para a primeira versão jogável.
Eles ficam gravados na partida, junto com os perfis e a versão do modelo.

## Quem vence

O host escolhe se vale o ranking financeiro individual ou a soma dos patrimônios
dos filiados de cada partido. A vitória por partidos exige partida clássica com
jogadores individuais. Os dois rankings permanecem visíveis; partidos do computador
não entram na disputa financeira. Se ninguém fundar um partido humano, vale o
ranking individual. Em empate de patrimônio entre partidos, vence o de menor
identificador, correspondente à fundação mais antiga.
