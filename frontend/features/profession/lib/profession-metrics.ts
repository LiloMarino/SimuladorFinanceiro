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
