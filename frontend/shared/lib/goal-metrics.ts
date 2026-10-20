import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoney } from "@/shared/lib/utils/display";
import { displayGoalPercent } from "./goal";

export const GOAL_PERCENT: MetricInfo = {
  label: "% da meta",
  description: "Quanto do caminho até a meta o patrimônio já andou",
  definition: "O patrimônio dividido pela meta. Como a meta é a mesma para todos, quem tem mais patrimônio está mais perto.",
  example: "Ex.: R$ 930.000 de uma meta de R$ 1.500.000 → 62%.",
  reading: "100% é chegar. Em equipes, vale a média do patrimônio dos membros dividida pela meta.",
  format: (value) => displayGoalPercent(Number(value)),
};

export const GOAL_REMAINING: MetricInfo = {
  label: "Falta para a meta",
  description: "Quanto patrimônio ainda falta para chegar",
  definition: "A meta menos o patrimônio de hoje, em reais. Zera quando a meta é atingida.",
  example: "Ex.: meta de R$ 1.500.000 e patrimônio de R$ 930.000 → faltam R$ 570.000.",
  reading: "Quanto menor, mais perto. A partida termina no dia em que alguém chega a zero.",
  format: (value) => displayMoney(value),
};
