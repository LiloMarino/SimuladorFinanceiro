import type { MetricItem, MetricsData, TrafficItem } from "@/types";

export const REFRESH_MS = 2000;
/** Mesmo corte do slow.log do servidor. */
export const SLOW_P95_MS = 500;
/** p95 de dez vezes a média ou mais: quase sempre rápida, de vez em quando trava. */
const STALL_RATIO = 10;
export const PAGE_SIZE = 10;
export const ENGINE_DAY = "Processar um dia";
/** Mensagem pesada e frequente é o que pesa no navegador em velocidade alta. */
const HEAVY_MESSAGE_BYTES = 100_000;

export type Kind = MetricItem["kind"];
export type KindFilter = "all" | Kind;

export const KIND_LABEL: Record<Kind, string> = {
  http: "HTTP",
  socket: "Socket.IO",
  engine: "Motor",
};
export const KIND_FILTERS: KindFilter[] = ["all", "http", "socket", "engine"];

export type Flag = "slow" | "stall" | null;

export function flagOf(item: MetricItem): Flag {
  if (item.p95_ms > SLOW_P95_MS) return "slow";
  if (item.mean_ms > 0 && item.p95_ms >= STALL_RATIO * item.mean_ms) return "stall";
  return null;
}

export interface Row extends MetricItem {
  /** Fração do tempo total medido (0 a 1). */
  share: number;
  flag: Flag;
  /** Como o nome aparece na tabela. */
  label: string;
}

export function buildRows(items: MetricItem[]): Row[] {
  const total = items.reduce((sum, item) => sum + item.total_ms, 0);
  return items.map((item) => ({
    ...item,
    share: total > 0 ? item.total_ms / total : 0,
    flag: flagOf(item),
    label: item.kind === "socket" ? `${item.name} (recebido)` : item.name,
  }));
}

export type SortKey = "calls" | "total_ms" | "mean_ms" | "p95_ms" | "max_ms" | "share";

export function sortRows(rows: Row[], key: SortKey): Row[] {
  return [...rows].sort((a, b) => b[key] - a[key] || a.label.localeCompare(b.label));
}

export function filterRows(rows: Row[], kind: KindFilter, search: string): Row[] {
  const term = search.trim().toLowerCase();
  return rows.filter((row) => (kind === "all" || row.kind === kind) && row.label.toLowerCase().includes(term));
}

export function countByKind(rows: Row[]): Record<KindFilter, number> {
  const counts: Record<KindFilter, number> = {
    all: rows.length,
    http: 0,
    socket: 0,
    engine: 0,
  };
  for (const row of rows) counts[row.kind] += 1;
  return counts;
}

export interface EngineStatus {
  item: MetricItem | undefined;
  speed: number;
  /** Tempo que cabe em cada dia na velocidade pedida; vazio com a partida pausada. */
  budgetMs: number | null;
  late: boolean;
  /** Velocidade que a partida realmente alcança, quando atrasa. */
  effectiveSpeed: number | null;
}

export function engineStatus(data: MetricsData): EngineStatus {
  const item = data.items.find((i) => i.kind === "engine" && i.name === ENGINE_DAY);
  const budgetMs = data.engine.budget_ms ?? null;
  const late = !!item && budgetMs !== null && item.mean_ms > budgetMs;
  return {
    item,
    speed: data.engine.speed,
    budgetMs,
    late,
    effectiveSpeed: late ? Math.round(1000 / item.mean_ms) : null,
  };
}

export interface HttpSummary {
  calls: number;
  p95Ms: number | null;
  slowRoutes: number;
}

export function httpSummary(data: MetricsData): HttpSummary {
  const http = data.items.filter((i) => i.kind === "http");
  return {
    calls: http.reduce((sum, i) => sum + i.calls, 0),
    p95Ms: data.overall.find((o) => o.kind === "http")?.p95_ms ?? null,
    slowRoutes: http.filter((i) => i.p95_ms > SLOW_P95_MS).length,
  };
}

export interface TrafficSummary {
  msgsPerSecond: number;
  bytesPerSecond: number;
  /** O evento que mais pesa e a fração do volume que ele responde. */
  top: { event: string; share: number } | null;
}

export function trafficSummary(traffic: TrafficItem[]): TrafficSummary {
  const bytesPerSecond = traffic.reduce((sum, t) => sum + t.bytes_per_s, 0);
  const top = [...traffic].sort((a, b) => b.bytes_per_s - a.bytes_per_s)[0];
  return {
    msgsPerSecond: traffic.reduce((sum, t) => sum + t.msgs_per_s, 0),
    bytesPerSecond,
    top: top && bytesPerSecond > 0 ? { event: top.event, share: top.bytes_per_s / bytesPerSecond } : null,
  };
}

export function isHeavy(item: TrafficItem): boolean {
  return item.bytes_per_msg >= HEAVY_MESSAGE_BYTES && item.msgs_per_s >= 1;
}
