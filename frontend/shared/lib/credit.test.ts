import { describe, expect, it } from "vitest";
import { displaySelicSpread, displaySpread, displayWholePercent, gradeTone, isDowngrade, monthlyEquivalent } from "./credit";

describe("monthlyEquivalent", () => {
  it("converte 9,25% ao ano em cerca de 0,74% ao mês", () => {
    expect(monthlyEquivalent("0.0925")).toBeCloseTo(0.0074, 4);
  });

  it("taxa zero fica zero", () => {
    expect(monthlyEquivalent(0)).toBe(0);
  });
});

describe("displaySpread", () => {
  it("escreve o spread em pontos", () => {
    expect(displaySpread("0.05")).toBe("+5");
    expect(displaySpread("0.065")).toBe("+6,5");
  });
});

describe("displaySelicSpread", () => {
  it("escreve o spread somado à SELIC, com espaço em volta do +", () => {
    expect(displaySelicSpread("0.05")).toBe("SELIC + 5");
    expect(displaySelicSpread("0.065")).toBe("SELIC + 6,5");
  });
});

describe("displayWholePercent", () => {
  it("arredonda para o inteiro", () => {
    expect(displayWholePercent("0.6")).toBe("60%");
    expect(displayWholePercent(0.45)).toBe("45%");
  });
});

describe("gradeTone", () => {
  it("separa as notas em três tons", () => {
    expect(gradeTone("A")).toBe("success");
    expect(gradeTone("BBB")).toBe("warning");
    expect(gradeTone("D")).toBe("destructive");
  });
});

describe("isDowngrade", () => {
  it("compara a posição na escada", () => {
    expect(isDowngrade("A", "BBB")).toBe(true);
    expect(isDowngrade("A", "AA")).toBe(false);
    expect(isDowngrade("A", "A")).toBe(false);
  });
});
