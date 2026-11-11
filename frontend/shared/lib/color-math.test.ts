import { describe, expect, it } from "vitest";
import { contrastRatio, deltaE2000, deltaE2000Lab } from "./color-math";

describe("contrastRatio", () => {
  it("vai de 21 (preto no branco) a 1 (cores iguais)", () => {
    expect(contrastRatio("#000000", "#FFFFFF")).toBeCloseTo(21, 5);
    expect(contrastRatio("#FFFFFF", "#000000")).toBeCloseTo(21, 5);
    expect(contrastRatio("#2350D8", "#2350D8")).toBeCloseTo(1, 5);
  });

  it("bate com o valor conhecido do cinza #767676 no branco (4,54)", () => {
    expect(contrastRatio("#767676", "#FFFFFF")).toBeCloseTo(4.54, 2);
  });
});

describe("deltaE2000", () => {
  it("é 0 para cores iguais e simétrico", () => {
    expect(deltaE2000("#209993", "#209993")).toBe(0);
    expect(deltaE2000("#D92D20", "#2350D8")).toBeCloseTo(deltaE2000("#2350D8", "#D92D20"), 8);
  });

  it("reproduz pares de referência de Sharma et al. (2005)", () => {
    expect(deltaE2000Lab([50, 2.6772, -79.7751], [50, 0, -82.7485])).toBeCloseTo(2.0425, 3);
    expect(deltaE2000Lab([50, 3.1571, -77.2803], [50, 0, -82.7485])).toBeCloseTo(2.8615, 3);
    expect(deltaE2000Lab([50, 2.5, 0], [73, 25, -18])).toBeCloseTo(27.1492, 3);
    expect(deltaE2000Lab([60.2574, -34.0099, 36.2677], [60.4626, -34.1751, 39.4387])).toBeCloseTo(1.2644, 3);
  });

  it("dá distância grande entre preto e branco", () => {
    expect(deltaE2000("#000000", "#FFFFFF")).toBeCloseTo(100, 0);
  });
});
