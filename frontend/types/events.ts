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
  sovereign_fund_update: RealtimeEventCatalog["sovereign_fund_update"];
  state_companies_update: RealtimeEventCatalog["state_companies_update"];
  credit_update: RealtimeEventCatalog["credit_update"];
  treasury_catalog_update: RealtimeEventCatalog["treasury_catalog_update"];
  treasury_history_update: RealtimeEventCatalog["treasury_history_update"];
  treasury_positions_update: RealtimeEventCatalog["treasury_positions_update"];
  life_status_update: RealtimeEventCatalog["life_status_update"];
  pending_update: RealtimeEventCatalog["pending_update"];
  fund_accounts_update: RealtimeEventCatalog["fund_accounts_update"];
  funds_list_update: RealtimeEventCatalog["funds_list_update"];
  fund_offers_update: RealtimeEventCatalog["fund_offers_update"];
  comanager_update: RealtimeEventCatalog["comanager_update"];
  budget_update: RealtimeEventCatalog["budget_update"];
  economy_update: RealtimeEventCatalog["economy_update"];
  base_update: RealtimeEventCatalog["base_update"];
  election_update: RealtimeEventCatalog["election_update"];
  map_update: RealtimeEventCatalog["map_update"];
  map_timeline_update: RealtimeEventCatalog["map_timeline_update"];
  campaign_update: RealtimeEventCatalog["campaign_update"];
  campaign_history_update: RealtimeEventCatalog["campaign_history_update"];
  promises_update: RealtimeEventCatalog["promises_update"];
  balances_update: RealtimeEventCatalog["balances_update"];
  government_panel_update: RealtimeEventCatalog["government_panel_update"];
  snapshot_update: RealtimeEventCatalog["snapshot_update"];
  portfolio_update: RealtimeEventCatalog["portfolio_update"];
  statistics_snapshot_update: RealtimeEventCatalog["statistics_snapshot_update"];
  order_executed: OrderExecutedEvent;
  order_partial_executed: OrderPartialExecutedEvent;
  order_canceled: RealtimeEventCatalog["order_canceled"];
  player_join: RealtimeEventCatalog["player_join"];
  player_exit: RealtimeEventCatalog["player_exit"];
  player_removed: RealtimeEventCatalog["player_removed"];
  player_color: RealtimeEventCatalog["player_color"];
  player_team: RealtimeEventCatalog["player_team"];
  player_profession: RealtimeEventCatalog["player_profession"];
  player_activity: RealtimeEventCatalog["player_activity"];
  player_bot: RealtimeEventCatalog["player_bot"];
  preparations_update: RealtimeEventCatalog["preparations_update"];
  simulation_selected: RealtimeEventCatalog["simulation_selected"];
  simulation_deleted: RealtimeEventCatalog["simulation_deleted"];
  simulation_settings_update: RealtimeEventCatalog["simulation_settings_update"];
  preset_applied_update: RealtimeEventCatalog["preset_applied_update"];
  goal_progress_update: RealtimeEventCatalog["goal_progress_update"];
  life_event: LifeEvent;
  auto_redeem: RealtimeEventCatalog["auto_redeem"];
  corporate_actions: RealtimeEventCatalog["corporate_actions"];
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
  strategy_log_update: RealtimeEventCatalog["strategy_log_update"];
  candle_challenge_state: RealtimeEventCatalog["candle_challenge_state"];
  candle_challenge_notice: RealtimeEventCatalog["candle_challenge_notice"];
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
} & {
  [K in `order_preview:${string}`]: RealtimeEventCatalog["order_preview"];
} & {
  [K in `indicators_update:${string}`]: RealtimeEventCatalog["indicators_update"];
} & {
  [K in `candle_patterns_update:${string}`]: RealtimeEventCatalog["candle_patterns_update"];
} & {
  [K in `state_company_update:${string}`]: RealtimeEventCatalog["state_company_update"];
} & {
  [K in `fixed_income_offer_update:${string}`]: RealtimeEventCatalog["fixed_income_offer_update"];
} & {
  [K in `fixed_income_projection:${string}`]: RealtimeEventCatalog["fixed_income_projection"];
} & {
  [K in `fund_update:${string}`]: RealtimeEventCatalog["fund_update"];
} & {
  [K in `fund_issuance_preview:${string}`]: RealtimeEventCatalog["fund_issuance_preview"];
} & {
  [K in `fund_subscription_preview:${string}`]: RealtimeEventCatalog["fund_subscription_preview"];
} & {
  [K in `fund_directed_preview:${string}`]: RealtimeEventCatalog["fund_directed_preview"];
} & {
  [K in `fund_merge_preview:${string}`]: RealtimeEventCatalog["fund_merge_preview"];
} & {
  [K in `fund_buyback_preview:${string}`]: RealtimeEventCatalog["fund_buyback_preview"];
} & {
  [K in `corporate_events_update:${string}`]: RealtimeEventCatalog["corporate_events_update"];
};
