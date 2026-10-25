import { describe, expect, it } from "vitest";
import type { MetricItem, MetricsData } from "@/types";
import {
  buildRows,
  countByKind,
  ENGINE_DAY,
  engineStatus,
  filterRows,
  flagOf,
  httpSummary,
  isHeavy,
  sortRows,
  trafficSummary,
} from "./stats";

const metric = (overrides: Partial<MetricItem>): MetricItem => ({
  kind: "http",
  name: "GET /api/x",
  calls: 1,
  total_ms: 0,
  mean_ms: 0,
  p95_ms: 0,
  max_ms: 0,
  ...overrides,
});

const metrics = (overrides: Partial<MetricsData>): MetricsData => ({
  pid: 1,
  players: 1,
  engine: { speed: 4, budget_ms: 250 },
  items: [],
  overall: [],
  traffic: [],
  ...overrides,
});

describe("marcação de lentidão", () => {
  it("p95 acima de 500 ms é lento", () => {
    expect(flagOf(metric({ mean_ms: 400, p95_ms: 501 }))).toBe("slow");
  });

  it("p95 de 10× a média ou mais é travada", () => {
    expect(flagOf(metric({ mean_ms: 10, p95_ms: 100 }))).toBe("stall");
    expect(flagOf(metric({ mean_ms: 10, p95_ms: 99 }))).toBeNull();
    expect(flagOf(metric({ mean_ms: 0, p95_ms: 100 }))).toBeNull();
  });
});

describe("linhas da tabela", () => {
  const rows = buildRows([
    metric({ name: "GET /a", calls: 5, total_ms: 300 }),
    metric({ kind: "socket", name: "join", calls: 5, total_ms: 100 }),
    metric({ kind: "engine", name: ENGINE_DAY, calls: 9, total_ms: 0 }),
  ]);

  it("a fatia é a parte do tempo total, e o socket ganha o rótulo de recebido", () => {
    expect(rows.map((r) => [r.label, r.share])).toEqual([
      ["GET /a", 0.75],
      ["join (recebido)", 0.25],
      [ENGINE_DAY, 0],
    ]);
  });

  it("sem tempo nenhum a fatia é zero", () => {
    expect(buildRows([metric({ total_ms: 0 })])[0].share).toBe(0);
  });

  it("ordena do maior para o menor e desempata pelo rótulo", () => {
    expect(sortRows(rows, "calls").map((r) => r.label)).toEqual([ENGINE_DAY, "GET /a", "join (recebido)"]);
  });

  it("filtra por tipo e pela busca, sem diferenciar maiúsculas", () => {
    expect(filterRows(rows, "socket", " JOIN ").map((r) => r.name)).toEqual(["join"]);
    expect(filterRows(rows, "all", "")).toHaveLength(3);
    expect(countByKind(rows)).toEqual({ all: 3, http: 1, socket: 1, engine: 1 });
  });
});

describe("estado do motor", () => {
  it("atrasado quando o dia leva mais que o orçamento, com a velocidade que dá para manter", () => {
    const status = engineStatus(metrics({ items: [metric({ kind: "engine", name: ENGINE_DAY, mean_ms: 500 })] }));
    // 1.000 ms ÷ 500 ms por dia = 2 dias por segundo
    expect(status).toMatchObject({ speed: 4, budgetMs: 250, late: true, effectiveSpeed: 2 });
  });

  it("sem orçamento nunca atrasa", () => {
    const status = engineStatus(
      metrics({
        engine: { speed: 4, budget_ms: null },
        items: [metric({ kind: "engine", name: ENGINE_DAY, mean_ms: 500 })],
      }),
    );
    expect(status).toMatchObject({ late: false, effectiveSpeed: null });
  });
});

describe("resumos", () => {
  it("soma as chamadas HTTP e conta as rotas lentas", () => {
    const summary = httpSummary(
      metrics({
        items: [
          metric({ calls: 10, p95_ms: 600 }),
          metric({ calls: 5, p95_ms: 100 }),
          metric({ kind: "socket", calls: 50, p95_ms: 900 }),
        ],
        overall: [{ kind: "http", p95_ms: 120 }],
      }),
    );
    expect(summary).toEqual({ calls: 15, p95Ms: 120, slowRoutes: 1 });
  });

  it("o tráfego soma tudo e aponta o evento mais pesado", () => {
    const summary = trafficSummary([
      { event: "tick", msgs_per_s: 2, bytes_per_s: 300, bytes_per_msg: 150 },
      { event: "chat", msgs_per_s: 1, bytes_per_s: 100, bytes_per_msg: 100 },
    ]);
    expect(summary).toEqual({ msgsPerSecond: 3, bytesPerSecond: 400, top: { event: "tick", share: 0.75 } });
    expect(trafficSummary([])).toEqual({ msgsPerSecond: 0, bytesPerSecond: 0, top: null });
  });

  it("mensagem pesada tem 100 KB ou mais e chega ao menos uma vez por segundo", () => {
    expect(isHeavy({ event: "x", msgs_per_s: 1, bytes_per_s: 100_000, bytes_per_msg: 100_000 })).toBe(true);
    expect(isHeavy({ event: "x", msgs_per_s: 1, bytes_per_s: 99_999, bytes_per_msg: 99_999 })).toBe(false);
    expect(isHeavy({ event: "x", msgs_per_s: 0.5, bytes_per_s: 50_000, bytes_per_msg: 100_000 })).toBe(false);
  });
});
