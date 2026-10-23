import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";

export const WITHDRAWAL_RATE: MetricInfo = {
  label: "Taxa de retirada",
  description: "Quanto do patrimônio dá para gastar por ano sem acabar com ele",
  definition:
    "A parte do patrimônio retirada a cada ano para pagar a despesa. A meta é a despesa do ano dividida por essa taxa.",
  example:
    "Ex.: despesa de R$ 5.000 por mês (R$ 60.000 por ano) e taxa de 4% → meta de R$ 1.500.000, que é 25× a despesa anual.",
  reading:
    "Taxa menor deixa a meta maior e mais segura; 4% é a referência clássica (regra dos 4%). Taxas mais altas pedem menos patrimônio, mas o dinheiro tende a acabar antes.",
  format: (value) => displayPercent(value, 1),
};

export const INDEPENDENCE_GOAL: MetricInfo = {
  label: "Meta de independência",
  description: "O patrimônio que paga a sua despesa só com a retirada anual",
  definition: "12 × a despesa mensal ÷ a taxa de retirada. Com 4%, é 25 vezes a despesa de um ano.",
  example: "Ex.: despesa de R$ 5.000 por mês → R$ 60.000 por ano ÷ 4% = R$ 1.500.000.",
  reading:
    "Ao chegar nela, retirar a taxa por ano cobre a despesa sem precisar do salário. Com correção pelo IPCA, a meta sobe junto com a despesa.",
  format: (value) => displayMoney(value),
};

export const RESERVE_MONTHS: MetricInfo = {
  label: "Reserva de emergência",
  description: "Quantos meses de despesa o caixa e a liquidez diária pagam sem você vender nada",
  definition:
    "Quantos meses de despesa você cobre com o que sai no mesmo dia: o caixa e os títulos de renda fixa com liquidez diária. Ações e títulos que só pagam no vencimento ficam de fora.",
  example: "Ex.: despesa de R$ 7.000 e R$ 39.317 entre caixa e liquidez diária dão 5,6 meses.",
  reading:
    "Abaixo de 3 meses é frágil: um imprevisto joga o caixa no cheque especial. De 3 a 6 meses pede atenção; 6 ou mais é boa.",
  format: (value) => `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(Number(value))} meses`,
};

export const OVERDRAFT: MetricInfo = {
  label: "Cheque especial",
  description: "O empréstimo automático de quando o caixa fica negativo",
  definition:
    "Com o caixa abaixo de zero, o banco cobre a diferença e cobra juros a cada pregão sobre o valor negativo, até você cobrir vendendo ou resgatando algo.",
  example: "Ex.: caixa em −R$ 2.340 a 8% ao mês paga uns R$ 8,60 de juros por pregão (cerca de R$ 187 no mês).",
  reading: "É um juro alto: quanto mais tempo no negativo, mais caro. O ideal é voltar a zero o quanto antes.",
  format: (value) => displayMoney(value),
};

export const GOAL_ETA: MetricInfo = {
  label: "Previsão para a meta",
  description: "Quando o patrimônio chega à meta se o ritmo dos últimos 12 meses continuar",
  definition:
    "Pega quanto o patrimônio cresceu nos últimos 12 meses, divide por 12 para ter o ganho por mês e vê em quantos meses esse ganho cobre o que falta.",
  example:
    "Ex.: o patrimônio foi de R$ 700.000 para R$ 940.000 em 12 meses (R$ 20.000 por mês). Se faltam R$ 560.000, são 28 meses.",
  reading:
    "É uma conta em linha reta: mercado, imprevistos e a meta subindo com o IPCA mudam o resultado. Serve de bússola, não de promessa.",
  format: (value) => String(value),
};
