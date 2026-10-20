import { displayGoalPercent } from "@/shared/lib/goal";
import { displayMoney, displayMoneyCompact, displayNumber, displaySignedPercent } from "@/shared/lib/utils/display";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import type { OverviewReport, VictoryCriterion } from "@/types";

/**
 * O que ordena o ranking: o critério escolhido na Clássica; fora dela, a fração da meta
 * (patrimônio ÷ meta, 1 = chegou) e as distâncias são diferenças de fração.
 */
export type RankingMeasure = VictoryCriterion | "GOAL";

export function rankingMeasure(report: Pick<OverviewReport, "game_type" | "criterion">): RankingMeasure {
  return report.game_type === "CLASSIC" ? report.criterion : "GOAL";
}

/** O nome do que decide a partida: o critério, ou "Primeiro a chegar à meta (R$ 1,5 mi)". */
export function criterionLabel(report: Pick<OverviewReport, "game_type" | "criterion" | "goal_net_worth">) {
  if (report.game_type === "CLASSIC") return VICTORY_CRITERIA[report.criterion].label;
  const target = report.game_type === "FINANCIAL_INDEPENDENCE" ? "independência financeira" : "meta";
  return `Primeiro a chegar à ${target}${report.goal_net_worth ? ` (${displayMoneyCompact(report.goal_net_worth)})` : ""}`;
}

/**
 * A distância do líder na unidade do critério: pontos, p.p. de retorno, reais ou Sharpe.
 * Na meta é a diferença de frações vezes a meta, em reais; sem meta única (comparando
 * partidas de metas diferentes) fica em pontos percentuais da meta.
 */
export function displayCriterionGap(
  criterion: RankingMeasure,
  gap: string | null | undefined,
  goal?: string | null,
) {
  if (gap === null || gap === undefined) return "—";
  if (Number(gap) === 0) return "líder";
  switch (criterion) {
    case "GOAL":
      return goal ? displayMoney(Number(gap) * Number(goal)) : `${displayNumber(Number(gap) * 100, 2)} p.p. da meta`;
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
export function displayCriterionValue(criterion: RankingMeasure, value: string | null | undefined) {
  const missing = value === null || value === undefined;
  switch (criterion) {
    case "GOAL":
      return missing ? "—" : displayGoalPercent(Number(value));
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

/** Quanto o jogador passa (+) ou fica abaixo (−) da média da equipe, na unidade do critério. */
export function displayCriterionContribution(criterion: RankingMeasure, value: string | null | undefined) {
  if (value === null || value === undefined) return "—";
  const amount = Number(value);
  const sign = amount > 0 ? "+" : amount < 0 ? "−" : "";
  const size = Math.abs(amount);
  switch (criterion) {
    case "GOAL":
      return `${sign}${displayNumber(size * 100, 2)} p.p.`;
    case "SCORE":
      return `${sign}${displayNumber(size, 0)}`;
    case "RETURN":
      return `${sign}${displayNumber(size * 100, 2)} p.p.`;
    case "NETWORTH":
      return `${sign}${displayMoney(size)}`;
    case "SHARPE":
      return `${sign}${displayNumber(size, 2)}`;
  }
}

/** Quanto falta de patrimônio para a meta, a partir da fração dela; zero quando já chegou. */
export function displayRemainingToGoal(fraction: string | null | undefined, goal: string | null | undefined) {
  if (fraction === null || fraction === undefined || !goal) return "—";
  return displayMoney(Math.max(0, 1 - Number(fraction)) * Number(goal));
}
