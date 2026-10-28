import { describe, expect, it } from "vitest";
import type { PortfolioState } from "@/types";
import { assetCount, classSlices, ringArc, sliceAngles, topAssets } from "./allocation-model";

function portfolio(partial: { cash: string; equity?: [string, string][]; fixed?: [string, string][] }): PortfolioState {
  const equity = partial.equity ?? [];
  const fixed = partial.fixed ?? [];
  const sum = (items: [string, string][]) => items.reduce((total, [, value]) => total + Number(value), 0);
  const variable = sum(equity);
  const fixedTotal = sum(fixed);
  return {
    cash: partial.cash,
    variable_income_value: String(variable),
    fixed_income_value: String(fixedTotal),
    assets_value: String(Number(partial.cash) + variable + fixedTotal),
    variable_income: equity.map(([ticker, value]) => ({ ticker, current_value: value })),
    fixed_income: fixed.map(([name, value]) => ({ asset: { name }, current_value: value })),
  } as unknown as PortfolioState;
}

describe("classSlices", () => {
  it("divide o que o jogador tem entre as classes que têm dinheiro", () => {
    // 60 em ações + 30 em renda fixa + 10 de caixa = 100: 60%, 30% e 10%
    const slices = classSlices(portfolio({ cash: "10", equity: [["PETR4", "60"]], fixed: [["CDB", "30"]] }));
    expect(slices.map((s) => [s.key, s.fraction])).toEqual([
      ["variable", 0.6],
      ["fixed", 0.3],
      ["cash", 0.1],
    ]);
  });

  it("deixa de fora a classe sem dinheiro", () => {
    const slices = classSlices(portfolio({ cash: "50000" }));
    expect(slices.map((s) => s.key)).toEqual(["cash"]);
    expect(slices[0]?.fraction).toBe(1);
  });
});

describe("topAssets", () => {
  it("ordena do maior para o menor, de qualquer classe", () => {
    const rows = topAssets(
      portfolio({
        cash: "0",
        equity: [
          ["VALE3", "20"],
          ["PETR4", "50"],
        ],
        fixed: [["CDB", "30"]],
      }),
    );
    expect(rows.map((r) => r.name)).toEqual(["PETR4", "CDB", "VALE3"]);
  });

  it("junta o que passa do limite em Outros, com a soma e a contagem", () => {
    // Limite de 2 ativos: sobram 3 + 1 + 1 = 5 numa linha só, de 5 em 85 do total
    const rows = topAssets(
      portfolio({
        cash: "0",
        equity: [
          ["AAA", "50"],
          ["BBB", "30"],
          ["CCC", "3"],
          ["DDD", "1"],
        ],
        fixed: [["EEE", "1"]],
      }),
      2,
    );
    expect(rows.map((r) => r.name)).toEqual(["AAA", "BBB", "Outros"]);
    expect(rows[2]).toMatchObject({ value: 5, count: 3 });
    expect(rows[2]?.fraction).toBeCloseTo(5 / 85, 10);
  });

  it("sem excedente não há linha Outros", () => {
    expect(topAssets(portfolio({ cash: "0", equity: [["AAA", "1"]] }), 2)).toHaveLength(1);
  });
});

describe("assetCount", () => {
  it("conta os ativos de todas as classes", () => {
    expect(
      assetCount(
        portfolio({
          cash: "1",
          equity: [
            ["A", "1"],
            ["B", "1"],
          ],
          fixed: [["C", "1"]],
        }),
      ),
    ).toBe(3);
  });
});

describe("sliceAngles", () => {
  it("reparte a volta pelas frações, com uma folga entre vizinhas", () => {
    // 50% e 50%: cada fatia ocupa meia volta menos a folga de 0,03 rad (0,015 de cada lado)
    const [first, second] = sliceAngles([0.5, 0.5]);
    expect(first?.start).toBeCloseTo(-Math.PI / 2 + 0.015, 10);
    expect(first?.end).toBeCloseTo(Math.PI / 2 - 0.015, 10);
    expect(second?.start).toBeCloseTo(Math.PI / 2 + 0.015, 10);
  });

  it("uma fatia única dá a volta inteira sem folga", () => {
    const [only] = sliceAngles([1]);
    expect((only?.end ?? 0) - (only?.start ?? 0)).toBeCloseTo(2 * Math.PI, 10);
  });
});

describe("ringArc", () => {
  it("desenha a volta inteira como dois círculos", () => {
    expect(ringArc(50, 50, 40, 30, -Math.PI / 2, (3 * Math.PI) / 2).match(/M/g)).toHaveLength(2);
  });

  it("marca o arco grande quando a fatia passa de meia volta", () => {
    expect(ringArc(50, 50, 40, 30, 0, Math.PI * 1.5)).toContain("0 1 1");
    expect(ringArc(50, 50, 40, 30, 0, Math.PI / 2)).toContain("0 0 1");
  });
});
