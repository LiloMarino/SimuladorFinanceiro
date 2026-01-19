import type { FixedIncomeAssetApi } from "./fixed-income";

export type Position = {
  ticker: string;
  size: number;
  total_cost: number;
  avg_price: number;
};

export type PatrimonialHistory = {
  snapshot_date: string; // ISO
  total_networth: number;
  total_equity: number;
  total_fixed: number;
  total_cash: number;
  total_contribution: number;
};

export type FixedIncomePosition = {
  asset: FixedIncomeAssetApi;
  total_applied: number;
  current_value: number;
};

export type PortfolioState = {
  starting_cash: number;
  total_contribution: number;
  cash: number;
  variable_income: Position[];
  fixed_income: FixedIncomePosition[];
  patrimonial_history: PatrimonialHistory[];
};
