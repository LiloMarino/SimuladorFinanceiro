import { describe, expect, it } from "vitest";
import type { BacktestResult, Player } from "@/types";
import { backtestRows, defaultMeasure, finalReferences, rankRows } from "./backtest-result";

const result = {
  config: {
    participants: [
      { nickname: "A", color: "#111111", strategy_key: "buy_and_hold", params: {} },
      { nickname: "B", color: "#222222", strategy_key: "buy_and_hold", params: {} },
    ],
  },
  failures: [{ nickname: "B", day: "2018-03-14", message: "erro" }],
  references: [
    { day: "2018-03-13", contributed: "100000", cdi: "100000", ibov: null },
    { day: "2018-03-14", contributed: "200000", cdi: "220000", ibov: "180000" },
  ],
} as unknown as BacktestResult;

const players = [
  { player_nickname: "A", total_networth: "300000", score: { total: "250" } },
  { player_nickname: "B", total_networth: "210000", score: null },
  { player_nickname: "Fora", total_networth: "1", score: null },
] as unknown as Player[];

describe("finalReferences", () => {
  it("usa o último pregão e o retorno sobre o aportado", () => {
    const refs = finalReferences(result)!;
    expect(refs.contributed).toBe(200000);
    expect(refs.cdi.returnOnContributed).toBeCloseTo(0.1);
    expect(refs.ibov?.returnOnContributed).toBeCloseTo(-0.1);
  });

  it("não há referência sem pontos", () => {
    expect(finalReferences({ ...result, references: [] })).toBeNull();
  });
});

describe("backtestRows", () => {
  const rows = backtestRows(players, result, finalReferences(result)!);

  it("só traz os participantes do backtest", () => {
    expect(rows.map((r) => r.participant.nickname)).toEqual(["A", "B"]);
  });

  it("calcula o retorno e a diferença para o CDI em fração", () => {
    expect(rows[0].returnOnContributed).toBeCloseTo(0.5);
    expect(rows[0].overCdi).toBeCloseTo(0.4);
    expect(rows[1].overCdi).toBeCloseTo(-0.05);
  });

  it("marca o dia em que a estratégia parou de operar", () => {
    expect(rows[1].failedOn).toBe("2018-03-14");
    expect(rows[0].failedOn).toBeNull();
  });

  it("ordena pela medida e deixa quem não tem nota no fim", () => {
    expect(rankRows(rows, "SCORE").map((r) => r.participant.nickname)).toEqual(["A", "B"]);
    expect(rankRows([...rows].reverse(), "NETWORTH").map((r) => r.participant.nickname)).toEqual(["A", "B"]);
  });

  it("cai para o patrimônio quando ninguém tem nota", () => {
    expect(defaultMeasure(rows)).toBe("SCORE");
    expect(defaultMeasure(rows.map((r) => ({ ...r, score: null })))).toBe("NETWORTH");
  });
});
