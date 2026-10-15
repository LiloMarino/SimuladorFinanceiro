import { displayMoney, displayNumber, displaySignedPercent } from "@/shared/lib/utils/display";
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

/** O valor do jogador no critério: "342 pts", "+12,81%", "R$ 121.840,10" ou "Sharpe 0,07". */
export function displayCriterionValue(criterion: VictoryCriterion, value: string | null | undefined) {
  const missing = value === null || value === undefined;
  switch (criterion) {
    case "SCORE":
      return missing ? "sem nota" : `${displayNumber(value, 0)} pts`;
    case "RETURN":
      return missing ? "—" : displaySignedPercent(value);
    case "NETWORTH":
      return missing ? "—" : displayMoney(value);
    case "SHARPE":
      return `Sharpe ${missing ? "—" : displayNumber(value, 2)}`;
  }
}
