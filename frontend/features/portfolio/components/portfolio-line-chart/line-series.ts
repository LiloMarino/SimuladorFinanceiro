export const PORTFOLIO_LINE_SERIES = [
  {
    key: "total_networth",
    label: "Patrimônio Total",
    color: "#2563eb",
    gradientId: "colorNetworth",
    defaultVisible: true,
  },
  {
    key: "total_equity",
    label: "Renda Variável",
    color: "#10B981",
    gradientId: "colorEquity",
    defaultVisible: false,
  },
  {
    key: "total_fixed",
    label: "Renda Fixa",
    color: "#F59E0B",
    gradientId: "colorFixed",
    defaultVisible: false,
  },
  {
    key: "total_cash",
    label: "Caixa",
    color: "#6B7280",
    gradientId: "colorCash",
    defaultVisible: false,
  },
] as const;

export type PortfolioSeriesKey = (typeof PORTFOLIO_LINE_SERIES)[number]["key"];
