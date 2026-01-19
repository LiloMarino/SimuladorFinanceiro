import type { PatrimonialHistory } from "./portfolio";

export type PerformanceMetric = "total_networth" | "total_equity" | "total_fixed" | "total_cash" | "total_contribution";

export type PlayerHistory = {
  player_nickname: string;
  starting_cash: number;
  history: PatrimonialHistory[];
};
