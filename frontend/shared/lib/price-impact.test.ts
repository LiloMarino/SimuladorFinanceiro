import { describe, expect, it } from "vitest";
import { isPriceImpactKHigh, priceImpactJump } from "./price-impact";

describe("priceImpactJump", () => {
  it("compra de 4 vezes o volume médio sobe k·2", () => {
    expect(priceImpactJump(0.1)).toBeCloseTo(0.2);
    expect(priceImpactJump(1)).toBeCloseTo(2);
  });

  it("segue a raiz do múltiplo informado", () => {
    expect(priceImpactJump(0.02, 1)).toBeCloseTo(0.02);
    expect(priceImpactJump(0.02, 25)).toBeCloseTo(0.1);
  });
});

describe("isPriceImpactKHigh", () => {
  it("avisa só acima de 0,10", () => {
    expect(isPriceImpactKHigh("0,10")).toBe(false);
    expect(isPriceImpactKHigh("0,11")).toBe(true);
    expect(isPriceImpactKHigh("3")).toBe(true);
  });

  it("não avisa com os presets nem com campo vazio ou inválido", () => {
    expect(isPriceImpactKHigh("0,02")).toBe(false);
    expect(isPriceImpactKHigh("0,05")).toBe(false);
    expect(isPriceImpactKHigh("")).toBe(false);
    expect(isPriceImpactKHigh("abc")).toBe(false);
  });
});
