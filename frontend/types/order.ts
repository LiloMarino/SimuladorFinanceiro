import type { components } from "@/types/openapi";

export type OrderAction = components["schemas"]["OrderAction"];

export type OrderType = components["schemas"]["OrderType"];

export type OrderStatus = components["schemas"]["OrderStatus"];

export type Order = components["schemas"]["OrderDTO"];

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
