import { describe, expect, it } from "vitest";
import { moneyToBody, shareToField } from "./money-field";

describe("shareToField", () => {
  it("25% de R$ 1.000,01 são R$ 250,00: a fração trunca nos centavos", () => {
    // 1000,01 × 0,25 = 250,0025
    expect(moneyToBody(shareToField("1000.01", 0.25))).toBe("250.00");
  });

  it("50% de R$ 0,03 truncam em R$ 0,01 e nunca passam do total", () => {
    expect(moneyToBody(shareToField("0.03", 0.5))).toBe("0.01");
  });

  it("o total devolve o valor inteiro", () => {
    expect(moneyToBody(shareToField("1000.01", 1))).toBe("1000.01");
  });
});
