import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoney, displayNumber, displayPercent, displaySignedPercent } from "@/shared/lib/utils/display";

export const REAL_RAISE: MetricInfo = {
  label: "Reajuste acima do IPCA",
  description: "Quanto o salário sobe por ano além da inflação",
  definition:
    "Todo ano o salário é corrigido pelo IPCA (a inflação) e ainda ganha este aumento por cima. Positivo, o salário compra mais a cada ano; zero, ele só acompanha os preços.",
  example: "Ex.: IPCA de 4% e reajuste de +1,5% acima dele → o salário sobe 5,5% na virada do ano.",
  reading: "Quanto maior, melhor. Zero quer dizer que a renda só repõe a inflação, sem ganhar poder de compra.",
  format: (value) => displaySignedPercent(value, 1),
};

export const LAYOFF_CHANCE: MetricInfo = {
  label: "Chance de demissão",
  description: "Quantas vezes a chance normal de perder a renda",
  definition:
    "O sorteio mensal de demissão tem uma chance normal. Esta métrica diz quantas vezes ela está maior ou menor agora, de acordo com o desemprego do país.",
  example:
    "Ex.: 0,6× a normal com o desemprego em 5,5% (o neutro é 9%): se a chance normal fosse de 10 em 1.000 por mês, hoje seriam 6 em 1.000.",
  reading:
    "Abaixo de 1× é melhor que o normal; acima de 1× é pior. Desemprego acima do neutro aumenta a chance, abaixo diminui.",
  format: (value) => `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(Number(value))}× a normal`,
};

export const HEALTH_COST: MetricInfo = {
  label: "Imprevisto de saúde",
  description: "Quantas vezes o custo normal de um imprevisto de saúde",
  definition:
    "Um imprevisto de saúde sorteado custa um valor normal do caixa. Algumas escolhas multiplicam esse custo, como a hora extra do CLT.",
  example: "Ex.: 2× o custo com a hora extra ligada → um imprevisto de R$ 3.000 passa a custar R$ 6.000.",
  reading: "1× é o custo normal. Acima disso, mantenha mais caixa de reserva para aguentar o imprevisto.",
  format: (value) => `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(Number(value))}× o custo`,
};

export const FGTS_BALANCE: MetricInfo = {
  label: "Saldo do FGTS",
  description: "Conta da empresa que fica no patrimônio, fora do caixa",
  definition:
    "Todo mês a empresa deposita 8% do salário bruto numa conta que rende 3% ao ano mais a TR. O dinheiro conta no patrimônio, mas só chega ao caixa se você for demitido.",
  example:
    "Ex.: salário bruto de R$ 5.600 → depósito de R$ 448 por mês. Na demissão, o saldo mais a multa de 40% caem no caixa.",
  reading: "Cresce sozinho e pesa na meta. Como é dinheiro preso, não conta para a reserva de emergência.",
  format: (value) => displayMoney(value),
};

export const OVERTIME: MetricInfo = {
  label: "Hora extra",
  description: "Mais renda agora, em troca de um imprevisto de saúde mais caro",
  definition:
    "Ligada, a renda bruta sobe 25% e o imprevisto de saúde custa o dobro. Só existe com o PIB de 12 meses em zero ou mais; na recessão a empresa corta a hora extra e ela fica desligada até você ligar de novo.",
  example:
    "Ex.: salário de R$ 4.850 com a hora extra ligada → +R$ 1.212,50 por mês, e um imprevisto de saúde de R$ 3.000 custa R$ 6.000.",
  reading:
    "Vale a pena com caixa de reserva folgado. Com reserva curta, o imprevisto dobrado pode levar ao cheque especial.",
  format: (value) => displayMoney(value),
};

export const GDP_12M: MetricInfo = {
  label: "PIB de 12 meses",
  description: "Quanto a economia cresceu nos últimos 12 meses",
  definition:
    "O quanto o país produziu a mais (ou a menos) do que um ano atrás. É o termômetro da atividade econômica.",
  example:
    "Ex.: PIB de +1,4% → o país produziu 1,4% a mais do que um ano atrás. Com o PIB acima de 2% (o neutro), o seu reajuste melhora.",
  reading:
    "Acima do neutro o reajuste melhora; abaixo de zero é recessão: o reajuste some e a hora extra do CLT é cortada.",
  format: (value) => displaySignedPercent(value, 1),
};

export const UNEMPLOYMENT: MetricInfo = {
  label: "Desemprego",
  description: "Parte de quem procura emprego e não acha",
  definition:
    "A fatia das pessoas que querem trabalhar e não conseguem vaga. Move a chance de demissão do sorteio mensal.",
  example: "Ex.: 5,5% → de cada 100 pessoas procurando emprego, 5 ou 6 estão sem.",
  reading:
    "No neutro de 9% a chance de demissão é a normal; com desemprego menor ela cai, com 18% ela sobe bem acima do normal.",
  format: (value) => displayPercent(value, 1),
};

export const TR: MetricInfo = {
  label: "TR (Taxa Referencial)",
  description: "Taxa oficial que corrige o FGTS e a poupança",
  definition: "Somada aos 3% ao ano fixos, é o que faz o saldo do FGTS render a cada mês.",
  example: "Ex.: TR de 0,29% ao ano → o FGTS rende 3,29% no ano.",
  reading: "Quase sempre perto de zero: na prática o FGTS rende pouco mais que os 3% ao ano e perde para a inflação.",
  format: (value) => displayPercent(value, 2),
};

export const TREASURY_FIXED: MetricInfo = {
  label: "Tesouro prefixado",
  description: "Título do governo com a taxa travada no dia da compra",
  definition: "Você sabe a taxa desde o começo e ela não muda, qualquer que seja o rumo da SELIC depois.",
  example: "Ex.: prefixado de 1 ano a 11,84% → R$ 1.000 viram R$ 1.118,40 no vencimento.",
  reading: "O CDB da casa paga 1 ponto acima do prefixado do mesmo prazo: é a vantagem de trabalhar no banco.",
  format: (value) => displayPercent(value, 2),
};

export const PARTY_MULTIPLE: MetricInfo = {
  label: "Renda do partido",
  description: "Quantas vezes o salário base você recebe",
  definition:
    "A renda do Comissionado depende de o partido dele estar no governo: dentro, ela é maior; se o partido perde a eleição, cai.",
  example:
    "Ex.: 1,5× o salário com o partido no governo, 0,5× se ele perder → de R$ 5.000 de base, R$ 7.500 ou R$ 2.500.",
  reading: "Acompanhe a eleição: é nela que a renda do Comissionado muda de patamar.",
  format: (value) => `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 }).format(Number(value))}× o salário`,
};

export const DOLLAR_CHANGE: MetricInfo = {
  label: "Variação do dólar em 12 meses",
  description: "Quanto o dólar subiu ou caiu em um ano",
  definition: "A diferença do preço do dólar em reais hoje contra o de um ano atrás.",
  example: "Ex.: +10% → o dólar que custava R$ 5,00 custa R$ 5,50.",
  reading: "Dólar alto tende a aumentar a renda de quem ganha em moeda estrangeira; dólar baixo a reduz.",
  format: (value) => displaySignedPercent(value, 1),
};

export const SELIC_RATE: MetricInfo = {
  label: "SELIC ao ano",
  description: "A taxa básica de juros da economia",
  definition: "O juro que o governo paga em seus títulos e que serve de base para todos os outros juros do país.",
  example: "Ex.: SELIC a 13,76% → um título de renda fixa pós-fixado rende cerca de 13,76% ao ano.",
  reading: "Para quem vive de renda de aluguel financeiro ou de juros, SELIC alta ajuda; para quem deve, pesa.",
  format: (value) => displayPercent(value, 2),
};

export const STOCKS_RETURN: MetricInfo = {
  label: "Retorno do Ibovespa em 12 meses",
  description: "Quanto a bolsa subiu ou caiu em um ano",
  definition: "A variação do índice Ibovespa, que resume as principais ações da bolsa, nos últimos 12 meses.",
  example: "Ex.: +20% → quem tinha R$ 10.000 numa carteira igual ao índice tem R$ 12.000.",
  reading: "Bolsa em alta aumenta a renda de profissões ligadas ao mercado; em queda, reduz.",
  format: (value) => displaySignedPercent(value, 1),
};

export const SERVANT_RAISE: MetricInfo = {
  label: "Aumento dos servidores",
  description: "O reajuste acima do IPCA que o governo da sala decidiu",
  definition: "Quanto o salário dos servidores sobe por ano além da inflação. É decisão do governo, não do mercado.",
  example: "Ex.: +1,5% ao ano com o IPCA a 4% → o salário sobe 5,5% na virada do ano.",
  reading: "Acompanhe as medidas do governo: cada mudança aparece na lista de mudanças recentes.",
  format: (value) => displaySignedPercent(value, 1),
};

export const RETIREE_RAISE: MetricInfo = {
  label: "Reajuste dos aposentados",
  description: "O reajuste acima do IPCA que o governo da sala decidiu",
  definition: "Quanto o benefício dos aposentados sobe por ano além da inflação. É decisão do governo.",
  example: "Ex.: +1,0% ao ano com o IPCA a 4% → o benefício sobe 5,0% na virada do ano.",
  reading: "Acompanhe as medidas do governo: cada mudança aparece na lista de mudanças recentes.",
  format: (value) => displaySignedPercent(value, 1),
};

export const WELFARE_SPENDING: MetricInfo = {
  label: "Gasto com auxílio",
  description: "Quanto do PIB o governo gasta com o auxílio",
  definition: "A parte do PIB que o governo destina ao auxílio. Quanto maior, maior o benefício pago a quem vive dele.",
  example: "Ex.: 5% do PIB contra 4% de referência → o auxílio paga 1,25× o de referência.",
  reading: "Acima da referência a renda sobe; abaixo, cai. Quem decide é o governo da sala.",
  format: (value) => displayPercent(value, 1),
};

export const LOCKED_DOLLAR: MetricInfo = {
  label: "Dólar travado (câmbio futuro)",
  description: "O dólar que você garante hoje para receber nos próximos meses",
  definition:
    "O dólar que você garante hoje para receber nos próximos meses. Ele é o dólar de hoje corrigido pela diferença entre o juro daqui e o de lá.",
  example:
    "Ex.: dólar a R$ 1,79, CDI a 13,66% e Fed Funds (o juro dos EUA) a 0,25%: em 12 meses o dólar travado é 1,79 × 1,1366 ÷ 1,0025 = R$ 2,0294.",
  reading:
    "Travar protege da queda do dólar e abre mão da alta. Se o dólar do dia cair abaixo do travado, a trava ganhou; se subir, perdeu.",
  format: (value) => `R$ ${displayNumber(value, 4)}`,
};

export const EXPORT_MIX: MetricInfo = {
  label: "Mix de exportação",
  description: "Quanto da receita vem de vender para fora",
  definition:
    "A parte exportada da receita segue o dólar; a parte vendida no Brasil segue o PIB. O mix é a fração de cada uma, e ele muda uma vez por trimestre.",
  example:
    "Ex.: 60% exportado com o dólar 12 meses em +6,1% (fator 1,05×) e o PIB a 1,4% (fator 0,98×): a renda base vai a 0,6 × 1,05 + 0,4 × 0,98 = 1,02×.",
  reading:
    "Com o dólar subindo, mais exportação rende mais; com o dólar caindo e o PIB firme, vender no Brasil protege a renda.",
  format: (value) => displayPercent(value, 0),
};

export const MARKET_REFERENCE: MetricInfo = {
  label: "Referência do mercado",
  description: "O preço que um autônomo da sua área cobra hoje",
  definition: "O preço que um autônomo da sua área cobra hoje. Ela sobe com o IPCA, a inflação oficial, todo mês.",
  example: "Ex.: referência de R$ 150,00 e IPCA de 0,5% no mês: no mês seguinte ela é R$ 150,75.",
  reading:
    "Preço acima da referência rende mais por cliente e perde clientes; abaixo, ganha clientes e a inflação corrói a renda.",
  format: (value) => displayMoney(value),
};

export const SERVICE_PRICE: MetricInfo = {
  label: "Seu preço",
  description: "Quanto você cobra por atendimento",
  definition:
    "O valor de cada atendimento. A renda do mês é o preço vezes os clientes, e os clientes dependem de o preço estar acima ou abaixo da referência do mercado.",
  example: "Ex.: R$ 180,00 por atendimento e 32 clientes no mês: a renda do mês é R$ 5.760,00.",
  reading:
    "Você muda o preço uma vez por mês. Preço parado perde para a inflação; preço muito acima da referência afasta clientes e aumenta a chance de um mês sem nenhum.",
  format: (value) => displayMoney(value),
};

export const COMPANY_CAPITAL: MetricInfo = {
  label: "Capital da empresa",
  description: "A parte do lucro que ficou dentro do negócio",
  definition:
    "O dinheiro que você reinvestiu na empresa. Ele não fica no caixa: conta no patrimônio como patrimônio travado, rende (ou encolhe) com o PIB e só vira caixa vendendo uma parte, com desconto de 20%.",
  example: "Ex.: R$ 38.000 de capital; vender 25% tira R$ 9.500 da empresa e põe R$ 7.600 no caixa.",
  reading:
    "Com PIB positivo o capital rende e o rendimento cai no caixa; com PIB negativo ele encolhe. Vender cedo custa 20% do que sai.",
  format: (value) => displayMoney(value),
};

export const CAPITAL_INCOME: MetricInfo = {
  label: "Renda do capital",
  description: "O que o capital rende no mês, pelo PIB",
  definition:
    "A taxa ao mês do capital segue o PIB dos últimos 12 meses: com PIB positivo, 0,9% ao mês para cada 1,4% de PIB; com PIB negativo, -1,4% ao mês para cada -1,2% de PIB. Com PIB zero, nada. A renda positiva cai no caixa; a negativa sai do capital.",
  example:
    "Ex.: R$ 38.000 de capital e PIB em 1,4%: rende 0,9% ao mês, +R$ 342,00 no caixa. Com PIB em -1,2%, rende -1,4%: o capital perde R$ 532,00.",
  reading: "Acima de zero o capital trabalha a seu favor; abaixo, cada real reinvestido encolhe até o PIB voltar.",
  format: (value) => displayMoney(value),
};

export const REINVEST_SHARE: MetricInfo = {
  label: "Quanto do lucro volta para a empresa",
  description: "A fração do lucro do mês que vira capital",
  definition:
    "No pagamento do mês, esta fração do lucro vai para o capital da empresa e o resto cai no caixa. Vale a partir do próximo pagamento e você muda quando quiser.",
  example: "Ex.: lucro de R$ 7.200 e 30% reinvestidos: R$ 2.160 viram capital e R$ 5.040 caem no caixa.",
  reading:
    "Com o PIB acima de 2% o capital costuma render mais do que o caixa parado; com o PIB negativo, reinvestir encolhe o dinheiro.",
  format: (value) => displayPercent(value, 0),
};

export const CAPITAL_SALE: MetricInfo = {
  label: "Vender parte da empresa",
  description: "Quanto do capital vira caixa, com desconto",
  definition:
    "A parte vendida sai do capital da empresa e entra no caixa com o desconto de 20% na venda. Você pode vender 10%, 25%, 50% ou 100% do capital quando quiser.",
  example: "Ex.: 25% de R$ 38.000 é R$ 9.500; com o desconto de 20%, R$ 7.600 entram no caixa.",
  reading: "Vender protege o capital numa recessão, mas o desconto de 20% é perda certa.",
  format: (value) => displayMoney(value),
};

export const PENSION_BALANCE: MetricInfo = {
  label: "Saldo da previdência",
  description: "Dinheiro travado que rende o CDI menos 1% ao ano",
  definition:
    "O saldo entra com 24 vezes a sua renda do mês e rende, todo mês, o CDI menos 1% ao ano (a taxa de administração do plano), sem IR no caminho. Conta no patrimônio, mas só chega ao caixa pelo resgate.",
  example:
    "Ex.: renda de R$ 5.000 por mês → saldo inicial de R$ 120.000. Com o CDI a 13,66%, o plano rende 12,66% ao ano, cerca de R$ 1.200 no primeiro mês.",
  reading:
    "O IR só aparece no resgate, e esperar mais tempo no plano baixa a alíquota. Converter em renda tira o valor do saldo para sempre.",
  format: (value) => displayMoney(value),
};

export const CONVERTED_INCOME: MetricInfo = {
  label: "Renda já convertida",
  description: "O que as parcelas convertidas pagam por mês, para sempre",
  definition:
    "A soma das rendas que cada parcela convertida paga por mês. Cada parcela fixa o juro real do dia da conversão e nunca mais muda. Não paga IR nem recebe o reajuste dos aposentados; na sala com correção, sobe todo mês pelo IPCA.",
  example: "Ex.: R$ 20.000 convertidos a 8,1% de juro real pagam R$ 130,81 por mês.",
  reading:
    "Quanto maior o juro real no dia de converter, mais renda cada real convertido paga. A conversão não volta: o valor sai do saldo.",
  format: (value) => displayMoney(value),
};

export const REAL_RATE: MetricInfo = {
  label: "Juro real",
  description: "Quanto a SELIC rende acima da inflação esperada",
  definition:
    "O juro que sobra depois de descontar a inflação: (1 + SELIC) ÷ (1 + IPCA esperado) − 1. O IPCA esperado é a última previsão do mercado (Focus) com até 30 dias; sem ela vale o IPCA dos últimos 12 meses.",
  example: "Ex.: SELIC a 13,76% e IPCA esperado de 5,2% → 1,1376 ÷ 1,052 − 1 = 8,1% ao ano de juro real.",
  reading:
    "Quanto maior, mais renda por mês cada real convertido paga. Com o juro real zerado ou negativo não dá para converter.",
  format: (value) => displayPercent(value, 2),
};

export const REDEEM_TAX: MetricInfo = {
  label: "IR regressivo",
  description: "O IR do resgate cai com o tempo no plano",
  definition:
    "O resgate paga IR sobre o valor inteiro, e a alíquota depende de há quanto tempo o saldo está no plano: quanto mais tempo, menor ela é. Converter em renda não paga IR.",
  example:
    "Ex.: resgatar R$ 20.000 com 3 anos e 4 meses no plano, na faixa de 30%: R$ 6.000 ficam com a Receita e R$ 14.000 caem no caixa.",
  reading: "Se a próxima faixa está perto, esperar deixa mais dinheiro no caixa; na faixa de 10% não há o que esperar.",
  format: (value) => displayPercent(value, 0),
};

export const WELFARE_SAVINGS: MetricInfo = {
  label: "Pé-de-Meia",
  description: "Poupança do governo, travada, que libera a cada 2 anos",
  definition:
    "Todo mês em que o seu caixa e a sua renda fixa (com o Tesouro, sem as ações) terminam maiores do que começaram, o governo deposita aqui uma parte dessa sobra. O dinheiro é do governo e não sai do seu caixa. Conta no patrimônio, mas só cai no caixa a cada 2 anos de partida, se o caixa não ficou negativo em nenhum dia do período, ou de uma vez se você virar CLT.",
  example:
    "Ex.: saldo de R$ 1.840 e a data de liberação chega com o caixa sempre acima de zero → os R$ 1.840 caem no caixa. Se o caixa ficou negativo num dia só, a liberação pula para daqui a 2 anos.",
  reading:
    "Mantenha o caixa acima de zero: um dia negativo adia a liberação em 2 anos. Quanto mais o caixa e a renda fixa crescem no mês, maior o depósito, até o teto.",
  format: (value) => displayMoney(value),
};

export const WELFARE_DEPOSIT: MetricInfo = {
  label: "Depósito deste mês",
  description: "O que o governo deposita no Pé-de-Meia pela sobra do mês",
  definition:
    "A sobra é quanto o caixa e a renda fixa cresceram desde o início do mês, sem contar as ações. O governo deposita 20% dela, multiplicado pelo fator do gasto do governo com auxílio (de 0,5× a 2×), até o teto de 10% da sua renda líquida, que o mesmo fator também multiplica. Sobra zero ou negativa não deposita nada.",
  example:
    "Ex.: sobra de R$ 600, renda líquida de R$ 1.400 e fator 1,0× → 20% de R$ 600 são R$ 120, abaixo do teto de R$ 140: deposita R$ 120. Com sobra de R$ 900, 20% dão R$ 180 e o depósito para no teto de R$ 140.",
  reading:
    "Comprar ou vender ações não muda a sobra. Quanto maior a sobra, maior o depósito, até o teto; com o governo gastando mais com auxílio, o fator sobe e o depósito cresce.",
  format: (value) => displayMoney(value),
};

export const SOCIAL_TARIFF: MetricInfo = {
  label: "Tarifa social",
  description: "Desconto na despesa mensal de quem vive do Auxílio",
  definition:
    "A despesa que você paga todo mês sai 15% mais barata. A meta e os imprevistos continuam pela despesa cheia. O desconto acaba quando você deixa o Auxílio.",
  example: "Ex.: despesa de R$ 1.600 → você paga R$ 1.360, R$ 240 a menos por mês.",
  reading:
    "É dinheiro que sobra no caixa todo mês e alimenta o depósito do Pé-de-Meia. Virar CLT pelo curso técnico faz a despesa voltar ao valor cheio.",
  format: (value) => displayMoney(value),
};

export const TECHNICAL_COURSE: MetricInfo = {
  label: "Curso técnico",
  description: "A saída do Auxílio para um emprego com carteira",
  definition:
    "A matrícula dura 12 meses. Nesse tempo a renda do bico cai pela metade e o benefício fica inteiro; o Pé-de-Meia e a tarifa social continuam. Ao concluir você vira CLT, perde a tarifa social e o benefício, e o saldo do Pé-de-Meia cai no caixa.",
  example:
    "Ex.: bico de R$ 1.400 → R$ 700 durante o curso. Concluído, vira CLT com o salário de R$ 2.300, FGTS e hora extra.",
  reading:
    "Vale a pena quando o salário de CLT supera o bico mais o benefício, e a partida é longa o bastante para colher isso depois do curso.",
  format: (value) => displayMoney(value),
};
