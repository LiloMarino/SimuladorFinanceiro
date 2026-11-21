import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundIssuanceEstimate } from "@/types";

/** A faixa vazia: nem os bots nem o Mercado devem comprar nada da sobra. */
export const isEmptyEstimate = (estimate: FundIssuanceEstimate) =>
  Number(estimate.quotas_min) === 0 && Number(estimate.quotas_max) === 0;

/** "min a max", ou o valor só quando os dois extremos coincidem. */
function range(min: string, max: string, show: (value: string) => string) {
  return Number(min) === Number(max) ? show(min) : `${show(min)} a ${show(max)}`;
}

/** O dinheiro que a faixa leva ao caixa: "R$ 11.500,00 a R$ 13.000,00". */
export const estimateRaisedText = (estimate: FundIssuanceEstimate) =>
  range(estimate.raised_min, estimate.raised_max, displayMoney);

/** As cotas da faixa e a comissão dos banqueiros, que sai desse dinheiro. */
export function estimateNote(estimate: FundIssuanceEstimate) {
  const quotas = `${range(estimate.quotas_min, estimate.quotas_max, displayQuantity)} cotas`;
  if (Number(estimate.commission_max) === 0) return quotas;
  const commission = range(estimate.commission_min, estimate.commission_max, displayMoney);
  return `${quotas}, já com a comissão dos banqueiros (${commission}) descontada`;
}

const POINTS_FORMAT = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });

/** Quanto a cota rende acima ou abaixo do CDI, em pontos percentuais: 0,02 → "a gestora rende 2 pontos acima do CDI". */
function performanceText(performance: number) {
  const points = Math.abs(performance) * 100;
  if (Number(points.toFixed(1)) === 0) return "a gestora rende o mesmo que o CDI";
  const unit = POINTS_FORMAT.format(points) === "1" ? "ponto" : "pontos";
  const side = performance > 0 ? "acima" : "abaixo";
  return `a gestora rende ${POINTS_FORMAT.format(points)} ${unit} ${side} do CDI`;
}

/** O que a faixa vazia diz sobre o que falta: o desempenho sobre o CDI e o ágio, os dois motivos que levam o Mercado a comprar. */
export function emptyEstimateReason(estimate: FundIssuanceEstimate) {
  const attractive = estimate.performance > 0 || estimate.premium > 0;
  if (attractive) {
    return "O Mercado quer comprar, mas a sobra é pequena demais para uma cota inteira, e os bots não têm caixa ou opinião para comprar.";
  }
  const premium =
    estimate.premium > 0 ? `a cota tem ${displayPercent(estimate.premium, 1)} de ágio` : "a cota não tem ágio";
  return `Bots e Mercado só compram quando a gestora rende acima do CDI ou a cota tem ágio: ${performanceText(estimate.performance)} e ${premium}.`;
}
