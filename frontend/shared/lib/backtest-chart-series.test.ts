import { describe, expect, it } from "vitest";
import type { BacktestParticipant, BacktestPoint } from "@/types";
import { chartSeries } from "./backtest-chart-series";

const participants = [{ nickname: "A", color: "chart-1", strategy_key: "x", params: {} }] as BacktestParticipant[];
const points = [
  { day: "2020-01-02", equity: ["100"], contributed: "100", cdi: "100", ibov: null },
  { day: "2020-01-30", equity: ["110"], contributed: "100", cdi: "101", ibov: "99" },
] as BacktestPoint[];

describe("chartSeries", () => {
  it("põe cada estratégia no índice da carteira dela", () => {
    const [strategy] = chartSeries(participants, points);
    expect(strategy.points.map((p) => p.value)).toEqual(["100", "110"]);
  });

  it("começa o Ibovespa só no primeiro dia com dado", () => {
    const ibov = chartSeries(participants, points).find((s) => s.key === "ibov");
    expect(ibov?.points).toEqual([{ date: "2020-01-30", value: "99" }]);
  });

  it("omite o Ibovespa quando nenhum ponto tem dado", () => {
    const series = chartSeries(participants, [points[0]]);
    expect(series.some((s) => s.key === "ibov")).toBe(false);
  });
});
