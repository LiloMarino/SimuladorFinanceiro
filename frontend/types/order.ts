export type OrderAction = "buy" | "sell";
export type OrderType = "market" | "limit";
export type OrderStatus = "pending" | "partial" | "executed" | "canceled";

export type Order = {
  id: string;
  player_nickname: string;
  action: OrderAction;
  order_type: OrderType;
  status: OrderStatus;
  size: number;
  remaining: number;
  limit_price: number | null;
  created_at: string;
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
