import type { FixedIncomeAssetApi } from "./fixed-income";
import type { FixedIncomePosition, Position } from "./portfolio";
import type { Snapshot } from "./snapshot";
import type { Stock } from "./stock";
import type { PatrimonialHistory } from "./portfolio";
import type { Order, OrderExecutedEvent, OrderPartialExecutedEvent } from "./order";

/** Eventos emitidos pelo servidor via WebSocket ou SSE */
export type SimulationEvents = {
  simulation_update: { currentDate: string };
  speed_update: { speed: number };
  cash_update: { cash: number };
  stocks_update: { stocks: Stock[] };
  fixed_assets_update: { assets: FixedIncomeAssetApi[] };
  snapshot_update: { snapshot: Snapshot };
  fixed_income_position_update: { positions: FixedIncomePosition[] };
  statistics_snapshot_update: {
    snapshots: {
      player_nickname: string;
      snapshot: PatrimonialHistory;
    }[];
  };
  order_executed: OrderExecutedEvent;
  order_partial_executed: OrderPartialExecutedEvent;
} & {
  [K in `stock_update:${string}`]: { stock: Stock };
} & {
  [K in `position_update:${string}`]: { position: Position };
} & {
  [K in `order_added:${string}`]: {
    order: Order;
  };
} & {
  [K in `order_updated:${string}`]: {
    order: Order;
  };
};

export type SimulationState = {
  currentDate?: string;
  speed?: number;
  cash?: number;
};
