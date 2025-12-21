export type Position = {
  ticker: string;
  size: number;
  total_cost: number;
  avg_price: number;
};

export type PatrimonialHistory = {
  date: string; // ISO
  total_networth: number;
  total_equity: number;
  total_fixed: number;
  total_cash: number;
};

export type PortfolioState = {
  cash: number;
  variable_income: Position[];
  fixed_income: unknown[];
  patrimonial_history: PatrimonialHistory[];
};
