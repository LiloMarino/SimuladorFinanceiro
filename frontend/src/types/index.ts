import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";

/** Item de navegação (menu lateral, abas etc.) */
export interface NavItem {
  key: string;
  label: string;
  endpoint: string;
  icon: IconDefinition;
}

/** Dados de um ativo retornado na listagem geral */
export type Stock = {
  ticker: string;
  name: string;
  price: number;
  low: number;
  high: number;
  volume: number;
  open: number;
  date: string; // ISO
  change: number;
  change_pct: string; // "+1.23%"
};

/** Registro histórico de preço (candlestick) */
export type StockCandle = {
  date: string; // ISO
  close: number;
  open: number;
  low: number;
  high: number;
  volume: number;
};

/** Detalhamento completo de um ativo (para a página individual) */
export type StockDetails = {
  ticker: string;
  name: string;
  price: number;
  low: number;
  high: number;
  volume: number;
  change: number;
  change_pct: string; // corrigido para string
  history: StockCandle[];
};

export type Position = {
  ticker: string;
  size: number;
  avg_price: number;
};

export type SimulationState = {
  currentDate?: string;
  speed?: number;
  cash?: number;
};

/** Eventos emitidos pelo servidor via WebSocket ou SSE */
export type SimulationEvents = {
  simulation_update: { currentDate: string };
  speed_update: { speed: number };
  cash_update: { cash: number };
  stocks_update: { stocks: Stock[] };
} & {
  [K in `stock_update:${string}`]: { stock: Stock };
};
