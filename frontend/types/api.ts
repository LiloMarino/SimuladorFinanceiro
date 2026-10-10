import type { components, operations } from "@/types/openapi";

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
export type SectorAllocation = PortfolioState["sectors"][number];

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
export type Sector = components["schemas"]["SectorDTO"];

// User
export type User = components["schemas"]["UserDTO"];
export type Session = components["schemas"]["SessionDTO"];

// Statistics
export type SeriesPoint = components["schemas"]["SeriesPointDTO"];
export type OverviewReport = components["schemas"]["OverviewReportDTO"];
// Toda linha de jogador de qualquer aba traz quem é e em que simulação
export type Score = NonNullable<OverviewReport["players"][number]["score"]>;
export type ScoreAxis = Score["axes"][number]["axis"];
export type ScoreMetric = Score["axes"][number]["metrics"][number]["metric"];
export type PlayerRef = Pick<OverviewReport["players"][number], "player_nickname" | "simulation_id" | "simulation_name">;
export type ReturnsReport = components["schemas"]["ReturnsReportDTO"];
export type RiskReport = components["schemas"]["RiskReportDTO"];
export type CompositionReport = components["schemas"]["CompositionReportDTO"];
export type OperationsReport = components["schemas"]["OperationsReportDTO"];

// Correlation
export type CorrelationAssets = components["schemas"]["CorrelationAssetsDTO"];
export type CorrelationMatrix = components["schemas"]["CorrelationMatrixDTO"];
export type CorrelationCell = CorrelationMatrix["rows"][number][number];
export type CorrelationQuery = operations["get_correlation_api_correlation_get"]["parameters"]["query"];
export type CorrelationWindow = NonNullable<CorrelationQuery["window"]>;

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
export type VictoryCriterion = components["schemas"]["VictoryCriterion"];
