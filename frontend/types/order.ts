export type OrderOperation = "buy" | "sell";
export type OrderType = "market" | "limit";
export type OrderStatus = "pending" | "partial" | "filled";

export type PendingOrder = {
  id: string;
  created_at: string;
  operation: "buy" | "sell";
  type: "market" | "limit";
  quantity: number;
  limit_price?: number;
  status: OrderStatus;
  user_name: string;
};
