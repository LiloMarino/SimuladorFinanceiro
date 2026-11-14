import { describe, expect, it } from "vitest";
import {
  feeCapFraction,
  feeCapToBody,
  feeCapToField,
  isFeeCap,
  managementFeeExample,
  performanceFeeExample,
} from "./fund-rules";

describe("teto de taxa da gestora", () => {
  it("a fração do servidor vira percentual no campo", () => {
    // 0,02 × 100 = 2%; 0,20 × 100 = 20%; 0,015 × 100 = 1,5%
    expect(feeCapToField("0.02")).toBe("2");
    expect(feeCapToField("0.20")).toBe("20");
    expect(feeCapToField("0.015")).toBe("1,5");
  });

  it("o campo com vírgula vira fração com quatro casas no corpo", () => {
    expect(feeCapFraction("1,5")).toBeCloseTo(0.015, 10);
    expect(feeCapToBody("2")).toBe("0.0200");
    expect(feeCapToBody("20")).toBe("0.2000");
    expect(feeCapToBody("1,5")).toBe("0.0150");
  });

  it("aceita de 0% a 100% e recusa campo vazio ou acima", () => {
    expect(isFeeCap("0")).toBe(true);
    expect(isFeeCap("100")).toBe(true);
    expect(isFeeCap("100,5")).toBe(false);
    expect(isFeeCap("")).toBe(false);
  });

  it("ida e volta devolve o valor do servidor", () => {
    expect(feeCapToBody(feeCapToField("0.0250"))).toBe("0.0250");
  });
});

describe("exemplos dos tetos de taxa", () => {
  it("administração: R$ 1 milhão a 2% ao ano rende R$ 1.667 por mês ao gestor", () => {
    // 1.000.000 × 0,02 ÷ 12 = 1.666,67
    expect(managementFeeExample("2")).toBeCloseTo(1666.67, 2);
    expect(managementFeeExample("")).toBeNull();
  });

  it("performance: o excesso de 5 pontos sobre o CDI, com 20% para o gestor, dá 1 ponto", () => {
    // 15% − 10% = 5 pontos acima do CDI; 5 × 0,20 = 1 ponto
    const example = performanceFeeExample("20");
    expect(example?.extraPoints).toBeCloseTo(5, 10);
    expect(example?.points).toBeCloseTo(1, 10);
    expect(performanceFeeExample("150")).toBeNull();
  });
});
