import { describe, expect, it } from "vitest";
import type { NetworthPoint } from "./networth-model";
import { classPanels } from "./networth-panels";

const point = (locked: number): NetworthPoint => ({
  date: "2024-01-02",
  networth: 10_000 + locked,
  provided: 10_000,
  debt: 0,
  equity: 0,
  fixed: 0,
  cash: 10_000,
  locked,
  equityByClass: undefined,
  goal: undefined,
});

describe("classPanels", () => {
  it("abre o painel do FGTS quando algum dia teve saldo", () => {
    const panels = classPanels([point(0), point(2_500)]);

    expect(panels.map((p) => p.label)).toEqual(["Renda variável", "Renda fixa", "Caixa", "FGTS"]);
    const fgts = panels.at(-1);
    expect(fgts?.color).toBe("var(--chart-7)");
    expect(fgts?.valueOf(point(2_500))).toBe(2_500);
  });

  it("some quando nenhum dia teve saldo", () => {
    const panels = classPanels([point(0), point(0)]);

    expect(panels.map((p) => p.label)).toEqual(["Renda variável", "Renda fixa", "Caixa"]);
  });
});
