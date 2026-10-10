import type { components } from "@/types/openapi";

// Stock
export type Stock = Omit<components["schemas"]["CandleDTO"], "id">;
export type StockCandle = components["schemas"]["StockPriceHistoryDTO"];
export type StockDetails = Omit<components["schemas"]["StockDetailsDTO"], "id">;

// Portfolio
export type Position = components["schemas"]["PositionDTO"];
export type PatrimonialHistory = components["schemas"]["PatrimonialHistoryDTO"];
export type FixedIncomePosition = components["schemas"]["FixedIncomePositionDTO"];
export type PortfolioState = components["schemas"]["PortfolioDTO"];
export type CashResponse = components["schemas"]["CashResponse"];
export type PortfolioPosition = PortfolioState["variable_income"][number];

// Fixed Income
export type RateIndex = components["schemas"]["RateIndexType"];
export type InvestmentType = components["schemas"]["FixedIncomeType"];
export type FixedIncomeAssetApi = components["schemas"]["FixedIncomeAssetDTO"];
export type FixedIncomeProjection = components["schemas"]["FixedIncomeProjectionDTO"];

// Economic
export type EconomicIndicators = components["schemas"]["EconomicIndicatorsDTO"];
export type IndicatorSeries = components["schemas"]["IndicatorSeries"];

// Data center
export type SeriesCoverage = components["schemas"]["SeriesCoverageDTO"];
export type AssetClass = components["schemas"]["AssetClass"];

// User
export type User = components["schemas"]["UserDTO"];
export type Session = components["schemas"]["SessionDTO"];

// Statistics
export type PerformanceMetric = "total_networth" | "total_equity" | "total_fixed" | "total_cash" | "total_contribution";
export type PerformanceReport = components["schemas"]["PerformanceReportDTO"];
export type PlayerPerformance = PerformanceReport["players"][number];

// Orders
export type OrderAction = components["schemas"]["OrderAction"];
export type OrderType = components["schemas"]["OrderType"];
export type OrderStatus = components["schemas"]["OrderStatus"];
export type Order = components["schemas"]["OrderDTO"];

// Notifications
export type NotificationPreferences = {
  orders: components["schemas"]["OrderNotificationSettings"];
};

// Simulation
export type SimulationState = Partial<components["schemas"]["SimulationStateResponse"]>;
export type SimulationData = components["schemas"]["SimulationDTO"];
export type SimulationSettingsData = components["schemas"]["SimulationSettingsDTO"];
export type SimulationSettings = components["schemas"]["SimulationSettingsResponse"];
export type SimulationInfo = components["schemas"]["SimulationStatusResponse"];
export type SimulationListItem = components["schemas"]["SimulationSummaryDTO"];
