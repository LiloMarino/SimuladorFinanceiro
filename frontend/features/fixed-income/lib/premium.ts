import { displayPoints, displayPremiumPoints } from "@/shared/lib/budget-metrics";
import { displayMonthShort, displayRateLabel, displayShortMonthYear, parseLocalDate } from "@/shared/lib/utils/display";
import type { Budget, FixedIncomeOffer } from "@/types";

type PremiumAsset = Pick<FixedIncomeOffer, "investment_type" | "risk_premium">;

/** O prêmio de risco do governo só entra nos títulos do Tesouro. */
export const isTreasury = (asset: Pick<FixedIncomeOffer, "investment_type">) =>
  asset.investment_type === "Tesouro Direto";

/** O prêmio gravado no título, em fração da taxa (0.019 = 1,9 ponto); zero quando ele não tem. */
export const premiumOf = (asset: Pick<FixedIncomeOffer, "risk_premium">) => Number(asset.risk_premium ?? 0);

/** Os títulos do Tesouro que carregam prêmio na taxa. */
export const hasPremium = (asset: PremiumAsset) => isTreasury(asset) && premiumOf(asset) > 0;

/** "inclui 1,9 de prêmio": o prêmio em pontos, sem a unidade. */
export function premiumTagLabel(asset: Pick<FixedIncomeOffer, "risk_premium">) {
  return `inclui ${(premiumOf(asset) * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} de prêmio`;
}

/** A taxa do título sem o prêmio: "IPCA + 6,28%" com 1,9 de prêmio vira "IPCA + 4,38%". */
export function rateWithoutPremium(asset: Pick<FixedIncomeOffer, "rate_index" | "interest_rate" | "risk_premium">) {
  return displayRateLabel(asset.rate_index, String(Number(asset.interest_rate) - premiumOf(asset)));
}

/** O prêmio de hoje contra o do primeiro fechamento da partida; sem histórico, nada a comparar. */
export function premiumSinceStart(budget: Pick<Budget, "history" | "month">) {
  const first = budget.history.find((month) => month.closed);
  if (!first) return null;
  const since = displayShortMonthYear(first.month_end);
  const change = (Number(budget.month.premium) - Number(first.premium)) * 100;
  if (Math.round(Math.abs(change) * 10) === 0) return { text: `estável desde ${since}`, rising: false };
  return {
    text: `${change > 0 ? "▲" : "▼"} ${displayPoints(Math.abs(change), 1)} desde ${since}`,
    rising: change > 0,
  };
}

/** "+1,87 ponto": o prêmio de hoje com o sinal, como a faixa do topo o lê. */
export const signedPremium = (premium: string) => `+${displayPremiumPoints(premium)}`;

/** "comprado em jun 2018, com prêmio de 1,80 ponto": o prêmio que a posição travou na compra. */
export function purchasePremiumNote(firstAppliedDate: string, asset: Pick<FixedIncomeOffer, "risk_premium">) {
  const year = parseLocalDate(firstAppliedDate).getFullYear();
  return `comprado em ${displayMonthShort(firstAppliedDate)} ${year}, com prêmio de ${displayPremiumPoints(premiumOf(asset))}`;
}
