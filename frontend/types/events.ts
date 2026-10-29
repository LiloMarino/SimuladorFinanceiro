import type { components } from "./openapi.generated";

/**
 * Catálogo de payloads de eventos realtime, gerado a partir do backend
 * (`backend/features/realtime/schemas.py` → `RealtimeEventCatalog`) via
 * `pnpm run types:generate`. Não editar os tipos de payload aqui à mão —
 * mudar o formato de um evento é uma mudança no DTO do backend.
 */
type RealtimeEventCatalog = components["schemas"]["RealtimeEventCatalog"];

type OrderExecutedEvent = RealtimeEventCatalog["order_executed"];
type OrderPartialExecutedEvent = RealtimeEventCatalog["order_partial_executed"];
type LifeEvent = RealtimeEventCatalog["life_event"];
export type FutureRecordingProgressEvent = RealtimeEventCatalog["future_recording_progress"];
export type AchievementUnlockedEvent = RealtimeEventCatalog["achievement_unlocked"];
export type StrategyOrderLine = RealtimeEventCatalog["strategy_orders"]["orders"][number];

/** Eventos emitidos pelo servidor via WebSocket */
export type SimulationEvents = {
  simulation_started: RealtimeEventCatalog["simulation_started"];
  simulation_ended: RealtimeEventCatalog["simulation_ended"];
  simulation_update: RealtimeEventCatalog["simulation_update"];
  speed_update: RealtimeEventCatalog["speed_update"];
  cash_update: RealtimeEventCatalog["cash_update"];
  stocks_update: RealtimeEventCatalog["stocks_update"];
  fixed_assets_update: RealtimeEventCatalog["fixed_assets_update"];
  snapshot_update: RealtimeEventCatalog["snapshot_update"];
  portfolio_update: RealtimeEventCatalog["portfolio_update"];
  statistics_snapshot_update: RealtimeEventCatalog["statistics_snapshot_update"];
  order_executed: OrderExecutedEvent;
  order_partial_executed: OrderPartialExecutedEvent;
  player_join: RealtimeEventCatalog["player_join"];
  player_exit: RealtimeEventCatalog["player_exit"];
  player_removed: RealtimeEventCatalog["player_removed"];
  player_color: RealtimeEventCatalog["player_color"];
  player_team: RealtimeEventCatalog["player_team"];
  player_activity: RealtimeEventCatalog["player_activity"];
  player_bot: RealtimeEventCatalog["player_bot"];
  simulation_selected: RealtimeEventCatalog["simulation_selected"];
  simulation_deleted: RealtimeEventCatalog["simulation_deleted"];
  simulation_settings_update: RealtimeEventCatalog["simulation_settings_update"];
  preset_applied_update: RealtimeEventCatalog["preset_applied_update"];
  goal_progress_update: RealtimeEventCatalog["goal_progress_update"];
  life_event: LifeEvent;
  future_recording_progress: FutureRecordingProgressEvent;
  achievement_unlocked: AchievementUnlockedEvent;
  summary_delivered: RealtimeEventCatalog["summary_delivered"];
  news_published: RealtimeEventCatalog["news_published"];
  credit_installment_paid: RealtimeEventCatalog["credit_installment_paid"];
  credit_monthly_summary: RealtimeEventCatalog["credit_monthly_summary"];
  credit_installment_late: RealtimeEventCatalog["credit_installment_late"];
  credit_installment_warning: RealtimeEventCatalog["credit_installment_warning"];
  credit_rating_changed: RealtimeEventCatalog["credit_rating_changed"];
  credit_loan_paid_off: RealtimeEventCatalog["credit_loan_paid_off"];
  government_update: RealtimeEventCatalog["government_update"];
  strategy_update: RealtimeEventCatalog["strategy_update"];
  strategy_orders: RealtimeEventCatalog["strategy_orders"];
  backtest_started: RealtimeEventCatalog["backtest_started"];
  backtest_progress: RealtimeEventCatalog["backtest_progress"];
  backtest_ended: RealtimeEventCatalog["backtest_ended"];
} & {
  [K in `stock_update:${string}`]: RealtimeEventCatalog["stock_update"];
} & {
  [K in `position_update:${string}`]: RealtimeEventCatalog["position_update"];
} & {
  [K in `order_added:${string}`]: RealtimeEventCatalog["order_added"];
} & {
  [K in `order_updated:${string}`]: RealtimeEventCatalog["order_updated"];
} & {
  [K in `order_book_snapshot:${string}`]: RealtimeEventCatalog["order_book_snapshot"];
};
