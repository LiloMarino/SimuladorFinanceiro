import { describe, expect, it } from "vitest";
import {
  aboveWaterMark,
  feeStep,
  feeToBody,
  feeToPoints,
  managementPerMonth,
  performanceExample,
  snapFee,
} from "./fund-fees";

describe("taxas da gestora", () => {
  it("converte a fração do servidor em pontos da régua e de volta", () => {
    expect(feeToPoints("0.0200")).toBeCloseTo(2, 9);
    expect(feeToBody(1.5)).toBe("0.0150");
    expect(feeToBody(20)).toBe("0.2000");
  });

  it("o passo é de décimos nos tetos pequenos e inteiro nos grandes", () => {
    expect(feeStep(2)).toBe(0.1);
    expect(feeStep(20)).toBe(1);
  });

  it("a régua arredonda ao passo e respeita o teto", () => {
    expect(snapFee(1.04, 2)).toBeCloseTo(1, 9);
    expect(snapFee(9, 2)).toBe(2);
    expect(snapFee(-1, 2)).toBe(0);
  });

  it("administração de 2% ao ano sobre R$ 1 milhão rende R$ 1.666,67 por mês", () => {
    expect(managementPerMonth(1_000_000, 2)).toBeCloseTo(1666.67, 2);
  });

  it("performance de 20% sobre 5 pontos acima do CDI leva 1 ponto", () => {
    expect(performanceExample(20)).toEqual({ extraPoints: 5, points: 1 });
  });

  it("só o que passa da marca d'água conta", () => {
    expect(aboveWaterMark(108, 110)).toBe(0);
    expect(aboveWaterMark(115, 110)).toBe(5);
    expect(aboveWaterMark(115, null)).toBe(0);
  });
});
