import type {
  FixedIncomeAssetApi,
  FixedIncomePosition,
  Order,
  OrderAction,
  PatrimonialHistory,
  Position,
  SimulationData,
  SimulationInfo,
  Stock,
} from "./api";

/** Snapshot de patrimônio emitido via WebSocket/SSE */
export type Snapshot = {
  user_id: number;
  snapshot_date: string; // ISO
  total_equity: number;
  total_fixed: number;
  total_cash: number;
  total_contribution: number;
  total_networth: number;
  created_at: string; // ISO
};

export type OrderExecutedEvent = {
  order_id: string;
  ticker: string;
  action: OrderAction;
  price: number;
  quantity: number;
};

export type OrderPartialExecutedEvent = {
  order_id: string;
  ticker: string;
  action: OrderAction;
  price: number;
  quantity: number;
  remaining: number;
};

/** Eventos emitidos pelo servidor via WebSocket ou SSE */
export type SimulationEvents = {
  simulation_started: SimulationInfo;
  simulation_ended: {
    reason: "completed" | "stopped_by_host";
  };
  simulation_update: { current_date: string };
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
