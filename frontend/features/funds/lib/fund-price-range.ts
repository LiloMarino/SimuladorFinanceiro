import { parseLocalDate } from "@/shared/lib/utils/display";

/** O preço de ranking fica 30% acima ou abaixo do patrimônio por cota. */
export const RANKING_BAND_FRACTION = 0.3;

export type PriceRange = "3m" | "6m" | "since_offer";

export const RANGES: readonly { value: PriceRange; label: string; months: number | null }[] = [
  { value: "3m", label: "3 meses", months: 3 },
  { value: "6m", label: "6 meses", months: 6 },
  { value: "since_offer", label: "Desde a oferta", months: null },
];

/** O instante a partir do qual o gráfico mostra pontos, contado do último dia da série; 0 mostra tudo. */
export function rangeCutoff(range: PriceRange, lastDay: string): number {
  const months = RANGES.find((item) => item.value === range)?.months ?? null;
  if (months === null) return 0;
  const cutoff = parseLocalDate(lastDay);
  cutoff.setMonth(cutoff.getMonth() - months);
  return cutoff.getTime();
}
