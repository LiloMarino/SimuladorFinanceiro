import type { PatrimonialHistory } from "./portfolio";

export type PerformanceMetric = "total_networth" | "total_equity" | "total_fixed" | "total_cash";

export type PlayerHistory = {
  playerId: string;
  playerName: string;
  history: PatrimonialHistory[];
};
