import type { components } from "./openapi.generated";

/**
 * Catálogo de payloads de eventos realtime, gerado a partir do backend
 * (`backend/features/realtime/schemas.py` → `RealtimeEventCatalog`) via
 * `pnpm run types:generate`. Não editar os tipos de payload aqui à mão —
 * mudar o formato de um evento é uma mudança no DTO do backend.
 */
type RealtimeEventCatalog = components["schemas"]["RealtimeEventCatalog"];

/** Snapshot de patrimônio emitido via WebSocket/SSE */
export type Snapshot = RealtimeEventCatalog["snapshot_update"]["snapshot"];

export type OrderExecutedEvent = RealtimeEventCatalog["order_executed"];
export type OrderPartialExecutedEvent = RealtimeEventCatalog["order_partial_executed"];

/** Eventos emitidos pelo servidor via WebSocket ou SSE */
export type SimulationEvents = {
  simulation_started: RealtimeEventCatalog["simulation_started"];
  simulation_ended: RealtimeEventCatalog["simulation_ended"];
  simulation_update: RealtimeEventCatalog["simulation_update"];
  speed_update: RealtimeEventCatalog["speed_update"];
  cash_update: RealtimeEventCatalog["cash_update"];
  stocks_update: RealtimeEventCatalog["stocks_update"];
  fixed_assets_update: RealtimeEventCatalog["fixed_assets_update"];
  snapshot_update: RealtimeEventCatalog["snapshot_update"];
  fixed_income_position_update: RealtimeEventCatalog["fixed_income_position_update"];
  statistics_snapshot_update: RealtimeEventCatalog["statistics_snapshot_update"];
  order_executed: OrderExecutedEvent;
  order_partial_executed: OrderPartialExecutedEvent;
  player_join: RealtimeEventCatalog["player_join"];
  player_exit: RealtimeEventCatalog["player_exit"];
  simulation_settings_update: RealtimeEventCatalog["simulation_settings_update"];
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
