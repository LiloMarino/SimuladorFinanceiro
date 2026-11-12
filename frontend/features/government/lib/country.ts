/** Como a faixa "O país" colore o crescimento do PIB em 12 meses. */
export type GrowthTone = "good" | "weak" | "recession";

/** A partir de 2% a economia vai bem; de 0% a 2% está fraca; abaixo de 0% é recessão. */
export function growthTone(growth: number): GrowthTone {
  if (growth < 0) return "recession";
  return growth >= 0.02 ? "good" : "weak";
}
