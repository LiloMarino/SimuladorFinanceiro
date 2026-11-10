import type { MetricInfo } from "@/shared/lib/metric-info";
import { signedIpca } from "@/shared/lib/effects";
import { displayPoints } from "@/shared/lib/budget-metrics";
import { displayPercent } from "@/shared/lib/utils/display";
import type { GeneralKind } from "./government";
import { salariesLabel } from "./presidency";

export const APPROVAL: MetricInfo = {
  label: "Aprovação",
  description: "De cada 100 eleitores, quantos aprovam o governo",
  definition:
    "É a média da satisfação dos 6 grupos de eleitores, pesada pelo tamanho de cada um. Cada grupo anda um terço do caminho até o alvo dele a cada fim de mês, e o alvo sai do que o grupo lê: inflação, juro real, bolsa, desemprego, prêmio de risco da dívida e as medidas do governo.",
  example:
    "Ex.: se os grupos que somam 60% do eleitorado estão em 70 e os outros 40% estão em 40, a aprovação geral é 0,6 × 70 + 0,4 × 40 = 58.",
  reading:
    "Acima de 50, o governo tem folga. Abaixo de 25 por 6 fechamentos seguidos, depois do primeiro ano, abre o pedido de impeachment, que a casa vota. A leitura vale para o mês: a aprovação se mede de novo no fechamento de cada mês.",
  format: (value) => `${value}%`,
};

export const SATISFACTION: MetricInfo = {
  label: "Satisfação",
  description: "De cada 100 pessoas do grupo, quantas aprovam o governo",
  definition:
    "A fatia do grupo que aprova o governo hoje. Na posse, cada grupo começa na proporção em que votou no presidente no turno que decidiu a eleição.",
  example: "Ex.: aposentados em 37 significa que 37 de cada 100 aposentados aprovam o governo.",
  reading:
    "Acima de 55, o grupo aprova o mês e o apoio ao partido do presidente sobe nele; abaixo de 45, reprova e a rejeição sobe. Entre os dois, fica neutro e nada muda.",
  format: (value) => `${value}`,
};

export const TARGET: MetricInfo = {
  label: "Alvo",
  description: "Onde a satisfação do grupo para se nada mudar",
  definition:
    "Sai do que o grupo lê (inflação, juro real, bolsa, desemprego e prêmio de risco da dívida) e das medidas que valem. A satisfação anda um terço do caminho até o alvo a cada fim de mês.",
  example: "Ex.: com satisfação 40 e alvo 70, o grupo vai a 50 no próximo fechamento, depois a 57 e a 61.",
  reading: "Alvo acima da satisfação: o grupo está melhorando. Abaixo: está piorando, mesmo que hoje ainda aprove.",
  format: (value) => `${value}`,
};

export const FORECAST: MetricInfo = {
  label: "Placar previsto",
  description: "Quantos votos Sim a medida deve ter, em faixa",
  definition:
    "Soma os votos Sim se cada bancada seguir a orientação, menos os deputados que podem votar contra porque a medida contraria quem elegeu a bancada. A faixa vai do pior caso (todos os que podem desobedecer votam contra) ao melhor (ninguém desobedece).",
  example:
    "Ex.: Sim 53 a 60 significa 60 votos se ninguém desobedecer e 53 se todos os 7 que podem desobedecer votarem Não.",
  reading:
    "A medida passa com 51 votos ou mais, de 101. Faixa toda acima de 51: passa. Toda abaixo: cai. Atravessando o 51: depende de quem desobedecer.",
  format: (value) => `${value}`,
};

export const DEFIANCE: MetricInfo = {
  label: "Pode desobedecer",
  description: "Deputados que podem votar contra a orientação do líder",
  definition:
    "Cada deputado é sorteado na votação. A chance de votar contra cresce com o quanto os eleitores da bancada querem o voto oposto ao orientado, e nunca passa de um terço da bancada.",
  example:
    "Ex.: os investidores são 40% de quem elegeu o MRC e perdem com a medida. Se o MRC orientar Sim, até 4 dos 16 deputados podem votar Não.",
  reading:
    "Quanto menor, mais a bancada é previsível: 0 significa que ela vota como o líder orientou. Um terço da bancada é o máximo.",
  format: (value) => `${value}`,
};

export const WITH_GOVERNMENT: MetricInfo = {
  label: "Com o governo",
  description: "Em quantos por cento das votações a bancada votou Sim",
  definition:
    "Entre as medidas que o presidente já levou à casa, a fatia dos deputados da bancada que votou Sim. Vem sempre com o número de votações: 100% de 2 votações pesa menos que 80% de 12.",
  example: "Ex.: 75% em 8 votações: de cada 4 votos da bancada, 3 foram Sim.",
  reading:
    "Perto de 100%, a bancada é da base do governo; perto de 0%, é da oposição. Com poucas votações o número ainda varia muito.",
  format: (value) => `${value}%`,
};

export const DEFECTION_RATE: MetricInfo = {
  label: "Desobediência",
  description: "Dos deputados da bancada, quantos por cento votaram contra o líder",
  definition: "Média, nas votações já feitas, dos deputados da bancada que votaram contra a orientação do líder.",
  example: "Ex.: 6% em 8 votações: de cada 100 votos da bancada, 6 foram contra o líder.",
  reading:
    "Perto de 0%, o líder manda na bancada. Acima de 15%, ele orienta contra o que os eleitores da bancada querem, com frequência.",
  format: (value) => `${value}%`,
};

export const BASE_SEATS: MetricInfo = {
  label: "Base do governo",
  description: "Cadeiras que orientam Sim em tudo o que o governo propõe",
  definition:
    "É a bancada do partido do presidente mais as bancadas aliadas, que recebem emenda em troca de orientar Sim. São 101 cadeiras; 51 aprovam uma medida e 68 derrubam o presidente.",
  example: "Ex.: 33 cadeiras do governo + 24 de aliados = base de 57, que passa a maioria de 51 com 6 de folga.",
  reading:
    "Abaixo de 51, cada medida depende de como as outras bancadas votam. Acima de 51, o governo aprova com folga, mas até um terço de cada bancada ainda pode desobedecer o líder.",
  format: (value) => `${value}`,
};

export const BASE_DEFECTION: MetricInfo = {
  label: "Desobediência",
  description: "Deputados da base que votaram contra a orientação na última medida",
  definition:
    "Mesmo com acordo, o líder não manda em todos: até um terço de cada bancada da base ainda pode votar contra a orientação Sim.",
  example: "Ex.: 3 deputados da base votaram Não numa medida que a base orientou Sim.",
  reading:
    "Poucos deputados não mudam o resultado quando a folga sobre a maioria é grande. Com a base perto de 51, três votos contra podem derrubar a medida.",
  format: (value) => `${value}`,
};

export const AMENDMENTS: MetricInfo = {
  label: "Emendas",
  description: "O que o governo paga por mês às bancadas aliadas",
  definition:
    "Cada cadeira aliada custa 0,005% do PIB por ano (o centrão, 1,5 vez). A emenda é gasto como outro qualquer: soma ao déficit e vira dívida.",
  example: "Ex.: 11 cadeiras × 0,005% = 0,055% do PIB por ano. Com PIB de R$ 9 tri, são cerca de R$ 41 mi por mês.",
  reading:
    "Quanto mais cadeiras compradas, maior o gasto e a dívida no fim do mandato. Vale pesar a maioria que se ganha contra o prêmio de risco que a dívida cobra.",
  format: (value) => `${value}`,
};

export const BARRIER: MetricInfo = {
  label: "Barreira de 5%",
  description: "O mínimo de votos válidos para ter cadeira",
  definition:
    "O partido que não alcança 5% dos votos válidos da eleição da casa fica sem cadeira, e os votos dele não entram na divisão.",
  example: "Ex.: com 4,2% dos votos, o partido fica de fora; com 5,3%, entra e leva umas 5 cadeiras de 101.",
  reading: "Partido pequeno precisa passar da barreira antes de pensar em bancada.",
  format: (value) => `${value}%`,
};

export const DHONDT: MetricInfo = {
  label: "Como os votos viram cadeiras",
  description: "O método D'Hondt, que divide as 101 cadeiras",
  definition:
    "Os votos de cada partido são divididos por 1, 2, 3 e assim por diante. As 101 maiores divisões levam uma cadeira cada, então a cadeira seguinte de um partido sempre vale menos votos que a anterior.",
  example:
    "Ex.: com 40, 35 e 25 votos, o primeiro partido leva a 1ª cadeira (40), o segundo a 2ª (35), o terceiro a 3ª (25), e a 4ª volta ao primeiro (40÷2 = 20)... até as 101 saírem.",
  reading:
    "O partido maior leva uma fatia de cadeiras um pouco acima da fatia de votos; os pequenos ficam um pouco abaixo.",
  format: (value) => `${value}`,
};

export const REVENUE: MetricInfo = {
  label: "Receita",
  description: "O que o governo arrecada no país em um ano",
  definition:
    "Tudo o que o governo recebe em impostos, medido em % do PIB por ano. Os impostos que o presidente muda são o consumo, o IR das empresas, o IR das pessoas, a contribuição sobre a folha e os do investimento (ações, day trade, renda fixa). O IR que os jogadores pagam não entra: as operações da sala são pequenas perto do país.",
  example: "Ex.: 18,38% de um PIB de R$ 7,4 tri são R$ 1,36 tri por ano, ou uns R$ 113 bi por mês.",
  reading:
    "Mexer na alíquota muda a receita, mas menos que proporcionalmente: quem paga menos passa a operar mais. Receita acima do gasto sobra e a dívida cai; abaixo, falta e a dívida sobe.",
  format: (value) => displayPercent(value, 2),
};

export type TaxPrice = { definition: string; example: string; reading: string };

/** O que cada imposto do país cobra além da arrecadação: o preço que o presidente paga ao mexer na alíquota. */
export const TAX_PRICE: Partial<Record<GeneralKind, TaxPrice>> = {
  CONSUMPTION_TAX_RATE: {
    definition:
      "Imposto embutido no preço do que as famílias compram. É a maior fonte de receita e a que menos reage à alíquota: aumentar arrecada quase na mesma proporção.",
    example:
      "Ex.: subir a alíquota de 18% para 22% em um ano soma uns 2 pontos ao IPCA (a inflação em 12 meses); a SELIC sobe com ela e a bolsa cai.",
    reading:
      "Cortar o imposto tira inflação e levanta a bolsa, mas abre um buraco na receita. Beneficiários, trabalhadores formais e aposentados são os que mais reclamam do aumento.",
  },
  CORPORATE_INCOME_TAX_RATE: {
    definition:
      "Imposto sobre o lucro das empresas. Quem paga mais vê o lucro encolher, e a bolsa desconta isso no preço das ações. É o imposto que mais reage à alíquota: subir muito arrecada menos que o esperado.",
    example: "Ex.: alíquota 5 pontos acima da padrão (39% contra 34%) tira 6% da bolsa; 5 pontos abaixo levanta 6%.",
    reading: "Cortar levanta a bolsa e agrada empreendedores e investidores; subir enche o caixa, mas pesa nas ações.",
  },
  PERSONAL_INCOME_TAX_RATE: {
    definition:
      "Imposto de renda descontado dos salários e das aposentadorias privadas. Não mexe na inflação nem na bolsa: o preço é político.",
    example:
      "Ex.: subir a alíquota em 3 pontos arrecada mais, mas quem paga (investidores, empreendedores, trabalhadores formais e servidores) perde satisfação.",
    reading: "Cortar agrada quem paga, mas tira receita; a conta é entre o caixa e a aprovação.",
  },
  PAYROLL_TAX_RATE: {
    definition:
      "Contribuição que a empresa paga em cima de cada salário. Com ela mais alta, contratar custa mais e o desemprego sobe aos poucos.",
    example:
      "Ex.: alíquota 5 pontos acima da padrão (25% contra 20%) soma 0,3 ponto por ano à taxa de desemprego, até a alíquota voltar.",
    reading:
      "Cortar cria vagas e arrecada menos; subir arrecada mais, mas o trabalhador formal e a inflação (pela curva de Phillips) sentem.",
  },
};

export const PRIMARY_RESULT: MetricInfo = {
  label: "Resultado primário",
  description: "Receita menos gasto, sem contar os juros da dívida",
  definition:
    "O que sobra (superávit) ou falta (déficit) depois de o governo pagar suas despesas, antes de pagar os juros da dívida. As medidas de imposto mexem aqui.",
  example: "Ex.: receita de R$ 113,3 bi e gasto de R$ 113,5 bi no mês dão primário de −R$ 0,2 bi: faltou um pouco.",
  reading:
    "Positivo é bom: sobra dinheiro para a dívida cair. Negativo por muito tempo faz a dívida subir, e o prêmio de risco junto.",
  format: (value) => displayPercent(value, 2),
};

export const INTEREST: MetricInfo = {
  label: "Juros da dívida",
  description: "Quanto o governo paga só para carregar a dívida",
  definition:
    "A dívida vezes o juro que ela paga: a SELIC mais o prêmio de risco. Sai da conta todo mês, mesmo que o governo não gaste nada de novo.",
  example: "Ex.: dívida de 77,8% do PIB com juro de 5,7% ao ano custa 4,4% do PIB por ano em juros.",
  reading:
    "Quanto menor, melhor. SELIC alta e dívida alta se somam, e o prêmio faz o juro subir justamente quando a dívida cresce.",
  format: (value) => displayPercent(value, 2),
};

export const RESULT: MetricInfo = {
  label: "Resultado",
  description: "O que sobra ou falta depois de pagar os juros",
  definition:
    "O resultado primário menos os juros da dívida. Se for negativo (déficit), o governo se endivida para fechar o mês, e o déficit vira dívida.",
  example: "Ex.: −R$ 0,1 bi de primário e −R$ 27,1 bi de juros dão resultado de −R$ 27,2 bi no mês.",
  reading:
    "Positivo, a dívida cai. Negativo, a dívida sobe, mas a economia crescendo também faz a dívida pesar menos no PIB.",
  format: (value) => displayPercent(value, 2),
};

export const QUEUE_BUDGET: MetricInfo = {
  label: "No orçamento",
  description: "Quanto a medida muda o resultado do governo",
  definition:
    "A variação do resultado do governo (receita menos gasto) que a medida causa, em % do PIB por ano. Verde melhora o resultado: imposto que arrecada mais ou gasto que cai. Vermelho piora: imposto que arrecada menos ou gasto que sobe. É uma estimativa: supõe a medida valendo e mais nada mudando.",
  example:
    "Ex.: −0,08% quer dizer que o governo passa a faltar 0,08% do PIB a mais por ano, uns R$ 5,9 bi num PIB de R$ 7,4 tri.",
  reading:
    "Resultado pior aumenta o déficit e a dívida; melhor, o contrário. Medida de poucos centésimos quase não pesa na conta do país.",
  format: (value) => displayPercent(value, 2),
};

export const QUEUE_INFLATION: MetricInfo = {
  label: "Na inflação",
  description: "Pontos que a medida soma ao IPCA de 12 meses, no pico",
  definition:
    "Só as medidas de gasto mexem aqui. O IPCA de 12 meses é a inflação acumulada no último ano; a medida soma ou tira pontos dele. O efeito demora: enche em 6 meses, vale cheio no pico e cai pela metade a cada 12 meses. Vermelho é inflação a mais; verde, a menos.",
  example: "Ex.: +0,25 com o IPCA em 3,3% leva o 12 meses a 3,55% no pico, uns 6 meses depois de a medida valer.",
  reading:
    "Inflação a mais desagrada quem lê a inflação, e o Banco Central autônomo sobe a SELIC 1,5 vez o tanto; com a SELIC do governo, ela só sobe no Copom. Abaixo de 0,1 ponto quase não se sente.",
  format: (value) => `${signedIpca(value)} ponto`,
};

export const INFLATION_EXPECTED: MetricInfo = {
  label: "Inflação esperada",
  description: "Quanto a medida muda o IPCA de 12 meses, no pico",
  definition:
    "A medida de gasto põe mais (ou menos) dinheiro nas mãos de quem consome, e os preços reagem meses depois. O efeito enche em 6 meses, vale cheio no pico e cai pela metade a cada 12 meses. Vale para a partida inteira, na história e no futuro gerado, e a série guardada não muda: a diferença aparece tracejada no painel da economia.",
  example:
    "Ex.: +0,55 ponto com o IPCA em 3,3% leva o 12 meses a 3,85% no pico. Com o Banco Central autônomo, que responde com 1,5 vez o tanto, a SELIC sobe 0,83 ponto.",
  reading:
    "Pontos a mais pesam contra o governo: os grupos que leem a inflação reprovam, a SELIC sobe (sozinha ou no Copom) e a bolsa cai. Menos de 0,1 ponto quase não se sente.",
  format: (value) => `${signedIpca(value)} ponto`,
};

export const SPENDING_COST: MetricInfo = {
  label: "Custa",
  description: "Quanto a medida pesa no gasto do governo, por ano",
  definition:
    "A parte do gasto do governo que a medida ocupa hoje, em % do PIB por ano e em reais por ano. No reajuste, é a folha de pagamento que ele multiplica, e ela cresce todo janeiro.",
  example: "Ex.: 1,40% de um PIB de R$ 7,4 tri são uns R$ 104 bi por ano.",
  reading:
    "Gasto maior que a receita aumenta o déficit e a dívida. O que a medida custa não diz se vale a pena: pese também o que ela faz com a inflação e com os grupos de eleitores.",
  format: (value) => displayPercent(value, 2),
};

export const SPENDING_INFLATION_NOW: MetricInfo = {
  label: "Na inflação agora",
  description: "Pontos de IPCA que a medida põe hoje",
  definition:
    "O quanto da medida já chegou ao IPCA de 12 meses neste dia. Sobe nos primeiros 6 meses depois de a medida valer, fica cheio no pico e cai pela metade a cada 12 meses.",
  example: "Ex.: +0,12 hoje e +0,25 no pico: a medida ainda está chegando e vai pesar mais nos próximos meses.",
  reading: "Zero ou traço: o efeito ainda não começou ou já sumiu. Vermelho é inflação a mais; verde, a menos.",
  format: (value) => `${signedIpca(value)} ponto`,
};

export const COPOM_SELIC: MetricInfo = {
  label: "SELIC",
  description: "O juro básico do país, ao ano; muda só nas reuniões do Copom",
  definition:
    "A taxa que serve de base para todos os outros juros: o CDI, os títulos do Tesouro, o crédito e o juro da dívida do governo. Nesta partida quem decide é o presidente, nas 8 reuniões do Copom do ano; a taxa nova vale do dia seguinte à reunião.",
  example:
    "Ex.: com a SELIC a 10,75% ao ano, R$ 100 parados nela viram R$ 110,75 em um ano. Com ela em −0,5%, viram R$ 99,50: a renda fixa pós-fixada perde valor e o dinheiro no caixa, que rende 0%, passa a render mais.",
  reading:
    "Subir a SELIC segura a inflação meses depois, mas encarece o crédito, derruba a bolsa e aumenta o juro da dívida. Baixar faz o contrário. O piso é 0%; só com o IPCA de 12 meses negativo (deflação) ele desce a −0,5%, o do Banco Central Europeu, e volta a 0% na reunião seguinte ao IPCA voltar a zero ou mais. Os bancos centrais não descem muito abaixo de zero porque as pessoas sacam o dinheiro.",
  format: (value) => displayPercent(value, 2),
};

export const COPOM_FOCUS: MetricInfo = {
  label: "Mercado espera",
  description: "A SELIC que o mercado espera para a próxima reunião do Copom",
  definition:
    "O Focus é a pesquisa semanal em que o Banco Central pergunta a bancos e consultorias a SELIC que eles esperam; vale a mediana. Fora da pesquisa (antes de nov/2004, no futuro gerado ou com a última pesquisa de mais de 30 dias), parte da SELIC de hoje. Sobre essa base o mercado soma o que espera do presidente: a regra do Banco Central e o quanto a última decisão ficou longe dela. A bolsa já tem esse número no preço.",
  example:
    "Ex.: o mercado espera 13,25% e o Copom decide 12,25%: é 1 ponto de surpresa para baixo, e a bolsa sobe uns 3% no dia em que a decisão passa a valer. Decidindo 13,25%, ela não se mexe.",
  reading:
    "A bolsa reage à distância entre a decisão e este número, e não à SELIC em si: 2,9% por ponto, para baixo se a decisão vier acima e para cima se vier abaixo. Decidir o que o mercado espera é neutro; quem se afasta da regra do Banco Central tem a surpresa cobrada no dia.",
  format: (value) => displayPercent(value, 2),
};

export const POLICY_REAL_RATE: MetricInfo = {
  label: "Juro real",
  description: "A SELIC menos a inflação: quanto o dinheiro rende de verdade",
  definition:
    "A SELIC menos o IPCA dos últimos 12 meses. É ele que mexe na inflação: abaixo da história, o crédito barato aquece a economia e a inflação sobe com até um ano de atraso (0,3 ponto de IPCA por ponto abaixo, mantido por um ano). O neutro, de 5%, é o juro real que nem aquece nem esfria a economia.",
  example: "Ex.: SELIC de 10,75% com IPCA de 4,5% dá juro real de 6,25%, um pouco acima do neutro: esfria devagar.",
  reading:
    "Os grupos de eleitores aceitam entre 2% e 7%. Abaixo de 2%, aposentados e investidores reclamam que a renda fixa não rende; acima de 7%, trabalhadores com carteira e empreendedores reclamam do crédito caro.",
  format: (value) => displayPercent(value, 2),
};

export const MEETING_CAP: MetricInfo = {
  label: "Teto da reunião",
  description: "O quanto a SELIC pode andar numa reunião, para cima ou para baixo",
  definition:
    "Cada reunião anda em passos de 0,25 ponto, até 3 pontos, para cima ou para baixo, com qualquer IPCA (a maior alta do Copom desde 1999). A janela sempre alcança a SELIC da história no dia, por mais que ela tenha andado desde a reunião anterior, e não desce do piso: 0%, ou −0,5% com o IPCA de 12 meses negativo.",
  example:
    "Ex.: SELIC de 10,75% com teto de 3 pontos: a reunião pode levá-la de 7,75% a 13,75%. Com a SELIC em 21% e a história em 25% no dia, a janela vai até 25%.",
  reading: "O juro que foge muito da história tem custo: a credibilidade cai e o mercado cobra prêmio de risco.",
  format: (value) => displayPoints(Number(value) * 100, 2),
};

export const CREDIBILITY: MetricInfo = {
  label: "Credibilidade",
  description: "O quanto o mercado confia que a SELIC vai segurar a inflação, de 0 a 100",
  definition:
    "Começa em 100, e a régua é a história. Cada reunião com o juro real da partida abaixo do da história e o IPCA acima da meta mais a tolerância tira 4 pontos por ponto abaixo da história, até 20 por reunião; cada alta da SELIC, ou juro real igual ou acima do da história, devolve 3. Sem credibilidade, a dívida paga até 2 pontos de prêmio de risco a mais, e o juro real baixo pesa até o dobro na inflação, mais cedo.",
  example:
    "Ex.: a história com juro real de 5% e a partida com 1%, com o IPCA acima da meta mais a tolerância: fica 4 pontos abaixo, a reunião tira 16 e a credibilidade vai a 84, com 0,32 ponto de prêmio a mais e o efeito do juro na inflação 1,16 vez maior.",
  reading:
    "100 é a confiança toda, e copiar a SELIC da história a mantém. Abaixo de 80 já custa prêmio e inflação; recuperar é lento, 3 pontos por reunião.",
  format: (value) => `${Math.round(Number(value))} de 100`,
};

export const PRESIDENT_SALARY: MetricInfo = {
  label: "Salário",
  description: "O que o cargo paga por mês, no lugar da renda da sua profissão",
  definition:
    "Enquanto governa, o presidente recebe 3 vezes o salário da partida por mês, no lugar da renda da profissão. O sorteio de salário não pago não vale no cargo, e as despesas continuam as mesmas. O pagamento acaba quando o sucessor toma posse.",
  example: "Ex.: com salário de R$ 8.000 na partida, o cargo paga 3 × R$ 8.000 = R$ 24.000 por mês.",
  reading:
    "Quanto maior o salário da partida, maior o ganho do cargo. Com salário zero na partida, o cargo também paga zero.",
  format: (value) => `${value}`,
};

export const LEGACY: MetricInfo = {
  label: "Legado acumulado",
  description: "O que o governo já rendeu para você levar ao deixar o cargo",
  definition:
    "Cada mês fechado do governo soma 0,05 salário por ponto de aprovação acima de 40. O total é pago em dinheiro, pelo salário da partida do dia, quando o mandato termina normalmente, inclusive o primeiro mandato de quem se reelege. O impeachment perde tudo.",
  example: "Ex.: com salário de R$ 8.000 e aprovação 60, o mês soma (60 − 40) × 5% = 1 salário, R$ 8.000.",
  reading:
    "Aprovação 60 soma 1 salário por mês, 80 soma 2 e 40 ou menos soma 0. Em 48 meses com aprovação 60, o legado chega a 48 salários. Sustentar a aprovação até o fim do mandato é o que paga.",
  format: (value) => salariesLabel(value),
};

export const SECTOR_BOOST: MetricInfo = {
  label: "Alta do setor",
  description: "Quanto as ações do setor sobem por causa da obra ou da emenda",
  definition:
    "É um empurrão no preço das ações do setor ou do segmento apontado. Sobe em linha reta por 6 meses, a partir do dia em que a obra passa a valer (ou o acordo começa), e fica lá enquanto durar. Na obra, vale 2,5 vezes a fatia do PIB gasta, até +7,5%. Na emenda, vale 30 vezes a fatia do PIB que o acordo paga por ano, até +6%. Junto com a isenção do setor, a alta total nunca passa de +20%.",
  example:
    "Ex.: uma obra de 1,2% do PIB em Energia dá 1,2% × 2,5 = +3%. Depois de 3 meses a alta é de +1,5%; no 6º mês, +3%. Se a obra mudar de setor, o setor antigo perde a alta no mesmo dia.",
  reading:
    "Quanto maior, mais o setor valoriza para quem tem ações dele. Quem aponta a obra para um setor em que investe ganha na bolsa, mas paga em aprovação (ver Favorecimento).",
  format: (value) => `${value}`,
};

export const FAVORITISM: MetricInfo = {
  label: "Favorecimento",
  description: "Aprovação que o presidente perde por apontar a obra para um setor em que investe",
  definition:
    "Mede a fatia da carteira do presidente que está no setor da obra. Cada grupo de eleitores perde 6 pontos de alvo de aprovação para cada 100% da carteira nesse setor, enquanto a obra valer.",
  example:
    "Ex.: com 30% da carteira em Energia, a obra em Energia custa 6 × 0,30 = 1,8 ponto de alvo de aprovação em todos os grupos. Com 5% da carteira, custa 0,3 ponto.",
  reading:
    "Perto de zero, o presidente quase não tem interesse no setor e o custo é pequeno. Acima de 3 pontos, a obra pesa na aprovação, e o ganho na bolsa precisa compensar.",
  format: (value) => `${value}`,
};
