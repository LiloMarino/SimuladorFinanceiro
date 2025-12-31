import type { PatrimonialHistory } from "./portfolio";

export type PerformanceMetric = "total_networth" | "total_equity" | "total_fixed" | "total_cash";

export type PlayerHistory = {
  player_id: string;
  player_nickname: string;
  starting_cash: number;
  history: PatrimonialHistory[];
  last_snapshot: PatrimonialHistory;
};
