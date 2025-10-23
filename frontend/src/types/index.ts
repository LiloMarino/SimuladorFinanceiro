import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";

export interface NavItem {
  key: string;
  label: string;
  endpoint: string;
  icon: IconDefinition;
}

export interface Stock {
  ticker: string;
  name: string;
  price: number;
  low: number;
  high: number;
  volume: number;
  open: number;
  date: string;
  change: number;
  change_pct: string; // ex: "+1.23%" ou "-0.45%"
}

export type SimulationEvents = {
  simulation_update: { currentDate: string };
  speed_update: { speed: number };
  stocks_update: { stocks: Stock[] };
} & {
  [K in `stock_update:${string}`]: { stock: Stock };
};
