import { describe, expect, it } from "vitest";
import type { BacktestPoint } from "@/types";
import { applyProgress, EMPTY_STATUS } from "./backtest-progress";

const point = (day: string): BacktestPoint => ({ day, equity: ["100"], contributed: "100", cdi: "100", ibov: null });
const progress = {
  ...{ simulation_id: 1, name: "n", host_nickname: "h" },
  start_date: "2011-01-03",
  end_date: "2011-12-30",
  total_days: 100,
  done_days: 20,
  current_date: "2011-02-01",
  seconds_left: 10,
};

describe("applyProgress", () => {
  it("soma os pontos novos ao fim da série", () => {
    const first = applyProgress(EMPTY_STATUS, { progress, points: [point("2011-02-01")], failures: [] });
    const second = applyProgress(first, { progress, points: [point("2011-03-01")], failures: [] });
    expect(second.points.map((p) => p.day)).toEqual(["2011-02-01", "2011-03-01"]);
  });

  it("ignora o ponto de um dia que a série já tem", () => {
    const first = applyProgress(EMPTY_STATUS, { progress, points: [point("2011-02-01")], failures: [] });
    const again = applyProgress(first, { progress, points: [point("2011-02-01")], failures: [] });
    expect(again.points).toHaveLength(1);
  });
});
