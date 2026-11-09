import { describe, expect, it } from "vitest";
import { breakEvenDollarRise, dollarPurchase } from "./carry";

describe("empate do dólar", () => {
  it("CDI de 13% contra Fed de 5% pede o dólar 7,6% mais caro", () => {
    expect(breakEvenDollarRise("0.13", "0.05")).toBeCloseTo(0.0762, 4);
  });

  it("juros iguais não pedem alta nenhuma", () => {
    expect(breakEvenDollarRise("0.05", "0.05")).toBe(0);
  });

  it("Fed acima do CDI dá um empate negativo: a conta ganha mesmo com o dólar caindo", () => {
    expect(breakEvenDollarRise("0.04", "0.05")).toBeLessThan(0);
  });
});

describe("compra de dólares", () => {
  it("R$ 10.000 a R$ 5,00 com IOF de 1,1% viram US$ 1.978 e R$ 110 de IOF", () => {
    const { iof, dollars } = dollarPurchase(10000, 5, "0.011");
    expect(iof).toBeCloseTo(110, 6);
    expect(dollars).toBeCloseTo(1978, 6);
  });
});
