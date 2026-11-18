import { describe, expect, it } from "vitest";
import { premium, quotasToControl, sellableKeepingControl } from "./fund-quota";

describe("controle", () => {
  it("faltam as cotas até passar de 50%", () => {
    // Metade de 10.000 é 5.000; precisa de 5.001. Com 2.100: 5.001 − 2.100 = 2.901
    expect(quotasToControl(2100, 10_000)).toBe(2901);
  });

  it("quem já controla não precisa de nenhuma", () => {
    expect(quotasToControl(5800, 10_000)).toBe(0);
  });

  it("o gestor vende o que passa do mínimo de controle", () => {
    // Mínimo 5.001; 5.800 − 5.001 = 799
    expect(sellableKeepingControl(5800, 10_000)).toBe(799);
  });

  it("sem controle não há o que vender mantendo-o", () => {
    expect(sellableKeepingControl(4000, 10_000)).toBe(0);
  });
});

describe("ágio", () => {
  it("é o preço sobre o patrimônio por cota, menos 1", () => {
    // 141,20 ÷ 128,40 − 1 = +9,97%
    expect(premium(141.2, 128.4)).toBeCloseTo(0.0997, 4);
  });

  it("deságio fica negativo", () => {
    // 90 ÷ 100 − 1 = −10%
    expect(premium(90, 100)).toBeCloseTo(-0.1, 6);
  });
});
