import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";

export const DIVIDEND_YIELD: MetricInfo = {
  label: "DY 12m",
  description: "Quanto o ativo pagou de provento em um ano, sobre o preço de hoje",
  definition:
    "Dividend yield: o que o ativo pagou por ação nos últimos 12 meses, dividido pelo preço de hoje. Mostra quanto de renda cada real que você colocaria hoje no ativo teria rendido só em proventos.",
  example: "Ex.: PETR4 pagou R$ 1,40 por ação e hoje custa R$ 29,85: 1,40 ÷ 29,85 = 4,7% ao ano.",
  reading:
    "Compare com o CDI: acima dele, só os proventos já rendem mais que a renda fixa. Fundos imobiliários costumam ficar entre 8% e 12%, ações de empresas que pagam bem entre 4% e 8%. Ativo que não pagou nada mostra 0,0%; cripto não paga provento.",
  format: (value) => displayPercent(value),
};

export const YIELD_ON_COST: MetricInfo = {
  label: "YoC",
  description: "O provento de 12 meses sobre o que você pagou pelo ativo",
  definition:
    "Yield on cost: o mesmo provento por ação dos últimos 12 meses, mas dividido pelo seu preço médio de compra, não pelo preço de hoje. Mostra o rendimento sobre o dinheiro que você de fato colocou.",
  example:
    "Ex.: você pagou R$ 24,10 em média por PETR4 e o ativo pagou R$ 1,40 por ação em 12 meses: 1,40 ÷ 24,10 = 5,8%. O DY, sobre os R$ 29,85 de hoje, é 4,7%.",
  reading:
    "Fica acima do DY quando você comprou mais barato que o preço de hoje, e abaixo quando comprou mais caro. Quanto maior, mais o ativo rende sobre o seu custo.",
  format: (value) => displayPercent(value),
};

export const RECEIVED_DIVIDENDS: MetricInfo = {
  label: "Proventos recebidos",
  description: "Tudo o que os ativos pagaram e caiu no seu caixa",
  definition:
    "A soma dos proventos (dividendos, rendimentos e JCP) que caíram no seu caixa na data ex, pela quantidade que você tinha na abertura do dia. O primeiro valor é o da partida inteira; o segundo, só os últimos 12 meses.",
  example: "Ex.: R$ 2.340,10 na partida, dos quais R$ 1.698,30 nos últimos 12 meses.",
  reading:
    "É dinheiro que entrou sem você vender nada, e todo ele é isento de IR. Ele fica no caixa: só rende de novo se você reinvestir.",
  format: (value) => displayMoney(value),
};

export const DIVIDENDS_PER_MONTH: MetricInfo = {
  label: "Média por mês",
  description: "O que os proventos de 12 meses dão por mês, contando os meses sem pagamento",
  definition: "O total recebido nos últimos 12 meses dividido por 12, inclusive os meses em que nada caiu no caixa.",
  example: "Ex.: R$ 1.698,30 em 12 meses dão R$ 141,53 por mês.",
  reading:
    "Serve para comparar a renda dos proventos com o gasto mensal da sua vida na partida: quanto mais perto, mais a carteira se paga sozinha.",
  format: (value) => displayMoney(value),
};

export const TOP_PAYERS: MetricInfo = {
  label: "Quem mais pagou em 12 meses",
  description: "A parte de cada ativo no total de proventos",
  definition:
    "Cada ativo com o quanto trouxe de proventos nos últimos 12 meses e a fatia que isso é do total recebido.",
  example: "Ex.: TAEE11 trouxe R$ 540 de R$ 1.698,30 recebidos: 32% de tudo o que entrou.",
  reading:
    "Fatia muito grande num ativo só quer dizer que sua renda depende dele: se cortar o pagamento, o total cai junto.",
  format: (value) => displayPercent(value),
};
