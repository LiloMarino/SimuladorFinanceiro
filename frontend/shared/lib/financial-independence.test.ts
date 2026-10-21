import { describe, expect, it } from "vitest";
import {
  annualExpenseMultiple,
  displayAnnualExpenseMultiple,
  displayAnnualMultiple,
  displayRatePercent,
  independenceGoal,
  unexpectedLabel,
  withdrawalRateToField,
} from "./financial-independence";

describe("meta de independência", () => {
  it("é a despesa de um ano dividida pela taxa de retirada", () => {
    // 12 × 5.000 = 60.000 por ano; a 4%, precisa de 1.500.000
    expect(independenceGoal(5000, 0.04)).toBeCloseTo(1_500_000, 6);
  });

  it("nos limites de 1% e 10% ao ano", () => {
    expect(independenceGoal(5000, 0.01)).toBeCloseTo(6_000_000, 6);
    expect(independenceGoal(5000, 0.1)).toBeCloseTo(600_000, 6);
  });
});

describe("múltiplo da despesa anual", () => {
  it("é o inverso da taxa", () => {
    expect(annualExpenseMultiple(0.04)).toBeCloseTo(25, 9);
    expect(annualExpenseMultiple(0.01)).toBeCloseTo(100, 9);
    expect(annualExpenseMultiple(0.1)).toBeCloseTo(10, 9);
  });

  it("aparece com uma casa no máximo", () => {
    expect(displayAnnualMultiple(0.04)).toBe("25×");
    expect(displayAnnualMultiple(0.03)).toBe("33,3×");
    expect(displayAnnualExpenseMultiple(0.04)).toBe("25× a despesa anual");
  });
});

describe("taxa como o jogador escreve", () => {
  it("vira percentual sem zeros sobrando", () => {
    expect(withdrawalRateToField("0.04")).toBe("4");
    expect(withdrawalRateToField("0.085")).toBe("8,5");
    expect(displayRatePercent(0.08)).toBe("8%");
    expect(displayRatePercent("0.005")).toBe("0,5%");
  });
});

describe("frequência de imprevistos", () => {
  it("usa o nome da opção, ou a contagem por ano", () => {
    expect(unexpectedLabel(3)).toBe("Normais");
    expect(unexpectedLabel(2)).toBe("2 por ano");
  });
});
