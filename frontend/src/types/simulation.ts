import type { FixedIncomeAssetApi } from "./fixed-income";
import type { Stock } from "./stock";

/** Eventos emitidos pelo servidor via WebSocket ou SSE */
export type SimulationEvents = {
  simulation_update: { currentDate: string };
  speed_update: { speed: number };
  cash_update: { cash: number };
  stocks_update: { stocks: Stock[] };
  fixed_assets_update: { assets: FixedIncomeAssetApi[] };
} & {
  [K in `stock_update:${string}`]: { stock: Stock };
};

export type SimulationState = {
  currentDate?: string;
  speed?: number;
  cash?: number;
};
