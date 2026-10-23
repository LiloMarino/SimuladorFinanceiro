import type { StrategySignal } from "@/types";

/** Cor do traço de cada estilo de linha na legenda do gráfico. */
export const LEGEND_SWATCH: Record<StrategySignal["lines"][number]["style"], string> = {
  price: "bg-faint-foreground",
  fast: "bg-chart-1",
  slow: "bg-chart-5",
  channel: "bg-chart-3",
  oscillator: "bg-chart-1",
};
