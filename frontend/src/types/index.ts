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
  change_pct: string;
  history: StockCandle[];
};

export type SimulationState = {
  currentDate?: string;
  speed?: number;
  cash?: number;
};

export type Position = {
  ticker: string;
  size: number;
  avg_price: number;
};

export type PortfolioState = {
  cash: number;
  variable_income: Position[];
  fixed_income: unknown[];
  patrimonial_history: unknown[];
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

export interface FixedIncomeAsset {
  name: string;
  issuer: string;
  interestRate: number;
  rateIndex: "CDI" | "IPCA" | "SELIC" | "PREFIXADO";
  investmentType: "CDB" | "LCI" | "LCA" | "TESOURO";
  maturityDate: string; // ISO
  daysToMaturity: number;
  incomeTax: string | null;
}
