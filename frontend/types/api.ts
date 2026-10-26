import type { components, operations } from "@/types/openapi";

// Stock
export type MarketQuote = components["schemas"]["MarketQuoteDTO"];
export type OrderPreview = components["schemas"]["OrderPreviewDTO"];
export type OrderPreviewRequest = components["schemas"]["OrderPreviewRequest"];
export type SubmitOrderRequest = components["schemas"]["SubmitOrderRequest"];
export type SubmitOrderResponse = components["schemas"]["SubmitOrderResponse"];
export type Trade = components["schemas"]["TradeDTO"];
export type StockCandle = components["schemas"]["StockPriceHistoryDTO"];
export type StockDetails = Omit<components["schemas"]["StockDetailsDTO"], "id">;

// Portfolio
export type Position = components["schemas"]["PositionDTO"];
export type PortfolioHistoryPoint = components["schemas"]["PortfolioHistoryPointDTO"];
export type FixedIncomePosition = components["schemas"]["FixedIncomePositionDTO"];
export type PortfolioState = components["schemas"]["PortfolioDTO"];

// Fixed Income
export type RateIndex = components["schemas"]["RateIndexType"];
export type FixedIncomeOffer = components["schemas"]["FixedIncomeOfferDTO"];
export type FixedIncomeQuote = components["schemas"]["FixedIncomeQuoteDTO"];
export type BuyFixedIncomeRequest = components["schemas"]["BuyFixedIncomeRequest"];
export type FixedIncomeRedemptionQuote = components["schemas"]["FixedIncomeRedemptionQuoteDTO"];
export type RedeemFixedIncomeRequest = components["schemas"]["RedeemFixedIncomeRequest"];

// Economic
export type EconomicIndicators = components["schemas"]["EconomicIndicatorsDTO"];

// Data center
export type SeriesCoverage = components["schemas"]["SeriesCoverageDTO"];
export type AssetClass = components["schemas"]["AssetClass"];
export type Sector = components["schemas"]["SectorDTO"];
export type StockSegment = components["schemas"]["StockSegmentDTO"];
export type TickerSuggestion = components["schemas"]["TickerSuggestionDTO"];
export type ImportResult = components["schemas"]["ImportResultDTO"];
export type ImportSettings = components["schemas"]["ImportSettingsDTO-Output"];
export type PriceCorrectionResult = components["schemas"]["PriceCorrectionResultDTO"];
export type ReplacedGenerated = components["schemas"]["ReplacedGeneratedDTO"];

// Futuro gerado
export type MarketRegime = components["schemas"]["MarketRegime"];
export type FutureParams = components["schemas"]["FutureParamsDTO"];
export type GeneratedFuture = components["schemas"]["GeneratedFutureDTO"];
export type FuturePreview = components["schemas"]["FuturePreviewDTO"];
export type FuturePreviewRequest = components["schemas"]["FuturePreviewRequest"];

// User
export type User = components["schemas"]["UserDTO"];
export type Session = components["schemas"]["SessionDTO"];
export type UserRegisterRequest = components["schemas"]["UserRegisterRequest"];
export type UserClaimRequest = components["schemas"]["UserClaimRequest"];

// Statistics
export type SeriesPoint = components["schemas"]["SeriesPointDTO"];
export type OverviewReport = components["schemas"]["OverviewReportDTO"];
export type StatisticsNextUpdate = components["schemas"]["StatisticsNextUpdateDTO"];
export type Highlights = components["schemas"]["HighlightsDTO"];
// Toda linha de jogador de qualquer aba traz quem é e em que simulação
type Score = NonNullable<OverviewReport["players"][number]["score"]>;
export type ScoreAxis = Score["axes"][number]["axis"];
export type ScoreMetric = Score["axes"][number]["metrics"][number]["metric"];
export type PlayerRef = Pick<
  OverviewReport["players"][number],
  "player_nickname" | "color" | "simulation_id" | "simulation_name" | "team" | "is_bot"
>;
export type ReturnsReport = components["schemas"]["ReturnsReportDTO"];
export type RiskReport = components["schemas"]["RiskReportDTO"];
export type ScoreHistoryReport = components["schemas"]["ScoreHistoryReportDTO"];
export type CompositionReport = components["schemas"]["CompositionReportDTO"];
export type OperationsReport = components["schemas"]["OperationsReportDTO"];
export type Player = OverviewReport["players"][number];
export type Team = OverviewReport["teams"][number];
export type ReturnsPlayer = ReturnsReport["players"][number];
export type RiskPlayer = RiskReport["players"][number];
export type CompositionPlayer = CompositionReport["players"][number];
export type OperationsPlayer = OperationsReport["players"][number];

// Correlation
export type CorrelationAssets = components["schemas"]["CorrelationAssetsDTO"];
export type CorrelationMatrix = components["schemas"]["CorrelationMatrixDTO"];
export type CorrelationCell = CorrelationMatrix["rows"][number][number];
type CorrelationQuery = operations["get_correlation_api_correlation_get"]["parameters"]["query"];
export type CorrelationWindow = NonNullable<CorrelationQuery["window"]>;

// Orders
export type Order = components["schemas"]["OrderDTO"];

// Notifications
export type NotificationPreferences = Pick<components["schemas"]["SettingsRequest"], "orders" | "players">;

// Configurações do jogador, com o que ele deixou ligado no gráfico das ações
export type UserSettings = components["schemas"]["SettingsRequest"];

// Indicadores técnicos
export type IndicatorSettings = components["schemas"]["IndicatorSettingsDTO-Output"];
export type IndicatorParams = components["schemas"]["IndicatorParamsDTO-Output"];
export type IndicatorKey = IndicatorSettings["visible"][number];
export type MovingAverage = IndicatorParams["averages"][number];
export type IndicatorsRequest = components["schemas"]["IndicatorsRequestDTO"];
export type TechnicalIndicators = components["schemas"]["TechnicalIndicatorsDTO"];
export type TechnicalSummary = TechnicalIndicators["summary"];
export type TechnicalReading = TechnicalSummary["readings"][number];
export type IndicatorPoint = components["schemas"]["IndicatorPointDTO"];

// Padrões de vela e desafio da vela
export type CandlePatterns = components["schemas"]["CandlePatternsDTO"];
export type CandlePattern = CandlePatterns["patterns"][number];
export type CandlePatternCode = CandlePattern["code"];
export type PatternStats = components["schemas"]["PatternStatsDTO"];
export type CandleChallenge = components["schemas"]["CandleChallengeDTO"];
export type ChallengeAnswer = NonNullable<CandleChallenge["last"]>;
export type ChallengeDirection = components["schemas"]["AnswerChallengeRequest"]["direction"];
export type CandleChallengeRanking = components["schemas"]["CandleChallengeRankingDTO"];

// Pastas do app no computador do host (config.toml e logs)
export type AppFolders = components["schemas"]["AppFoldersResponse"];
export type AppFolderTarget = keyof AppFolders;

// Modo debug: definido no boot do servidor, só leitura
export type DebugMode = components["schemas"]["SettingsResponse"]["debug"];

// Painel de desempenho
export type MetricsData = components["schemas"]["MetricsResponse"];
export type MetricItem = components["schemas"]["MetricItem"];
export type TrafficItem = components["schemas"]["TrafficItem"];

// Simulation
export type SimulationState = Partial<components["schemas"]["SimulationStateResponse"]>;
export type SimulationData = components["schemas"]["SimulationDTO"];
export type CreateSimulationRequest = components["schemas"]["CreateSimulationRequest"];
export type SimulationSettingsData = components["schemas"]["SimulationSettingsDTO"];
export type SetSpeedResponse = components["schemas"]["SetSpeedResponse"];
export type UpdateSettingsRequest = components["schemas"]["UpdateSettingsRequest"];
export type SimulationSettings = components["schemas"]["SimulationSettingsResponse"];
// Jogador da sala com a cor (chave da paleta) que o servidor deu a ele
export type RoomPlayer = components["schemas"]["PlayerNickname"];
// Bots: a estratégia que o jogador-robô joga, como a sala e o ranking o mostram
export type RoomBotRequest = components["schemas"]["RoomBotRequest"];
export type BotReport = components["schemas"]["BotReportDTO"];
export type BotParam = BotReport["params"][number];
// O que o jogador está fazendo na sala (a tela em que está, ou fora da aba do jogo)
export type PlayerActivity = components["schemas"]["PlayerActivity"];
export type SimulationInfo = components["schemas"]["SimulationStatusResponse"];
export type SimulationListItem = components["schemas"]["SavedSimulationDTO"];
// Presets de partida
export type Preset = components["schemas"]["PresetDTO"];
export type AppliedPreset = components["schemas"]["AppliedPresetDTO"];
export type PresetLoadResponse = components["schemas"]["PresetLoadResponse"];
export type PresetRuleGroup = components["schemas"]["PresetRuleGroup"];
export type SavePresetRequest = components["schemas"]["SavePresetRequest"];
export type PriceImpactPreview = components["schemas"]["PriceImpactPreviewDTO"];
export type VictoryCriterion = components["schemas"]["VictoryCriterion"];
export type GameType = components["schemas"]["GameType"];
export type ComputerDifficulty = components["schemas"]["ComputerDifficulty"];
export type TunnelStatus = components["schemas"]["TunnelStatusDTO"];
export type GoalProgress = components["schemas"]["GoalProgressDTO"];
export type GoalRunner = GoalProgress["players"][number];
export type PlayerGrouping = components["schemas"]["PlayerGrouping"];
export type TeamNaming = components["schemas"]["TeamNaming"];

// Governo & Política
export type ElectionPanel = components["schemas"]["ElectionPanelDTO"];
export type ElectionPhase = components["schemas"]["ElectionPhase"];
export type ElectionParty = ElectionPanel["parties"][number];
export type ElectionRound = components["schemas"]["RoundResultDTO"];
export type PartyCandidate = components["schemas"]["PartyCandidateDTO"];
export type FoundPartyRequest = components["schemas"]["FoundPartyRequest"];
export type JoinPartyRequest = components["schemas"]["JoinPartyRequest"];
export type ContributionRequest = components["schemas"]["ContributionRequest"];
export type ExpelRequest = components["schemas"]["ExpelRequest"];
export type TicketRequest = components["schemas"]["TicketRequest"];
export type ViceAnswerRequest = components["schemas"]["ViceAnswerRequest"];
export type DonationRequest = components["schemas"]["DonationRequest"];
export type GovernmentPanel = components["schemas"]["GovernmentPanelDTO"];
export type GovernmentMeasure = components["schemas"]["MeasureDTO"];
export type GovernmentNotice = components["schemas"]["GovernmentUpdateEventDTO"];
export type MeasureKind = components["schemas"]["MeasureKind"];
export type MeasureStatus = components["schemas"]["MeasureStatus"];
export type ProposeMeasureRequest = components["schemas"]["ProposeMeasureRequest"];
export type MeasurePreview = components["schemas"]["MeasurePreviewDTO"];
export type GovernmentApproval = NonNullable<GovernmentPanel["approval"]>;

// Viver de renda
export type LifeStatus = components["schemas"]["LifeStatusDTO"];
export type LifeHistoryPage = components["schemas"]["LifeHistoryPageDTO"];
export type LifeHistoryRow = LifeHistoryPage["items"][number];
export type LifeHistoryCategory = components["schemas"]["LifeHistoryCategory"];
export type LifeHistorySort = components["schemas"]["LifeHistorySort"];
export type LifeHistoryKind = LifeHistoryRow["kind"];

// Conquistas
export type Achievement = components["schemas"]["AchievementDTO"];
export type AchievementCategory = components["schemas"]["AchievementCategory"];
export type AchievementIconName = components["schemas"]["AchievementIcon"];

// Crédito
export type CreditOverview = components["schemas"]["CreditOverviewDTO"];
export type CreditGrade = components["schemas"]["CreditGrade"];
export type CreditLoan = CreditOverview["loans"][number];
export type CreditRating = CreditOverview["rating"];
export type CreditLadderTier = CreditRating["ladder"][number];
export type CreditSuggestion = CreditOverview["suggestions"][number];
export type LoanQuote = components["schemas"]["LoanQuoteDTO"];
export type PrepaymentPreview = components["schemas"]["PrepaymentPreviewDTO"];
export type PrepaymentMode = components["schemas"]["PrepaymentMode"];
export type ContractLoanRequest = components["schemas"]["ContractLoanRequestDTO"];
export type PrepayLoanRequest = components["schemas"]["PrepayLoanRequestDTO"];

// Backtest
export type BacktestConfigRequest = components["schemas"]["BacktestConfigDTO-Input"];
export type BacktestParticipant = components["schemas"]["BacktestParticipantDTO-Output"];
export type BacktestPriceImpact = components["schemas"]["BacktestPriceImpact"];
export type BacktestSetup = components["schemas"]["BacktestSetupDTO"];
export type BacktestCoverage = components["schemas"]["BacktestCoverageDTO"];
export type BacktestStatus = components["schemas"]["BacktestStatusDTO"];
export type BacktestProgress = NonNullable<BacktestStatus["progress"]>;
export type BacktestPoint = components["schemas"]["BacktestPointDTO"];
export type BacktestFailure = components["schemas"]["BacktestFailureDTO"];
export type BacktestResult = components["schemas"]["BacktestResultDTO"];
export type BacktestStopped = components["schemas"]["BacktestStoppedDTO"];

// Estratégias
export type StrategyInfo = components["schemas"]["StrategyInfoDTO"];
export type StrategyParam = StrategyInfo["params"][number];
export type StrategyParamValue = components["schemas"]["StrategyParamValue"];
export type StrategyGroup = components["schemas"]["StrategyGroup"];
export type StrategyAction = components["schemas"]["StrategyAction"];
export type StrategyOrderStatus = components["schemas"]["StrategyOrderStatus"];
export type MyStrategy = components["schemas"]["MyStrategyDTO"];
export type StrategyPanel = NonNullable<MyStrategy["panel"]>;
export type StrategyError = NonNullable<MyStrategy["error"]>;
export type SetStrategyRequest = components["schemas"]["SetStrategyRequestDTO"];
export type StrategySignal = components["schemas"]["SignalDTO"];
export type StrategyViewKind = components["schemas"]["StrategyView"];
export type StrategyViewData = components["schemas"]["StrategyViewDTO"];
export type StrategyRanking = NonNullable<StrategyViewData["ranking"]>;
export type StrategyAllocation = NonNullable<StrategyViewData["allocation"]>;
export type StrategyLogPage = components["schemas"]["StrategyLogPageDTO"];
export type StrategyLogRow = StrategyLogPage["items"][number];
export type StrategyLogKind = components["schemas"]["StrategyLogKind"];
export type StrategyLogFilter = "all" | "orders" | "modes";

// Caixa de entrada
export type Inbox = components["schemas"]["InboxDTO"];
export type InboxEntry = components["schemas"]["InboxEntryDTO"];
export type MonthSummary = components["schemas"]["MonthSummaryDTO"];
export type YearReview = components["schemas"]["YearReviewDTO"];
