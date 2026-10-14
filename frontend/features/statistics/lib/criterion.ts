import { displayMoney, displayNumber } from "@/shared/lib/utils/display";
import type { VictoryCriterion } from "@/types";

/** A distância do líder na unidade do critério: pontos, p.p. de retorno, reais ou Sharpe. */
export function displayCriterionGap(criterion: VictoryCriterion, gap: string | null | undefined) {
  if (gap === null || gap === undefined) return "—";
  if (Number(gap) === 0) return "líder";
  switch (criterion) {
    case "SCORE":
      return `${displayNumber(gap, 0)} pts`;
    case "RETURN":
      return `${displayNumber(Number(gap) * 100, 2)} p.p.`;
    case "NETWORTH":
      return displayMoney(gap);
    case "SHARPE":
      return displayNumber(gap, 2);
  }
}
