export const PORTFOLIO_AREA_SERIES = [
  {
    key: "total_networth",
    label: "Patrimônio Total",
    color: "var(--color-chart-1)",
    gradientId: "colorNetworth",
    defaultVisible: true,
  },
  {
    key: "total_equity",
    label: "Renda Variável",
    color: "var(--color-chart-2)",
    gradientId: "colorEquity",
    defaultVisible: false,
  },
  {
    key: "total_fixed",
    label: "Renda Fixa",
    color: "var(--color-chart-3)",
    gradientId: "colorFixed",
    defaultVisible: false,
  },
  {
    key: "total_cash",
    label: "Caixa",
    color: "var(--color-chart-4)",
    gradientId: "colorCash",
    defaultVisible: false,
  },
  {
    key: "total_contribution",
    label: "Total Aportado",
    color: "var(--color-chart-5)",
    gradientId: "colorContribution",
    defaultVisible: false,
  },
] as const;

export type PortfolioSeriesKey = (typeof PORTFOLIO_AREA_SERIES)[number]["key"];
