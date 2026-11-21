import { describe, expect, it } from "vitest";
import { billionsToField, CONTRIBUTION_SHORTCUTS_BILLIONS, fundCashLabel, shortcutLabel } from "./sovereign-fund";

describe("aporte no Fundo Soberano", () => {
  it("os atalhos vão de 25 a 500 bilhões", () => {
    expect([...CONTRIBUTION_SHORTCUTS_BILLIONS]).toEqual([25, 100, 250, 500]);
  });

  it("o atalho preenche o campo em reais e rotula em bilhões", () => {
    expect(billionsToField(25)).toContain("25.000.000.000");
    expect(shortcutLabel(25)).toContain("25");
    expect(shortcutLabel(25)).toContain("bi");
  });

  it("o caixa zerado aparece como R$ 0", () => {
    expect(fundCashLabel("0")).toBe("R$ 0");
    expect(fundCashLabel("0.00")).toBe("R$ 0");
    expect(fundCashLabel("18400000000")).toContain("bi");
  });
});
