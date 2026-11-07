import { describe, expect, it } from "vitest";
import type { ReturnSources } from "@/types";
import { buildWaterfall, playerPoints, segmentLayout, shareOfReturn } from "./return-sources";

const sources = (overrides: Partial<ReturnSources> = {}): ReturnSources => ({
  appreciation: "9000",
  dividends: "2000",
  fixed_income_interest: "1500",
  taxes: "-500",
  debt_interest: "0",
  campaign: "0",
  ...overrides,
});

describe("buildWaterfall", () => {
  it("a cascata soma as parcelas e cada barra começa onde a anterior terminou", () => {
    const { rows, total } = buildWaterfall(sources());
    expect(total).toBe(12000);
    expect(rows.map((r) => [r.key, r.start, r.end])).toEqual([
      ["appreciation", 0, 9000],
      ["dividends", 9000, 11000],
      ["fixed_income_interest", 11000, 12500],
      ["taxes", 12500, 12000],
    ]);
  });

  it("juro de dívida e campanha só entram quando existem", () => {
    const keys = (s: ReturnSources) => buildWaterfall(s).rows.map((r) => r.key);
    expect(keys(sources())).not.toContain("debt_interest");
    expect(keys(sources({ debt_interest: "-80", campaign: "-20" }))).toEqual(
      expect.arrayContaining(["debt_interest", "campaign"]),
    );
  });

  it("a escala inclui o zero e o maior acumulado", () => {
    const { min, max } = buildWaterfall(
      sources({ appreciation: "-300", dividends: "0", fixed_income_interest: "0", taxes: "0" }),
    );
    expect([min, max]).toEqual([-300, 0]);
  });
});

describe("shareOfReturn", () => {
  it("é a fatia do retorno, e não existe sem retorno positivo", () => {
    expect(shareOfReturn(2000, 10000)).toBe(0.2);
    expect(shareOfReturn(2000, -100)).toBeNull();
  });
});

describe("playerPoints", () => {
  it("divide cada grupo pelo aporte e junta os custos", () => {
    const points = playerPoints(sources({ debt_interest: "-100" }), 10000);
    expect(points?.map((p) => [p.key, p.points])).toEqual([
      ["appreciation", 0.9],
      ["dividends", 0.2],
      ["fixed_income_interest", 0.15],
      ["costs", -0.06],
    ]);
  });

  it("sem aporte não há pontos", () => {
    expect(playerPoints(sources(), 0)).toBeNull();
  });
});

describe("segmentLayout", () => {
  it("empilha os ganhos à direita do zero e os custos à esquerda", () => {
    const points = playerPoints(sources({ taxes: "-1000" }), 10000)!;
    // Escala de 100 pontos de largura: 1,05 à direita, 0,10 à esquerda
    const layout = segmentLayout(points, 1.15, 8.7);
    expect(layout.map((s) => [s.point.key, Math.round(s.start * 10) / 10])).toEqual([
      ["appreciation", 8.7],
      ["dividends", 8.7 + Math.round((0.9 / 1.15) * 1000) / 10],
      ["fixed_income_interest", 8.7 + Math.round(((0.9 + 0.2) / 1.15) * 1000) / 10],
      ["costs", 0],
    ]);
  });
});
