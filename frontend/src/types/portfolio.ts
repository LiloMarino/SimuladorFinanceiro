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
