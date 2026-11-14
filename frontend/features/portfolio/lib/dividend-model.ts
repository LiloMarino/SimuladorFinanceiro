import { displayMonthShort, parseLocalDate } from "@/shared/lib/utils/display";
import type { AssetClass, DividendBucket } from "@/types";

export type DividendPeriod = "month" | "year";

/** Uma cor por classe, do âmbar cheio das ações ao claro dos FIIs; a classe nova sem cor não compila. */
export const DIVIDEND_CLASS_COLORS: Record<AssetClass, string> = {
  STOCK: "bg-dividend-bar",
  FII: "bg-dividend-bar-soft",
  ETF: "bg-dividend-bar-etf",
  BDR: "bg-dividend-bar-bdr",
  CRYPTO: "bg-dividend-bar",
  FUND: "bg-dividend-bar-soft",
};

const STEPS = [1, 2, 2.5, 5, 10];
const MAX_TICKS = 5;

/** Teto e marcas do eixo: o menor passo "redondo" que cobre o maior valor em até cinco faixas. */
export function dividendScale(max: number): { ceiling: number; ticks: number[] } {
  if (max <= 0) return { ceiling: 100, ticks: [0, 100] };
  const magnitude = 10 ** Math.floor(Math.log10(max / MAX_TICKS));
  const step = (STEPS.find((s) => s * magnitude * MAX_TICKS >= max) ?? 10) * magnitude;
  const count = Math.ceil(max / step);
  return { ceiling: count * step, ticks: Array.from({ length: count + 1 }, (_, i) => i * step) };
}

/** O rótulo da coluna: o mês curto na visão mensal e o ano na anual. */
export function bucketLabel(bucket: DividendBucket, period: DividendPeriod) {
  return period === "month" ? displayMonthShort(bucket.period) : String(parseLocalDate(bucket.period).getFullYear());
}

/** O título do tooltip: "dez 2018" no mês e "2018" no ano. */
export function bucketTitle(bucket: DividendBucket, period: DividendPeriod) {
  const year = parseLocalDate(bucket.period).getFullYear();
  return period === "month" ? `${displayMonthShort(bucket.period)} ${year}` : String(year);
}

/** A frase dos ativos que pagaram no período: "TAEE11 e PETR4 pagaram no mesmo mês." */
export function payersSentence(bucket: DividendBucket, period: DividendPeriod) {
  const tickers = bucket.payers.map((p) => p.ticker);
  if (tickers.length === 0) return "Nada caiu no caixa neste período.";
  const where = period === "month" ? "no mesmo mês" : "no mesmo ano";
  if (tickers.length === 1) return `${tickers[0]} pagou ${where}.`;
  const shown = tickers.slice(0, 3);
  const rest = tickers.length - shown.length;
  const head = shown.slice(0, -1).join(", ");
  const tail = rest > 0 ? `${shown.at(-1)} e mais ${rest}` : `e ${shown.at(-1)}`;
  return rest > 0 ? `${head}, ${tail} pagaram ${where}.` : `${head} ${tail} pagaram ${where}.`;
}
