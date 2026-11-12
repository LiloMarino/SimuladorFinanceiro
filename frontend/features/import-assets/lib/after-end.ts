import type { SeriesCoverage } from "@/types";

/**
 * O que a partida faz depois do último dado real da série:
 * `generated` usa o futuro gerado; `repeat` repete o último valor enquanto não há futuro gerado;
 * `computed` calcula na partida a partir da SELIC, do IPCA e da bolsa; `none` não estende a série.
 */
export type AfterEnd = "generated" | "repeat" | "computed" | "none";

export function afterEnd(series: SeriesCoverage): AfterEnd {
  if (series.kind === "EXPECTATION") return "none";
  if (!series.has_generated_future) return "computed";
  return series.generated_end ? "generated" : "repeat";
}
