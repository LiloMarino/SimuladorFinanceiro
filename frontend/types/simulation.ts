import type { FixedIncomeAssetApi } from "./fixed-income";
import type { FixedIncomePosition, Position } from "./portfolio";
import type { Snapshot } from "./snapshot";
import type { Stock } from "./stock";
import type { PatrimonialHistory } from "./portfolio";
import type { Order, OrderExecutedEvent, OrderPartialExecutedEvent } from "./order";

/** Eventos emitidos pelo servidor via WebSocket ou SSE */
export type SimulationEvents = {
  simulation_started: SimulationInfo;
  simulation_ended: {
    reason: "completed" | "stopped_by_host";
  };
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
  order_rejected: { reason: string };
  player_join: {
    nickname: string;
  };
  player_exit: {
    nickname: string;
  };
  simulation_settings_update: SimulationData;
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
} & {
  [K in `order_book_snapshot:${string}`]: {
    orders: Order[];
  };
};

export type SimulationState = {
  currentDate?: string;
  speed?: number;
  cash?: number;
};

export type SimulationData = {
  start_date: string;
  end_date: string;
  starting_cash: number;
};

export type SimulationSettings = {
  is_host: boolean;
  simulation: SimulationData;
};

export type SimulationInfo = {
  active: boolean;
  simulation?: SimulationData;
};
