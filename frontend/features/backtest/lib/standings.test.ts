import { describe, expect, it } from "vitest";
import type { BacktestParticipant, BacktestPoint } from "@/types";
import { referencesOf, standingsOf } from "./standings";

const participants = [
  { nickname: "A", color: "chart-1", strategy_key: "x", params: {} },
  { nickname: "B", color: "chart-2", strategy_key: "x", params: {} },
] as BacktestParticipant[];

const point = { day: "2020-03-02", equity: ["110.00", "150.00"], contributed: "100.00", cdi: "120.00", ibov: null } as BacktestPoint;

describe("standingsOf", () => {
  it("ordena pelo patrimônio e calcula o retorno sobre o aportado", () => {
    const [first, second] = standingsOf(participants, point, []);
    expect(first.participant.nickname).toBe("B");
    expect(first.returnOnContributed).toBeCloseTo(0.5);
    expect(second.returnOnContributed).toBeCloseTo(0.1);
  });

  it("marca o dia do erro", () => {
    const standings = standingsOf(participants, point, [{ nickname: "A", day: "2020-02-03", message: "x" }]);
    expect(standings.find((s) => s.participant.nickname === "A")?.failedOn).toBe("2020-02-03");
  });

  it("vem vazia antes do primeiro ponto", () => {
    expect(standingsOf(participants, undefined, [])).toEqual([]);
  });
});

describe("referencesOf", () => {
  it("omite o Ibovespa sem dado", () => {
    expect(referencesOf(point).map((r) => r.key)).toEqual(["cdi"]);
    expect(referencesOf(point)[0].returnOnContributed).toBeCloseTo(0.2);
  });
});
